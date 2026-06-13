# Neurolens Production Deployment Plan

This document details the configuration requirements, steps, and orchestration architecture for deploying Neurolens locally or in a production cloud environment.

---

## 🐋 1. Local Containerized Orchestration (Docker Compose)

Neurolens is fully dockerized and ready for local development, demo review, or clinic-server execution. The deployment runs three services:
1.  **neurolens_db**: A PostgreSQL 15 relational database container.
2.  **neurolens_backend**: A FastAPI service running the OIE engine (expose port 8000).
3.  **neurolens_frontend**: A Next.js 16/React application (expose port 3000).

### Launching the Application
To build and start the entire application suite locally:
```bash
docker-compose up --build -d
```

### Automatic Startup Sequence
During container boot, the `neurolens_backend` runs [entrypoint.sh](file:///d:/Desktop/New_Autism/backend/entrypoint.sh):
1.  Verifies relational database connection using Python's SQLAlchemy engine configuration.
2.  Applies database schema migrations up to the current head using Alembic (`alembic upgrade head`).
3.  Executes `app.database.seed` to seed demo users, scenario-specific profiles, and clinical trial records.
4.  Launches Uvicorn on port 8000.

---

## ☁️ 2. Cloud Infrastructure Architecture

For production deployments, the following AWS cloud architecture is recommended:

```mermaid
graph LR
    User([Caregiver / Clinician]) -->|HTTPS| Route53[AWS Route 53]
    Route53 --> ALB[AWS Application Load Balancer]
    ALB -->|Port 80/443| ECS[AWS ECS Fargate Cluster]
    ECS -->|Backend Container| API[FastAPI API]
    ECS -->|Frontend Container| Next[Next.js SSR Server]
    API -->|Read/Write| RDS[(AWS RDS PostgreSQL)]
    Next -->|Fetch Data| API
    API -->|Store Reports| S3[(AWS S3 Bucket)]
```

### Component Details
*   **SSL/TLS Termination**: Managed at the Application Load Balancer (ALB) via AWS Certificate Manager (ACM).
*   **Compute Instance**: AWS ECS Fargate task with `1 vCPU` and `2GB RAM` (minimizes costs while providing enough overhead for memory-resident SentenceTransformer embeddings).
*   **Database Isolation**: RDS PostgreSQL instance restricted to the private subnet, accessible only by security group rule from the ECS container task.

---

## 🔐 3. Production Environment Checklist

Before transitioning the application to production, populate `.env` with the following variables:

```ini
# Environment Profile
ENVIRONMENT=production

# Database Configuration (AWS RDS Endpoint)
DATABASE_URL=postgresql://db_user:secure_prod_pass@rds-endpoint:5432/neurolens_prod

# JWT Credentials (MUST be long, secure random string)
JWT_SECRET_KEY=a_highly_secure_cryptographic_random_string_xyz_123

# CORS Origin Control (Only allow production domains)
BACKEND_CORS_ORIGINS=["https://neurolens.yourdomain.com"]
```

---

## 🩺 4. Health Checks & Maintenance

*   **API Healthcheck**: The backend provides a `/health` endpoint validating database connectivity.
*   **DB Backups**: Configure AWS RDS automated daily snapshots retained for 30 days to protect caregiver and clinician clinical records.
*   **Monitoring**: Configure container resource alerts on AWS CloudWatch to monitor CPU/Memory load during observation index generation.
