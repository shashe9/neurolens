# Neurolens Phase 6C: Recommendations & Implementation Plan (Revised)

This document establishes the revised roadmap for Neurolens Phase 6C. It details the implementation specs for the highest-ROI task and sets out the plans for landing page messaging, judge evidence cards, multi-account seeding, role validation stats, and automated deployment.

---

## 🏆 Single Highest-ROI Feature: Report Export Polish (F-01)

The **Report Export Polish** is the highest-ROI feature. Clinician reports are the ultimate artifact of the Neurolens system. Every judge will compile and review a report. Polishing the printable layout and PDF generation adds immediate, undeniable professionalism with minimal coding.

---

## 🛠️ F-01: Technical Implementation Specifications

To achieve a clean, printable medical report layout on A4 paper or PDF saving, add the following rules in `frontend/src/app/globals.css` ([globals.css](file:///d:/Desktop/New_Autism/frontend/src/app/globals.css)):

```css
@media print {
  /* 1. Hide interactive elements, navbars, and buttons */
  header,
  nav,
  button,
  select,
  input,
  label,
  .print\:hidden {
    display: none !important;
  }

  /* 2. Reset dark background colors and force high-contrast print colors */
  body, 
  html {
    background-color: white !important;
    color: #0f172a !important; /* Slate 900 */
    font-size: 12pt !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  /* 3. Strip shadow borders and force the card content to fill the page print layout */
  .bg-white,
  .rounded-2xl,
  .shadow-2xl,
  .border {
    padding: 0 !important;
    border: none !important;
    box-shadow: none !important;
    background-color: transparent !important;
    color: #0f172a !important;
  }

  /* 4. Force background colors to print for critical highlights (e.g. disclaimer and status tags) */
  .bg-amber-50\/70,
  .bg-indigo-50\/50,
  .bg-slate-50,
  .bg-violet-50,
  .bg-emerald-50,
  .bg-amber-50 {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    background-color: #fef3c7 !important; /* Force readable background */
    border: 1px solid #f59e0b !important;
  }

  /* 5. Clean table formatting for print */
  table {
    width: 100% !important;
    border-collapse: collapse !important;
  }
  
  tr {
    page-break-inside: avoid !important;
    break-inside: avoid !important;
  }

  th, td {
    border-bottom: 1px solid #e2e8f0 !important;
    padding: 6pt 8pt !important;
  }

  /* 6. Enforce page breaks for sections */
  .print-section {
    page-break-inside: avoid !important;
    break-inside: avoid !important;
    margin-top: 15pt !important;
  }
}
```

---

## 📋 Technical Plan for Secondary Recommendations

### F-02: Landing Page Impact & Safety Section
Update `frontend/src/app/page.tsx` ([page.tsx](file:///d:/Desktop/New_Autism/frontend/src/app/page.tsx)) to establish Neurolens' purpose:
*   **Hero Badge**: A badge next to the logo stating *"OIE Multilingual Core: 96.25% Top-3 Accuracy"* or *"55/55 Passing Verification Tests"*.
*   **Problem Card**: *"Parents arrive at pediatrician appointments with fragmented memories, undocumented observations, and no structured developmental history."*
*   **Solution Card**: *"Neurolens transforms daily parent observations into structured, evidence-linked developmental summaries for pediatricians."*
*   **Evidence Metrics Grid**: Showcases metrics (80 milestones, 160 benchmark observations, 96.25% accuracy) immediately to the judge.
*   **Safety Notice Footer**: High-visibility disclaimer stating Neurolens is an educational milestone logging tool, not a diagnostic or ASD predictor.

### F-03: Judge Portal Evidence Cards
Add three responsive cards to `frontend/src/app/judge/page.tsx` ([judge/page.tsx](file:///d:/Desktop/New_Autism/frontend/src/app/judge/page.tsx)):
1.  **AI Pipeline Flow**: A visual diagram: `Parent Observation` $\rightarrow$ `Transliteration` $\rightarrow$ `Embedding Match` $\rightarrow$ `Milestone Suggestion` $\rightarrow$ `Human Review` $\rightarrow$ `Report Snapshot`.
2.  **AI Safety Boundaries**: Lists clear constraints: No risk scores, no diagnostic labels, static educational mapping.
3.  **Verification Coverage**: Highlights the testing suite (80 standard milestones, 160 evaluation samples, 55 passing tests).

### F-04: Multi-Account Demo Seeding (Passive & Safe)
Modify `seed_db` in `backend/app/database/seed.py` ([seed.py](file:///d:/Desktop/New_Autism/backend/app/database/seed.py)) to seed three separate accounts:
*   `judge_typical@neurolens.demo` $\rightarrow$ Linked to child with typical developmental logs (smiling, pointing, saying two-word phrases) and fully observed milestones.
*   `judge_concern@neurolens.demo` $\rightarrow$ Linked to child with concern logs (spinning wheels, no eye contact, no response to name) and developmental alerts.
*   `judge_mixed@neurolens.demo` $\rightarrow$ Linked to child with balanced, mixed observations.
All accounts set with password `secure_judge_2026`. This avoids the complex, dangerous resetting of active databases during a live demo.

### F-05: Validation Sample Split & Counts
*   **Pre-seed validation study data** in `seed.py` with 14 caregiver ratings (rating usability/trust) and 5 clinician ratings (rating usefulness) alongside realistic comments.
*   Extend `/validation-study/stats` in `backend/app/api/endpoints/validation.py` to query averages grouped by role:
    ```python
    stats_by_role = db.query(
        HumanValidationSession.role,
        func.count(HumanValidationSession.id),
        func.avg(HumanValidationSession.usability_score),
        func.avg(HumanValidationSession.trust_score),
        func.avg(HumanValidationSession.report_usefulness_score)
    ).group_by(HumanValidationSession.role).all()
    ```
*   Update `/judge` UI to display caregiver averages (Sample Size: 14) separately from clinician averages (Sample Size: 5).

### F-06: Deployment & Startup Automation
*   Write an `entrypoint.sh` startup script for the Docker backend:
    ```bash
    #!/bin/sh
    # 1. Wait for database readiness
    echo "Waiting for postgres..."
    while ! nc -z postgres 5432; do
      sleep 0.5
    done
    echo "PostgreSQL started"

    # 2. Run database migrations
    echo "Running alembic migrations..."
    alembic upgrade head

    # 3. Seed database
    echo "Seeding database..."
    python app/database/seed.py

    # 4. Start Uvicorn
    exec uvicorn main:app --host 0.0.0.0 --port 8000
    ```
*   Add configuration files to support easy deployment on Render or Railway with managed PostgreSQL.
