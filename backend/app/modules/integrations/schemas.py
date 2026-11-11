from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IntegrationCreate(BaseModel):
    provider: str = Field(min_length=1, max_length=80)
    config: dict[str, object] = Field(default_factory=dict)
    credential_ref: str | None = Field(default=None, max_length=512)


class IntegrationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    provider: str
    status: str
    config: dict[str, object]
    credential_ref: str | None
