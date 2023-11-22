from typing import Annotated, List, Optional, Type

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload


from sqlalchemy import and_
from app.core.auth import get_current_user

from app.db.models import DbAds, DbInfo, DbProfessionals, DbUsers
from app.schemas.professional import ProfessionalInfoDisplay


DEFAULT_VALUE_ITEMS_PER_PAGE = 10


async def edit_info(db: Session, user: DbUsers, first_name: Optional[str], 
                    last_name: Optional[str], location: str):
    
    professional: DbProfessionals = await get_professional(db, user)
   
    if first_name:
        professional.first_name = first_name.capitalize()
    if last_name:
        professional.last_name = last_name.capitalize()
    if location:
        if professional.info is None:
            await create_professional_info(db, professional, summary="Your default summary", location=location)
        else:
            professional.info.location = location.capitalize()
    
    db.commit()
    
    return {"message": "Update successful"}


async def create_professional_info(db: Session, professional: DbProfessionals, summary: str, location: str):
    if summary and location:
        new_info = DbInfo(description=summary,location=location)
        db.add(new_info)
        db.commit()
        db.refresh(new_info)

        professional.info = new_info
        db.commit()
        
    else:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fields should be valid: 'summary' and 'location'!")
    

async def get_info(db: Session, user: DbUsers):
    professional: DbProfessionals = await get_professional(db, user)
    if professional.info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Please edit your personal information.')
    
    resumes = get_resumes(db, professional)

    return ProfessionalInfoDisplay(
        first_name=professional.first_name,
        last_name=professional.last_name,
        summary=professional.info.description,
        location=professional.info.location,
        status=professional.status,
        picture=professional.info.picture,
        active_resumes=len(resumes)
    )
    

def get_resumes(db: Session, professional: DbProfessionals):
    resumes_db = db.query(DbAds).filter(DbAds.info_id == professional.info.id).all()
    resumes = [
            {
                "id": resume.id,
                "description": resume.description,
                "location": resume.location,
                "status": resume.status,
                "min_salary": resume.min_salary,
                "max_salary": resume.max_salary,
            }
            for resume in resumes_db
        ]

    return resumes


async def change_status(status: str, db: Session, user: DbProfessionals):
    professional: DbProfessionals = await get_professional(db, user)
    professional.status = status
    db.commit()

    return {'message': 'Status changed successfully!'}


async def get_professional(db: Session, user: DbUsers):
    professional = (db.query(DbProfessionals).filter(DbProfessionals.user_id == user.id).first())
    if not professional:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='You are not logged as professional')
    
    return professional


async def delete_resume_by_id(db: Session, user: DbUsers, resume_id: str):
    professional: DbProfessionals = await get_professional(db, user)
    resume:DbAds = db.query(DbAds).filter(DbAds.id == resume_id).first()
    if resume and resume.info.id == professional.info.id:
        db.delete(resume)
        db.commit()

        raise HTTPException(status_code=204, detail="Main resume changed successfully")
    
    raise HTTPException(status_code=404, detail="Resume not found")


async def setup_main_resume(resume_id: str, db: Session, user: DbUsers):
    professional: DbProfessionals = await get_professional(db, user)
    resume = db.query(DbAds).filter(DbAds.id == resume_id).first()
    if resume:
        professional.info.main_ad = resume.id
        db.commit()

        return {'message': 'Main resume changed successfully'}
    
    return {"message": "Resume not found"}


def is_user_verified(user: Annotated[DbUsers, Depends(get_current_user)]) -> Optional[None]:
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Please verify your account.'
        )
    return user

async def get_all_approved_professionals(db: Session, first_name: Optional[str],last_name: Optional[str],
                                         status: Optional[str], location: Optional[str], page: Optional[int], page_items: Optional[int]) -> List[Type[DbProfessionals]]:
    queries = [DbUsers.is_verified == True]
    if first_name:
        queries.append(DbProfessionals.first_name.like(f"%{first_name}%"))
    if last_name:
        queries.append(DbProfessionals.last_name.like(f"%{last_name}%"))
    if status:
        queries.append(DbProfessionals.status == status)
    if location:
        queries.append(DbInfo.location.ilike(f"%{location}%"))

    page = page if page is not None else 1
    page_items = page_items if page_items is not None else DEFAULT_VALUE_ITEMS_PER_PAGE

    professionals = (db.query(DbProfessionals).join(DbProfessionals.user).outerjoin(DbProfessionals.info).filter(*queries))
    total_elements = professionals.count()

    return professionals.offset((page - 1) * page_items).limit(page_items).all()
    
    
async def edit_professional_summary(db: Session, user: DbUsers, summary: str):
    professional: DbProfessionals = await get_professional(db, user)
    if professional.info is None:
        new_info = DbInfo(description=summary,location='')
        db.add(new_info)
        db.commit()
        db.refresh(new_info)

        professional.info = new_info
        db.commit()

    else:
        professional.info.description = summary
        db.commit()
    
    
    return {'message': 'Your summary has been updated successfully'}
    


    
