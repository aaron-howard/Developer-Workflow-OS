import subprocess

from app.server.routine_scheduler import RoutineScheduler


def test_routine_scheduler_registers_and_runs_routine(tmp_path):
    """A registered routine should run and persist its output artifact."""
    repo = tmp_path / "routine-repo"
    repo.mkdir()

    subprocess.run(["git", "init", "-b", "main"], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(repo), capture_output=True, check=True)
    (repo / "README.md").write_text("demo\n")
    subprocess.run(["git", "add", "."], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=str(repo), capture_output=True, check=True)

    memory_dir = tmp_path / "memory"
    scheduler = RoutineScheduler(repo_path=str(repo), memory_path=str(memory_dir))

    def sample_routine():
        return {
            "summary": "sample run",
            "status": "ok",
            "commits": 1,
        }

    scheduler.register_routine("sample", sample_routine, interval="daily")
    result = scheduler.run_routine("sample")

    assert result["status"] == "ok"
    assert result["result"]["summary"] == "sample run"
    assert scheduler.get_latest_artifact("sample") is not None


def test_routine_scheduler_lists_registered_routines(tmp_path):
    """Routine scheduler should expose registered routines with interval metadata."""
    repo = tmp_path / "routine-list-repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(repo), capture_output=True, check=True)
    (repo / "README.md").write_text("demo\n")
    subprocess.run(["git", "add", "."], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(repo), capture_output=True, check=True)

    scheduler = RoutineScheduler(repo_path=str(repo), memory_path=str(tmp_path / "memory"))
    scheduler.register_routine("nightly_digest", lambda: {"summary": "nightly"}, interval="nightly")
    scheduler.register_routine("weekly_digest", lambda: {"summary": "weekly"}, interval="weekly")

    routines = scheduler.list_routines()
    names = {routine["name"] for routine in routines}

    assert {"nightly_digest", "weekly_digest"}.issubset(names)
    assert {routine["interval"] for routine in routines}.issuperset({"nightly", "weekly"})


def test_routine_scheduler_builds_default_routines(tmp_path):
    """The scheduler should offer default repo health routines."""
    repo = tmp_path / "default-routine-repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(repo), capture_output=True, check=True)
    (repo / "README.md").write_text("demo\n")
    subprocess.run(["git", "add", "."], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=str(repo), capture_output=True, check=True)

    scheduler = RoutineScheduler(repo_path=str(repo), memory_path=str(tmp_path / "memory"))
    scheduler.install_default_routines()

    names = {routine["name"] for routine in scheduler.list_routines()}
    assert {"nightly_digest", "weekly_digest", "release_readiness"}.issubset(names)


def test_scheduler_api_lists_and_runs_routines(tmp_path):
    """The Flask app should expose scheduler endpoints for listing and running routines."""
    from app.server.api import create_app

    repo = tmp_path / "scheduler-api-repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(repo), capture_output=True, check=True)
    (repo / "README.md").write_text("demo\n")
    subprocess.run(["git", "add", "."], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=str(repo), capture_output=True, check=True)

    app = create_app(repo_path=str(repo), memory_path=str(tmp_path / "memory"))
    client = app.test_client()

    response = client.get("/api/routines")
    assert response.status_code == 200
    payload = response.get_json()
    names = {item["name"] for item in payload["routines"]}
    assert {"nightly_digest", "weekly_digest", "release_readiness"}.issubset(names)

    response = client.post("/api/routines/weekly_digest/run")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["name"] == "weekly_digest"
    assert payload["result"]["repo_name"] == repo.name


def test_routine_scheduler_runs_due_routines_automatically(tmp_path):
    """Due routines should execute without manual triggers when the scheduler checks them."""
    repo = tmp_path / "due-routine-repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(repo), capture_output=True, check=True)
    (repo / "README.md").write_text("demo\n")
    subprocess.run(["git", "add", "."], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=str(repo), capture_output=True, check=True)

    scheduler = RoutineScheduler(repo_path=str(repo), memory_path=str(tmp_path / "memory"))

    def sample():
        return {"summary": "due", "status": "ok"}

    scheduler.register_routine("sample", sample, interval="hourly")
    scheduler._routines["sample"]["last_run"] = None
    fired = scheduler.run_due_routines()

    assert fired == ["sample"]
    assert scheduler.get_latest_artifact("sample") is not None
