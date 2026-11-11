from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.modules.auth.dependencies import (
    get_current_user,
    require_organization_member,
)
from backend.app.modules.integrations.schemas import IntegrationCreate, IntegrationRead
from backend.app.modules.integrations.services import IntegrationService
from backend.app.modules.organizations.models import OrganizationMember
from backend.app.modules.users.models import User
from backend.app.schemas import api_response

router = APIRouter(
    prefix="/organizations/{organization_id}/integrations",
    tags=["integrations"],
)


@router.get("")
def list_integrations(
    organization_id: UUID,
    provider: str | None = Query(default=None, max_length=80),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _membership: OrganizationMember = Depends(require_organization_member),
) -> dict[str, object]:
    records, total = IntegrationService(db).list(
        organization_id, provider=provider, limit=limit, offset=offset
    )
    return api_response(
        [IntegrationRead.model_validate(record).model_dump(mode="json") for record in records],
        meta={"count": total, "limit": limit, "offset": offset},
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_integration(
    organization_id: UUID,
    payload: IntegrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    membership: OrganizationMember = Depends(require_organization_member),
) -> dict[str, object]:
    if membership.role not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Organization administrator role required")
    record = IntegrationService(db).create(
        organization_id,
        provider=payload.provider,
        config=payload.config,
        credential_ref=payload.credential_ref,
        actor_id=current_user.id,
    )
    return api_response(IntegrationRead.model_validate(record).model_dump(mode="json"))
