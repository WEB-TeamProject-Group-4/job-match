from pydantic import BaseModel
from app.schemas.user import UsernameDisplay, UserCreate


class ProfessionalCreate(UserCreate):
    first_name: str
    last_name: str

    @staticmethod
    def get_type():
        return 'professional'

class ProfessionalDisplay(BaseModel):
    user: UsernameDisplay
    first_name: str
    last_name: str
