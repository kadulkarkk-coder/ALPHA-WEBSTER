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
from core.voice.manager import VoiceManager


class Runtime:
    """Stores every long-lived Webster runtime subsystem."""

    def __init__(self) -> None:
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
        self._voice: VoiceManager | None = None
        self._application = None
        self._initialized = False
        self._running = False

    @property
    def services(self):
        return self._services

    @services.setter
    def services(self, value):
        self._services = value

    @property
    def provider(self):
        return self._provider

    @provider.setter
    def provider(self, value):
        self._provider = value

    @property
    def providers(self):
        return self._provider

    @property
    def capability_engine(self):
        return self._capability_engine

    @capability_engine.setter
    def capability_engine(self, value):
        self._capability_engine = value

    @property
    def capabilities(self):
        return self._capability_engine

    @property
    def planning_engine(self):
        return self._planning_engine

    @planning_engine.setter
    def planning_engine(self, value):
        self._planning_engine = value

    @property
    def planning(self):
        return self._planning_engine

    @property
    def ai(self):
        return self._ai

    @ai.setter
    def ai(self, value):
        self._ai = value

    @property
    def ai_engine(self):
        return self._ai

    @ai_engine.setter
    def ai_engine(self, value):
        self._ai = value

    @property
    def memory(self):
        return self._memory

    @memory.setter
    def memory(self, value):
        self._memory = value

    @property
    def conversation(self):
        return self._conversation

    @conversation.setter
    def conversation(self, value):
        self._conversation = value

    @property
    def plugins(self):
        return self._plugins

    @plugins.setter
    def plugins(self, value):
        self._plugins = value

    @property
    def events(self):
        return self._events

    @events.setter
    def events(self, value):
        self._events = value

    @property
    def messaging(self):
        return self._messaging

    @messaging.setter
    def messaging(self, value):
        self._messaging = value

    @property
    def voice(self):
        return self._voice

    @voice.setter
    def voice(self, value):
        self._voice = value

    @property
    def application(self):
        return self._application

    @application.setter
    def application(self, value):
        self._application = value

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

    def initialize(self) -> None:
        if self._initialized:
            return
        self._initialized = True

    def start(self) -> None:
        if self._running:
            return
        if not self._initialized:
            self.initialize()
        self._running = True

    def shutdown(self) -> None:
        if not self._running:
            return
        self._running = False

    def clear(self) -> None:
        self._planning_engine = None
        self._capability_engine = None
        self._ai = None
        self._memory = None
        self._conversation = None
        self._plugins = None
        self._events = None
        self._messaging = None
        self._provider = None
        self._voice = None

        if self._services is not None:
            self._services.clear()

        self._services = None
        self._application = None
        self._initialized = False
        self._running = False

    @property
    def provider_count(self) -> int:
        if self._provider is None:
            return 0
        return self._provider.provider_count

    @property
    def capability_count(self) -> int:
        if self._capability_engine is None:
            return 0
        return self._capability_engine.capability_count()

    @property
    def workflow_count(self) -> int:
        if self._planning_engine is None:
            return 0
        return self._planning_engine.workflow_count

    @property
    def component_count(self) -> int:
        return sum(
            value is not None
            for value in (
                self._services,
                self._provider,
                self._capability_engine,
                self._planning_engine,
                self._ai,
                self._memory,
                self._conversation,
                self._plugins,
                self._events,
                self._messaging,
                self._voice,
            )
        )

    def health(self) -> dict:
        return {
            "initialized": self._initialized,
            "running": self._running,
            "healthy": self.ready,
            "components": {
                "services": self.services is not None,
                "provider": self.provider is not None,
                "memory": self.memory is not None,
                "conversation": self.conversation is not None,
                "plugins": self.plugins is not None,
                "events": self.events is not None,
                "messaging": self.messaging is not None,
                "voice": self.voice is not None,
                "capabilities": self.capability_engine is not None,
                "planning": self.planning_engine is not None,
                "ai": self.ai is not None,
            },
        }

    def __repr__(self) -> str:
        return (
            f"Runtime(initialized={self._initialized}, "
            f"running={self._running})"
        )
