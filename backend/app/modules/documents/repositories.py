from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.modules.documents.models import Document


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self,
        tenant_id: UUID,
        project_id: UUID,
        *,
        status_filter: str | None,
        sort_by: str,
        descending: bool,
        limit: int,
        offset: int,
    ) -> tuple[list[Document], int]:
        conditions = [
            Document.tenant_id == tenant_id,
            Document.project_id == project_id,
            Document.deleted_at.is_(None),
        ]
        if status_filter is not None:
            conditions.append(Document.status == status_filter)
        sort_column = {"title": Document.title, "created_at": Document.created_at}[sort_by]
        total = self.db.scalar(select(func.count(Document.id)).where(*conditions)) or 0
        query = (
            select(Document)
            .where(*conditions)
            .order_by(sort_column.desc() if descending else sort_column.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(query)), total

    def get(self, tenant_id: UUID, document_id: UUID) -> Document | None:
        return self.db.scalar(
            select(Document).where(
                Document.tenant_id == tenant_id,
                Document.id == document_id,
                Document.deleted_at.is_(None),
            )
        )
