from typing import Union, Generic, TypeVar, Type

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.schemas.company import CompanyCreate, CompanyCreateDisplay
from app.db.models import DbUsers, DbProfessionals, DbCompanies
from app.schemas.professional import ProfessionalCreate, ProfessionalCreateDisplay
from app.schemas.user import UserCreate
from app.email import *
from app.core.hashing import Hash

UserModelType = TypeVar("UserModelType", bound=DbUsers)


class UserFactory(Generic[UserModelType]):
    @staticmethod
    async def create_db_user(db: Session, schema: Union[UserCreate, ProfessionalCreate, CompanyCreate],
                             user_type: str) -> UserModelType:
        new_user = DbUsers(
            username=schema.username,
            password=Hash.bcrypt(schema.password),
            email=schema.email,
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
    async def create_db_user(db: Session, schema: Union[UserCreate, ProfessionalCreate, CompanyCreate],
                             user_type: str) -> ProfessionalCreateDisplay:
        new_user = await UserFactory.create_db_user(db, schema, "professional")

        new_professional = DbProfessionals(
            first_name=schema.first_name,
            last_name=schema.last_name,
            user_id=new_user.id
        )

        db.add(new_professional)
        db.commit()
        db.refresh(new_professional)
        await send_email([schema.email], new_user)
        return ProfessionalCreateDisplay(username=new_user.username, first_name=new_professional.first_name,
                                         last_name=new_professional.last_name)


class CompanyFactory(UserFactory[DbCompanies]):
    @staticmethod
    async def create_db_user(db: Session, schema: Union[UserCreate, ProfessionalCreate, CompanyCreate],
                             user_type: str) -> CompanyCreateDisplay:
        new_user = await UserFactory.create_db_user(db, schema, "company")

        new_company = DbCompanies(
            name=schema.name,
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
            await send_email([schema.email], new_user)
            return CompanyCreateDisplay(username=new_user.username, name=new_company.name)


def create_user_factory(user_type: str) -> Type[UserFactory]:
    factories = {
        "admin": UserFactory,
        "professional": ProfessionalFactory,
        "company": CompanyFactory
    }
    return factories.get(user_type, UserFactory)


async def create_user(db: Session, schema: Union[UserCreate, ProfessionalCreate, CompanyCreate]) -> UserModelType:
    user_type = schema.get_type()
    factory = create_user_factory(user_type)
    new_user = await factory.create_db_user(db, schema, user_type)
    return new_user
