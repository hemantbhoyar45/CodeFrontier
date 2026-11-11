from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.modules.knowledge.models import KnowledgeItem


class KnowledgeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self,
        tenant_id: UUID,
        project_id: UUID,
        *,
        kind: str | None,
        sort_by: str,
        descending: bool,
        limit: int,
        offset: int,
    ):
        conditions = [
            KnowledgeItem.tenant_id == tenant_id,
            KnowledgeItem.project_id == project_id,
            KnowledgeItem.deleted_at.is_(None),
        ]
        if kind is not None:
            conditions.append(KnowledgeItem.kind == kind)
        sort_column = {"title": KnowledgeItem.title, "created_at": KnowledgeItem.created_at}[
            sort_by
        ]
        total = self.db.scalar(select(func.count(KnowledgeItem.id)).where(*conditions)) or 0
        query = (
            select(KnowledgeItem)
            .where(*conditions)
            .order_by(sort_column.desc() if descending else sort_column.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(query)), total

    def get(self, tenant_id: UUID, item_id: UUID) -> KnowledgeItem | None:
        return self.db.scalar(
            select(KnowledgeItem).where(
                KnowledgeItem.tenant_id == tenant_id,
                KnowledgeItem.id == item_id,
                KnowledgeItem.deleted_at.is_(None),
            )
        )
