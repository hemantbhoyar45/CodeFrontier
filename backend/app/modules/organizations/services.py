from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.tenant import set_tenant_context
from backend.app.modules.audit.services import AuditService
from backend.app.modules.organizations.models import Organization, OrganizationMember
from backend.app.modules.organizations.repositories import OrganizationRepository
from backend.app.modules.users.models import User


class OrganizationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = OrganizationRepository(db)

    def list_for_user(
        self, user_id, *, search, sort_by, descending, limit, offset
    ):
        if sort_by not in {"name", "created_at"}:
            raise ValueError("Unsupported organization sort field")
        return self.repository.for_user(
            user_id,
            search=search,
            sort_by=sort_by,
            descending=descending,
            limit=limit,
            offset=offset,
        )

    def create(self, user_id, *, name: str):
        slug = f"{_slugify(name)}-{str(uuid4())[:8]}"
        organization = Organization(name=name.strip(), slug=slug)
        self.db.add(organization)
        self.db.flush()
        set_tenant_context(self.db, organization.id)
        self.db.add(
            OrganizationMember(
                tenant_id=organization.id,
                organization_id=organization.id,
                user_id=user_id,
                role="owner",
            )
        )
        AuditService(self.db).record(
            organization.id,
            user_id,
            action="organization.created",
            resource_type="organization",
            resource_id=organization.id,
        )
        self.db.commit()
        return organization

    def add_member(self, organization_id, *, email: str, role: str, actor_id):
        user = self.db.scalar(
            select(User).where(User.email == email.strip().lower(), User.deleted_at.is_(None))
        )
        if user is None:
            return None
        membership = OrganizationMember(
            tenant_id=organization_id,
            organization_id=organization_id,
            user_id=user.id,
            role=role,
        )
        self.db.add(membership)
        AuditService(self.db).record(
            organization_id,
            actor_id,
            action="organization.member_added",
            resource_type="organization_member",
            resource_id=membership.id,
            details={"role": role},
        )
        self.db.commit()
        return membership, user


def _slugify(value: str) -> str:
    slug = "-".join(value.lower().split())
    return "".join(char for char in slug if char.isalnum() or char == "-").strip("-") or "org"
