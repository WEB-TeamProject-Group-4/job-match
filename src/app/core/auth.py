import jwt
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import DbUsers
from app.core.security import oauth2_scheme, SECRET_KEY
from app.core.config import settings


def get_user_by_username(db: Session, username: str):
    """
    Function Name: get_user_by_username

    Description: Retrieves a user from the database based on their username.
    This function is designed to fetch a specific user, ensuring that the user has not been marked as deleted.

    Parameters:
    - **db** (Session): The active database session for querying the database.
    - **username** (str): The username of the user to be retrieved.

    Returns: The user object if found.

    Errors:
    - Raises HTTPException with status 404 if a user with the specified username is not found or is marked as deleted.
    """
    user = db.query(DbUsers).filter(DbUsers.username == username, DbUsers.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f'User with username {username} not found!'
        )
    return user


def get_current_user(db: Annotated[Session, Depends(get_db)],
                     token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Function Name: get_current_user

    Description: Authenticates and retrieves the current user based on the provided JWT (JSON Web Token).
    This function decodes the token, extracts the username, and fetches the corresponding user from the database.

    Parameters:
    - **db** (Session): The active database session for querying the database.
    - **token** (str): The verification token sent to the user's email.

    Returns: The authenticated user object.

    Errors:
    - Raises HTTPException with status 401 if the token is invalid, expired, or the user is not found.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get('username')
        if username is None:
            raise credentials_exception
    except jwt.DecodeError:
        raise credentials_exception
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user
