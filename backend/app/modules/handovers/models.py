from uuid import UUID

from sqlalchemy import JSON, ForeignKey, ForeignKeyConstraint, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base, SoftDeleteMixin, TimestampedUUIDMixin


class HandoverReport(TimestampedUUIDMixin, SoftDeleteMixin, Base):
    __tablename__ = "handover_reports"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "project_id"],
            ["projects.tenant_id", "projects.id"],
            ondelete="CASCADE",
            name="fk_handovers_project_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "created_by"],
            ["organization_members.tenant_id", "organization_members.user_id"],
            ondelete="RESTRICT",
            name="fk_handover_creator_tenant_member",
        ),
        Index("ix_handovers_tenant_project", "tenant_id", "project_id"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    created_by: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    recipient_role: Mapped[str | None] = mapped_column(String(120), nullable=True)
    content: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
