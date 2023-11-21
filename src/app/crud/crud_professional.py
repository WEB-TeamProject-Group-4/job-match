from typing import List, Optional, Type

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload


from sqlalchemy import and_

from app.db.models import DbAds, DbInfo, DbProfessionals, DbUsers
from app.schemas.professional import ProfessionalInfoDisplay


async def edit_info(db: Session, user: DbUsers, first_name: Optional[str], 
                    last_name: Optional[str], location: str):
    
    professional: DbProfessionals = await get_professional(db, user)
   
    if first_name:
        professional.first_name = first_name.capitalize()
    if last_name:
        professional.last_name = last_name.capitalize()
    if location:
        if professional.info_id == None:
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
        return {"message": "Professional Info not available"}
    
    resumes = get_resumes(db, professional.info)

    return ProfessionalInfoDisplay(
        first_name=professional.first_name,
        last_name=professional.last_name,
        summary=professional.info.description,
        location=professional.info.location,
        status=professional.status,
        picture=professional.info.picture,
        active_resumes=len(resumes)
    )
    

def get_resumes(db: Session, professional_info: DbInfo):
    resumes_db = db.query(DbAds).filter(DbAds.info_id == professional_info.id).all()
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


def delete_resume_by_id(db: Session, resume_id: str):
    resume = db.query(DbAds).filter(DbAds.id == resume_id).first()
    if resume:
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


def is_user_verified(user: DbUsers) -> Optional[None]:
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Please verify your account.'
        )

async def get_all_approved_professionals(db: Session, first_name: Optional[str],last_name: Optional[str],
                                         status: Optional[str], location: Optional[str]) -> List[Type[DbProfessionals]]:
    queries = [DbUsers.is_verified == True]
    if first_name:
        queries.append(DbProfessionals.first_name.like(f"%{first_name}%"))
    if last_name:
        queries.append(DbProfessionals.last_name.like(f"%{last_name}%"))
    if status:
        queries.append(DbProfessionals.status == status)
    if location:
        queries.append(DbInfo.location.ilike(f"%{location}%"))

    # professionals = db.query(DbProfessionals).join(DbProfessionals.user).filter(*queries).all()

    professionals = (db.query(DbProfessionals).join(DbProfessionals.user).outerjoin(DbProfessionals.info).filter(*queries))
    return professionals
    
    


    
