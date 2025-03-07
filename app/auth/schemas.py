from pydantic import BaseModel, Field

class CreateUser(BaseModel):
    email: str
    username: str = Field(max_length=64)
    last_name: str = Field(max_length=32)
    first_name: str = Field(max_length=32)
    password: str
    company: str

class UserLoginModel(BaseModel):
    email_or_username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
