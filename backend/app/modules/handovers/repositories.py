from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.modules.handovers.models import HandoverReport


class HandoverRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self, tenant_id: UUID, project_id: UUID, *, sort_by: str, limit: int, offset: int
    ):
        conditions = (
            HandoverReport.tenant_id == tenant_id,
            HandoverReport.project_id == project_id,
            HandoverReport.deleted_at.is_(None),
        )
        total = self.db.scalar(select(func.count(HandoverReport.id)).where(*conditions)) or 0
        sort_column = {"title": HandoverReport.title, "created_at": HandoverReport.created_at}[
            sort_by
        ]
        reports = list(
            self.db.scalars(
                select(HandoverReport)
                .where(*conditions)
                .order_by(sort_column.desc())
                .offset(offset)
                .limit(limit)
            )
        )
        return reports, total

    def get(self, tenant_id: UUID, report_id: UUID):
        return self.db.scalar(
            select(HandoverReport).where(
                HandoverReport.tenant_id == tenant_id,
                HandoverReport.id == report_id,
                HandoverReport.deleted_at.is_(None),
            )
        )
