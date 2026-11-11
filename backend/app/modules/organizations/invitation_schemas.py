from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class InvitationCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    role: str = Field(default="member", pattern="^(admin|member|viewer)$")


class InvitationPreview(BaseModel):
    organization_id: UUID
    organization_name: str
    invited_email: str
    role: str
    expires_at: datetime


class InvitationCreated(BaseModel):
    id: UUID
    invited_email: str
    role: str
    expires_at: datetime
    token: str


class InvitationAccepted(BaseModel):
    organization_id: UUID
    organization_name: str
    role: str
