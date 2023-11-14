from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    password: str
    email: str


class UserDisplay(BaseModel):
    username: str
    type: str


class UsernameDisplay(BaseModel):
    username: str
