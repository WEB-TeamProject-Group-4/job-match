from app.schemas.user import UsernameDisplay, UserCreate


class CompanyCreate(UserCreate):
    name: str

    @staticmethod
    def get_type():
        return 'company'


class CompanyDisplay(UsernameDisplay):
    name: str
