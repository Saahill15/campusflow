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
