import secrets
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = Field("CampusFlow", env="APP_NAME")
    APP_VERSION: str = Field("0.0.0", env="APP_VERSION")
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    DATABASE_URL: str = Field("sqlite+aiosqlite:///:memory:", env="DATABASE_URL")
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")

    class Config:
        env_file = ".env"


settings = Settings()
