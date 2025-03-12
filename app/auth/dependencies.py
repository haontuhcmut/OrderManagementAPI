from typing import Annotated, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends, HTTPException, status, Request
from app.db.session import get_session
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from app.db.redis import token_in_blocklist
from app.auth.utils import decode_token
from app.auth.services import UserService
from app.db.models import User


SessionDep = Annotated[AsyncSession, Depends(get_session)]
user_services = UserService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token") #Note: tokenUrl support to get token


class TokenBear:
    def __init__(self):
        self.credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async def __call__(self, token: Annotated[str, Depends(oauth2_scheme)]):
        token_data = decode_token(token)

        if token_data is None:
            raise self.credentials_exception

        if await token_in_blocklist(token_data["sub"]):
            raise self.credentials_exception

        self.verify_token_data(token_data)
        return token_data

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please override this method in child classes")


class AccessTokenBearer(TokenBear):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise self.credentials_exception


class RefreshTokenBearer(TokenBear):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise self.credentials_exception


async def get_current_user(
    token_details: Annotated[dict, Depends(AccessTokenBearer())], session: SessionDep
):
    user_email = token_details.get("email")
    user = await user_services.get_user(user_email, session)
    return user


class RoleChecker:
    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Annotated[User, Depends(get_current_user)]) -> Any:
        if not current_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )
        if current_user.role in self.allowed_roles:
            return True
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have enough permission to perform this action",
        )
