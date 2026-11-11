from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.db.tenant import set_tenant_context
from backend.app.modules.audit.services import AuditService
from backend.app.modules.auth.repositories import UserRepository
from backend.app.modules.auth.security import hash_password, verify_password
from backend.app.modules.organizations.models import Organization, OrganizationMember
from backend.app.modules.users.models import User


class AuthenticationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register(
        self, *, email: str, full_name: str, password: str, organization_name: str
    ) -> tuple[User, Organization]:
        user = self.users.add(
            User(email=email, full_name=full_name.strip(), password_hash=hash_password(password))
        )
        organization = Organization(
            name=organization_name.strip(),
            slug=f"{_slugify(organization_name)}-{str(uuid4())[:8]}",
        )
        self.db.add(organization)
        self.db.flush()
        set_tenant_context(self.db, organization.id)
        self.db.add(
            OrganizationMember(
                tenant_id=organization.id,
                organization_id=organization.id,
                user_id=user.id,
                role="owner",
            )
        )
        AuditService(self.db).record(
            organization.id,
            user.id,
            action="organization.created",
            resource_type="organization",
            resource_id=organization.id,
        )
        self.db.commit()
        return user, organization

    def authenticate(self, *, email: str, password: str) -> User | None:
        user = self.users.by_email(email)
        if user is None or not user.is_active or not verify_password(password, user.password_hash):
            return None
        return user


def _slugify(value: str) -> str:
    slug = "-".join(value.lower().split())
    return "".join(char for char in slug if char.isalnum() or char == "-").strip("-") or "org"
