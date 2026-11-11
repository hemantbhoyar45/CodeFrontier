from uuid import UUID

from backend.app.modules.dashboard.repositories import DashboardRepository
from backend.app.modules.dashboard.schemas import (
    DashboardActivity,
    DashboardProject,
    DashboardSummary,
)


class DashboardService:
    def __init__(self, db) -> None:
        self.repository = DashboardRepository(db)

    def summary(
        self, tenant_id: UUID, user_id: UUID, organization_role: str
    ) -> DashboardSummary:
        rows = self.repository.projects(tenant_id, user_id, organization_role)
        project_ids = [row.id for row in rows]
        counts = self.repository.counts(tenant_id, project_ids)
        projects = [
            DashboardProject(
                id=row.id,
                name=row.name,
                description=row.description,
                status=row.status,
                created_by=row.created_by,
                owner_name=row.owner_name,
                updated_at=row.updated_at,
                team_members=row.member_count,
                knowledge_items=row.knowledge_count,
                knowledge_completeness=100 if row.knowledge_count else 0,
            )
            for row in rows
        ]
        total_projects = len(projects)
        covered_projects = sum(bool(project.knowledge_items) for project in projects)
        score = round(covered_projects / total_projects * 100) if total_projects else 0
        status = "strong" if score >= 75 else "building" if score >= 40 else "needs_attention"
        activity = [
            DashboardActivity(
                id=row.id,
                action=row.action,
                resource_type=row.resource_type,
                resource_id=row.resource_id,
                actor_name=row.actor_name,
                created_at=row.created_at,
            )
            for row in self.repository.recent_activity(tenant_id)
        ]
        return DashboardSummary(
            total_projects=total_projects,
            active_projects=sum(project.status == "active" for project in projects),
            knowledge_items=counts["knowledge_items"],
            pending_reviews=counts["pending_reviews"],
            open_blockers=counts["open_blockers"],
            generated_handovers=counts["generated_handovers"],
            continuity_score=score,
            continuity_status=status,
            projects=projects,
            recent_activity=activity,
        )
