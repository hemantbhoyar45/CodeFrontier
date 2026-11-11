# Development setup

## Requirements

- Docker Desktop and Docker Compose v2 for the complete stack.
- Node.js 22 and npm for standalone frontend development.
- Python 3.12+ for standalone backend and worker development.
- PostgreSQL and Redis for running the backend and worker outside Docker.

## Complete stack

From the repository root in PowerShell:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Use the development override for frontend/API hot reload:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

The API applies Alembic migrations before serving requests. PostgreSQL uses
pgvector and a dedicated non-superuser runtime role; Redis supplies the shared
rate limiter and Celery broker. The runtime-role init script only runs on a
fresh database volume. For an existing volume, ask a PostgreSQL administrator
to provision the app role and vector extension before starting this version.
Services have
container health checks; PostgreSQL data persists in the `postgres_data` named
volume and Redis data in `redis_data`.

Stop the stack with `Ctrl+C`, then run `docker compose down`. To intentionally
remove local database and Redis data as well, use
`docker compose down --volumes` (this permanently deletes those local volumes).

## Start services independently

Start PostgreSQL and Redis first, for example with
`docker compose up -d postgres redis`. Copy `.env.example` to `.env`; its
database and Redis URLs use `localhost` for processes running on the host.

Backend, from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements-dev.txt
python -m alembic -c backend/alembic.ini upgrade head
uvicorn backend.app.main:app --reload
```

Frontend, in a second terminal:

```powershell
Copy-Item frontend/.env.example frontend/.env.local
Set-Location frontend
npm ci
npm run dev
```

Worker, in a third terminal:

```powershell
python -m celery -A workers.celery_app:celery_app worker --loglevel=INFO
```

The standalone backend and worker share `KNOWBRIDGE_DATABASE_URL` and
`KNOWBRIDGE_REDIS_URL` from the root `.env`. Use the non-superuser application
role in `KNOWBRIDGE_DATABASE_URL`; RLS is not effective for superuser or
`BYPASSRLS` credentials. Configure `KNOWBRIDGE_JWT_SECRET_KEY` with a
deployment-generated secret in production.

## Verification

```powershell
python -m pytest backend/tests workers
python -m ruff check backend workers
Set-Location frontend
npm run lint
npm run build
```

With the full stack running and backend development dependencies installed, run
`python scripts/smoke_test.py` from the repository root to verify frontend/API
HTTP responses and a Celery task round trip.

With the stack running, check:

- `http://localhost:3000` — frontend
- `http://localhost:8000/docs` — OpenAPI documentation
- `http://localhost:8000/api/v1/health/live` — process liveness
- `http://localhost:8000/api/v1/health/ready` — PostgreSQL and Redis readiness

The API docs at `/docs` list the authentication, organizations/users,
projects/memberships, document metadata, knowledge, handover, and audit routes.
