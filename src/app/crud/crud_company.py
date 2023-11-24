from typing import Type, TypeVar, Generic, Union

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models import DbCompanies, DbUsers, DbInfo, DbAds, DbJobsMatches
from app.schemas.company import CompanyInfoCreate, CompanyInfoDisplay

CompanyModelType = TypeVar('CompanyModelType', bound=Union[Type[DbCompanies], DbCompanies])
UserModelType = TypeVar('UserModelType', bound=Union[Type[DbUsers], DbUsers])
InfoModel = TypeVar('InfoModel', bound=Union[DbInfo, Type[DbInfo]])


class CRUDCompany(Generic[CompanyModelType, InfoModel, UserModelType]):
    @staticmethod
    async def get_multi(db: Session, name: str | None, page: int) -> list[CompanyModelType]:
        queries = [DbUsers.is_verified == 1, DbUsers.is_deleted == False]
        if name:
            search = "%{}%".format(name)
            queries.append(DbCompanies.name.like(search))

        companies = db.query(DbCompanies).join(DbCompanies.user).filter(*queries).limit(10).offset(
            (page - 1) * 10).all()
        return companies

    @staticmethod
    async def get_by_id(db: Session, company_id: str) -> CompanyModelType:
        company = db.query(DbCompanies).filter(DbCompanies.id == company_id,
                                               DbCompanies.is_deleted == False).first()
        return company

    @staticmethod
    async def update(db: Session, name: str | None, contact: str | None, user_id: str) -> CompanyModelType:
        company = db.query(DbCompanies).filter(DbCompanies.user_id == user_id,
                                               DbCompanies.is_deleted == False).first()
        if name:
            company.name = name
        if contact:
            company.contacts = contact
        db.commit()

        return company

    @staticmethod
    async def delete_by_id(db: Session, company_id: str, user: UserModelType) -> None:
        company: CompanyModelType = db.query(DbCompanies).filter(DbCompanies.id == company_id,
                                                                 DbCompanies.is_deleted == False).first()
        if not await is_admin(user) and not await is_owner(company, user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Deletion of the company is restricted to administrators or the company owner.'
            )
        else:
            company.is_deleted = True
            db.commit()
            return

    @staticmethod
    async def create_info(db: Session, company_id: str, schema: CompanyInfoCreate) -> InfoModel:
        company = await CRUDCompany.get_by_id(db, company_id)
        new_info = DbInfo(**dict(schema))
        db.add(new_info)
        db.commit()
        db.refresh(new_info)
        company.info_id = new_info.id
        db.commit()
        return new_info

    @staticmethod
    async def get_info_by_id(db: Session, info_id: str, company_id: str) -> CompanyInfoDisplay:
        info = db.query(DbInfo).filter(DbInfo.id == info_id, DbInfo.is_deleted == False).first()
        active_job_ads = db.query(DbAds).filter(DbAds.info_id == info_id,
                                                DbAds.status == 'active',).count()
        number_of_matches = db.query(DbJobsMatches).filter(DbJobsMatches.company_id == company_id).count()

        return CompanyInfoDisplay(**info.__dict__, active_job_ads=active_job_ads,
                                  number_of_matches=number_of_matches)

    @staticmethod
    async def update_info(db: Session, info_id: str, description: str | None, location: str | None) -> InfoModel:
        info = db.query(DbInfo).filter(DbInfo.id == info_id, DbInfo.is_deleted == False).first()
        if description:
            info.description = description
        if location:
            info.location = location
        db.commit()
        return info

    @staticmethod
    async def delete_info_by_id(db: Session, info_id: str, user: UserModelType):
        company_id: int = user.company[0].id
        company = db.query(DbCompanies).filter(DbCompanies.id == company_id).first()
        info = db.query(DbInfo).filter(DbInfo.id == info_id).first()
        if not await is_admin(user) and not await is_owner(company, user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Deletion of the company is restricted to administrators or the company owner.'
            )
        else:
            db.delete(info)
            db.commit()
            return


async def is_admin(user: UserModelType) -> bool:
    return user.type == 'admin'


async def is_owner(company: CompanyModelType, user_id: str) -> bool:
    return company.user_id == user_id
