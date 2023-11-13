from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from app.schemas.company import CompanyLoginDisplay, CompanyCreate
from app.schemas.professional import ProfessionalLoginDisplay, ProfessionalCreate
from app.schemas.user import UserDisplay, UserCreate
from typing import Annotated, List
from app.db.database import get_db
from app.crud.crud_user import create_db_user, create_db_professional, create_db_company
from app.db.models import DbUsers, DbProfessionals, DbCompanies
from app.core.security import get_current_user

router = APIRouter()


@router.post('/user', response_model=UserDisplay)
def create_user(request: UserCreate, db: Annotated[Session, Depends(get_db)]):
    return create_db_user(db, request)


@router.post('/professional', response_model=ProfessionalLoginDisplay)
def create_professional(request: ProfessionalCreate, db: Annotated[Session, Depends(get_db)]):
    return create_db_professional(db, request)


@router.post('/company', response_model=CompanyLoginDisplay)
def create_company(request: CompanyCreate, db: Annotated[Session, Depends(get_db)]):
    return create_db_company(db, request)


@router.get('/users', response_model=List[UserDisplay])
def get_users(db: Annotated[Session, Depends(get_db)],
              current_user: Annotated[UserDisplay, Depends(get_current_user)]):
    users = db.query(DbUsers).all()
    return users


@router.get('/professionals', response_model=List[ProfessionalLoginDisplay])
def get_professionals(db: Annotated[Session, Depends(get_db)],
                      current_user: Annotated[UserDisplay, Depends(get_current_user)]):
    professionals = db.query(DbProfessionals, DbUsers.username).join(DbUsers).all()
    return [
        {"username": username, "first_name": professional.first_name, "last_name": professional.last_name}
        for professional, username in professionals
    ]


@router.get('/companies', response_model=List[CompanyLoginDisplay])
def get_companies(db: Annotated[Session, Depends(get_db)],
                  current_user: Annotated[UserDisplay, Depends(get_current_user)]):
    companies = db.query(DbCompanies).all()
    return companies
