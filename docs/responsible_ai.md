# Responsible AI Boundary Guidelines

Neurolens is a developmental observation and clinician preparation platform designed to help parents record developmental observations, track milestones, and prepare context for clinician visits. It is designed to act as an information compilation helper, NOT a clinical agent.

This document outlines the strict functional boundaries of Neurolens for developers, reviewers, and mentors.

---

## Permitted Features (Allowed)

The platform is explicitly designed to support parents and clinicians by structuring existing factual information:

1. **Developmental Observation Logging**:
   - Allowing parents to write observations in their own words.
   - Organizing logs by developmental domains (e.g., Communication, Fine Motor) or linking them to specific milestones.
   - Categorizing entry types (General Observation, Concern, Milestone Observation).

2. **Factual Milestone Checklist**:
   - Presenting standard developmental milestones (e.g., CDC/AAP developmental milestones) categorized by age ranges.
   - Tracking parent-reported milestone statuses (Not Started, In Progress, Achieved).

3. **Visit Context Compilation**:
   - Assisting parents in organizing their concerns, questions, and priority items before clinical visits.

4. **Clinician Report Assembly**:
   - Assembling parent-recorded child details, observations, milestone matrices, and visit concerns into a single formatted, printable clinician report.
   - Saving reports as immutable JSON snapshots of historical observation logs.

---

## Forbidden Features (Forbidden)

Neurolens MUST NOT implement or attempt to perform any clinical analysis, assessment, or automated screening:

1. **No Autism Detection/Screening**:
   - The platform must not calculate "probability scores," "autism indicators," or "risk indexes" for autism spectrum disorder (ASD) or any other neurodevelopmental condition.
   - Do not integrate diagnostic screening tools (e.g., M-CHAT, CARS, ADOS) that generate automated diagnostic outcomes.

2. **No Clinical Recommendations or Advice**:
   - The platform must not provide diagnostic opinions, suggest clinical treatment paths, or advise on therapeutic interventions.
   - The clinician report must only present parent observations and recorded milestone statuses without automated clinical commentary.

3. **No Automated Risk Scoring**:
   - Do not display warnings or risk categories (e.g., "high risk," "borderline") to the parent. Highlighting parent-recorded "Concerns" is allowed, but must not be augmented by algorithmic interpretation.

4. **No Automated Predictive Analysis**:
   - The platform must not use machine learning or heuristic rules to predict future developmental delays or conditions.

5. **No AI Chatbots / Conversational Clinical Advisors**:
   - Do not implement conversational AI models that act as medical advisors or counselors.

---

## Summary for Mentors

Neurolens V1 serves as a **context aggregator** that bridges the communication gap between parents and clinicians. By keeping the platform focused solely on tracking factual evidence and assembling clean reports, we ensure that clinical authority and diagnostic execution remain entirely in the hands of qualified healthcare professionals.
