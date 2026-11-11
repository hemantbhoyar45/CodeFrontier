from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.tenant import set_invitation_context, set_tenant_context
from backend.app.modules.auth.dependencies import get_current_user, require_organization_member
from backend.app.modules.organizations.invitation_schemas import (
    InvitationAccepted,
    InvitationCreate,
    InvitationCreated,
    InvitationPreview,
)
from backend.app.modules.organizations.invitations import InvitationService
from backend.app.modules.organizations.models import Organization, OrganizationMember
from backend.app.modules.organizations.repositories import OrganizationRepository
from backend.app.modules.organizations.schemas import (
    MemberCreate,
    OrganizationCreate,
    OrganizationRead,
)
from backend.app.modules.organizations.services import OrganizationService
from backend.app.modules.users.models import User
from backend.app.schemas import api_response

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    organization = OrganizationService(db).create(current_user.id, name=payload.name)
    return api_response(OrganizationRead.model_validate(organization).model_dump(mode="json"))


@router.get("")
def list_organizations(
    search: str | None = Query(default=None, max_length=160),
    sort_by: str = Query(default="name", pattern="^(name|created_at)$"),
    descending: bool = False,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    organizations, total = OrganizationService(db).list_for_user(
        current_user.id,
        search=search,
        sort_by=sort_by,
        descending=descending,
        limit=limit,
        offset=offset,
    )
    values = [
        OrganizationRead.model_validate(item).model_dump(mode="json")
        for item in organizations
    ]
    return api_response(
        values, meta={"count": total, "limit": limit, "offset": offset}
    )


@router.get("/{organization_id}/members")
def list_members(
    organization_id: UUID,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _membership: OrganizationMember = Depends(require_organization_member),
) -> dict[str, object]:
    members, total = OrganizationRepository(db).members(
        organization_id, limit=limit, offset=offset
    )
    values = [
        {
            "id": member.id,
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": member.role,
        }
        for member, user in members
    ]
    return api_response(
        values, meta={"count": total, "limit": limit, "offset": offset}
    )


@router.get("/{organization_id}/members/me")
def read_my_membership(
    organization_id: UUID,
    membership: OrganizationMember = Depends(require_organization_member),
) -> dict[str, object]:
    return api_response(
        {
            "organization_id": str(organization_id),
            "role": membership.role,
        }
    )


@router.post("/{organization_id}/members", status_code=status.HTTP_201_CREATED)
def add_member(
    organization_id: UUID,
    payload: MemberCreate,
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    if membership.role not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Organization administrator role required")
    try:
        created = OrganizationService(db).add_member(
            organization_id,
            email=payload.email,
            role=payload.role,
            actor_id=current_user.id,
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="User is already an organization member"
        ) from exc
    if created is None:
        raise HTTPException(status_code=404, detail="User not found")
    new_member, user = created
    return api_response(
        {
            "id": str(new_member.id),
            "user_id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": new_member.role,
        }
    )


@router.post("/{organization_id}/invitations", status_code=status.HTTP_201_CREATED)
def create_invitation(
    organization_id: UUID,
    payload: InvitationCreate,
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    if membership.role not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Organization administrator role required")
    set_tenant_context(db, organization_id)
    invitation, token = InvitationService(db).create(
        organization_id,
        current_user.id,
        email=payload.email,
        role=payload.role,
    )
    return api_response(
        InvitationCreated(
            id=invitation.id,
            invited_email=invitation.invited_email,
            role=invitation.role,
            expires_at=invitation.expires_at,
            token=token,
        ).model_dump(mode="json")
    )


@router.get("/invitations/{token}")
def preview_invitation(
    token: str,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    set_invitation_context(db, token)
    result = InvitationService(db).preview(token)
    if result is None:
        raise HTTPException(status_code=404, detail="Invitation is invalid or expired")
    invitation, organization = result
    return api_response(
        InvitationPreview(
            organization_id=organization.id,
            organization_name=organization.name,
            invited_email=invitation.invited_email,
            role=invitation.role,
            expires_at=invitation.expires_at,
        ).model_dump(mode="json")
    )


@router.post("/invitations/{token}/accept")
def accept_invitation(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    set_invitation_context(db, token)
    service = InvitationService(db)
    result = service.preview(token)
    if result is None:
        raise HTTPException(status_code=404, detail="Invitation is invalid or expired")
    invitation, organization = result
    set_tenant_context(db, organization.id)
    accepted = service.accept(token, current_user)
    if accepted == "email_mismatch":
        raise HTTPException(status_code=403, detail="Invitation belongs to a different email")
    if accepted == "already_member":
        raise HTTPException(status_code=409, detail="User is already an organization member")
    if accepted is None:
        raise HTTPException(status_code=404, detail="Invitation is invalid or expired")
    return api_response(
        InvitationAccepted(
            organization_id=organization.id,
            organization_name=organization.name,
            role=invitation.role,
        ).model_dump(mode="json")
    )


@router.get("/{organization_id}")
def get_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    _membership: OrganizationMember = Depends(require_organization_member),
) -> dict[str, object]:
    organization = db.scalar(
        select(Organization).where(
            Organization.id == organization_id, Organization.deleted_at.is_(None)
        )
    )
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return api_response(OrganizationRead.model_validate(organization).model_dump(mode="json"))
