"""
WEBSTER ALPHA

Application Runtime
"""

from __future__ import annotations

from core.capability.engine import CapabilityEngine
from core.planning.engine import PlanningEngine
from core.container.service_registry import ServiceRegistry
from core.ai.engine import AIEngine
from core.conversation.manager import ConversationManager
from core.memory.manager import MemoryManager
from core.plugins.manager import PluginManager
from core.events.event_bus import EventBus
from core.messaging.manager import MessagingManager
from core.provider.manager import ProviderManager


class Runtime:
    """Stores every long-lived Webster runtime subsystem."""

    def __init__(
        self,
    ) -> None:

        self._services: ServiceRegistry | None = None
        self._provider: ProviderManager | None = None
        self._capability_engine: CapabilityEngine | None = None
        self._planning_engine: PlanningEngine | None = None
        self._ai: AIEngine | None = None
        self._memory: MemoryManager | None = None
        self._conversation: ConversationManager | None = None
        self._plugins: PluginManager | None = None
        self._events: EventBus | None = None
        self._messaging: MessagingManager | None = None
        self._application = None
        self._initialized = False
        self._running = False

    # =====================================================
    # Subsystem Access
    # =====================================================

    @property
    def services(self) -> ServiceRegistry | None:
        return self._services

    @services.setter
    def services(self, value: ServiceRegistry | None) -> None:
        self._services = value

    @property
    def provider(self) -> ProviderManager | None:
        return self._provider

    @provider.setter
    def provider(self, value: ProviderManager | None) -> None:
        self._provider = value

    @property
    def capability_engine(self) -> CapabilityEngine | None:
        return self._capability_engine

    @capability_engine.setter
    def capability_engine(self, value: CapabilityEngine | None) -> None:
        self._capability_engine = value

    @property
    def capabilities(self) -> CapabilityEngine | None:
        return self._capability_engine

    @property
    def planning_engine(self) -> PlanningEngine | None:
        return self._planning_engine

    @planning_engine.setter
    def planning_engine(self, value: PlanningEngine | None) -> None:
        self._planning_engine = value

    @property
    def planning(self) -> PlanningEngine | None:
        return self._planning_engine

    @property
    def ai(self) -> AIEngine | None:
        return self._ai

    @ai.setter
    def ai(self, value: AIEngine | None) -> None:
        self._ai = value

    @property
    def ai_engine(self) -> AIEngine | None:
        return self._ai

    @ai_engine.setter
    def ai_engine(self, value: AIEngine | None) -> None:
        self._ai = value

    @property
    def memory(self) -> MemoryManager | None:
        return self._memory

    @memory.setter
    def memory(self, value: MemoryManager | None) -> None:
        self._memory = value

    @property
    def conversation(self) -> ConversationManager | None:
        return self._conversation

    @conversation.setter
    def conversation(self, value: ConversationManager | None) -> None:
        self._conversation = value

    @property
    def plugins(self) -> PluginManager | None:
        return self._plugins

    @plugins.setter
    def plugins(self, value: PluginManager | None) -> None:
        self._plugins = value

    @property
    def events(self) -> EventBus | None:
        return self._events

    @events.setter
    def events(self, value: EventBus | None) -> None:
        self._events = value

    @property
    def messaging(self) -> MessagingManager | None:
        return self._messaging

    @messaging.setter
    def messaging(self, value: MessagingManager | None) -> None:
        self._messaging = value

    @property
    def application(self):
        return self._application

    @application.setter
    def application(self, value) -> None:
        self._application = value

    # =====================================================
    # State
    # =====================================================

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def running(self) -> bool:
        return self._running

    @property
    def ready(self) -> bool:
        return self._initialized and self._running

    @property
    def is_healthy(self) -> bool:
        return self.ready

    # =====================================================
    # Lifecycle
    # =====================================================

    def initialize(
        self,
    ) -> None:
        """Initialize the runtime container itself."""

        if self._initialized:
            return

        self._initialized = True

    def start(
        self,
    ) -> None:
        """Start the runtime container."""

        if self._running:
            return

        if not self._initialized:
            self.initialize()

        self._running = True

    def shutdown(
        self,
    ) -> None:
        """Stop the runtime container."""

        if not self._running:
            return

        self._running = False

    def clear(
        self,
    ) -> None:
        """Clear runtime references."""

        self._planning_engine = None
        self._capability_engine = None
        self._ai = None
        self._memory = None
        self._conversation = None
        self._plugins = None
        self._events = None
        self._messaging = None
        self._provider = None

        if self._services is not None:
            self._services.clear()

        self._services = None
        self._application = None
        self._initialized = False
        self._running = False

    # =====================================================
    # Statistics
    # =====================================================

    @property
    def provider_count(self) -> int:
        return (
            self._provider.provider_count
            if self._provider is not None
            else 0
        )

    @property
    def capability_count(self) -> int:
        if self._capability_engine is None:
            return 0

        try:
            return self._capability_engine.capability_count()
        except Exception:
            return 0

    @property
    def workflow_count(self) -> int:
        if self._planning_engine is None:
            return 0

        return self._planning_engine.workflow_count

    @property
    def component_count(self) -> int:
        return (
            (1 if self._services is not None else 0)
            + (1 if self._provider is not None else 0)
            + (1 if self._capability_engine is not None else 0)
            + (1 if self._planning_engine is not None else 0)
            + (1 if self._ai is not None else 0)
            + (1 if self._memory is not None else 0)
            + (1 if self._conversation is not None else 0)
            + (1 if self._plugins is not None else 0)
            + (1 if self._events is not None else 0)
            + (1 if self._messaging is not None else 0)
        )

    # =====================================================
    # Health
    # =====================================================

    def health(
        self,
    ) -> dict:

        components = {
            "services": self.services is not None,
            "provider": self.provider is not None,
            "memory": self.memory is not None,
            "conversation": self.conversation is not None,
            "plugins": self.plugins is not None,
            "events": self.events is not None,
            "messaging": self.messaging is not None,
            "capabilities": self.capability_engine is not None,
            "planning": self.planning_engine is not None,
            "ai": self.ai is not None,
        }

        return {
            "initialized": self._initialized,
            "running": self._running,
            "healthy": self.ready,
            "components": components,
        }

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(initialized={self._initialized}, "
            f"running={self._running})"
        )
