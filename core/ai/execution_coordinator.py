"""WEBSTER ALPHA - coordinated AI execution path."""

from __future__ import annotations

from typing import Any

from core.ai.planning_bridge import AIPlanningBridge
from core.ai.router import Intent


class AIExecutionCoordinator:
    """Coordinates actionable AI requests without duplicating execution engines."""

    def __init__(self, bridge: AIPlanningBridge) -> None:
        if bridge is None:
            raise ValueError("AIExecutionCoordinator requires an AIPlanningBridge.")
        self._bridge = bridge
        self._executions = 0
        self._failures = 0

    def execute(self, message: str, intent: Intent) -> Any:
        try:
            result = self._bridge.execute(message, intent)
            self._executions += 1
            return result
        except Exception:
            self._failures += 1
            raise

    def health(self) -> dict[str, Any]:
        return {
            "healthy": self._failures == 0,
            "executions": self._executions,
            "failures": self._failures,
            "bridge": self._bridge.health(),
        }
