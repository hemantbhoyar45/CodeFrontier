from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HandoverCreate(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    recipient_role: str | None = Field(default=None, max_length=120)
    content: dict[str, object] = Field(default_factory=dict)


class HandoverRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    project_id: UUID
    created_by: UUID
    title: str
    recipient_role: str | None
    content: dict[str, object]
    status: str
    created_at: datetime
    updated_at: datetime
