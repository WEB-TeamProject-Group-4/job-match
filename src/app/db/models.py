from app.db.database import Base
from sqlalchemy import Table, Column, String, ForeignKey, Boolean, LargeBinary, INT
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
    ad_id = Column(String(50), ForeignKey('ads.id'), primary_key=True, nullable=False)
    professional_id = Column(String(50), ForeignKey('professionals.id'), primary_key=True, nullable=False)
    company_id = Column(String(50), ForeignKey('companies.id'), primary_key=True, nullable=False)
    approved = Column(Boolean)
    professional = relationship('DbProfessionals', back_populates='match')
    company = relationship('DbCompanies', back_populates='match')
    ad = relationship('DbAds', back_populates='match')


class DbUsers(Base):
    __tablename__ = 'users'
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    username = Column(String(45), nullable=False, unique=True)
    password = Column(String(150), nullable=False)
    email = Column(String(45), nullable=False, unique=True)
    type = Column(String(45), nullable=False)
    is_verified = Column(Boolean, default=False)
    professional = relationship('DbProfessionals', back_populates='user')
    company = relationship('DbCompanies', back_populates='user')


class DbProfessionals(Base):
    __tablename__: str = 'professionals'
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    status = Column(String(45), nullable=True, default=None)
    user_id = Column(String(50), ForeignKey('users.id'), nullable=False)
    user = relationship('DbUsers', back_populates='professional')
    info_id = Column(String(50), ForeignKey('info.id'), nullable=True, default=None)
    info = relationship('DbInfo', back_populates='professional')
    match = relationship('DbJobsMatches', back_populates='professional')


class DbCompanies(Base):
    __tablename__: str = 'companies'
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    name = Column(String(45), nullable=False, unique=True)
    contacts = Column(String(45), nullable=True, default=None)
    user_id = Column(String(50), ForeignKey('users.id'), nullable=False)
    user = relationship('DbUsers', back_populates='company')
    info_id = Column(String(50), ForeignKey('info.id'), nullable=True, default=None)
    info = relationship('DbInfo', back_populates='company')
    match = relationship("DbJobsMatches", back_populates='company')

class DbInfo(Base):
    __tablename__: str = 'info'
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    description = Column(String(45), nullable=True)
    location = Column(String(45), nullable=True)
    picture = Column(LargeBinary, nullable=True, default=None)
    company = relationship('DbCompanies', back_populates='info')
    professional = relationship('DbProfessionals', back_populates='info')
    ad_id = Column(String(50), ForeignKey('ads.id'), nullable=False)
    ad = relationship('DbAds', back_populates='info')


class DbAds(Base):
    __tablename__: str = 'ads'
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    description = Column(String(100), nullable=False)
    location = Column(String(45), nullable=False)
    status = Column(String(45), nullable=False)
    salary_range_id = Column(String(50), ForeignKey('salary_ranges.id'), nullable=False)
    salary_range = relationship('DbSalaryRanges', back_populates='ad')
    info = relationship('DbInfo', back_populates='ad')
    requirements = relationship("DbSkills", secondary=adds_skills, back_populates="ad")
    match = relationship('DbJobsMatches', back_populates='ad')


class DbSkills(Base):
    __tablename__ = 'skills'
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    name = Column(String(45), nullable=False)
    ad = relationship("DbAds", secondary=adds_skills, back_populates="requirements")


class DbSalaryRanges(Base):
    __tablename__: str = 'salary_ranges'
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    min = Column(INT, nullable=False)
    max = Column(INT, nullable=False)
    ad = relationship('DbAds', back_populates='salary_range')
