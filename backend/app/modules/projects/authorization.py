from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.projects.models import Project, ProjectMember


def require_project_access(
    db: Session,
    tenant_id: UUID,
    project_id: UUID,
    user_id: UUID,
    *,
    organization_role: str,
    write: bool = False,
) -> str:
    project = db.scalar(
        select(Project.id).where(
            Project.tenant_id == tenant_id,
            Project.id == project_id,
            Project.deleted_at.is_(None),
        )
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if organization_role in {"owner", "admin"}:
        return "admin"
    member = db.scalar(
        select(ProjectMember).where(
            ProjectMember.tenant_id == tenant_id,
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.deleted_at.is_(None),
        )
    )
    if member is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if write and member.role == "viewer":
        raise HTTPException(status_code=403, detail="Project write permission required")
    return member.role
