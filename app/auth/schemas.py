from pydantic import BaseModel, Field
from app.config import Config

class CreateUser(BaseModel):
    email: str
    username: str = Field(max_length=64)
    last_name: str = Field(max_length=32)
    first_name: str = Field(max_length=32)
    password: str
    company: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class ForgotPasswordModel(BaseModel):
    email: str

class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str

class AdminCreateModel(BaseModel):
    email: str = Config.EMAIL_AD
    last_name: str = "root"
    first_name: str = "root"
    username: str = Config.USERNAME_AD
    password: str = Config.PASSWORD_AD
    is_verified: bool = True
    role: str = "admin"



