# Neurolens: Known Limitations

This document lists the verified boundaries and limitations of the Neurolens prototype. It acts as an honest disclaimer for reviewers, mentors, and hackathon judges.

---

## 🚫 1. System & Functional Boundaries

*   **No Diagnostic Engine**: Neurolens does **NOT** diagnose neurodevelopmental delays, Autism Spectrum Disorder (ASD), or any other clinical conditions. It does not output risk categories (e.g. "at risk") or autism probability metrics.
*   **No Treatment or Referral Guidance**: The application does not propose speech therapies, behavioral interventions, or pediatric referral priorities.
*   **Intake Preparation Only**: Compiled reports are designed as preparation summaries to help parents organize their memories before clinic visits. They cannot replace standardized screening assessments (e.g. M-CHAT, ASQ-3) or clinical examinations.
*   **Wording Status**: `[VERIFIED]` (Aligned with [responsible_ai.md](file:///d:/Desktop/New_Autism/docs/responsible_ai.md)).

---

## 🧠 2. Technical AI Limitations

*   **Retrieval Thresholds**: The Observation Intelligence Engine (OIE) is a semantic retrieval system, not a conversational assistant. It maps parent observations to standard guidelines but does not generate free-form text or advice.
*   **Overlapping Semantics**: The model struggles to separate overlapping developmental behaviors, particularly in distinguishing complex interactions that span both **Communication** and **Social Emotional** domains.
*   **No Context Aggregation in Vectors**: Embeddings are generated per individual observation text. The engine does not aggregate context across multiple different observations to infer progression trends.
*   **Wording Status**: `[VERIFIED]`.

---

## 📊 3. Validation Limitations

*   **Demonstration Dataset Only**: The database validation records (N=19) constitute a **demonstration validation dataset** preseeded for demonstration purposes. **No clinical trial, usability study, or pilot evaluation has been conducted with external real-world caregivers or clinicians.**
*   **Limited Evaluation Scope**: The OIE retrieval benchmarks (Top-3 accuracy: 96.25%) are calculated against a clean, pre-labeled dataset of 160 observations. Performance on messy, unstructured, or highly noisy caregiver text entries may vary.
*   **Wording Status**: `[VERIFIED]`.

---

## 🗣️ 4. Linguistic Limitations

*   **English/Hinglish Bias**: The underlying vector model (`paraphrase-multilingual-MiniLM-L12-v2`) is optimized for English semantic structures. The local transliteration glossary currently maps 8 basic Hindi developmental terms written in Latin script (Hinglish) to English.
*   **Regional Dialect Gaps**: Neurolens does not support other Indian regional languages (e.g. Tamil, Telugu, Marathi), nor does it support native script inputs (e.g., Devanagari text).
*   **Wording Status**: `[VERIFIED]`.

---

## 🐋 5. Deployment Limitations

*   **Docker Host Compatibility**: Local container builds and execution are unverified (`[NOT VERIFIED]`) on the local workspace host due to missing Docker binaries on the host system PATH. 
*   **No Cloud Staging**: No live staging url, active domain DNS, SSL certificates, or cloud container instances are currently configured.
*   **Wording Status**: `[VERIFIED]`.
