from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    content: str = Field(min_length=1, max_length=50000)
    kind: str = Field(default="note", pattern="^(note|decision|task|blocker|fact)$")


class KnowledgeUpdate(BaseModel):
    title: str = Field(default=None, min_length=1, max_length=240)
    content: str = Field(default=None, min_length=1, max_length=50000)
    status: str = Field(default=None, pattern="^(draft|verified|archived)$")


class KnowledgeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    project_id: UUID
    title: str
    content: str
    kind: str
    status: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
