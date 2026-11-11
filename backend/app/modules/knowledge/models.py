from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    JSON,
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

EMBEDDING = Vector(1536).with_variant(JSON(), "sqlite")


class KnowledgeItem(TimestampedUUIDMixin, SoftDeleteMixin, Base):
    __tablename__ = "knowledge_items"
    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_knowledge_items_tenant_id"),
        ForeignKeyConstraint(
            ["tenant_id", "project_id"],
            ["projects.tenant_id", "projects.id"],
            ondelete="CASCADE",
            name="fk_knowledge_project_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "created_by"],
            ["organization_members.tenant_id", "organization_members.user_id"],
            ondelete="RESTRICT",
            name="fk_knowledge_creator_tenant_member",
        ),
        Index("ix_knowledge_tenant_project", "tenant_id", "project_id"),
        Index(
            "ix_knowledge_items_embedding",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[str] = mapped_column(String(48), nullable=False, default="note")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    embedding: Mapped[list[float] | None] = mapped_column(EMBEDDING, nullable=True)
    created_by: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )


class KnowledgeSource(TimestampedUUIDMixin, Base):
    __tablename__ = "knowledge_sources"
    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_knowledge_sources_tenant_id"),
        ForeignKeyConstraint(
            ["tenant_id", "knowledge_item_id"],
            ["knowledge_items.tenant_id", "knowledge_items.id"],
            ondelete="CASCADE",
            name="fk_knowledge_source_item_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "document_id"],
            ["documents.tenant_id", "documents.id"],
            ondelete="CASCADE",
            name="fk_knowledge_source_document_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "document_version_id"],
            ["document_versions.tenant_id", "document_versions.id"],
            ondelete="CASCADE",
            name="fk_knowledge_source_version_tenant",
        ),
        Index("ix_knowledge_sources_tenant_item", "tenant_id", "knowledge_item_id"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    knowledge_item_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    document_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    document_version_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    locator: Mapped[str | None] = mapped_column(String(2048), nullable=True)


class Decision(TimestampedUUIDMixin, SoftDeleteMixin, Base):
    __tablename__ = "decisions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "project_id"],
            ["projects.tenant_id", "projects.id"],
            ondelete="CASCADE",
            name="fk_decisions_project_tenant",
        ),
        Index("ix_decisions_tenant_project", "tenant_id", "project_id"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="proposed")
    decided_by: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )


class Task(TimestampedUUIDMixin, SoftDeleteMixin, Base):
    __tablename__ = "tasks"
    __table_args__ = (
        UniqueConstraint("tenant_id", "id", name="uq_tasks_tenant_id"),
        ForeignKeyConstraint(
            ["tenant_id", "project_id"],
            ["projects.tenant_id", "projects.id"],
            ondelete="CASCADE",
            name="fk_tasks_project_tenant",
        ),
        Index("ix_tasks_tenant_project_status", "tenant_id", "project_id", "status"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    assignee_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )


class Dependency(TimestampedUUIDMixin, Base):
    __tablename__ = "dependencies"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "task_id"],
            ["tasks.tenant_id", "tasks.id"],
            ondelete="CASCADE",
            name="fk_dependencies_task_tenant",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "depends_on_task_id"],
            ["tasks.tenant_id", "tasks.id"],
            ondelete="CASCADE",
            name="fk_dependencies_target_task_tenant",
        ),
        UniqueConstraint("tenant_id", "task_id", "depends_on_task_id", name="uq_task_dependency"),
        Index("ix_dependencies_tenant_task", "tenant_id", "task_id"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    task_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    depends_on_task_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)


class Blocker(TimestampedUUIDMixin, SoftDeleteMixin, Base):
    __tablename__ = "blockers"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "project_id"],
            ["projects.tenant_id", "projects.id"],
            ondelete="CASCADE",
            name="fk_blockers_project_tenant",
        ),
        Index("ix_blockers_tenant_project_status", "tenant_id", "project_id", "status"),
    )

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
