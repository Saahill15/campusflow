from pathlib import Path
from pydantic import BaseSettings, PostgresDsn

class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    SECRET_KEY: str
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = Path(__file__).resolve().parents[1] / '.env'
        env_file_encoding = 'utf-8'

settings = Settings()
