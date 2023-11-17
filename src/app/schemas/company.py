from pydantic import BaseModel
from app.schemas.user import UsernameDisplay, UserCreate


class CompanyCreate(UserCreate):
    name: str

    @staticmethod
    def get_type():
        return 'company'

class CompanyDisplay(BaseModel):
    user: UsernameDisplay
    name: str
