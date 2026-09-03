from __future__ import annotations

import json
import os
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

        self.runs_log_path = self.memory_path / "runs.log"

        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.routines_dir.mkdir(parents=True, exist_ok=True)

        self._load_index()

    def log_run_event(self, action: str, model: str = "claude-sonnet-3.7", effort: str = "medium", status: str = "ok") -> None:
        """Log skill button / routine execution event to .memory/runs.log matching Skills Level 3."""
        timestamp = datetime.now(timezone.utc).isoformat()
        line = f"[{timestamp}] action='{action}' model='{model}' effort='{effort}' status='{status}'\n"
        with open(self.runs_log_path, "a", encoding="utf-8") as f:
            f.write(line)


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

        # Sanitize with basename and strictly validate format
        clean_id = os.path.basename(artifact_id)
        if clean_id != artifact_id or not re.match(r"^[a-zA-Z0-9_-]+$", clean_id):
            return None

        # Ensure ID belongs to an indexed artifact
        if clean_id not in self._index.get("artifacts", {}):
            return None

        try:
            base_dir = os.path.realpath(str(self.artifacts_dir))
            target_path = os.path.realpath(os.path.join(base_dir, clean_id + ".json"))

            # Verify path containment using commonpath and separator prefix
            if os.path.commonpath([base_dir, target_path]) != base_dir:
                return None
            if not target_path.startswith(base_dir + os.sep):
                return None
            return Path(target_path)
        except (ValueError, OSError):
            return None

    def get_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        """Retrieve a stored artifact by ID safely."""
        artifact_file = self._resolve_artifact_path(artifact_id)
        if not artifact_file or not os.path.isfile(str(artifact_file)):
            return None
        with open(artifact_file, "r", encoding="utf-8") as f:
            return json.load(f)

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
        if not artifact_file or not os.path.isfile(str(artifact_file)):
            return False

        os.remove(str(artifact_file))
        if artifact_id in self._index.get("artifacts", {}):
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

    def get_artifacts_navigation(self) -> dict[str, Any]:
        """Fetch all artifacts and provide navigation structure using index seam."""
        artifacts = []
        # Direct index lookup
        for art in self.list_artifacts(limit=100):
            artifacts.append({
                "name": art.get("name", art["id"]),
                "type": art.get("type", "unknown"),
                "created_at": art.get("created_at"),
                "path": f".memory/artifacts/{art['id']}.json",
            })

        # Fallback for unindexed raw files created in tests
        if not artifacts and self.memory_path.exists():
            for artifact_file in sorted(self.memory_path.glob("*.json"), reverse=True):
                try:
                    with artifact_file.open(encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            artifacts.append({
                                "name": data.get("name", artifact_file.stem),
                                "type": data.get("type", "unknown"),
                                "created_at": data.get("created_at", artifact_file.stat().st_mtime),
                                "path": str(artifact_file.relative_to(self.memory_path.parent if self.memory_path.parent != self.memory_path else self.memory_path)),
                            })
                except (json.JSONDecodeError, OSError):
                    continue

        return {
            "artifacts": artifacts,
            "total_count": len(artifacts),
        }

    def get_routine_history(self) -> dict[str, Any]:
        """Fetch routine execution history from memory artifacts."""
        routine_executions = []
        if self.memory_path.exists():
            for history_file in self.memory_path.glob("*routine*"):
                try:
                    with history_file.open(encoding="utf-8") as f:
                        history = json.load(f)
                        if isinstance(history, dict) and "executions" in history:
                            for execution in history.get("executions", []):
                                routine_executions.append({
                                    "routine": execution.get("routine_name", "unknown"),
                                    "timestamp": execution.get("timestamp"),
                                    "status": execution.get("status", "unknown"),
                                })
                except (json.JSONDecodeError, OSError):
                    continue

        return {
            "routines": routine_executions,
            "total_executions": len(routine_executions),
        }

    def generate_sprint_recap(self) -> dict[str, Any]:
        """Generate comprehensive sprint recap from stored artifacts."""
        features_implemented = []
        tasks_completed = []

        for art in self.list_artifacts(limit=200):
            art_type = art.get("type")
            art_name = art.get("name", art["id"])
            if art_type == "feature":
                features_implemented.append(art_name)
            elif art_type == "task":
                tasks_completed.append(art_name)

        if not features_implemented and not tasks_completed and self.memory_path.exists():
            for artifact_file in sorted(self.memory_path.glob("*.json")):
                try:
                    with artifact_file.open(encoding="utf-8") as f:
                        artifact = json.load(f)
                        if isinstance(artifact, dict):
                            if artifact.get("type") == "feature":
                                features_implemented.append(artifact.get("name", artifact_file.stem))
                            elif artifact.get("type") == "task":
                                tasks_completed.append(artifact.get("name", artifact_file.stem))
                except (json.JSONDecodeError, OSError):
                    continue

        return {
            "summary": f"Sprint recap: {len(features_implemented)} features, {len(tasks_completed)} tasks",
            "features_implemented": features_implemented,
            "tasks_completed": tasks_completed,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def validate_feature_parity(self) -> dict[str, Any]:
        """Validate that planned features match implemented features."""
        planned_features = [
            "Implementation Checklist",
            "Issue-to-Code Mapping",
            "Dashboard Release Status",
            "Action Items Integration",
            "Artifact Navigation",
            "Routine History",
        ]
        implemented_features = []

        for art in self.list_artifacts(limit=200):
            name = art.get("name", "")
            if any(planned.lower() in name.lower() for planned in planned_features):
                implemented_features.append(name)

        if not implemented_features and self.memory_path.exists():
            for artifact_file in self.memory_path.glob("*.json"):
                try:
                    with artifact_file.open(encoding="utf-8") as f:
                        artifact = json.load(f)
                        if isinstance(artifact, dict):
                            name = artifact.get("name", artifact_file.stem)
                            if any(planned.lower() in name.lower() for planned in planned_features):
                                implemented_features.append(name)
                except (json.JSONDecodeError, OSError):
                    continue

        parity_score = (len(implemented_features) / len(planned_features) * 100) if planned_features else 0

        return {
            "planned_features": planned_features,
            "implemented_features": list(set(implemented_features)),
            "parity_score": round(parity_score, 1),
            "missing_features": [f for f in planned_features if not any(f.lower() in impl.lower() for impl in implemented_features)],
        }

    def generate_project_snapshot(self) -> dict[str, Any]:
        """Generate consolidated snapshot of project state."""
        nav = self.get_artifacts_navigation()
        analysis_artifacts = nav.get("artifacts", [])[:20]

        return {
            "repo_name": self.repo_path.name,
            "analysis_artifacts": analysis_artifacts,
            "workflow_status": "active",
            "total_artifacts": nav.get("total_count", 0),
            "snapshot_time": datetime.now(timezone.utc).isoformat(),
        }

