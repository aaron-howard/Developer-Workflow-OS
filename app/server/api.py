from __future__ import annotations

from flask import Flask, jsonify, request

from app.server.branch_summary import summarize_branch
from app.server.release_readiness import assess_release_readiness
from app.server.repo_memory import build_feature_context, index_repo
from app.server.weekly_digest import generate_weekly_digest


def create_app(repo_path: str = ".") -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config["REPO_PATH"] = repo_path

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

    @app.route("/api/digest/weekly", methods=["GET"])
    def weekly_digest_endpoint():
        """Return weekly digest and summary."""
        base = request.args.get("base", "main")
        try:
            result = generate_weekly_digest(app.config["REPO_PATH"], base)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app
