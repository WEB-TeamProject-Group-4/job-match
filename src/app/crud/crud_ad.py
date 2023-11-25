from typing import Type, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import DbAds, DbSkills, adds_skills, DbUsers, DbProfessionals, DbCompanies
from app.schemas.ad import AdCreate, AdSkills, IncludeSkillToAddDisplay, AdDisplay, JobAdStatus, SkillLevel


async def create_ad_crud(db: Session, current_user: DbUsers, schema: AdCreate) -> DbAds:
    current_user_type: str = current_user.type
    current_user_id: str = current_user.id

    if current_user_type == 'professional':
        professional = db.query(DbProfessionals).filter(DbProfessionals.user_id == current_user_id).first()
        user_info = professional.info_id
    elif current_user_type == 'company':
        company = db.query(DbCompanies).filter(DbCompanies.user_id == current_user_id).first()
        user_info = company.info_id
    else:
        raise HTTPException(
            status_code=status.HTTP_400_FORBIDDEN,
            detail='Only professionals and companies can create ads.')

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You need to complete your info before creating an ad')

    is_resume = current_user_type == 'professional'
    new_ad = DbAds(
        description=schema.description,
        location=schema.location,
        status=schema.status.value,
        min_salary=schema.min_salary,
        max_salary=schema.max_salary,
        info_id=user_info,
        is_resume=is_resume
    )
    try:
        db.add(new_ad)
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err.args))
    else:
        db.refresh(new_ad)
        return new_ad


async def get_job_ads_crud(db: Session, user_type: str, description: Optional[str] = None,
                           location: Optional[str] = None,
                           ad_status: Optional[JobAdStatus] = None, min_salary: Optional[int] = None,
                           max_salary: Optional[int] = None, page: Optional[int] = 1) -> List[Type[AdDisplay]]:
    if user_type == 'company':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Section not available for company users'
        )

    query = db.query(DbAds).filter(DbAds.is_resume == 0)

    if description:
        keywords = description.split()
        for keyword in keywords:
            query = query.filter(DbAds.description.ilike(f'%{keyword}%'))
    if location:
        query = query.filter(DbAds.location.ilike(f'%{location}%'))
    if ad_status:
        ad_status_value: str = JobAdStatus.value
        query = query.filter(DbAds.status == ad_status_value)
    if min_salary:
        query = query.filter(DbAds.min_salary >= min_salary)
    if max_salary:
        query = query.filter(DbAds.max_salary <= max_salary)

    ads = query.limit(2).offset((page - 1) * 2).all()

    if not ads:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no results for your search"
        )

    return ads


async def get_resumes_crud(db: Session, user_type: str, description: Optional[str] = None,
                           location: Optional[str] = None,
                           ad_status: Optional[JobAdStatus] = None, min_salary: Optional[int] = None,
                           max_salary: Optional[int] = None, page: Optional[int] = 1) -> List[Type[AdDisplay]]:
    if user_type == 'professional':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Section not available for professional users'
        )

    query = db.query(DbAds).filter(DbAds.is_resume == 1)

    if description:
        keywords = description.split()
        for keyword in keywords:
            query = query.filter(DbAds.description.ilike(f'%{keyword}%'))
    if location:
        query = query.filter(DbAds.location.ilike(f'%{location}%'))
    if ad_status:
        ad_status_value: str = JobAdStatus.value
        query = query.filter(DbAds.status == ad_status_value)
    if min_salary:
        query = query.filter(DbAds.min_salary >= min_salary)
    if max_salary:
        query = query.filter(DbAds.max_salary <= max_salary)

    ads = query.limit(2).offset((page - 1) * 2).all()

    if not ads:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no results for your search"
        )

    return ads


async def update_ad_company_crud(db: Session, current_user: DbUsers, ad_id=str,
                                 description: Optional[str] = None, location: Optional[str] = None,
                                 ad_status: Optional[JobAdStatus] = None, min_salary: Optional[int] = None,
                                 max_salary: Optional[int] = None) -> Type[DbAds]:

    if current_user.type == 'professional':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Restricted section')

    company = db.query(DbCompanies).filter(DbCompanies.user_id == str(current_user.id)).first()
    ad = db.query(DbAds).filter(DbAds.id == ad_id, DbAds.is_deleted == 0).first()
    if not ad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ad not found')

    if company.info_id != ad.info_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only the author can make changes to the ad')

    if description:
        ad.description = description
    if location:
        ad.location = location
    if ad_status:
        ad.status = ad_status.value
    if min_salary:
        ad.min_salary = min_salary
    if max_salary:
        ad.max_salary = max_salary
    db.commit()

    return ad


async def update_ad_professional_crud(db: Session, current_user: DbUsers, ad_id=str,
                                      description: Optional[str] = None, location: Optional[str] = None,
                                      ad_status: Optional[JobAdStatus] = None, min_salary: Optional[int] = None,
                                      max_salary: Optional[int] = None) -> Type[DbAds]:

    if current_user.type == 'company':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Restricted section')

    professional = db.query(DbProfessionals).filter(DbProfessionals.user_id == str(current_user.id)).first()
    ad = db.query(DbAds).filter(DbAds.id == ad_id, DbAds.is_deleted == 0).first()
    if not ad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ad not found')

    if professional.info_id != ad.info_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only the author can make changes to the ad')

    if description:
        ad.description = description
    if location:
        ad.location = location
    if ad_status:
        ad.status = ad_status.value
    if min_salary:
        ad.min_salary = min_salary
    if max_salary:
        ad.max_salary = max_salary
    db.commit()

    return ad


async def delete_ad_crud(db: Session, ad_id: str) -> None:
    ad = db.query(DbAds).filter(DbAds.id == ad_id).first()

    if not ad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ad not found')

    db.delete(ad)
    try:
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err.args))


async def get_ad_by_id_crud(db: Session, ad_id: str) -> Type[AdDisplay]:
    ad = db.query(DbAds).filter(DbAds.id == ad_id).first()

    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Ad with id {ad_id} does not exist'
        )

    return ad


async def create_new_skill(db: Session, schema: AdSkills) -> DbSkills:
    new_skill = DbSkills(
        name=schema.name
    )
    try:
        db.add(new_skill)
        db.commit()
    except IntegrityError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err.args))
    else:
        db.refresh(new_skill)
        return new_skill


async def get_skills_crud(db: Session, page: Optional[int] = 1) -> List[Type[AdSkills]]:
    skills_query = db.query(DbSkills).limit(5).offset((page - 1) * 5)
    skills = skills_query.all()
    if not skills:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no available skills to display, add a skill first'
        )

    return skills


async def update_skill_crud(db: Session, skill_name: str, new_name: str) -> Type[DbSkills]:
    skill = db.query(DbSkills).filter(DbSkills.name == skill_name).first()

    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Skill not found')

    existing_skill = db.query(DbSkills).filter(DbSkills.name == new_name).first()
    if existing_skill:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Skill already exists')

    skill.name = new_name

    try:
        db.commit()
        db.refresh(skill)
        return skill
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err.args))


async def delete_skill_crud(db: Session, skill_name: str) -> None:
    skill = db.query(DbSkills).filter(DbSkills.name == skill_name).first()

    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Skill not found')

    db.delete(skill)
    try:
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err.args))


async def add_skill_to_ad_crud(db: Session, ad_id: str, skill_name: str, level: SkillLevel) -> IncludeSkillToAddDisplay:
    ad = db.query(DbAds).filter(DbAds.id == ad_id).first()
    ad_id: int = ad.id
    skill = db.query(DbSkills).filter(DbSkills.name == skill_name).first()
    skill_id: int = skill.id

    if not ad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ad not found')
    elif not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Skill not found')

    skill_added = db.query(adds_skills) \
        .join(DbSkills, adds_skills.c.skill_id == skill_id) \
        .join(DbAds, adds_skills.c.ad_id == ad_id) \
        .filter(DbAds.id == ad_id, DbSkills.name == skill_name) \
        .first()

    if skill_added:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Skill already added')

    ad_skill = adds_skills.insert().values(ad_id=ad.id, skill_id=skill.id, level=level.value)
    db.execute(ad_skill)

    try:
        db.commit()
        return IncludeSkillToAddDisplay(
            skill_name=skill.name,
            level=level
        )
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err.args))


async def remove_skill_from_ad_crud(db: Session, ad_id: str, skill_name: str) -> None:
    ad = db.query(DbAds).filter(DbAds.id == ad_id).first()
    ad_id: int = ad.id
    skill = db.query(DbSkills).filter(DbSkills.name == skill_name).first()
    skill_id: int = skill.id

    if not ad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ad not found')
    elif not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Skill not found')

    skill_to_remove = (db.query(adds_skills)
                       .join(DbSkills, adds_skills.c.skill_id == skill_id)
                       .join(DbAds, adds_skills.c.ad_id == ad_id)
                       .filter(DbAds.id == ad_id, DbSkills.name == skill_name)
                       .first())

    if not skill_to_remove:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Skill not associated with this ad')

    db.execute(
        adds_skills.delete().where(
            adds_skills.c.ad_id == ad_id,
            adds_skills.c.skill_id == skill.id)
    )

    try:
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err.args))


async def is_admin(user: DbUsers) -> bool:
    return user.type == 'admin'
