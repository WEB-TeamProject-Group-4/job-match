from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app.schemas.user import UserDisplay, UserCreate
from typing import Annotated, List
from app.db.database import get_db
from app.crud.crud_user import create_db_user
from app.db.models import DbUsers
from app.core.security import get_current_user

router = APIRouter()


@router.post('/user', response_model=UserDisplay)
def create_user(request: UserCreate, db: Annotated[Session, Depends(get_db)]):
    return create_db_user(db, request)


@router.get('/user', response_model=List[UserDisplay])
def get_user(db: Annotated[Session, Depends(get_db)],
             current_user: Annotated[UserDisplay, Depends(get_current_user)]):
    user = db.query(DbUsers).all()
    return user
