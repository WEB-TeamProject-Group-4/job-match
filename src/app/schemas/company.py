from pydantic import BaseModel

from app.schemas.user import UsernameDisplay


class CompanyCreate(BaseModel):
    username: str
    password: str
    name: str


class CompanyLoginDisplay(BaseModel):
    username: str
    name: str


class CompanyDisplay(BaseModel):
    user: UsernameDisplay
    name: str
