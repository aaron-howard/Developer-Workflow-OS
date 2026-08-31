from app.server.plan_alignment import load_plan_sections, plan_coverage_report


def test_plan_alignment_loads_the_mvp_sections():
    """The plan doc should be the source of truth for the MVP feature list."""
    sections = load_plan_sections()

    names = {item["name"] for item in sections}

    assert "Repo indexer" in names
    assert "Feature context engine" in names
    assert "Branch and PR summary engine" in names
    assert "Release readiness agent" in names
    assert "Sprint digest agent" in names
    assert "Command centre UI" in names


def test_plan_alignment_reports_implemented_feature_coverage():
    """The coverage report should map implemented modules to planned project sections."""
    report = plan_coverage_report()

    assert report["status"] in {"complete", "partial"}
    assert "repo_indexer" in report["coverage"]
    assert "release_readiness" in report["coverage"]
    assert "weekly_digest" in report["coverage"]
    assert "command_centre" in report["coverage"]


def test_plan_status_api_exposes_plan_coverage():
    """The API should expose the plan coverage summary for the dashboard widget."""
    from app.server.api import create_app

    app = create_app(repo_path=".", memory_path=".memory")
    client = app.test_client()

    response = client.get("/api/plan/status")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] in {"complete", "partial"}
    assert "coverage" in payload
    assert "missing" in payload
