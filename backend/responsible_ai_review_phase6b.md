# Responsible AI Review: Neurolens Phase 6B Safety & Compliance Audit

This document reviews the Responsible AI safeguards, transparency guidelines, and safety disclaimers implemented across the Neurolens platform in Phase 6B.

---

## 1. Safety Notice Placement & Coverage

A unified clinical disclaimer (`ResponsibleAINotice`) has been systematically integrated into all user-facing layouts to prevent any misinterpretation of observation logs as clinical diagnoses.

### Disclaimer Coverage Matrix

| Screen | Target Placement | Styling & Context |
| :--- | :--- | :--- |
| **Caregiver Dashboard** | Page Footer (`dashboard/page.tsx`) | Permanent dark glassmorphism card, visible on page load. |
| **AI Suggestions Panel** | suggestions Card Footer (`observations/page.tsx`) | Displays directly below suggestion list to anchor OIE suggestions. |
| **Clinician Report Preview** | Report Header (`report/page.tsx`) | Rendered in high-visibility light-yellow container. Enforced to render inside printed PDF reports. |
| **Login Screen** | Footer (`login/page.tsx`) | Small, clean text footer framing the application login form. |
| **Judge Demo Guide** | Safety Section (`judge_demo_guide.md`) | Included in the guide documentation to align validation expectations. |

---

## 2. Responsible AI Pillars

### A. Non-Diagnostic Guarantee (Preventing Scope Creep)
*   **No Risk Scoring**: Neurolens does not compute diagnostic labels, autism spectrum severity markers, or probability percentages.
*   **No Machine Decisions**: AI suggestions are presented purely as matching candidate *milestones* for parents to confirm or reject. OIE never overrides a parent's judgment or automatically changes a logged entry without explicit caregiver action.
*   **Qualified Clinician Boundary**: Disclaimers clearly specify that developmental clinical decisions and final diagnoses must be made by qualified healthcare professionals.

### B. Truthful Explainability (No Fabrications)
*   **No Auto-Generated Text**: OIE does not synthesize descriptive explanations using large language model prompts.
*   **Metadata-Driven Proof**: Explanations are strictly derived from verifiable repository facts:
    1.  *Domain Match*: Rationale linked directly to the developmental domain category.
    2.  *Age Suitability*: Truthful screening flags based on standard low/high month brackets (On-Track vs Screening checks).
    3.  *Transliteration Mapping*: Traceable Hinglish glossary matches (identifying exactly which local caregiver words were translated to English).

### C. Explicit Human-in-the-Loop Workflow
*   **Explicit Action**: Replaced all auto-run and autocomplete suggestion behavior with an explicit **"Analyze Observation with AI"** button. Suggestions are only loaded when requested.
*   **Lifecycle Telemetry**: Parent interaction choices (linking, thumbs rating, not-helpful comments) are logged. Caregiver metrics display simple utility summaries (Suggestions Reviewed, Helpful Votes) while hard benchmark figures are segregated to the validator portal.
