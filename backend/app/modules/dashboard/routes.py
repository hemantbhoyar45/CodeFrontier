from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.modules.auth.dependencies import (
    get_current_user,
    require_organization_member,
)
from backend.app.modules.dashboard.services import DashboardService
from backend.app.modules.organizations.models import OrganizationMember
from backend.app.modules.users.models import User
from backend.app.schemas import api_response

router = APIRouter(prefix="/organizations/{organization_id}/dashboard", tags=["dashboard"])


@router.get("")
def read_dashboard(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    membership: OrganizationMember = Depends(require_organization_member),
) -> dict[str, object]:
    result = DashboardService(db).summary(
        organization_id, current_user.id, membership.role
    )
    return api_response(result.model_dump(mode="json"))
