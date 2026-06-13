# Neurolens Phase 6C: Prioritization Matrix & Roadmap (Revised)

This revised prioritization matrix ranks Phase 6C deliverables according to their immediate impact on the judge's 2-to-5 minute review flow, technical complexity, and safety.

---

## 📊 Priority Matrix

| Feature ID | Feature Name | Description | Judge Impact | Implementation Effort | Technical Risk | Priority Rank | ROI Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **F-01** | **Report PDF/Print Layout Polish** | `@media print` CSS overrides to hide headers, navbars, and buttons, formatting the card for clean A4 printing. | **Critical** (High) | **Low** (15 mins) | **Low** | **1** (Highest) | **10 / 10** |
| **F-02** | **Landing Page Impact & Safety Section** | Showcase problem/solution, OIE metrics badge, and non-diagnostic safety boundaries on entrance. | **Critical** (High) | **Low** | **Low** | **2** | **9.5 / 10** |
| **F-03** | **Judge Portal Evidence Cards** | Visual AI Pipeline Flow, Safety Bounds Card, and Database/Test coverage metrics. | **High** | **Low** | **Low** | **3** | **9.0 / 10** |
| **F-04** | **Multi-Account Demo Seeding** | Seed three isolated, scenario-specific judge accounts (typical, concern, mixed) instead of destructive resets. | **High** | **Low-Moderate** | **None** (Passive) | **4** | **8.5 / 10** |
| **F-05** | **Validation Sample Split & Counts** | Show role averages alongside caregiver (14) and clinician (5) participant counts. | **Medium-High** | **Low-Moderate** | **Low** | **5** | **8.0 / 10** |
| **F-06** | **Deployment & Startup Automation** | Configure backend auto-migration and database seeding startup scripts for Render/Railway VPS. | **Critical** (High) | **Moderate** | **Low** | **6** | **8.0 / 10** |

---

## 🔍 Cost-Benefit Analysis

### F-01: Report PDF/Print Layout Polish
*   **Benefits**: Ensures that reports print as clean, professional medical summaries, immediately demonstrating clinical document-generation readiness.
*   **Costs**: Extremely low; simple CSS changes.

### F-02: Landing Page Impact & Safety Section
*   **Benefits**: Tells the judge immediately why Neurolens exists, what problem it solves, and how the OIE performs responsibly.
*   **Costs**: None; purely frontend UI content changes.

### F-03: Judge Portal Evidence Cards
*   **Benefits**: Explains the system's pipeline and boundaries in under 30 seconds of reading.
*   **Costs**: Minimal; simple card layouts.

### F-04: Multi-Account Demo Seeding
*   **Benefits**: Eliminates the high risk of foreign key errors, database corruption, or UI complexity. Switch demo context simply by logging in.
*   **Costs**: Slight script extensions in `seed.py`.

### F-05: Validation Sample Split & Counts
*   **Benefits**: Converts the "validation study" from a conceptual framework into an empirical clinical study.
*   **Costs**: Small SQL grouping queries and frontend metric grids.

### F-06: Deployment & Startup Automation
*   **Benefits**: Guarantees that remote demo server instances launch and sync with PostgreSQL automatically without manual CLI steps.
*   **Costs**: Requires setting up an `entrypoint.sh` startup script.
