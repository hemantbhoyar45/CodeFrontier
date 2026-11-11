from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.audit.services import AuditService
from backend.app.modules.organizations.models import OrganizationMember
from backend.app.modules.projects.models import Project, ProjectMember
from backend.app.modules.projects.repositories import ProjectRepository


class ProjectService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = ProjectRepository(db)

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
    ):
        if sort_by not in {"name", "created_at"}:
            raise ValueError("Unsupported project sort field")
        return self.repository.list(
            tenant_id,
            status_filter=status_filter,
            sort_by=sort_by,
            descending=descending,
            limit=limit,
            offset=offset,
            user_id=user_id,
            organization_role=organization_role,
        )

    def create(self, tenant_id: UUID, user_id: UUID, *, name: str, description: str | None):
        project = Project(
            tenant_id=tenant_id,
            name=name.strip(),
            description=description,
            created_by=user_id,
        )
        self.db.add(project)
        self.db.flush()
        self.db.add(
            ProjectMember(
                tenant_id=tenant_id,
                project_id=project.id,
                user_id=user_id,
                role="admin",
            )
        )
        AuditService(self.db).record(
            tenant_id,
            user_id,
            action="project.created",
            resource_type="project",
            resource_id=project.id,
        )
        self.db.commit()
        return project

    def update(
        self, tenant_id: UUID, project_id: UUID, values: dict[str, object], *, actor_id: UUID
    ):
        project = self.repository.get(tenant_id, project_id)
        if project is None:
            return None
        for field, value in values.items():
            setattr(project, field, value)
        AuditService(self.db).record(
            tenant_id,
            actor_id,
            action="project.updated",
            resource_type="project",
            resource_id=project.id,
            details={"fields": sorted(values)},
        )
        self.db.commit()
        return project

    def delete(self, tenant_id: UUID, project_id: UUID, *, actor_id: UUID) -> bool:
        project = self.repository.get(tenant_id, project_id)
        if project is None:
            return False
        project.deleted_at = datetime.now(UTC)
        AuditService(self.db).record(
            tenant_id,
            actor_id,
            action="project.deleted",
            resource_type="project",
            resource_id=project.id,
        )
        self.db.commit()
        return True

    def add_member(
        self, tenant_id: UUID, project_id: UUID, user_id: UUID, role: str, *, actor_id: UUID
    ):
        project = self.repository.get(tenant_id, project_id)
        if project is None:
            return "project_missing"
        organization_member = self.db.scalar(
            select(OrganizationMember).where(
                OrganizationMember.tenant_id == tenant_id,
                OrganizationMember.user_id == user_id,
                OrganizationMember.deleted_at.is_(None),
            )
        )
        if organization_member is None:
            return "user_missing"
        member = ProjectMember(
            tenant_id=tenant_id, project_id=project_id, user_id=user_id, role=role
        )
        self.db.add(member)
        AuditService(self.db).record(
            tenant_id,
            actor_id,
            action="project.member_added",
            resource_type="project_member",
            resource_id=member.id,
            details={"user_id": str(user_id), "role": role},
        )
        self.db.commit()
        return member

    def remove_member(
        self, tenant_id: UUID, project_id: UUID, user_id: UUID, *, actor_id: UUID
    ) -> bool:
        member = self.db.scalar(
            select(ProjectMember).where(
                ProjectMember.tenant_id == tenant_id,
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
                ProjectMember.deleted_at.is_(None),
            )
        )
        if member is None:
            return False
        member.deleted_at = datetime.now(UTC)
        AuditService(self.db).record(
            tenant_id,
            actor_id,
            action="project.member_removed",
            resource_type="project_member",
            resource_id=member.id,
            details={"user_id": str(user_id)},
        )
        self.db.commit()
        return True
