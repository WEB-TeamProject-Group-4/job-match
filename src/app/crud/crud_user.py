from sqlalchemy.orm import Session
from app.db.models import DbUsers, DbProfessionals, DbCompanies
from app.schemas.company import CompanyCreate, CompanyLoginDisplay
from app.schemas.professional import ProfessionalCreate, ProfessionalLoginDisplay
from app.schemas.user import UserCreate
from app.email import *
from fastapi import HTTPException, status
from app.core.hashing import Hash
from sqlalchemy.exc import IntegrityError


async def create_db_user(db: Session, request: UserCreate):
    new_user = await create_user(db, request, "admin")
    await send_email([request.email], new_user)
    return new_user


async def create_db_professional(db: Session, request: ProfessionalCreate):
    new_user = await create_user(db, request, "professional")
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
    new_user = await create_user(db, request, "company")

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

    return CompanyLoginDisplay(username=new_user.username, name=new_company.name)


async def create_user(db: Session, request, user_type: str):
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
