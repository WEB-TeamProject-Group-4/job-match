from typing import Annotated, List
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.crud.crud_user import create_user
from app.db.database import get_db
from app.db.models import DbCompanies
from app.schemas.company import CompanyCreate, CompanyDisplay
from app.schemas.user import UserDisplay


router = APIRouter()


@router.post('/companies', response_model=CompanyDisplay)
async def create_company(request: CompanyCreate, db: Annotated[Session, Depends(get_db)]):
    return await create_user(db, request)


@router.get('/companies', response_model=List[CompanyDisplay])
def get_companies(db: Annotated[Session, Depends(get_db)],
                  current_user: Annotated[UserDisplay, Depends(get_current_user)]):
    companies = db.query(DbCompanies).all()
    return companies