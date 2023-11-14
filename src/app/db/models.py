from app.db.database import Base
from sqlalchemy import Table, Column, String, ForeignKey, Boolean, LargeBinary
from sqlalchemy.orm import relationship
import uuid

adds_skills = Table(
    'adds_skills',
    Base.metadata,
    Column('skill_id', String, ForeignKey('skills.id')),
    Column('ad_id', String, ForeignKey('ads.id')),
    Column('level', String),
)


class DbJobsMatches(Base):
    __tablename__ = 'jobs_matches'
    ad_id = Column(String(50), ForeignKey('ads.id'), primary_key=True)
    professional_id = Column(String(50), ForeignKey('professionals.id'), primary_key=True)
    company_id = Column(String(50), ForeignKey('companies.id'))
    approved = Column(Boolean)
    professional = relationship('DbProfessionals', back_populates='match')
    company = relationship('DbCompanies', back_populates='match')
    ad = relationship('DbAds', back_populates='match')


class DbUsers(Base):
    __tablename__ = 'users'
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    username = Column(String)
    password = Column(String)
    email = Column(String)
    type = Column(String)
    is_verified = Column(Boolean)
    professional = relationship('DbProfessionals', back_populates='user')
    company = relationship('DbCompanies', back_populates='user')


class DbProfessionals(Base):
    __tablename__: str = 'professionals'
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    first_name = Column(String)
    last_name = Column(String)
    user_id = Column(String(50), ForeignKey('users.id'))
    user = relationship('DbUsers', back_populates='professional')
    professional_info_id = Column(String(50), ForeignKey('professional_info.id'))
    professional_info = relationship('DbProfessionalInfo', back_populates='professional')
    match = relationship('DbJobsMatches', back_populates='professional')


class DbCompanies(Base):
    __tablename__: str = 'companies'
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    name = Column(String)
    user_id = Column(String(50), ForeignKey('users.id'))
    user = relationship('DbUsers', back_populates='company')
    company_info_id = Column(String(50), ForeignKey('company_info.id'))
    company_info = relationship('DbCompanyInfo', back_populates='company')
    match = relationship("DbJobsMatches", back_populates='company')
    # ads = relationship('DbAds', secondary=DbJobsMatches, backref='ads_associated')


class DbProfessionalInfo(Base):
    __tablename__: str = 'professional_info'
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    status = Column(String)
    professional = relationship('DbProfessionals', back_populates='professional_info')
    info_id = Column(String(50), ForeignKey('info.id'))
    info = relationship('DbInfo', back_populates='professional_info')


class DbCompanyInfo(Base):
    __tablename__: str = 'company_info'
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    contacts = Column(String)
    company = relationship('DbCompanies', back_populates='company_info')
    info_id = Column(String(50), ForeignKey('info.id'))
    info = relationship('DbInfo', back_populates='company_info')


class DbInfo(Base):
    __tablename__: str = 'info'
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    description = Column(String)
    location = Column(String)
    picture = Column(LargeBinary, nullable=True, default=None)
    company_info = relationship('DbCompanyInfo', back_populates='info')
    professional_info = relationship('DbProfessionalInfo', back_populates='info')
    ad_id = Column(String(50), ForeignKey('ads.id'))
    ad = relationship('DbAds', back_populates='info')


class DbAds(Base):
    __tablename__: str = 'ads'
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    description = Column(String)
    location = Column(String)
    status = Column(String)
    salary_range_id = Column(String(50), ForeignKey('salary_ranges.id'))
    salary_range = relationship('DbSalaryRanges', back_populates='ad')
    info = relationship('DbInfo', back_populates='ad')
    requirements = relationship("DbSkills", secondary=adds_skills, backref="ad_associated")
    match = relationship('DbJobsMatches', back_populates='ad')


class DbSkills(Base):
    __tablename__ = 'skills'
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    name = Column(String)
    ad = relationship("DbAds", secondary=adds_skills, backref="skills_associated")


class DbSalaryRanges(Base):
    __tablename__: str = 'salary_ranges'
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    min = Column(String)
    max = Column(String)
    ad = relationship('DbAds', back_populates='salary_range')
