from typing import Annotated

from fastapi import APIRouter, Request, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.hashing import very_token
from fastapi.templating import Jinja2Templates
from app.db.database import get_db


router = APIRouter()

templates = Jinja2Templates(directory='app/templates')


@router.get('/verification', response_class=HTMLResponse, include_in_schema=False)
async def email_verification(request: Request, token: str,
                             db: Annotated[Session, Depends(get_db)]):
    user = await very_token(token, db)
    if user:
        if not user.is_verified:
            user.is_verified = True
            db.commit()
            return templates.TemplateResponse('verification.html',
                                            {'request': request,'username': user.username})
        elif user.is_verified:
            return HTMLResponse(content="<html>User already verified</html>", status_code=200)

    raise HTTPException(
        status_code=401,
        detail='Invalid token',
        headers={'WWW-Authenticate': 'Bearer'}
    )
