# Phase 6B Pre-Implementation Audit: Neurolens Explainability & Validation

This audit documents the current state of Neurolens' AI suggestion, reporting, and telemetry infrastructure before implementing the explainability, user feedback, validation analytics, and safety features of Phase 6B.

---

## 1. AISuggestionEvent Schema

The database model is defined in `backend/app/models/models.py#L233-L262`. 

### Database Table: `ai_suggestion_events`
*   **`id`** (`uuid.UUID`, Primary Key): Generated as `uuid.uuid4()`.
*   **`child_id`** (`uuid.UUID`, Foreign Key pointing to `children.id`): References the child profile. Employs a database-level `CASCADE` delete constraint.
*   **`observation_id`** (`uuid.UUID`, Foreign Key pointing to `observations.id`, nullable): Set to `NULL` during `POST /ai/suggest`, and optionally linked to a saved observation when a suggestion is accepted or confirmed. Employs `ON DELETE SET NULL`.
*   **`raw_text`** (`Text`, Not Null): The input text of the observation before preprocessing.
*   **`suggested_domains`** (`JSON`, Not Null): A JSON list of domains suggested by the OIE (e.g., `{"domain_name": "Communication", "relevance_score": 0.85, "relevance_label": "Strong relevance"}`).
*   **`suggested_milestones`** (`JSON`, Not Null): A JSON list of milestones suggested by the OIE. Currently stored as objects with `milestone_id`, `title`, `relevance_score`, and `relevance_label`.
*   **`selected_domain`** (`String(100)`, Nullable): The domain selected by the parent/caregiver if confirmed.
*   **`selected_milestone_id`** (`uuid.UUID`, Foreign Key pointing to `milestones.id`, nullable): The specific milestone selected/confirmed by the user. Employs `ON DELETE SET NULL`.
*   **`max_similarity`** (`Float`, Not Null): The maximum cosine similarity score across suggested milestones.
*   **`relevance_rank`** (`String(50)`, Not Null): The relevance label of the top milestone.
*   **`interaction_type`** (`InteractionType` as String, Not Null): Can be `ACCEPTED`, `OVERRIDDEN`, `IGNORED`, or `MANUAL_ONLY`.
*   **`model_version`** (`String(50)`, Not Null): Stored as `oie_v1_multilingual`.
*   **`processing_time_ms`** (`Integer`, Not Null): Records backend request processing speed.
*   **`error_type`** (`String(100)`, Nullable): Captures any processing or alignment failure error messages.
*   **`created_at`** (`DateTime`, Not Null): Defaults to `datetime.utcnow`.
*   **`accepted_at`** (`DateTime`, Nullable): Set to the timestamp when `interaction_type` becomes `ACCEPTED`.

---

## 2. AI Endpoint Responses

The AI endpoint responses are controlled by the Pydantic schemas in `backend/app/schemas/schemas.py` and endpoints in `backend/app/api/endpoints/ai.py`.

### A. Endpoint: `POST /ai/suggest`
*   **Request Schema (`AISuggestRequest`)**:
    *   `observation_text` (String, 10–1000 characters)
    *   `child_id` (`uuid.UUID`)
    *   `child_age_months` (Integer, 0–120)
*   **Response Schema (`AISuggestResponse`)**:
    *   `domains`: List of suggested domains, each having `domain_name`, `relevance_score`, `relevance_label`.
    *   `milestones`: List of suggested milestones, each having `milestone_id`, `title`, `relevance_score`, `relevance_label`.
    *   `observation_patterns`: List of regex-matched patterns extracted by `ObservationPatternExtractor.extract`.
    *   `report_keywords`: List of keywords extracted for clinician reporting.
    *   `explanations`: List of string explanations generated in a basic loop using word overlaps.
    *   `event_id` (`uuid.UUID`): Database identifier of the suggestion event.
    *   `model_version`: Multilingual engine version string.

### B. Endpoint: `POST /ai/confirm/{event_id}`
*   **Request Schema (`AIConfirmRequest`)**:
    *   `selected_domain` (String, Optional)
    *   `selected_milestone_id` (`uuid.UUID`, Optional)
    *   `interaction_type` (`InteractionType` Enum: `ACCEPTED`, `OVERRIDDEN`, `IGNORED`, `MANUAL_ONLY`)
*   **Response Schema**: Returns the updated suggestion event record.

### C. Endpoint: `GET /ai/metrics/{child_id}`
*   **Response Schema**:
    *   `total_suggestions` (Integer)
    *   `accepted` (Integer)
    *   `overridden` (Integer)
    *   `ignored` (Integer)
    *   `manual_only` (Integer)
    *   `acceptance_rate` (Float)
    *   `top_domains` (List of Strings)
    *   `top_milestones` (List of Strings)

---

## 3. Observation Suggestion UI

### Frontend Page: `frontend/src/app/observations/page.tsx`
*   **Current UI State**: The observations page consists of a standard HTML form that allows logging an observation manually. Users can select an entry type (`general`, `concern`, `milestone`), choose a domain, select a milestone (if type is `milestone`), and write their text description.
*   **OIE suggestions integration**: AI suggestions are **not** currently displayed. When parents log observations, the system does not dynamically query the `/ai/suggest` endpoint, nor does it present recommendations, feedback options, or explainability details in the interface.
*   **Required Update**: Integrate a client-side panel within the observation flow that requests AI recommendations, shows them to the user, offers a way to confirm/link them, and displays explainability and feedback controls.

---

## 4. Report Generation Pipeline

### Service: `backend/app/services/report_service.py`
*   **Function**: `generate_report(db, child_id, visit_id)`
*   **Current Snapshot Content**:
    *   **Demographics**: Child age in months, name, gender.
    *   **Historian Details**: Parents associated with the child.
    *   **Qualitative Evidence Feed**: Active parent observation logs, including locations, relations, and regression flags.
    *   **Milestone Matrix**: Complete list of the 80 milestones, each with status (`not_observed`, `emerging`, `observed`, etc.), evidence references, and clinical source citations.
    *   **Visit Context**: Clinician details, date, priority status, concern level, and clinician note.
    *   **Coverage Summary**: Aggregate metrics per domain (supported milestones vs. total).
*   **Current State of Suggestions/Feedback in Reports**: AI suggest events, confirmation states, and parent feedback statistics are **completely excluded** from the report compilation process. Report outputs remain strictly focused on validated milestones and raw parent observations.

---

## 5. Existing Telemetry Structures

*   **Database logging**: Suggestion metrics (processing times, similarity scores, selected vs. suggested domain mappings) are saved inside the `ai_suggestion_events` table.
*   **Analytics capability**: The `GET /ai/metrics/{child_id}` endpoint aggregates basic counts and acceptance rates.
*   **Telemetry Gaps**:
    *   No mechanism for capturing user satisfaction (thumbs up/down ratings) on suggestions.
    *   No comments or audit trail for rejected or misclassified suggestions.
    *   No visualization on the frontend for tracking AI utility (for parents or visiting judges).
    *   No unified disclaimers or Responsible AI safety notifications on user-facing pages.
