import logging
import uuid
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timezone, timedelta

from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
from app.config import Config
from fastapi import HTTPException, status


pwd_context = CryptContext(schemes="bcrypt", deprecated="auto")


def get_hashed_password(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET, salt="email-configuration"
)


def encode_url_safe_token(data: dict):
    token = serializer.dumps(data)
    return token


def decode_url_safe_token(token: str):
    try:
        token_data = serializer.loads(token, max_age=3600)
        return token_data

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Invalid token",
        )


def create_access_token(data: dict, expires_delta: timedelta | None = None, refresh: bool = False):
    if expires_delta:
        expires = datetime.now(timezone.utc) + expires_delta
    else:
        expires = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode = {
        **data,
        "exp": expires,
        "refresh": refresh,
        "sub": str(uuid.uuid4())
    }
    encode_jwt = jwt.encode(to_encode, Config.JWT_SECRET, Config.JWT_ALGORITHM)
    return encode_jwt

def decode_token(token: str):
    try:
        token_data = jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
        return token_data
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    


