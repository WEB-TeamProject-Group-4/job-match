from typing import Annotated

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app.db.database import get_db
from app.db.models import DbUsers
from app.core.security import create_access_token
from app.core.hashing import Hash

router = APIRouter()


@router.post('/login', include_in_schema=False)
async def login(schema: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: Annotated[Session, Depends(get_db)]):
    """
    Endpoint: POST /login

    Description:
    Authenticates a user and provides an access token for subsequent authenticated requests.This endpoint is responsible
    for verifying user credentials and issuing a JWT (JSON Web Token) upon successful authentication.

    Parameters:
    - **schema** (OAuth2PasswordRequestForm): A form data object containing the username and password.
    - **db** (Session): The database session dependency used for interacting with the database.

    Responses:
    200 OK: Successful login. Returns an object containing the access_token, token_type, user_id, and username
    401 Unauthorized: Returned if the username is invalid or the password is incorrect.
    """
    user = db.query(DbUsers).filter(DbUsers.username == schema.username,
                                    DbUsers.is_deleted == False).first()
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
