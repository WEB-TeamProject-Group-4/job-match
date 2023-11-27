import io
from typing import Type, TypeVar, Generic, Union

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse

from app.db.models import DbCompanies, DbUsers, DbInfo, DbAds, DbJobsMatches
from app.schemas.company import CompanyInfoCreate, CompanyInfoDisplay

CompanyModelType = TypeVar('CompanyModelType', bound=Union[Type[DbCompanies], DbCompanies])
UserModelType = TypeVar('UserModelType', bound=Union[Type[DbUsers], DbUsers])
InfoModelType = TypeVar('InfoModelType', bound=Union[DbInfo, Type[DbInfo]])
AdModelType = TypeVar('AdModelType', bound=Union[DbAds, Type[DbAds]])


class CRUDCompany(Generic[CompanyModelType, InfoModelType, UserModelType]):
    @staticmethod
    async def get_multi(db: Session, name: str | None, page: int) -> list[CompanyModelType]:
        """
         Retrieve a list of companies based on optional search parameters.

        This method queries the database to fetch a list of companies based on the provided search parameters.

        :param db:The database session.
        :param name:Optional parameter for filtering companies by name.
        :param page:The page number for pagination (starts from 1).
        :return:A list of company models.
        """
        queries = [DbUsers.is_verified == True, DbUsers.is_deleted == False]
        if name:
            search = "%{}%".format(name)
            queries.append(DbCompanies.name.like(search))

        companies: list[CompanyModelType] = db.query(DbCompanies).join(DbCompanies.user).filter(*queries).limit(
            10).offset(
            (page - 1) * 10).all()
        return companies

    @staticmethod
    async def get_by_id(db: Session, company_id: str) -> CompanyModelType:
        """
        Retrieve a company by its unique identifier.

        This method queries the database to fetch a specific company based on its unique identifier.

        :param db:The database session.
        :param company_id:The unique identifier of the company.
        :return:The company model for the specified identifier.
        :raises HTTPException 404: If no company is found with the provided company_id.
        """
        company: CompanyModelType = db.query(DbCompanies).filter(DbCompanies.id == company_id,
                                                                 DbCompanies.is_deleted == False).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Company with id {company_id} does not exist.'
            )
        return company

    @staticmethod
    async def update(db: Session, name: str | None, contact: str | None, user_id: str) -> CompanyModelType:
        """
        Update information for a company.

        This method updates information for a company based on the provided parameters.

        :param db:The database session.
        :param name:Optional parameter for updating the company name.
        :param contact:Optional parameter for updating the company contact information.
        :param user_id:The unique identifier of the user associated with the company.
        :return:The updated company model.
        :raises HTTPException 404: If no company is found for the provided user_id.
        """
        company: CompanyModelType = db.query(DbCompanies).filter(DbCompanies.user_id == user_id,
                                                                 DbCompanies.is_deleted == False).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Company does not exist.'
            )
        if name:
            company.name = name
        if contact:
            company.contacts = contact
        db.commit()

        return company

    @staticmethod
    async def delete_by_id(db: Session, company_id: str, user: UserModelType) -> None:
        """
        Delete a company by its unique identifier.

        This method marks a company as deleted in the database based on its unique identifier. Additionally, it checks
        permissions to ensure that only administrators or the company owner can delete the company.
        :param db:The database session.
        :param company_id:The unique identifier of the company to be deleted.
        :param user:The user attempting to delete the company.
        :return:None
        :raises HTTPException 403: If the user does not have sufficient permissions to delete the company.
        :raises HTTPException 404: If no company is found with the provided company_id.
        """
        company: CompanyModelType = db.query(DbCompanies).filter(DbCompanies.id == company_id,
                                                                 DbCompanies.is_deleted == False).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Company with id {company_id} does not exist.'
            )
        if not await is_admin(user) and not await is_owner(company, user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Deletion of the company is restricted to administrators or the company owner.'
            )
        else:
            resumes: AdModelType = db.query(DbAds).filter(DbAds.info_id == company.info_id).all()
            if resumes:
                for resume in resumes:
                    resume.is_deleted = True
            company.mark_as_deleted(db)
            return

    @staticmethod
    async def create_info(db: Session, company_id: str, schema: CompanyInfoCreate) -> InfoModelType:
        """
        Create or update additional information for a company.

        This method creates or updates additional information for a company based on the provided parameters.

        :param db:The database session.
        :param company_id:The unique identifier of the company.
        :param schema:The schema containing information for creating or updating company information.
        :return:The created or updated company information model.
        """
        company: CompanyModelType = await CRUDCompany.get_by_id(db, company_id)
        if company.info_id and not company.info.is_deleted:
            return await CRUDCompany.update_info(db, company.info_id, schema.description, schema.location)
        new_info = DbInfo(**dict(schema))
        db.add(new_info)
        db.commit()
        db.refresh(new_info)
        company.info_id = new_info.id
        db.commit()
        return new_info

    @staticmethod
    async def get_info_by_id(db: Session, info_id: str, company_id: str) -> CompanyInfoDisplay:
        """
        Retrieve additional information about a company by its unique identifier.

        This method queries the database to fetch additional information about a company based on its unique identifier.
        It also includes additional statistics, such as the number of active job ads and the number of job matches for
        the company.
        :param db:The database session.
        :param info_id:The unique identifier of the company information.
        :param company_id:The unique identifier of the company.
        :return:Information about the company's additional information with additional statistics.
        :raises HTTPException 404: If no company information is found with the provided info_id.
        """
        info = db.query(DbInfo).filter(DbInfo.id == info_id, DbInfo.is_deleted == False).first()
        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Info with id {info_id} does not exist.'
            )
        active_job_ads = db.query(DbAds).filter(DbAds.info_id == info_id,
                                                DbAds.status == 'active', ).count()
        number_of_matches = db.query(DbJobsMatches).filter(DbJobsMatches.company_id == company_id).count()

        return CompanyInfoDisplay(**info.__dict__, active_job_ads=active_job_ads,
                                  number_of_matches=number_of_matches)

    @staticmethod
    async def update_info(db: Session, info_id: str, description: str | None, location: str | None) -> InfoModelType:
        """
        Update additional information for a company.

        This method updates additional information for a company based on the provided parameters.
        :param db:The database session.
        :param info_id:The unique identifier of the company information.
        :param description:Optional parameter for updating the company information description.
        :param location:Optional parameter for updating the company information location.
        :return:The updated company information model.
        :raises HTTPException 404: If no company information is found with the provided info_id.
        """
        info: InfoModelType = db.query(DbInfo).filter(DbInfo.id == info_id, DbInfo.is_deleted == False).first()
        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Info with id {info_id} does not exist.'
            )
        if description:
            info.description = description
        if location:
            info.location = location
        db.commit()
        return info

    @staticmethod
    async def delete_info_by_id(db: Session, info_id: str, user: UserModelType) -> None:
        """
        Delete additional information for a company by its unique identifier.

        This method marks additional information for a company as deleted in the database based on its unique identifier.
        It checks permissions to ensure that only administrators or the company owner can delete the information.
        :param db:The database session.
        :param info_id:The unique identifier of the company information to be deleted.
        :param user:The user attempting to delete the information.
        :return:Nine
        :raises HTTPException 403: If the user does not have sufficient permissions to delete the information.
        :raises HTTPException 404: If no company information is found with the provided info_id.
        """
        company_id: int = user.company[0].id
        company: CompanyModelType = db.query(DbCompanies).filter(DbCompanies.id == company_id).first()
        info: InfoModelType = db.query(DbInfo).filter(DbInfo.id == info_id).first()
        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Info with id {info_id} does not exist.'
            )
        if not await is_admin(user) and not await is_owner(company, user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Deletion of the company is restricted to administrators or the company owner.'
            )
        else:
            info.is_deleted = True
            db.commit()
            return

    @staticmethod
    async def upload(db: Session, info_id: str, image: bytearray) -> StreamingResponse:
        """
        Upload an image for additional information of a company.

        This method uploads an image for the additional information of a company based on the provided parameters.
        The image is associated with the company information and stored in the database.
        :param db:The database session.
        :param info_id:The unique identifier of the company information.
        :param image:The image data to be uploaded.
        :return: A streaming response containing the uploaded image.
        :raises HTTPException 404: If no company information is found with the provided info_id.

        """
        info: InfoModelType = db.query(DbInfo).filter(DbInfo.id == info_id, DbInfo.is_deleted == False).first()
        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Info with id {info_id} does not exist.'
            )
        info.picture = image
        db.commit()
        return StreamingResponse(io.BytesIO(image), media_type="image/jpeg")

    @staticmethod
    async def get_image(db: Session, info_id: str) -> StreamingResponse:
        """
        Retrieve the image associated with additional information for a company.

        This method retrieves the image associated with the additional information of a company based on
        the provided parameters.
        :param db:The database session.
        :param info_id:The unique identifier of the company information.
        :return:A streaming response containing the retrieved image.
        :raises HTTPException 404: If no company information is found with the provided info_id.
        """
        info: InfoModelType = db.query(DbInfo).filter(DbInfo.id == info_id, DbInfo.is_deleted == False).first()
        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Info with id {info_id} does not exist.'
            )
        return StreamingResponse(io.BytesIO(info.picture), media_type="image/jpeg")


async def is_admin(user: UserModelType) -> bool:
    """
    Check if the user has administrative privileges.

    This method checks whether the provided user has administrative privileges based on their user type.
    :param user:The user model for whom to check administrative privileges.
    :return:True if the user has administrative privileges, False otherwise.
    """
    return user.type == 'admin'


async def is_owner(company: CompanyModelType, user_id: str) -> bool:
    """
    Check if the provided user is the owner of the company.

    This method checks whether the provided user is the owner of the specified company based on their user ID.

    :param company:The company model for which ownership is being checked.
    :param user_id:The unique identifier of the user to check for ownership.
    :return:True if the user is the owner of the company, False otherwise.
    """
    return company.user_id == user_id
