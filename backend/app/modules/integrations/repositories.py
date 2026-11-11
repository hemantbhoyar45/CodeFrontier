from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.modules.integrations.models import Integration


class IntegrationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, tenant_id: UUID, *, provider: str | None, limit: int, offset: int):
        conditions = (
            Integration.tenant_id == tenant_id,
            Integration.deleted_at.is_(None),
        )
        if provider:
            conditions += (Integration.provider == provider,)
        total = self.db.scalar(select(func.count(Integration.id)).where(*conditions)) or 0
        integrations = list(
            self.db.scalars(
                select(Integration)
                .where(*conditions)
                .order_by(Integration.provider)
                .offset(offset)
                .limit(limit)
            )
        )
        return integrations, total

    def add(self, integration: Integration):
        self.db.add(integration)
        self.db.commit()
        return integration
