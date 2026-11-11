import pytest
from pydantic import ValidationError

from backend.app.modules.organizations.schemas import MemberCreate


def test_member_role_is_restricted_to_supported_roles() -> None:
    assert MemberCreate(email="member@example.com", role="viewer").role == "viewer"
    with pytest.raises(ValidationError):
        MemberCreate(email="member@example.com", role="owner")
