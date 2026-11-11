from uuid import UUID

from pydantic import BaseModel, Field


class EvidenceCreate(BaseModel):
    target_type: str = Field(min_length=1, max_length=48)
    target_id: UUID
    document_id: UUID | None = None
    document_version_id: UUID | None = None
    locator: str | None = Field(default=None, max_length=2048)
