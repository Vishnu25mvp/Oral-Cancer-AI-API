from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# Load the correct .env file based on ENVIRONMENT variable
ENV = os.getenv("ENVIRONMENT", "development")
if ENV == "production":
    load_dotenv(".env.production")
else:
    load_dotenv(".env.development")


class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Server
    HOST: str
    PORT: int
    DEBUG: bool = True

    # Databases
    SQL_DATABASE_URL: str
    MONGO_URI: str
    MONGO_DB_NAME: str

    class Config:
        env_file = None  # Already loaded manually


settings = Settings()
