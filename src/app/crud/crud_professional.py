from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import DbAds, DbInfo, DbProfessionals, DbUsers
from app.schemas.professional import ProfessionalInfoCreate, ProfessionalInfoDisplay


async def edit_info(db: Session, schema: ProfessionalInfoCreate, user: DbUsers):
    professional = await get_professional(db, user)

    if schema.first_name != '' or schema.last_name != '':
        await update_name(db, professional, schema.first_name, schema.last_name)

    if professional.info is None:
        new_info = DbInfo(
            description=schema.summary,
            location=schema.location
        )
        db.add(new_info)
        db.commit()
        db.refresh(new_info)

        professional.info = new_info
        db.commit()
    
    else:
        if schema.summary != '':
            professional.info.description = schema.summary
        if schema.location != '': 
            professional.info.location = schema.location
        db.commit()

    return {"message": "Update successful"}


async def update_name(db: Session, professional: DbProfessionals, first_name: Optional[str], last_name: Optional[str]):
    if first_name != '':
        professional.first_name = first_name
    if last_name != '':
        professional.last_name = last_name

    db.commit()


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
    ad = db.query(DbAds).filter(DbAds.id == resume_id).first()
    if ad:
        db.delete(ad)
        db.commit()

        return {"message": "Deleted successfully"}
    
    return {"message": "Resume not found"}

