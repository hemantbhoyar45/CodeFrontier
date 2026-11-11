from uuid import UUID

from sqlalchemy import JSON, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base, SoftDeleteMixin, TimestampedUUIDMixin


class Integration(TimestampedUUIDMixin, SoftDeleteMixin, Base):
    __tablename__ = "integrations"
    __table_args__ = (Index("ix_integrations_tenant_provider", "tenant_id", "provider"),)

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="disconnected")
    config: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    credential_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
