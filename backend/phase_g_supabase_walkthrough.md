# Phase G: Supabase Migration & Hardening Walkthrough

This document guides you through the changes introduced in Phase G to stabilize Neurolens for production deployment using **Supabase Postgres** as the primary persistent database.

## 1. Key Database Architecture Decisions

- **Primary DB**: Supabase Postgres (production).
- **Local Fallback**: SQLite (`sqlite:///neurolens.db`) is preserved as an optional local/offline fallback for ease of development.
- **FastAPI Custom JWT Auth**: Preserved. User/parent records and session tokens reside in the Postgres database rather than utilizing Supabase Auth.
- **Backend as Brain**: Next.js frontend interacts exclusively with the FastAPI backend, which handles all communication with Supabase.
- **Separated DB Connections**:
  - `DATABASE_URL`: Runtime connection URL for FastAPI / SQLAlchemy (uses pgBouncer pooler port `6543`).
  - `DIRECT_URL`: Direct/session connection URL for Alembic schema migrations and seeding (uses direct port `5432`).

## 2. Authoritative Environment Resolution

To prevent conflicts in a monorepo setup, environment resolution is deterministically backend-scoped:
- **`backend/.env`** is the authoritative environment file for all backend tasks (FastAPI runtime, Alembic, database seeding, test runners).
- The repo root `.env` will only be used as a fallback if `backend/.env` is missing, ensuring your database config is not overridden by global monorepo files.
- The property `resolved_backend_env_file` is exposed on `settings` for debugging and verifying the active file path.

### Backend `.env`

Create a `backend/.env` file with:

```env
ENVIRONMENT=production
DATABASE_URL=postgresql://postgres.xxx:6543/postgres?pgbouncer=true
DIRECT_URL=postgresql://postgres.xxx:5432/postgres
JWT_SECRET_KEY=<strong-random-jwt-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
BACKEND_CORS_ORIGINS=["https://neurolens.vercel.app","http://localhost:3000"]
FRONTEND_URL=https://neurolens.vercel.app
SEED_ON_STARTUP=false
```

> [!IMPORTANT]
> - Both `DATABASE_URL` and `DIRECT_URL` automatically normalize `postgres://` prefixes to `postgresql://` on startup.
> - **pgBouncer Port & Query Stripping**: Since psycopg2 does not support `pgbouncer=true` connection options for raw transactions or seeding, `settings.admin_database_url` automatically filters out `?pgbouncer=true` (or any other pgbouncer query parameters) to keep direct administration connections clean and functional.
> - Alembic migrations run using `DIRECT_URL` (or fallback to `DATABASE_URL` if not present) via the `alembic_database_url` settings property.
> - If `ENVIRONMENT=production`, the backend enforces that `JWT_SECRET_KEY` is **not** the default development value (`dev_secret_key_for_neurolens_2026`). If it is, startup will fail with a `RuntimeError`.

### Frontend `.env.local`

For Next.js, create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=https://neurolens-backend.onrender.com
```

## 3. Centralized Frontend Base URL

The frontend now resolves API calls centrally via [config.ts](file:///d:/Desktop/New_Autism/frontend/src/config.ts):
- Resolves to `NEXT_PUBLIC_API_BASE_URL` first.
- Falls back to `NEXT_PUBLIC_API_URL`.
- Defaults to `http://localhost:8000` locally.

All pages have been refactored to use this centralized `API_BASE_URL`.

## 4. Verification & Testing

To test the database connectivity check, migrations, and seeds locally:

```powershell
# Check database connectivity with detailed logs (admin/direct DSN, password masked)
.venv\Scripts\python -m app.database.wait_for_db

# Run migrations to target schema
alembic upgrade head

# Run database seed loader (Postgres & SQLite safe)
.venv\Scripts\python -m app.database.seed
```

To execute the test suite (70 tests):
```powershell
.venv\Scripts\python -m pytest
```
