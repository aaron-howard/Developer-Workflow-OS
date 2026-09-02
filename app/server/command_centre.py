from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class CommandCentre:
    """
    Central command and memory hub for the Developer Workflow OS.
    Handles artifact storage, retrieval, and routine orchestration.
    """

    def __init__(self, repo_path: str, memory_path: str = ".memory"):
        """Initialize the command centre with repo and memory paths."""
        self.repo_path = Path(repo_path)
        self.memory_path = Path(memory_path)
        self.artifacts_dir = self.memory_path / "artifacts"
        self.routines_dir = self.memory_path / "routines"
        self.index_path = self.memory_path / "index.json"

        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.routines_dir.mkdir(parents=True, exist_ok=True)

        self._load_index()

    def _load_index(self) -> None:
        """Load or initialize the artifact index."""
        if self.index_path.exists():
            self._index = json.loads(self.index_path.read_text(encoding="utf-8"))
        else:
            self._index = {"artifacts": {}}

    def _save_index(self) -> None:
        """Persist the artifact index to disk."""
        self.index_path.write_text(json.dumps(self._index, indent=2), encoding="utf-8")

    def store_artifact(
        self,
        name: str,
        artifact_type: str,
        content: Any,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Store an artifact (summary, digest, release notes, etc.) in memory.

        Args:
            name: Human-readable artifact name
            artifact_type: Type of artifact (e.g., "weekly_digest", "branch_summary")
            content: The artifact content (dict, string, etc.)
            tags: Optional list of tags for categorization

        Returns:
            Artifact metadata including ID and timestamp
        """
        artifact_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        tags = tags or []

        artifact = {
            "id": artifact_id,
            "name": name,
            "type": artifact_type,
            "content": content,
            "tags": tags,
            "created_at": timestamp,
        }

        artifact_file = self.artifacts_dir / f"{artifact_id}.json"
        artifact_file.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

        self._index["artifacts"][artifact_id] = {
            "id": artifact_id,
            "name": name,
            "type": artifact_type,
            "tags": tags,
            "created_at": timestamp,
        }
        self._save_index()

        return {
            "id": artifact_id,
            "name": name,
            "type": artifact_type,
            "tags": tags,
            "created_at": timestamp,
        }

    def _resolve_artifact_path(self, artifact_id: str) -> Path | None:
        """
        Safely resolve the file path for an artifact_id, preventing path traversal.

        Returns the resolved Path if valid and strictly within artifacts_dir, otherwise None.
        """
        if not artifact_id or not isinstance(artifact_id, str):
            return None

        # Disallow path separators, traversal dots, and non-alphanumeric characters
        if not re.match(r"^[a-zA-Z0-9_-]+$", artifact_id):
            return None

        try:
            target_file = (self.artifacts_dir / f"{artifact_id}.json").resolve()
            base_dir = self.artifacts_dir.resolve()
            if not target_file.is_relative_to(base_dir):
                return None
            return target_file
        except (ValueError, OSError):
            return None

    def get_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        """Retrieve a stored artifact by ID safely."""
        artifact_file = self._resolve_artifact_path(artifact_id)
        if not artifact_file or not artifact_file.exists():
            return None
        return json.loads(artifact_file.read_text(encoding="utf-8"))

    def list_artifacts(
        self,
        artifact_type: str | None = None,
        tag: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        List stored artifacts, optionally filtered by type or tag.

        Args:
            artifact_type: Filter by artifact type
            tag: Filter by tag
            limit: Maximum number of results to return

        Returns:
            List of artifact metadata (not full content)
        """
        results = []

        for artifact_meta in self._index["artifacts"].values():
            if artifact_type and artifact_meta["type"] != artifact_type:
                continue
            if tag and tag not in artifact_meta.get("tags", []):
                continue
            results.append(artifact_meta)

        results.sort(key=lambda x: x["created_at"], reverse=True)
        return results[:limit]

    def get_latest_artifact(
        self,
        artifact_type: str,
        tag: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Retrieve the most recently created artifact of a given type.

        Args:
            artifact_type: Type of artifact to retrieve
            tag: Optional tag filter

        Returns:
            Full artifact (with content) or None if not found
        """
        artifacts = self.list_artifacts(artifact_type=artifact_type, tag=tag, limit=1)
        if not artifacts:
            return None
        return self.get_artifact(artifacts[0]["id"])

    def delete_artifact(self, artifact_id: str) -> bool:
        """Delete a stored artifact safely."""
        artifact_file = self._resolve_artifact_path(artifact_id)
        if not artifact_file or not artifact_file.exists():
            return False

        artifact_file.unlink()
        if artifact_id in self._index["artifacts"]:
            del self._index["artifacts"][artifact_id]
            self._save_index()
        return True

    def cleanup_old_artifacts(self, artifact_type: str, keep_count: int = 10) -> int:
        """
        Remove old artifacts of a type, keeping only the most recent N.

        Args:
            artifact_type: Type of artifact to cleanup
            keep_count: Number of recent artifacts to retain

        Returns:
            Number of artifacts deleted
        """
        artifacts = self.list_artifacts(artifact_type=artifact_type, limit=None)
        deleted = 0

        for artifact in artifacts[keep_count:]:
            if self.delete_artifact(artifact["id"]):
                deleted += 1

        return deleted
