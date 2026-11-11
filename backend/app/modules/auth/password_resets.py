import hashlib
import secrets
import smtplib
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import get_settings
from backend.app.db.tenant import set_password_reset_context
from backend.app.modules.auth.models import PasswordReset
from backend.app.modules.auth.security import hash_password
from backend.app.modules.users.models import User

RESET_TTL = timedelta(minutes=30)


class EmailDeliveryUnavailable(Exception):
    pass


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def send_password_reset_email(email: str, token: str) -> None:
    settings = get_settings()
    if not settings.smtp_host or not settings.smtp_from_email:
        raise EmailDeliveryUnavailable("Password reset email delivery is not configured")
    message = EmailMessage()
    message["Subject"] = "Reset your KNOWBRIDGE password"
    message["From"] = settings.smtp_from_email
    message["To"] = email
    reset_link = f"{settings.frontend_base_url.rstrip('/')}/reset-password?token={token}"
    message.set_content(
        "A password reset was requested for your KNOWBRIDGE account.\n\n"
        f"Use this link within 30 minutes: {reset_link}\n\n"
        "If you did not request this, you can ignore this message."
    )
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password or "")
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailDeliveryUnavailable("Password reset email could not be sent") from exc


class PasswordResetService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def request(self, email: str) -> str | None:
        user = self.db.scalar(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        if user is None:
            return None
        token = secrets.token_urlsafe(32)
        token_hash = hash_reset_token(token)
        set_password_reset_context(self.db, token_hash)
        self.db.add(
            PasswordReset(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=datetime.now(UTC) + RESET_TTL,
            )
        )
        self.db.commit()
        return token

    def confirm(self, token: str, password: str) -> bool:
        token_hash = hash_reset_token(token)
        set_password_reset_context(self.db, token_hash)
        reset = self.db.scalar(
            select(PasswordReset).where(
                PasswordReset.token_hash == token_hash,
                PasswordReset.used_at.is_(None),
            )
        )
        if reset is None:
            return False
        expires_at = reset.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at <= datetime.now(UTC):
            return False
        user = self.db.get(User, reset.user_id)
        if user is None or user.deleted_at is not None:
            return False
        user.password_hash = hash_password(password)
        reset.used_at = datetime.now(UTC)
        self.db.commit()
        return True
