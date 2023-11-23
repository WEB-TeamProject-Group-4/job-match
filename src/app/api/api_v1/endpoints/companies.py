from typing import Annotated, List

from fastapi import Depends, APIRouter, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.crud.crud_user import create_user
from app.crud.crud_company import CRUDCompany
from app.db.database import get_db
from app.db.models import DbUsers
from app.schemas import company

router = APIRouter(tags=['company'])


@router.post('/companies', response_model=company.CompanyCreateDisplay)
async def create_company(schema: company.CompanyCreate, db: Annotated[Session, Depends(get_db)]):
    return await create_user(db, schema)


@router.get('/companies', response_model=List[company.CompanyDisplay])
async def get_companies(db: Annotated[Session, Depends(get_db)],
                        current_user: Annotated[DbUsers, Depends(get_current_user)],
                        name: Annotated[str, Query(description='Optional name search parameter')] = None,
                        page: Annotated[int, Query(description='Optional page number query parameter', ge=1)] = 1):
    companies = await CRUDCompany.get_multi(db, name, page)
    return companies


@router.get('/companies/{company_id}', response_model=company.CompanyDisplay)
async def get_company_by_id(db: Annotated[Session, Depends(get_db)],
                            company_id: Annotated[str, Path(description='Mandatory company id path parameter')]):
    company = await CRUDCompany.get_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Company with id {company_id} does not exist.'
        )
    return company


@router.patch('/companies', response_model=company.UpdateCompanyDisplay)
async def update_company(db: Annotated[Session, Depends(get_db)],
                         current_user: Annotated[DbUsers, Depends(get_current_user)],
                         name: Annotated[str, Query(description='Optional name update parameter')] = None,
                         contact: Annotated[str, Query(description='Optional contact update parameter')] = None):
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Please verify your account.'
        )
    else:
        updated_company = await CRUDCompany.update(db, name, contact, current_user.id)
        return updated_company


@router.delete('/companies/{company_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(db: Annotated[Session, Depends(get_db)],
                         company_id: Annotated[str, Path(description='Mandatory company id path parameter')],
                         current_user: Annotated[DbUsers, Depends(get_current_user)]
                         ):
    return await CRUDCompany.delete_by_id(db, company_id, current_user)


@router.post('/companies/info', response_model=company.CompanyInfoCreateDisplay)
async def create_company_info(db: Annotated[Session, Depends(get_db)],
                              current_user: Annotated[DbUsers, Depends(get_current_user)],
                              schema: company.CompanyInfoCreate
                              ):
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Please verify your account.'
        )
    else:
        info = await CRUDCompany.create_info(db, current_user.company[0].id, schema)
        return info


@router.get('/companies/info/', response_model=company.CompanyInfoDisplay)
async def get_company_info(db: Annotated[Session, Depends(get_db)],
                           current_user: Annotated[DbUsers, Depends(get_current_user)]):
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Please verify your account.'
        )
    else:
        info = await CRUDCompany.get_info_by_id(db, current_user.company[0].info_id,
                                                current_user.company[0].id)
        return info


@router.patch('/companies/info', response_model=company.CompanyInfoCreateDisplay)
async def update_info(db: Annotated[Session, Depends(get_db)],
                      current_user: Annotated[DbUsers, Depends(get_current_user)],
                      description: Annotated[str, Query(description='Optional description update parameter')] = None,
                      location: Annotated[str, Query(description='Optional location update parameter')] = None
                      ):
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Please verify your account.'
        )
    else:
        new_info = await CRUDCompany.update_info(db, current_user.company[0].info_id, description, location)
        return new_info


@router.delete('/companies/info/{info_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_info(db: Annotated[Session, Depends(get_db)],
                      current_user: Annotated[DbUsers, Depends(get_current_user)],
                      info_id: Annotated[str, Path(description='Mandatory info id path parameter')]
                      ):
    return await CRUDCompany.delete_info_by_id(db, info_id, current_user)
