from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.modules.audit.models import AuditLog, BackgroundJob


class AuditRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_logs(self, tenant_id: UUID, *, limit: int, offset: int):
        total = self.db.scalar(
            select(func.count(AuditLog.id)).where(AuditLog.tenant_id == tenant_id)
        ) or 0
        records = list(
            self.db.scalars(
                select(AuditLog)
                .where(AuditLog.tenant_id == tenant_id)
                .order_by(AuditLog.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
        )
        return records, total

    def add_log(self, tenant_id: UUID, actor_id: UUID | None, *, action: str, resource_type: str,
                resource_id: UUID | None, details: dict[str, object]):
        log = AuditLog(
            tenant_id=tenant_id,
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
        )
        self.db.add(log)
        self.db.flush()
        return log


class BackgroundJobRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, tenant_id: UUID, job_id: UUID):
        return self.db.scalar(
            select(BackgroundJob).where(
                BackgroundJob.tenant_id == tenant_id, BackgroundJob.id == job_id
            )
        )
