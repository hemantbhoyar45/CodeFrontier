from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.modules.projects.models import Project, ProjectMember
from backend.app.modules.users.models import User


class ProjectRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self,
        tenant_id: UUID,
        *,
        status_filter: str | None,
        sort_by: str,
        descending: bool,
        limit: int,
        offset: int,
        user_id: UUID,
        organization_role: str,
    ) -> tuple[list[Project], int]:
        sort_column = {"name": Project.name, "created_at": Project.created_at}[sort_by]
        conditions = [
            Project.tenant_id == tenant_id, Project.deleted_at.is_(None)
        ]
        if status_filter is not None:
            conditions.append(Project.status == status_filter)
        if organization_role not in {"owner", "admin"}:
            conditions.append(
                Project.id.in_(
                    select(ProjectMember.project_id).where(
                        ProjectMember.tenant_id == tenant_id,
                        ProjectMember.user_id == user_id,
                        ProjectMember.deleted_at.is_(None),
                    )
                )
            )
        total = self.db.scalar(select(func.count(Project.id)).where(*conditions)) or 0
        query = (
            select(Project)
            .where(*conditions)
            .order_by(sort_column.desc() if descending else sort_column.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(query)), total

    def get(self, tenant_id: UUID, project_id: UUID) -> Project | None:
        return self.db.scalar(
            select(Project).where(
                Project.tenant_id == tenant_id,
                Project.id == project_id,
                Project.deleted_at.is_(None),
            )
        )

    def members(self, tenant_id: UUID, project_id: UUID, *, limit: int, offset: int):
        conditions = (
            ProjectMember.tenant_id == tenant_id,
            ProjectMember.project_id == project_id,
            ProjectMember.deleted_at.is_(None),
            User.deleted_at.is_(None),
        )
        total = self.db.scalar(
            select(func.count(ProjectMember.id))
            .join(User, User.id == ProjectMember.user_id)
            .where(*conditions)
        ) or 0
        members = list(
            self.db.execute(
                select(ProjectMember, User)
                .join(User, User.id == ProjectMember.user_id)
                .where(*conditions)
                .order_by(User.email)
                .offset(offset)
                .limit(limit)
            )
        )
        return members, total
