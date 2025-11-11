from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/web3_edu_platform"

    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Gemini AI
    gemini_api_key: Optional[str] = None

    # Server
    debug: bool = True
    port: int = 8001

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
