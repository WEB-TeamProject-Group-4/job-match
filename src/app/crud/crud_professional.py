from typing import Annotated, Dict, List, Optional, Type, Union
import io

from fastapi import Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.auth import get_current_user
from app.db.models import DbAds, DbCompanies, DbInfo, DbJobsMatches, DbProfessionals, DbUsers
from app.schemas.professional import ProfessionalAdMatchDisplay, ProfessionalInfoDisplay


DEFAULT_VALUE_ITEMS_PER_PAGE = 10
MAX_IMAGE_SIZE_BYTES = 300 * 300


async def edit_info(db: Session, user: DbUsers, first_name: Optional[str], 
                    last_name: Optional[str], location: str) -> Dict[str, str]:
    """
    Edit information for the specified professional.

    Parameters:
    - `db` (Session): The SQLAlchemy database session.
    - `user` (DbUsers): The user whose information is being edited.
    - `first_name` (str, optional): The updated first name.
    - `last_name` (str, optional): The updated last name.
    - `location` (str): The updated location.

    Returns:
    Dict[str, str]: A message indicating the success of the update.

    Raises:
    Exception: If there's an issue updating the professional's information.
    """
    professional: DbProfessionals = await get_professional(db, user)
   
    if first_name:
        professional.first_name = first_name.capitalize()
    if last_name:
        professional.last_name = last_name.capitalize()
    if location:
        if professional.info is None:
            await create_professional_info(db, professional, summary="Your default summary", location=location)
        else:
            professional.info.location = location.capitalize()
            professional.info.is_deleted = False
    
    db.commit()
    
    return {"message": "Update successful"}


async def create_professional_info(db: Session, professional: DbProfessionals, summary: str, location: str) -> None:
    """
    Create professional information for the specified professional.

    Parameters:
    - `db` (Session): The SQLAlchemy database session.
    - `professional` (DbProfessionals): The professional for whom information is being created.
    - `summary` (str): The summary information for the professional.
    - `location` (str): The location information for the professional.

    Returns:
    None

    Raises:
    HTTPException: If either the summary or location is missing.
    """
    if summary and location:
        new_info = DbInfo(description=summary,location=location)
        db.add(new_info)
        db.commit()
        db.refresh(new_info)

        professional.info = new_info
        db.commit()
        
    else:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fields should be valid: 'summary' and 'location'!")
    

async def edit_professional_summary(db: Session, user: DbUsers, summary: str) -> Dict[str, str]:
    professional: DbProfessionals = await get_professional(db, user)
    """
    Edit the summary for the specified professional.

    Parameters:
    - `db` (Session): The SQLAlchemy database session.
    - `user` (DbUsers): The user whose summary is being edited.
    - `summary` (str): The updated summary.

    Returns:
    Dict[str, str]: A message indicating the success of the update.

    Raises:
    Exception: If there's an issue updating the professional's summary.
    """
    if professional.info is None:
        new_info = DbInfo(description=summary,location='')
        db.add(new_info)
        db.commit()
        db.refresh(new_info)

        professional.info = new_info
        db.commit()

    else:
        professional.info.description = summary
        db.commit()
    
    
    return {'message': 'Your summary has been updated successfully'}


async def get_info(db: Session, user: DbUsers) -> ProfessionalInfoDisplay:
    """
    Get detailed information about the specified professional.

    Parameters:
    - `db` (Session): The SQLAlchemy database session.
    - `user` (DbUsers): The user whose information is being retrieved.

    Returns:
    ProfessionalInfoDisplay: Detailed information about the professional.

    Raises:
    HTTPException: If the professional information is not found or if there's an issue retrieving it.
    """
    professional: DbProfessionals = await get_professional(db, user)
    if professional.info is None or professional.info.is_deleted == True:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Please edit your personal information.')
    
    resumes = get_resumes(db, professional)

    return ProfessionalInfoDisplay(
        first_name=professional.first_name,
        last_name=professional.last_name,
        summary=professional.info.description,
        location=professional.info.location,
        status=professional.status,
        active_resumes=len(resumes)
    )
    

def get_resumes(db: Session, professional: DbProfessionals)  -> List[Dict[Union[str, int, bool], Optional[str]]]:
    """
    Get a list of resumes associated with the specified professional.

    Parameters:
    - `db` (Session): The SQLAlchemy database session.
    - `professional` (DbProfessionals): The professional whose resumes are being retrieved.

    Returns:
    List[Dict[Union[str, int, bool], Optional[str]]]: A list of resumes with relevant information.

    Note:
    If there are no resumes or an issue occurs during retrieval, an empty list will be returned.
    """
    try:
        resumes_db = db.query(DbAds).filter(DbAds.info_id == professional.info.id, DbAds.is_deleted == False).all()
    except AttributeError:
        return []
    resumes = [
            {
                "id": resume.id,
                "description": resume.description,
                "location": resume.location,
                "status": resume.status,
                "min_salary": resume.min_salary,
                "max_salary": resume.max_salary,
            }
            for resume in resumes_db
        ]

    return resumes


async def change_status(status: str, db: Session, user: DbProfessionals) -> Dict[str, str]:
    """
    Change the status of the specified professional.

    Parameters:
    - `status` (str): The updated status.
    - `db` (Session): The SQLAlchemy database session.
    - `user` (DbProfessionals): The professional whose status is being updated.

    Returns:
    Dict[str, str]: A message indicating the success of the status change.

    Raises:
    Exception: If there's an issue changing the professional's status.
    """
    professional: DbProfessionals = await get_professional(db, user)
    professional.status = status
    db.commit()

    return {'message': 'Status changed successfully!'}


async def get_professional(db: Session, user: DbUsers) -> DbProfessionals:
    """
    Get the professional associated with the specified user.

    Parameters:
    - `db` (Session): The SQLAlchemy database session.
    - `user` (DbUsers): The user whose professional information is being retrieved.

    Returns:
    DbProfessionals: The professional associated with the user.

    Raises:
    HTTPException: If the professional is not found or if the user is not logged in as a professional.
    """
    professional = (db.query(DbProfessionals).filter(DbProfessionals.user_id == user.id, DbProfessionals.is_deleted == False).first())
    if not professional:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='You are not logged as professional')
    
    return professional


async def delete_resume_by_id(db: Session, user: DbUsers, resume_id: str):
    professional: DbProfessionals = await get_professional(db, user)
    resume:DbAds = db.query(DbAds).filter(DbAds.id == resume_id, DbAds.is_deleted == False).first()
    if resume and resume.info.id == professional.info.id:
        db.delete(resume)
        db.commit()

        raise HTTPException(status_code=204, detail="Main resume changed successfully")
    
    raise HTTPException(status_code=404, detail="Resume not found")

    
async def delete_professional_by_id(db: Session, professional_id: str) -> None:
    """
    Delete the professional and associated resumes by ID.

    Parameters:
    - `db` (Session): The SQLAlchemy database session.
    - `professional_id` (str): The ID of the professional to be deleted.

    Returns:
    None

    Note:
    This function soft deletes the professional and marks associated resumes as deleted.
    """
    professional: DbProfessionals = db.query(DbProfessionals).filter(DbProfessionals.id == professional_id).first()
    resumes:DbAds = db.query(DbAds).filter(DbAds.info_id == professional.info_id).all()
    if resumes:
        for resume in resumes:
            resume.is_deleted = True

    if professional:
        professional.mark_as_deleted(db)
        return


async def setup_main_resume(resume_id: str, db: Session, user: DbUsers) -> Dict[str, str]:
    """
    Set the specified resume as the main resume for the authenticated professional.

    Parameters:
    - `resume_id` (str): The ID of the resume to be set as the main resume.
    - `db` (Session): The SQLAlchemy database session.
    - `user` (DbUsers): The authenticated user.

    Returns:
    Dict[str, str]: A message indicating the success of setting up the main resume.

    Raises:
    Exception: If there's an issue setting up the main resume.
    """
    professional: DbProfessionals = await get_professional(db, user)
    resume = db.query(DbAds).filter(DbAds.id == resume_id, DbAds.is_deleted == False).first()
    if resume:
        professional.info.main_ad = resume.id
        db.commit()

        return {'message': 'Main resume changed successfully'}
    
    return {"message": "Resume not found"}


def is_user_verified(user: Annotated[DbUsers, Depends(get_current_user)]) -> Optional[None]:
    """
    Verify that the user is a verified professional.

    Parameters:
    - `user` (DbUsers): The user obtained from the dependency.

    Returns:
    None

    Raises:
    HTTPException: If the user is not verified or is not of type 'professional'.
    """
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Please verify your account'
        )
    if not user.type == 'professional':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN
        )
    return user


async def get_all_approved_professionals(db: Session, first_name: Optional[str],last_name: Optional[str],
                                         status: Optional[str], location: Optional[str], page: Optional[int], page_items: Optional[int]) -> List[Type[DbProfessionals]]:
    """
    Get a paginated list of all approved professionals based on specified filters.

    Parameters:
    - `db` (Session): The SQLAlchemy database session.
    - `first_name` (str, optional): Optional first name search parameter.
    - `last_name` (str, optional): Optional last name search parameter.
    - `status` (str, optional): Optional status search parameter.
    - `location` (str, optional): Optional location search parameter.
    - `page` (int, optional): Optional page for pagination.
    - `page_items` (int, optional): Optional total elements per page.

    Returns:
    List[Type[DbProfessionals]]: A paginated list of approved professionals based on the specified filters.
    """
    queries = [DbUsers.is_verified == True, DbUsers.is_deleted == False]
    if first_name:
        queries.append(DbProfessionals.first_name.like(f"%{first_name}%"))
    if last_name:
        queries.append(DbProfessionals.last_name.like(f"%{last_name}%"))
    if status:
        queries.append(DbProfessionals.status == status)
    if location:
        queries.append(DbInfo.location.ilike(f"%{location}%"))

    page = page if page is not None else 1
    page_items = page_items if page_items is not None else DEFAULT_VALUE_ITEMS_PER_PAGE

    professionals = (db.query(DbProfessionals).join(DbProfessionals.user).outerjoin(DbProfessionals.info).filter(*queries))
    total_elements = professionals.count()

    return professionals.offset((page - 1) * page_items).limit(page_items).all()


async def upload_picture(db: Session, info_id: str, image: bytearray) -> Dict[str, str]:
    """
    Uploads a user's profile picture to the database.

    Parameters:
    - `db` (Session): The SQLAlchemy database session.
    - `info_id` (str): The ID of the user's information record.
    - `image` (bytearray): The binary representation of the image to be uploaded.

    Returns:
    Dict[str, str]: A dictionary with a message indicating the success of the image upload.

    Raises:
    HTTPException: If the user's information is not found or if there's an issue with the image size.
    """
    user_info:DbInfo = db.query(DbInfo).filter(DbInfo.id == info_id, DbInfo.is_deleted == False).first()
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Please edit your personal information.'
        )
    
    if len(image) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Image size exceeds the maximum allowed size.'
        )
    
    user_info.picture = image
    db.commit()
    return {"message": "Image uploaded successfully"}


async def get_image(db: Session, info_id: DbUsers) -> StreamingResponse:
    """
    Retrieves a user's profile picture as a streaming response.

    Parameters:
    - `db` (Session): The SQLAlchemy database session.
    - `info_id` (DbUsers): The ID of the user's information record.

    Returns:
    StreamingResponse: A streaming response containing the user's profile picture.

    Raises:
    HTTPException: If the user's information is not found.
    """
    user_info:DbInfo = db.query(DbInfo).filter(DbInfo.id == info_id, DbInfo.is_deleted == False).first()
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Please edit your personal information.'
        )
    
    return StreamingResponse(io.BytesIO(user_info.picture), media_type="image/jpeg")


async def find_matches(db: Session, user: DbUsers, threshold: float) -> Dict[str, str]:
    result = False
    professional: DbProfessionals = await get_professional(db, user)
    if not professional.info:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail='You have no matches'
        )
    resumes:DbAds = db.query(DbAds).filter(DbAds.info_id == professional.info_id).all()
    if not resumes:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail='You have no matches'
        )
    
    for resume in resumes:
        salary_range_adjusted_min = int(resume.min_salary - (resume.min_salary * threshold))
        salary_range_adjusted_max = int(resume.max_salary + (resume.max_salary * threshold))
        resume_skills = [skill.id for skill in resume.skills]
        ads = db.query(DbAds).filter(
            DbAds.is_deleted == False, 
            DbAds.status == 'Active', 
            DbAds.location == resume.location, 
            DbAds.min_salary >= salary_range_adjusted_min, 
            DbAds.max_salary <= salary_range_adjusted_max, 
            DbAds.is_resume == 0).all()
        
        if ads:
            for ad in ads:
                try:
                    ad_skills = [skill.id for skill in ad.skills]
                    company = db.query(DbCompanies.id).join(DbInfo, DbAds.info).filter(DbAds.id == ad.id).first()
                    company_id = company[0]
                    similarity = calculate_similarity(set(resume_skills), set(ad_skills), threshold=(1-threshold))
                    if similarity:
                        new_match = DbJobsMatches(ad_id=ad.id, professional_id=professional.id, company_id=company_id,
                                            approved=False)
                        db.add(new_match)
                        result = True
                        db.commit()
                except IntegrityError as error:
                    db.rollback()
                    continue

    if result:
        return {'message': 'You have new matches!'}

    raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail='You have no matches'
        )


def calculate_similarity(resume_skills: set, ad_skills: set, threshold: float):
    intersection_size = len(resume_skills.intersection(ad_skills))
    union_size = len(resume_skills.union(ad_skills))

    if union_size == 0:
        return 0
    else:
        similarity = intersection_size / union_size
    
    return similarity >= threshold


async def get_matches(db :Session, user: DbUsers) -> list[ProfessionalAdMatchDisplay]:
    """
    Retrieve a list of matches for the authenticated professional.

    Parameters:
    - `db` (Session): The SQLAlchemy database session.
    - `user` (DbUsers): The authenticated user.

    Returns:
    List[ProfessionalAdMatchDisplay]: A list of matches represented as ProfessionalAdMatchDisplay instances.
    """
    matches: List[DbJobsMatches] = (db.query(DbJobsMatches).join(DbAds, DbJobsMatches.ad_id == DbAds.id)
    .filter(DbJobsMatches.professional_id == user.professional[0].id, DbJobsMatches.is_deleted == False)
    .all())

    return [
    ProfessionalAdMatchDisplay(
        ad_id=match.ad_id,
        description=match.ad.description,
        location=match.ad.location,
        status=match.ad.status,
        min_salary=match.ad.min_salary,
        max_salary=match.ad.max_salary,
        is_approved=match.approved
    )
    for match in matches
]


async def approve_match_by_ad_id(db: Session, user: DbUsers, ad_id: str) -> Dict[str, str]:
    """
    Approve a match by updating the approval status based on the provided ad ID.

    Parameters:
    - `db` (Session): The SQLAlchemy database session.
    - `user` (DbUsers): The authenticated user.
    - `ad_id` (str): The ID of the ad associated with the match to be approved.

    Returns:
    Dict[str, str]: A dictionary indicating the success of the operation.

    Raises:
    HTTPException: If the ad with the specified ID is not found in job matches.
    """
    ad_in_job_matches: DbJobsMatches = db.query(DbJobsMatches).filter(DbJobsMatches.ad_id == ad_id, DbJobsMatches.is_deleted == False).first()
    if ad_in_job_matches:
        ad_in_job_matches.approved = True
        db.commit()
        return {'message': 'Match approved!'}

    raise HTTPException(
        status.HTTP_404_NOT_FOUND,
        detail=f"There is no ad with ID:{ad_id}"
    )



    



    
    




    


    
