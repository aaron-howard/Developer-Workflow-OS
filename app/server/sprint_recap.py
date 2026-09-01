from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def generate_sprint_recap(repo_path: str, memory_path: str) -> dict[str, Any]:
    """Generate comprehensive sprint recap from all artifacts."""
    memory_dir = Path(memory_path)
    
    features_implemented = []
    tasks_completed = []
    
    if memory_dir.exists():
        for artifact_file in sorted(memory_dir.glob("*.json")):
            try:
                with artifact_file.open(encoding="utf-8") as f:
                    artifact = json.load(f)
                    
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
        "generated_at": datetime.now().isoformat(),
    }


def validate_feature_parity(repo_path: str, memory_path: str) -> dict[str, Any]:
    """Validate that planned features match implemented features."""
    memory_dir = Path(memory_path)
    
    planned_features = [
        "Implementation Checklist",
        "Issue-to-Code Mapping",
        "Dashboard Release Status",
        "Action Items Integration",
        "Artifact Navigation",
        "Routine History",
    ]
    
    implemented_features = []
    
    if memory_dir.exists():
        for artifact_file in memory_dir.glob("*.json"):
            try:
                with artifact_file.open(encoding="utf-8") as f:
                    artifact = json.load(f)
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


def generate_project_snapshot(repo_path: str, memory_path: str) -> dict[str, Any]:
    """Generate consolidated snapshot of project state."""
    memory_dir = Path(memory_path)
    analysis_artifacts = []
    
    if memory_dir.exists():
        for artifact_file in sorted(memory_dir.glob("*.json"), reverse=True):
            try:
                with artifact_file.open(encoding="utf-8") as f:
                    artifact = json.load(f)
                    analysis_artifacts.append({
                        "name": artifact.get("name", artifact_file.stem),
                        "type": artifact.get("type", "unknown"),
                        "created_at": artifact.get("created_at", artifact_file.stat().st_mtime),
                    })
            except (json.JSONDecodeError, OSError):
                continue
    
    return {
        "repo_name": Path(repo_path).name,
        "analysis_artifacts": analysis_artifacts[:20],  # Last 20 artifacts
        "workflow_status": "active",
        "total_artifacts": len(analysis_artifacts),
        "snapshot_time": datetime.now().isoformat(),
    }
