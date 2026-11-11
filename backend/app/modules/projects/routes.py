from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.modules.auth.dependencies import (
    get_current_user,
    require_organization_member,
)
from backend.app.modules.organizations.models import OrganizationMember
from backend.app.modules.projects.authorization import require_project_access
from backend.app.modules.projects.repositories import ProjectRepository
from backend.app.modules.projects.schemas import (
    ProjectCreate,
    ProjectMemberCreate,
    ProjectMemberRead,
    ProjectRead,
    ProjectUpdate,
)
from backend.app.modules.projects.services import ProjectService
from backend.app.modules.users.models import User
from backend.app.schemas import api_response

router = APIRouter(prefix="/organizations/{organization_id}/projects", tags=["projects"])


@router.get("")
def list_projects(
    organization_id: UUID,
    status_filter: str | None = Query(default=None, alias="status", max_length=32),
    sort_by: str = Query(default="created_at", pattern="^(created_at|name)$"),
    descending: bool = True,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    projects, total = ProjectService(db).list(
        organization_id,
        status_filter=status_filter,
        sort_by=sort_by,
        descending=descending,
        limit=limit,
        offset=offset,
        user_id=current_user.id,
        organization_role=membership.role,
    )
    return api_response(
        [ProjectRead.model_validate(item).model_dump(mode="json") for item in projects],
        meta={"count": total, "limit": limit, "offset": offset},
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_project(
    organization_id: UUID,
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    membership: OrganizationMember = Depends(require_organization_member),
) -> dict[str, object]:
    if membership.role not in {"owner", "admin", "member"}:
        raise HTTPException(status_code=403, detail="Insufficient organization permissions")
    project = ProjectService(db).create(
        organization_id,
        current_user.id,
        name=payload.name,
        description=payload.description,
    )
    return api_response(ProjectRead.model_validate(project).model_dump(mode="json"))


@router.get("/{project_id}")
def get_project(
    organization_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    require_project_access(
        db,
        organization_id,
        project_id,
        current_user.id,
        organization_role=membership.role,
    )
    project = ProjectService(db).repository.get(organization_id, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return api_response(ProjectRead.model_validate(project).model_dump(mode="json"))


@router.patch("/{project_id}")
def update_project(
    organization_id: UUID,
    project_id: UUID,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    if membership.role not in {"owner", "admin", "member"}:
        raise HTTPException(status_code=403, detail="Insufficient organization permissions")
    require_project_access(
        db,
        organization_id,
        project_id,
        current_user.id,
        organization_role=membership.role,
        write=True,
    )
    values = payload.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(status_code=422, detail="At least one field must be provided")
    project = ProjectService(db).update(
        organization_id, project_id, values, actor_id=current_user.id
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return api_response(ProjectRead.model_validate(project).model_dump(mode="json"))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    organization_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> None:
    if membership.role not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Organization administrator role required")
    require_project_access(
        db,
        organization_id,
        project_id,
        current_user.id,
        organization_role=membership.role,
    )
    if not ProjectService(db).delete(
        organization_id, project_id, actor_id=current_user.id
    ):
        raise HTTPException(status_code=404, detail="Project not found")


@router.get("/{project_id}/members")
def list_project_members(
    organization_id: UUID,
    project_id: UUID,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    require_project_access(
        db,
        organization_id,
        project_id,
        current_user.id,
        organization_role=membership.role,
    )
    members, total = ProjectRepository(db).members(
        organization_id, project_id, limit=limit, offset=offset
    )
    return api_response(
        [
            ProjectMemberRead(
                id=member.id,
                user_id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=member.role,
            ).model_dump(mode="json")
            for member, user in members
        ],
        meta={"count": total, "limit": limit, "offset": offset},
    )


@router.post("/{project_id}/members", status_code=status.HTTP_201_CREATED)
def add_project_member(
    organization_id: UUID,
    project_id: UUID,
    payload: ProjectMemberCreate,
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    if membership.role not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Organization administrator role required")
    try:
        result = ProjectService(db).add_member(
            organization_id,
            project_id,
            payload.user_id,
            payload.role,
            actor_id=current_user.id,
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="User is already a project member") from exc
    if result == "project_missing":
        raise HTTPException(status_code=404, detail="Project not found")
    if result == "user_missing":
        raise HTTPException(status_code=404, detail="Organization user not found")
    return api_response({"id": str(result.id), "user_id": str(result.user_id), "role": result.role})


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_project_member(
    organization_id: UUID,
    project_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> None:
    if membership.role not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Organization administrator role required")
    service = ProjectService(db)
    if service.repository.get(organization_id, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if not service.remove_member(
        organization_id, project_id, user_id, actor_id=current_user.id
    ):
        raise HTTPException(status_code=404, detail="Project member not found")
