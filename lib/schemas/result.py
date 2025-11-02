# lib/schemas/result_schema.py
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr

class ResultBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

class ResultCreate(ResultBase):
    pass

class ResultRead(BaseModel):
    id: int
    user_id: int
    created_by: int
    age: int
    gender: str
    result: str | None = None
    confidence: float | None = None
    images: List[str] = []
    date: datetime

    class Config:
        from_attributes = True


class PaginatedResultResponse(BaseModel):
    page: int
    limit: int
    total: int
    pages: int
    count: int
    data: List[ResultRead]