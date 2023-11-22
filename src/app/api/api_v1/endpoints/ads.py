from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.crud.crud_ad import create_new_ad, create_new_skill, add_skill_to_ad, get_ad_by_id_crud, get_all_ads_crud, \
    get_all_skills_crud, update_ad_crud
from app.db.database import get_db
from app.db.models import DbUsers
from app.schemas.ad import AdCreate, AdSkills, IncludeSkillToAdd, IncludeSkillToAddDisplay, AdDisplay

router = APIRouter()


@router.post('/ads', response_model=AdCreate)
async def create_add(schema: AdCreate, db: Annotated[Session, Depends(get_db)],
                     current_user: Annotated[DbUsers, Depends(get_current_user)]):
    return await create_new_ad(db, schema)


@router.get('/ads', response_model=List[AdDisplay])
async def get_all_ads(db: Annotated[Session, Depends(get_db)],
                      current_user: Annotated[DbUsers, Depends(get_current_user)]):
    ads = await get_all_ads_crud(db)
    if not ads:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no available ads"
        )
    return ads


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
                     current_user: Annotated[DbUsers, Depends(get_current_user)]):
    skills = await get_all_skills_crud(db)
    if not skills:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no available skills, kindly add a skill first'
        )
    return skills


@router.post('/ads/{ad_id}/add-skill/{skill_id}', response_model=IncludeSkillToAddDisplay)
async def add_skill_to_existing_ad(schema: IncludeSkillToAdd, db: Annotated[Session, Depends(get_db)],
                                   current_user: Annotated[DbUsers, Depends(get_current_user)]):
    return await add_skill_to_ad(db, schema)


@router.put('/ads/{ad_id}', response_model=AdDisplay)
async def update_ad(ad_id: str, db: Annotated[Session, Depends(get_db)],
                    current_user: Annotated[DbUsers, Depends(get_current_user)],
                    description: Annotated[str, Query(description='Optional name update parameter')] = None,
                    location: Annotated[str, Query(description='Optional contact update parameter')] = None,
                    status: Annotated[str, Query(description='Optional status update parameter')] = None,
                    min_salary: Annotated[int, Query(description='Optional status update parameter')] = None,
                    max_salary: Annotated[int, Query(description='Optional status update parameter')] = None):
    updated_ad = await update_ad_crud(db, ad_id, description, location, status, min_salary, max_salary)
    return updated_ad
