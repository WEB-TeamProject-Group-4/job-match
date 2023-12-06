import secrets
import jwt

from typing import Optional
from datetime import timedelta, datetime, UTC

from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY: str = secrets.token_urlsafe(32)
EMAIL_KEY: str = secrets.token_urlsafe(32)


def create_access_token(data: dict, expires_delta: Optional[int] = None, security_key: Optional[str] = SECRET_KEY) -> str:
    """
    Function Name: create_access_token

    Description: Generates a JWT (JSON Web Token) for user authentication.
    This function creates an access token with an optional expiration time, encoding user-specific data and a secret key.

    Parameters:
    - **data** (dict): A dictionary containing data to be included in the token, typically user identification information.
    - **expires_delta** (Optional[int]): The number of minutes until the token expires. If not specified,
    a default expiration time is used.
    - **security_key** (Optional[str]): The secret key used for encoding the token. Defaults to SECRET_KEY if not specified.

    Returns: str: The encoded JWT token.
    """

    if expires_delta:
        expire = datetime.now(UTC) + timedelta(minutes=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, security_key, algorithm=settings.ALGORITHM)
    return encoded_jwt



all_labels = [
    "BUTTOCKS_EXPOSED",
    "FEMALE_BREAST_EXPOSED",
    "FEMALE_GENITALIA_EXPOSED",
    "MALE_BREAST_EXPOSED",
    "ANUS_EXPOSED",
    "FEET_EXPOSED",
    "ARMPITS_EXPOSED",
    "BELLY_EXPOSED",
    "MALE_GENITALIA_EXPOSED",
]
