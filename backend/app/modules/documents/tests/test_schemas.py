import pytest
from pydantic import ValidationError

from backend.app.modules.documents.schemas import DocumentUpdate


def test_document_status_is_validated() -> None:
    with pytest.raises(ValidationError):
        DocumentUpdate(status="unknown")
