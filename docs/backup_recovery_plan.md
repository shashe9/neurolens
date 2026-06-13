# Neurolens Data Backup & Recovery Plan

This document outlines the backup parameters, restore guides, and disaster recovery plan for Neurolens across local deployment and cloud instances.

---

## 🗄️ 1. Backup Strategy

### Local Host Database Persistence
*   **Method**: File Copy / Volume Mapping `[VERIFIED]`
*   **Details**: The SQLite database file `neurolens.db` is written directly to the host filesystem. During container execution, docker volumes map the database files, ensuring data persists across container shutdowns.

### Cloud Database Backups
*   **Method**: Automated Snapshots `[PLANNED]`
*   **Details**: If deployed to AWS RDS, database snapshots will execute daily during low-traffic windows (e.g. 02:00 AM UTC).
*   **Retention Period**: `[PLANNED]` 30 days.

---

## 🚀 2. Disaster Recovery Scenarios

Every recovery duration is an **`[ESTIMATED]`** target:

| Disaster Scenario | Recovery Strategy | Status | Recovery Point Objective (RPO) | Recovery Time Objective (RTO) |
| :--- | :--- | :---: | :---: | :---: |
| **Accidental Child Profile Deletion** | Neurolens uses **soft deletion** (archives children using a `deleted_at` field). Profiles can be un-archived via the dashboard UI with zero data loss. | `[VERIFIED]` | 0 Minutes | < 1 Minute |
| **Local Database File Corruption** | Stop database services, replace `neurolens.db` with a copy from the local filesystem backup directory, and restart services. | `[ESTIMATED]` | < 24 Hours | < 10 Minutes |
| **Cloud Database Loss / Outage** | Spin up a new AWS RDS PostgreSQL instance, import the latest RDS snapshot, update FastAPI container env connections, and restart the ECS task cluster. | `[ESTIMATED]` | < 24 Hours | < 2 Hours |
| **Incorrect Migration Failure** | Run `alembic downgrade -1` or `alembic downgrade base` to revert schema updates, then restore the database file to pre-migration state. | `[VERIFIED]` | 0 Minutes | < 5 Minutes |

---

## 🔧 3. Verified Local Restore Guide

To manually restore a local SQLite database file to a clean state:
1.  **Stop containers**:
    ```bash
    docker-compose down
    ```
2.  **Restore DB File**: Copy your backup database file over `backend/neurolens.db`.
3.  **Relaunch and verify**:
    ```bash
    docker-compose up -d
    ```
    *(The startup sequence will check schema version structures automatically and keep existing data intact).*
