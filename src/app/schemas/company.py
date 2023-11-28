from pydantic import BaseModel, ByteSize
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
    contacts: str | None


class CompanyInfoCreate(BaseModel):
    description: str
    location: str


class CompanyInfoDisplay(CompanyInfoCreate):
    id: str
    active_job_ads: int
    number_of_matches: int


class AdDisplay(BaseModel):
    id: str
    description: str
    location: str
    min_salary: int
    max_salary: int


class CompanyMatchDisplay(BaseModel):
    company_name: str
    job_ad: AdDisplay
    professional_name: str
    resume: AdDisplay
