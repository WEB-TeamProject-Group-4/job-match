from typing import Type

import jwt
from passlib.context import CryptContext

from app.core.security import EMAIL_KEY
from app.db.models import DbUsers
from fastapi import HTTPException
from jwt import PyJWTError
from sqlalchemy.orm import Session

pwd_cxt = CryptContext(schemes=['bcrypt'], deprecated='auto')


class Hash:
    @staticmethod
    def bcrypt(password: str):
        return pwd_cxt.hash(password)

    @staticmethod
    def verify(hashed_password, plain_password):
        return pwd_cxt.verify(plain_password, hashed_password)


async def very_token(token: str,
                     db: Session) -> Type[DbUsers] | None:
    try:
        payload = jwt.decode(token, EMAIL_KEY, algorithms=['HS256'])
        user_id = payload.get('id')
        user = db.get(DbUsers, user_id)

    except PyJWTError:
        raise HTTPException(
            status_code=401,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    return user
