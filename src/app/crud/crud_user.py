from sqlalchemy.orm import Session
from app.schemas.company import CompanyCreate, CompanyLoginDisplay
from app.db.models import DbUsers, DbProfessionals, DbCompanies
from app.schemas.professional import ProfessionalCreate, ProfessionalLoginDisplay
from app.schemas.user import UserCreate
from app.email import *
from fastapi import HTTPException, status
from app.core.hashing import Hash
from sqlalchemy.exc import IntegrityError
from typing import Union, Generic, TypeVar, Type

UserModelType = TypeVar("UserModelType", bound=DbUsers)


class UserFactory(Generic[UserModelType]):
    @staticmethod
    def create_user(db: Session, request: Union[UserCreate, ProfessionalCreate, CompanyCreate],
                    user_type: str) -> UserModelType:
        new_user = DbUsers(
            username=request.username,
            password=Hash.bcrypt(request.password),
            email=request.email,
            type=user_type
        )
        try:
            db.add(new_user)
            db.commit()
        except IntegrityError as err:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err.args)
        else:
            db.refresh(new_user)
            return new_user


class ProfessionalFactory(UserFactory[DbProfessionals]):
    @staticmethod
    def create_user(db: Session, request: Union[UserCreate, ProfessionalCreate, CompanyCreate],
                    user_type: str) -> DbProfessionals:
        new_user = UserFactory.create_user(db, request, "professional")

        new_professional = DbProfessionals(
            first_name=request.first_name,
            last_name=request.last_name,
            user_id=new_user.id
        )

        db.add(new_professional)
        db.commit()
        db.refresh(new_professional)
        return new_professional


class CompanyFactory(UserFactory[DbCompanies]):
    @staticmethod
    def create_user(db: Session, request: Union[UserCreate, ProfessionalCreate, CompanyCreate],
                    user_type: str) -> DbCompanies:
        new_user = UserFactory.create_user(db, request, "company")

        new_company = DbCompanies(
            name=request.name,
            user_id=new_user.id
        )

        try:
            db.add(new_company)
            db.commit()
        except IntegrityError as err:
            db.rollback()
            db.delete(new_user)
            db.commit()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err.args)
        else:
            db.refresh(new_company)
            return new_company


def create_user_factory(user_type: str) -> Type[UserFactory]:
    factories = {
        "admin": UserFactory,
        "professional": ProfessionalFactory,
        "company": CompanyFactory
    }
    return factories.get(user_type, UserFactory)


async def create_user(db: Session, request: Union[UserCreate, ProfessionalCreate, CompanyCreate]) -> UserModelType:
    user_type = request.get_type()
    factory = create_user_factory(user_type)
    new_user = await factory.create_user(db, request, user_type)
    await send_email([request.email], new_user)
    return new_user
