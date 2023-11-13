from typing import Annotated, List
from fastapi import FastAPI, Depends, Body, APIRouter
from sqlalchemy.orm import Session
# from app.schemas.user import UserBase, JobsMatchesBase
# from app.schemas.company import CompanyBase
from app.db.models import DbUsers, DbJobsMatches
from app.db.database import get_db

router = APIRouter()

# @router.get('/users/', response_model=List[JobsMatchesBase])
# def get_user(db: Annotated[Session, Depends(get_db)]):
#     user = db.query(DbJobsMatches).all()
#     return user