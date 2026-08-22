"""WEBSTER capability permission evaluation."""

from __future__ import annotations

from dataclasses import dataclass

from core.capability.capability import Capability
from core.capability.request import CapabilityRequest
from core.capability.types import CapabilityPermission


@dataclass(frozen=True, slots=True)
class PermissionDecision:
    """Result of checking the permissions required by a capability."""

    allowed: bool
    missing: tuple[CapabilityPermission, ...] = ()
    reason: str = ""


class PermissionManager:
    """Evaluates capability permissions without performing the operation."""

    def __init__(self, granted: set[CapabilityPermission] | None = None) -> None:
        self._granted = set(granted or {CapabilityPermission.NONE})

    def grant(self, permission: CapabilityPermission) -> None:
        self._granted.add(permission)

    def revoke(self, permission: CapabilityPermission) -> None:
        if permission != CapabilityPermission.NONE:
            self._granted.discard(permission)

    def is_granted(self, permission: CapabilityPermission) -> bool:
        return permission == CapabilityPermission.NONE or permission in self._granted

    def evaluate(self, capability: Capability, request: CapabilityRequest) -> PermissionDecision:
        del request  # Reserved for request-scoped permission policies.
        missing = tuple(
            permission
            for permission in capability.permissions
            if not self.is_granted(permission)
        )
        if missing:
            names = ", ".join(permission.name for permission in missing)
            return PermissionDecision(False, missing, f"Missing permission(s): {names}.")
        return PermissionDecision(True)

    @property
    def granted(self) -> frozenset[CapabilityPermission]:
        return frozenset(self._granted)
