from pydantic import BaseModel


class ProfessionalCreate(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str


class ProfessionalLoginDisplay(BaseModel):
    username: str
    first_name: str
    last_name: str
