from uuid import UUID

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, ForeignKeyConstraint, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base, TimestampedUUIDMixin


class ReviewRequest(TimestampedUUIDMixin, Base):
    __tablename__ = "review_requests"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "project_id"],
            ["projects.tenant_id", "projects.id"],
            ondelete="CASCADE",
            name="fk_review_requests_project_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "requested_by"],
            ["organization_members.tenant_id", "organization_members.user_id"],
            ondelete="RESTRICT",
            name="fk_review_requester_tenant_member",
        ),
        Index("ix_review_requests_tenant_project_status", "tenant_id", "project_id", "status"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    requested_by: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    target_type: Mapped[str] = mapped_column(String(48), nullable=False)
    target_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
