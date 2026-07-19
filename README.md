# CampusFlow

CampusFlow is a reusable event management platform built for colleges and campus communities. This repository is prepared for development with a clean monorepo foundation and authoritative documentation in `docs/`.

## Tech Stack

- Frontend: React, Vite, TypeScript, Tailwind CSS, React Router, TanStack Query, Axios, React Hook Form, Zod, shadcn/ui, Lucide Icons
- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL, Pydantic

## Architecture

The repository follows a monorepo layout with separated frontend and backend concerns. The codebase is organized to support frontend UI development and backend API development independently while sharing a unified product vision.

## Project Structure

- `docs/` — authoritative documentation for requirements, architecture, API design, and database design
- `frontend/` — React application scaffold and build configuration
- `backend/` — FastAPI application scaffold and backend configuration
- `.github/workflows/` — CI workflow placeholders

## Getting Started

This repository is ready for development with the necessary folder structure and configuration files. No feature implementation, UI pages, backend routes, or database models are included yet.

## Development Workflow

1. Review the documentation in `docs/`
2. Implement features following the documented architecture and API design
3. Keep code quality settings consistent across frontend and backend

## Documentation Folder

`docs/` is the single source of truth for CampusFlow product, architecture, API, and database decisions.

## Contributing

Follow the documentation governance rules in `docs/PROJECT_RULES.md`.

## License

This project is licensed under the MIT License.
