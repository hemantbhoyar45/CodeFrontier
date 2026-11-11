from backend.app.modules.audit.schemas import AuditLogRead


def test_audit_log_read_is_available() -> None:
    assert "details" in AuditLogRead.model_fields
