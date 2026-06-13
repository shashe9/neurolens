# Migration Guide: Transitioning from Sandbox Parent to Authenticated Parent Session

This document details the database migration, model changes, and API transitions implemented to move Neurolens from a single-user sandbox parent architecture to a secure, multi-user authentication model.

---

## 🗄️ 1. Database Schema Extensions

To support authentication, the existing SQLite schema was updated.

### Parent Table Modifications
*   **Column Added**: `hashed_password` (type `String(255)`, nullable) added to the `parents` table.
*   **Nullable Rationale**: Nullable structure preserves database compatibility for existing sandbox parents and ensures legacy mock test rows continue to load without constraint failures.

---

## 🚀 2. Alembic Migration Track

The migration script adds the password credentials column in a linear Alembic sequence:

*   **Migration Script**: [f5a8a0c2b993_add_parent_hashed_password.py](file:///d:/Desktop/New_Autism/backend/alembic/versions/)
*   **Revision ID**: `f5a8a0c2b993`
*   **Down Revision**: `2d4906a1b5bd` (the actual database head from Phase 4/5)
*   **Behavior**: Adds the `hashed_password` column to the `parents` table on upgrade, and drops it on downgrade.

To apply this migration to your local database:
```bash
alembic upgrade head
```

---

## 🔗 3. API & Controller Transitions

The table below outlines how endpoints changed to support user session isolation:

| Endpoint | Previous V1 Sandbox Behavior | New Phase 6A Authenticated Behavior |
| :--- | :--- | :--- |
| `POST /auth/login` | *N/A (Did not exist)* | Validates plain credentials, generates access JWT token. |
| `POST /children` | Auto-linked child to a default sandbox parent | Requires auth; links to the authenticated parent session context. |
| `GET /children` | Fetched all children in DB | Enforces boundary: filters and returns children linked to the current parent. |
| `GET /children/{id}` | Fetched child profile directly | Validates that child belongs to current parent; returns 403 if unlinked. |
| `POST /observations` | Saved observation under default sandbox parent ID | Requires auth; saves observation under authenticated parent context. |
| `POST /reports` | Allowed compiling reports for any child | Validates child ownership link; restricts compilation to authenticated user. |

---

## 🧪 4. Testing Suite Compatibility

To prevent breaking existing test files, a test client dependency override is injected in [conftest.py](file:///d:/Desktop/New_Autism/backend/tests/conftest.py).

*   **Implementation**:
    ```python
    app.dependency_overrides[get_current_parent] = override_get_current_parent
    ```
*   **Mock Verification**: The override checks the database for any parent created inside the test context and automatically links test child records to it, resolving authorization boundaries dynamically while keeping tests decoupled from the HTTP login endpoints.
