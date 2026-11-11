from backend.app.modules.integrations.schemas import IntegrationCreate


def test_integration_does_not_require_inline_credentials() -> None:
    config = IntegrationCreate(provider="github")
    assert config.credential_ref is None
