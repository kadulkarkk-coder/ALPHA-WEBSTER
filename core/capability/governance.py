"""WEBSTER capability governance."""

from __future__ import annotations

from dataclasses import dataclass

from core.capability.availability import Availability, availability_for
from core.capability.capability import Capability
from core.capability.execution_policy import ExecutionPolicy, PolicyResult
from core.capability.permission import PermissionDecision, PermissionManager
from core.capability.request import CapabilityRequest


@dataclass(frozen=True, slots=True)
class GovernanceDecision:
    """Final pre-execution decision for a capability request."""

    allowed: bool
    reason: str
    availability: Availability
    permission: PermissionDecision
    policy: PolicyResult


class CapabilityGovernance:
    """Central preflight authority for capability execution."""

    def __init__(
        self,
        permission_manager: PermissionManager | None = None,
        execution_policy: ExecutionPolicy | None = None,
    ) -> None:
        self.permissions = permission_manager or PermissionManager()
        self.policy = execution_policy or ExecutionPolicy()

    def evaluate(
        self,
        capability: Capability,
        request: CapabilityRequest,
    ) -> GovernanceDecision:
        availability = Availability(state=availability_for(capability.status))
        permission = self.permissions.evaluate(capability, request)
        policy = self.policy.evaluate(capability, request)

        if not availability.usable:
            return GovernanceDecision(False, f"Capability is {availability.state.name.lower()}.", availability, permission, policy)
        if not permission.allowed:
            return GovernanceDecision(False, permission.reason, availability, permission, policy)
        if not policy.allowed:
            return GovernanceDecision(False, policy.reason, availability, permission, policy)
        return GovernanceDecision(True, "Capability is authorized for execution.", availability, permission, policy)

    def can_execute(self, capability: Capability, request: CapabilityRequest) -> bool:
        return self.evaluate(capability, request).allowed

    def __repr__(self) -> str:
        return "CapabilityGovernance(permissions=..., policy=...)"
