from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from app.auth.schemas import CreateUser
from sqlmodel.ext.asyncio.session import AsyncSession

from app.celery_tasks import send_email
from app.db.session import get_session
from app.auth.services import UserService
from app.auth.utils import encode_url_safe_token, decode_url_safe_token
from app.config import Config
from jinja2 import Environment, FileSystemLoader

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

env = Environment(loader=FileSystemLoader(BASE_DIR.parent.parent/"templates"))


user_services = UserService()
oauth_route = APIRouter()

@oauth_route.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: CreateUser, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    email_exists = await user_services.email_exists(email, session)
    if email_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    username = user_data.username
    username_exist = await user_services.username_exists(username, session)
    if username_exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")
    new_user = await user_services.create_user(user_data, session)
    token = encode_url_safe_token({email: email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"
    template = env.get_template("verify-email.html")
    html_content = template.render(action_url=link)
    email = [email]
    subject = "Verify your email"
    send_email.delay(email, subject, html_content)

    return {
        "message": "Account created! Check email to verify your account",
        "user": new_user
    }

@oauth_route.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")
    if user_email:
        user = await user_services.get_email(user_email, session)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        await user_services.update_user(user, {"is_verified": True}, session)
        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content="Error occurred during verification",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
