from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.modules.audit.models import AuditLog
from backend.app.modules.handovers.models import HandoverReport
from backend.app.modules.knowledge.models import Blocker, KnowledgeItem
from backend.app.modules.organizations.models import OrganizationMember
from backend.app.modules.projects.models import Project, ProjectMember
from backend.app.modules.reviews.models import ReviewRequest
from backend.app.modules.users.models import User


class DashboardRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def projects(self, tenant_id: UUID, user_id: UUID, organization_role: str):
        knowledge_counts = (
            select(KnowledgeItem.project_id, func.count(KnowledgeItem.id).label("knowledge_count"))
            .where(
                KnowledgeItem.tenant_id == tenant_id,
                KnowledgeItem.deleted_at.is_(None),
            )
            .group_by(KnowledgeItem.project_id)
            .subquery()
        )
        member_counts = (
            select(ProjectMember.project_id, func.count(ProjectMember.id).label("member_count"))
            .where(
                ProjectMember.tenant_id == tenant_id,
                ProjectMember.deleted_at.is_(None),
            )
            .group_by(ProjectMember.project_id)
            .subquery()
        )
        query = (
            select(
                Project.id,
                Project.name,
                Project.description,
                Project.status,
                Project.created_by,
                User.full_name.label("owner_name"),
                Project.updated_at,
                func.coalesce(member_counts.c.member_count, 0).label("member_count"),
                func.coalesce(knowledge_counts.c.knowledge_count, 0).label("knowledge_count"),
            )
            .join(User, User.id == Project.created_by)
            .outerjoin(member_counts, member_counts.c.project_id == Project.id)
            .outerjoin(knowledge_counts, knowledge_counts.c.project_id == Project.id)
            .where(Project.tenant_id == tenant_id, Project.deleted_at.is_(None))
            .order_by(Project.updated_at.desc())
        )
        if organization_role not in {"owner", "admin"}:
            query = query.where(
                Project.id.in_(
                    select(ProjectMember.project_id).where(
                        ProjectMember.tenant_id == tenant_id,
                        ProjectMember.user_id == user_id,
                        ProjectMember.deleted_at.is_(None),
                    )
                )
            )
        return list(self.db.execute(query))

    def counts(self, tenant_id: UUID, project_ids: list[UUID]) -> dict[str, int]:
        if not project_ids:
            return {
                "knowledge_items": 0,
                "pending_reviews": 0,
                "open_blockers": 0,
                "generated_handovers": 0,
            }
        statements = {
            "knowledge_items": select(func.count(KnowledgeItem.id)).where(
                KnowledgeItem.tenant_id == tenant_id,
                KnowledgeItem.project_id.in_(project_ids),
                KnowledgeItem.deleted_at.is_(None),
            ),
            "pending_reviews": select(func.count(ReviewRequest.id)).where(
                ReviewRequest.tenant_id == tenant_id,
                ReviewRequest.project_id.in_(project_ids),
                ReviewRequest.status == "pending",
            ),
            "open_blockers": select(func.count(Blocker.id)).where(
                Blocker.tenant_id == tenant_id,
                Blocker.project_id.in_(project_ids),
                Blocker.status == "open",
                Blocker.deleted_at.is_(None),
            ),
            "generated_handovers": select(func.count(HandoverReport.id)).where(
                HandoverReport.tenant_id == tenant_id,
                HandoverReport.project_id.in_(project_ids),
                HandoverReport.status == "generated",
                HandoverReport.deleted_at.is_(None),
            ),
        }
        return {
            name: self.db.scalar(statement) or 0
            for name, statement in statements.items()
        }

    def recent_activity(self, tenant_id: UUID, *, limit: int = 8):
        return list(
            self.db.execute(
                select(
                    AuditLog.id,
                    AuditLog.action,
                    AuditLog.resource_type,
                    AuditLog.resource_id,
                    User.full_name.label("actor_name"),
                    AuditLog.created_at,
                )
                .outerjoin(User, User.id == AuditLog.actor_id)
                .where(AuditLog.tenant_id == tenant_id)
                .order_by(AuditLog.created_at.desc())
                .limit(limit)
            )
        )
