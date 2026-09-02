import json
import subprocess
from pathlib import Path

from app.server.command_centre import CommandCentre


def test_command_centre_stores_and_retrieves_artifacts(tmp_path):
    """Test that command centre can store and retrieve generated artifacts."""
    repo = tmp_path / "command-repo"
    repo.mkdir()

    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    (repo / "README.md").write_text("test project\n")
    subprocess.run(
        ["git", "add", "."],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()

    centre = CommandCentre(repo_path=str(repo), memory_path=str(memory_dir))

    artifact = centre.store_artifact(
        name="test_digest",
        artifact_type="weekly_digest",
        content={"summary": "test summary", "commits": 5},
        tags=["weekly", "digest"],
    )

    assert artifact["id"]
    assert artifact["name"] == "test_digest"
    assert artifact["type"] == "weekly_digest"
    assert artifact["tags"] == ["weekly", "digest"]

    retrieved = centre.get_artifact(artifact["id"])
    assert retrieved is not None
    assert retrieved["content"]["summary"] == "test summary"


def test_command_centre_lists_artifacts_by_type(tmp_path):
    """Test that command centre can list artifacts by type."""
    repo = tmp_path / "list-repo"
    repo.mkdir()

    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    (repo / "README.md").write_text("test\n")
    subprocess.run(
        ["git", "add", "."],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()

    centre = CommandCentre(repo_path=str(repo), memory_path=str(memory_dir))

    centre.store_artifact("digest1", "weekly_digest", {"data": "1"}, ["digest"])
    centre.store_artifact("digest2", "weekly_digest", {"data": "2"}, ["digest"])
    centre.store_artifact("branch1", "branch_summary", {"data": "3"}, ["branch"])

    digests = centre.list_artifacts(artifact_type="weekly_digest")
    branches = centre.list_artifacts(artifact_type="branch_summary")

    assert len(digests) == 2
    assert len(branches) == 1
    assert all(a["type"] == "weekly_digest" for a in digests)
    assert all(a["type"] == "branch_summary" for a in branches)


def test_command_centre_retrieves_latest_artifact(tmp_path):
    """Test that command centre can retrieve the latest artifact of a type."""
    repo = tmp_path / "latest-repo"
    repo.mkdir()

    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    (repo / "README.md").write_text("test\n")
    subprocess.run(
        ["git", "add", "."],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()

    centre = CommandCentre(repo_path=str(repo), memory_path=str(memory_dir))

    centre.store_artifact("old_digest", "weekly_digest", {"version": 1})
    centre.store_artifact("new_digest", "weekly_digest", {"version": 2})

    latest = centre.get_latest_artifact(artifact_type="weekly_digest")
    assert latest is not None
    assert latest["content"]["version"] == 2


def test_command_centre_prevents_path_traversal_on_get_and_delete(tmp_path):
    """Verify that get_artifact and delete_artifact block path traversal attempts."""
    repo = tmp_path / "traversal-repo"
    repo.mkdir()
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()

    # Create an outside file that should not be accessible
    outside_file = tmp_path / "secret.json"
    outside_file.write_text('{"secret": "leak"}', encoding="utf-8")

    centre = CommandCentre(repo_path=str(repo), memory_path=str(memory_dir))

    # Path traversal attempts
    assert centre.get_artifact("../secret") is None
    assert centre.get_artifact("..\\secret") is None
    assert centre.get_artifact("../../secret") is None
    assert centre.get_artifact("nested/../../secret") is None
    assert centre.get_artifact("invalid-name!@#") is None

    # Delete traversal attempts
    assert centre.delete_artifact("../secret") is False
    assert centre.delete_artifact("..\\secret") is False
    assert outside_file.exists()  # outside file must remain untouched

    # Stored artifact still gets and deletes cleanly
    valid_artifact = centre.store_artifact("safe", "weekly_digest", {"ok": True})
    art_id = valid_artifact["id"]
    assert centre.get_artifact(art_id) is not None
    assert centre.delete_artifact(art_id) is True
    assert centre.get_artifact(art_id) is None

