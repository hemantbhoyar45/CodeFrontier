from uuid import uuid4

from backend.app.modules.auth.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_and_verification() -> None:
    stored = hash_password("a-long-test-password")
    assert stored != "a-long-test-password"
    assert verify_password("a-long-test-password", stored)
    assert not verify_password("wrong-password", stored)


def test_access_token_round_trip() -> None:
    user_id = uuid4()
    assert decode_access_token(create_access_token(user_id)) == user_id
