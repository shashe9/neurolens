# Neurolens: Team Clone & Setup Guide

This guide describes how to clone, install, and execute the Neurolens codebase locally for development, review, or demo purposes.

---

## 📥 1. Cloning the Repository

```bash
git clone https://github.com/shashe9/neurolens.git
cd neurolens
```

---

## 🐍 2. Backend Installation & Startup

The backend is a FastAPI application. Ensure you have **Python 3.13** installed locally.

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate    # Unix/macOS

# Install dependencies
pip install -r requirements.txt

# Set SQLite database URL environment variable (required on host)
$env:DATABASE_URL="sqlite:///neurolens.db"   # Windows PowerShell
export DATABASE_URL="sqlite:///neurolens.db" # Unix/macOS

# Apply database migrations
alembic upgrade head

# Seed demo accounts & data
python -m app.database.seed

# Start the development server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

*   **API Healthcheck**: Access [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) to confirm the database connects successfully.

---

## 🎨 3. Frontend Installation & Startup

The frontend is a Next.js application. Ensure you have **Node.js 20+** installed locally.

```bash
cd ../frontend

# Install node dependencies
npm install

# Start the development server
npm run dev
```

*   **Access the App**: Open [http://localhost:3000](http://localhost:3000) in your web browser.

---

## 🔑 4. Demo Login Credentials

All demonstration accounts share the same password: **`secure_judge_2026`**

1.  **Typical Childhood Track**: `judge_typical@neurolens.demo`
2.  **Childhood Concerns Track**: `judge_concern@neurolens.demo`
3.  **Mixed Milestones Track**: `judge_mixed@neurolens.demo`

---

## 🩺 5. Setup Verification Checklist

After installation, verify the environment behaves correctly by completing the following sequence:

*   [ ] **Login**: Navigate to `/login`, submit credentials for `judge_typical@neurolens.demo`, and verify you redirect to `/dashboard`.
*   [ ] **Dashboard**: Verify the `Typical Child` active profile cards load.
*   [ ] **Timeline Observations**: Navigate to `/observations` and verify the preseeded timeline entries render.
*   [ ] **AI suggestions (OIE)**: Type the Hinglish log *"Baccha khilona lane ke liye bolta hai"* and click **"Analyze Observation with AI"**. Verify matching CDC milestones appear.
*   [ ] **Feedback Loops**: Provide 👍 or 👎 feedback on suggestions and verify the response counts on the judge portal.
*   [ ] **Report Compilation**: Navigate to `/report`, click **"Compile Clinician Report"**, and press `Ctrl + P` to verify the clean print layout.
*   [ ] **Judge Portal**: Navigate to `/judge` and verify OIE accuracy metrics split by Caregiver/Clinician cohorts are loaded.
