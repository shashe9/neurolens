# Neurolens: SahAI Hackathon Final Submission Package

This document compiles the submission-ready project summaries, metrics, and architecture overviews for the Neurolens platform.

---

## 📌 1. Project Overview

*   **Project Name**: Neurolens
*   **One-Sentence Description**: Neurolens is an evidence-first developmental observation platform that helps caregivers transform everyday observations into structured evidence and clinician-ready reports using transparent, local retrieval-based AI.

---

## 🔍 2. Problem & Challenges

### The Problem
Caregivers spend months observing early developmental behaviors but often struggle to articulate these observations structured during clinical visits. Conversely, pediatricians are constrained by time and lack structured, longitudinal evidence to guide developmental screening.

### Existing Challenges
1.  **High Attrition & Delay**: Long clinic waitlists delay developmental assessments during critical early learning windows.
2.  **Parent Recalling Bias**: Caregivers forget specific timelines or overlook subtle developmental behaviors.
3.  **Hinglish Linguistic Gaps**: Existing screening platforms fail to parse or transliterate local vernacular terms (Hinglish) recorded by caregivers.

---

## 💡 3. The Neurolens Solution

Neurolens acts as a **structured context compiler**, bridging the communication gap between parents and clinicians.
*   **Timeline Logs**: Caregivers capture observations in natural language.
*   **OIE suggestions**: A local embedding preprocessor translates Hinglish tokens and maps observations to CDC/AAP milestones.
*   **Traceable Compilation**: Accepted milestones link to parent observations to compile immutable clinician readiness summaries.

---

## 🏗️ 4. Technical Architecture

*   **Frontend**: Next.js 16 (React, TypeScript), styling via vanilla CSS with print-layout media overrides. `[VERIFIED]`
*   **Backend**: FastAPI, managed using Python 3.13. `[VERIFIED]`
*   **Database**: SQLite/PostgreSQL tables managed via Alembic migrations. `[VERIFIED]`

---

## 🧠 5. AI Integration

The **Observation Intelligence Engine (OIE)** is a localized retrieval model executing on the host CPU.
*   **Model**: `paraphrase-multilingual-MiniLM-L12-v2` `[VERIFIED]`
*   **Workflow**: Preprocessing (Hinglish glossary detection) ➡️ Encoding (MiniLM) ➡️ Similarity Calculation (Cosine similarity) ➡️ Weighting (steep linear age band multipliers) ➡️ Interactive Suggestion UI.

---

## 📊 6. AI Performance & Testing Benchmarks

*   **OIE Benchmark Dataset**: 160 labeled parent observations mapped against 85 standard developmental milestones. `[VERIFIED]`
*   **OIE Retrieval Scores**:
    *   *Top-1 Milestone Accuracy*: **80.62%** `[VERIFIED]`
    *   *Top-3 Milestone Accuracy*: **96.25%** `[VERIFIED]`
    *   *Domain Classification Accuracy*: **86.88%** `[VERIFIED]`
*   **Test Suite Coverage**: **55/55 tests passed** cleanly. `[VERIFIED]`

---

## 🛡️ 7. Responsible AI Guardrails

Neurolens is built to ensure absolute clinical safety and user trust:
1.  **No Diagnostic Classifiers**: The system calculates zero autism risk percentages and outputs no probability values.
2.  **Human-in-the-Loop Validation**: Caregivers retain complete control, reviewing and confirming all suggestions manually.
3.  **Clean Disclaimer Banner**: Notices warning that Neurolens does not replace professional pediatric visits are rendered across all panels.

---

## 💰 8. Project Sustainability

*   **Operational Cost**: `[ESTIMATED]` ~$46.25 - $66.25/month for cloud compute (AWS Fargate/RDS), and $0.00/month for local clinical clinic servers.
*   **Inference Costs**: Running the embedding models locally on host CPUs eliminates third-party cloud API costs.

---

## 🔮 9. Future Work

*   **ONNX In-Browser Inference**: `[PLANNED]` Compiling the SentenceTransformer model to ONNX to run vector generation directly inside the client's browser, reducing server execution costs to zero.
*   **Multilingual Expansion**: `[PLANNED]` Adding regional language translation support (e.g. Tamil, Telugu, Hindi-script vectors).
