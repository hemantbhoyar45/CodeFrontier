from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.modules.auth.dependencies import (
    get_current_user,
    require_organization_member,
)
from backend.app.modules.handovers.repositories import HandoverRepository
from backend.app.modules.handovers.schemas import HandoverCreate, HandoverRead
from backend.app.modules.handovers.services import HandoverService
from backend.app.modules.organizations.models import OrganizationMember
from backend.app.modules.projects.authorization import require_project_access
from backend.app.modules.users.models import User
from backend.app.schemas import api_response

router = APIRouter(
    prefix="/organizations/{organization_id}/projects/{project_id}/handovers",
    tags=["handovers"],
)


def _require_project(
    db: Session,
    tenant_id: UUID,
    project_id: UUID,
    user_id: UUID,
    organization_role: str,
    *,
    write: bool = False,
) -> None:
    require_project_access(
        db,
        tenant_id,
        project_id,
        user_id,
        organization_role=organization_role,
        write=write,
    )


@router.get("")
def list_handovers(
    organization_id: UUID,
    project_id: UUID,
    sort_by: str = Query(default="created_at", pattern="^(created_at|title)$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    _require_project(
        db, organization_id, project_id, current_user.id, membership.role
    )
    reports, total = HandoverRepository(db).list(
        organization_id, project_id, sort_by=sort_by, limit=limit, offset=offset
    )
    return api_response(
        [HandoverRead.model_validate(item).model_dump(mode="json") for item in reports],
        meta={"count": total, "limit": limit, "offset": offset},
    )


@router.post("", status_code=201)
def create_handover(
    organization_id: UUID,
    project_id: UUID,
    payload: HandoverCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    membership: OrganizationMember = Depends(require_organization_member),
) -> dict[str, object]:
    _require_project(
        db,
        organization_id,
        project_id,
        current_user.id,
        membership.role,
        write=True,
    )
    report = HandoverService(db).create(
        organization_id,
        project_id,
        current_user.id,
        title=payload.title,
        recipient_role=payload.recipient_role,
        content=payload.content,
    )
    return api_response(HandoverRead.model_validate(report).model_dump(mode="json"))


@router.get("/{report_id}")
def get_handover(
    organization_id: UUID,
    report_id: UUID,
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    report = HandoverRepository(db).get(organization_id, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Handover report not found")
    require_project_access(
        db,
        organization_id,
        report.project_id,
        current_user.id,
        organization_role=membership.role,
    )
    return api_response(HandoverRead.model_validate(report).model_dump(mode="json"))
