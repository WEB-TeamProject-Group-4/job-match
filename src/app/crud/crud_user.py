from sqlalchemy.orm import Session
from app.schemas.company import CompanyCreate, CompanyDisplay
from app.db.models import DbUsers, DbProfessionals, DbCompanies
from app.schemas.professional import ProfessionalCreate, ProfessionalDisplay
from app.schemas.user import UserCreate
from app.email import *
from fastapi import HTTPException, status
from app.core.hashing import Hash
from sqlalchemy.exc import IntegrityError
from typing import Union, Generic, TypeVar, Type

UserModelType = TypeVar("UserModelType", bound=DbUsers)


class UserFactory(Generic[UserModelType]):
    @staticmethod
    async def create_db_user(db: Session, request: Union[UserCreate, ProfessionalCreate, CompanyCreate],
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
    async def create_db_user(db: Session, request: Union[UserCreate, ProfessionalCreate, CompanyCreate],
                          user_type: str) -> ProfessionalDisplay:
        new_user = await UserFactory.create_db_user(db, request, "professional")

        new_professional = DbProfessionals(
            first_name=request.first_name,
            last_name=request.last_name,
            user_id=new_user.id
        )

        db.add(new_professional)
        db.commit()
        db.refresh(new_professional)
        await send_email([request.email], new_user)
        return ProfessionalDisplay(username=new_user.username, first_name=new_professional.first_name,
                                   last_name=new_professional.last_name)


class CompanyFactory(UserFactory[DbCompanies]):
    @staticmethod
    async def create_db_user(db: Session, request: Union[UserCreate, ProfessionalCreate, CompanyCreate],
                          user_type: str) -> CompanyDisplay:
        new_user = await UserFactory.create_db_user(db, request, "company")

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
            await send_email([request.email], new_user)
            return CompanyDisplay(username=new_user.username, name=new_company.name)


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
    new_user = await factory.create_db_user(db, request, user_type)
    return new_user
