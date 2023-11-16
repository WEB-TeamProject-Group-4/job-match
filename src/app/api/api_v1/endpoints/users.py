from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from app.schemas.company import CompanyCreate, CompanyDisplay
from app.schemas.professional import ProfessionalCreate, ProfessionalDisplay
from app.schemas.user import UserDisplay, UserCreate
from typing import Annotated, List
from app.db.database import get_db

from app.db.models import DbUsers, DbProfessionals, DbCompanies
from app.core.auth import get_current_user
from app.crud.crud_user import create_user

router = APIRouter()


@router.post('/users', response_model=UserDisplay)
async def create_user_admin(request: UserCreate, db: Annotated[Session, Depends(get_db)]):
    return await create_user(db, request)


@router.post('/professionals', response_model=ProfessionalDisplay)
async def create_professional(request: ProfessionalCreate, db: Annotated[Session, Depends(get_db)]):
    return await create_user(db, request)


@router.post('/companies', response_model=CompanyDisplay)
async def create_company(request: CompanyCreate, db: Annotated[Session, Depends(get_db)]):
    return await create_user(db, request)


@router.get('/users', response_model=List[UserDisplay])
def get_users(db: Annotated[Session, Depends(get_db)],
              current_user: Annotated[UserDisplay, Depends(get_current_user)]):
    users = db.query(DbUsers).all()
    return users


@router.get('/professionals', response_model=List[ProfessionalDisplay])
def get_professionals(db: Annotated[Session, Depends(get_db)],
                      current_user: Annotated[UserDisplay, Depends(get_current_user)]):
    professionals = db.query(DbProfessionals).all()
    return professionals


@router.get('/companies', response_model=List[CompanyDisplay])
def get_companies(db: Annotated[Session, Depends(get_db)],
                  current_user: Annotated[UserDisplay, Depends(get_current_user)]):
    companies = db.query(DbCompanies).all()
    return companies
