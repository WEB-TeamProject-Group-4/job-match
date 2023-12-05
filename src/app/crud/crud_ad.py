from typing import Type, List, Optional, Union, TypeVar

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import DbUsers, DbProfessionals, DbCompanies, DbAds, DbSkills, adds_skills, DbInfo, DbJobsMatches
from app.schemas.ad import AdCreate, AdSkills, AddSkillToAdDisplay, AdDisplay, ResumeStatus, JobAdStatus, SkillLevel

AdModelType = TypeVar('AdModelType', bound=Union[Type[DbAds], DbAds])
SkillModelType = TypeVar('SkillModelType', bound=Union[Type[DbSkills], DbSkills])
CompanyModelType = TypeVar('CompanyModelType', bound=Union[Type[DbCompanies], DbCompanies])
ProfessionalModelType = TypeVar('ProfessionalModelType', bound=Union[Type[DbProfessionals], DbProfessionals])


async def create_ad_crud(db: Session, current_user: DbUsers, schema: AdCreate) -> DbAds:
    """
    Function Name: create_ad_crud

    Description: Handles the backend logic for creating a new advertisement. It determines whether the current user
    is a professional or associated with a company, checks if the user's information is complete, and then creates
    the advertisement in the database.

    Parameters:
    - **db** (Session): The active database session.
    - **current_user** (DbUsers): The authenticated user attempting to create the ad.
    - **schema** (AdCreate): The schema containing details for the ad creation.

    Returns:
    DbAds: The newly created advertisement record.

    Errors:
    - Raises HTTPException with status 400 if the user's information is incomplete.
    """

    professional = await get_professional(db, current_user)
    company = await get_company(db, current_user)
    user_info = await professional.info_id if professional else company.info_id if company else None

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Complete your info before creating an ad')

    is_resume = current_user.type == 'professional'
    new_ad = DbAds(
        description=schema.description,
        location=schema.location,
        status=schema.status.value,
        min_salary=schema.min_salary,
        max_salary=schema.max_salary,
        info_id=user_info,
        is_resume=is_resume)

    db.add(new_ad)
    db.commit()

    return new_ad


async def get_resumes_crud(db: Session, description: Optional[str] = None, location: Optional[str] = None,
                           ad_status: Optional[ResumeStatus] = None, min_salary: Optional[int] = None,
                           max_salary: Optional[int] = None, page: Optional[int] = 1) -> List[Type[AdDisplay]]:
    """
    Function Name: get_resumes_crud

    Description: Retrieves a paginated list of resume advertisements based on provided search criteria. This function
    filters resumes from the database according to various optional parameters, such as description, location,
    status, and salary range.

    Parameters:
    - **db** (Session): The active database session.
    - **description** (Optional[str]): An optional search parameter to filter resumes by their description.
    - **location** (Optional[str]): An optional search parameter to filter resumes by their location.
    - **ad_status** (Optional[ResumeStatus]): An optional search parameter to filter resumes by their status.
    - **min_salary** (Optional[int]): An optional search parameter to filter resumes by minimum salary.
    - **max_salary** (Optional[int]): An optional search parameter to filter resumes by maximum salary.
    - **page** (Optional[int], default=1): Pagination parameter to specify the page number of results.

    Returns:
    List[Type[AdDisplay]]: A list of AdDisplay objects representing the filtered resumes.

    Errors:
    - Raises HTTPException with status 404 if no resumes match the search criteria.
    """

    query = db.query(DbAds).filter(DbAds.is_resume == True, DbAds.is_deleted == False)
    query = await filter_ads(query, description, location, ad_status, min_salary, max_salary)
    ads = await paginate(query, page)

    if not ads:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no results for your search")

    return ads


async def get_job_ads_crud(db: Session, description: Optional[str] = None, location: Optional[str] = None,
                           ad_status: Optional[JobAdStatus] = None, min_salary: Optional[int] = None,
                           max_salary: Optional[int] = None, page: Optional[int] = 1) -> List[Type[AdDisplay]]:
    """
    Function Name: get_job_ads_crud

    Description: Retrieves a paginated list of job advertisements based on provided search criteria. This function
    filters resumes from the database according to various optional parameters, such as description, location,
    status, and salary range.

    Parameters:
    - **db** (Session): The active database session.
    - **description** (Optional[str]): An optional search parameter to filter resumes by their description.
    - **location** (Optional[str]): An optional search parameter to filter resumes by their location.
    - **ad_status** (Optional[JobAdStatus]): An optional search parameter to filter job ads by their status.
    - **min_salary** (Optional[int]): An optional search parameter to filter resumes by minimum salary.
    - **max_salary** (Optional[int]): An optional search parameter to filter resumes by maximum salary.
    - **page** (Optional[int], default=1): Pagination parameter to specify the page number of results.

    Returns:
    List[Type[AdDisplay]]: A list of AdDisplay objects representing the filtered resumes.

    Errors:
    - Raises HTTPException with status 404 if no job ads match the search criteria.
    """

    query = db.query(DbAds).filter(DbAds.is_resume == False, DbAds.is_deleted == False)
    query = await filter_ads(query, description, location, ad_status, min_salary, max_salary)
    ads = await paginate(query, page)

    if not ads:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no results for your search")

    return ads


async def update_resumes_crud(db: Session, current_user: DbUsers, ad_id: str,
                              description: Optional[str] = None, location: Optional[str] = None,
                              ad_status: Optional[ResumeStatus] = None, min_salary: Optional[int] = None,
                              max_salary: Optional[int] = None) -> AdModelType:
    """
    Function Name: update_resumes_crud

    Description: Retrieves a paginated list of resume advertisements based on provided search criteria. This function
    filters resumes from the database according to various optional parameters, such as description, location,
    status, and salary range.

    Parameters:
    - **db** (Session): The active database session.
    - **current_user** (DbUsers): The current authenticated user attempting to update the ad.
    - **ad_id** (str): The unique identifier of the resume ad to be updated.
    - **description** (Optional[str]): New description for the resume ad (optional).
    - **location** (Optional[str]): New location for the resume ad (optional).
    - **ad_status** (Optional[JobAdStatus]): New status for the resume ad (optional).
    - **min_salary** (Optional[int]): New minimum salary for the resume ad (optional).
    - **max_salary** (Optional[int]): New maximum salary for the resume ad (optional).

    Returns:
    AdModelType: The updated resume advertisement object.

    Errors:
    - Raises HTTPException with status 400 if the ad is not a resume ad.
    - Raises HTTPException with status 403 if the user is not authorized to update the ad.
    """

    ad = await get_ad(db, ad_id)
    if not ad.is_resume:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot update job ads')

    professional = await get_professional(db, current_user)
    await check_user_authorization(current_user, professional, ad)
    await update_ad(ad, description, location, ad_status, min_salary, max_salary)

    db.commit()

    return ad


async def update_job_ads_crud(db: Session, current_user: DbUsers, ad_id: str,
                              description: Optional[str] = None, location: Optional[str] = None,
                              ad_status: Optional[JobAdStatus] = None, min_salary: Optional[int] = None,
                              max_salary: Optional[int] = None) -> AdModelType:
    """
    Function Name: update_job_ads_crud

    Description: Retrieves a paginated list of job advertisements based on provided search criteria. This function
    filters job ads from the database according to various optional parameters, such as description, location,
    status, and salary range.

    Parameters:
    - **db** (Session): The active database session.
    - **current_user** (DbUsers): The current authenticated user attempting to update the ad.
    - **ad_id** (str): The unique identifier of the resume ad to be updated.
    - **description** (Optional[str]): New description for the job ad (optional).
    - **location** (Optional[str]): New location for the job ad (optional).
    - **ad_status** (Optional[JobAdStatus]): New status for the job ad (optional).
    - **min_salary** (Optional[int]): New minimum salary for the job ad (optional).
    - **max_salary** (Optional[int]): New maximum salary for the job ad (optional).

    Returns:
    AdModelType: The updated job advertisement object.

    Errors:
    - Raises HTTPException with status 400 if the ad is not a job ad.
    - Raises HTTPException with status 403 if the user is not authorized to update the ad.
    """

    ad = await get_ad(db, ad_id)
    if ad.is_resume:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot update resumes')

    company = await get_company(db, current_user)
    await check_user_authorization(current_user, company, ad)
    await update_ad(ad, description, location, ad_status, min_salary, max_salary)

    db.commit()

    return ad


async def get_ad_by_id_crud(db: Session, ad_id: str) -> Type[AdDisplay]:
    """
    Function Name: get_ad_by_id_crud

    Description: Retrieves an advertisement by its unique identifier. This function is designed to fetch the details
    of a specific ad, provided it has not been marked as deleted.

    Parameters:
    - **db** (Session): The active database session.
    - **ad_id** (str): The unique identifier of the resume ad to be updated.

    Returns:
    Type[AdDisplay]: An AdDisplay object representing the advertisement's details.

    Errors:
    - HTTPException 404: Raised if no advertisement is found with the given ad_id.
    """

    ad = await get_ad(db, ad_id)
    return ad


async def delete_ad_crud(db: Session, ad_id: str, current_user: DbUsers) -> None:
    """
    Function Name: delete_ad_crud

    Description: Handles the deletion of an advertisement. This function marks an ad as deleted based on its ID. It
    checks user authorization before proceeding with the deletion and handles any associated tasks such as removing
    job matches and updating resume status if necessary.

    Parameters:
    - **db** (Session): The active database session.
    - **ad_id** (str): The unique identifier of the resume ad to be updated.
    - **current_user** (DbUsers): The current authenticated user attempting to update the ad.

    Process: Retrieves the ad using its ID. Checks if the current user is a professional or a company, and checks if
    they are authorized to delete the ad. For professional users, checks if the ad is their main resume. Removes any
    job matches associated with the ad. Sets the is_deleted flag of the ad to True.

    Errors:
    - HTTPException 404: Raised if the user is not authorized to delete the ad.
    - HTTPException 404: Raised if the ad does not exist.
    """

    ad = await get_ad(db, ad_id)
    professional = await get_professional(db, current_user)
    company = await get_company(db, current_user)

    if professional:
        await check_user_authorization(current_user, professional, ad)
        await if_main_resume(db, ad)
    else:
        await check_user_authorization(current_user, company, ad)

    await delete_job_matches(db, ad)
    ad.is_deleted = True

    db.commit()

    return


async def create_new_skill(db: Session, schema: AdSkills) -> DbSkills:
    """
    Function Name: create_new_skill

    Description: Creates a new skill entry in the database.
    This function is responsible for adding a unique skill, as specified in the given schema, to the skills table.

    Parameters:
    - **db** (Session): The active database session.
    - **schema** (AdSkills): The schema containing details for the ad creation.

    Process: Verifies if the skill already exists in the database to avoid duplicates. If the skill does not exist,
    it creates a new DbSkills object with the provided name. Adds the new skill to the database session and commits
    the changes. Refreshes the session to reflect the new state and returns the newly created skill.

    Errors:
    - Raises HTTPException with status 400 if the user's information is incomplete.
    """

    await new_skill_already_exists(db, schema.name)
    new_skill = DbSkills(name=schema.name)
    db.add(new_skill)

    db.commit()
    db.refresh(new_skill)

    return new_skill


async def get_skills_crud(db: Session, page: Optional[int] = 1) -> List[Type[AdSkills]]:
    """
    Function Name: get_skills_crud

    Description: Retrieves a paginated list of skills from the database. This function fetches skills that have not
    been marked as deleted, presenting them in a paginated format based on the specified page number.

    Parameters:
    - **db** (Session): The active database session.
    - **page** (Optional[int], default=1): The page number for the paginated response. Each page includes a set number
     of skills (defaults to 5 skills per page).

    Process: Forms a query to fetch skills that are not marked as deleted. Applies pagination to the query,
    dividing the results into pages.

    Returns:
    List[Type[AdSkills]]: A list of AdSkills objects, each representing a skill.

    Errors:
    - Raises HTTPException with status 404 if there are no skills available to display on the requested page.
    """

    query = db.query(DbSkills).filter(DbSkills.is_deleted == False)
    skills = await paginate(query, page, 5)

    if not skills:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='There are no available skills to display, add a skill first')

    return skills


async def update_skill_crud(db: Session, skill_name: str, new_name: str) -> SkillModelType:
    """
    Function Name: update_skill_crud

    Description: Updates the name of an existing skill in the database. This function allows for renaming a skill,
    ensuring the new name is unique and does not conflict with existing skills.

    Parameters:
    - **db** (Session): The active database session.
    - **skill_name** (str): The current name of the skill to be updated.
    - **new_name** (str): The new name for the skill.

    Process: Fetches the skill using the current name. Ensures that the new name does not already exist in the database.
    If the new name is unique, updates the skill with the new name.

    Returns:
    SkillModelType: The skill object with the updated name.

    Errors:
    - Raises HTTPException with status 400 if a skill with the new name already exists.
    - Raises HTTPException with status 404 if the skill with the given current name does not exist.
    """

    skill = await get_skill(db, skill_name)
    await new_skill_already_exists(db, new_name)
    skill.name = new_name

    db.commit()
    db.refresh(skill)

    return skill


async def delete_skill_crud(db: Session, skill_name: str) -> None:
    """
    Function Name: delete_skill_crud

    Description: Soft-deletes a skill from the database. This function marks a specified skill as deleted, effectively
    removing it from active use while retaining its record in the database.

    Parameters:
    - **db** (Session): The active database session.
    - **skill_name** (str, query parameter): The current name of the skill to be updated.

    Process: Fetches the skill using the provided name. Sets the is_deleted flag of the skill to True.

    Errors:
    - Raises HTTPException with status 404 if the skill with the given current name does not exist.
    """

    skill = await get_skill(db, skill_name)
    skill.is_deleted = True

    db.commit()

    return


async def add_skill_to_ad_crud(db: Session, ad_id: str, skill_name: str, level: SkillLevel) -> AddSkillToAdDisplay:
    """
    Function Name: add_skill_to_ad_crud

    Description: Associates a specific skill with an advertisement along with its proficiency level. This function is
    designed to add a skill to an ad, checking for duplicates to ensure the same skill is not added more than once

    Parameters:
    - **db** (Session): The active database session.
    - **ad_id** (str): The unique identifier of the advertisement to which the skill will be added.
    - **skill_name** (str, query parameter): The name of the skill to be added to the advertisement.
    - **level** (SkillLevel): The proficiency level of the skill (e.g., beginner, intermediate, expert).

    Process: Fetches the advertisement and skill using their respective identifiers. Verifies if the skill is already
    added to the ad. If not already added, associates the skill with the ad, including the proficiency level.

    Returns:
    AddSkillToAdDisplay: An object representing the added skill and its level in the context of the ad.

    Errors:
    - Raises HTTPException with status 400 if the skill is already associated with the ad.
    - Raises HTTPException with status 404 if the skill with the given current name does not exist.
    """

    ad = await get_ad(db, ad_id)
    skill = await get_skill(db, skill_name)

    skill_already_added = db.query(adds_skills) \
        .join(DbSkills, adds_skills.c.skill_id == str(skill.id)) \
        .join(DbAds, adds_skills.c.ad_id == str(ad.id)) \
        .filter(DbAds.id == ad_id, DbSkills.name == skill_name) \
        .first()

    if skill_already_added:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"'{skill_name}' already added to this ad")

    ad_skill = adds_skills.insert().values(ad_id=ad.id, skill_id=skill.id, level=level.value)

    db.execute(ad_skill)
    db.commit()

    return AddSkillToAdDisplay(
        skill_name=skill.name,
        level=level)


async def remove_skill_from_ad_crud(db: Session, ad_id: str, skill_name: str) -> None:
    """
    Function Name: remove_skill_from_ad_crud

    Description: Removes a specific skill association from an advertisement. This function is intended for
    disassociating a previously added skill from an ad, ensuring that the skill is no longer linked to that
    particular advertisement.

    Parameters:
    - **db** (Session): The active database session.
    - **ad_id** (str): The unique identifier of the advertisement to which the skill will be added.
    - **skill_name** (str, query parameter): The name of the skill to be added to the advertisement.

    Process: Fetches the advertisement and skill using their respective identifiers. Identifies if the specified skill
    is currently associated with the ad. If the skill is found, removes the association from the ad.

    Errors:
    - Raises HTTPException with status 404 if the specified skill is not associated with the given ad.
    """

    ad = await get_ad(db, ad_id)
    skill = await get_skill(db, skill_name)

    skill_to_remove = (db.query(adds_skills)
                       .join(DbSkills, adds_skills.c.skill_id == str(skill.id))
                       .join(DbAds, adds_skills.c.ad_id == str(ad.id))
                       .filter(DbAds.id == ad_id, DbSkills.name == skill_name)
                       .first())

    if not skill_to_remove:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"'{skill_name}' does not exist in this ad")

    db.execute(
        adds_skills.delete().where(
            adds_skills.c.ad_id == ad_id,
            adds_skills.c.skill_id == skill.id))

    db.commit()

    return


async def filter_ads(query, description=None, location=None, ad_status=None, min_salary=None, max_salary=None):
    """
    Function Name: filter_ads

    Description: Applies various filters to an existing query of advertisements. This function enhances a query by
    adding conditions based on provided criteria such as description, location, ad status, and salary range. It's
    designed to be a flexible tool for refining advertisement queries according to user-specific needs.

    Parameters:
    - **query**: The initial query object to which filters will be applied.
    - **description** (Optional[str]): A keyword or phrase to filter ads by their description.
     The function splits the description into keywords and checks for matches in each ad's description.
    - **location** (Optional[str]): A location string to filter ads by their geographical location.
    - **ad_status** (Optional[JobAdStatus]): An ad status value to filter ads by their current status.
    - **min_salary** (Optional[int]): A minimum salary value to filter ads that offer at least this salary.
    - **max_salary** (Optional[int]): A maximum salary value to filter ads that offer no more than this salary.

    Returns: The modified query object with applied filters.
    """

    if description:
        keywords = description.split()
        for keyword in keywords:
            query = query.filter(DbAds.description.ilike(f'%{keyword}%'))
    if location:
        query = query.filter(DbAds.location.ilike(f'%{location}%'))
    if ad_status:
        query = query.filter(DbAds.status == ad_status.value)
    if min_salary:
        query = query.filter(DbAds.min_salary >= min_salary)
    if max_salary:
        query = query.filter(DbAds.max_salary <= max_salary)

    return query


async def update_ad(ad: Type[DbAds], description: Optional[str] = None, location: Optional[str] = None,
                    ad_status: Union[Optional[JobAdStatus], Optional[ResumeStatus], None] = None,
                    min_salary: Optional[int] = None, max_salary: Optional[int] = None):
    """
    Function Name: update_ad

    Description: Updates the attributes of an advertisement object. This function modifies various fields of an
    existing advertisement, such as its description, location, status, and salary range, based on provided values.

    Parameters:
    - **ad_id** (Type[DbAds]): The advertisement object to be updated.
    - **description** (Optional[str]): : The new description for the ad. If provided, the ad's description is updated.
    - **location** (Optional[str]): The new location for the ad. If provided, the ad's location is updated.
    - **ad_status** (Union[Optional[JobAdStatus], Optional[ResumeStatus], None]): The new status for the ad.
     If provided, the ad's status is updated to the specified value.
    - **min_salary** (Optional[int]): The new minimum salary for the ad. If provided, the ad's min salary is updated.
    - **max_salary** (Optional[int]): The new maximum salary for the ad. If provided, the ad's max salary is updated.
    """

    if description is not None:
        ad.description = description
    if location is not None:
        ad.location = location
    if ad_status is not None:
        ad.status = ad_status.value
    if min_salary is not None:
        ad.min_salary = min_salary
    if max_salary is not None:
        ad.max_salary = max_salary


async def paginate(query, page: int, page_size: Optional[int] = 3):
    """
    Function Name: paginate

    Description: Applies pagination to a SQL Alchemy query object. This function limits the results to a specified
     number per page and computes the correct offset based on the page number.

    Parameters:
    - **query**: The initial query object to which filters will be applied.
    - **page** (int): The page number of the results to retrieve.
    - **page_size ** (Optional[int], default=3): The number of results per page.

    Returns: A list of results for the specified page.
    """
    return query.limit(page_size).offset((page - 1) * page_size).all()


async def get_ad(db: Session, ad_id: str) -> AdModelType:
    """
    Function Name: get_ad

    Description: Fetches an advertisement from the database using its unique ID. The function ensures that only
     non-deleted ads are retrieved.

    Parameters:
    - **db** (Session): The active database session.
    - **ad_id** (str): The unique identifier of the advertisement.

    Returns: AdModelType: The advertisement object if found.
    """

    ad = db.query(DbAds).filter(DbAds.id == ad_id, DbAds.is_deleted == False).first()
    if not ad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ad not found')

    return ad


async def get_skill(db: Session, skill_name: str) -> SkillModelType:
    """
    Function Name: get_skill

    Description: Retrieves a skill from the database based on its name. The function gets skills that are not deleted.

    Parameters:
    - **db** (Session): The active database session.
    - **skill_name** (str): The name of the skill to retrieve.

    Returns: SkillModelType: The skill object if found.

    Errors:
    - Raises HTTPException with status 404 if the skill is not found or has been marked as deleted.
    """

    skill = db.query(DbSkills).filter(DbSkills.name == skill_name, DbSkills.is_deleted == False).first()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Skill not found')

    return skill


async def new_skill_already_exists(db: Session, skill_name: str) -> None:
    """
    Function Name: new_skill_already_exists

    Description: Checks if a skill with the given name already exists in the database. This function is used to prevent
     the creation of duplicate skills.

    Parameters:
    - **db** (Session): The active database session for querying the database.
    - **skill_name** (str): The name of the skill to check for existence.

    Returns: None: Indicates that the skill does not exist and can be created.

    Errors:
    - Raises HTTPException with status 400 if a skill with the given name already exists.
    """

    skill = db.query(DbSkills).filter(DbSkills.name == skill_name, DbSkills.is_deleted == False).first()
    if skill:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Skill with name '{skill_name}' already"
                                                                            f" exists")


async def get_professional(db: Session, current_user: DbUsers) -> ProfessionalModelType | None:
    """
    Function Name: get_professional

    Description: Retrieves the professional details associated with the current user.

    Parameters:
    - **db** (Session): The active database session for querying the database.
    - **current_user** (DbUsers): The current authenticated user.

    Returns: ProfessionalModelType | None: The professional details if the user is a professional, otherwise None.
    """

    professional = db.query(DbProfessionals).filter(DbProfessionals.user_id == str(current_user.id)).first()

    return professional


async def get_company(db: Session, current_user: DbUsers) -> CompanyModelType | None:
    """
    Function Name: get_company

    Description: Retrieves the company details associated with the current user.

    Parameters:
    - **db** (Session): The active database session for querying the database.
    - **current_user** (DbUsers): The current authenticated user.

    Returns: CompanyModelType | None: The company details if the user is associated with a company, otherwise None.
    """
    company = db.query(DbCompanies).filter(DbCompanies.user_id == str(current_user.id)).first()

    return company


async def check_user_authorization(user: DbUsers, author: Union[ProfessionalModelType, CompanyModelType],
                                   ad: AdModelType):
    """
    Function Name: check_user_authorization

    Description: Verifies if a user is authorized to make changes to an advertisement. It checks if the user is either
    the author of the ad or an admin.

    Parameters:
    - **user** (DbUsers): The user attempting to make changes.
    - **author** (Union[ProfessionalModelType, CompanyModelType]): The author, which can be a professional or a company.
    - **ad** (AdModelType): The advertisement in question.

    Errors:
    - Raises HTTPException with status 403 if the user is not authorized (not the author or an admin).
    """
    if user.type != 'admin' and author.info_id != ad.info_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only the author can apply changes')


async def if_main_resume(db: Session, ad: AdModelType) -> None:
    """
    Function Name: if_main_resume

    Description: Designed to use when deleting an ad. Checks if an advertisement is set as a main resume for a
    professional. If so, it clears the main resume designation.

    Parameters:
    - **db ** (Session): The active database session.
    - **ad** (AdModelType): The advertisement being checked.

    Returns: None: Indicates completion of the operation.
    """
    resume = db.query(DbInfo).filter(DbInfo.main_ad == str(ad.id)).first()
    if resume:
        resume.main_ad = None
        return


async def delete_job_matches(db: Session, ad: AdModelType):
    """
    Function Name: delete_job_matches

    Description: Soft-deletes job matches associated with a given advertisement.
    The function marks all job matches related to the ad as deleted.

    Parameters:
    - **db ** (Session): The active database session.
    - **ad** (AdModelType): The advertisement whose job matches are to be deleted.

    Returns: None: Indicates successful completion of the operation.
    """
    if ad.is_resume:
        job_matches = db.query(DbJobsMatches).filter(DbJobsMatches.resume_id == str(ad.id)).all()
    else:
        job_matches = db.query(DbJobsMatches).filter(DbJobsMatches.ad_id == str(ad.id)).all()

    for j_m in job_matches:
        j_m.is_deleted = True

    return
