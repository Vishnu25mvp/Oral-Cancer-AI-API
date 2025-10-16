from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
from lib.config.settings import settings
from lib.models.sql import *  # Import all SQL models

# =========================
# SQL (Async MySQL) CONFIG
# =========================
async_engine = create_async_engine(
    settings.SQL_DATABASE_URL, echo=settings.DEBUG
)

async_session = sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)

async def init_sql_db():
    """Initialize SQLModel tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("✅ SQL database initialized successfully")

async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session


# =========================
# MONGO DATABASE CONFIG
# =========================
mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
mongo_db = mongo_client[settings.MONGO_DB_NAME]

def get_collection(name: str):
    return mongo_db[name]

async def init_mongo_db():
    """Test Mongo connection"""
    try:
        await mongo_db.command("ping")
        print(f"✅ MongoDB connected to: {settings.MONGO_DB_NAME}")
    except Exception as e:
        print("❌ MongoDB connection failed:", str(e))


# =========================
# COMBINED INITIALIZER
# =========================
async def init_databases():
    await init_sql_db()
    await init_mongo_db()
