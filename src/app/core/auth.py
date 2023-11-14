from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import DbUsers
from typing import Annotated
from app.core.security import oauth2_scheme, SECRET_KEY, ALGORITHM
import jwt


def get_user_by_username(db: Session, username: str):
    user = db.query(DbUsers).filter(DbUsers.username == username).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f'User with username {username} not found!'
        )
    return user


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                     db: Annotated[Session, Depends(get_db)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('username')
        if username is None:
            raise credentials_exception
    except jwt.DecodeError:
        raise credentials_exception
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user
