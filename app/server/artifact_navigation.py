from __future__ import annotations

from typing import Any

from app.server.command_centre import CommandCentre


def get_artifacts_navigation(memory_path: str) -> dict[str, Any]:
    """Fetch all artifacts and provide navigation structure via CommandCentre."""
    centre = CommandCentre(repo_path=".", memory_path=memory_path)
    return centre.get_artifacts_navigation()


def get_routine_history(memory_path: str) -> dict[str, Any]:
    """Fetch routine execution history via CommandCentre."""
    centre = CommandCentre(repo_path=".", memory_path=memory_path)
    return centre.get_routine_history()


def trigger_routine(repo_path: str, routine_name: str) -> dict[str, Any]:
    """Manually trigger a specific routine and return execution status."""
    from app.server.routine_scheduler import RoutineScheduler

    scheduler = RoutineScheduler(repo_path)
    scheduler.install_default_routines()

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

