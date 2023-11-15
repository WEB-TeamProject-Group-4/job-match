from sqlalchemy.orm import Session
from app.db.models import DbUsers, DbProfessionals, DbCompanies
from app.schemas.company import CompanyCreate, CompanyLoginDisplay
from app.schemas.professional import ProfessionalCreate, ProfessionalLoginDisplay
from app.schemas.user import UserCreate
from app.email import *

from app.core.hashing import Hash


async def create_db_user(db: Session, request: UserCreate):
    new_user = DbUsers(
        username=request.username,
        password=Hash.bcrypt(request.password),
        email=request.email,
        type='admin'
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    await send_email([request.email], new_user)
    return new_user


async def create_db_professional(db: Session, request: ProfessionalCreate):
    new_user = DbUsers(
        username=request.username,
        password=Hash.bcrypt(request.password),
        email=request.email,
        type='professional'
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    await send_email([request.email], new_user)

    new_professional = DbProfessionals(
        first_name=request.first_name,
        last_name=request.last_name,
        user_id=new_user.id
    )
    db.add(new_professional)
    db.commit()
    db.refresh(new_professional)
    return ProfessionalLoginDisplay(username=new_user.username, first_name=new_professional.first_name,
                                    last_name=new_professional.last_name)


async def create_db_company(db: Session, request: CompanyCreate):
    new_user = DbUsers(
        username=request.username,
        password=Hash.bcrypt(request.password),
        email=request.email,
        type='company'
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    await send_email([request.email], new_user)

    new_company = DbCompanies(
        name=request.name,
        user_id=new_user.id
    )
    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return CompanyLoginDisplay(username=new_user.username, name=new_company.name)
