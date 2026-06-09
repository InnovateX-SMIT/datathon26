import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Crime Intelligence Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(default="supersecretjwtkeyforcrimeplatform2026!", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    DATABASE_URL: str = Field(default="sqlite:///./crime_intel.db", env="DATABASE_URL")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
