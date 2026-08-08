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




class Runtime:
    """
    Stores every long-lived runtime subsystem
    used by Webster.
    """

    def __init__(self) -> None:

        self._services: ServiceRegistry | None = None

        self._capability_engine: CapabilityEngine | None = None

        self._planning_engine: PlanningEngine | None = None

        self._ai: AIEngine | None = None

        self._memory: MemoryManager | None = None

        self._conversation: ConversationManager | None = None

        self._plugins: PluginManager | None = None

        self._events: EventBus | None = None

        self._messaging: MessagingManager | None = None

        self._initialized = False

        self._running = False

    # =====================================================
    # Capability Engine
    # =====================================================

    @property
    def capability_engine(self) -> CapabilityEngine | None:

        return self._capability_engine

    @capability_engine.setter
    def capability_engine(
        self,
        engine: CapabilityEngine | None,
    ) -> None:

        self._capability_engine = engine

    # =====================================================
    # Planning Engine
    # =====================================================

    @property
    def planning_engine(self) -> PlanningEngine | None:

        return self._planning_engine

    @planning_engine.setter
    def planning_engine(
        self,
        engine: PlanningEngine | None,
    ) -> None:

        self._planning_engine = engine

    # =====================================================
    # Convenience Aliases
    # =====================================================

    @property
    def capabilities(self) -> CapabilityEngine | None:

        return self._capability_engine

    @property
    def planning(self) -> PlanningEngine | None:

        return self._planning_engine

    # =====================================================
    # Service Registry
    # =====================================================

    @property
    def services(self) -> ServiceRegistry | None:

        return self._services

    @services.setter
    def services(self, registry: ServiceRegistry | None) -> None:

        self._services = registry

    # =====================================================
    # AI
    # =====================================================

    @property
    def ai(self) -> AIEngine | None:

        return self._ai

    @ai.setter
    def ai(self, engine: AIEngine | None) -> None:

        self._ai = engine

    @property
    def ai_engine(self) -> AIEngine | None:

        return self._ai

    @ai_engine.setter
    def ai_engine(self, engine: AIEngine | None) -> None:

        self._ai = engine

    # =====================================================
    # Memory
    # =====================================================

    @property
    def memory(self) -> MemoryManager | None:

        return self._memory

    @memory.setter
    def memory(self, manager: MemoryManager | None) -> None:

        self._memory = manager

    # =====================================================
    # Conversation
    # =====================================================

    @property
    def conversation(self) -> ConversationManager | None:

        return self._conversation

    @conversation.setter
    def conversation(self, manager: ConversationManager | None) -> None:

        self._conversation = manager

    # =====================================================
    # Plugins
    # =====================================================

    @property
    def plugins(self) -> PluginManager | None:

        return self._plugins

    @plugins.setter
    def plugins(self, manager: PluginManager | None) -> None:

        self._plugins = manager

    # =====================================================
    # Events
    # =====================================================

    @property
    def events(self) -> EventBus | None:

        return self._events

    @events.setter
    def events(self, bus: EventBus | None) -> None:

        self._events = bus

    # =====================================================
    # Messaging
    # =====================================================

    @property
    def messaging(self) -> MessagingManager | None:

        return self._messaging

    @messaging.setter
    def messaging(self, manager: MessagingManager | None) -> None:

        self._messaging = manager

    # =====================================================
    # Runtime State
    # =====================================================

    @property
    def initialized(self) -> bool:
        """
        Returns True when all required runtime
        services are available.
        """

        return (
            self._services is not None
            and self._capability_engine is not None
            and self._planning_engine is not None
            and self._ai is not None
            and self._initialized is not None
            and self._memory is not None
            and self._conversation is not None
            and self._events is not None
            and self._messaging is not None
            and self._plugins is not None
        )

    # -----------------------------------------------------

    @property
    def running(
        self,
    ) -> bool:

        return self._running

    # -----------------------------------------------------

    @property
    def ready(
        self,
    ) -> bool:

        return (

            self._initialized

            and self._running

        )

    @property
    def is_healthy(
        self,
    ) -> bool:

        return self.ready

    # =====================================================
    # Lifecycle
    # =====================================================

    def initialize(
        self,
    ) -> None:
        """
        Initialize the Webster runtime container.

        Runtime initialization prepares the runtime itself.
        Individual subsystems are initialized by Launcher.
        """

        if self._initialized:

            return

        #
        # Ensure the runtime state exists.
        #

        if not hasattr(
            self,
            "services",
        ):

            self.services = None

        if not hasattr(
            self,
            "provider",
        ):

            self.provider = None

        if not hasattr(
            self,
            "memory",
        ):

            self.memory = None

        if not hasattr(
            self,
            "conversation",
        ):

            self.conversation = None

        if not hasattr(
            self,
            "plugins",
        ):

            self.plugins = None

        if not hasattr(
            self,
            "events",
        ):

            self.events = None

        if not hasattr(
            self,
            "messaging",
        ):

            self.messaging = None

        if not hasattr(
            self,
            "capability_engine",
        ):

            self.capability_engine = None

        if not hasattr(
            self,
            "planning_engine",
        ):

            self.planning_engine = None

        if not hasattr(
            self,
            "ai",
        ):

            self.ai = None

        self._initialized = True

    # -----------------------------------------------------

    def start(
        self,
    ) -> None:
        """
        Start the Webster runtime.
        """

        if self._running:

            return

        if not self._initialized:

            self.initialize()

        self._running = True

    # -----------------------------------------------------

    def shutdown(
        self,
    ) -> None:
        """
        Stop the Webster runtime.

        Runtime shutdown only changes runtime state.
        Individual subsystems are shut down by Launcher.
        """

        if not self._running:

            return

        self._running = False



    
    # -----------------------------------------------------

    def clear(self) -> None:
        """
        Clears every runtime subsystem.
        """

        self._planning_engine = None

        self._capability_engine = None

        if self._services is not None:
            self._services.clear()

        self._services = None

    # =====================================================
    # Health
    # =====================================================

    def health(
        self,
    ) -> dict:
        """
        Return the current runtime health.
        """

        components = {

            "services": self.services is not None,

            "provider": self.provider is not None,

            "memory": self.memory is not None,

            "conversation": (
                self.conversation is not None
            ),

            "plugins": self.plugins is not None,

            "events": self.events is not None,

            "messaging": (
                self.messaging is not None
            ),

            "capabilities": (
                self.capability_engine is not None
            ),

            "planning": (
                self.planning_engine is not None
            ),

            "ai": self.ai is not None,

        }

        return {

            "initialized": self._initialized,

            "running": self._running,

            "healthy": self.ready,

            "components": components,

        }

    # -----------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(initialized={self.initialized})"
        )

