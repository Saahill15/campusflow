import secrets
from pathlib import Path
from urllib.parse import urlparse

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR / 'migration_test.db'}"


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    values: list[str] = []
    for item in value.split(','):
        cleaned = item.strip()
        if not cleaned:
            continue
        values.append(cleaned)
    return values


def _normalize_trusted_host(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme and parsed.netloc:
        return parsed.netloc
    return value


def _normalize_origin(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return value


def _normalize_database_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme in {'postgresql', 'postgres'}:
        return value.replace(f'{parsed.scheme}://', 'postgresql+asyncpg://', 1)
    return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    APP_NAME: str = "Pragyarambh 2026"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = DEFAULT_DATABASE_URL
    SECRET_KEY: str | None = None
    MAIL_HOST: str | None = None
    MAIL_PORT: int = 587
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_FROM: str | None = None
    MAIL_FROM_NAME: str | None = None
    MAIL_USE_TLS: bool = True
    CORS_ALLOWED_ORIGINS: str | None = None
    TRUSTED_HOSTS: str | None = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    REGISTRATION_DIAGNOSTIC_TOKEN: str | None = None
    RENDER_GIT_COMMIT: str | None = None

    @property
    def cors_allowed_origins(self) -> list[str]:
        origins = _split_csv(self.CORS_ALLOWED_ORIGINS)
        normalized = [_normalize_origin(value) for value in origins]
        if self.ENVIRONMENT == "development":
            defaults = [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ]
            return list(dict.fromkeys(defaults + normalized))
        return normalized

    @property
    def cors_allow_credentials(self) -> bool:
        return bool(self.cors_allowed_origins)

    @property
    def trusted_hosts(self) -> list[str]:
        hosts = _split_csv(self.TRUSTED_HOSTS)
        normalized = [_normalize_trusted_host(value) for value in hosts]
        if self.ENVIRONMENT == "development":
            defaults = ["localhost", "127.0.0.1", "[::1]"]
            return list(dict.fromkeys(defaults + normalized))
        return normalized

    @model_validator(mode="after")
    def validate_production_settings(self):
        normalized_db_url = _normalize_database_url(self.DATABASE_URL)
        if normalized_db_url != self.DATABASE_URL:
            object.__setattr__(self, "DATABASE_URL", normalized_db_url)

        if self.ENVIRONMENT != "development":
            if self.SECRET_KEY is None or self.SECRET_KEY.strip() == "":
                raise ValueError("SECRET_KEY must be set in production.")
            if self.DATABASE_URL == DEFAULT_DATABASE_URL:
                raise ValueError("DATABASE_URL must be set to a production database in production.")
            if not self.TRUSTED_HOSTS:
                raise ValueError("TRUSTED_HOSTS must be set in production.")
        else:
            if self.SECRET_KEY is None:
                object.__setattr__(self, "SECRET_KEY", secrets.token_urlsafe(32))
        return self


settings = Settings()
