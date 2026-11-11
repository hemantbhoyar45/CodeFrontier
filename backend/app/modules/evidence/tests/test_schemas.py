from uuid import uuid4

from backend.app.modules.evidence.schemas import EvidenceCreate


def test_evidence_reference_requires_target() -> None:
    item = EvidenceCreate(target_type="knowledge", target_id=uuid4())
    assert item.document_id is None
