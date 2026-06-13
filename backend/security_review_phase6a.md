# Neurolens Phase 6A Security Review

This document provides a security review of the Authentication Lite implementation introduced in Neurolens Phase 6A.

---

## 🔒 1. Cryptographic Password Hashing

Neurolens enforces standard, one-way password hashing for all parent credential stores using the `bcrypt` algorithm.

*   **Implementation**: Hashing and verification helper functions reside in [security.py](file:///d:/Desktop/New_Autism/backend/app/core/security.py) using the native `bcrypt` library.
*   **Safety Properties**:
    *   Passwords are never stored in plain text.
    *   Bcrypt dynamically applies a salt parameter before hashing, mitigating dictionary and precomputed rainbow table attacks.
    *   Password verification is executed using standard, time-constant hashing comparisons to guard against timing attacks.

---

## 🔑 2. JSON Web Token (JWT) Session Management

JWT signature encoding and decoding handle stateless session authorization.

*   **Secret Management**:
    *   The `JWT_SECRET_KEY` is loaded dynamically from environment variables.
    *   A production runtime safety guard is established in [config.py](file:///d:/Desktop/New_Autism/backend/app/core/config.py): if the application environment is configured as `production` and the environment variable `JWT_SECRET_KEY` is missing or matches the development fallback default, the backend raises a `RuntimeError` and aborts startup immediately. This prevents accidental deployments with default keys.
*   **Signature Security**:
    *   Tokens are signed using the robust HMAC-SHA256 (`HS256`) algorithm.
    *   Bearer tokens have a configurable expiry threshold set by default to 24 hours (`ACCESS_TOKEN_EXPIRE_MINUTES = 1440`), minimizing replay windows.

---

## 🛡️ 3. Request Boundary Protection

API endpoints are secured behind the authentication dependency injection barrier.

*   **Dependency Injection**: The `get_current_parent` dependency inside [dependencies.py](file:///d:/Desktop/New_Autism/backend/app/api/dependencies.py) intercepts incoming requests, extracts the JWT from the `Authorization: Bearer <token>` header, decodes and validates the signature, and matches the subject identity to a database `Parent` record.
*   **Endpoint Coverage**: All stateful endpoints (`/children`, `/observations`, `/milestones`, `/visits`, `/reports`, `/ai`) require a valid session context.
*   **Data Isolation Check**:
    *   Endpoint controllers validate parent-child ownership boundaries by verifying that the child ID requested matches a record linked to the current parent ID in the `parent_child_links` database table.
    *   Cross-parent access attempts return a strict `403 Forbidden` error, isolating parent sessions.
