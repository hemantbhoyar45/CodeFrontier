from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.reviews.models import ReviewRequest


class ReviewRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_project(self, tenant_id: UUID, project_id: UUID):
        return list(
            self.db.scalars(
                select(ReviewRequest)
                .where(
                    ReviewRequest.tenant_id == tenant_id,
                    ReviewRequest.project_id == project_id,
                )
                .order_by(ReviewRequest.created_at.desc())
            )
        )

    def list_for_organization(self, tenant_id: UUID, *, status_filter: str | None):
        query = select(ReviewRequest).where(ReviewRequest.tenant_id == tenant_id)
        if status_filter is not None:
            query = query.where(ReviewRequest.status == status_filter)
        return list(self.db.scalars(query.order_by(ReviewRequest.created_at.desc())))

    def get(self, tenant_id: UUID, review_id: UUID):
        return self.db.scalar(
            select(ReviewRequest).where(
                ReviewRequest.tenant_id == tenant_id,
                ReviewRequest.id == review_id,
            )
        )
