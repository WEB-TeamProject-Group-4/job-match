import uuid

from sqlalchemy import Table, Column, String, Integer, ForeignKey, Boolean, BINARY, LargeBinary
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship

from app.db.database import Base

adds_skills = Table(
    'adds_skills', Base.metadata,
    Column('ad_id', String(50), ForeignKey('ads.id'), primary_key=True),
    Column('skill_id', String(50), ForeignKey('skills.id'), primary_key=True),
    Column('level', String(45), nullable=True, default=None)
)


class DbJobsMatches(Base):
    __tablename__: str = 'jobs_matches'
    ad_id = Column(String(50), ForeignKey('ads.id'), primary_key=True, nullable=False)
    resume_id = Column(String(50), nullable=False)
    professional_id = Column(String(50), ForeignKey('professionals.id'), primary_key=True, nullable=False)
    company_id = Column(String(50), ForeignKey('companies.id'), primary_key=True, nullable=False)
    company_approved = Column(Boolean, default=False)
    professional_approved = Column(Boolean, default=False)
    professional = relationship('DbProfessionals', back_populates='match')
    company = relationship('DbCompanies', back_populates='match')
    ad = relationship('DbAds', back_populates='match')
    is_deleted = Column(Boolean, default=False)


class DbUsers(Base):
    __tablename__: str = 'users'
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    username = Column(String(45), nullable=False, unique=True)
    password = Column(String(150), nullable=False)
    email = Column(String(45), nullable=False, unique=True)
    type = Column(String(45), nullable=False)
    is_verified = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    professional = relationship('DbProfessionals', back_populates='user', cascade='all, delete-orphan')
    company = relationship('DbCompanies', back_populates='user', cascade='all, delete-orphan')


class DbProfessionals(Base):
    __tablename__: str = 'professionals'
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    status = Column(String(45), nullable=True, default=None)
    user_id = Column(String(50), ForeignKey('users.id'), nullable=False)
    is_deleted = Column(Boolean, default=False)
    user = relationship('DbUsers', back_populates='professional', cascade='all, delete-orphan', single_parent=True)
    info_id = Column(String(50), ForeignKey('info.id'), nullable=True, default=None)
    info = relationship('DbInfo', back_populates='professional', cascade='all, delete-orphan', single_parent=True)
    match = relationship('DbJobsMatches', back_populates='professional')

    def mark_as_deleted(self, db: Session):
        if self.user:
            self.user.is_deleted = True
        if self.info:
            self.info.is_deleted = True
        for match in self.match:
            match.is_deleted = True
        self.is_deleted = True

        db.commit()


class DbCompanies(Base):
    __tablename__: str = 'companies'
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    name = Column(String(45), nullable=False, unique=True)
    contacts = Column(String(45), nullable=True, default=None)
    user_id = Column(String(50), ForeignKey('users.id'), nullable=False)
    is_deleted = Column(Boolean, default=False)
    user = relationship('DbUsers', back_populates='company', cascade='all, delete-orphan', single_parent=True)
    info_id = Column(String(50), ForeignKey('info.id'), nullable=True, default=None)
    info = relationship('DbInfo', back_populates='company', cascade='all, delete-orphan', single_parent=True)
    match = relationship("DbJobsMatches", back_populates='company')

    def mark_as_deleted(self, db: Session):
        if self.user:
            self.user.is_deleted = True
        if self.info:
            self.info.is_deleted = True
        for match in self.match:
            match.is_deleted = True
        self.is_deleted = True

        db.commit()


class DbInfo(Base):
    __tablename__: str = 'info'
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    description = Column(String(45), nullable=True)
    location = Column(String(45), nullable=True)
    picture = Column(LargeBinary, nullable=True, default=None)
    main_ad = Column(String(50), nullable=True, default=None)
    is_deleted = Column(Boolean, default=False)
    company = relationship('DbCompanies', back_populates='info', cascade='all, delete-orphan')
    professional = relationship('DbProfessionals', back_populates='info')
    ad = relationship('DbAds', back_populates='info', cascade='all, delete-orphan')


class DbAds(Base):
    __tablename__: str = 'ads'
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    description = Column(String(100), nullable=False)
    location = Column(String(45), nullable=False)
    status = Column(String(45), nullable=False)
    min_salary = Column(Integer, nullable=False)
    max_salary = Column(Integer, nullable=False)
    is_resume = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    info_id = Column(String(50), ForeignKey('info.id'), nullable=False)
    info = relationship('DbInfo', back_populates='ad')
    skills = relationship("DbSkills", secondary=adds_skills, back_populates="ads")
    match = relationship('DbJobsMatches', back_populates='ad', cascade='all, delete-orphan')


class DbSkills(Base):
    __tablename__: str = 'skills'
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    name = Column(String(45), nullable=False)
    is_deleted = Column(Boolean, default=False)
    ads = relationship("DbAds", secondary=adds_skills, back_populates="skills")
