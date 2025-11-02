from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    admin = "admin"
    counselor = "counselor"
    user = "user"


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Optional[UserRole] = UserRole.user


class UserCreate(UserBase):
    password: Optional[str] = None  # ✅ Optional password for counselor/admin


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # ✅ Pydantic v2 compatible


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None
