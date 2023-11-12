from typing import Annotated, List
from fastapi import FastAPI, Depends, Body
from sqlalchemy.orm import Session
from schemas.user import UserBase
from db.models import DbUsers
from db.database import get_db

app = FastAPI()


@app.get('/users/', response_model=List[UserBase])
def get_user(db: Annotated[Session, Depends(get_db)]):
    user = db.query(DbUsers).all()
    return user