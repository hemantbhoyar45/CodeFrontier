from uuid import UUID

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base, SoftDeleteMixin, TimestampedUUIDMixin


class Organization(TimestampedUUIDMixin, SoftDeleteMixin, Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class OrganizationMember(TimestampedUUIDMixin, SoftDeleteMixin, Base):
    __tablename__ = "organization_members"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_org_member_user"),
        UniqueConstraint("tenant_id", "user_id", name="uq_org_member_tenant_user"),
        CheckConstraint("tenant_id = organization_id", name="ck_org_member_tenant_matches_org"),
        Index("ix_org_members_tenant_user", "tenant_id", "user_id"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    organization_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )
    role: Mapped[str] = mapped_column(String(40), nullable=False, default="member")


class Role(TimestampedUUIDMixin, Base):
    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_roles_tenant_name"),)

    tenant_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Permission(TimestampedUUIDMixin, Base):
    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)


class RolePermission(TimestampedUUIDMixin, Base):
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
        ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        Index("ix_role_permissions_role", "role_id"),
    )

    role_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    permission_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)


class OrganizationInvitation(TimestampedUUIDMixin, Base):
    __tablename__ = "organization_invitations"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_org_invitation_token_hash"),
        Index("ix_org_invitations_tenant_email", "tenant_id", "invited_email"),
        CheckConstraint("role IN ('admin', 'member', 'viewer')", name="ck_invitation_role"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    invited_email: Mapped[str] = mapped_column(String(320), nullable=False)
    role: Mapped[str] = mapped_column(String(40), nullable=False, default="member")
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    invited_by: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
