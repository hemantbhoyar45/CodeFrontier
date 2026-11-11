from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.modules.audit.services import AuditService
from backend.app.modules.reviews.models import ReviewRequest
from backend.app.modules.reviews.repositories import ReviewRepository


class ReviewService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = ReviewRepository(db)

    def create(
        self,
        tenant_id: UUID,
        project_id: UUID,
        user_id: UUID,
        *,
        target_type: str,
        target_id: UUID,
        comment: str | None,
    ) -> ReviewRequest:
        review = ReviewRequest(
            tenant_id=tenant_id,
            project_id=project_id,
            requested_by=user_id,
            target_type=target_type,
            target_id=target_id,
            comment=comment,
        )
        self.db.add(review)
        self.db.flush()
        AuditService(self.db).record(
            tenant_id,
            user_id,
            action="review.requested",
            resource_type="review_request",
            resource_id=review.id,
        )
        self.db.commit()
        return review

    def decide(self, tenant_id: UUID, review_id: UUID, user_id: UUID, *, status: str, comment):
        review = self.repository.get(tenant_id, review_id)
        if review is None or review.status != "pending":
            return None
        review.status = status
        review.comment = comment
        review.reviewed_by = user_id
        review.reviewed_at = datetime.now(UTC)
        AuditService(self.db).record(
            tenant_id,
            user_id,
            action=f"review.{status}",
            resource_type="review_request",
            resource_id=review.id,
        )
        self.db.commit()
        return review
