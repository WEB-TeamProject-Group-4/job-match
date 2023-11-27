from typing import Annotated, Dict, List, Optional, Type, Union

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.core.auth import get_current_user
from app.db.models import DbAds, DbInfo, DbProfessionals, DbUsers
from app.schemas.professional import ProfessionalInfoDisplay


DEFAULT_VALUE_ITEMS_PER_PAGE = 10


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
        picture=professional.info.picture,
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
    
    




    


    
