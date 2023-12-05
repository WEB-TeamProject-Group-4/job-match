from typing import List
from enum import Enum

from pydantic import BaseModel


class AdStatusCreate(str, Enum):
    ACTIVE = 'Active'
    ARCHIVED = 'Archived'
    HIDDEN = 'Hidden'
    PRIVATE = 'Private'
    MATCHED = 'Matched'


class JobAdStatus(str, Enum):
    ACTIVE = 'Active'
    ARCHIVED = 'Archived'


class ResumeStatus(str, Enum):
    ACTIVE = 'Active'
    HIDDEN = 'Hidden'
    PRIVATE = 'Private'
    MATCHED = 'Matched'


class SkillLevel(str, Enum):
    BEGINNER = 'Beginner'
    INTERMEDIATE = 'Intermediate'
    ADVANCED = 'Advanced'
    PROFICIENT = 'Proficient'
    NATIVE = 'Native'
    MASTER = 'Master'


class AdCreate(BaseModel):
    description: str
    location: str
    status: AdStatusCreate
    min_salary: int
    max_salary: int


class AdSkills(BaseModel):
    name: str


class AdDisplay(AdCreate):
    skills: List[AdSkills]


class AddSkillToAdDisplay(BaseModel):
    skill_name: str
    level: SkillLevel
