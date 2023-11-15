import secrets
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from datetime import timedelta, datetime, UTC
import jwt
from app.core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY: str = secrets.token_urlsafe(32)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


