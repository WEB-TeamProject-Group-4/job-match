from typing import List

from pydantic import BaseModel


class Ad(BaseModel):
    description: str
    location: str
    status: str
    min_salary: int
    max_salary: int


class AdCreate(Ad):
    info_id: str


class AdSkills(BaseModel):
    name: str


class AdDisplay(Ad):
    skills: List[AdSkills]


class SkillToAd(BaseModel):
    ad_id: str
    skill_id: str


class IncludeSkillToAddDisplay(BaseModel):
    skill_name: str
    level: str
