"""
WEBSTER ALPHA

Application
"""

from __future__ import annotations

from datetime import datetime

from app.launcher import Launcher
from app.runtime import Runtime

from core.status.status_manager import StatusManager
from core.state.state_manager import StateManager
from core.ai.request import AIRequest
from core.messaging.message import Message
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.planning.goal import Goal
from core.memory.types import MemoryType


class Application:
    """
    Main Webster application.

    This class provides the public API for
    interacting with the Webster runtime.
    """

    VERSION = "0.1.0-alpha"

    def __init__(self) -> None:

        self._launcher = Launcher()

        self._runtime = self._launcher.runtime

        self._state = StateManager()

        self._status = StatusManager()

        self._running = False

        self._started = datetime.now()

    # =====================================================
    # Properties
    # =====================================================

    @property
    def launcher(self) -> Launcher:
        return self._launcher

    @property
    def runtime(self) -> Runtime:
        return self._runtime

    @property
    def state(self) -> StateManager:
        return self._state

    @property
    def status(self) -> StatusManager:
        return self._status

    @property
    def running(self) -> bool:
        return self._running

    @running.setter
    def running(
        self,
        value: bool,
    ) -> None:

        self._running = value

    @property
    def started(self) -> datetime:
        return self._started

    # =====================================================
    # Runtime Services
    # =====================================================

    @property
    def capabilities(self):
        """
        Webster Capability Engine.
        """

        return self.runtime.capabilities

    @property
    def planning(self):
        """
        Webster Planning Engine.
        """

        return self.runtime.planning

    # =====================================================
    # State
    # =====================================================

    @property
    def initialized(self) -> bool:
        """
        Returns True if Webster has been initialized.
        """

        return self.launcher.initialized

    @property
    def ready(self) -> bool:
        """
        Returns True if Webster is ready.
        """

        return self.launcher.ready

    # =====================================================
    # Lifecycle
    # =====================================================

    def initialize(self) -> None:
        """
        Initialize Webster.
        """

        self.launcher.initialize()

    # -----------------------------------------------------

    def start(self) -> None:
        """
        Start Webster.
        """

        if self.running:
            return

        self.initialize()

        self.running = True

        self.status.set_running(True)

    # -----------------------------------------------------

    def shutdown(self) -> None:
        """Alias for stop/shutdown all subsystems."""

        self.stop()

    # =====================================================
    # High-level APIs
    # =====================================================

    def chat(self, prompt: str) -> object:
        """Send a chat prompt through conversation -> AI -> response.

        Returns the AIResponse.
        """

        if not self.running:
            self.start()

        conv = self.runtime.conversation

        ai = self.runtime.ai

        if conv is None or ai is None:
            raise RuntimeError("Conversation or AI subsystem not available.")

        msg = Message(sender="user", receiver="ai", payload=prompt)

        conv.receive(msg)

        context = conv.build_context()

        request = AIRequest(prompt=prompt, context=context)

        return ai.generate(request)

    def plan_goal(self, goal: str | Goal) -> object:
        """Generate a plan for a goal without executing it."""

        if not self.running:
            self.start()

        planning = self.runtime.planning

        if planning is None:
            raise RuntimeError("Planning subsystem not available.")

        return planning.plan_goal(goal)

    def execute_goal(self, goal: str | Goal):
        """Execute a goal via the planning engine."""

        if not self.running:
            self.start()

        planning = self.runtime.planning

        if planning is None:
            raise RuntimeError("Planning subsystem not available.")

        return planning.execute_goal(goal)

    def execute_capability(self, capability_action: str, **kwargs) -> CapabilityResult:
        """Execute a capability by string like 'browser.open_url' and keyword args."""

        if not self.running:
            self.start()

        cap_engine = self.runtime.capabilities

        if cap_engine is None:
            raise RuntimeError("Capability subsystem not available.")

        if "." in capability_action:
            capability, action = capability_action.split(".", 1)
        else:
            capability = capability_action
            action = "run"

        step = __import__("core.planning.step", fromlist=["PlanStep"]).PlanStep(capability=capability, arguments=kwargs)

        req = CapabilityRequest(capability=capability, action=action, step=step, arguments=kwargs)

        return cap_engine.execute(req)

    def execute_workflow(self, workflow_name: str) -> list:
        """Execute a workflow (by name) through PlanningEngine."""

        if not self.running:
            self.start()

        planning_engine = self.runtime.planning

        if planning_engine is None:
            raise RuntimeError("Planning subsystem not available.")

        return planning_engine.execute_workflow(workflow_name)

    def remember_intent(self, topic: str, value: str, source: str = "user", confidence: float = 1.0) -> None:
        """Store an intent or contextual memory entry."""

        if self.runtime.memory is None:
            raise RuntimeError("Memory subsystem not available.")

        self.runtime.memory.remember(
            memory_type=MemoryType.GOAL,
            topic=topic,
            value=value,
            source=source,
            confidence=confidence,
        )

    def get_conversation_context(self) -> object:
        """Fetch the current conversation context."""

        if self.runtime.conversation is None:
            raise RuntimeError("Conversation subsystem not available.")

        return self.runtime.conversation.build_context()

    # -----------------------------------------------------

    def stop(self) -> None:
        """
        Shutdown Webster.
        """

        if not self.running:
            return

        self.running = False

        self.status.set_running(False)

        self.launcher.shutdown()

    # -----------------------------------------------------

    def restart(self) -> None:
        """
        Restart Webster.
        """

        self.stop()

        self.start()

    # =====================================================
    # Diagnostics
    # =====================================================

    def health(self) -> dict:
        """
        Returns the current health status of Webster.
        """

        return {

            "application": {

                "running": self.running,

                "started": self.started,

                "healthy": self.running,

                "version": self.VERSION,

            },

            "runtime": {

                "initialized": self.initialized,

                "ready": self.ready,

                "components": self.launcher.component_count,

                "services": self.launcher.service_count,

                "providers": self.launcher.provider_count,

                "capabilities": self.launcher.capability_count,

                "ai": self.runtime.ai.health() if self.runtime.ai is not None else None,

                "memory": {
                    "count": self.runtime.memory.count if self.runtime.memory is not None else 0,
                    "active": self.runtime.memory.active if self.runtime.memory is not None else 0,
                    "archived": self.runtime.memory.archived if self.runtime.memory is not None else 0,
                },

            },

            "planning": {

                "plans": self.launcher.plan_count,

                "workflows": self.launcher.workflow_count,

                "goals": self.launcher.planning_manager.goal_count,

                "tasks": self.launcher.planning_manager.task_count,

            },

        }

    # -----------------------------------------------------

    @property
    def is_running(self) -> bool:
        """
        Returns True if Webster is running.
        """

        return self.running

    # -----------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(version={self.VERSION!r}, "
            f"running={self.running}, "
            f"ready={self.ready})"
        )