# Neurolens Authentication Design Audit

This document outlines the security architecture and design choices for implementing Authentication Lite in the Neurolens platform for Phase 6A.

---

## 1. Existing Model & API Structure Audit

Prior to Phase 6A, Neurolens operated in a single-user sandbox layout:
1.  **Parent Model**: Defined in [models.py](file:///d:/Desktop/New_Autism/backend/app/models/models.py) with no password fields or auth associations.
2.  **API Structure**: The frontend retrieved a hardcoded sandbox parent via `/children/parent/sandbox` (which resolved to `sandbox.parent@example.com` or `jane.doe@example.com` in [children.py](file:///d:/Desktop/New_Autism/backend/app/api/endpoints/children.py)). This ID was saved in `localStorage` under `neurolens_parent_id` and supplied as a URL parameter for observations/child queries.
3.  **Vulnerability**: No endpoint required authentication headers or checked token signatures. Anyone could access details by guessing a child's UUID or calling children listing routes without filtering parameters.

---

## 2. Authentication Strategy Design

### A. Password Cryptography
*   **Algorithm**: `bcrypt` (using Python's `bcrypt` package directly to prevent version conflicts on Python 3.12/3.13).
*   **Process**: Passwords will be salted and hashed before database storage. Plaintext passwords are never stored.
*   **Verification**: Password inputs are verified using `bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))`.

### B. JWT Token Strategy
*   **Signature Security**: The token is signed using `HS256` symmetric key encryption.
*   **Secret Key Management**: The signing key is loaded dynamically from `os.getenv("JWT_SECRET_KEY")`. A development fallback is provided, but in production, startup halts immediately if no key is configured.
*   **Token Content (Claims)**:
    *   `sub`: Stored as the parent's email (e.g. `judge@neurolens.demo`).
    *   `exp`: Expiration claim (Unix timestamp representing 24 hours from issuance).
*   **Expiration Duration**: Set to 24 hours (`1440` minutes) to ensure that the evaluation session remains uninterrupted during judging sessions.

### C. Login Flow
1.  Client submits JSON credentials (`email` and `password`) to `POST /auth/login`.
2.  Backend queries `Parent` by email.
3.  Backend verifies the password hash using the `bcrypt` helper.
4.  On verification, the backend compiles a signed JWT access token.
5.  Response payload:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
      "token_type": "bearer",
      "parent_id": "uuid-string-of-parent",
      "email": "parent@example.com"
    }
    ```

### D. Protected Routes Schema
FastAPI endpoints will require user context via the `get_current_parent` dependency:
```python
def get_current_parent(request: Request, db: Session = Depends(get_db)) -> Parent:
    ...
```

The dependency parses the incoming headers, decodes the JWT, fetches the matching parent, and injects it into the route handler. 

#### Endpoints Enforcing Authentication:
*   `/children` (POST, GET, PUT, DELETE, POST /restore)
*   `/visits` (POST, GET)
*   `/reports` (POST, GET)
*   `/ai/suggest` (POST)
*   `/ai/confirm/{event_id}` (POST)
*   `/ai/events/{child_id}` (GET)
*   `/ai/metrics/{child_id}` (GET)
*   `/children/{child_id}/observations` (POST, GET, GET /stats)
*   `/observations/{id}` (GET, PUT, DELETE)
*   `/children/{child_id}/milestones` (GET, PUT /status, GET /coverage, POST /evidence, DELETE /evidence)

---

## 3. Test Harness Adaptations

To maintain 100% cleanliness in production, the dependency check will not include conditional testing checks in `dependencies.py`. Instead, all compatibility is resolved in the test harness at [conftest.py](file:///d:/Desktop/New_Autism/backend/tests/conftest.py) by overriding the dependency on the TestClient:
```python
# conftest.py
@pytest.fixture(scope="function")
def client(db):
    def override_get_current_parent():
        return db.query(Parent).first()
    app.dependency_overrides[get_current_parent] = override_get_current_parent
    ...
```
This guarantees that unit and integration tests run seamlessly using the seeded test parents, while keeping production code completely free of testing-specific fallbacks. Real authentication functionality is separately validated in `tests/test_auth.py` by hitting routes with a clean, non-overridden client.
