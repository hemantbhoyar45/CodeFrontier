from uuid import UUID

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewRequestCreate(BaseModel):
    project_id: UUID
    target_type: str = Field(min_length=1, max_length=48)
    target_id: UUID
    comment: str | None = Field(default=None, max_length=10000)


class ReviewDecision(BaseModel):
    status: str = Field(pattern="^(approved|changes_requested)$")
    comment: str | None = Field(default=None, max_length=10000)


class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    requested_by: UUID
    target_type: str
    target_id: UUID
    status: str
    comment: str | None
    created_at: datetime
    reviewed_by: UUID | None
    reviewed_at: datetime | None
