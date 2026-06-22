# Deployment Runbook: Production Rollout

This document provides step-by-step instructions for deploying Neurolens to production using **Supabase Postgres**, **FastAPI on Render**, and **Next.js on Vercel**.

---

## Phase 1: Database Setup (Supabase)

1. **Create Project**:
   - Go to [Supabase Dashboard](https://supabase.com).
   - Create a new project.
   - Choose your region and set a strong database password.
2. **Retrieve Connection Strings**:
   - Navigate to **Project Settings** -> **Database**.
   - **Transaction Pooler Connection String** (under URI, select Mode: Transaction, usually port `6543`):
     - Format: `postgresql://postgres.xxx:6543/postgres?pgbouncer=true`
     - Use this connection string for **DATABASE_URL** (for runtime FastAPI).
   - **Direct Connection String** (under URI, select Mode: Session, or directly copy the host URI with port `5432`):
     - Format: `postgresql://postgres.xxx:5432/postgres`
     - Use this connection string for **DIRECT_URL** (for Alembic migrations).
3. **No Auth Setup Needed**:
   - Neurolens uses a custom JWT auth schema. You do **not** need to enable or configure Supabase Auth.

---

## Phase 2: Backend Deployment (Render)

1. **Create Web Service**:
   - Connect your GitHub repository to [Render](https://render.com).
   - Create a new **Web Service** pointing to the repository.
   - Set the root directory to `backend`.
2. **Build & Start Commands**:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. **Configure Environment Variables**:
   Add the following variables under the **Environment** tab:
   - `ENVIRONMENT`: `production`
   - `DATABASE_URL`: `[YOUR-SUPABASE-POOLED-CONNECTION-URI-PORT-6543]`
   - `DIRECT_URL`: `[YOUR-SUPABASE-DIRECT-CONNECTION-URI-PORT-5432]`
   - `JWT_SECRET_KEY`: `[GENERATE-A-SECURE-JWT-SECRET]`
   - `JWT_ALGORITHM`: `HS256`
   - `BACKEND_CORS_ORIGINS`: `["https://[YOUR-APP].vercel.app", "http://localhost:3000"]`
   - `FRONTEND_URL`: `https://[YOUR-APP].vercel.app`
   - `SEED_ON_STARTUP`: `false` (set to `true` on first launch only to preseed developmental milestones, then disable it)
4. **Run Migrations on Deploy**:
   To automatically run migrations on every build:
   - In Render, configure a **Pre-Deploy Command** (under Settings):
     `alembic upgrade head`
   - Alternatively, append `alembic upgrade head &&` to your start command.

---

## Phase 3: Frontend Deployment (Vercel)

1. **Import Project**:
   - Log into [Vercel](https://vercel.com).
   - Click **Add New** -> **Project** and select your GitHub repo.
2. **Framework & Directory Settings**:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
3. **Configure Environment Variables**:
   - Add `NEXT_PUBLIC_API_BASE_URL` with the URL of your Render backend service (e.g. `https://neurolens-backend.onrender.com`).
4. **Deploy**:
   - Click **Deploy**. Vercel will automatically build the production Next.js application.

---

## Verification & Post-Deployment Checklist

- [ ] **Database Connection**: Check Render backend logs to verify it connects to Supabase and runs Alembic migrations without errors.
- [ ] **Milestone Seeding**: Set `SEED_ON_STARTUP=true` in Render env, restart the service, and verify the backend prints `"Database seeding completed successfully!"` in the logs. Then revert `SEED_ON_STARTUP=false`.
- [ ] **User Signup/Login**: Attempt logging in with the preseeded parent credentials (`demo.parent@example.com` / `Password123`) or register a new parent account.
- [ ] **CORS Verification**: Open the browser Console on your Vercel deployment. Ensure there are no CORS preflight blockages when accessing the backend API routes.
