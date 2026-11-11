from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.modules.auth.dependencies import (
    get_current_user,
    require_organization_member,
)
from backend.app.modules.documents.repositories import DocumentRepository
from backend.app.modules.documents.schemas import DocumentCreate, DocumentRead, DocumentUpdate
from backend.app.modules.documents.services import DocumentService
from backend.app.modules.organizations.models import OrganizationMember
from backend.app.modules.projects.authorization import require_project_access
from backend.app.modules.users.models import User
from backend.app.schemas import api_response

router = APIRouter(
    prefix="/organizations/{organization_id}/projects/{project_id}/documents",
    tags=["documents"],
)


def _require_project(
    db: Session,
    tenant_id: UUID,
    project_id: UUID,
    user_id: UUID,
    organization_role: str,
    *,
    write: bool = False,
) -> None:
    require_project_access(
        db,
        tenant_id,
        project_id,
        user_id,
        organization_role=organization_role,
        write=write,
    )


@router.get("")
def list_documents(
    organization_id: UUID,
    project_id: UUID,
    status_filter: str | None = Query(default=None, alias="status", max_length=32),
    sort_by: str = Query(default="created_at", pattern="^(created_at|title)$"),
    descending: bool = True,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    _require_project(
        db, organization_id, project_id, current_user.id, membership.role
    )
    documents, total = DocumentRepository(db).list(
        organization_id,
        project_id,
        status_filter=status_filter,
        sort_by=sort_by,
        descending=descending,
        limit=limit,
        offset=offset,
    )
    return api_response(
        [DocumentRead.model_validate(item).model_dump(mode="json") for item in documents],
        meta={"count": total, "limit": limit, "offset": offset},
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_document(
    organization_id: UUID,
    project_id: UUID,
    payload: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    membership: OrganizationMember = Depends(require_organization_member),
) -> dict[str, object]:
    _require_project(
        db,
        organization_id,
        project_id,
        current_user.id,
        membership.role,
        write=True,
    )
    document = DocumentService(db).create(
        organization_id,
        project_id,
        current_user.id,
        title=payload.title,
        source_uri=payload.source_uri,
        content_type=payload.content_type,
    )
    return api_response(DocumentRead.model_validate(document).model_dump(mode="json"))


@router.get("/{document_id}")
def get_document(
    organization_id: UUID,
    document_id: UUID,
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    document = DocumentRepository(db).get(organization_id, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    require_project_access(
        db,
        organization_id,
        document.project_id,
        current_user.id,
        organization_role=membership.role,
    )
    return api_response(DocumentRead.model_validate(document).model_dump(mode="json"))


@router.patch("/{document_id}")
def update_document(
    organization_id: UUID,
    document_id: UUID,
    payload: DocumentUpdate,
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    if membership.role not in {"owner", "admin", "member"}:
        raise HTTPException(status_code=403, detail="Insufficient organization permissions")
    values = payload.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(status_code=422, detail="At least one field must be provided")
    document = DocumentRepository(db).get(organization_id, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    require_project_access(
        db,
        organization_id,
        document.project_id,
        current_user.id,
        organization_role=membership.role,
        write=True,
    )
    document = DocumentService(db).update(
        organization_id, document_id, values, actor_id=current_user.id
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return api_response(DocumentRead.model_validate(document).model_dump(mode="json"))


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    organization_id: UUID,
    document_id: UUID,
    db: Session = Depends(get_db),
    membership: OrganizationMember = Depends(require_organization_member),
    current_user: User = Depends(get_current_user),
) -> None:
    if membership.role not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Organization administrator role required")
    document = DocumentRepository(db).get(organization_id, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    require_project_access(
        db,
        organization_id,
        document.project_id,
        current_user.id,
        organization_role=membership.role,
    )
    if not DocumentService(db).delete(
        organization_id, document_id, actor_id=current_user.id
    ):
        raise HTTPException(status_code=404, detail="Document not found")
