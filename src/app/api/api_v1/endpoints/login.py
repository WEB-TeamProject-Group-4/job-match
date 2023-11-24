from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.db.database import get_db
from app.db.models import DbUsers
from app.core.security import create_access_token
from app.core.hashing import Hash

router = APIRouter()


@router.post('/login', include_in_schema=False)
async def login(schema: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: Annotated[Session, Depends(get_db)]):
    user = db.query(DbUsers).filter(DbUsers.username == schema.username,
                                    DbUsers.is_deleted is False).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail='Invalid username'
        )
    if not Hash.verify(user.password, schema.password):
        raise HTTPException(
            status_code=401,
            detail='Incorrect password'
        )
    access_token = create_access_token(data={'username': user.username})
    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'user_id': user.id,
        'username': user.username
    }
