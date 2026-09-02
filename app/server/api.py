from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, request, send_file

from app.server.branch_summary import summarize_branch
from app.server.command_centre import CommandCentre
from app.server.artifact_navigation import (
    get_artifacts_navigation,
    get_routine_history,
)
from app.server.dashboard_integration import get_action_items, get_release_status
from app.server.plan_alignment import plan_coverage_report
from app.server.implementation_checklist import generate_implementation_checklist
from app.server.issue_mapping import map_issue_to_code
from app.server.release_notes import generate_release_notes
from app.server.release_readiness import assess_release_readiness
from app.server.sprint_recap import (
    generate_sprint_recap,
    validate_feature_parity,
    generate_project_snapshot,
)
from app.server.repo_memory import build_feature_context, index_repo
from app.server.routine_scheduler import RoutineScheduler
from app.server.weekly_digest import generate_weekly_digest


def create_app(repo_path: str = ".", memory_path: str = ".memory", slack_webhook_url: str | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config["REPO_PATH"] = repo_path
    app.config["MEMORY_PATH"] = memory_path
    app.centre = CommandCentre(repo_path=repo_path, memory_path=memory_path)
    app.scheduler = RoutineScheduler(repo_path=repo_path, memory_path=memory_path, slack_webhook_url=slack_webhook_url)
    app.scheduler.install_default_routines()
    app.scheduler.run_due_routines()

    @app.route("/", methods=["GET"])
    def dashboard_root():
        """Serve the local dashboard UI at the application root."""
        dashboard_path = Path(__file__).resolve().parents[1] / "dashboard" / "index.html"
        return send_file(dashboard_path, mimetype="text/html")

    @app.route("/api/repo/index", methods=["GET"])
    def repo_index():
        """Return repo indexing and workspace map."""
        try:
            result = index_repo(app.config["REPO_PATH"])
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/repo/feature", methods=["GET"])
    def repo_feature():
        """Return feature context and related files."""
        feature = request.args.get("feature", "")
        if not feature:
            return jsonify({"error": "feature query parameter is required"}), 400
        try:
            result = build_feature_context(app.config["REPO_PATH"], feature)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/branch/summary", methods=["GET"])
    def branch_summary():
        """Return branch diff summary and risk areas."""
        base = request.args.get("base", "main")
        target = request.args.get("target", "")
        if not target:
            return jsonify({"error": "target query parameter is required"}), 400
        try:
            result = summarize_branch(app.config["REPO_PATH"], base, target)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/release/readiness", methods=["GET"])
    def release_readiness():
        """Return release readiness score and blockers."""
        base = request.args.get("base", "main")
        try:
            result = assess_release_readiness(app.config["REPO_PATH"], base)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/release/notes", methods=["GET"])
    def release_notes():
        """Return a draft release note summary for the current repo state."""
        base = request.args.get("base", "main")
        try:
            result = generate_release_notes(app.config["REPO_PATH"], base)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/feature/checklist", methods=["GET"])
    def feature_checklist():
        """Return an implementation checklist for a feature request."""
        feature = request.args.get("feature", "")
        if not feature:
            return jsonify({"error": "feature query parameter is required"}), 400
        try:
            result = generate_implementation_checklist(app.config["REPO_PATH"], feature)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/issue/map", methods=["GET"])
    def issue_map():
        """Map an issue description to the code that will need to be modified."""
        issue = request.args.get("issue", "")
        if not issue:
            return jsonify({"error": "issue query parameter is required"}), 400
        try:
            result = map_issue_to_code(app.config["REPO_PATH"], issue)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/digest/weekly", methods=["GET"])
    def weekly_digest_endpoint():
        """Return weekly digest and summary."""
        base = request.args.get("base", "main")
        try:
            result = generate_weekly_digest(app.config["REPO_PATH"], base)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/plan/status", methods=["GET"])
    def plan_status():
        """Return the plan coverage summary for the dashboard widget."""
        try:
            return jsonify(plan_coverage_report()), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/dashboard/release-status", methods=["GET"])
    def dashboard_release_status():
        """Return combined release readiness and notes for the dashboard."""
        base = request.args.get("base", "main")
        try:
            result = get_release_status(app.config["REPO_PATH"], base)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/dashboard/action-items", methods=["GET"])
    def dashboard_action_items():
        """Return actionable items (checklists and issue mapping) for a context."""
        context = request.args.get("context", "")
        if not context:
            return jsonify({"error": "context query parameter is required"}), 400
        try:
            result = get_action_items(app.config["REPO_PATH"], context)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/artifacts/navigation", methods=["GET"])
    def artifacts_navigation():
        """Return artifact navigation structure and history."""
        try:
            result = get_artifacts_navigation(app.config["MEMORY_PATH"])
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/routines/history", methods=["GET"])
    def routines_history():
        """Return routine execution history."""
        try:
            result = get_routine_history(app.config["MEMORY_PATH"])
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/routines/trigger", methods=["POST"])
    def routines_trigger():
        """Manually trigger a specific routine."""
        data = request.get_json() or {}
        routine = data.get("routine", "")
        if not routine:
            return jsonify({"error": "routine parameter is required"}), 400
        try:
            result = app.scheduler.run_routine(routine)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/sprint/recap", methods=["GET"])
    def sprint_recap():
        """Generate comprehensive sprint recap."""
        try:
            result = generate_sprint_recap(app.config["REPO_PATH"], app.config["MEMORY_PATH"])
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/features/parity", methods=["GET"])
    def features_parity():
        """Validate feature parity against planned roadmap."""
        try:
            result = validate_feature_parity(app.config["REPO_PATH"], app.config["MEMORY_PATH"])
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/project/snapshot", methods=["GET"])
    def project_snapshot():
        """Generate project snapshot with consolidated artifacts."""
        try:
            result = generate_project_snapshot(app.config["REPO_PATH"], app.config["MEMORY_PATH"])
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/routines", methods=["GET"])
    def list_routines():
        """List registered scheduler routines."""
        try:
            routines = app.scheduler.list_routines()
            return jsonify({"routines": routines}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/routines/<routine_name>/run", methods=["POST"])
    def run_routine(routine_name):
        """Execute a registered routine and record its result as an artifact."""
        try:
            result = app.scheduler.run_routine(routine_name)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/artifacts", methods=["GET"])
    def list_artifacts():
        """List stored artifacts, optionally filtered by type."""
        artifact_type = request.args.get("type", None)
        tag = request.args.get("tag", None)
        limit = request.args.get("limit", 50, type=int)
        try:
            artifacts = app.centre.list_artifacts(
                artifact_type=artifact_type, tag=tag, limit=limit
            )
            return jsonify({"artifacts": artifacts}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/artifacts", methods=["POST"])
    def store_artifact():
        """Store a new artifact."""
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        name = data.get("name")
        artifact_type = data.get("type")
        content = data.get("content")
        tags = data.get("tags", [])

        if not name or not artifact_type or content is None:
            return jsonify({"error": "name, type, and content are required"}), 400

        try:
            result = app.centre.store_artifact(
                name=name, artifact_type=artifact_type, content=content, tags=tags
            )
            return jsonify(result), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/artifacts/<artifact_id>", methods=["GET"])
    def get_artifact_by_id(artifact_id):
        """Retrieve a specific artifact by ID."""
        try:
            artifact = app.centre.get_artifact(artifact_id)
            if not artifact:
                return jsonify({"error": "Artifact not found"}), 404
            return jsonify(artifact), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/artifacts/latest", methods=["GET"])
    def get_latest():
        """Retrieve the latest artifact of a given type."""
        artifact_type = request.args.get("type", None)
        if not artifact_type:
            return jsonify({"error": "type query parameter is required"}), 400
        try:
            artifact = app.centre.get_latest_artifact(artifact_type=artifact_type)
            if not artifact:
                return (
                    jsonify({"error": f"No artifacts of type {artifact_type}"}),
                    404,
                )
            return jsonify(artifact), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app
