from typing import Annotated, List

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.crud.crud_professional import change_status, delete_resume_by_id, edit_info, get_info, get_professional, \
    get_resumes
from app.crud.crud_user import create_user
from app.db.database import get_db
from app.db.models import DbProfessionals, DbUsers
from app.schemas.professional import ProfessionalCreate, ProfessionalCreateDisplay, ProfessionalDisplay, \
    ProfessionalInfoCreate, ProfessionalInfoDisplay, ProfessionalStatus
from app.schemas.user import UserDisplay

router = APIRouter()


@router.post('/professionals', response_model=ProfessionalCreateDisplay)
async def create_professional(schema: ProfessionalCreate, db: Annotated[Session, Depends(get_db)]):
    return await create_user(db, schema)


@router.get('/professionals', response_model=List[ProfessionalDisplay])
def get_professionals(db: Annotated[Session, Depends(get_db)],
                      current_user: Annotated[UserDisplay, Depends(get_current_user)]):
    professionals = db.query(DbProfessionals).join(DbProfessionals.user).filter(DbUsers.is_verified == 1).all()
    return professionals


@router.post('/professionals/info', status_code=201)
async def edit_professional_info(schema: ProfessionalInfoCreate, db: Annotated[Session, Depends(get_db)],
                                 current_user: Annotated[DbUsers, Depends(get_current_user)]):
    return await edit_info(db, schema, current_user)


@router.get('/professionals/info', response_model=ProfessionalInfoDisplay)
async def get_professional_info(db: Annotated[Session, Depends(get_db)],
                                current_user: Annotated[DbUsers, Depends(get_current_user)]):
    return await get_info(db, current_user)


@router.patch('/professionals/status')
async def change_professional_status(status: ProfessionalStatus, db: Annotated[Session, Depends(get_db)],
                                     current_user: Annotated[DbUsers, Depends(get_current_user)]):
    return await change_status(status, db, current_user)


@router.get('/professionals/resumes')
async def get_all_resumes(db: Annotated[Session, Depends(get_db)],
                          current_user: Annotated[DbUsers, Depends(get_current_user)]):
    professional: DbProfessionals = await get_professional(db, current_user)

    return get_resumes(db, professional.info)


@router.delete('/professionals/resume/{resume_id}', status_code=204)
def delete_professional_resume(resume_id: str, db: Annotated[Session, Depends(get_db)],
                               current_user: Annotated[UserDisplay, Depends(get_current_user)]):
    return delete_resume_by_id(db, resume_id)


def search_for_job_ads():
    pass
