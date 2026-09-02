from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def get_artifacts_navigation(memory_path: str) -> dict[str, Any]:
    """Fetch all artifacts and provide navigation structure."""
    memory_dir = Path(memory_path)
    artifacts = []

    if memory_dir.exists():
        for artifact_file in sorted(memory_dir.glob("*.json"), reverse=True):
            try:
                with artifact_file.open(encoding="utf-8") as f:
                    artifact = json.load(f)
                    artifacts.append({
                        "name": artifact.get("name", artifact_file.stem),
                        "type": artifact.get("type", "unknown"),
                        "created_at": artifact.get("created_at", artifact_file.stat().st_mtime),
                        "path": str(artifact_file.relative_to(memory_dir.parent)),
                    })
            except (json.JSONDecodeError, OSError):
                continue

    return {
        "artifacts": artifacts,
        "total_count": len(artifacts),
    }


def get_routine_history(memory_path: str) -> dict[str, Any]:
    """Fetch routine execution history from memory artifacts."""
    memory_dir = Path(memory_path)
    routine_executions = []

    if memory_dir.exists():
        for history_file in memory_dir.glob("*routine*"):
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


def trigger_routine(repo_path: str, routine_name: str) -> dict[str, Any]:
    """Manually trigger a specific routine and return execution status."""
    from app.server.routine_scheduler import RoutineScheduler

    scheduler = RoutineScheduler(repo_path)
    scheduler.install_default_routines()

    # Find and execute the routine
    try:
        result = scheduler.run_routine(routine_name)
        return {
            "routine": routine_name,
            "status": "triggered",
            "message": f"Routine '{routine_name}' executed successfully",
            "result": result,
        }
    except ValueError as e:
        return {
            "routine": routine_name,
            "status": "not_found",
            "message": str(e),
        }
    except Exception as e:
        return {
            "routine": routine_name,
            "status": "error",
            "message": str(e),
        }
