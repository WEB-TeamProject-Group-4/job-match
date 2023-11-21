from pydantic import BaseModel
from app.schemas.user import UsernameDisplay, UserCreate


class CompanyCreate(UserCreate):
    name: str

    @staticmethod
    def get_type():
        return 'company'


class CompanyCreateDisplay(UsernameDisplay):
    name: str


class CompanyDisplay(BaseModel):
    user: UsernameDisplay
    name: str


class UpdateCompanyDisplay(CompanyDisplay):
    contacts: str


class CompanyInfoCreate(BaseModel):
    description: str
    location: str


class CompanyInfoCreateDisplay(CompanyInfoCreate):
    picture: str | None
