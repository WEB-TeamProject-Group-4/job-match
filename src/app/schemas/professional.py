from enum import Enum
from typing import Any, Optional, Union
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


class ProfessionalInfoDisplay(BaseModel):
    first_name: str
    last_name: str
    summary: str
    location: str
    status: Optional[str]
    active_resumes: int


class ProfessionalStatus(str, Enum):
    active = 'active'
    busy = 'busy'


class ProfessionalAdMatchDisplay(BaseModel):
    ad_id: str
    description: str
    location: str
    status: str
    min_salary: int
    max_salary: int
    is_approved: bool


