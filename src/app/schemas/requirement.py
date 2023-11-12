from typing import Optional
from pydantic import BaseModel, Field


class RequirementBase(BaseModel):
    first_name: str
    last_name = str


class RequirementCreate(RequirementBase):
    first_name: str
    last_name = str


class RequirementUpdate(RequirementBase):
    first_name: str
    last_name = str


class RequirementInDBBase(RequirementBase):
    id: Optional[str] = Field(None, title="ID", description="Optional ID")
    first_name: str
    last_name = str

    class Config:
        orm_mode = True