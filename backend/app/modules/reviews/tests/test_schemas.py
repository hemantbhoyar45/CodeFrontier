from uuid import uuid4

from backend.app.modules.reviews.schemas import ReviewRequestCreate


def test_review_request_accepts_project_and_target_ids() -> None:
    project_id = uuid4()
    request = ReviewRequestCreate(
        project_id=project_id, target_type="knowledge", target_id=uuid4()
    )
    assert request.project_id == project_id
