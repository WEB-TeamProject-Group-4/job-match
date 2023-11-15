from typing import Annotated

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.hashing import very_token
from fastapi.templating import Jinja2Templates
from app.db.database import get_db


router = APIRouter()

templates = Jinja2Templates(directory='app/templates')


@router.get('/verification', response_class=HTMLResponse)
async def email_verification(request: Request, token: str,
                             db: Annotated[Session, Depends(get_db)]):
    user = await very_token(token, db)

    if user and not user.is_verified:
        user.is_verified = True
        db.commit()
        return templates.TemplateResponse('verification.html',
                                          {'request': request,
                                           'username': user.username})
    raise HTTPException(
        status_code=401,
        detail='Invalid token',
        headers={'WWW-Authenticate': 'Bearer'}
    )
