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


class JenkinsNormalizer(BaseNormalizer):
    """
    Normalizer for Jenkins Notification Plugin and Generic Webhook builds.
    """
    def normalize(
        self,
        raw_payload: Dict[str, Any],
        category: str,
        provider: str
    ) -> SDLCEvent:
        build = raw_payload.get("build", {})
        job_name = raw_payload.get("job") or raw_payload.get("name") or build.get("full_url") or "jenkins-job"
        if isinstance(job_name, str) and "/" in job_name:
            job_name = job_name.split("/")[-1] or job_name

        build_num = raw_payload.get("build_number") or raw_payload.get("number") or build.get("number") or 1
        status = (
            raw_payload.get("status")
            or raw_payload.get("result")
            or build.get("status")
            or build.get("phase")
            or "SUCCESS"
        ).upper()

        if status in ("SUCCESS", "SUCCESSFUL", "COMPLETED", "PASSED"):
            evt = SDLCEventType.BUILD_PASSED
            delta = 5.0
            risk = SDLCRiskLevel.LOW
            msg = f"Jenkins build #{build_num} passed for job '{job_name}'"
        else:
            evt = SDLCEventType.BUILD_FAILED
            delta = -10.0
            risk = SDLCRiskLevel.HIGH
            msg = f"Jenkins build #{build_num} failed ({status}) for job '{job_name}'"

        return SDLCEvent(
            source="jenkins",
            category=SDLCCategory.BUILD,
            event_type=evt,
            repository=str(job_name),
            actor=SDLCActor(name="jenkins-bot"),
            payload=raw_payload,
            health_impact=SDLCHealthImpact(
                score_delta=delta,
                risk_level=risk,
                message=msg
            )
        )


class CircleCINormalizer(BaseNormalizer):
    """
    Normalizer for CircleCI workflow-completed and job-completed events.
    """
    def normalize(
        self,
        raw_payload: Dict[str, Any],
        category: str,
        provider: str
    ) -> SDLCEvent:
        workflow = raw_payload.get("workflow", {})
        pipeline = raw_payload.get("pipeline", {})
        project = raw_payload.get("project", {})
        
        repo_name = project.get("name") or pipeline.get("vcs", {}).get("repo_name") or "circleci-repo"
        workflow_name = workflow.get("name") or raw_payload.get("type", "workflow")
        
        status = (workflow.get("status") or raw_payload.get("status") or "success").lower()

        if status in ("success", "passed"):
            evt = SDLCEventType.BUILD_PASSED
            delta = 5.0
            risk = SDLCRiskLevel.LOW
            msg = f"CircleCI workflow '{workflow_name}' succeeded in {repo_name}"
        else:
            evt = SDLCEventType.BUILD_FAILED
            delta = -10.0
            risk = SDLCRiskLevel.HIGH
            msg = f"CircleCI workflow '{workflow_name}' failed ({status}) in {repo_name}"

        return SDLCEvent(
            source="circleci",
            category=SDLCCategory.BUILD,
            event_type=evt,
            repository=repo_name,
            actor=SDLCActor(name="circleci-bot"),
            payload=raw_payload,
            health_impact=SDLCHealthImpact(
                score_delta=delta,
                risk_level=risk,
                message=msg
            )
        )


class GradleNormalizer(BaseNormalizer):
    """
    Normalizer for Gradle init plugin build listener telemetry.
    """
    def normalize(
        self,
        raw_payload: Dict[str, Any],
        category: str,
        provider: str
    ) -> SDLCEvent:
        project_name = raw_payload.get("projectName") or raw_payload.get("project") or "gradle-project"
        tasks = raw_payload.get("taskNames", [])
        duration_ms = raw_payload.get("durationMs", 0)
        has_failure = bool(raw_payload.get("failure", False))

        task_str = ", ".join(tasks) if isinstance(tasks, list) else str(tasks)

        if has_failure:
            evt = SDLCEventType.BUILD_FAILED
            delta = -5.0
            risk = SDLCRiskLevel.MEDIUM
            msg = f"Gradle build failed for project '{project_name}' [tasks: {task_str}]"
        else:
            evt = SDLCEventType.BUILD_PASSED
            delta = 3.0
            risk = SDLCRiskLevel.LOW
            msg = f"Gradle build passed for project '{project_name}' [tasks: {task_str}] ({duration_ms}ms)"

        return SDLCEvent(
            source="gradle",
            category=SDLCCategory.BUILD,
            event_type=evt,
            repository=project_name,
            actor=SDLCActor(name="gradle-runner"),
            payload=raw_payload,
            health_impact=SDLCHealthImpact(
                score_delta=delta,
                risk_level=risk,
                message=msg
            )
        )


class PlaywrightNormalizer(BaseNormalizer):
    """
    Normalizer for Playwright and JUnit E2E test execution reports.
    """
    def normalize(
        self,
        raw_payload: Dict[str, Any],
        category: str,
        provider: str
    ) -> SDLCEvent:
        passed = int(raw_payload.get("passed", 0))
        failed = int(raw_payload.get("failed", 0))
        skipped = int(raw_payload.get("skipped", 0))
        suite_name = raw_payload.get("suite") or raw_payload.get("project") or "playwright-e2e"

        if failed > 0:
            evt = SDLCEventType.TESTS_FAILED
            delta = -12.0
            risk = SDLCRiskLevel.HIGH
            msg = f"Playwright E2E suite '{suite_name}' failed: {failed} failed, {passed} passed"
        else:
            evt = SDLCEventType.TESTS_PASSED
            delta = 5.0
            risk = SDLCRiskLevel.LOW
            msg = f"Playwright E2E suite '{suite_name}' passed: {passed} passed ({skipped} skipped)"

        return SDLCEvent(
            source="playwright",
            category=SDLCCategory.TESTING,
            event_type=evt,
            repository=suite_name,
            actor=SDLCActor(name="playwright-runner"),
            payload=raw_payload,
            health_impact=SDLCHealthImpact(
                score_delta=delta,
                risk_level=risk,
                message=msg
            )
        )


class DatadogNormalizer(BaseNormalizer):
    """
    Normalizer for Datadog Monitor webhook alerts and incident events.
    """
    def normalize(
        self,
        raw_payload: Dict[str, Any],
        category: str,
        provider: str
    ) -> SDLCEvent:
        alert_type = (raw_payload.get("alert_type") or raw_payload.get("event_type") or "error").lower()
        title = raw_payload.get("title") or raw_payload.get("event_title") or "Datadog Alert"
        hostname = raw_payload.get("hostname") or "datadog-agent"

        if alert_type in ("error", "alert", "critical"):
            evt = SDLCEventType.INCIDENT_CREATED
            delta = -15.0
            risk = SDLCRiskLevel.CRITICAL
            msg = f"Datadog Monitor Alert [{alert_type.upper()}]: {title}"
        elif alert_type == "warning":
            evt = SDLCEventType.SECURITY_ALERT
            delta = -5.0
            risk = SDLCRiskLevel.MEDIUM
            msg = f"Datadog Monitor Warning: {title}"
        else:
            evt = SDLCEventType.INCIDENT_RESOLVED
            delta = 10.0
            risk = SDLCRiskLevel.LOW
            msg = f"Datadog Monitor Recovered: {title}"

        return SDLCEvent(
            source="datadog",
            category=SDLCCategory.OBSERVABILITY,
            event_type=evt,
            repository=str(hostname),
            actor=SDLCActor(name="datadog-bot"),
            payload=raw_payload,
            health_impact=SDLCHealthImpact(
                score_delta=delta,
                risk_level=risk,
                message=msg
            )
        )


class SentryNormalizer(BaseNormalizer):
    """
    Normalizer for Sentry exception webhooks and issue webhooks.
    """
    def normalize(
        self,
        raw_payload: Dict[str, Any],
        category: str,
        provider: str
    ) -> SDLCEvent:
        action = (raw_payload.get("action") or "created").lower()
        issue = raw_payload.get("issue") or raw_payload.get("data", {}).get("issue") or {}
        
        title = issue.get("title") or raw_payload.get("title") or "Unhandled Exception"
        culprit = issue.get("culprit") or raw_payload.get("culprit") or "app-core"

        if action in ("resolved", "ignored"):
            evt = SDLCEventType.INCIDENT_RESOLVED
            delta = 8.0
            risk = SDLCRiskLevel.LOW
            msg = f"Sentry issue resolved: {title}"
        else:
            evt = SDLCEventType.INCIDENT_CREATED
            delta = -12.0
            risk = SDLCRiskLevel.HIGH
            msg = f"Sentry exception in {culprit}: {title}"

        return SDLCEvent(
            source="sentry",
            category=SDLCCategory.OBSERVABILITY,
            event_type=evt,
            repository=str(culprit),
            actor=SDLCActor(name="sentry-bot"),
            payload=raw_payload,
            health_impact=SDLCHealthImpact(
                score_delta=delta,
                risk_level=risk,
                message=msg
            )
        )


class PagerDutyNormalizer(BaseNormalizer):
    """
    Normalizer for PagerDuty v3 incident webhook events.
    """
    def normalize(
        self,
        raw_payload: Dict[str, Any],
        category: str,
        provider: str
    ) -> SDLCEvent:
        event_data = raw_payload.get("event") or raw_payload
        event_type = (event_data.get("event_type") or raw_payload.get("event_type") or "incident.triggered").lower()
        incident = event_data.get("data") or raw_payload.get("incident") or {}
        
        title = incident.get("title") or incident.get("summary") or "Production Incident"
        service = incident.get("service", {}).get("summary") or "prod-service"

        if "triggered" in event_type:
            evt = SDLCEventType.INCIDENT_CREATED
            delta = -20.0
            risk = SDLCRiskLevel.CRITICAL
            msg = f"PagerDuty CRITICAL Incident triggered for {service}: {title}"
        elif "resolved" in event_type:
            evt = SDLCEventType.INCIDENT_RESOLVED
            delta = 10.0
            risk = SDLCRiskLevel.LOW
            msg = f"PagerDuty Incident resolved for {service}: {title}"
        else:
            evt = SDLCEventType.ISSUE_UPDATED
            delta = 0.0
            risk = SDLCRiskLevel.MEDIUM
            msg = f"PagerDuty Incident updated ({event_type}): {title}"

        return SDLCEvent(
            source="pagerduty",
            category=SDLCCategory.OBSERVABILITY,
            event_type=evt,
            repository=str(service),
            actor=SDLCActor(name="pagerduty-bot"),
            payload=raw_payload,
            health_impact=SDLCHealthImpact(
                score_delta=delta,
                risk_level=risk,
                message=msg
            )
        )


class NewRelicNormalizer(BaseNormalizer):
    """
    Normalizer for New Relic APM and Infrastructure incident alerts.
    """
    def normalize(
        self,
        raw_payload: Dict[str, Any],
        category: str,
        provider: str
    ) -> SDLCEvent:
        state = (raw_payload.get("current_state") or raw_payload.get("state") or "open").lower()
        condition_name = raw_payload.get("condition_name") or raw_payload.get("policy_name") or "APM Alert"
        target = raw_payload.get("targets", [{}])[0].get("name") if isinstance(raw_payload.get("targets"), list) else "newrelic-app"

        if state in ("open", "active", "triggered"):
            evt = SDLCEventType.INCIDENT_CREATED
            delta = -10.0
            risk = SDLCRiskLevel.HIGH
            msg = f"New Relic Incident OPEN for {target}: {condition_name}"
        else:
            evt = SDLCEventType.INCIDENT_RESOLVED
            delta = 8.0
            risk = SDLCRiskLevel.LOW
            msg = f"New Relic Incident CLOSED for {target}: {condition_name}"

        return SDLCEvent(
            source="newrelic",
            category=SDLCCategory.OBSERVABILITY,
            event_type=evt,
            repository=str(target),
            actor=SDLCActor(name="newrelic-bot"),
            payload=raw_payload,
            health_impact=SDLCHealthImpact(
                score_delta=delta,
                risk_level=risk,
                message=msg
            )
        )



