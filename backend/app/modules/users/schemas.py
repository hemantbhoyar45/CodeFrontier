from uuid import UUID

from pydantic import BaseModel

from backend.app.modules.auth.schemas import UserRead


class UserSummary(UserRead):
    id: UUID


class UserCreate(BaseModel):
    full_name: str
    email: str
