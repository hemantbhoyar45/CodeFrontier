from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.modules.evidence.models import EvidenceReference


class EvidenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_project(self, tenant_id: UUID, project_id: UUID):
        return list(
            self.db.scalars(
                select(EvidenceReference).where(
                    EvidenceReference.tenant_id == tenant_id,
                    EvidenceReference.project_id == project_id,
                )
            )
        )
