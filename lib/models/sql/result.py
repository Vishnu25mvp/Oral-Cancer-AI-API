# lib/models/sql/result.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Column

class Result(SQLModel, table=True):
    __tablename__ = "results"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)  # patient or user
    created_by: int = Field(foreign_key="users.id", nullable=False)  # who created this record
    age: Optional[int] = Field(default=None)
    gender: Optional[str] = Field(default=None)
    result: Optional[str] = Field(default=None)
    confidence: Optional[float] = Field(default=None)
    date: datetime = Field(default_factory=datetime.utcnow)
    images: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))

    # Relationships
    user: Optional["User"] = Relationship(sa_relationship_kwargs={"foreign_keys": "[Result.user_id]"})
    creator: Optional["User"] = Relationship(sa_relationship_kwargs={"foreign_keys": "[Result.created_by]"})
