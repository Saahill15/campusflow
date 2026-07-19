# Frontend

This folder contains the React-based frontend for Pragyarambh '26.

## Purpose

- Separate UI concerns from backend logic
- Support modular feature folders for future pages and flows
- Keep build and runtime config centralized for Vercel deployment

## Key folders

- `src/` — application source files
- `src/modules/` — module-specific folders for future feature implementation
- `src/lib/` — reusable client utilities, API helpers, and router setup
- `src/routes/` — route registration and route utilities
- `public/` — static assets and build-time metadata

## Config files

- `package.json` — frontend package manifest
- `tsconfig.json` — TypeScript compiler config
- `vite.config.ts` — Vite build and dev server config
- `tailwind.config.js` — Tailwind CSS config
- `postcss.config.js` — PostCSS config
- `vercel.json` — optional deployment settings for Vercel
- `.env.example` — example environment variables
