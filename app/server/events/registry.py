"""
Event Registry for Provider & Category Routing
"""
from typing import Dict, Type
from app.server.events.schema import SDLCEvent
from app.server.events.normalizer import (
    BaseNormalizer,
    GenericWebhookNormalizer,
    GitHubNormalizer,
    GitLabNormalizer,
    AzureDevOpsNormalizer,
    JiraNormalizer,
    LinearNormalizer,
    JenkinsNormalizer,
    CircleCINormalizer,
    GradleNormalizer,
    PlaywrightNormalizer,
    DatadogNormalizer,
    SentryNormalizer,
    PagerDutyNormalizer,
    NewRelicNormalizer
)


class EventRegistry:
    """
    Central registry routing raw payloads to provider-specific normalizers.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventRegistry, cls).__new__(cls)
            cls._instance._normalizers: Dict[str, BaseNormalizer] = {}
            cls._instance._fallback = GenericWebhookNormalizer()
            cls._instance._register_defaults()
        return cls._instance

    def _register_defaults(self):
        self.register("github", GitHubNormalizer())
        self.register("gitlab", GitLabNormalizer())
        self.register("azure_devops", AzureDevOpsNormalizer())
        self.register("azure", AzureDevOpsNormalizer())
        self.register("jira", JiraNormalizer())
        self.register("linear", LinearNormalizer())
        self.register("jenkins", JenkinsNormalizer())
        self.register("circleci", CircleCINormalizer())
        self.register("gradle", GradleNormalizer())
        self.register("playwright", PlaywrightNormalizer())
        self.register("junit", PlaywrightNormalizer())
        self.register("datadog", DatadogNormalizer())
        self.register("sentry", SentryNormalizer())
        self.register("pagerduty", PagerDutyNormalizer())
        self.register("newrelic", NewRelicNormalizer())




    def register(self, provider: str, normalizer: BaseNormalizer):
        self._normalizers[provider.lower()] = normalizer

    def get_normalizer(self, provider: str) -> BaseNormalizer:
        return self._normalizers.get(provider.lower(), self._fallback)

    def ingest(
        self,
        raw_payload: dict,
        category: str,
        provider: str
    ) -> SDLCEvent:
        normalizer = self.get_normalizer(provider)
        return normalizer.normalize(raw_payload, category, provider)


# Global singleton instance accessor
def get_event_registry() -> EventRegistry:
    return EventRegistry()
