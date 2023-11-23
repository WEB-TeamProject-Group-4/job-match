from typing import Type, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import DbAds, DbSkills, adds_skills
from app.schemas.ad import AdCreate, AdSkills, IncludeSkillToAddDisplay, AdDisplay


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


async def update_skill_crud(db: Session, skill_name: str, new_name: str) -> Type[DbSkills]:
    skill = db.query(DbSkills).filter(DbSkills.name == skill_name).first()

    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Skill not found')

    existing_skill = db.query(DbSkills).filter(DbSkills.name == new_name).first()
    if existing_skill:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Skill already exists')

    skill.name = new_name

    try:
        db.commit()
        db.refresh(skill)
        return skill
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err.args))


async def delete_skill_crud(db: Session, skill_name: str) -> None:
    skill = db.query(DbSkills).filter(DbSkills.name == skill_name).first()

    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Skill not found')

    db.delete(skill)
    try:
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err.args))


async def add_skill_to_ad_crud(db: Session, ad_id: str, skill_name: str, level: str) -> IncludeSkillToAddDisplay:
    ad = db.query(DbAds).filter(DbAds.id == ad_id).first()
    skill = db.query(DbSkills).filter(DbSkills.name == skill_name).first()

    if not ad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ad not found')
    elif not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Skill not found')

    skill_added = db.query(adds_skills) \
        .join(DbSkills, adds_skills.c.skill_id == DbSkills.id) \
        .join(DbAds, adds_skills.c.ad_id == DbAds.id) \
        .filter(DbAds.id == ad_id, DbSkills.name == skill_name) \
        .first()

    if skill_added:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Skill already added')

    ad_skill = adds_skills.insert().values(ad_id=ad.id, skill_id=skill.id, level=level)
    db.execute(ad_skill)

    try:
        db.commit()
        return IncludeSkillToAddDisplay(
            skill_name=skill.name,
            level=level
        )
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err.args))


async def remove_skill_from_ad_crud(db: Session, ad_id: str, skill_name: str) -> None:
    ad = db.query(DbAds).filter(DbAds.id == ad_id).first()
    skill = db.query(DbSkills).filter(DbSkills.name == skill_name).first()

    if not ad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ad not found')
    elif not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Skill not found')

    skill_to_remove = db.query(adds_skills) \
        .join(DbSkills, adds_skills.c.skill_id == DbSkills.id) \
        .join(DbAds, adds_skills.c.ad_id == DbAds.id) \
        .filter(DbAds.id == ad_id, DbSkills.name == skill_name) \
        .first()

    if not skill_to_remove:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Skill not associated with this ad')

    db.execute(
        adds_skills.delete().where(
            adds_skills.c.ad_id == ad_id,
            adds_skills.c.skill_id == skill.id)
    )

    try:
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err.args))


async def get_ads_crud(db: Session, description: Optional[str] = None, location: Optional[str] = None,
                       ad_status: Optional[str] = None, min_salary: Optional[int] = None,
                       max_salary: Optional[int] = None, page: Optional[int] = 1) -> List[Type[AdDisplay]]:
    query = db.query(DbAds)

    if description:
        keywords = description.split()
        for keyword in keywords:
            query = query.filter(DbAds.description.ilike(f'%{keyword}%'))
    if location:
        query = query.filter(DbAds.location.ilike(f'%{location}%'))
    if ad_status:
        query = query.filter(DbAds.status == ad_status)
    if min_salary:
        query = query.filter(DbAds.min_salary >= min_salary)
    if max_salary:
        query = query.filter(DbAds.max_salary <= max_salary)

    ads = query.limit(2).offset((page - 1) * 2).all()

    return ads


async def get_ad_by_id_crud(db: Session, ad_id: str) -> Type[AdDisplay]:
    ad = db.query(DbAds).filter(DbAds.id == ad_id).first()
    return ad


async def delete_ad_crud(db: Session, ad_id: str) -> None:
    ad = db.query(DbAds).filter(DbAds.id == ad_id).first()

    if not ad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ad not found')

    db.delete(ad)
    try:
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err.args))


async def get_all_skills_crud(db: Session, page: Optional[int] = 1) -> List[Type[AdSkills]]:
    skills_query = db.query(DbSkills).limit(5).offset((page - 1) * 5)
    skills = skills_query.all()

    return skills


async def update_ad_crud(db: Session, ad_id=str, description: Optional[str] = None, location: Optional[str] = None,
                         ad_status: Optional[str] = None, min_salary: Optional[int] = None,
                         max_salary: Optional[int] = None):
    ad = db.query(DbAds).filter(DbAds.id == ad_id).first()
    if description:
        ad.description = description
    if location:
        ad.location = location
    if ad_status:
        ad.status = ad_status
    if min_salary:
        ad.min_salary = min_salary
    if max_salary:
        ad.max_salary = max_salary
    db.commit()

    return ad
