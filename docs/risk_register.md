# Neurolens Project Risk Register

This document audits current and future operational risks for the Neurolens platform, outlining mitigation procedures.

---

## ⚡ 1. Current Operational Risks

Every metric below is **`[VERIFIED]`** under local staging structures:

| Risk Description | Severity | Likelihood | Status / Mitigation |
| :--- | :---: | :---: | :--- |
| **Seeding Record Duplication** | High | Low | **Mitigated**: Seeder logic validates duplicate entries before inserting child profiles or validation records, ensuring 100% idempotency across restarts. |
| **Authentication Session Bypass** | High | Low | **Mitigated**: API endpoints verify JWT authorization headers via FastAPI dependencies. Unauthenticated requests are blocked. |
| **Data Isolation Breach** | Critical | Low | **Mitigated**: Child database bounds are checked against `parent_child_links` ownership matches. Attempting to fetch or link observations from another child returns an HTTP 403 or 400 error. |
| **Local Model Loading Failures** | Medium | Medium | **Mitigated**: The sentence-transformer model checks the local cache folder. If missing, it downloads it once on backend startup. System healthcheck reports status if load fails. |
| **OIE Retrieval Overfitting** | Medium | Low | **Mitigated**: Cosine similarity matches are weighted strictly using linear age decays rather than absolute score matches. |
| **Demonstration Dataset Misinterpretation** | High | Medium | **Mitigated**: All validation-related dashboard components (`/judge` interface) and documentation files explicitly designate metrics as a preseeded demonstration validation dataset. |
| **Host Docker Path Issues** | Low | High | **Unmitigated**: Host OS lacks docker binaries on the path, requiring manual local python command execution for developer review. |

---

## 🔮 2. Future Production & Scaling Risks

Every metric below is **`[ESTIMATED]`** or **`[PLANNED]`** for future scaling milestones:

| Risk Description | Severity | Likelihood | Status / Mitigation |
| :--- | :---: | :---: | :--- |
| **OIE Inference CPU Latency** | Medium | Medium | `[PLANNED]` Compile the SentenceTransformer model to ONNX to run vector generation directly inside the caregiver's browser, offloading server workload. |
| **Multi-Clinic Data Growth** | Medium | Low | `[PLANNED]` Configure partition structures in RDS PostgreSQL tables. Aggregate database summaries during low-traffic windows. |
| **Parent Misunderstanding of Warnings** | High | Low | `[VERIFIED]` Render explicit disclaimers in dark red/bold styling across the caregiver dashboard, suggestion panel, and printed report templates. |
| **Cloud Outage of DB Instances** | High | Low | `[PLANNED]` Configure multi-AZ deployments for RDS databases with daily automated backups. |
| **Linguistic Transliteration Decay** | Low | Medium | `[PLANNED]` Leverage clinician and caregiver feedback inputs to regularly append new Hinglish terms to the local dictionary glossary. |
