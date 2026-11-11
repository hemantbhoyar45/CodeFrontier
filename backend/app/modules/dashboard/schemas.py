from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DashboardProject(BaseModel):
    id: UUID
    name: str
    description: str | None
    status: str
    created_by: UUID
    owner_name: str | None
    updated_at: datetime
    team_members: int
    knowledge_items: int
    knowledge_completeness: int


class DashboardActivity(BaseModel):
    id: UUID
    action: str
    resource_type: str
    resource_id: UUID | None
    actor_name: str | None
    created_at: datetime


class DashboardSummary(BaseModel):
    total_projects: int
    active_projects: int
    knowledge_items: int
    pending_reviews: int
    open_blockers: int
    generated_handovers: int
    continuity_score: int
    continuity_status: str
    projects: list[DashboardProject]
    recent_activity: list[DashboardActivity]
