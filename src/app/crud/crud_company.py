from typing import List, Type

from sqlalchemy.orm import Session

from app.db.models import DbCompanies, DbUsers


async def get_companies_crud(db: Session, name: str | None) -> List[Type[DbCompanies]]:
    companies = db.query(DbCompanies).join(DbCompanies.user).filter(DbUsers.is_verified == 1).all()
    return companies


async def get_company_by_id_crud(db: Session, company_id: str) -> Type[DbCompanies]:
    company = db.query(DbCompanies).filter(DbCompanies.id == company_id).first()
    return company
