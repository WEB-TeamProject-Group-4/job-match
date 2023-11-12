from typing import Optional
from database import Base
from sqlalchemy import Table, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship


requirements_has_ads = Table(
    'requirements_has_ads',
    Base.metadata,
    Column('requirements_id', String, ForeignKey('requirements.id')),
    Column('ad_id', String, ForeignKey('ads.id')),
    Column('level', String), 
)

jobs_matches = Table(
    'jobs_matches',
    Base.metadata,
    Column('ad_id', String, ForeignKey('ads.id')),
    Column('professional_id', String, ForeignKey('professionals.id')),
    Column('company_id', String, ForeignKey('companies.id')),
    Column('approved', Boolean), 
)

class DbUsers(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)
    type = Column(String)
    professional = relationship('DbProfessionals', back_populates='user')
    company = relationship('DbCompanies', back_populates='user')

class DbProfessionals(Base):
    __tablename__: str = 'professionals'
    id = Column(String, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    user = relationship('DbUsers', back_populates='professional')
    professional_info = relationship('DbProfessionalInfo', back_populates='professional')
    jobs_matches = relationship("DbAds", secondary=jobs_matches, backref="professionals")

class DbCompanies(Base):
    __tablename__: str = 'companies'
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    user = relationship('DbUsers', back_populates='company')
    company_info = relationship('DbCompanyInfo', back_populates='company')
    jobs_matches = relationship("DbAds", secondary=jobs_matches, backref="companies")

class DbProfessionalInfo(Base):
    __tablename__: str = 'professional_info'
    id = Column(String, primary_key=True, index=True)
    status = Column(String)
    professional = relationship('DbProfessionals', back_populates='professional_info')
    info = relationship('DbInfo', back_populates='professional_info')

class DbCompanyInfo(Base):
    __tablename__: str = 'company_info'
    id = Column(String, primary_key=True, index=True)
    contacts = Column(String)
    company = relationship('DbCompanies', back_populates='company_info')
    info = relationship('DbInfo', back_populates='company_info')

class DbInfo(Base):
    __tablename__: str = 'info'
    id = Column(String, primary_key=True, index=True)
    description = Column(String)
    location = Column(String)
    picture = Column(String)
    company_info = relationship('DbCompanyInfo', back_populates='info')
    professional_info = relationship('DbProfessionalInfo', back_populates='info')
    ads = relationship('DbAds', back_populates='info')

class DbAds(Base):
    __tablename__: str = 'ads'
    id = Column(String, primary_key=True, index=True)
    description = Column(String)
    location = Column(String)
    status = Column(String)
    salary_range = relationship('DbSalaryRange', back_populates='ads')
    info = relationship('DbInfo', back_populates='ads')
    requirements = relationship("DbRequirements", secondary=requirements_has_ads, backref="ads")
    jobs_matches = relationship("DbProfessionalInfo", secondary=jobs_matches, backref="ads")

class DbRequirements(Base):
    __tablename__ = 'requirements'
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    ads = relationship("DbAds", secondary=requirements_has_ads, backref="requirements")

class DbSalaryRange(Base):
    __tablename__: str = 'salary_range'
    id = Column(String, primary_key=True, index=True)
    min = Column(String)
    max = Column(String)
    ads = relationship('DbAds', back_populates='salary_range')







