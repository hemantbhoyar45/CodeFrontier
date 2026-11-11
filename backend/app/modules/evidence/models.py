from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base, TimestampedUUIDMixin


class EvidenceReference(TimestampedUUIDMixin, Base):
    __tablename__ = "evidence_references"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "project_id"],
            ["projects.tenant_id", "projects.id"],
            ondelete="CASCADE",
            name="fk_evidence_project_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "document_id"],
            ["documents.tenant_id", "documents.id"],
            ondelete="CASCADE",
            name="fk_evidence_document_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "document_version_id"],
            ["document_versions.tenant_id", "document_versions.id"],
            ondelete="CASCADE",
            name="fk_evidence_document_version_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "knowledge_source_id"],
            ["knowledge_sources.tenant_id", "knowledge_sources.id"],
            ondelete="CASCADE",
            name="fk_evidence_knowledge_source_tenant",
        ),
        Index("ix_evidence_tenant_project", "tenant_id", "project_id"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    target_type: Mapped[str] = mapped_column(String(48), nullable=False)
    target_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    document_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    document_version_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    knowledge_source_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    locator: Mapped[str | None] = mapped_column(String(2048), nullable=True)
