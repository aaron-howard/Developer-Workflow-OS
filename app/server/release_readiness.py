from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def _git(repo_path: str, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo_path, text=True, stderr=subprocess.STDOUT).strip()


def assess_release_readiness(repo_path: str, base_branch: str = "main") -> dict[str, Any]:
    repo = Path(repo_path)
    blockers: list[str] = []
    checks: list[str] = []

    if not repo.exists():
        return {
            "score": 0,
            "status": "blocked",
            "blockers": [f"Repository path does not exist: {repo_path}"],
            "summary": "Release readiness is blocked because the repository path is missing.",
            "checks": [],
        }

    try:
        branch = _git(repo_path, "branch", "--show-current") or "main"
    except subprocess.CalledProcessError:
        branch = "main"

    try:
        changed_files = _git(repo_path, "diff", "--name-only", f"{base_branch}...{branch}")
        files = [line.strip() for line in changed_files.splitlines() if line.strip()]
    except subprocess.CalledProcessError:
        changed_files = _git(repo_path, "status", "--short")
        files = [line[3:].strip() for line in changed_files.splitlines() if line.strip()]

    if not files:
        checks.append("No local branch diff detected against the base branch")
        blockers.append("No code changes currently queued for release")

    has_code = any(path.endswith((".py", ".js", ".ts", ".java", ".cs")) for path in files)
    has_tests = any("test" in path.lower() for path in files)
    has_docs = any(path.endswith(".md") for path in files)

    if has_code and not has_tests:
        blockers.append("Code changes are present without matching test updates")
    if not has_docs:
        checks.append("No documentation changes were detected in the current diff")
    if not has_code:
        checks.append("No runtime code changes were detected")

    test_candidates = list(repo.glob("**/test*.py")) + list(repo.glob("**/*_test.py"))
    if not test_candidates:
        blockers.append("No obvious automated tests are present in the repo")

    score = 100
    score -= len(blockers) * 25
    score -= max(0, len(checks) - 1) * 5
    score = max(0, min(100, score))

    if blockers:
        status = "blocked" if score < 40 else "watch"
    elif score >= 80:
        status = "ready"
    else:
        status = "watch"

    summary = (
        f"Release readiness for {repo.name} is {status} "
        f"with a score of {score}/100. "
        f"The current change set includes {len(files)} relevant file(s); "
        f"{len(blockers)} blocker(s) were detected and {len(checks)} review signal(s) were noted."
    )

    return {
        "repo": repo.name,
        "base_branch": base_branch,
        "branch": branch,
        "score": score,
        "status": status,
        "blockers": blockers,
        "summary": summary,
        "checks": checks,
        "changed_files": files,
    }
