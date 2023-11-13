from sqlalchemy.orm import Session
from app.db.models import DbUsers
from app.schemas.user import UserCreate
from fastapi import HTTPException
from app.core.security import Hash


def create_db_user(db: Session, request: UserCreate):
    new_user = DbUsers(
        username=request.username,
        password=Hash.bcrypt(request.password),
        type='user'
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
