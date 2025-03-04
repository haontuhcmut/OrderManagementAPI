import logging

from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
from app.config import Config
from fastapi import HTTPException


pwd_context = CryptContext(schemes="bcrypt", deprecate="auto")

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



