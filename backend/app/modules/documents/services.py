from datetime import UTC, datetime
from uuid import UUID

from backend.app.modules.audit.services import AuditService
from backend.app.modules.documents.models import Document
from backend.app.modules.documents.repositories import DocumentRepository


class DocumentService:
    def __init__(self, db) -> None:
        self.db = db
        self.repository = DocumentRepository(db)

    def create(self, tenant_id: UUID, project_id: UUID, user_id: UUID, *, title: str, **metadata):
        document = Document(
            tenant_id=tenant_id,
            project_id=project_id,
            created_by=user_id,
            title=title.strip(),
            **metadata,
        )
        self.db.add(document)
        self.db.flush()
        AuditService(self.db).record(
            tenant_id,
            user_id,
            action="document.created",
            resource_type="document",
            resource_id=document.id,
        )
        self.db.commit()
        return document

    def update(
        self,
        tenant_id: UUID,
        document_id: UUID,
        values: dict[str, object],
        *,
        actor_id: UUID,
    ):
        document = self.repository.get(tenant_id, document_id)
        if document is None:
            return None
        for field, value in values.items():
            setattr(document, field, value)
        AuditService(self.db).record(
            tenant_id,
            actor_id,
            action="document.updated",
            resource_type="document",
            resource_id=document.id,
            details={"fields": sorted(values)},
        )
        self.db.commit()
        return document

    def delete(self, tenant_id: UUID, document_id: UUID, *, actor_id: UUID) -> bool:
        document = self.repository.get(tenant_id, document_id)
        if document is None:
            return False
        document.deleted_at = datetime.now(UTC)
        AuditService(self.db).record(
            tenant_id,
            actor_id,
            action="document.deleted",
            resource_type="document",
            resource_id=document.id,
        )
        self.db.commit()
        return True
