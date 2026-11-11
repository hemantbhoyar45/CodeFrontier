from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.modules.organizations.models import OrganizationMember
from backend.app.modules.users.models import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def organization_users(
        self, tenant_id, *, search: str | None, sort_by: str, limit: int, offset: int
    ):
        conditions = [
            OrganizationMember.tenant_id == tenant_id,
            OrganizationMember.deleted_at.is_(None),
            User.deleted_at.is_(None),
        ]
        if search:
            search_term = f"%{search.strip()}%"
            conditions.append(User.email.ilike(search_term) | User.full_name.ilike(search_term))
        total = self.db.scalar(
            select(func.count(User.id))
            .join(OrganizationMember, OrganizationMember.user_id == User.id)
            .where(*conditions)
        ) or 0
        sort_column = {"email": User.email, "full_name": User.full_name}[sort_by]
        users = list(
            self.db.scalars(
                select(User)
                .join(OrganizationMember, OrganizationMember.user_id == User.id)
                .where(*conditions)
                .order_by(sort_column)
                .offset(offset)
                .limit(limit)
            )
        )
        return users, total
