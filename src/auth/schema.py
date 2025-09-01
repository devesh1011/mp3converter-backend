from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    id: int
    username: str
    name: str


class ValidateResponse(BaseModel):
    username: str
    valid: bool = True
