"""Create the initial KNOWBRIDGE product schema and tenant policies.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-11-10
"""

from collections.abc import Sequence

from alembic import op

import backend.app.db.models  # noqa: F401
from backend.app.db.base import Base

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    connection = op.get_bind()
    if connection.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    Base.metadata.create_all(bind=connection)

    if connection.dialect.name == "postgresql":
        for table in Base.metadata.sorted_tables:
            tenant_column = table.columns.get("tenant_id")
            if tenant_column is None:
                continue
            table_name = table.name
            policy_name = f"tenant_isolation_{table_name}"
            tenant_condition = (
                "tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid"
            )
            op.execute(f'ALTER TABLE "{table_name}" ENABLE ROW LEVEL SECURITY')
            op.execute(f'ALTER TABLE "{table_name}" FORCE ROW LEVEL SECURITY')
            op.execute(
                f'CREATE POLICY "{policy_name}" ON "{table_name}" '
                f"USING ({tenant_condition}) WITH CHECK ({tenant_condition})"
            )
            if table_name == "organization_members":
                op.execute(
                    'CREATE POLICY "organization_members_self_read" '
                    'ON "organization_members" FOR SELECT '
                    "USING (user_id = NULLIF(current_setting('app.user_id', true), '')::uuid)"
                )
            elif table_name == "roles":
                op.execute(
                    'CREATE POLICY "roles_global_read" ON "roles" FOR SELECT '
                    "USING (tenant_id IS NULL)"
                )
            elif table_name == "organization_invitations":
                op.execute(
                    'CREATE POLICY "organization_invitations_token_lookup" '
                    'ON "organization_invitations" FOR SELECT '
                    "USING (token_hash = "
                    "NULLIF(current_setting('app.invitation_token_hash', true), ''))"
                )
        op.execute('ALTER TABLE "password_resets" ENABLE ROW LEVEL SECURITY')
        op.execute('ALTER TABLE "password_resets" FORCE ROW LEVEL SECURITY')
        op.execute(
            'CREATE POLICY "password_resets_token_access" ON "password_resets" '
            "USING (token_hash = "
            "NULLIF(current_setting('app.password_reset_token_hash', true), '')) "
            "WITH CHECK (token_hash = "
            "NULLIF(current_setting('app.password_reset_token_hash', true), ''))"
        )


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
