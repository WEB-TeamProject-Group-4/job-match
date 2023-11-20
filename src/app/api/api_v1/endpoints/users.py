from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app.schemas.user import UserDisplay, UserCreate
from typing import Annotated, List
from app.db.database import get_db
from app.db.models import DbUsers 
from app.core.auth import get_current_user
from app.crud.crud_user import create_user


router = APIRouter()


@router.post('/users', response_model=UserDisplay)
async def create_user_admin(schema: UserCreate, db: Annotated[Session, Depends(get_db)]):
    return await create_user(db, schema)


@router.get('/users', response_model=List[UserDisplay])
def get_users(db: Annotated[Session, Depends(get_db)],
              current_user: Annotated[UserDisplay, Depends(get_current_user)]):
    users = db.query(DbUsers).filter(DbUsers.is_verified == 1).all()
    return users



