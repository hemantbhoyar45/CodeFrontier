from backend.app.modules.handovers.schemas import HandoverCreate


def test_handover_defaults_to_empty_content() -> None:
    assert HandoverCreate(title="Transition").content == {}
