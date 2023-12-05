from typing import Annotated

from fastapi import APIRouter, Request, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.hashing import very_token
from app.db.database import get_db


router = APIRouter()

templates = Jinja2Templates(directory='app/templates')


@router.get('/verification', response_class=HTMLResponse, include_in_schema=False)
async def email_verification(schema: Request, token: str,
                             db: Annotated[Session, Depends(get_db)]):
    """
    Endpoint: GET /verification

    Description:
    Handles the email verification process for users. When a user clicks on the verification link sent to their email,
    this endpoint verifies the user's account using a provided token.

    Parameters:
    - **schema** (OAuth2PasswordRequestForm): A form data object containing the username and password.
    - **token** (str): The verification token sent to the user's email.
    - **db** (Session): The database session dependency used for interacting with the database.

    Responses:
    200 OK: Returns an HTML response indicating whether the user is successfully verified or already verified.
    401 Unauthorized: Returned if the username is invalid or the password is incorrect.
    """

    user = await very_token(token, db)
    if user:
        if not user.is_verified:
            user.is_verified = True
            db.commit()
            return templates.TemplateResponse('verification.html',
                                              {'request': schema, 'username': user.username})
        elif user.is_verified:
            return HTMLResponse(content="<html>User already verified</html>", status_code=200)

    raise HTTPException(
        status_code=401,
        detail='Invalid token',
        headers={'WWW-Authenticate': 'Bearer'}
    )
