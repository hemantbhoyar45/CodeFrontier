from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    source_uri: str | None = Field(default=None, max_length=2048)
    content_type: str | None = Field(default=None, max_length=160)


class DocumentUpdate(BaseModel):
    title: str = Field(default=None, min_length=1, max_length=240)
    source_uri: str | None = Field(default=None, max_length=2048)
    content_type: str | None = Field(default=None, max_length=160)
    status: str = Field(default=None, pattern="^(queued|processing|ready|failed)$")


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    project_id: UUID
    title: str
    source_uri: str | None
    content_type: str | None
    status: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
