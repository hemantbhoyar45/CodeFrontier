from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base, SoftDeleteMixin, TimestampedUUIDMixin


class Project(TimestampedUUIDMixin, SoftDeleteMixin, Base):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_projects_tenant_id"),
        Index("ix_projects_tenant_status", "tenant_id", "status"),
        ForeignKeyConstraint(
            ["tenant_id", "created_by"],
            ["organization_members.tenant_id", "organization_members.user_id"],
            ondelete="RESTRICT",
            name="fk_project_creator_tenant_member",
        ),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    created_by: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ProjectMember(TimestampedUUIDMixin, SoftDeleteMixin, Base):
    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("tenant_id", "project_id", "user_id", name="uq_project_member_user"),
        ForeignKeyConstraint(
            ["tenant_id", "project_id"],
            ["projects.tenant_id", "projects.id"],
            ondelete="CASCADE",
            name="fk_project_member_project_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "user_id"],
            ["organization_members.tenant_id", "organization_members.user_id"],
            ondelete="CASCADE",
            name="fk_project_member_org_member_tenant",
        ),
        Index("ix_project_members_tenant_user", "tenant_id", "user_id"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(40), nullable=False, default="member")
