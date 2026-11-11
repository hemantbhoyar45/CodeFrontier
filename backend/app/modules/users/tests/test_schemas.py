from backend.app.modules.users.schemas import UserSummary


def test_user_read_schema_excludes_password_hash() -> None:
    assert "password_hash" not in UserSummary.model_fields
