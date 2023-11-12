from typing import Optional
from pydantic import BaseModel, Field


class SalaryRangeBase(BaseModel):
    min: str
    max = str


class SalaryRangeCreate(SalaryRangeBase):
    min: str
    max = str


class SalaryRangeUpdate(SalaryRangeBase):
    min: str
    max = str


class SalaryRangeInDBBase(SalaryRangeBase):
    id: Optional[str] = Field(None, title="ID", description="Optional ID")
    min: str
    max = str

    class Config:
        orm_mode = True