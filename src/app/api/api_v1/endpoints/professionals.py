from typing import Annotated, List

from fastapi import Depends, APIRouter, Path, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
import app.crud.crud_professional as crud_professional
from app.crud.crud_user import create_user
from app.db.database import get_db
from app.db.models import DbProfessionals, DbUsers
from app.schemas.professional import ProfessionalCreate, ProfessionalCreateDisplay, ProfessionalDisplay, ProfessionalInfoDisplay, ProfessionalStatus
from app.schemas.user import UserDisplay

router = APIRouter()


@router.get('/professionals/resumes')
async def get_all_resumes(db: Annotated[Session, Depends(get_db)],
                          current_user: Annotated[DbUsers, Depends(get_current_user)]):
    crud_professional.is_user_verified(current_user)
    professional: DbProfessionals = await crud_professional.get_professional(db, current_user)

    return crud_professional.get_resumes(db, professional.info)


@router.get('/professionals', response_model=List[ProfessionalDisplay])
async def get_professionals(db: Annotated[Session, Depends(get_db)],
                      current_user: Annotated[UserDisplay, Depends(get_current_user)],
                      search_by_first_name: Annotated[str, Query(description='Optional first name search parameter')] = None,
                      search_by_last_name: Annotated[str, Query(description='Optional last name search parameter')] = None,
                      search_by_status: Annotated[ProfessionalStatus, Query(description='Optional status search parameter')] = None,
                      search_by_location: Annotated[str, Query(description='Optional location search parameter')] = None,
                      page: Annotated[int, Query(description='Optional page for pagination')] = None,
                      page_items: Annotated[int, Query(description='Optional total elements per page')] = None):
    
    crud_professional.is_user_verified(current_user)
    professionals = await crud_professional.get_all_approved_professionals(db, search_by_first_name, search_by_last_name, search_by_status, search_by_location, page, page_items)
    return professionals


@router.get('/professionals/info', response_model=ProfessionalInfoDisplay)
async def get_professional_info(db: Annotated[Session, Depends(get_db)],
                                current_user: Annotated[DbUsers, Depends(get_current_user)]):
    crud_professional.is_user_verified(current_user)
    return await crud_professional.get_info(db, current_user)


@router.post('/professionals', response_model=ProfessionalCreateDisplay)
async def create_professional(schema: ProfessionalCreate, db: Annotated[Session, Depends(get_db)]):
    return await create_user(db, schema)


@router.post('/professionals/info', status_code=201)
async def edit_professional_info(db: Annotated[Session, Depends(get_db)],
                        current_user: Annotated[DbUsers, Depends(get_current_user)],
                        location: str,
                        first_name: Annotated[str, Query(description='Optional first name update parameter')] = None,
                        last_name: Annotated[str, Query(description='Optional last name update parameter')] = None):

    crud_professional.is_user_verified(current_user)
    return await crud_professional.edit_info(db, current_user, first_name, last_name, location)


@router.patch('/professionals/summary')
async def edit_summary(db: Annotated[Session, Depends(get_db)],
                        current_user: Annotated[DbUsers, Depends(get_current_user)],
                        summary: Annotated[str, Query(description='Optional summary update parameter')] = None):
    
    crud_professional.is_user_verified(current_user)
    return await crud_professional.edit_professional_summary(db, current_user, summary)


@router.patch('/professionals/status')
async def change_professional_status(status: ProfessionalStatus, db: Annotated[Session, Depends(get_db)],
                                     current_user: Annotated[DbUsers, Depends(get_current_user)]):
    crud_professional.is_user_verified(current_user)
    return await crud_professional.change_status(status, db, current_user)


@router.patch('/professionals/resume/{resume_id}')
async def set_main_resume(resume_id: str, db: Annotated[Session, Depends(get_db)],
                               current_user: Annotated[UserDisplay, Depends(get_current_user)]):
    crud_professional.is_user_verified(current_user)
    return await crud_professional.setup_main_resume(resume_id, db, current_user)


@router.delete('/professionals/resume/{resume_id}')
def delete_professional_resume(db: Annotated[Session, Depends(get_db)],
                               current_user: Annotated[UserDisplay, Depends(get_current_user)],
                               resume_id: Annotated[str, Path(description='Optional resume id update parameter')]):
    crud_professional.is_user_verified(current_user)
    return crud_professional.delete_resume_by_id(db, resume_id)


def search_for_job_ads():
    pass
