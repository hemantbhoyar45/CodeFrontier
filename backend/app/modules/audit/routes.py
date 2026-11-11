from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.modules.audit.repositories import AuditRepository
from backend.app.modules.audit.schemas import AuditLogRead
from backend.app.modules.auth.dependencies import require_organization_member
from backend.app.modules.organizations.models import OrganizationMember
from backend.app.schemas import api_response

router = APIRouter(prefix="/organizations/{organization_id}/audit-logs", tags=["audit"])


@router.get("")
def list_audit_logs(
    organization_id: UUID,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _membership: OrganizationMember = Depends(require_organization_member),
) -> dict[str, object]:
    records, total = AuditRepository(db).list_logs(
        organization_id, limit=limit, offset=offset
    )
    return api_response(
        [AuditLogRead.model_validate(record).model_dump(mode="json") for record in records],
        meta={"count": total, "limit": limit, "offset": offset},
    )
