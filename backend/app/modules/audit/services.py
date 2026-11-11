from backend.app.modules.audit.repositories import AuditRepository


class AuditService:
    def __init__(self, db) -> None:
        self.repository = AuditRepository(db)

    def record(self, tenant_id, actor_id, *, action, resource_type, resource_id=None, details=None):
        return self.repository.add_log(
            tenant_id,
            actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
        )
