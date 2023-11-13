from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserDisplay(BaseModel):
    username: str
    type: str
