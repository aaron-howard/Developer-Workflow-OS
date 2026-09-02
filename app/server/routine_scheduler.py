from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from app.server.command_centre import CommandCentre
from app.server.release_readiness import assess_release_readiness
from app.server.weekly_digest import generate_weekly_digest
from app.server.slack_notifier import SlackNotifier


class RoutineScheduler:
    """Register and run recurring developer workflow routines."""

    _INTERVAL_SECONDS = {
        "hourly": 60 * 60,
        "daily": 24 * 60 * 60,
        "nightly": 24 * 60 * 60,
        "weekly": 7 * 24 * 60 * 60,
    }

    def __init__(self, repo_path: str, memory_path: str = ".memory", slack_webhook_url: str | None = None):
        self.repo_path = Path(repo_path)
        self.memory_path = Path(memory_path)
        self.routines_dir = self.memory_path / "routines"
        self.routines_dir.mkdir(parents=True, exist_ok=True)
        self.centre = CommandCentre(repo_path=str(self.repo_path), memory_path=str(self.memory_path))
        self._routines: dict[str, dict[str, Any]] = {}
        self.slack = SlackNotifier(slack_webhook_url) if slack_webhook_url else None

    def _interval_seconds(self, interval: str) -> int:
        """Map a routine interval to a duration in seconds."""
        return self._INTERVAL_SECONDS.get(interval.lower(), 24 * 60 * 60)

    def register_routine(
        self,
        name: str,
        func: Callable[..., Any],
        interval: str = "daily",
        description: str | None = None,
    ) -> dict[str, Any]:
        """Register a routine that can be executed later."""
        routine = {
            "name": name,
            "interval": interval,
            "description": description or f"Routine '{name}'",
            "callable": func,
            "last_run": None,
        }
        self._routines[name] = routine

        metadata_path = self.routines_dir / f"{name}.json"
        metadata = {
            "name": name,
            "interval": interval,
            "description": routine["description"],
        }
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        return metadata

    def list_routines(self) -> list[dict[str, Any]]:
        """Return a list of registered routines."""
        routines = []
        for name, routine in sorted(self._routines.items()):
            routines.append(
                {
                    "name": routine["name"],
                    "interval": routine["interval"],
                    "description": routine["description"],
                }
            )
        return routines

    def run_routine(self, name: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Execute a registered routine and record the result as an artifact."""
        if name not in self._routines:
            raise ValueError(f"Unknown routine: {name}")

        routine = self._routines[name]
        result = routine["callable"](*args, **kwargs)

        payload = {
            "routine": name,
            "interval": routine["interval"],
            "status": "ok",
            "result": result,
        }
        if isinstance(result, dict):
            payload["status"] = result.get("status", "ok")

        routine["last_run"] = datetime.now(timezone.utc)
        self.centre.store_artifact(
            name=f"{name}_routine",
            artifact_type="routine_result",
            content=payload,
            tags=[name, routine["interval"], "routine"],
        )
        
        if self.slack:
            self.slack.post_routine_result(name, payload)

        return {
            "name": name,
            "interval": routine["interval"],
            "status": payload["status"],
            "result": result,
        }

    def run_due_routines(self) -> list[str]:
        """Execute any registered routines whose interval has elapsed since the last run."""
        fired: list[str] = []
        now = datetime.now(timezone.utc)

        for name, routine in self._routines.items():
            last_run = routine.get("last_run")
            if last_run is None:
                self.run_routine(name)
                fired.append(name)
                continue

            last_run_dt = last_run
            if isinstance(last_run, str):
                last_run_dt = datetime.fromisoformat(last_run)

            if now - last_run_dt > timedelta(seconds=self._interval_seconds(routine["interval"])):
                self.run_routine(name)
                fired.append(name)

        return fired

    def get_latest_artifact(self, routine_name: str) -> dict[str, Any] | None:
        """Fetch the most recent artifact recorded for a routine."""
        return self.centre.get_latest_artifact(artifact_type="routine_result", tag=routine_name)

    def install_default_routines(self) -> list[dict[str, Any]]:
        """Install the standard repo health and digest routines."""

        def nightly_digest() -> dict[str, Any]:
            return generate_weekly_digest(str(self.repo_path), base_branch="main")

        def weekly_digest() -> dict[str, Any]:
            return generate_weekly_digest(str(self.repo_path), base_branch="main")

        def release_check() -> dict[str, Any]:
            return assess_release_readiness(str(self.repo_path), base_branch="main")

        self.register_routine("nightly_digest", nightly_digest, interval="nightly", description="Summarize the repo at the end of the day.")
        self.register_routine("weekly_digest", weekly_digest, interval="weekly", description="Summarize the repo for the week.")
        self.register_routine("release_readiness", release_check, interval="daily", description="Check shipping confidence and blockers.")

        return self.list_routines()
