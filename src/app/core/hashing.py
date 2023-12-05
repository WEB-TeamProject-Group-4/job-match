import jwt
from typing import Type

from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.core.security import EMAIL_KEY
from app.db.models import DbUsers


pwd_cxt = CryptContext(schemes=['bcrypt'], deprecated='auto')


class Hash:
    @staticmethod
    def bcrypt(password: str):
        return pwd_cxt.hash(password)

    @staticmethod
    def verify(hashed_password, plain_password):
        return pwd_cxt.verify(plain_password, hashed_password)


async def very_token(token: str, db: Session) -> Type[DbUsers] | None:
    """
    Function Name: very_token

    Description: Verifies the authenticity of a JWT (JSON Web Token) used typically for email verification processes.
    This function decodes the token to extract the user's ID and retrieves the corresponding user from the database.

    Parameters:
    - **token** (str): The JWT token to be verified.
    - **db** (Session): The active database session for querying the database.

    Returns: Type[DbUsers] | None: The user object if the token is valid and the user is found, otherwise None.

    Errors:
    - Raises HTTPException with status 401 if the token is invalid or if any issue arises during its decoding.
    """

    try:
        payload = jwt.decode(token, EMAIL_KEY, algorithms=['HS256'])
        user_id = payload.get('id')
        user = db.get(DbUsers, user_id)

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    return user
