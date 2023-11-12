from typing import Optional
from pydantic import BaseModel, Field


class ProfessionalBase(BaseModel):
    first_name: str
    last_name = str


class ProfessionalCreate(ProfessionalBase):
    first_name: str
    last_name = str


class ProfessionalUpdate(ProfessionalBase):
    first_name: str
    last_name = str


class ProfessionalInDBBase(ProfessionalBase):
    id: Optional[str] = Field(None, title="ID", description="Optional ID")
    first_name: str
    last_name = str

    class Config:
        orm_mode = True