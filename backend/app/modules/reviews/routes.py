from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.modules.auth.dependencies import (
    get_current_user,
    require_organization_member,
)
from backend.app.modules.organizations.models import OrganizationMember
from backend.app.modules.projects.authorization import require_project_access
from backend.app.modules.projects.models import ProjectMember
from backend.app.modules.reviews.schemas import (
    ReviewDecision,
    ReviewRead,
    ReviewRequestCreate,
)
from backend.app.modules.reviews.services import ReviewService
from backend.app.modules.users.models import User
from backend.app.schemas import api_response

router = APIRouter(tags=["reviews"])


@router.get("/organizations/{organization_id}/reviews")
def list_reviews(
    organization_id: UUID,
    status_filter: str | None = Query(default=None, alias="status", max_length=32),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    records = ReviewService(db).repository.list_for_organization(
        organization_id, status_filter=status_filter
    )
    if membership.role not in {"owner", "admin"}:
        project_ids = set(
            db.scalars(
                select(ProjectMember.project_id).where(
                    ProjectMember.tenant_id == organization_id,
                    ProjectMember.user_id == current_user.id,
                    ProjectMember.deleted_at.is_(None),
                )
            )
        )
        records = [record for record in records if record.project_id in project_ids]
    total = len(records)
    selected = records[offset : offset + limit]
    return api_response(
        [ReviewRead.model_validate(record).model_dump(mode="json") for record in selected],
        meta={"count": total, "limit": limit, "offset": offset},
    )


@router.post(
    "/organizations/{organization_id}/projects/{project_id}/reviews", status_code=201
)
def request_review(
    organization_id: UUID,
    project_id: UUID,
    payload: ReviewRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    membership: OrganizationMember = Depends(require_organization_member),
) -> dict[str, object]:
    require_project_access(
        db,
        organization_id,
        project_id,
        current_user.id,
        organization_role=membership.role,
        write=True,
    )
    if payload.project_id != project_id:
        raise HTTPException(status_code=422, detail="Review project does not match request path")
    review = ReviewService(db).create(
        organization_id,
        project_id,
        current_user.id,
        target_type=payload.target_type,
        target_id=payload.target_id,
        comment=payload.comment,
    )
    return api_response(ReviewRead.model_validate(review).model_dump(mode="json"))


@router.post("/organizations/{organization_id}/reviews/{review_id}/decision")
def decide_review(
    organization_id: UUID,
    review_id: UUID,
    payload: ReviewDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    membership: OrganizationMember = Depends(require_organization_member),
) -> dict[str, object]:
    review = ReviewService(db).repository.get(organization_id, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review request not found")
    require_project_access(
        db,
        organization_id,
        review.project_id,
        current_user.id,
        organization_role=membership.role,
    )
    updated = ReviewService(db).decide(
        organization_id,
        review_id,
        current_user.id,
        status=payload.status,
        comment=payload.comment,
    )
    if updated is None:
        raise HTTPException(status_code=409, detail="Review request has already been resolved")
    return api_response(ReviewRead.model_validate(updated).model_dump(mode="json"))
