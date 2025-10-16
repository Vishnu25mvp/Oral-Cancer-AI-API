from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
