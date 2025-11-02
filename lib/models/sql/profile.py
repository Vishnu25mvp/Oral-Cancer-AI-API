from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

# from server.lib.models.sql.user import User


class Profile(SQLModel, table=True):
    __tablename__ = "profiles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    phone: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    date_of_birth: Optional[datetime] = Field(default=None)
    bio: Optional[str] = Field(default=None)

    # Relationship back to User
    user: Optional["User"] = Relationship(back_populates="profile")
