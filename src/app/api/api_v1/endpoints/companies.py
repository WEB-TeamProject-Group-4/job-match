from typing import Annotated, List

from fastapi import Depends, APIRouter, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.crud.crud_user import create_user
from app.crud import crud_company
from app.db.database import get_db
from app.schemas.company import CompanyCreate, CompanyCreateDisplay, CompanyDisplay, UpdateCompanyDisplay
from app.schemas.user import UserDisplay

router = APIRouter()


@router.post('/companies', response_model=CompanyCreateDisplay)
async def create_company(schema: CompanyCreate, db: Annotated[Session, Depends(get_db)]):
    return await create_user(db, schema)


@router.get('/companies', response_model=List[CompanyDisplay])
async def get_companies(db: Annotated[Session, Depends(get_db)],
                        current_user: Annotated[UserDisplay, Depends(get_current_user)],
                        name: Annotated[str, Query(description='Optional name search parameter')] = None):
    companies = await crud_company.get_companies_crud(db, name)
    return companies


@router.get('/companies/{company_id}', response_model=CompanyDisplay)
async def get_company_by_id(db: Annotated[Session, Depends(get_db)],
                            company_id: Annotated[str, Path(description='Mandatory company id path parameter')]):
    company = await crud_company.get_company_by_id_crud(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Company with id {company_id} does not exist.'
        )
    return company


@router.patch('/companies', response_model=UpdateCompanyDisplay)
async def update_company(db: Annotated[Session, Depends(get_db)],
                         current_user: Annotated[UserDisplay, Depends(get_current_user)],
                         name: Annotated[str, Query(description='Optional name update parameter')] = None,
                         contact: Annotated[str, Query(description='Optional contact update parameter')] = None):
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Please verify your account.'
        )
    else:
        updated_company = await crud_company.update_company_crud(db, name, contact, current_user.id)
        return updated_company

