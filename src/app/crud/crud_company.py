import io
from typing import Type, TypeVar, Generic, Union

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse

from app.crud.crud_professional import calculate_similarity
from app.db.models import DbCompanies, DbUsers, DbInfo, DbAds, DbJobsMatches
from app.schemas.company import CompanyInfoCreate, CompanyInfoDisplay, AdDisplay, CompanyMatchDisplay

CompanyModelType = TypeVar('CompanyModelType', bound=Union[Type[DbCompanies], DbCompanies])
UserModelType = TypeVar('UserModelType', bound=Union[Type[DbUsers], DbUsers])
InfoModelType = TypeVar('InfoModelType', bound=Union[DbInfo, Type[DbInfo]])
AdModelType = TypeVar('AdModelType', bound=Union[DbAds, Type[DbAds]])
JobMatchesModelType = TypeVar('JobMatchesModelType', bound=Union[DbJobsMatches, Type[DbJobsMatches]])


class CRUDCompany(Generic[CompanyModelType, InfoModelType, UserModelType, AdModelType, JobMatchesModelType]):
    @staticmethod
    async def get_multi(db: Session, name: str | None, page: int) -> list[CompanyModelType]:
        """
         Retrieve a list of companies based on optional search parameters.

        This method queries the database to fetch a list of companies based on the provided search parameters.

        Parameters:
        - **db**: The database session.
        - **name**:8Optional parameter for filtering companies by name.
        - **page**: The page number for pagination (starts from 1).

        Returns:
        - A list of company models.
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

        Parameters:
        - **db**: The database session.
        - **company_id**: The unique identifier of the company.

        Returns:
        - The company model for the specified identifier.

        Raises:
        - HTTPException 404: If no company is found with the provided company_id.
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

        Parameters:
        - **db**: The database session.
        - **name**: Optional parameter for updating the company name.
        - **contact**: Optional parameter for updating the company contact information.
        - **user_id**: The unique identifier of the user associated with the company.

        Returns:
        - The updated company model.

        Raises:
        - HTTPException 404: If no company is found for the provided user_id.
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

        Parameters:
        - **db**: The database session.
        - **company_id**: The unique identifier of the company to be deleted.
        - **user**: The user attempting to delete the company.

        Returns:
        - None

        Raises:
        - HTTPException 403: If the user does not have sufficient permissions to delete the company.
        - HTTPException 404: If no company is found with the provided company_id.
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
            resumes: list[AdModelType] = db.query(DbAds).filter(DbAds.info_id == str(company.info_id)).all()
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

        Parameters:
        - **db**: The database session.
        - **company_id**: The unique identifier of the company.
        - **schema**: The schema containing information for creating or updating company information.

        Returns:
        - The created or updated company information model.
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

        Parameters:
        - **db**: The database session.
        - **info_id**: The unique identifier of the company information.
        - **company_id**: The unique identifier of the company.

        Returns:
        - Information about the company's additional information with additional statistics.

        Raises:
        - HTTPException 404: If no company information is found with the provided info_id.
        """
        info: InfoModelType = db.query(DbInfo).filter(DbInfo.id == info_id, DbInfo.is_deleted == False).first()
        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Info with id {info_id} does not exist.'
            )
        active_job_ads: int = db.query(DbAds).filter(DbAds.info_id == info_id,
                                                     DbAds.status == 'Active', ).count()
        number_of_matches: int = db.query(DbJobsMatches).filter(DbJobsMatches.company_id == company_id,
                                                                DbJobsMatches.is_deleted == False).count()

        return CompanyInfoDisplay(**info.__dict__, active_job_ads=active_job_ads,
                                  number_of_matches=number_of_matches)

    @staticmethod
    async def update_info(db: Session, info_id: str, description: str | None, location: str | None) -> InfoModelType:
        """
        Update additional information for a company.

        This method updates additional information for a company based on the provided parameters.

        Parameters:
        - **db**: The database session.
        - **info_id**: The unique identifier of the company information.
        - **description**: Optional parameter for updating the company information description.
        - **location**: Optional parameter for updating the company information location.

        Returns:
        - The updated company information model.

        Raises:
        - HTTPException 404: If no company information is found with the provided info_id.
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

        Parameters:
        - **db**: The database session.
        - **info_id**: The unique identifier of the company information to be deleted.
        - **user**: The user attempting to delete the information.

        Returns:
        - None

        Raises:
        - HTTPException 403: If the user does not have sufficient permissions to delete the information.
        - HTTPException 404: If no company information is found with the provided info_id.
        """
        company: CompanyModelType = db.query(DbCompanies).filter(DbCompanies.id == str(user.company[0].id)).first()
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

        Parameters:
        - **db**: The database session.
        - **info_id**: The unique identifier of the company information.
        - **image**: The image data to be uploaded.

        Returns:
        - A streaming response containing the uploaded image.

        Raises:
        - HTTPException 404: If no company information is found with the provided info_id.

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

        Parameters:
        - **db**: The database session.
        - **info_id**: The unique identifier of the company information.

        Returns:
        - A streaming response containing the retrieved image.

        Raises:
        - HTTPException 404: If no company information is found with the provided info_id.
        """
        info: InfoModelType = db.query(DbInfo).filter(DbInfo.id == info_id, DbInfo.is_deleted == False).first()
        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Info with id {info_id} does not exist.'
            )
        return StreamingResponse(io.BytesIO(info.picture), media_type="image/jpeg")

    @staticmethod
    async def find_matches(db: Session, company: CompanyModelType, ad_id: str, threshold: float) -> JSONResponse:
        """
         Find matches between a company's job advertisement and professionals' resume.

        This method searches for matches between a company's job advertisement and professionals' resume based on
         the provided parameters. Matches are determined using a similarity calculation of skills and other criteria.

        Parameters:
        - **db**: The database session.
        - **company**: The company model representing the searching company.
        - **ad_id**: The unique identifier of the company's job advertisement.
        - **threshold**: The percentage for adjusting the salary range and determining skill similarity.

        Returns:
        - A JSONResponse with a message indicating the result of the match search.

        Raises:
        - HTTPException 404: If the company's information is not set or if the job advertisement is not found.
        """
        result = False
        if not company.info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Please set your info first.'
            )
        ad: AdModelType = db.query(DbAds).filter(DbAds.id == ad_id, DbAds.is_deleted == False).first()
        if not ad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Ad with id {ad_id} not found.'
            )
        salary_range_adjusted_min = int(ad.min_salary - (ad.min_salary * threshold))
        salary_range_adjusted_max = int(ad.max_salary + (ad.max_salary * threshold))
        location: str = ad.location
        ad_skills = [skill.id for skill in ad.skills]
        resumes: list[AdModelType] = db.query(DbAds).filter(DbAds.is_deleted == False, DbAds.status == 'Active',
                                                            DbAds.location == location, DbAds.is_resume == True,
                                                            DbAds.min_salary >= salary_range_adjusted_min,
                                                            DbAds.min_salary <= salary_range_adjusted_max, ).all()
        if resumes:
            for resume in resumes:
                try:
                    resume_skills = [skill.id for skill in resume.skills]
                    similarity = calculate_similarity(set(resume_skills), set(ad_skills), (1 - threshold))
                    if similarity:
                        professional_id = resume.info.professional[0].id
                        new_match = DbJobsMatches(ad_id=ad_id, resume_id=resume.id, professional_id=professional_id,
                                                  company_id=company.id)
                        db.add(new_match)
                        db.commit()
                        result = True
                except IntegrityError:
                    db.rollback()
                    continue
        if result:
            return JSONResponse({
                'message': 'You have new matches!'
            })
        else:
            return JSONResponse({
                'message': 'You have no matches!'
            })

    @staticmethod
    async def get_matches_multi(db: Session, company: CompanyModelType) -> list[CompanyMatchDisplay]:
        """
         Retrieve matches for a company's job advertisements.

        This method retrieves matches for a company's job advertisements based on the provided company model.

        Parameters:
        - **db**: The database session.
        - **company**: The company model for which matches are retrieved.

        Returns: A list of CompanyMatchDisplay instances containing information about the matches.
        -
        """
        company_id: str = company.id
        matches: list[JobMatchesModelType] = db.query(DbJobsMatches).join(DbAds).filter(
            DbJobsMatches.is_deleted == False,
            DbJobsMatches.company_id == company_id).all()
        return [CompanyMatchDisplay(company_name=match.company.name,
                                    professional_name=match.professional.first_name + ' ' + match.professional.last_name,
                                    job_ad=AdDisplay(**match.ad.__dict__),
                                    resume=AdDisplay(
                                        **db.query(DbAds).filter(DbAds.id == str(match.resume_id)).first().__dict__
                                    )) for match in matches]

    @staticmethod
    async def approve_match(db: Session, resume_id: str, company_id: str) -> JSONResponse:
        """
        Approve a match between a company and a professional.

        This method approves a match between a company and a professional based on the provided parameters.

        Parameters:
        - **db**: The database session.
        - **resume_id**: The unique identifier of the professional ad to be approved.
        - **company_id**: The unique identifier of the company approving the match.

        Returns:
        - A JSONResponse with a message indicating the result of the match approval.

        Raises:
        - HTTPException 404: If the match with the provided resume_id and company_id is not found.
        """
        match: JobMatchesModelType = db.query(DbJobsMatches).filter(DbJobsMatches.is_deleted == False,
                                                                    DbJobsMatches.resume_id == resume_id,
                                                                    DbJobsMatches.company_id == company_id).first()
        if match:
            match.company_approved = True
            db.commit()
            return JSONResponse({
                'message': 'Match approved!'
            })
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Resume with id {resume_id} not found.'
            )


async def is_admin(user: UserModelType) -> bool:
    """
    Check if the user has administrative privileges.

    This method checks whether the provided user has administrative privileges based on their user type.

    Parameters:
    - **user**: The user model for whom to check administrative privileges.

    Returns:
    - True if the user has administrative privileges, False otherwise.
    """
    return user.type == 'admin'


async def is_owner(company: CompanyModelType, user_id: str) -> bool:
    """
    Check if the provided user is the owner of the company.

    This method checks whether the provided user is the owner of the specified company based on their user ID.

    Parameters:
    - **company**: The company model for which ownership is being checked.
    - **user_id**: The unique identifier of the user to check for ownership.

    Returns:
    - True if the user is the owner of the company, False otherwise.
    """
    return company.user_id == user_id
