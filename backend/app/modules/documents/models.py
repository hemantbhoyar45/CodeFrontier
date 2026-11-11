from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base, SoftDeleteMixin, TimestampedUUIDMixin


class Document(TimestampedUUIDMixin, SoftDeleteMixin, Base):
    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_documents_tenant_id"),
        ForeignKeyConstraint(
            ["tenant_id", "project_id"],
            ["projects.tenant_id", "projects.id"],
            ondelete="CASCADE",
            name="fk_documents_project_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "created_by"],
            ["organization_members.tenant_id", "organization_members.user_id"],
            ondelete="RESTRICT",
            name="fk_document_creator_tenant_member",
        ),
        Index("ix_documents_tenant_project", "tenant_id", "project_id"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    source_uri: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(160), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    created_by: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )


class DocumentVersion(TimestampedUUIDMixin, Base):
    __tablename__ = "document_versions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_document_versions_tenant_id"),
        UniqueConstraint("tenant_id", "document_id", "version", name="uq_document_version"),
        ForeignKeyConstraint(
            ["tenant_id", "document_id"],
            ["documents.tenant_id", "documents.id"],
            ondelete="CASCADE",
            name="fk_document_version_document_tenant",
        ),
        Index("ix_document_versions_tenant_document", "tenant_id", "document_id"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    document_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    content_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    storage_uri: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
