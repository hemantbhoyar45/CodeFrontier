import pytest
from pydantic import ValidationError

from backend.app.modules.projects.schemas import ProjectUpdate


def test_project_update_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError):
        ProjectUpdate(status="unknown")
