from pydantic import BaseModel

from app.schemas.user import UsernameDisplay


class ProfessionalCreate(BaseModel):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str


class ProfessionalLoginDisplay(BaseModel):
    username: str
    first_name: str
    last_name: str


class ProfessionalDisplay(BaseModel):
    user: UsernameDisplay
    first_name: str
    last_name: str
