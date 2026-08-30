import os
from pydantic_settings import BaseSettings
from pydantic import Field

# Calculate root database path dynamically so it is relative to the backend root directory
BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = BACKEND_ROOT
DEFAULT_DB_URL = f"sqlite:///{os.path.join(BACKEND_ROOT, 'crime_intel.db')}"

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Crime Intelligence Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(default="supersecretjwtkeyforcrimeplatform2026!", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    DATABASE_URL: str = Field(default=DEFAULT_DB_URL, env="DATABASE_URL")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    # Zoho Catalyst QuickML Credentials
    QUICKML_CRIME_RISK_ENDPOINT: str = ""
    QUICKML_HOTSPOT_ENDPOINT: str = ""
    QUICKML_OFFENDER_ENDPOINT: str = ""
    QUICKML_API_KEY: str = ""
    QUICKML_HOTSPOT_API_KEY: str = ""
    QUICKML_OFFENDER_API_KEY: str = ""
    QUICKML_CATALYST_ORG: str = ""
    QUICKML_ENVIRONMENT: str = "Development"

    # Zoho OAuth Credentials
    ZOHO_CLIENT_ID: str = ""
    ZOHO_CLIENT_SECRET: str = ""
    ZOHO_GRANT_TOKEN: str = ""
    ZOHO_ACCESS_TOKEN: str = ""
    ZOHO_REFRESH_TOKEN: str = ""

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

    def __init__(self, **values):
        super().__init__(**values)

settings = Settings()
