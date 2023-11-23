from enum import Enum
from typing import List

from pydantic import BaseModel


class AdStatus(str, Enum):
    ACTIVE = 'Active'
    ARCHIVED = 'Archived'
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


class Ad(BaseModel):
    description: str
    location: str
    status: AdStatus
    min_salary: int
    max_salary: int


class AdCreate(Ad):
    info_id: str


class AdSkills(BaseModel):
    name: str


class AdDisplay(Ad):
    skills: List[AdSkills]


class IncludeSkillToAddDisplay(BaseModel):
    skill_name: str
    level: SkillLevel
