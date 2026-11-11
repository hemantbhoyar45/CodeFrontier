from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.modules.auth.dependencies import (
    get_current_user,
    require_organization_member,
)
from backend.app.modules.knowledge.schemas import KnowledgeCreate, KnowledgeRead, KnowledgeUpdate
from backend.app.modules.knowledge.services import KnowledgeService
from backend.app.modules.organizations.models import OrganizationMember
from backend.app.modules.projects.authorization import require_project_access
from backend.app.modules.users.models import User
from backend.app.schemas import api_response

router = APIRouter(
    prefix="/organizations/{organization_id}/projects/{project_id}/knowledge",
    tags=["knowledge"],
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
def list_knowledge(
    organization_id: UUID,
    project_id: UUID,
    kind: str | None = Query(default=None, max_length=48),
    sort_by: str = Query(default="created_at", pattern="^(created_at|title)$"),
    descending: bool = True,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    _require_project(
        db, organization_id, project_id, current_user.id, membership.role
    )
    items, total = KnowledgeService(db).repository.list(
        organization_id,
        project_id,
        kind=kind,
        sort_by=sort_by,
        descending=descending,
        limit=limit,
        offset=offset,
    )
    return api_response(
        [KnowledgeRead.model_validate(item).model_dump(mode="json") for item in items],
        meta={"count": total, "limit": limit, "offset": offset},
    )


@router.post("", status_code=201)
def create_knowledge(
    organization_id: UUID,
    project_id: UUID,
    payload: KnowledgeCreate,
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
    item = KnowledgeService(db).create(
        organization_id,
        project_id,
        current_user.id,
        title=payload.title,
        content=payload.content,
        kind=payload.kind,
    )
    return api_response(KnowledgeRead.model_validate(item).model_dump(mode="json"))


@router.get("/{item_id}")
def get_knowledge(
    organization_id: UUID,
    item_id: UUID,
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    item = KnowledgeService(db).repository.get(organization_id, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    require_project_access(
        db,
        organization_id,
        item.project_id,
        current_user.id,
        organization_role=membership.role,
    )
    return api_response(KnowledgeRead.model_validate(item).model_dump(mode="json"))


@router.patch("/{item_id}")
def update_knowledge(
    organization_id: UUID,
    item_id: UUID,
    payload: KnowledgeUpdate,
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    if membership.role not in {"owner", "admin", "member"}:
        raise HTTPException(status_code=403, detail="Insufficient organization permissions")
    values = payload.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(status_code=422, detail="At least one field must be provided")
    item = KnowledgeService(db).repository.get(organization_id, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    require_project_access(
        db,
        organization_id,
        item.project_id,
        current_user.id,
        organization_role=membership.role,
        write=True,
    )
    item = KnowledgeService(db).update(
        organization_id, item_id, values, actor_id=current_user.id
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    return api_response(KnowledgeRead.model_validate(item).model_dump(mode="json"))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge(
    organization_id: UUID,
    item_id: UUID,
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> None:
    if membership.role not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Organization administrator role required")
    item = KnowledgeService(db).repository.get(organization_id, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    require_project_access(
        db,
        organization_id,
        item.project_id,
        current_user.id,
        organization_role=membership.role,
    )
    if not KnowledgeService(db).delete(
        organization_id, item_id, actor_id=current_user.id
    ):
        raise HTTPException(status_code=404, detail="Knowledge item not found")
