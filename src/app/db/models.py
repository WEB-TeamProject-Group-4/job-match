from db.database import Base
from sqlalchemy import Table, Column, String, ForeignKey, Boolean, LargeBinary
from sqlalchemy.orm import relationship
import uuid


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
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    username = Column(String)
    password = Column(String)
    type = Column(String)
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
    jobs_matches = relationship("DbAds", secondary=jobs_matches, backref="professionals")

class DbCompanies(Base):
    __tablename__: str = 'companies'
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    name = Column(String)
    user_id = Column(String(50), ForeignKey('users.id'))
    user = relationship('DbUsers', back_populates='company')
    company_info_id = Column(String(50), ForeignKey('company_info.id'))
    company_info = relationship('DbCompanyInfo', back_populates='company')
    jobs_matches = relationship("DbAds", secondary=jobs_matches, backref="companies")

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
    ads = relationship('DbAds', back_populates='info')

class DbAds(Base):
    __tablename__: str = 'ads'
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    description = Column(String)
    location = Column(String)
    status = Column(String)
    salary_range_id = Column(String(50), ForeignKey('salary_range.id'))
    salary_range = relationship('DbSalaryRange', back_populates='ads')
    info = relationship('DbInfo', back_populates='ads')
    requirements = relationship("DbRequirements", secondary=requirements_has_ads, backref="ads_associated")
    jobs_matches = relationship("DbProfessionalInfo", secondary=jobs_matches, backref="ads")

class DbRequirements(Base):
    __tablename__ = 'requirements'
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    name = Column(String)
    ads = relationship("DbAds", secondary=requirements_has_ads, backref="requirements_associated")

class DbSalaryRange(Base):
    __tablename__: str = 'salary_range'
    id = Column(String(50), primary_key=True, default=str(uuid.uuid4()))
    min = Column(String)
    max = Column(String)
    ads = relationship('DbAds', back_populates='salary_range')







