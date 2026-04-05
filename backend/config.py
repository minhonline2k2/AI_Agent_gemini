"""
config.py - Doc cau hinh tu file .env
Moi gia tri nhay cam (mat khau, API key) deu lay tu .env
KHONG BAO GIO hardcode secret trong code
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "AI Incident Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"

    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://aiops:aiops_password@postgres:5432/ai_incident_db"
    DATABASE_URL_SYNC: str = "postgresql://aiops:aiops_password@postgres:5432/ai_incident_db"

    # --- Redis ---
    REDIS_URL: str = "redis://redis:6379/0"

    # --- Auth ---
    JWT_SECRET: str = "jwt-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480

    # --- Gemini AI ---
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"
    GEMINI_MAX_CONCURRENT: int = 10
    GEMINI_TIMEOUT: int = 60

    # --- Agent ---
    AGENT_SECRET: str = "agent-secret-change-me"

    # --- Ingestion ---
    INGEST_TOKEN: str = "ingest-token-change-me"
    INGEST_RATE_LIMIT: int = 100

    # --- Public URL ---
    PUBLIC_URL: str = "https://app.example.com"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Tao instance duy nhat, dung trong toan bo app
settings = Settings()
