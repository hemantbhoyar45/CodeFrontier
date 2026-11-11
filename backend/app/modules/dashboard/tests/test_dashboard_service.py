def test_dashboard_summary_is_explicitly_defined() -> None:
    from backend.app.modules.dashboard.schemas import DashboardSummary

    expected = {
        "total_projects",
        "active_projects",
        "knowledge_items",
        "pending_reviews",
        "open_blockers",
        "generated_handovers",
        "continuity_score",
        "continuity_status",
    }
    assert expected <= DashboardSummary.model_fields.keys()
