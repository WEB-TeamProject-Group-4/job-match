from typing import Annotated, List

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.crud.crud_ad import (create_ad_crud, create_new_skill, add_skill_to_ad_crud, get_ad_by_id_crud, \
                              get_job_ads_crud, get_skills_crud, update_ad_company_crud, remove_skill_from_ad_crud,
                              delete_ad_crud,
                              delete_skill_crud, update_skill_crud, get_resumes_crud, update_ad_professional_crud)
from app.db.database import get_db
from app.db.models import DbUsers
from app.schemas.ad import AdCreate, AdSkills, IncludeSkillToAddDisplay, AdDisplay, JobAdStatus, SkillLevel, \
    ResumeStatus

router = APIRouter(tags=['ad'])


@router.post('/ads', response_model=AdCreate)
async def create_ad(db: Annotated[Session, Depends(get_db)],
                    current_user: Annotated[DbUsers, Depends(get_current_user)],
                    schema: AdCreate):
    return await create_ad_crud(db, current_user, schema)


@router.get('/ads/companies', response_model=List[AdDisplay])
async def get_resumes(db: Annotated[Session, Depends(get_db)],
                      current_user: Annotated[DbUsers, Depends(get_current_user)],
                      description: Annotated[str, Query(description='Optional key-word search parameter')] = None,
                      location: Annotated[str, Query(description='Optional location search parameter')] = None,
                      ad_status: Annotated[ResumeStatus, Query(description='Optional status search parameter')] = None,
                      min_salary: Annotated[int, Query(description='Optional minimal salary search parameter')] = None,
                      max_salary: Annotated[int, Query(description='Optional maximal salary search parameter')] = None,
                      page: Annotated[int, Query(description='Optional query parameter. Results = 2', ge=1)] = 1):
    ads = await get_resumes_crud(db, current_user.type, description, location, ad_status, min_salary, max_salary, page)
    return ads


@router.get('/ads/professionals', response_model=List[AdDisplay])
async def get_job_ads(db: Annotated[Session, Depends(get_db)],
                      current_user: Annotated[DbUsers, Depends(get_current_user)],
                      description: Annotated[str, Query(description='Optional key-word search parameter')] = None,
                      location: Annotated[str, Query(description='Optional location search parameter')] = None,
                      ad_status: Annotated[JobAdStatus, Query(description='Optional status search parameter')] = None,
                      min_salary: Annotated[int, Query(description='Optional minimal salary search parameter')] = None,
                      max_salary: Annotated[int, Query(description='Optional maximal salary search parameter')] = None,
                      page: Annotated[int, Query(description='Optional query parameter. Results = 2', ge=1)] = 1):
    ads = await get_job_ads_crud(db, current_user.type, description, location, ad_status, min_salary, max_salary, page)
    return ads


@router.put('/ads/companies', response_model=AdDisplay)
async def update_company_ad(db: Annotated[Session, Depends(get_db)],
                            current_user: Annotated[DbUsers, Depends(get_current_user)],
                            ad_id: str,
                            description: Annotated[
                                str, Query(description='Optional description update parameter')] = None,
                            location: Annotated[
                                str, Query(description='Optional location update parameter')] = None,
                            ad_status: Annotated[
                                JobAdStatus, Query(description='Optional status update parameter')] = None,
                            min_salary: Annotated[
                                int, Query(description='Optional minimal salary update parameter')] = None,
                            max_salary: Annotated[
                                int, Query(description='Optional maximal salary update parameter')] = None):
    updated_ad = await update_ad_company_crud(db, current_user, ad_id, description,
                                              location, ad_status, min_salary, max_salary)
    return updated_ad


@router.put('/ads/professionals', response_model=AdDisplay)
async def update_professional_ad(db: Annotated[Session, Depends(get_db)],
                                 current_user: Annotated[DbUsers, Depends(get_current_user)],
                                 ad_id: str,
                                 description: Annotated[
                                     str, Query(description='Optional description update parameter')] = None,
                                 location: Annotated[
                                     str, Query(description='Optional location update parameter')] = None,
                                 ad_status: Annotated[
                                     ResumeStatus, Query(description='Optional status update parameter')] = None,
                                 min_salary: Annotated[
                                     int, Query(description='Optional minimal salary update parameter')] = None,
                                 max_salary: Annotated[
                                     int, Query(description='Optional maximal salary update parameter')] = None):
    updated_ad = await update_ad_professional_crud(db, current_user, ad_id, description,
                                                   location, ad_status, min_salary, max_salary)
    return updated_ad


@router.delete('/ads', status_code=status.HTTP_204_NO_CONTENT)
async def delete_ad(db: Annotated[Session, Depends(get_db)],
                    current_user: Annotated[DbUsers, Depends(get_current_user)],
                    ad_id: str):
    return await delete_ad_crud(db, ad_id)


@router.get('/ads/{ad_id}', response_model=AdDisplay)
async def get_ad_by_id(db: Annotated[Session, Depends(get_db)],
                       current_user: Annotated[DbUsers, Depends(get_current_user)],
                       ad_id: str):
    ad = await get_ad_by_id_crud(db, ad_id)
    return ad


@router.post('/skills', response_model=AdSkills)
async def create_skill(db: Annotated[Session, Depends(get_db)],
                       current_user: Annotated[DbUsers, Depends(get_current_user)],
                       schema: AdSkills):
    return await create_new_skill(db, schema)


@router.get('/skills', response_model=List[AdSkills])
async def get_skills(db: Annotated[Session, Depends(get_db)],
                     current_user: Annotated[DbUsers, Depends(get_current_user)],
                     page: Annotated[int, Query(description='Optional page number query parameter', ge=1)] = 1):
    skills = await get_skills_crud(db, page)
    return skills


@router.patch('/skills', response_model=AdSkills)
async def update_skill(db: Annotated[Session, Depends(get_db)],
                       current_user: Annotated[DbUsers, Depends(get_current_user)],
                       skill_name: Annotated[str, Query(..., description='Current skill name')],
                       new_name: Annotated[str, Query(..., description='New skill name')]):
    skill = await update_skill_crud(db, skill_name, new_name)
    return skill


@router.delete('/skills', status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(db: Annotated[Session, Depends(get_db)],
                       current_user: Annotated[DbUsers, Depends(get_current_user)],
                       skill_name: Annotated[str, Query(..., description='Skill name')]):
    return await delete_skill_crud(db, skill_name)


@router.post('/ads/{ad_id}/skills/{skill_id}', response_model=IncludeSkillToAddDisplay)
async def add_skill_to_ad(db: Annotated[Session, Depends(get_db)],
                          current_user: Annotated[DbUsers, Depends(get_current_user)],
                          ad_id: str,
                          skill_name: Annotated[str, Query(description='Include skill')],
                          level: Annotated[SkillLevel, Query(description='Select skill level')] = SkillLevel.BEGINNER):
    return await add_skill_to_ad_crud(db, ad_id, skill_name, level)


@router.delete('/ads/{ad_id}/skills/{skill_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_skill_from_ad(db: Annotated[Session, Depends(get_db)],
                               current_user: Annotated[DbUsers, Depends(get_current_user)],
                               ad_id: str,
                               skill_name: Annotated[str, Query(description='Remove skill')]):
    return await remove_skill_from_ad_crud(db, ad_id, skill_name)
