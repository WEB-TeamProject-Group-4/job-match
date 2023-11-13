from pydantic import BaseModel


class CompanyCreate(BaseModel):
    username: str
    password: str
    name: str


class CompanyLoginDisplay(BaseModel):
    name: str
