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


class GitLabNormalizer(BaseNormalizer):
    """
    Normalizer for GitLab merge_request, push, and tag_push webhooks.
    """
    def normalize(
        self,
        raw_payload: Dict[str, Any],
        category: str,
        provider: str
    ) -> SDLCEvent:
        project = raw_payload.get("project", {})
        repo_name = project.get("path_with_namespace") or project.get("name") or "unknown"
        
        user = raw_payload.get("user", {})
        actor = SDLCActor(
            name=user.get("name") or user.get("username") or "gitlab-user",
            username=user.get("username")
        )

        obj_kind = raw_payload.get("object_kind")
        if obj_kind == "merge_request":
            attrs = raw_payload.get("object_attributes", {})
            state = attrs.get("state", "opened")
            action = attrs.get("action", state)
            branch = attrs.get("source_branch")
            mr_id = attrs.get("iid") or attrs.get("id")

            if state == "merged" or action == "merge":
                evt = SDLCEventType.PR_MERGED
                delta = 10.0
                risk = SDLCRiskLevel.LOW
            elif state == "opened":
                evt = SDLCEventType.PR_OPENED
                delta = 0.0
                risk = SDLCRiskLevel.LOW
            else:
                evt = SDLCEventType.PR_CLOSED
                delta = 0.0
                risk = SDLCRiskLevel.LOW

            return SDLCEvent(
                source="gitlab",
                category=SDLCCategory.CODE,
                event_type=evt,
                repository=repo_name,
                branch=branch,
                actor=actor,
                payload=raw_payload,
                health_impact=SDLCHealthImpact(
                    score_delta=delta,
                    risk_level=risk,
                    message=f"GitLab MR !{mr_id} ({action}) in {repo_name}"
                )
            )

        if obj_kind in ("push", "tag_push"):
            ref = raw_payload.get("ref", "")
            branch = ref.replace("refs/heads/", "") if ref.startswith("refs/heads/") else ref
            commits = raw_payload.get("commits", [])
            
            return SDLCEvent(
                source="gitlab",
                category=SDLCCategory.CODE,
                event_type=SDLCEventType.COMMIT_PUSHED,
                repository=repo_name,
                branch=branch,
                actor=actor,
                payload=raw_payload,
                health_impact=SDLCHealthImpact(
                    score_delta=2.0,
                    risk_level=SDLCRiskLevel.LOW,
                    message=f"GitLab pushed {len(commits)} commits to {branch} in {repo_name}"
                )
            )

        return GenericWebhookNormalizer().normalize(raw_payload, category, "gitlab")


class AzureDevOpsNormalizer(BaseNormalizer):
    """
    Normalizer for Azure DevOps git.pullrequest, git.push, and workitem Service Hooks.
    """
    def normalize(
        self,
        raw_payload: Dict[str, Any],
        category: str,
        provider: str
    ) -> SDLCEvent:
        event_type = raw_payload.get("eventType", "")
        resource = raw_payload.get("resource", {})
        repo_data = resource.get("repository", {})
        repo_name = repo_data.get("name") or "azure-devops-repo"

        created_by = resource.get("createdBy", {})
        actor = SDLCActor(
            name=created_by.get("displayName") or created_by.get("uniqueName") or "azure-user",
            username=created_by.get("uniqueName")
        )

        if "git.pullrequest" in event_type:
            status = resource.get("status")
            branch = resource.get("sourceRefName", "").replace("refs/heads/", "")
            pr_id = resource.get("pullRequestId")

            if status == "completed":
                evt = SDLCEventType.PR_MERGED
                delta = 10.0
                risk = SDLCRiskLevel.LOW
            else:
                evt = SDLCEventType.PR_OPENED
                delta = 0.0
                risk = SDLCRiskLevel.LOW

            return SDLCEvent(
                source="azure_devops",
                category=SDLCCategory.CODE,
                event_type=evt,
                repository=repo_name,
                branch=branch,
                actor=actor,
                payload=raw_payload,
                health_impact=SDLCHealthImpact(
                    score_delta=delta,
                    risk_level=risk,
                    message=f"Azure DevOps PR #{pr_id} ({status}) in {repo_name}"
                )
            )

        if event_type == "git.push":
            ref = resource.get("refUpdates", [{}])[0].get("name", "")
            branch = ref.replace("refs/heads/", "") if ref.startswith("refs/heads/") else ref
            commits = resource.get("commits", [])

            return SDLCEvent(
                source="azure_devops",
                category=SDLCCategory.CODE,
                event_type=SDLCEventType.COMMIT_PUSHED,
                repository=repo_name,
                branch=branch,
                actor=actor,
                payload=raw_payload,
                health_impact=SDLCHealthImpact(
                    score_delta=2.0,
                    risk_level=SDLCRiskLevel.LOW,
                    message=f"Azure DevOps pushed {len(commits)} commits to {branch} in {repo_name}"
                )
            )

        return GenericWebhookNormalizer().normalize(raw_payload, category, "azure_devops")


class JiraNormalizer(BaseNormalizer):
    """
    Normalizer for Jira Cloud webhook events and release blocker detection.
    """
    def normalize(
        self,
        raw_payload: Dict[str, Any],
        category: str,
        provider: str
    ) -> SDLCEvent:
        issue = raw_payload.get("issue", {})
        key = issue.get("key") or raw_payload.get("key") or "JIRA-000"
        fields = issue.get("fields", {})
        summary = fields.get("summary", "")
        
        status_data = fields.get("status", {})
        status_name = status_data.get("name", "").lower()
        
        priority_data = fields.get("priority", {})
        priority_name = priority_data.get("name", "").lower()

        labels = [str(l).lower() for l in fields.get("labels", [])]
        user_data = raw_payload.get("user", {}) or fields.get("reporter", {})
        actor = SDLCActor(
            name=user_data.get("displayName") or user_data.get("name") or "jira-user",
            email=user_data.get("emailAddress")
        )

        is_blocker = (
            "blocker" in status_name
            or "blocker" in priority_name
            or "release-blocker" in labels
            or "blocker" in labels
        )

        if is_blocker:
            evt = SDLCEventType.ISSUE_BLOCKED
            delta = -15.0
            risk = SDLCRiskLevel.HIGH
            msg = f"Jira Release Blocker flagged: [{key}] {summary}"
        else:
            event_name = raw_payload.get("webhookEvent", "jira:issue_updated")
            if "created" in event_name:
                evt = SDLCEventType.ISSUE_CREATED
            else:
                evt = SDLCEventType.ISSUE_UPDATED
            delta = 1.0
            risk = SDLCRiskLevel.LOW
            msg = f"Jira issue [{key}] updated to state '{status_name or 'updated'}'"

        return SDLCEvent(
            source="jira",
            category=SDLCCategory.TICKET,
            event_type=evt,
            repository=key,
            actor=actor,
            payload=raw_payload,
            health_impact=SDLCHealthImpact(
                score_delta=delta,
                risk_level=risk,
                message=msg
            )
        )


class LinearNormalizer(BaseNormalizer):
    """
    Normalizer for Linear issue and project webhooks.
    """
    def normalize(
        self,
        raw_payload: Dict[str, Any],
        category: str,
        provider: str
    ) -> SDLCEvent:
        data = raw_payload.get("data", {})
        identifier = data.get("identifier") or data.get("title") or "LINEAR-0"
        state = data.get("state", {})
        state_name = state.get("name", "").lower() if isinstance(state, dict) else str(state).lower()
        
        action = raw_payload.get("action", "update")
        
        is_blocker = "blocker" in state_name or "blocked" in state_name
        if is_blocker:
            evt = SDLCEventType.ISSUE_BLOCKED
            delta = -10.0
            risk = SDLCRiskLevel.HIGH
            msg = f"Linear Blocker flagged: [{identifier}] {data.get('title', '')}"
        elif action == "create":
            evt = SDLCEventType.ISSUE_CREATED
            delta = 1.0
            risk = SDLCRiskLevel.LOW
            msg = f"Linear issue created: [{identifier}]"
        else:
            evt = SDLCEventType.ISSUE_UPDATED
            delta = 1.0
            risk = SDLCRiskLevel.LOW
            msg = f"Linear issue updated: [{identifier}] ({state_name})"

        return SDLCEvent(
            source="linear",
            category=SDLCCategory.TICKET,
            event_type=evt,
            repository=identifier,
            actor=SDLCActor(name="linear-user"),
            payload=raw_payload,
            health_impact=SDLCHealthImpact(
                score_delta=delta,
                risk_level=risk,
                message=msg
            )
        )

