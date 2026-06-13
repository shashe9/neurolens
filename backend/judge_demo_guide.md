# Neurolens Judge Demo Guide & Walkthrough

Welcome to the Neurolens Judge Demo Guide! This document provides all the necessary instructions, login credentials, and walkthrough steps to demonstrate the **Phase 6A: Authentication and Judge Readiness** features of Neurolens.

---

## 🔑 Demo Account Credentials

Use the following credentials to access the pre-seeded Judge Profile:

| Field | Value |
| :--- | :--- |
| **Email Address** | `judge@neurolens.demo` |
| **Password** | `secure_judge_2026` |

---

## ⚙️ Setup & Startup Commands

To start both the FastAPI backend and Next.js frontend locally:

### 1. Start the Backend API
Navigate to the `backend/` directory, activate the virtual environment, run migrations, seed the database, and start the development server:

```powershell
# Navigate to backend
cd backend

# Activate Virtual Environment (Windows)
.venv\Scripts\activate

# Apply migrations to local SQLite database
alembic upgrade head

# Run seed script to seed database including the judge profile
.venv\Scripts\python app/database/seed.py

# Launch the FastAPI dev server
.venv\Scripts\python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Start the Frontend Application
In a separate terminal window, navigate to the `frontend/` directory, install dependencies, and start the Next.js app:

```powershell
# Navigate to frontend
cd frontend

# Install dependencies (if not already installed)
npm install

# Start Next.js development server
npm run dev
```
The application will be accessible at: [http://localhost:3000](http://localhost:3000).

---

## 🚶‍♂️ Showcase Walkthrough Scenarios

Follow this step-by-step walkthrough to experience the full flow of the platform:

### Step 1: Secure Authentication & Redirection
1. Open [http://localhost:3000](http://localhost:3000).
2. You will be automatically redirected to the `/login` page because Neurolens now enforces authentication boundaries on all pages.
3. Observe the premium dark-themed, glassmorphic login card. Enter the demo credentials:
   - **Email**: `judge@neurolens.demo`
   - **Password**: `secure_judge_2026`
4. Click **Log In**. Upon verification, you will be redirect to the dashboard.

### Step 2: Children Profile Selection
1. On the landing page or header dropdown, select **Demo Child A** (e.g. 24 Months).
2. Click on the header profile dropdown (top-right). Note that you can see and switch between **Demo Child A** and **Demo Child B** dynamically, which are isolated strictly to your judge parent profile.

### Step 3: Log a Multilingual Observation
1. Navigate to **Log Observation** using the navbar or dashboard action button.
2. Log a new general parent observation for **Demo Child A** using Hinglish vocabulary:
   - **Observer Relation**: `Mother`
   - **Entry Type**: `general`
   - **Developmental Domain**: `Communication`
   - **Observation Details**: `Mera beta ab simple words bolta hai, and he dekhta hai jab hum uska naam call karte hain.`
3. Click **Add to Report Evidence**. The observation is immediately saved and visible in the **Evidence Logs** feed.

### Step 4: Compare & Track Milestones
1. Navigate to **Review Milestones** in the navbar.
2. Select the **Communication** domain tab and locate the **"Points to show"** milestone (or any other milestone).
3. Change its status dropdown to **🏆 Consistently Demonstrated**.
4. Scroll down to look at **Show Supporting Evidence**. You can link your logged observations inline as proof of the milestone's completion, illustrating clinical audit trails.

### Step 5: Schedule Visit Priorities
1. Navigate to **Prepare Visit** in the navbar.
2. Configure a upcoming clinic visit:
   - **Visit Date**: Set a future date.
   - **Clinician Name**: `Dr. Sarah Marcus`
   - **Visit Priority**: `Consultation / Assessment`
   - **Concern Level**: `Medium Concern`
   - **Primary Concern Note**: `Discussing responsiveness to name calls and verbal cues observed during home play.`
3. Click **Save Visit Context**.

### Step 6: Generate Immutable Clinician Report
1. Navigate to **Generate Report** in the navbar.
2. In the visit context dropdown, select `Dr. Sarah Marcus`.
3. Click **Compile Report Snapshot**.
4. Inspect the generated report:
   - Note the **Evidence Coverage Summary** ratios showing how many milestones have supporting parent observations.
   - View the detailed logs under **Traceable Observation Evidence Segments** displaying full timestamps and reporter relations.
   - Toggle **Developer Mode** on the top-right to inspect the raw structured JSON snapshot stored in the database.
5. Click **Print / Save PDF** to generate an audit-ready hardcopy document.

### Step 7: Logout Action
1. Click the header profile dropdown (top-right).
2. Click **🚪 Logout**. You will be securely logged out, token storage cleared, and redirected back to the login screen.

### Step 8: AI Suggestion & Explainability Alignment
1. Navigate to **Log Observation** using the navbar.
2. In the **Observation Details** text area, input a Hinglish-rich developmental observation:
   - *Text*: `He ishaara karta hai jab use gudiya chahiye.`
3. Click the **✨ Analyze with OIE AI** button.
4. Note that OIE retrieves milestone suggestions. Click **Why was this suggested?** to expand the explainability accordion.
5. Verify that:
   - The domain classification is correct.
   - The age suitability match displays.
   - The translator glossary correctly identifies Hinglish caregiver terminology (`ishaara` translated to `pointing` and `gudiya` translated to `doll`).
6. Click **🔗 Link to Log** on the suggestion card. Observe that the form's entry type, domain, and linked milestone dropdown are automatically populated with the suggested values.
7. Click the **👍 Helpful** or **👎 Not Helpful** buttons to record feedback. (If rating Not Helpful, input an optional comment and submit).

### Step 9: Dedicated Judge Metrics & Human Validation Portal
1. Navigate to **⚖️ Judge Portal** in the navbar.
2. View the **OIE Multilingual Model Benchmarks** card displaying the empirical accuracies (Top-1: 80.62%, Top-3: 96.25%, Domain: 86.88%).
3. View the aggregated caregiver feedback metrics and OIE suggestion confirmation percentages.
4. Simulate a new validation study participant log on the **Log Study Participant Session** form:
   - **Participant ID**: `JUDGE-VAL-2026`
   - **Role**: `Judge`
   - **Usability, Trust, and Usefulness Ratings**: Set to `5`
   - **Comments**: `Multilingual explainability is clear, data and disclaimers are compliant.`
5. Click **Log validation run**. Verify that the session is added to the historical sessions list on the right and updates the average study ratings dynamically.

### Step 10: Responsible AI Safety Audit
1. Audit and verify that the clinical disclaimers are clearly visible at:
   - **Login Page**: Footer notice below the demo guide hint.
   - **Dashboard**: Card container footer.
   - **Observations Suggestions**: Notice visible below suggestions.
   - ** clinician Report page**: Visible in a light-yellow disclaimer box at the top of the report preview (and renders in print and PDF views).

