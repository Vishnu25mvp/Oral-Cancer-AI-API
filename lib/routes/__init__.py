from fastapi import FastAPI, APIRouter, Depends
from lib.config.database import get_async_session, get_collection
from lib.models.sql import User
from lib.models.nosql import MongoUser
from sqlmodel import select

# Create a router instance
router = APIRouter(prefix="/smtp", tags=["SMTP"])

# Example route
@router.get("/")
async def get_smtp_info():
    return {"message": "SMTP info route"}

@router.get("/test/sql")
async def test_sql(session=Depends(get_async_session)):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return {"sql_users": [u.dict() for u in users]}

@router.get("/test/mongo")
async def test_mongo():
    users_col = get_collection("users")
    users = await users_col.find().to_list(10)
    print("Here is the User Data", users)
    return {"mongo_users": users}

# Function to register routes to the main app
def register_routes(app: FastAPI):
    app.include_router(router, prefix="/api/v1")


__all__ = ["register_routes"]
