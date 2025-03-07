from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.schemas import CreateUser, UserLoginModel, Token
from app.auth.dependencies import SessionDep, RefreshTokenBearer

from app.celery_tasks import send_email
from app.auth.services import UserService
from app.auth.utils import (
    encode_url_safe_token,
    decode_url_safe_token,
    create_access_token,
)
from app.config import Config

from typing import Annotated
from datetime import timedelta, datetime, timezone
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
env = Environment(loader=FileSystemLoader(BASE_DIR.parent.parent / "templates"))
user_services = UserService()
oauth_route = APIRouter()


@oauth_route.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: CreateUser, session: SessionDep):
    email = user_data.email
    username = user_data.username
    user_exists = await user_services.user_exists(username, email, session)
    if user_exists == "email_exists":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    if user_exists == "username_exists":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already registered"
        )
    new_user = await user_services.create_user(user_data, session)
    token = encode_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/verify/{token}"
    template = env.get_template("verify-email.html")
    html_content = template.render(action_url=link)
    emails = [email]
    subject = "Verify your email"
    send_email.delay(emails, subject, html_content)
    return {
        "message": "Account created! Check email to verify your account",
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
async def user_login(user_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep) -> Token:
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
            "sub": str(user.id),
            "role": user.role,
        },
        expires_delta=timedelta(minutes=Config.ACCESS_TOKEN_EXPIRES_MINUTES),
    )
    refresh_token = create_access_token(
        {"email": user.email, "user_uid": str(user.id)},
        expires_delta=timedelta(days=Config.REFRESH_TOKEN_EXPIRES_DAYS),
        refresh=True,
    )
    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
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

