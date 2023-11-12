from typing import Optional
from pydantic import BaseModel, Field


class AdsBase(BaseModel):
    description: str
    location = str
    status = str


class AdsCreate(AdsBase):
    description: str
    location = str
    status = str


class AdsUpdate(AdsBase):
    description: str
    location = str
    status = str


class AdsInDBBase(AdsBase):
    id: Optional[str] = Field(None, title="ID", description="Optional ID")
    description: str
    location: str
    status: str

    class Config:
        orm_mode = True