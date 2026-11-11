from backend.app.modules.users.repositories import UserRepository


class UserService:
    def __init__(self, db) -> None:
        self.repository = UserRepository(db)

    def list_organization_users(
        self, tenant_id, *, search: str | None, sort_by: str, limit: int, offset: int
    ):
        if sort_by not in {"email", "full_name"}:
            raise ValueError("Unsupported user sort field")
        return self.repository.organization_users(
            tenant_id, search=search, sort_by=sort_by, limit=limit, offset=offset
        )
