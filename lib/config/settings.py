from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv


ENV = os.getenv("ENVIRONMENT", "development")

if ENV == "production":
    load_dotenv(".env.production")
else:
    load_dotenv(".env.development")



class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # default 1 hour

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True


    SQL_DATABASE_URL: str
    MONGO_URI: str
    MONGO_DB_NAME: str

    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_USE_TLS: bool = True
    SMTP_FROM_EMAIL: str
    SMTP_FROM_NAME: str = "Support Team"

    class Config:
        env_file = None  



settings = Settings()
