from typing import List, Type

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models import DbCompanies, DbUsers


async def get_companies_crud(db: Session, name: str | None, page: int) -> List[Type[DbCompanies]]:
    queries = [DbUsers.is_verified == 1]
    if name:
        search = "%{}%".format(name)
        queries.append(DbCompanies.name.like(search))

    companies = db.query(DbCompanies).join(DbCompanies.user).filter(*queries).limit(10).offset((page - 1) * 10).all()
    return companies


async def get_company_by_id_crud(db: Session, company_id: str) -> Type[DbCompanies]:
    company = db.query(DbCompanies).filter(DbCompanies.id == company_id).first()
    return company


async def update_company_crud(db: Session, name: str | None, contact: str | None, user_id: str) -> Type[DbCompanies]:
    company = db.query(DbCompanies).filter(DbCompanies.user_id == user_id).first()
    if name:
        company.name = name
    if contact:
        company.contacts = contact
    db.commit()

    return company


async def check_company_delete_permission(db: Session, company_id: str, user_id: str) -> Type[DbCompanies]:
    user = db.query(DbUsers).filter(DbUsers.id == user_id).first()
    company = db.query(DbCompanies).filter(DbCompanies.id == company_id).first()
    if not company.user_id == user_id and user.type != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Deletion of the company is restricted to administrators or the company owner.'
        )
    return company


async def delete_company_by_id_crud(db: Session, company_id: str, user_id: str) -> None:
    company = await check_company_delete_permission(db, company_id, user_id)
    db.delete(company)
    db.commit()
    return
