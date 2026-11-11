from backend.app.modules.evidence.repositories import EvidenceRepository


class EvidenceService:
    def __init__(self, db) -> None:
        self.repository = EvidenceRepository(db)
