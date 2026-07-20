import os
from pydantic_settings import BaseSettings
from pydantic import Field

# Calculate root database path dynamically so it is not relative to the starting directory
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if os.path.exists(os.path.join(PARENT_DIR, 'crime_intel.db')):
    DEFAULT_DB_URL = f"sqlite:///{os.path.join(PARENT_DIR, 'crime_intel.db')}"
else:
    DEFAULT_DB_URL = f"sqlite:///{os.path.join(APP_DIR, 'crime_intel.db')}"

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Crime Intelligence Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(default="supersecretjwtkeyforcrimeplatform2026!", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    DATABASE_URL: str = Field(default=DEFAULT_DB_URL, env="DATABASE_URL")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    class Config:
        case_sensitive = True
        env_file = ".env"

    def __init__(self, **values):
        super().__init__(**values)
        if self.ENVIRONMENT.lower() == "production" and self.SECRET_KEY == "supersecretjwtkeyforcrimeplatform2026!":
            raise ValueError("SECRET_KEY must be configured as a secure custom value when running in PRODUCTION environment!")

settings = Settings()
