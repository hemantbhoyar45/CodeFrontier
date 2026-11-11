# KNOWBRIDGE backend architecture

## Deployment shape

The system is a modular monolith with independently started processes:

- **Frontend:** Next.js App Router application.
- **API:** FastAPI application; JSON REST endpoints are versioned under `/api/v1`.
- **Worker:** Celery process, sharing backend configuration and dependencies.
- **PostgreSQL:** Relational persistence with a named Docker volume.
- **Redis:** Celery broker and result backend with a named Docker volume.

Docker Compose wires these services together for local development. The API
and worker can also be started separately when their dependencies are available.
`backend/Dockerfile` and `frontend/Dockerfile` have production runtime targets;
`docker-compose.dev.yml` selects development targets with source mounts.

## Backend modules and APIs

The API is exposed as `backend.app.main:app`; versioned routes are included from
`backend.app.api.v1.router`. Runtime settings are validated by Pydantic Settings
and are shared by the API, Alembic, and Celery. SQLAlchemy uses synchronous
sessions with PostgreSQL's Psycopg 3 driver. Alembic is configured in
`backend/alembic.ini`. Domain modules separate models, schemas, routes,
services, repositories, and tests for authentication, organizations, users,
projects, documents, knowledge, evidence, reviews, handovers, integrations,
and audit/background jobs.

Authentication uses signed JWT access tokens and scrypt password hashes.
Project, document, knowledge, and handover APIs require organization
membership; project-level membership grants scoped access, with viewer roles
read-only. Mutations append tenant-scoped audit events. Successful domain
responses use a `data` envelope and paginated lists add `meta`; errors use a
consistent `error` envelope.

Tenant-owned rows carry `tenant_id`. Repositories filter by that tenant and
services validate membership before writes. The initial Alembic migration
enables PostgreSQL row-level security with transaction-local
`app.tenant_id`/`app.user_id` context and `FORCE ROW LEVEL SECURITY`.
Application database credentials must be non-superuser and must not have
`BYPASSRLS`; compose provisions a dedicated runtime role for fresh volumes.
Embeddings use pgvector's 1536-dimensional vector type and an HNSW cosine index.

Redis provides atomic, shared per-IP fixed-window rate limits with a stricter
authentication limit. The API returns HTTP 503 if Redis is unavailable rather
than silently disabling the limiter. `/api/v1/health/live` checks process
liveness; `/api/v1/health/ready` checks PostgreSQL and Redis and returns HTTP
503 when either dependency is unavailable.

## Worker boundaries

The worker starts with `workers.celery_app:celery_app`. Tasks live in
`workers.tasks`; `knowbridge.sample.add` is a deterministic smoke-test task.
Slow ingestion and AI workloads belong in workers rather than API request
handlers as product modules are introduced.

## Frontend boundaries

The frontend uses the App Router under `frontend/src/app`. Shared UI primitives
belong in `frontend/src/components/ui`, application components in
`frontend/src/components`, and API access in `frontend/src/lib/api`. The API
base URL is configured with `NEXT_PUBLIC_API_BASE_URL`; because this variable
is public and embedded in the browser bundle, it must never contain a secret.

## Security and evolution

Imported source content must be treated as untrusted, and AI-generated claims
must retain source evidence and require review for consequential use. Keep
migrations as immutable revisions; evolve the metadata through new Alembic
revisions rather than editing the initial schema after deployment.

Do not expose database or Redis ports in production deployments. Configure
production secrets through the deployment platform, restrict CORS to trusted
origins, and terminate TLS at the deployment edge.
