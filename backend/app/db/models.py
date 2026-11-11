"""Import all mapped domain classes so SQLAlchemy and Alembic see full metadata."""

from backend.app.modules.audit.models import AuditLog, BackgroundJob
from backend.app.modules.auth.models import PasswordReset
from backend.app.modules.documents.models import Document, DocumentVersion
from backend.app.modules.evidence.models import EvidenceReference
from backend.app.modules.handovers.models import HandoverReport
from backend.app.modules.integrations.models import Integration
from backend.app.modules.knowledge.models import (
    Blocker,
    Decision,
    Dependency,
    KnowledgeItem,
    KnowledgeSource,
    Task,
)
from backend.app.modules.organizations.models import (
    Organization,
    OrganizationInvitation,
    OrganizationMember,
    Permission,
    Role,
    RolePermission,
)
from backend.app.modules.projects.models import Project, ProjectMember
from backend.app.modules.reviews.models import ReviewRequest
from backend.app.modules.users.models import User

__all__ = [
    "AuditLog",
    "BackgroundJob",
    "Blocker",
    "Decision",
    "Dependency",
    "Document",
    "DocumentVersion",
    "EvidenceReference",
    "HandoverReport",
    "Integration",
    "KnowledgeItem",
    "KnowledgeSource",
    "Organization",
    "OrganizationInvitation",
    "OrganizationMember",
    "PasswordReset",
    "Permission",
    "Project",
    "ProjectMember",
    "ReviewRequest",
    "Role",
    "RolePermission",
    "User",
    "Task",
]
