from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.crud.crud_ad import create_new_ad, create_new_skill, add_skill_to_ad_crud, get_ad_by_id_crud, get_ads_crud, \
    get_all_skills_crud, update_ad_crud, remove_skill_from_ad_crud, delete_ad_crud, delete_skill_crud, \
    update_skill_crud
from app.db.database import get_db
from app.db.models import DbUsers
from app.schemas.ad import AdCreate, AdSkills, IncludeSkillToAddDisplay, AdDisplay, SkillToAd

router = APIRouter(tags=['ad'])


@router.post('/ads', response_model=AdCreate)
async def create_ad(schema: AdCreate, db: Annotated[Session, Depends(get_db)],
                    current_user: Annotated[DbUsers, Depends(get_current_user)]):
    return await create_new_ad(db, schema)


@router.get('/ads', response_model=List[AdDisplay])
async def get_ads(db: Annotated[Session, Depends(get_db)],
                  current_user: Annotated[DbUsers, Depends(get_current_user)],
                  description: Annotated[str, Query(description='Optional key-word search parameter')] = None,
                  location: Annotated[str, Query(description='Optional location search parameter')] = None,
                  ad_status: Annotated[str, Query(description='Optional status search parameter')] = None,
                  min_salary: Annotated[int, Query(description='Optional minimal salary search parameter')] = None,
                  max_salary: Annotated[int, Query(description='Optional maximal salary search parameter')] = None,
                  page: Annotated[int, Query(description='Optional page number query parameter', ge=1)] = 1):
    ads = await get_ads_crud(db, description, location, ad_status, min_salary, max_salary, page)
    if not ads:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no results for your search"
        )
    return ads


@router.put('/ads', response_model=AdDisplay)
async def update_ad(ad_id: str, db: Annotated[Session, Depends(get_db)],
                    current_user: Annotated[DbUsers, Depends(get_current_user)],
                    description: Annotated[str, Query(description='Optional name update parameter')] = None,
                    location: Annotated[str, Query(description='Optional contact update parameter')] = None,
                    ad_status: Annotated[str, Query(description='Optional status update parameter')] = None,
                    min_salary: Annotated[int, Query(description='Optional status update parameter')] = None,
                    max_salary: Annotated[int, Query(description='Optional status update parameter')] = None):
    updated_ad = await update_ad_crud(db, ad_id, description, location, ad_status, min_salary, max_salary)
    return updated_ad


@router.delete('/ads', status_code=status.HTTP_204_NO_CONTENT)
async def delete_ad(ad_id: str, db: Annotated[Session, Depends(get_db)],
                    current_user: Annotated[DbUsers, Depends(get_current_user)]):
    return await delete_ad_crud(db, ad_id)


@router.get('/ads/{ad_id}', response_model=AdDisplay)
async def get_ad_by_id(ad_id: str, db: Annotated[Session, Depends(get_db)],
                       current_user: Annotated[DbUsers, Depends(get_current_user)]):
    ad = await get_ad_by_id_crud(db, ad_id)
    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Ad with id {ad_id} does not exist'
        )
    return ad


@router.post('/skills', response_model=AdSkills)
async def create_skill(schema: AdSkills, db: Annotated[Session, Depends(get_db)],
                       current_user: Annotated[DbUsers, Depends(get_current_user)]):
    return await create_new_skill(db, schema)


@router.get('/skills', response_model=List[AdSkills])
async def get_skills(db: Annotated[Session, Depends(get_db)],
                     current_user: Annotated[DbUsers, Depends(get_current_user)],
                     page: Annotated[int, Query(description='Optional page number query parameter', ge=1)] = 1):
    skills = await get_all_skills_crud(db, page)
    if not skills:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no available skills, kindly add a skill first'
        )
    return skills


@router.patch('/skills', response_model=AdSkills)
async def update_skill(
        skill_name: Annotated[str, Query(..., description='Current skill name')],
        new_name: Annotated[str, Query(..., description='New skill name')],
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[DbUsers, Depends(get_current_user)]):
    skill = await update_skill_crud(db, skill_name, new_name)
    return skill


@router.delete('/skills', status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
        skill_name: Annotated[str, Query(..., description='Skill name')],
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[DbUsers, Depends(get_current_user)]):
    return await delete_skill_crud(db, skill_name)


@router.post('/ads/{ad_id}/skills/{skill_id}', response_model=IncludeSkillToAddDisplay)
async def add_skill_to_ad(
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[DbUsers, Depends(get_current_user)],
        ad_id: str,
        skill_name: Annotated[str, Query(description='Name of the skill you want to add')],
        level: Annotated[str, Query(description='Skill level, exp: "Advanced"')] = None):
    return await add_skill_to_ad_crud(db, ad_id, skill_name, level)


@router.delete('/ads/{ad_id}/skills/{skill_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_skill_from_ad(
        db: Annotated[Session, Depends(get_db)],
        ad_id: str,
        skill_name: Annotated[str, Query(description='Name of the skill you want to add')],
        current_user: Annotated[DbUsers, Depends(get_current_user)]
):
    return await remove_skill_from_ad_crud(db, ad_id, skill_name)
