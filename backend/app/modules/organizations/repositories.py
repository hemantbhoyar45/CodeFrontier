from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.modules.organizations.models import Organization, OrganizationMember
from backend.app.modules.users.models import User


class OrganizationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def for_user(
        self,
        user_id,
        *,
        search: str | None,
        sort_by: str,
        descending: bool,
        limit: int,
        offset: int,
    ):
        conditions = (
            OrganizationMember.user_id == user_id,
            OrganizationMember.deleted_at.is_(None),
            Organization.deleted_at.is_(None),
            Organization.is_active.is_(True),
        )
        if search:
            conditions += (Organization.name.ilike(f"%{search.strip()}%"),)
        total = self.db.scalar(
            select(func.count(Organization.id))
            .join(OrganizationMember, OrganizationMember.organization_id == Organization.id)
            .where(*conditions)
        ) or 0
        sort_column = {"name": Organization.name, "created_at": Organization.created_at}[sort_by]
        organizations = list(
            self.db.scalars(
                select(Organization)
                .join(OrganizationMember, OrganizationMember.organization_id == Organization.id)
                .where(*conditions)
                .order_by(sort_column.desc() if descending else sort_column.asc())
                .offset(offset)
                .limit(limit)
            )
        )
        return organizations, total

    def members(self, organization_id, *, limit: int, offset: int):
        conditions = (
            OrganizationMember.tenant_id == organization_id,
            OrganizationMember.deleted_at.is_(None),
            User.deleted_at.is_(None),
        )
        total = self.db.scalar(
            select(func.count(OrganizationMember.id))
            .join(User, User.id == OrganizationMember.user_id)
            .where(*conditions)
        ) or 0
        members = list(
            self.db.execute(
                select(OrganizationMember, User)
                .join(User, User.id == OrganizationMember.user_id)
                .where(*conditions)
                .order_by(User.email)
                .offset(offset)
                .limit(limit)
            )
        )
        return members, total
