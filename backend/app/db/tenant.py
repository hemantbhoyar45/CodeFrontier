from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


def set_tenant_context(db: Session, tenant_id: UUID) -> None:
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        db.execute(
            text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
            {"tenant_id": str(tenant_id)},
        )


def set_user_context(db: Session, user_id: UUID) -> None:
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        db.execute(
            text("SELECT set_config('app.user_id', :user_id, true)"),
            {"user_id": str(user_id)},
        )


def set_invitation_context(db: Session, token: str) -> None:
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        from backend.app.modules.organizations.invitations import hash_invitation_token

        db.execute(
            text("SELECT set_config('app.invitation_token_hash', :token_hash, true)"),
            {"token_hash": hash_invitation_token(token)},
        )


def set_password_reset_context(db: Session, token_hash: str) -> None:
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        db.execute(
            text("SELECT set_config('app.password_reset_token_hash', :token_hash, true)"),
            {"token_hash": token_hash},
        )
