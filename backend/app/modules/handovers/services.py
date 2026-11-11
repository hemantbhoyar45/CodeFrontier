from uuid import UUID

from backend.app.modules.audit.services import AuditService
from backend.app.modules.handovers.models import HandoverReport
from backend.app.modules.handovers.repositories import HandoverRepository


class HandoverService:
    def __init__(self, db) -> None:
        self.db = db
        self.repository = HandoverRepository(db)

    def create(
        self,
        tenant_id: UUID,
        project_id: UUID,
        user_id: UUID,
        *,
        title: str,
        recipient_role: str | None,
        content: dict[str, object],
    ):
        report = HandoverReport(
            tenant_id=tenant_id,
            project_id=project_id,
            created_by=user_id,
            title=title.strip(),
            recipient_role=recipient_role,
            content=content,
        )
        self.db.add(report)
        self.db.flush()
        AuditService(self.db).record(
            tenant_id,
            user_id,
            action="handover.created",
            resource_type="handover_report",
            resource_id=report.id,
        )
        self.db.commit()
        return report
