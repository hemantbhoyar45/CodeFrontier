#!/bin/sh
set -eu

: "${KNOWBRIDGE_DB_USER:?KNOWBRIDGE_DB_USER must be set}"
: "${KNOWBRIDGE_DB_PASSWORD:?KNOWBRIDGE_DB_PASSWORD must be set}"

psql -v ON_ERROR_STOP=1 \
    --username "$POSTGRES_USER" \
    --dbname "$POSTGRES_DB" \
    --set=app_user="$KNOWBRIDGE_DB_USER" \
    --set=app_password="$KNOWBRIDGE_DB_PASSWORD" <<'SQL'
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'app_user', :'app_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'app_user')
\gexec
CREATE EXTENSION IF NOT EXISTS vector;
SELECT format('GRANT CONNECT ON DATABASE %I TO %I', current_database(), :'app_user')
\gexec
GRANT USAGE, CREATE ON SCHEMA public TO :"app_user";
SQL
