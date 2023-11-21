from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.crud_ad import create_new_ad, create_new_skill
from app.db.database import get_db
from app.schemas.ad import AdCreate, AdCreateDisplay, SkillCreateDisplay, SkillCreate

router = APIRouter()


@router.post('/ads', response_model=AdCreateDisplay)
async def create_add(schema: AdCreate, db: Annotated[Session, Depends(get_db)]):
    return create_new_ad(db, schema)


@router.post('/skills', response_model=SkillCreateDisplay)
async def create_skill(schema: SkillCreate, db: Annotated[Session, Depends(get_db)]):
    return create_new_skill(db, schema)