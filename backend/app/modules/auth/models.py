from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base, TimestampedUUIDMixin
from backend.app.modules.users.models import User


class PasswordReset(TimestampedUUIDMixin, Base):
    __tablename__ = "password_resets"
    __table_args__ = (
        Index("ix_password_resets_user_expires", "user_id", "expires_at"),
        Index("ix_password_resets_token_hash", "token_hash", unique=True),
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

__all__ = ["PasswordReset", "User"]
