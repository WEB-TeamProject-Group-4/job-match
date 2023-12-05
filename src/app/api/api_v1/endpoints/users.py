from typing import Annotated, List

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from app.schemas.user import UserDisplay, UserCreate
from app.db.database import get_db
from app.db.models import DbUsers
from app.core.auth import get_current_user
from app.crud.crud_user import create_user


router = APIRouter()


@router.post('/users', response_model=UserDisplay)
async def create_user_admin(schema: UserCreate, db: Annotated[Session, Depends(get_db)]):
    """
    POST /users

    Description:
    Creates a new user in the system. This endpoint is designed to allow the creation of different types of users,
    including admins, professionals, and companies, depending on the provided schema.

    Parameters:
    - **schema** (UserCreate): The schema containing the information for creating a new user.
    - **db** (Session): The database session dependency used for interacting with the database.

    Returns:
    200 OK: Returns a UserDisplay object with the created user's details.

    Raises:
    - HTTPException 400: If user's info has not been completed before reqeust.
    - HTTPException 401: If the user is not authenticated.
    - HTTPException 422: If there are validation errors in the provided schema.
    """

    return await create_user(db, schema)


@router.get('/users', response_model=List[UserDisplay])
def get_users(db: Annotated[Session, Depends(get_db)],
              current_user: Annotated[DbUsers, Depends(get_current_user)]):
    """
    GET /users

    Description:
    Retrieves a paginated list of verified users.
    This endpoint fetches users who are verified and presents them in a paginated format.

    Parameters:
    - **db** (Session): The database session dependency used for interacting with the database.
    - **current_user** (DbUsers): Information about the authenticated user, obtained from the authentication token.
    - **schema** (UserCreate): The schema containing the information for creating a new user.

    Returns:
    200 OK: Returns a list of UserDisplay objects for the specified page of verified users.

    Raises:
    - HTTPException 401: If the user is not authenticated.
    - HTTPException 404: If there are no available users.
    """

    users = db.query(DbUsers).filter(DbUsers.is_verified == 1).all()
    return users
