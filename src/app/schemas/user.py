from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    password: str


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True
