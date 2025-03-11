from pydantic import BaseModel, Field

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
    email: str = "root@root.com"
    last_name: str = "root"
    first_name: str = "root"
    username: str = "root"
    password: str = "root123"
    is_verified: bool = True
    role: str = "admin"



