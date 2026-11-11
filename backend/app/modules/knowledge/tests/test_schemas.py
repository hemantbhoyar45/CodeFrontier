import pytest
from pydantic import ValidationError

from backend.app.modules.knowledge.schemas import KnowledgeCreate


def test_knowledge_kind_is_validated() -> None:
    with pytest.raises(ValidationError):
        KnowledgeCreate(title="Test", content="Text", kind="unsupported")
