from pydantic import BaseModel, EmailStr

class RegisterDto(BaseModel):
    name: str | None = None
    email: EmailStr
    password: str

class LoginDto(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "Bearer"
