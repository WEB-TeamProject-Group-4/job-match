from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import DbAds, DbSkills
from app.schemas.ad import AdCreate, SkillCreate


async def create_new_ad(db: Session, schema: AdCreate):
    new_ad = DbAds(
        description=schema.description,
        location=schema.location,
        status=schema.status,
        min_salary=schema.min_salary,
        max_salary=schema.max_salary
    )
    try:
        db.add(new_ad)
        db.commit()
    except IntegrityError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err.args)
    else:
        db.refresh(new_ad)
        return new_ad


async def create_new_skill(db: Session, schema: SkillCreate):
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
