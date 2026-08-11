# Backend

This folder contains the FastAPI backend for Pragyarambh '26.

## Purpose

- Provide REST APIs for the event platform
- Offer a modular service architecture for future feature expansion
- Keep database migrations and schema management organized

## Key folders

- `app/` — FastAPI application package
- `app/api/` — API route groups and versioning
- `app/core/` — application settings, startup, and dependency wiring
- `app/db/` — database engine, session, and models
- `app/models/` — SQLAlchemy ORM models
- `app/schemas/` — pydantic request/response schemas
- `app/services/` — business services for modular features
- `app/utils/` — reusable utilities and helpers
- `app/modules/` — feature modules (registration, events, analytics, etc.)
- `migrations/` — Alembic migration environment

## Config files

- `pyproject.toml` — backend dependencies and packaging
- `alembic.ini` — Alembic configuration
- `.env.example` — environment variable reference

## Production migration

- Run database migrations in production with:
  `alembic -c alembic.ini upgrade head`

## Email configuration

For confirmation emails, configure these environment variables in local development and production:

- `MAIL_HOST`
- `MAIL_PORT`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_FROM`
- `MAIL_FROM_NAME`
- `MAIL_USE_TLS`

If these are not set, the backend falls back to console logging for email delivery in development and tests.
