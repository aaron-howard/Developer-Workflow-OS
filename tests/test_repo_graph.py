"""Tests for repo graph generator endpoint and module."""

from app.server.repo_graph import generate_repo_graph


def test_generate_repo_graph(tmp_path):
    # Create test directory structure
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "index.py").write_text("print('hello')")
    (tmp_path / "CLAUDE.md").write_text("# Router")

    result = generate_repo_graph(repo_path=str(tmp_path))
    assert "total_nodes" in result
    assert "total_links" in result
    assert "nodes" in result
    assert "links" in result
    assert result["total_nodes"] > 0
    assert result["total_links"] > 0

    node_ids = [n["id"] for n in result["nodes"]]
    assert "root" in node_ids
    assert "app" in node_ids


def test_repo_graph_endpoint(tmp_path):
    from app.server.api import create_app

    app = create_app(repo_path=str(tmp_path), memory_path=str(tmp_path / ".memory"))
    client = app.test_client()

    response = client.get("/api/repo/graph")
    assert response.status_code == 200
    data = response.get_json()
    assert "nodes" in data
    assert "links" in data
