from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    counselor = "counselor"
    user = "user"


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", "role", name="uq_email_role"),  # ✅ composite unique constraint
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    email: str = Field(index=True, nullable=False)
    password: str = Field(nullable=False)
    role: UserRole = Field(default=UserRole.user, nullable=False)
    otp_code: Optional[str] = Field(default=None, nullable=True)
    otp_verified: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    profile: Optional["Profile"] = Relationship(back_populates="user")
