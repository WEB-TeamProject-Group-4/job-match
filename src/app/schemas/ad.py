from typing import List

from pydantic import BaseModel


class AdCreate(BaseModel):
    description: str
    location: str
    status: str
    min_salary: int
    max_salary: int
    skills: List[str]


class AdCreateDisplay(BaseModel):
    description: str
    location: str
    status: str
    min_salary: int
    max_salary: int


class SkillCreate(BaseModel):
    name: str


class SkillCreateDisplay(BaseModel):
    name: str
