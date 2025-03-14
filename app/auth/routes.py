from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.schemas import (
    CreateUser,
    Token,
    ForgotPasswordModel,
    PasswordResetConfirmModel,
)
from app.auth.dependencies import (
    SessionDep,
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
)

from app.celery_tasks import send_email
from app.auth.services import UserService, AdminService
from app.auth.utils import (
    encode_url_safe_token,
    decode_url_safe_token,
    create_access_token,
    get_hashed_password,
)
from app.config import Config
from app.db.redis import add_sub_to_blocklist

from typing import Annotated
from datetime import timedelta, datetime, timezone
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
env = Environment(loader=FileSystemLoader(BASE_DIR.parent.parent / "templates"))

access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["user", "admin"])
admin_role_checker = Depends(RoleChecker(["admin"]))
user_services = UserService()
admin_services = AdminService()

oauth_route = APIRouter()


@oauth_route.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: CreateUser, session: SessionDep):
    email = user_data.email
    email_exists = await user_services.user_exists(email, session)
    if email_exists == "email_exists":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    username = user_data.username
    username_exists = await user_services.user_exists(username, session)
    if username_exists == "username_exists":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered. Please choose another username.",
        )
    new_user = await user_services.create_user(user_data, session)
    token = encode_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/verify/{token}"
    template = env.get_template("verify-email.html")
    html_content = template.render(action_url=link, first_name=user_data.first_name)
    emails = [email]
    subject = "Verify your email"
    send_email.delay(emails, subject, html_content)
    return {
        "message": "Account created! Check email to verify your account. You have 1 hour to verify, otherwise your account will be deleted.",
        "user": new_user,
    }


@oauth_route.get("/verify/{token}")
async def verify_user_account(token: str, session: SessionDep):
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")

    if user_email:
        user = await user_services.get_user(user_email, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        await user_services.update_user(user, {"is_verified": True}, session)
        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(
        content="Error occurred during verification",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@oauth_route.post("/token")
async def user_login(
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> Token:
    user = await user_services.authenticate_user(
        user_data.username, user_data.password, session
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(
        data={
            "email": user.username,
            "user_id": str(user.id),
            "role": user.role,
        },
        expires_delta=timedelta(minutes=Config.ACCESS_TOKEN_EXPIRES_MINUTES),
    )
    refresh_token = create_access_token(
        {"email": user.email, "user_id": str(user.id)},
        expires_delta=timedelta(days=Config.REFRESH_TOKEN_EXPIRES_DAYS),
        refresh=True,
    )
    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@oauth_route.get("/me")
async def get_current_user(
    user=Depends(get_current_user),
    _: bool = Depends(role_checker),
):
    return user


@oauth_route.get("/logout")
async def revoke_token(token_details: Annotated[dict, Depends(access_token_bearer)]):
    sub = token_details.get("sub")
    await add_sub_to_blocklist(sub)
    return JSONResponse(
        content={"message": "Logged out successfully"}, status_code=status.HTTP_200_OK
    )


@oauth_route.get("/refresh_token")
async def get_new_access_token(
    token_details: Annotated[dict, Depends(RefreshTokenBearer())],
):
    expiry_timestamp = token_details["exp"]
    if datetime.fromtimestamp(expiry_timestamp, timezone.utc) > datetime.now(
        timezone.utc
    ):
        new_access_token = create_access_token(
            data=token_details,
            expires_delta=timedelta(minutes=Config.ACCESS_TOKEN_EXPIRES_MINUTES),
        )
        return new_access_token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


@oauth_route.post("/forgot-password")
async def password_reset_request(email_data: ForgotPasswordModel, session: SessionDep):
    email = email_data.email
    user = await user_services.get_user(email, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Error user not found"
        )
    token = encode_url_safe_token({"email": email})
    link = f"http:{Config.DOMAIN}/password-reset-confirm/{token}"
    template = env.get_template("password-reset.html")
    html_content = template.render(action_url=link, first_name=user.first_name)
    subject = "Forgot your password"
    send_email.delay([email], subject, html_content)
    return JSONResponse(
        content={
            "message": "Please check your email for instruction to reset your password"
        },
        status_code=status.HTTP_200_OK,
    )


@oauth_route.post("/password-reset-confirm/{token}")
async def valid_reset_password(
    token: str, password: PasswordResetConfirmModel, session: SessionDep
):
    new_password = password.new_password
    confirm_new_password = password.confirm_new_password
    if new_password != confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password does match the confirmation password",
        )
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")
    if user_email:
        user = await user_services.get_user(user_email, session)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Error user not found"
            )
        hashed_password = get_hashed_password(new_password)
        await user_services.update_user(
            user, {"hashed_password": hashed_password}, session
        )
        return JSONResponse(
            content={"message": "Password reset successfully"},
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(
        content="Error occurred during password reset",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@oauth_route.patch(
    "/upgrade_to_admin/{username_or_email}", dependencies=[admin_role_checker]
)
async def upgrade_user(
    username_or_email: str,
    session: SessionDep,
    _: Annotated[dict, Depends(access_token_bearer)],
):
    user = await admin_services.get_user(username_or_email, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Error user not found"
        )
    else:
        await admin_services.update_user(user, {"role": "admin"}, session)
        return JSONResponse(
            content={"message": "User upgraded successfully"},
            status_code=status.HTTP_200_OK,
        )


@oauth_route.delete(
    "/delete_user/{username_or_email}", dependencies=[admin_role_checker]
)
async def delete_user(
    username_or_email: str,
    _: Annotated[dict, Depends(access_token_bearer)],
    session: SessionDep,
):
    user_to_delete = await admin_services.delete_user_account(
        username_or_email, session
    )
    return {"message": "User is deleted", "user": user_to_delete}
