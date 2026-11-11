from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.users.models import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email, User.deleted_at.is_(None)))

    def add(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user
