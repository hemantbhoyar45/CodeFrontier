import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.organizations.models import Organization, OrganizationInvitation
from backend.app.modules.organizations.models import OrganizationMember
from backend.app.modules.users.models import User

INVITATION_TTL = timedelta(days=7)


def hash_invitation_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class InvitationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        tenant_id: UUID,
        actor_id: UUID,
        *,
        email: str,
        role: str,
    ) -> tuple[OrganizationInvitation, str]:
        token = secrets.token_urlsafe(32)
        invitation = OrganizationInvitation(
            tenant_id=tenant_id,
            invited_email=email.strip().lower(),
            role=role,
            token_hash=hash_invitation_token(token),
            expires_at=datetime.now(UTC) + INVITATION_TTL,
            invited_by=actor_id,
        )
        self.db.add(invitation)
        self.db.commit()
        return invitation, token

    def preview(self, token: str):
        invitation = self.db.scalar(
            select(OrganizationInvitation).where(
                OrganizationInvitation.token_hash == hash_invitation_token(token),
                OrganizationInvitation.accepted_at.is_(None),
                OrganizationInvitation.revoked_at.is_(None),
                OrganizationInvitation.expires_at > datetime.now(UTC),
            )
        )
        if invitation is None:
            return None
        organization = self.db.get(Organization, invitation.tenant_id)
        if organization is None or organization.deleted_at is not None:
            return None
        return invitation, organization

    def accept(self, token: str, user: User):
        invitation = self.db.scalar(
            select(OrganizationInvitation).where(
                OrganizationInvitation.token_hash == hash_invitation_token(token),
                OrganizationInvitation.accepted_at.is_(None),
                OrganizationInvitation.revoked_at.is_(None),
                OrganizationInvitation.expires_at > datetime.now(UTC),
            )
        )
        if invitation is None:
            return None
        if invitation.invited_email != user.email:
            return "email_mismatch"
        membership = self.db.scalar(
            select(OrganizationMember).where(
                OrganizationMember.tenant_id == invitation.tenant_id,
                OrganizationMember.user_id == user.id,
            )
        )
        if membership is not None:
            if membership.deleted_at is None:
                return "already_member"
            membership.deleted_at = None
            membership.role = invitation.role
        else:
            self.db.add(
                OrganizationMember(
                    tenant_id=invitation.tenant_id,
                    organization_id=invitation.tenant_id,
                    user_id=user.id,
                    role=invitation.role,
                )
            )
        invitation.accepted_at = datetime.now(UTC)
        self.db.commit()
        return invitation
