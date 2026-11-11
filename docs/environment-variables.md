# Environment variables

Copy the root `.env.example` to `.env` for local Compose and standalone backend
development. Copy `frontend/.env.example` to `frontend/.env.local` for Next.js
development. These example files contain no real credentials.

| Variable | Consumer | Purpose |
|---|---|---|
| `POSTGRES_DB` | Compose/PostgreSQL | Local database name. |
| `POSTGRES_USER` | Compose/PostgreSQL | Local database user. |
| `POSTGRES_PASSWORD` | Compose/PostgreSQL | Local-only placeholder in `.env.example`; replace for any shared environment. |
| `KNOWBRIDGE_DB_USER` | PostgreSQL init/API/worker | Non-superuser application role used by the API and worker. |
| `KNOWBRIDGE_DB_PASSWORD` | PostgreSQL init/API/worker | Local-only runtime database password; use a secret manager outside local development. |
| `KNOWBRIDGE_DATABASE_URL` | API, Alembic, worker | SQLAlchemy Psycopg connection URL. Use `localhost` for host processes; Compose supplies an internal service URL. |
| `KNOWBRIDGE_REDIS_URL` | API settings and worker | Redis broker/result backend URL. Use `localhost` for host processes; Compose supplies the internal service URL. |
| `KNOWBRIDGE_ENVIRONMENT` | Backend and worker | `development`, `test`, or `production`. |
| `KNOWBRIDGE_LOG_LEVEL` | Backend | Python logging level, such as `INFO` or `DEBUG`. |
| `KNOWBRIDGE_JWT_SECRET_KEY` | Backend | At least 32 characters; the development fallback is rejected in production. |
| `KNOWBRIDGE_ACCESS_TOKEN_EXPIRE_MINUTES` | Backend | JWT access-token lifetime, from 1 to 1440 minutes. |
| `KNOWBRIDGE_RATE_LIMIT_PER_MINUTE` | Backend | Shared Redis-backed per-IP API request limit. |
| `KNOWBRIDGE_AUTH_RATE_LIMIT_PER_MINUTE` | Backend | Stricter shared Redis-backed per-IP limit for authentication routes. |
| `KNOWBRIDGE_CORS_ORIGINS` | Backend | JSON array of allowed browser origins. Do not use wildcard origins with credentials. |
| `NEXT_PUBLIC_API_BASE_URL` | Frontend | Public API base URL, compiled into the browser bundle. Never put secrets in `NEXT_PUBLIC_*` variables. |

Compose replaces database and Redis hostnames with its service names and
constructs the connection URL from the PostgreSQL variables. If a password
contains URL-reserved characters, URL-encode it in the connection URL or use
separately managed deployment secrets and connection configuration. Never
commit `.env`, production secrets, tokens, or credentials.

Compose initializes pgvector and a non-superuser application role for a fresh
PostgreSQL data volume, then uses that role for API traffic and migrations.
Tenant RLS policies are forced; do not run the API as a PostgreSQL superuser
or a role with `BYPASSRLS`. The init script only runs on a fresh volume.
Existing local volumes need the runtime role and pgvector extension
provisioned once by a database administrator.
