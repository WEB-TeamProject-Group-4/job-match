from enum import Enum
from typing import Optional
from pydantic import BaseModel
from app.schemas.user import UsernameDisplay, UserCreate


class ProfessionalCreate(UserCreate):
    first_name: str
    last_name: str

    @staticmethod
    def get_type():
        return 'professional'


class ProfessionalCreateDisplay(UsernameDisplay):
    first_name: str
    last_name: str


class ProfessionalDisplay(BaseModel):
    user: UsernameDisplay
    first_name: str
    last_name: str


class ProfessionalInfoCreate(BaseModel):
    first_name: str
    last_name: str
    summary: str
    location: str


class ProfessionalInfoDisplay(ProfessionalInfoCreate):
    status: Optional[str]
    picture: Optional[str]
    active_resumes: int
    # matches: list


class ProfessionalStatus(str, Enum):
    active = 'active'
    busy = 'busy'



