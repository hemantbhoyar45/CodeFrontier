# KNOWBRIDGE

KNOWBRIDGE is an AI-powered knowledge continuity and handover platform. This
repository contains a Next.js frontend, modular FastAPI backend, separate
Celery worker, and Docker Compose development stack.

## Repository layout

```text
frontend/       Next.js application
backend/        FastAPI application, database setup, and Alembic migrations
workers/        Celery application and background tasks
infrastructure/ Reserved for deployable infrastructure configuration
docs/           Architecture, setup, and environment documentation
scripts/        Local development and verification helpers
```

## Quick start (Docker)

Requirements: Docker Desktop with Compose v2.

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Open the frontend at <http://localhost:3000>, API docs at
<http://localhost:8000/docs>, and API readiness at
<http://localhost:8000/api/v1/health/ready>.

For the development override with hot reload:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

See [docs/setup.md](docs/setup.md) for standalone startup, tests, and shutdown.
The checked-in `.env.example` includes local-only placeholder credentials; do
not reuse them outside local development.

## Backend capabilities

The backend exposes authentication, organization and member management,
tenant-scoped project and membership CRUD, document metadata, knowledge items,
handover reports, and audit-log APIs under `/api/v1`. SQLAlchemy models cover
the wider project knowledge, evidence, review, integration, and background-job
schema. PostgreSQL migrations enable pgvector and row-level tenant policies;
Redis provides shared rate limiting. See [docs/architecture.md](docs/architecture.md)
and [docs/setup.md](docs/setup.md) for details.
