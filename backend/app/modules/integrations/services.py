from backend.app.modules.integrations.repositories import IntegrationRepository
from backend.app.modules.integrations.models import Integration
from backend.app.modules.audit.services import AuditService


class IntegrationService:
    def __init__(self, db) -> None:
        self.db = db
        self.repository = IntegrationRepository(db)

    def list(self, tenant_id, *, provider, limit, offset):
        return self.repository.list(tenant_id, provider=provider, limit=limit, offset=offset)

    def create(self, tenant_id, *, provider, config, credential_ref, actor_id):
        integration = Integration(
            tenant_id=tenant_id,
            provider=provider,
            status="disconnected",
            config=config,
            credential_ref=credential_ref,
        )
        self.db.add(integration)
        self.db.flush()
        AuditService(self.db).record(
            tenant_id,
            actor_id,
            action="integration.configured",
            resource_type="integration",
            resource_id=integration.id,
            details={"provider": provider},
        )
        self.db.commit()
        return integration
