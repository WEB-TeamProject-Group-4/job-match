from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    password: str
    email: str

    def get_type(self):
        return 'admin'


class UserDisplay(BaseModel):
    username: str
    type: str


class UsernameDisplay(BaseModel):
    username: str
