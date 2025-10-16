from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from bson import ObjectId


class PyObjectId(ObjectId):
    """Helper for BSON ObjectId conversion"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        # Pydantic v2 replacement for __modify_schema__. Return a simple
        # JSON schema that represents ObjectId as a string.
        return {"type": "string"}


class MongoUser(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    email: EmailStr
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Pydantic v2: use `model_config` for configuration
    model_config = {
        "json_encoders": {ObjectId: str},
        "arbitrary_types_allowed": True,
    }
