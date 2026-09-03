"""
Canonical SDLC Event Schema Definitions
"""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, Optional
import time
import uuid


class SDLCCategory(str, Enum):
    CODE = "code"
    BUILD = "build"
    DEPLOY = "deploy"
    TICKET = "ticket"
    INFRA_HEALTH = "infra_health"
    SECURITY_QUALITY = "security_quality"
    TESTING = "testing"
    OBSERVABILITY = "observability"


class SDLCRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SDLCEventType(str, Enum):
    # SCM / Code Events
    COMMIT_PUSHED = "commit_pushed"
    PR_OPENED = "pr_opened"
    PR_MERGED = "pr_merged"
    PR_CLOSED = "pr_closed"
    
    # CI/CD & Build Events
    BUILD_STARTED = "build_started"
    BUILD_PASSED = "build_passed"
    BUILD_FAILED = "build_failed"
    
    # Deployment & Infrastructure Events
    DEPLOY_STARTED = "deploy_started"
    DEPLOY_SUCCESS = "deploy_success"
    DEPLOY_FAILED = "deploy_failed"
    K8S_POD_CRASH = "k8s_pod_crash"
    
    # Ticket / Project Events
    ISSUE_CREATED = "issue_created"
    ISSUE_UPDATED = "issue_updated"
    ISSUE_BLOCKED = "issue_blocked"
    
    # Observability & Monitoring Events
    INCIDENT_CREATED = "incident_created"
    INCIDENT_RESOLVED = "incident_resolved"
    SECURITY_ALERT = "security_alert"
    
    # Security / Quality / Testing
    QUALITY_GATE_FAILED = "quality_gate_failed"
    TESTS_PASSED = "tests_passed"
    TESTS_FAILED = "tests_failed"
    SECURITY_VULN_DETECTED = "security_vuln_detected"
    
    # Generic Fallback
    GENERIC_SIGNAL = "generic_signal"



@dataclass
class SDLCHealthImpact:
    score_delta: float = 0.0
    risk_level: SDLCRiskLevel = SDLCRiskLevel.LOW
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scoreDelta": self.score_delta,
            "riskLevel": self.risk_level.value if isinstance(self.risk_level, Enum) else self.risk_level,
            "message": self.message
        }


@dataclass
class SDLCActor:
    name: str = "system"
    email: Optional[str] = None
    username: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "email": self.email,
            "username": self.username
        }


@dataclass
class SDLCEvent:
    id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    source: str = "generic"
    category: SDLCCategory = SDLCCategory.CODE
    event_type: SDLCEventType = SDLCEventType.GENERIC_SIGNAL
    repository: str = "unknown"
    branch: Optional[str] = None
    environment: Optional[str] = None
    actor: SDLCActor = field(default_factory=SDLCActor)
    payload: Dict[str, Any] = field(default_factory=dict)
    health_impact: SDLCHealthImpact = field(default_factory=SDLCHealthImpact)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "source": self.source,
            "category": self.category.value if isinstance(self.category, Enum) else self.category,
            "eventType": self.event_type.value if isinstance(self.event_type, Enum) else self.event_type,
            "repository": self.repository,
            "branch": self.branch,
            "environment": self.environment,
            "actor": self.actor.to_dict() if hasattr(self.actor, "to_dict") else self.actor,
            "payload": self.payload,
            "healthImpact": self.health_impact.to_dict() if hasattr(self.health_impact, "to_dict") else self.health_impact
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SDLCEvent":
        actor_data = data.get("actor", {})
        if isinstance(actor_data, dict):
            actor = SDLCActor(
                name=actor_data.get("name", "system"),
                email=actor_data.get("email"),
                username=actor_data.get("username")
            )
        else:
            actor = SDLCActor(name=str(actor_data))

        impact_data = data.get("healthImpact", {})
        if isinstance(impact_data, dict):
            risk_val = impact_data.get("riskLevel", "LOW")
            try:
                risk_enum = SDLCRiskLevel(risk_val)
            except ValueError:
                risk_enum = SDLCRiskLevel.LOW
                
            impact = SDLCHealthImpact(
                score_delta=float(impact_data.get("scoreDelta", 0.0)),
                risk_level=risk_enum,
                message=str(impact_data.get("message", ""))
            )
        else:
            impact = SDLCHealthImpact()

        cat_val = data.get("category", "code")
        try:
            category_enum = SDLCCategory(cat_val)
        except ValueError:
            category_enum = SDLCCategory.CODE

        evt_val = data.get("eventType", "generic_signal")
        try:
            evt_enum = SDLCEventType(evt_val)
        except ValueError:
            evt_enum = SDLCEventType.GENERIC_SIGNAL

        return cls(
            id=data.get("id", f"evt_{uuid.uuid4().hex[:12]}"),
            timestamp=data.get("timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
            source=data.get("source", "generic"),
            category=category_enum,
            event_type=evt_enum,
            repository=data.get("repository", "unknown"),
            branch=data.get("branch"),
            environment=data.get("environment"),
            actor=actor,
            payload=data.get("payload", {}),
            health_impact=impact
        )
