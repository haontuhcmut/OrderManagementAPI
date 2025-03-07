from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends, HTTPException, status
from app.db.session import get_session
from fastapi.security import OAuth2PasswordBearer
from app.db.redis import token_in_blocklist
from app.auth.utils import decode_token

SessionDep = Annotated[AsyncSession, Depends(get_session)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

