"""WEBSTER capability execution policy."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from core.capability.capability import Capability
from core.capability.request import CapabilityRequest


class PolicyDecision(Enum):
    ALLOW = auto()
    DENY = auto()
    ASK = auto()
    REQUIRE_CONFIRMATION = auto()


@dataclass(frozen=True, slots=True)
class PolicyResult:
    decision: PolicyDecision
    reason: str = ""

    @property
    def allowed(self) -> bool:
        return self.decision is PolicyDecision.ALLOW


class ExecutionPolicy:
    """Small, deterministic policy layer for capability execution."""

    def __init__(self, confirmation_required: set[str] | None = None) -> None:
        self._confirmation_required = set(confirmation_required or ())

    def require_confirmation(self, capability_name: str) -> None:
        self._confirmation_required.add(capability_name)

    def clear_confirmation_requirement(self, capability_name: str) -> None:
        self._confirmation_required.discard(capability_name)

    def evaluate(self, capability: Capability, request: CapabilityRequest) -> PolicyResult:
        del request  # Reserved for request-specific policy rules.
        if capability.name in self._confirmation_required:
            return PolicyResult(
                PolicyDecision.REQUIRE_CONFIRMATION,
                "This capability requires explicit confirmation.",
            )
        return PolicyResult(PolicyDecision.ALLOW)

    @property
    def confirmation_required(self) -> frozenset[str]:
        return frozenset(self._confirmation_required)
