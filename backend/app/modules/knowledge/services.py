from datetime import UTC, datetime
from uuid import UUID

from backend.app.modules.audit.services import AuditService
from backend.app.modules.knowledge.models import KnowledgeItem
from backend.app.modules.knowledge.repositories import KnowledgeRepository


class KnowledgeService:
    def __init__(self, db) -> None:
        self.db = db
        self.repository = KnowledgeRepository(db)

    def create(
        self,
        tenant_id: UUID,
        project_id: UUID,
        user_id: UUID,
        *,
        title: str,
        content: str,
        kind: str,
    ):
        item = KnowledgeItem(
            tenant_id=tenant_id,
            project_id=project_id,
            created_by=user_id,
            title=title.strip(),
            content=content,
            kind=kind,
        )
        self.db.add(item)
        self.db.flush()
        AuditService(self.db).record(
            tenant_id,
            user_id,
            action="knowledge_item.created",
            resource_type="knowledge_item",
            resource_id=item.id,
        )
        self.db.commit()
        return item

    def update(
        self, tenant_id: UUID, item_id: UUID, values: dict[str, object], *, actor_id: UUID
    ):
        item = self.repository.get(tenant_id, item_id)
        if item is None:
            return None
        for field, value in values.items():
            setattr(item, field, value)
        AuditService(self.db).record(
            tenant_id,
            actor_id,
            action="knowledge_item.updated",
            resource_type="knowledge_item",
            resource_id=item.id,
            details={"fields": sorted(values)},
        )
        self.db.commit()
        return item

    def delete(self, tenant_id: UUID, item_id: UUID, *, actor_id: UUID) -> bool:
        item = self.repository.get(tenant_id, item_id)
        if item is None:
            return False
        item.deleted_at = datetime.now(UTC)
        AuditService(self.db).record(
            tenant_id,
            actor_id,
            action="knowledge_item.deleted",
            resource_type="knowledge_item",
            resource_id=item.id,
        )
        self.db.commit()
        return True
