# Neurolens

Neurolens is a developmental observation and clinician preparation platform designed to help parents record day-to-day observations, review milestones, and prepare structured context for clinician visits. 

**This is a developmental monitoring context aggregator, not an autism screening, prediction, or diagnostic tool.**

---

## Project Structure

```text
neurolens/
├── frontend/             # Next.js 15 (TypeScript, Tailwind v4, App Router)
├── backend/              # FastAPI (SQLAlchemy 2.0, Alembic, Pydantic v2)
├── docs/                 # Documentation (Responsible AI guidelines)
├── docker-compose.yml    # Multicontainer setup orchestrating frontend, backend, postgres
├── .env.example          # Environment variables template
└── README.md             # This setup and guidance file
```

---

## Local Development Setup

To run Neurolens V1 locally on your host environment, follow these steps:

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (optional, defaults to SQLite for quick local host running)

---

### 1. Environment Configuration
Copy the template `.env.example` into a new `.env` file at the root:
```bash
cp .env.example .env
```
By default, the `.env` uses `localhost` and a fallback SQLite connection string (`sqlite:///./neurolens.db`) to enable zero-configuration startup on your machine without requiring a running database server.

---

### 2. Backend Setup & Run

Navigate to the `backend` folder, set up a Python virtual environment, install requirements, and run the FastAPI server:

```bash
cd backend
python -m venv .venv

# Activate virtual environment
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Database Migrations (Alembic)
Apply database migrations to construct tables:
```bash
alembic upgrade head
```

#### Seed Database
Run the seed script to pre-populate developmental domains, milestone targets, and evolutionary evidence sources:
```bash
python -m app.database.seed
```

#### Launch API Server
Start the Uvicorn server:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive Swagger docs will be available at: [http://localhost:8000/docs](http://localhost:8000/docs)
- API Health Check endpoint: [http://localhost:8000/health](http://localhost:8000/health)

---

### 3. Frontend Setup & Run

Navigate to the `frontend` folder, install Node packages, and run the Next.js development server:

```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser to view the client application.

---

### 4. Running Tests
To execute backend test suites validating endpoints and report generation snapshots:
```bash
cd backend
.venv\Scripts\python -m pytest
```

---

## Docker Quickstart

To run the complete Neurolens stack inside Docker container environments, execute:

```bash
docker compose up --build
```
This command starts:
- PostgreSQL database on port `5432`
- FastAPI backend API on port `8000`
- Next.js frontend on port `3000`
