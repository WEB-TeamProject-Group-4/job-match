from typing import Type, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import DbAds, DbSkills, adds_skills
from app.schemas.ad import AdCreate, AdSkills, IncludeSkillToAdd, IncludeSkillToAddDisplay, AdDisplay


async def create_new_ad(db: Session, schema: AdCreate) -> DbAds:
    new_ad = DbAds(
        description=schema.description,
        location=schema.location,
        status=schema.status,
        min_salary=schema.min_salary,
        max_salary=schema.max_salary,
        info_id=schema.info_id
    )
    try:
        db.add(new_ad)
        db.commit()
    except IntegrityError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err.args)
    else:
        db.refresh(new_ad)
        return new_ad


async def create_new_skill(db: Session, schema: AdSkills) -> DbSkills:
    new_skill = DbSkills(
        name=schema.name
    )
    try:
        db.add(new_skill)
        db.commit()
    except IntegrityError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err.args)
    else:
        db.refresh(new_skill)
        return new_skill


async def add_skill_to_ad(db: Session, schema: IncludeSkillToAdd) -> IncludeSkillToAddDisplay:
    ad = db.query(DbAds).filter(DbAds.id == schema.ad_id).first()
    skill = db.query(DbSkills).filter(DbSkills.id == schema.skill_id).first()

    if not ad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ad not found')
    elif not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Skill not found')

    skill_added = db.query(adds_skills).filter(
        adds_skills.c.ad_id == schema.ad_id,
        adds_skills.c.skill_id == schema.skill_id).first()

    if skill_added:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Skill already added')

    ad_skill = adds_skills.insert().values(ad_id=ad.id, skill_id=skill.id, level=schema.level)
    db.execute(ad_skill)

    try:
        db.commit()
        return IncludeSkillToAddDisplay(
            skill_name=skill.name,
            level=schema.level
        )
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err.args))


async def get_all_ads_crud(db: Session) -> List[Type[AdDisplay]]:
    ads = db.query(DbAds).all()
    return ads


async def get_ad_by_id_crud(db: Session, ad_id: str) -> Type[AdDisplay]:
    ad = db.query(DbAds).filter(DbAds.id == ad_id).first()
    return ad


async def get_all_skills_crud(db: Session) -> List[Type[AdSkills]]:
    skills = db.query(DbSkills).all()
    return skills


async def update_ad_crud(db: Session, ad_id=str, description: Optional[str] = None, location: Optional[str] = None,
                         status: Optional[str] = None, min_salary: Optional[int] = None,
                         max_salary: Optional[int] = None):
    ad = db.query(DbAds).filter(DbAds.id == ad_id).first()
    if description:
        ad.description = description
    if location:
        ad.location = location
    if status:
        ad.status = status
    if min_salary:
        ad.min_salary = min_salary
    if max_salary:
        ad.max_salary = max_salary
    db.commit()

    return ad
