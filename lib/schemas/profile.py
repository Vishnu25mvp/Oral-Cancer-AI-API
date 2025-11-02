from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ProfileBase(BaseModel):
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    bio: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileRead(ProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True  # ✅ For ORM mode (Pydantic v2)
