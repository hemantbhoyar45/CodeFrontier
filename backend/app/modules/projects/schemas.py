from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=10000)


class ProjectUpdate(BaseModel):
    name: str = Field(default=None, min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=10000)
    status: str = Field(default=None, pattern="^(active|paused|completed|archived)$")


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    name: str
    description: str | None
    status: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class ProjectMemberCreate(BaseModel):
    user_id: UUID
    role: str = Field(default="member", pattern="^(admin|member|viewer)$")


class ProjectMemberRead(BaseModel):
    id: UUID
    user_id: UUID
    email: str
    full_name: str
    role: str
