"""
Event Normalizers for SDLC Ingestion Engine
"""
from typing import Dict, Any, Optional
from app.server.events.schema import (
    SDLCEvent,
    SDLCCategory,
    SDLCEventType,
    SDLCHealthImpact,
    SDLCRiskLevel,
    SDLCActor
)


class BaseNormalizer:
    """
    Base class for all provider-specific event normalizers.
    """
    def normalize(
        self,
        raw_payload: Dict[str, Any],
        category: str,
        provider: str
    ) -> SDLCEvent:
        raise NotImplementedError("Normalizers must implement normalize()")


class GenericWebhookNormalizer(BaseNormalizer):
    """
    Fallback normalizer for generic webhooks and test signals.
    """
    def normalize(
        self,
        raw_payload: Dict[str, Any],
        category: str,
        provider: str
    ) -> SDLCEvent:
        repo = raw_payload.get("repository") or raw_payload.get("repo") or "unknown"
        branch = raw_payload.get("branch") or raw_payload.get("ref")
        env = raw_payload.get("environment") or raw_payload.get("env")
        actor_name = raw_payload.get("actor") or raw_payload.get("user") or "system"
        
        event_type_str = raw_payload.get("eventType") or raw_payload.get("event_type") or "generic_signal"
        try:
            evt_type = SDLCEventType(event_type_str)
        except ValueError:
            evt_type = SDLCEventType.GENERIC_SIGNAL

        try:
            cat_enum = SDLCCategory(category)
        except ValueError:
            cat_enum = SDLCCategory.CODE

        return SDLCEvent(
            source=provider,
            category=cat_enum,
            event_type=evt_type,
            repository=repo,
            branch=branch,
            environment=env,
            actor=SDLCActor(name=str(actor_name)),
            payload=raw_payload,
            health_impact=SDLCHealthImpact(
                score_delta=float(raw_payload.get("scoreDelta", 0.0)),
                risk_level=SDLCRiskLevel.LOW,
                message=raw_payload.get("message", f"Event ingested from {provider}")
            )
        )


class GitHubNormalizer(BaseNormalizer):
    """
    Normalizer for GitHub push, pull_request, and workflow_run webhooks.
    """
    def normalize(
        self,
        raw_payload: Dict[str, Any],
        category: str,
        provider: str
    ) -> SDLCEvent:
        repo_data = raw_payload.get("repository", {})
        repo_name = repo_data.get("full_name") or repo_data.get("name") or "unknown"
        
        sender = raw_payload.get("sender", {})
        actor = SDLCActor(
            name=sender.get("login", "github-user"),
            username=sender.get("login")
        )

        if "pull_request" in raw_payload:
            pr = raw_payload["pull_request"]
            action = raw_payload.get("action", "opened")
            branch = pr.get("head", {}).get("ref")
            
            is_merged = pr.get("merged", False) or action == "merged"
            if is_merged:
                evt = SDLCEventType.PR_MERGED
                delta = 10.0
                risk = SDLCRiskLevel.LOW
            elif action == "opened":
                evt = SDLCEventType.PR_OPENED
                delta = 0.0
                risk = SDLCRiskLevel.LOW
            else:
                evt = SDLCEventType.PR_CLOSED
                delta = 0.0
                risk = SDLCRiskLevel.LOW

            return SDLCEvent(
                source="github",
                category=SDLCCategory.CODE,
                event_type=evt,
                repository=repo_name,
                branch=branch,
                actor=actor,
                payload=raw_payload,
                health_impact=SDLCHealthImpact(
                    score_delta=delta,
                    risk_level=risk,
                    message=f"GitHub PR #{pr.get('number')} {action} in {repo_name}"
                )
            )

        if "commits" in raw_payload:
            ref = raw_payload.get("ref", "")
            branch = ref.replace("refs/heads/", "") if ref.startswith("refs/heads/") else ref
            commit_count = len(raw_payload.get("commits", []))
            
            return SDLCEvent(
                source="github",
                category=SDLCCategory.CODE,
                event_type=SDLCEventType.COMMIT_PUSHED,
                repository=repo_name,
                branch=branch,
                actor=actor,
                payload=raw_payload,
                health_impact=SDLCHealthImpact(
                    score_delta=2.0,
                    risk_level=SDLCRiskLevel.LOW,
                    message=f"Pushed {commit_count} commits to {branch} in {repo_name}"
                )
            )

        # Fallback generic GitHub event
        return GenericWebhookNormalizer().normalize(raw_payload, category, "github")
