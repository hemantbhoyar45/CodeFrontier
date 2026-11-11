from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.modules.auth.dependencies import require_organization_member
from backend.app.modules.organizations.models import OrganizationMember
from backend.app.modules.users.schemas import UserSummary
from backend.app.modules.users.services import UserService
from backend.app.schemas import api_response

router = APIRouter(prefix="/organizations/{organization_id}/users", tags=["users"])


@router.get("")
def list_users(
    organization_id: UUID,
    search: str | None = Query(default=None, max_length=160),
    sort_by: str = Query(default="email", pattern="^(email|full_name)$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _membership: OrganizationMember = Depends(require_organization_member),
) -> dict[str, object]:
    users, total = UserService(db).list_organization_users(
        organization_id,
        search=search,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
    )
    return api_response(
        [UserSummary.model_validate(user).model_dump(mode="json") for user in users],
        meta={"count": total, "limit": limit, "offset": offset},
    )
