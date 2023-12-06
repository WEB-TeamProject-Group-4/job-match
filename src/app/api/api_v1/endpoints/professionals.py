from typing import Annotated, List
from nudenet import NudeDetector
import os

from fastapi import Depends, APIRouter, File, HTTPException, Path, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.security import all_labels
import app.crud.crud_professional as crud_professional
from app.crud.crud_user import create_user
from app.db.database import get_db
from app.db.models import DbProfessionals, DbUsers
from app.schemas.professional import ProfessionalAdMatchDisplay, ProfessionalCreate, ProfessionalCreateDisplay, ProfessionalDisplay, ProfessionalInfoDisplay, ProfessionalStatus
from app.schemas.user import UserDisplay

router = APIRouter()


@router.get('/professionals/resumes')
async def get_all_resumes(db: Annotated[Session, Depends(get_db)],
                          verified_user: Annotated[DbUsers, Depends(crud_professional.is_user_verified)]):
    """
    Retrieve all resumes associated with the authenticated professional.

    Parameters:
    - `db` (Session): The SQLAlchemy database session dependency.
    - `verified_user` (DbUsers): The verified user obtained from the dependency.

    Returns:
    List[Resume]: A list of resumes associated with the authenticated professional.

    Raises:
    HTTPException: If the user is not verified or if there's an issue retrieving the resumes.
    """
    professional: DbProfessionals = await crud_professional.get_professional(db, verified_user)

    return crud_professional.get_resumes(db, professional)


@router.get('/professionals', response_model=List[ProfessionalDisplay])
async def get_professionals(db: Annotated[Session, Depends(get_db)],
                      _: Annotated[UserDisplay, Depends(get_current_user)],
                      search_by_first_name: Annotated[str, Query(description='Optional first name search parameter')] = None,
                      search_by_last_name: Annotated[str, Query(description='Optional last name search parameter')] = None,
                      search_by_status: Annotated[ProfessionalStatus, Query(description='Optional status search parameter')] = None,
                      search_by_location: Annotated[str, Query(description='Optional location search parameter')] = None,
                      page: Annotated[int, Query(description='Optional page for pagination')] = None,
                      page_items: Annotated[int, Query(description='Optional total elements per page')] = None):
    """
    Retrieve a list of professionals based on specified search parameters.

    Parameters:
    - `db` (Session): The SQLAlchemy database session dependency.
    - `_` (UserDisplay): The current user obtained from the dependency.
    - `search_by_first_name` (str, optional): Optional first name search parameter.
    - `search_by_last_name` (str, optional): Optional last name search parameter.
    - `search_by_status` (ProfessionalStatus, optional): Optional status search parameter.
    - `search_by_location` (str, optional): Optional location search parameter.
    - `page` (int, optional): Optional page number for pagination.
    - `page_items` (int, optional): Optional total elements per page.

    Returns:
    List[ProfessionalDisplay]: A list of professionals based on the specified search parameters.

    Raises:
    HTTPException: If there's an issue retrieving the professionals.
    """
    professionals = await crud_professional.get_all_approved_professionals(db, search_by_first_name, search_by_last_name, search_by_status, search_by_location, page, page_items)
    return professionals


@router.get('/professionals/info', response_model=ProfessionalInfoDisplay)
async def get_professional_info(db: Annotated[Session, Depends(get_db)],
                                verified_user: Annotated[DbUsers, Depends(crud_professional.is_user_verified)]):
    """
    Retrieve detailed information about the authenticated professional.

    Parameters:
    - `db` (Session): The SQLAlchemy database session dependency.
    - `verified_user` (DbUsers): The verified user obtained from the dependency.

    Returns:
    ProfessionalInfoDisplay: Detailed information about the authenticated professional.

    Raises:
    HTTPException: If the user is not verified or if there's an issue retrieving the professional's information.
    """
    return await crud_professional.get_info(db, verified_user)


@router.get('/professionals/image')
async def get_image(db: Annotated[Session, Depends(get_db)],
                 current_user: Annotated[DbUsers, Depends(crud_professional.is_user_verified)]):
    """
    Get the image associated with the professional profile.

    Parameters:
    - `db` (Session): The SQLAlchemy database session.
    - `current_user` (DbUsers): The authenticated user.

    Returns:
    StreamingResponse: A streaming response containing the professional's image.
                      Returns a 404 error if the professional or image is not found.
    """

    return await crud_professional.get_image(db, current_user.professional[0].info_id)


@router.post('/professionals', response_model=ProfessionalCreateDisplay)
async def create_professional(schema: ProfessionalCreate, db: Annotated[Session, Depends(get_db)]):
    """
    Create a new professional based on the provided information.

    Parameters:
    - `schema` (ProfessionalCreate): The data schema for creating a professional.
    - `db` (Session): The SQLAlchemy database session dependency.

    Returns:
    ProfessionalCreateDisplay: Information about the created professional.

    Raises:
    HTTPException: If there's an issue creating the professional.
    """
    return await create_user(db, schema)


@router.post('/professionals/info', status_code=201)
async def edit_professional_info(db: Annotated[Session, Depends(get_db)],
                        verified_user: Annotated[DbUsers, Depends(crud_professional.is_user_verified)],
                        location: str,
                        first_name: Annotated[str, Query(description='Optional first name update parameter')] = None,
                        last_name: Annotated[str, Query(description='Optional last name update parameter')] = None):
    """
    Update information about the authenticated professional.

    Parameters:
    - `db` (Session): The SQLAlchemy database session dependency.
    - `verified_user` (DbUsers): The verified user obtained from the dependency.
    - `location` (str): The updated location information.
    - `first_name` (str, optional): Optional updated first name parameter.
    - `last_name` (str, optional): Optional updated last name parameter.

    Returns:
    dict: A message indicating the successful update.

    Raises:
    HTTPException: If the user is not verified or if there's an issue updating the professional's information.
    """
    return await crud_professional.edit_info(db, verified_user, first_name, last_name, location)


@router.post('/professionals/image')
async def upload(db: Annotated[Session, Depends(get_db)],
                 current_user: Annotated[DbUsers, Depends(crud_professional.is_user_verified)],
                 image: Annotated[UploadFile, File()]):
    """
    Upload a new image for the professional profile.

    Parameters:
    - `db` (Session): The SQLAlchemy database session.
    - `current_user` (DbUsers): The authenticated user.
    - `image` (UploadFile): The image file to be uploaded.

    Returns:
    Dict[str, str]: A dictionary with a message indicating the success of the image upload.
                   Returns a 404 error if the professional profile is not found.
    """
    file = await image.read()
    file_path = './image.jpeg'
    detector = NudeDetector()

    with open(file_path, "wb") as f:
        f.write(file)

        result = detector.detect(file_path)
        if any(element['class'] in all_labels for element in result):
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail='This photo is with explicit content.'
            ) 

        os.remove(file_path)
        
    binary_pic = bytearray(file)
    return await crud_professional.upload_picture(db, current_user.professional[0].info_id, binary_pic)


@router.patch('/professionals/summary')
async def edit_summary(db: Annotated[Session, Depends(get_db)],
                        verified_user: Annotated[DbUsers, Depends(crud_professional.is_user_verified)],
                        summary: str):
    """
    Update the professional summary for the authenticated professional.

    Parameters:
    - `db` (Session): The SQLAlchemy database session dependency.
    - `verified_user` (DbUsers): The verified user obtained from the dependency.
    - `summary` (str): The updated professional summary.

    Returns:
    dict: A message indicating the successful update.

    Raises:
    HTTPException: If the user is not verified or if there's an issue updating the professional's summary.
    """
    return await crud_professional.edit_professional_summary(db, verified_user, summary)


@router.patch('/professionals/status')
async def change_professional_status(status: ProfessionalStatus, db: Annotated[Session, Depends(get_db)],
                                     verified_user: Annotated[DbUsers, Depends(crud_professional.is_user_verified)]):
    """
    Change the status of the authenticated professional.

    Parameters:
    - `status` (ProfessionalStatus): The updated professional status.
    - `db` (Session): The SQLAlchemy database session dependency.
    - `verified_user` (DbUsers): The verified user obtained from the dependency.

    Returns:
    dict: A message indicating the successful status change.

    Raises:
    HTTPException: If the user is not verified or if there's an issue changing the professional's status.
    """
    return await crud_professional.change_status(status, db, verified_user)


@router.patch('/professionals/resume/{resume_id}')
async def set_main_resume(resume_id: str, db: Annotated[Session, Depends(get_db)],
                               verified_user: Annotated[UserDisplay, Depends(crud_professional.is_user_verified)]):
    """
    Set the specified resume as the main resume for the authenticated professional.

    Parameters:
    - `resume_id` (str): The ID of the resume to be set as the main resume.
    - `db` (Session): The SQLAlchemy database session dependency.
    - `verified_user` (UserDisplay): The verified user obtained from the dependency.

    Returns:
    dict: A message indicating the successful setup of the main resume.

    Raises:
    HTTPException: If the user is not verified or if there's an issue setting up the main resume.
    """
    return await crud_professional.setup_main_resume(resume_id, db, verified_user)


# @router.delete('/professionals/resume/{resume_id}')
# async def delete_professional_resume(db: Annotated[Session, Depends(get_db)],
#                                verified_user: Annotated[UserDisplay, Depends(crud_professional.is_user_verified)],
#                                resume_id: Annotated[str, Path(description='Optional resume id update parameter')]):
#     return await crud_professional.delete_resume_by_id(db, verified_user, resume_id)


@router.delete('/professionals/{professional_id}', status_code=204)
async def delete_professional_profile(db: Annotated[Session, Depends(get_db)],
                               _: Annotated[UserDisplay, Depends(crud_professional.is_user_verified)],
                               professional_id: Annotated[str, Path(description='Optional resume id update parameter')]):
    """
    Delete the profile of a specific professional.

    Parameters:
    - `db` (Session): The SQLAlchemy database session dependency.
    - `_` (UserDisplay): The current user obtained from the dependency.
    - `professional_id` (str): The ID of the professional profile to be deleted.

    Returns:
    None

    Raises:
    HTTPException: If the user is not verified or if there's an issue deleting the professional profile.
    """
    return await crud_professional.delete_professional_by_id(db, professional_id)


@router.get('/professionals/matches-search')
async def search_for_match(db: Annotated[Session, Depends(get_db)],
                            current_user: Annotated[DbUsers, Depends(crud_professional.is_user_verified)],
                            ad_id: Annotated[str, Query(title='Active ad id')],
                            threshold: float = Query(0, title="Threshold Percentage", description="Percentage for adjusting salary range", ge=0, le=100)):
    """
    Get matches for a professional based on specified threshold.

    Parameters:
    - `db`: SQLAlchemy database session dependency.
    - `current_user`: Current authenticated user (DbUsers).
    - `threshold` (float): Percentage for adjusting salary range (between 0 and 100).

    Returns:
    - A list of matches for the professional based on the specified threshold.

    Raises:
    - HTTPException 400: If the threshold is not within the valid range (0 to 100).
    """
    result = round(threshold / 100, 2)
    return await crud_professional.find_matches(db, current_user, result, ad_id)


@router.get('/professionals/matches-all', response_model=list[ProfessionalAdMatchDisplay])
async def get_all_matches(db: Annotated[Session, Depends(get_db)],
                               current_user: Annotated[DbUsers, Depends(crud_professional.is_user_verified)]):
    """
    Retrieve a list of all matches for the authenticated professional.

    Parameters:
    - `db`: SQLAlchemy database session dependency.
    - `current_user`: Current authenticated user (DbUsers).

    Returns:
    - A list of ProfessionalAdMatchDisplay instances representing all matches.
    """
    return await crud_professional.get_potential_matches(db, current_user)


@router.patch('/professionals/matches-approve')
async def approve_match(db: Annotated[Session, Depends(get_db)],
                               current_user: Annotated[DbUsers, Depends(crud_professional.is_user_verified)],
                               ad_id: Annotated[str, Query(title="Ad id", description="Looking for a match by ad id for approval")]):
    """
    Approve a match for a professional based on the provided ad_id.

    Parameters:
    - db (Session): The database session dependency.
    - current_user (DbUsers): The current authenticated user, verified as a professional.
    - ad_id (str): The id of the advertisement for which a match is to be approved.

    Returns:
    - The result of approving the match, typically a success message or status.

    Raises:
    - HTTPException(400): If the ad_id is not valid or if there is an issue with the approval process.
    - HTTPException(401): If the user is not verified as a professional.
    - HTTPException(404): If the specified advertisement id is not found.
    """
    return await crud_professional.approve_match_by_ad_id(db, current_user, ad_id)


    














