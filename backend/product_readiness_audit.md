# Product Readiness Audit

This document presents a comprehensive repository-wide product readiness audit of the Neurolens codebase. This audit evaluates the software's structural, architectural, and security posture in preparation for the SahAI submission. 

---

## Authentication & Authorization

### 1. Current State
The application currently operates entirely in a **Single-User Sandbox Mode** with **zero authentication and authorization mechanisms**. There are no user registration, login, logout, password storage, session handling, or token-based authentication services. Multi-user isolation is absent, as all database profiles and associated developmental observations are exposed to anyone who can query the API. 

The application utilizes a hardcoded sandbox parent profile (`sandbox.parent@example.com` or `jane.doe@example.com`) as a fallback identity.

### 2. Evidence from Repository
*   **Models**: In [models.py](file:///d:/Desktop/New_Autism/backend/app/models/models.py#L50-L66), the `Parent` table contains only basic attributes (`id`, `first_name`, `last_name`, `email`, `created_at`). There are no columns for passwords, salts, hashes, roles, active sessions, or security metadata.
*   **Endpoints**: In [children.py](file:///d:/Desktop/New_Autism/backend/app/api/endpoints/children.py#L12-L30), the `get_sandbox_parent()` dependency maps directly to a hardcoded sandbox parent query:
    ```python
    @router.get("/parent/sandbox", response_model=ParentResponse)
    def get_sandbox_parent(db: Session = Depends(get_db)):
        parent = db.query(Parent).filter(Parent.email == "sandbox.parent@example.com").first()
        ...
    ```
*   **Frontend Context**: In [ActiveChildContext.tsx](file:///d:/Desktop/New_Autism/frontend/src/components/ActiveChildContext.tsx#L40-L56), the client defaults to requesting the sandbox endpoint and saving the returned parent ID in `localStorage`:
    ```typescript
    const parentRes = await fetch(`${apiUrl}/children/parent/sandbox`);
    const parentData: Parent = await parentRes.json();
    setActiveParentId(parentData.id);
    localStorage.setItem("neurolens_parent_id", parentData.id);
    ```
*   **API Openness**: Across all routes in `backend/app/api/endpoints/`, no dependencies enforce authenticated headers or validation tokens. For example, in [observations.py](file:///d:/Desktop/New_Autism/backend/app/api/endpoints/observations.py#L69-L76), observations are fetched based solely on a path parameter (`child_id`) without confirming if the request origin corresponds to an authorized parent profile.

### 3. Missing Components
*   **Password Cryptography**: No password hashing libraries (e.g., `bcrypt`, `argon2-cffi`) are configured in the backend environment.
*   **Credentials Database Schema**: Columns on the `Parent` table to store password hashes.
*   **Auth Router**: Authentication endpoints (`/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`).
*   **Token Verification Dependency**: Security dependencies in FastAPI (e.g., using `HTTPBearer` or `OAuth2PasswordBearer` with `PyJWT`) to parse and validate incoming request headers.
*   **Route Guards & Forms**: Next.js login/registration page layouts and route protection logic to intercept unauthenticated clients.

### 4. Risk Level
> [!CAUTION]
> **CRITICAL**
> Since Neurolens processes sensitive developmental logs and healthcare-adjacent information for children, deploying this system without access controls exposes all patient records to arbitrary data extraction, modification, and deletion.

### 5. Recommended Action
1.  Add `bcrypt` and `pyjwt` to backend requirements.
2.  Update the `Parent` model to support credentialed logins (add `password_hash` column).
3.  Implement standard JWT token emission on login/register endpoints.
4.  Introduce a FastAPI dependency `get_current_parent` to validate JWTs and secure all endpoints under `backend/app/api/`.
5.  Construct Next.js login/logout pages and wrap children/observations views in client-side auth context guards.

---

## Data Model Readiness

### 1. Current State
The database schema defines a foundational relational model supporting parents, children, milestones, observations, and clinical reports. However, because there are no authentication constraints or tenant separation keys, the tables are queried globally. Furthermore, the clinician role has no dedicated table or attributes—clinicians exist only as unstructured strings inside clinical visit configurations.

### 2. Evidence from Repository
*   **Parent-Child Junction**: The `parent_child_links` association table in [models.py](file:///d:/Desktop/New_Autism/backend/app/models/models.py#L29-L36) links parents to children, but the queries across endpoints do not assert this relationship.
*   **Open Children Retrieval**: In [children.py](file:///d:/Desktop/New_Autism/backend/app/api/endpoints/children.py#L72-L88), calling `list_children()` without a `parent_id` parameter returns the entire list of children registered on the database:
    ```python
    @router.get("", response_model=List[ChildResponse])
    def list_children(
        parent_id: Optional[uuid.UUID] = None,
        include_archived: bool = False,
        db: Session = Depends(get_db)
    ):
        query = db.query(Child)
        ...
        if parent_id:
            query = query.join(Child.parents).filter(Parent.id == parent_id)
        return query.all()
    ```
*   **Report Generation Fallbacks**: In [report_service.py](file:///d:/Desktop/New_Autism/backend/app/services/report_service.py#L43-L54), parent relationships are hardcoded during clinical summary compilation:
    ```python
    parents_data.append({
        "id": str(parent.id),
        "first_name": parent.first_name,
        "last_name": parent.last_name,
        "email": parent.email,
        "relationship": "Parent" # Simple default relationship for V1
    })
    ```
*   **Unstructured Clinicians**: In [models.py](file:///d:/Desktop/New_Autism/backend/app/models/models.py#L198-L214), `ClinicalVisit` stores `clinician_name: Mapped[str] = mapped_column(String(100), nullable=False)`. No `Clinician` account table or profiles exist, meaning clinicians cannot independently log in, review dashboard backlogs, or manage patients.

### 3. Missing Components
*   **Clinician Database Entity**: A `Clinician` database model (storing NPI details, practice affiliations, and login credentials) to separate caregiver actions from clinician actions.
*   **Enforced Junction Assertions**: Business logic checking that queries requesting child-specific details verify if `current_user.id` exists in `parent_child_links`.
*   **Multi-Tenant Schema Keys**: Tenant isolation columns (e.g., `practice_id` or `clinic_id`) if the platform is deployed to support multiple pediatric centers.

### 4. Risk Level
> [!WARNING]
> **HIGH**
> Under high-concurrency production usage, the lack of parent-child relationship checking on resource lookups results in a direct data leakage vulnerability. Any authenticated parent could fetch observations or reports for *any* child ID.

### 5. Recommended Action
1.  Enforce relationship validations at the API controller layer (e.g., check `parent_child_links` inside `list_observations`, `create_observation`, and `generate_report`).
2.  Add a `Clinician` database model and separate the API schema into parent-facing vs. clinician-facing routers.
3.  Deprecate the fallback relationship default in report assembly, replacing it with the actual value from the junction table.

---

## Judge Experience

### 1. Current State
The sandbox setup allows judges to view preloaded sample data and explore features without manual onboarding. However, there is zero interface guidance, no ability for judges to register test profiles from the frontend, and no integrated mechanism to reset modified database records. Furthermore, the clinician visit preparation and developmental summary outputs exist in a single unified interface, obscuring the distinct viewpoints of parents and clinicians.

### 2. Evidence from Repository
*   **Single Entry point**: The root dashboard redirects directly to the child selection page mapped in [page.tsx](file:///d:/Desktop/New_Autism/frontend/src/app/page.tsx). If a judge alters or deletes observations, the changes persist, and the judge cannot restore default sample profiles from the UI.
*   **Preloaded Seeds**: In [seed.py](file:///d:/Desktop/New_Autism/backend/app/database/seed.py), excellent developmental patterns are created for "Demo Child A" (consistently points to objects, says two words together) and "Demo Child B" (exhibits concern observations like lack of response when name is called). However, executing this seed requires direct terminal command-line interface (CLI) execution:
    ```bash
    python -m app.database.seed
    ```
*   **Interface Overlap**: Parent activities (logging observations, reviewing progress charts) are displayed on the same layout as clinician tasks (writing visit concern priorities, compiling immutable JSON reports), causing potential workflow confusion.

### 3. Missing Components
*   **Visual Scenario Switcher / Admin Bar**: A visible debug overlay or demo controller that lets judges populate alternative mock scenarios (e.g., Delay Concern vs. Normal Progression) with one click.
*   **Interactive Onboarding Walkthrough**: Step-by-step UI helper overlays (e.g., using `intro.js` or `driver.js`) highlighting how the Observation Intelligence Engine (OIE) suggests domains and links milestones to natural observations.
*   **Reset DB Controller**: An admin API endpoint `/api/admin/reset` exposed on the UI allowing immediate database re-seeding.

### 4. Risk Level
> [!NOTE]
> **MEDIUM**
> Evaluators might get confused about the separation between parent input and clinician output, or might mutate the database state in a way that breaks subsequent pages without a clear way to restore the demo.

### 5. Recommended Action
1.  Implement a floating "Demo Control Hub" overlay in the Next.js UI (visible only in dev/demo environments).
2.  Create an admin API route in the backend `/admin/database/reset` that drops SQLite tables, re-runs Alembic migrations, and re-triggers the database seed. Expose this as a "Reset Default Demo Data" button in the control hub.
3.  Incorporate a step-by-step guided user walkthrough highlighting the observation submission -> AI domain suggestion -> report compilation workflow.

---

## Deployment Readiness

### 1. Current State
The repository contains Dockerfiles and a Docker Compose orchestrator. However, the frontend Docker container is configured for development mode, database passwords are hardcoded in environment templates, and there is no automated database migration pipeline. Neurolens cannot be deployed directly to a production server in its current state.

### 2. Evidence from Repository
*   **Frontend Dockerfile**: In [Dockerfile](file:///d:/Desktop/New_Autism/frontend/Dockerfile#L15-L16), the next.js image runs in development mode rather than compiling a production bundle:
    ```dockerfile
    # Start development server
    CMD ["npm", "run", "dev"]
    ```
*   **Hardcoded Secrets**: The database credentials are hardcoded across multiple configuration files:
    *   [config.py](file:///d:/Desktop/New_Autism/backend/app/core/config.py#L12): `DATABASE_URL: str = "postgresql://postgres:postgres_secure_pass_123@localhost:5432/neurolens_db"`
    *   [.env.example](file:///d:/Desktop/New_Autism/.env.example#L11): `DATABASE_URL=postgresql://postgres:postgres_secure_pass_123@postgres:5432/neurolens_db`
    *   [docker-compose.yml](file:///d:/Desktop/New_Autism/docker-compose.yml#L29): `DATABASE_URL=postgresql://postgres:postgres_secure_pass_123@postgres:5432/neurolens_db`
*   **Migration Steps**: The `docker-compose.yml` does not contain an entrypoint step to run migrations. If the containers are started in a clean Docker VM, the backend fails to connect or query tables until a user manually executes `alembic upgrade head` on the host container shell.

### 3. Missing Components
*   **Production Frontend Dockerfile**: A multi-stage Docker build for Next.js that executes `npm run build` and serves static files or launches optimized standalone builds.
*   **Orchestration Startup Order**: An entrypoint shell script (`entrypoint.sh`) in the backend container that tests PostgreSQL connection readiness, automatically runs `alembic upgrade head`, and loads seeds before starting Uvicorn.
*   **Host CORS Restrictions**: A configurable origin list in the production environment variables (currently defaults to `http://localhost:3000` or open origins).

### 4. Risk Level
> [!WARNING]
> **HIGH**
> Attempting to deploy the current configuration to cloud environments will result in low performance (Next.js dev engine in container), potential server crashes on new database instances (missing auto-migrations), and vulnerability to default credentials.

### 5. Recommended Action
1.  Refactor `frontend/Dockerfile` into a multi-stage production environment:
    ```dockerfile
    FROM node:20-alpine AS builder
    WORKDIR /app
    COPY package*.json ./
    RUN npm ci
    COPY . .
    RUN npm run build
    
    FROM node:20-alpine AS runner
    WORKDIR /app
    ENV NODE_ENV=production
    COPY --from=builder /app/.next ./.next
    COPY --from=builder /app/package.json ./package.json
    COPY --from=builder /app/node_modules ./node_modules
    EXPOSE 3000
    CMD ["npm", "start"]
    ```
2.  Add a `wait-for-it.sh` or a healthcheck retry loop script in the backend Dockerfile to run `alembic upgrade head` before spawning the main thread.
3.  Remove hardcoded passwords from `config.py` and enforce database connection variables through environmental injection.

---

## User Validation Readiness

### 1. Current State
The database logs OIE suggestions and user action triggers (accepted, overridden, ignored, etc.) via the `AISuggestionEvent` table. However, there is no visualization of these metrics, no way for users to report bugs or misclassifications from the UI, and no external telemetry integrations.

### 2. Evidence from Repository
*   **AISuggestionEvent Table**: Model definitions in [models.py](file:///d:/Desktop/New_Autism/backend/app/models/models.py#L232-L261) capture detailed metrics (processing speed, relevance rank, similarity scores, selected vs. suggested domain mappings).
*   **Missing Feedback Interfaces**: Examining frontend views under `frontend/src/app/observations` shows that when the OIE provides domain suggestions, there is no thumbs up/down validation interface or feedback input form for caregivers or clinicians to submit accuracy remarks.
*   **No Telemetry Services**: There are no analytical libraries, logging aggregators, or error-reporting packages (e.g., `Sentry`, `PostHog`, or `Mixpanel`) initialized in either the Next.js frontend or the FastAPI backend configurations.

### 3. Missing Components
*   **User Feedback Endpoint**: Backend controllers to receive validation remarks (e.g. `POST /api/ai/suggestions/{event_id}/feedback`).
*   **Feedback UI elements**: Simple verification icons (👍/👎) adjacent to suggested developmental domains and milestone matches.
*   **Developer Dashboard / Accuracy KPI Page**: An internal analytics page displaying live performance parameters (e.g. OIE acceptance rate, common milestone classification overrides, average retrieval latency).

### 4. Risk Level
> [!NOTE]
> **MEDIUM**
> Without structured user feedback collection, developers cannot isolate real-world classification errors or measure the performance of the Hinglish terminology mappings post-deployment.

### 5. Recommended Action
1.  Expose a feedback submission schema and update `ai_suggestion_events` with qualitative rating columns.
2.  Add basic rating buttons to the OIE suggestion display blocks in the Next.js front-end.
3.  Configure a simple admin analytics page in the frontend showing cumulative OIE performance indices (total matches, acceptance percentage, top overridden milestones).

---

## Admin / Demo Mode

### 1. Current State
While Neurolens includes pre-seeded databases to demonstrate features, it lacks a dedicated admin panel, scenario simulators, or database management options within the UI.

### 2. Evidence from Repository
*   **Seed Dependency**: The `backend/app/database/seed.py` file creates excellent preloaded cases, such as "Demo Child A" (who has developmental logs and linked milestones) and "Demo Child B" (configured with developmental concern observations).
*   **Lack of UI Trigger**: There is no button, admin route, or configuration page in `frontend/src/app` that triggers db updates or showcases clinician views.
*   **Static Client Selection**: The landing page list in [page.tsx](file:///d:/Desktop/New_Autism/frontend/src/app/page.tsx) lists the preloaded child profiles directly from the `/children` endpoint, but offers no scenario guidelines explaining the diagnostic differences between Child A (typical development) and Child B (possible delay concerns).

### 3. Missing Components
*   **Scenario Configurator UI**: Visual selectors to load specific diagnostic scenarios (e.g., "Reset to Typical Speech Development", "Reset to Developmental Concerns").
*   **Database Seeding Endpoint**: An administrative endpoint allowing secure remote database resets.
*   **Visual Admin Panel**: A dashboard showing backend system health, SQLite file dimensions, total registered child profiles, and active observations.

### 4. Risk Level
> [!NOTE]
> **LOW-MEDIUM**
> In the absence of an easy-to-use reset mechanism, judges testing the application might corrupt the state of preloaded profiles and have no way to restore them without terminal CLI access.

### 5. Recommended Action
1.  Implement a secure administrative API controller `/api/admin/reseed` in the backend.
2.  Add a floating "Scenario Simulator" panel in the frontend layout to allow judges to toggle between developmental delay and typical progress scenarios.
3.  Add explicit documentation in the UI header explaining the purpose of Child A vs. Child B.

---

## Security Review

### 1. Current State
The system currently lacks essential security controls. It features no authentication checking, has hardcoded database passwords in version control, lacks input sanitization rules, and exposes all children's data via unrestricted API calls.

### 2. Evidence from Repository
*   **Unauthenticated API Routes**: Standard FastAPI routers loaded in [router.py](file:///d:/Desktop/New_Autism/backend/app/api/router.py) lack dependencies checking authorization credentials.
*   **Exposed Secret Credentials**: Secret variables are stored directly in source control:
    *   [docker-compose.yml](file:///d:/Desktop/New_Autism/docker-compose.yml#L29): Database connection secrets are committed in cleartext.
    *   [config.py](file:///d:/Desktop/New_Autism/backend/app/core/config.py#L12): Default postgres passwords are stored as code strings.
*   **Lack of Object Validation**: Endpoint functions (e.g., `update_child`, `delete_observation`, `create_report`) execute database mutations directly using client-supplied IDs without verifying relationship ownership.
*   **No Input Sanitization**: Text observations are stored directly as string fields in `Observation.body` and rendered inside React elements without filtering.

### 3. Missing Components
*   **Authentication Middleware**: Standard token verification wrappers at the API gateway layer.
*   **Environment Secret Vault**: Secret environment management (e.g. AWS Secrets Manager, Doppler, or hidden `.env` files omitted from Git).
*   **XSS Input Sanitization**: Input validation schemas that escape HTML/JavaScript tags before persisting database entities.
*   **Strict CORS Policy**: Production configurations restricting CORS origins to approved frontend domains instead of dev wildcards.

### 4. Risk Level
> [!CAUTION]
> **CRITICAL**
> Exposing child-specific developmental data without validation checks, security boundaries, or credential verification violates standard data protection practices and represents a major risk for deployment.

### 5. Recommended Action
1.  Introduce JWT-based auth dependencies to block unauthenticated access.
2.  Add ownership validations verifying that the requesting parent possesses a link to the queried child.
3.  Configure input sanitization (e.g., using `bleach` in python) for qualitative observations.
4.  Remove all cleartext secrets from Git tracking and load database variables via environment values.

---

## Submission Readiness Score

### AI Readiness
*   **Score**: **9 / 10**
*   **Rationale**: The OIE is highly optimized. The Hinglish normalizations, glossary layers, and milestone keywords have been refined based on thorough error audits. The retrieval accuracy meets the target specifications (Top-1: 80.62%, Top-3: 96.25%, Domain: 86.88%) and is supported by 48+ passing test suites.

### Product Readiness
*   **Score**: **4 / 10**
*   **Rationale**: The core layout is functional for logging and compilation. However, it operates as a single-user system. Missing flows such as credentials, account creation, role differentiation, clinician profiles, and data isolation must be implemented before launch.

### Deployment Readiness
*   **Score**: **5 / 10**
*   **Rationale**: While Docker files and compose configurations exist, the frontend image runs in development mode, database migrations are manual (no automated Alembic upgrade scripts in the entrypoint), and secrets are hardcoded in source files.

### Judge Readiness
*   **Score**: **6 / 10**
*   **Rationale**: The database seed script populates excellent test cases (Child A & B). However, judges cannot reset the database state or toggle scenario paths from the UI. Furthermore, the clinician workspace is not visually distinct from the parent interface.
