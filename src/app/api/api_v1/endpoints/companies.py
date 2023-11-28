from typing import Annotated, List

from fastapi import Depends, APIRouter, HTTPException, status, Query, Path, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.crud.crud_user import create_user
from app.crud.crud_company import CRUDCompany
from app.db.database import get_db
from app.db.models import DbUsers
from app.schemas import company

router = APIRouter(tags=['company'])


@router.post('/companies', response_model=company.CompanyCreateDisplay, status_code=status.HTTP_201_CREATED)
async def create_company(schema: company.CompanyCreate, db: Annotated[Session, Depends(get_db)]):
    """
    Create a new company.

    This endpoint allows the creation of a new company using the provided company creation schema.

    Parameters:
    - **schema** (CompanyCreate): The schema containing information for creating the company.
    - **db** (Session): The database session dependency.

    Returns:
    - Information about the created company.

    Raises:
    - HTTPException 400: If there are validation errors in the provided schema.
    """
    return await create_user(db, schema)


@router.get('/companies', response_model=List[company.CompanyDisplay])
async def get_companies(db: Annotated[Session, Depends(get_db)],
                        current_user: Annotated[DbUsers, Depends(get_current_user)],
                        name: Annotated[str, Query(description='Optional name search parameter')] = None,
                        page: Annotated[int, Query(description='Optional page number query parameter', ge=1)] = 1):
    """
    Retrieve a list of companies.

    This endpoint allows fetching a list of companies based on optional search parameters.

    Parameters:
    - **db**: The database session dependency.
    - **current_user**: Details about the current user obtained from the authentication token.
    - **name**: Optional parameter for filtering companies by name.
    - **page**: Optional parameter for specifying the page number (default is 1).

    Returns:
    - A list of company displays containing information about each company.

    Raises:
    - HTTPException 401: If the user is not authenticated.
    """
    companies = await CRUDCompany.get_multi(db, name, page)
    return companies


@router.get('/companies/{company_id}', response_model=company.CompanyDisplay)
async def get_company_by_id(db: Annotated[Session, Depends(get_db)],
                            company_id: Annotated[str, Path(description='Mandatory company id path parameter')]):
    """
    Retrieve company details by its unique identifier.

    This endpoint allows fetching details of a specific company based on its unique identifier.

    Parameters:
    - **db**: The database session dependency.
    - **company_id**: The unique identifier of the company.

    Returns:
    - Information about the specified company.

    Raises:
    - HTTPException 404: If no company is found with the provided company_id.
    """
    return await CRUDCompany.get_by_id(db, company_id)


@router.patch('/companies', response_model=company.UpdateCompanyDisplay)
async def update_company(db: Annotated[Session, Depends(get_db)],
                         current_user: Annotated[DbUsers, Depends(get_current_user)],
                         name: Annotated[str, Query(description='Optional name update parameter')] = None,
                         contact: Annotated[str, Query(description='Optional contact update parameter')] = None):
    """
    Update company information.

    This endpoint allows updating information for the authenticated user's company.

    Parameters:
    - **db**: The database session dependency.
    - **current_user**: Details about the current user obtained from the authentication token.
    - **name**: Optional parameter for updating the company name.
    - **contact**: Optional parameter for updating the company contact information.

    Returns:
    - Information about the updated company.

    Raises:
    - HTTPException 401: If the user is not authenticated.
    - HTTPException 403: If the user's account is not verified.
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Please verify your account.'
        )
    else:
        updated_company = await CRUDCompany.update(db, name, contact, current_user.id)
        return updated_company


@router.delete('/companies/{company_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(db: Annotated[Session, Depends(get_db)],
                         company_id: Annotated[str, Path(description='Mandatory company id path parameter')],
                         current_user: Annotated[DbUsers, Depends(get_current_user)]):
    """
    Delete a company by its unique identifier.

    This endpoint allows deleting a specific company based on its unique identifier.

    Parameters:
    - **db**: The database session dependency.
    - **company_id**: The unique identifier of the company to be deleted.
    - **current_user**: Details about the current user obtained from the authentication token.

    Returns:
    - None

    Raises:
    - HTTPException 401: If the user is not authenticated.
    """
    return await CRUDCompany.delete_by_id(db, company_id, current_user)


@router.post('/companies/info', response_model=company.CompanyInfoCreate,
             status_code=status.HTTP_201_CREATED)
async def create_company_info(db: Annotated[Session, Depends(get_db)],
                              current_user: Annotated[DbUsers, Depends(get_current_user)],
                              schema: company.CompanyInfoCreate):
    """
     Create additional information for a company.

    This endpoint allows creating additional information for the authenticated user's company.

    Parameters:
    - **db**: The database session dependency.
    - **current_user**: Details about the current user obtained from the authentication token.
    - **schema**: The schema containing information for creating company information.

    Returns:
    - Information about the created company info.

    Raises
    - HTTPException 401: If the user is not authenticated.
    - HTTPException 403: If the user's account is not verified.
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Please verify your account.'
        )
    else:
        info = await CRUDCompany.create_info(db, current_user.company[0].id, schema)
        return info


@router.post('/companies/info/upload')
async def upload(db: Annotated[Session, Depends(get_db)],
                 current_user: Annotated[DbUsers, Depends(get_current_user)],
                 image: Annotated[UploadFile, File()]) -> StreamingResponse:
    """
    Upload an image for company information.

    This endpoint allows uploading an image for the company info associated with the authenticated user's company.

    Parameters:
    - **db**: The database session dependency.
    - **current_user**: Details about the current user obtained from the authentication token.
    - **image**: The uploaded image file.

    Returns:
    - A streaming response for the uploaded image.

    Raises:
    - HTTPException 401: If the user is not authenticated.
    """
    f = await image.read()
    b = bytearray(f)
    return await CRUDCompany.upload(db, current_user.company[0].info_id, b)


@router.get('/companies/info/image')
async def get_image(db: Annotated[Session, Depends(get_db)],
                    current_user: Annotated[DbUsers, Depends(get_current_user)]) -> StreamingResponse:
    """
    Retrieve the image associated with company information.

    This endpoint allows fetching the image associated with the company information of the authenticated user's company.

    Parameters:
    - **db**: The database session dependency.
    - **current_user**: Details about the current user obtained from the authentication token.

    Returns:
    - A streaming response for the company information image.

    Raises:
    - HTTPException 401: If the user is not authenticated.
    """
    return await CRUDCompany.get_image(db, current_user.company[0].info_id)


@router.get('/companies/info/', response_model=company.CompanyInfoDisplay)
async def get_company_info(db: Annotated[Session, Depends(get_db)],
                           current_user: Annotated[DbUsers, Depends(get_current_user)]):
    """
    Retrieve additional information about a company.

    This endpoint allows fetching additional information about the authenticated user's company.


    Parameters:
    - **db**: The database session dependency.
    - **current_user**: Details about the current user obtained from the authentication token.

    Returns:
    - Information about the company.

    Raises:
    - HTTPException 403: If the user's account is not verified.
    - HTTPException 401: If the user is not authenticated.
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Please verify your account.'
        )
    else:
        info = await CRUDCompany.get_info_by_id(db, current_user.company[0].info_id,
                                                current_user.company[0].id)
        return info


@router.patch('/companies/info', response_model=company.CompanyInfoCreate)
async def update_info(db: Annotated[Session, Depends(get_db)],
                      current_user: Annotated[DbUsers, Depends(get_current_user)],
                      description: Annotated[str, Query(description='Optional description update parameter')] = None,
                      location: Annotated[str, Query(description='Optional location update parameter')] = None):
    """
    Update additional information for a company.

    This endpoint allows updating the additional information for the authenticated user's company.

    Parameters:
    - **db**: The database session dependency.
    - **current_user**: Details about the current user obtained from the authentication token.
    - **description**: Optional parameter for updating the company information description.
    - **location**: Optional parameter for updating the company information location.

    Returns:
    - Information about the updated company info.

    Raises:
    - HTTPException 401: If the user is not authenticated.
    - HTTPException 403: If the user's account is not verified.
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Please verify your account.'
        )
    else:
        new_info = await CRUDCompany.update_info(db, current_user.company[0].info_id, description, location)
        return new_info


@router.delete('/companies/info/{info_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_info(db: Annotated[Session, Depends(get_db)],
                      current_user: Annotated[DbUsers, Depends(get_current_user)],
                      info_id: Annotated[str, Path(description='Mandatory info id path parameter')]):
    """
    Delete additional information for a company by its unique identifier.

    This endpoint allows deleting the info for the authenticated user's company based on its unique identifier.

    Parameters:
    - **db**: The database session dependency.
    - **current_user**: Details about the current user obtained from the authentication token.
    - **info_id**: The unique identifier of the company information to be deleted.

    Returns:
    - None

    Raises:
    - HTTPException 401: If the user is not authenticated.
    """
    return await CRUDCompany.delete_info_by_id(db, info_id, current_user)


@router.post('/companies/match')
async def search_for_matches(db: Annotated[Session, Depends(get_db)],
                             current_user: Annotated[DbUsers, Depends(get_current_user)],
                             ad_id: Annotated[str, Query(description='Mandatory company ad id parameter.')],
                             threshold: Annotated[float, Query(description="Percentage for adjusting salary range",
                                                               ge=0, le=100)] = 0) -> JSONResponse:
    """
    Search for matches between a company's ad and professionals' resume.

    This endpoint allows a company to search for matches between their job advertisement and professionals' resume.
    The search is based on the provided ad_id and an optional threshold for adjusting the salary range.

    Parameters:
    - **db**: The database session dependency.
    - **current_user**: Details about the current user obtained from the authentication token.
    - **ad_id**: Mandatory parameter representing the unique identifier of the company's job advertisement.
    - **threshold**: Optional parameter representing the percentage for adjusting the salary range. Should be
                     between 0 and 100.

    Returns:
    - A JSON response containing information about search result.
    """
    threshold = round(threshold / 100, 2)
    return await CRUDCompany.find_matches(db, current_user.company[0], ad_id, threshold)


@router.get('/companies/match/')
async def get_matches(db: Annotated[Session, Depends(get_db)],
                      current_user: Annotated[DbUsers, Depends(get_current_user)]) -> list[company.CompanyMatchDisplay]:
    """
    Retrieve matches for a company's job advertisements.

    This endpoint allows a company to retrieve matches for their job advertisements.
    The matches are based on the current user's company and its associated job advertisements.

    Parameters:
    - **db**: The database session dependency.
    - **current_user**: Details about the current user obtained from the authentication token.

    Returns:
    - **list[CompanyMatchDisplay]**: A list of company match displays containing information about the matches.
    """
    return await CRUDCompany.get_matches_multi(db, current_user.company[0])


@router.patch('/companies/match')
async def approve_match(db: Annotated[Session, Depends(get_db)],
                        current_user: Annotated[DbUsers, Depends(get_current_user)],
                        resume_id: Annotated[str, Query(description='Mandatory professional ad id')]) -> JSONResponse:
    """
    Approve a match between a company and a professional.

    This endpoint allows a company to approve a match between their job advertisement and a professionals' resume.
    The approval is based on the provided resume_id.

    Parameters:
    - **db**: The database session dependency.
    - **current_user**: Details about the current user obtained from the authentication token.
    - **resume_id**: Mandatory parameter representing the unique identifier of the professional resume.

    Returns:
    - A JSON response containing information about the approval.
    """
    return await CRUDCompany.approve_match(db, resume_id, current_user.company[0].id)
