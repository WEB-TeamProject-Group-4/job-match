from typing import Optional
from pydantic import BaseModel, Field


class CompanyBase(BaseModel):
    name: str


class CompanyCreate(CompanyBase):
    name: str


class CompanyUpdate(CompanyBase):
    name: str


class CompanyInDBBase(CompanyBase):
    id: Optional[str] = Field(None, title="ID", description="Optional ID")
    name: str

    class Config:
        orm_mode = True