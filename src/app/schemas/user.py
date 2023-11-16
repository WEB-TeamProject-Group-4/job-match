from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr

    def get_type(self):
        return 'admin'


class UsernameDisplay(BaseModel):
    username: str


class UserDisplay(UsernameDisplay):
    type: str


