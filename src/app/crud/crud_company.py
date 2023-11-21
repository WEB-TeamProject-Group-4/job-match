from typing import List, Type

from sqlalchemy.orm import Session

from app.db.models import DbCompanies, DbUsers


async def get_companies_crud(db: Session, name: str | None) -> List[Type[DbCompanies]]:
    queries = [DbUsers.is_verified == 1]
    if name:
        search = "%{}%".format(name)
        queries.append(DbCompanies.name.like(search))

    companies = db.query(DbCompanies).join(DbCompanies.user).filter(*queries).all()
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
