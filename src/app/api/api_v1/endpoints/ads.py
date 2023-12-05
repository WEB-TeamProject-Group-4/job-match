from typing import Annotated, List

from fastapi import APIRouter, Depends, status, Query, HTTPException, Path
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import DbUsers
from app.core.auth import get_current_user
from app.schemas.ad import (AdCreate, AdSkills, AddSkillToAdDisplay, AdDisplay, JobAdStatus, SkillLevel, ResumeStatus)
from app.crud.crud_ad import (create_ad_crud, get_resumes_crud, get_job_ads_crud, update_resumes_crud,
                              update_job_ads_crud, delete_ad_crud, get_ad_by_id_crud, create_new_skill, get_skills_crud,
                              delete_skill_crud, update_skill_crud, add_skill_to_ad_crud, remove_skill_from_ad_crud)

router = APIRouter(tags=['ad'])


@router.post('/ads', response_model=AdCreate)
async def create_ad(db: Annotated[Session, Depends(get_db)],
                    current_user: Annotated[DbUsers, Depends(get_current_user)], schema: AdCreate):
    """
    POST /ads

    Creates a new advertisement based on the user's input.
    This endpoint is tailored for both professional and company users to post ads.

    Parameters:
    - **db** (Session): The database session dependency used for interacting with the database.
    - **current_user** (DbUsers): Information about the authenticated user, obtained from the authentication token.
    - **schema** (AdCreate): The schema contains the information for creating an ad.

    Returns:
    200 OK: Information about the created ad.

    Raises:
    - HTTPException 400: If user's info has not been completed before reqeust.
    - HTTPException 401: If the user is not authenticated.
    - HTTPException 422: If there are validation errors in the provided schema.
    """
    return await create_ad_crud(db, current_user, schema)


@router.get('/ads/companies', response_model=List[AdDisplay])
async def get_resumes(db: Annotated[Session, Depends(get_db)],
                      current_user: Annotated[DbUsers, Depends(get_current_user)],
                      description: Annotated[str, Query(description='Optional key-word search parameter')] = None,
                      location: Annotated[str, Query(description='Optional location search parameter')] = None,
                      ad_status: Annotated[ResumeStatus, Query(description='Optional status search parameter')] = None,
                      min_salary: Annotated[int, Query(description='Optional minimal salary search parameter')] = None,
                      max_salary: Annotated[int, Query(description='Optional maximal salary search parameter')] = None,
                      page: Annotated[int, Query(description='Optional query parameter. Results = 2', ge=1)] = 1):
    """
    GET /ads/companies

    Retrieves a list of advertisements that match specified search criteria.
    This endpoint is designed for company users to search for relevant ads / resumes.

    Parameters:
    - **db** (Session): The database session dependency.
    - **current_user** (DbUsers): Information about the authenticated user, obtained from the authentication token.
    - **description** (str, optional): A keyword search parameter to filter ads by keywords in their description.
    - **location** (str, optional): A location search parameter to filter ads by their geographical location.
    - **ad_status** (ResumeStatus, optional): A status search parameter to filter ads by their current status.
    - **min_salary** (int, optional): A minimal salary search parameter to filter ads by their salary range.
    - **max_salary** (int, optional): A maximal salary search parameter to filter ads by their salary range.
    - **page** (int, optional, default=1): Pagination parameter to specify the page number of results.
    Each page contains 2 results.

    Responses:
    200 OK: Returns a list of AdDisplay objects matching the search criteria.

    Exceptions:
    - HTTPException 401: If the user is not authenticated.
    - HTTPException 403: Raised if a user with a 'professional' type attempts to access the endpoint.
    - HTTPException 404: Raised if there are no ads that match the search criteria.
    """

    if current_user.type == 'professional':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Section restricted for professionals')

    ads = await get_resumes_crud(db, description, location, ad_status, min_salary, max_salary, page)

    return ads


@router.get('/ads/professionals', response_model=List[AdDisplay])
async def get_job_ads(db: Annotated[Session, Depends(get_db)],
                      current_user: Annotated[DbUsers, Depends(get_current_user)],
                      description: Annotated[str, Query(description='Optional key-word search parameter')] = None,
                      location: Annotated[str, Query(description='Optional location search parameter')] = None,
                      ad_status: Annotated[JobAdStatus, Query(description='Optional status search parameter')] = None,
                      min_salary: Annotated[int, Query(description='Optional minimal salary search parameter')] = None,
                      max_salary: Annotated[int, Query(description='Optional maximal salary search parameter')] = None,
                      page: Annotated[int, Query(description='Optional query parameter. Results = 2', ge=1)] = 1):
    """
    GET /ads/professionals

    Retrieves a list of advertisements that match specified search criteria.
    This endpoint is designed for professional users to search for relevant job ads.

    Parameters:
    - **db** (Session): The database session dependency.
    - **current_user** (DbUsers): Information about the authenticated user, obtained from the authentication token.
    - **description** (str, optional): A keyword search parameter to filter ads by keywords in their description.
    - **location** (str, optional): A location search parameter to filter ads by their geographical location.
    - **ad_status** (JobAdStatus, optional): A status search parameter to filter ads by their current status.
    - **min_salary** (int, optional): A minimal salary search parameter to filter ads by their salary range.
    - **max_salary** (int, optional): A maximal salary search parameter to filter ads by their salary range.
    - **page** (int, optional, default=1): Pagination parameter to specify the page number of results.
    Each page contains 2 results.

    Responses:
    200 OK: Returns a list of AdDisplay objects matching the search criteria.

    Exceptions:
    - HTTPException 401: If the user is not authenticated.
    - HTTPException 403: Raised if a user with a 'professional' type attempts to access the endpoint.
    - HTTPException 404: Raised if there are no ads that match the search criteria.
    """

    if current_user.type == 'company':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Section not available for company users')

    ads = await get_job_ads_crud(db, description, location, ad_status, min_salary, max_salary, page)

    return ads


@router.put('/ads/professionals/{ad_id}', response_model=AdDisplay)
async def update_resumes(db: Annotated[Session, Depends(get_db)],
                         current_user: Annotated[DbUsers, Depends(get_current_user)],
                         ad_id: Annotated[str, Path(description='Mandatory ad id path parameter')],
                         description: Annotated[str, Query(description='Optional update parameter')] = None,
                         location: Annotated[str, Query(description='Optional update parameter')] = None,
                         ad_status: Annotated[ResumeStatus, Query(description='Optional update parameter')] = None,
                         min_salary: Annotated[int, Query(description='Optional update parameter')] = None,
                         max_salary: Annotated[int, Query(description='Optional update parameter')] = None):
    """
    PUT /ads/professionals/{ad_id}

    Updates an existing professional ad with new information.
    This endpoint is specifically for professional users to update their resume ads.

    Parameters:
    - **db** (Session): The database session dependency for interacting with the database.
    - **current_user** (DbUsers): Information about the authenticated user, obtained from the authentication token.
    - **ad_id** (str, path parameter): The unique identifier of the ad to be updated. This is a mandatory parameter.
    - **description** (str, query parameter, optional): New description for the ad.
    - **location** (str, query parameter, optional): New location for the ad.
    - **ad_status** (ResumeStatus, query parameter, optional): New status for the ad.
    - **min_salary** (int, query parameter, optional): New minimum salary for the ad.
    - **max_salary** (int, query parameter, optional): New maximum salary for the ad.

    Restrictions:
    Accessible only by professional users. Company users will receive a 403 Forbidden error.

    Responses:
    200 OK: Returns the updated AdDisplay object.

    Exceptions:
    - HTTPException 400: Raised if the specified ad is not a resume ad.
    - HTTPException 401: If the user is not authenticated.
    - HTTPException 403: Raised if a company user attempts to access the endpoint, or when the user is not the author.
    - HTTPException 404: Raised if no ad is found with the given ad_id.
    """

    if current_user.type == 'company':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Restricted section')

    resume = await update_resumes_crud(db, current_user, ad_id, description, location, ad_status, min_salary,
                                       max_salary)

    return resume


@router.put('/ads/companies/{ad_id}', response_model=AdDisplay)
async def update_job_ads(db: Annotated[Session, Depends(get_db)],
                         current_user: Annotated[DbUsers, Depends(get_current_user)],
                         ad_id: Annotated[str, Path(description='Mandatory ad id path parameter')],
                         description: Annotated[str, Query(description='Optional update parameter')] = None,
                         location: Annotated[str, Query(description='Optional update parameter')] = None,
                         ad_status: Annotated[JobAdStatus, Query(description='Optional update parameter')] = None,
                         min_salary: Annotated[int, Query(description='Optional update parameter')] = None,
                         max_salary: Annotated[int, Query(description='Optional update parameter')] = None):
    """
    PUT /ads/companies/{ad_id}

    Updates an existing company ad with new information.
    This endpoint is specifically for company users to update their job ads.

    Parameters:
    - **db** (Session): The database session dependency for interacting with the database.
    - **current_user** (DbUsers): Information about the authenticated user, obtained from the authentication token.
    - **ad_id** (str, path parameter): The unique identifier of the ad to be updated. This is a mandatory parameter.
    - **description** (str, query parameter, optional): New description for the ad.
    - **location** (str, query parameter, optional): New location for the ad.
    - **ad_status** (JobAdStatus, query parameter, optional): New status for the ad.
    - **min_salary** (int, query parameter, optional): New minimum salary for the ad.
    - **max_salary** (int, query parameter, optional): New maximum salary for the ad.

    Restrictions:
    Accessible only by company users. Professional users will receive a 403 Forbidden error.

    Responses:
    200 OK: Returns the updated AdDisplay object.

    Exceptions:
    - HTTPException 400: Raised if the specified ad is not a resume ad.
    - HTTPException 401: If the user is not authenticated.
    - HTTPException 403: Raised if a professional user attempts to access the endpoint, or when company not the author.
    - HTTPException 404: Raised if no ad is found with the given ad_id.
    """

    if current_user.type == 'professional':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Restricted section')

    updated_ad = await update_job_ads_crud(db, current_user, ad_id, description, location, ad_status,
                                           min_salary, max_salary)

    return updated_ad


@router.get('/ads/{ad_id}', response_model=AdDisplay)
async def get_ad_by_id(db: Annotated[Session, Depends(get_db)],
                       current_user: Annotated[DbUsers, Depends(get_current_user)],
                       ad_id: Annotated[str, Path(description='Mandatory ad id path parameter')]):
    """
    GET /ads/{ad_id}

    Retrieves the details of a specific advertisement using its unique identifier.
    This endpoint is intended for users to view detailed information about an ad.

    Parameters:
    - **db** (Session): The database session dependency for interacting with the database.
    - **current_user** (DbUsers): Information about the authenticated user, obtained from the authentication token.
    - **ad_id** (str, path parameter): The unique identifier of the ad. This is a mandatory parameter.

    Responses:
    200 OK: Returns the AdDisplay object containing detailed information about the requested advertisement.

    Exceptions:
    - HTTPException 401: If the user is not authenticated.
    - HTTPException 404: Raised if no advertisement is found with the given ad_id.
    """

    ad = await get_ad_by_id_crud(db, ad_id)

    return ad


@router.delete('/ads/{ad_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_ad(db: Annotated[Session, Depends(get_db)],
                    current_user: Annotated[DbUsers, Depends(get_current_user)],
                    ad_id: Annotated[str, Path(description='Mandatory ad id path parameter')]):
    """
    DELETE /ads/{ad_id}

    Deletes a specific advertisement identified by its unique identifier.
    This endpoint is intended for users to remove their own ads or for admin users to manage ads on the platform.

    Parameters:
    - **db** (Session): The database session dependency for interacting with the database.
    - **current_user** (DbUsers): Information about the authenticated user, obtained from the authentication token.
    - **ad_id** (str, path parameter): The unique identifier of the ad to be deleted. This is a mandatory parameter.

    Restrictions:
    Users can only delete their own ads unless they are admin users.
    Additional checks are performed for professional users to manage their main resumes.

    Responses:
    - 204 No Content: Successfully deleted the advertisement. No content is returned.

    Exceptions:
    - HTTPException 401: If the user is not authenticated.
    - HTTPException 403: Raised if the user attempting to delete the ad is neither its author nor an admin.
    - HTTPException 404: Raised if no advertisement is found with the given ad_id.
    """
    return await delete_ad_crud(db, ad_id, current_user)


@router.post('/skills', response_model=AdSkills)
async def create_skill(db: Annotated[Session, Depends(get_db)],
                       current_user: Annotated[DbUsers, Depends(get_current_user)], schema: AdSkills):

    """
    POST /skills

    Creates a new skill entry in the database.
    This endpoint allows users to add unique skills to the system, which can be later associated with ads and resumes.

    Parameters:
    - **db** (Session): The database session dependency used for interacting with the database.
    - **current_user** (DbUsers): Information about the authenticated user, obtained from the authentication token.
    - **schema** (AdSkills): The schema for creating a new skill. It contains the name of the skill to be added.

    Returns:
    200 OK: Returns the AdSkills object of the successfully created skill.

    Raises:
    - HTTPException 401: If the user is not authenticated.
    - HTTPException 409: Raised if the skill with the provided name already exists.
    """

    return await create_new_skill(db, schema)


@router.get('/skills', response_model=List[AdSkills])
async def get_skills(db: Annotated[Session, Depends(get_db)],
                     current_user: Annotated[DbUsers, Depends(get_current_user)],
                     page: Annotated[int, Query(description='Optional page number query parameter', ge=1)] = 1):
    """
    GET /skills

    Retrieves a list of available skills.
    This endpoint is designed for users to view a paginated list of skills currently in the system.

    Parameters:
    - **db** (Session): The database session dependency used for interacting with the database.
    - **current_user** (DbUsers): Information about the authenticated user, obtained from the authentication token.
    - **page** (int, optional, default=1): The page number for pagination. Each page displays 5 skills.
    This is an optional parameter, and it defaults to 1.

    Returns:
    200 OK: Returns a list of AdSkills objects, each representing a skill.

    Raises:
    - HTTPException 401: If the user is not authenticated.
    - HTTPException 404: Raised if there are no skills available in the system.
    """

    skills = await get_skills_crud(db, page)

    return skills


@router.patch('/skills', response_model=AdSkills)
async def update_skill(db: Annotated[Session, Depends(get_db)],
                       current_user: Annotated[DbUsers, Depends(get_current_user)],
                       skill_name: Annotated[str, Query(..., description='Current skill name')],
                       new_name: Annotated[str, Query(..., description='New skill name')]):

    """
    PATCH /skills

    Updates the name of an existing skill in the database.
    This endpoint allows users to modify the name of a skill, if the new name does not already exist in the system.

    Parameters:
    - **db** (Session): The database session dependency used for interacting with the database.
    - **current_user** (DbUsers): Information about the authenticated user, obtained from the authentication token.
    - **skill_name** (str, query parameter): The current name of the skill that needs to be updated.
    - **new_name** (str, query parameter): The new name for the skill.

    Request:
    The request should include the current name of the skill and the new name that it should be updated to.
    Both skill_name and new_name are mandatory query parameters.

    Returns:
    200 OK: Returns the updated AdSkills object with the new skill name.

    Raises:
    - HTTPException 401: If the user is not authenticated.
    - HTTPException 404: Raised if no skill is found with the provided current name.
    - HTTPException 409: Raised if a skill with the new name already exists in the system.
    """

    skill = await update_skill_crud(db, skill_name, new_name)

    return skill


@router.delete('/skills', status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(db: Annotated[Session, Depends(get_db)],
                       current_user: Annotated[DbUsers, Depends(get_current_user)],
                       skill_name: Annotated[str, Query(..., description='Skill name')]):

    """
    DELETE /skills

    Deletes a specific skill from the database.
    This endpoint allows users to mark a skill as deleted, effectively removing it from active use.

    Parameters:
    - **db** (Session): The database session dependency used for interacting with the database.
    - **current_user** (DbUsers): Information about the authenticated user, obtained from the authentication token.
    - **skill_name** (str, query parameter): The current name of the skill that needs to be deleted.

    Request:
    The request should include the name of the skill to be deleted. skill_name is a mandatory query parameter.

    Returns:
    204 No Content: Indicates successful deletion of the skill. No content is returned in the response.

    Raises:
    - HTTPException 401: If the user is not authenticated.
    - HTTPException 404: Raised if no skill is found with the provided current name.
    """

    return await delete_skill_crud(db, skill_name)


@router.post('/ads/{ad_id}/skills', response_model=AddSkillToAdDisplay)
async def add_skill_to_ad(db: Annotated[Session, Depends(get_db)],
                          current_user: Annotated[DbUsers, Depends(get_current_user)],
                          ad_id: Annotated[str, Path(description='Mandatory ad id path parameter')],
                          skill_name: Annotated[str, Query(description='Include skill')],
                          level: Annotated[SkillLevel, Query(description='Select skill level')] = SkillLevel.BEGINNER):

    """
    POST /ads/{ad_id}/skills

    Associates a specific skill with an advertisement.
    This endpoint allows users to add a skill to an advertisement, along with the skill level.

    Parameters:
    - **db** (Session): The database session dependency used for interacting with the database.
    - **current_user** (DbUsers): Information about the authenticated user, obtained from the authentication token.
    - **ad_id** (str, path parameter): The unique identifier of the ad to which the skill will be added. This is a
    mandatory parameter.
    - **skill_name** (str, query parameter): The name of the skill to be added to the ad.
    - **level** (SkillLevel, query parameter, default=BEGINNER): The level of proficiency in the skill, with BEGINNER as
    the default value.

    Request:
    The request should include the ad_id, skill_name, and optionally the level of the skill.

    Returns:
    200 OK: Returns an AddSkillToAdDisplay object containing the added skill's name and level.

    Raises:
    - HTTPException 400: Raised if the skill is already added to the ad.
    - HTTPException 401: If the user is not authenticated.
    - HTTPException 404: Raised if no skill is found with the provided current name.
    """

    return await add_skill_to_ad_crud(db, ad_id, skill_name, level)


@router.delete('/ads/{ad_id}/skills', status_code=status.HTTP_204_NO_CONTENT)
async def remove_skill_from_ad(db: Annotated[Session, Depends(get_db)],
                               current_user: Annotated[DbUsers, Depends(get_current_user)],
                               ad_id: Annotated[str, Path(description='Mandatory ad id path parameter')],
                               skill_name: Annotated[str, Query(description='Remove skill')]):

    """
    DELETE /ads/{ad_id}/skills

    Removes a specific skill from an advertisement.
    This endpoint is designed for users to disassociate a previously added skill from an ad.

    Parameters:
    - **db** (Session): The database session dependency used for interacting with the database.
    - **current_user** (DbUsers): Information about the authenticated user, obtained from the authentication token.
    - **ad_id** (str, path parameter): The unique identifier of the ad from which the skill will be removed. This is a
    mandatory parameter.
    - **skill_name** (str, query parameter): The name of the skill to be removed from the ad.

    Request:
    The request should include the ad_id and the skill_name of the skill to be removed.

    Returns:
    204 No Content: Successfully removed the skill from the advertisement. No content is returned in the response.

    Raises:
    - HTTPException 401: If the user is not authenticated.
    - HTTPException 404: Raised if the skill is not found in the specified ad.
    """

    return await remove_skill_from_ad_crud(db, ad_id, skill_name)
