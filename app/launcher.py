"""
WEBSTER ALPHA

Application Launcher
"""

from __future__ import annotations

from app.runtime import Runtime

from core.capability.browser.back import BackCapability
from core.capability.browser.open_url import OpenUrlCapability
from core.capability.browser.refresh import RefreshCapability
from core.capability.file.create_folder import CreateFolderCapability
from core.capability.file.delete import DeleteFileCapability
from core.capability.file.rename import RenameFileCapability
from core.capability.registry import CapabilityRegistry
from core.container.service_registry import ServiceRegistry
from core.planning.analyzer import GoalAnalyzer
from core.planning.decomposer import TaskDecomposer
from core.capability.engine import CapabilityEngine
from core.capability.manager import CapabilityManager
from core.planning.engine import PlanningEngine
from core.planning.manager import PlanningManager
from core.planning.planner import Planner
from core.planning.validator import Validator
from core.planning.executor import Executor
from core.ai.engine import AIEngine
from core.ai.router import IntentRouter
from core.ai.goal_builder import GoalBuilder
from core.ai.response_builder import ResponseBuilder
from core.memory.manager import MemoryManager
from core.conversation.manager import ConversationManager
from core.plugins.manager import PluginManager
from core.events.event_bus import EventBus
from core.messaging.manager import MessagingManager
from core.provider.ollama import OllamaProvider
from core.provider.manager import ProviderManager


class Launcher:
    """Responsible for constructing and bootstrapping Webster."""

    def __init__(self) -> None:
        """Construct all long-lived Webster objects."""

        self._initialized = False
        self._running = False

        self._runtime = Runtime()

        self.event_bus = EventBus()
        self.service_registry = ServiceRegistry()
        self.plugin_manager = PluginManager()
        self.messaging_manager = MessagingManager()

        self.memory_manager = MemoryManager(
            event_bus=self.event_bus,
        )

        self.conversation_manager = ConversationManager(
            memory=self.memory_manager,
            event_bus=self.event_bus,
        )

        self.capability_registry = CapabilityRegistry()

        self.capability_manager = CapabilityManager(
            registry=self.capability_registry,
        )

        self.capability_engine = CapabilityEngine(
            registry=self.capability_registry,
            manager=self.capability_manager,
            event_bus=self.event_bus,
        )

        # Planning must validate against the same registry used by
        # CapabilityEngine. There must be one capability source of truth.
        self.plan_registry = self.capability_registry

        self.planning_manager = PlanningManager()

        self._planner = Planner(
            registry=self.plan_registry,
        )

        self.validator = Validator(
            registry=self.plan_registry,
        )

        self.executor = Executor(
            capability_engine=self.capability_engine,
        )

        self.goal_analyzer = GoalAnalyzer()
        self.task_decomposer = TaskDecomposer()

        self.planning_engine = PlanningEngine(
            capability_engine=self.capability_engine,
            manager=self.planning_manager,
            planner=self._planner,
            validator=self.validator,
            executor=self.executor,
            analyzer=self.goal_analyzer,
            decomposer=self.task_decomposer,
            event_bus=self.event_bus,
            registry=self.plan_registry,
        )

        self.provider_manager = ProviderManager()
        self.provider = OllamaProvider()

        self.intent_router = IntentRouter()
        self.goal_builder = GoalBuilder()
        self.response_builder = ResponseBuilder()

        self.ai_engine = AIEngine(
            provider_manager=self.provider_manager,
            planning_engine=self.planning_engine,
            capability_engine=self.capability_engine,
            memory_manager=self.memory_manager,
            conversation_manager=self.conversation_manager,
            router=self.intent_router,
            goal_builder=self.goal_builder,
            response_builder=self.response_builder,
        )

        self._runtime.ai = self.ai_engine
        self._runtime.memory = self.memory_manager
        self._runtime.conversation = self.conversation_manager
        self._runtime.capability_engine = self.capability_engine
        self._runtime.planning_engine = self.planning_engine
        self._runtime.plugins = self.plugin_manager
        self._runtime.events = self.event_bus
        self._runtime.messaging = self.messaging_manager
        self._runtime.services = self.service_registry

    # =====================================================
    # Initialization
    # =====================================================

    def initialize(self) -> None:
        """Initialize Webster exactly once."""

        if self._initialized:
            return

        self._runtime.initialize()

        self.service_registry.initialize()
        self.provider_manager.initialize()
        self.plugin_manager.initialize()
        self.memory_manager.initialize()
        self.conversation_manager.initialize()
        self.messaging_manager.initialize()
        self.event_bus.initialize()

        self._register_services()
        self._register_providers()
        self._register_capabilities()
        self._register_workflows()

        self.capability_engine.initialize()
        self.planning_engine.initialize()
        self.ai_engine.initialize()

        self._runtime.services = self.service_registry
        self._runtime.provider = self.provider_manager
        self._runtime.memory = self.memory_manager
        self._runtime.conversation = self.conversation_manager
        self._runtime.plugins = self.plugin_manager
        self._runtime.events = self.event_bus
        self._runtime.messaging = self.messaging_manager
        self._runtime.capability_engine = self.capability_engine
        self._runtime.planning_engine = self.planning_engine
        self._runtime.ai = self.ai_engine

        if self._runtime.application is None:
            from app.application import Application

            # Runtime owns the application reference. Launcher exposes it
            # through the read-only application property below.
            self._runtime.application = Application(
                runtime=self._runtime,
            )

        self._initialized = True

    # =====================================================
    # Registration
    # =====================================================

    def _register_services(self) -> None:
        """Register all Webster services."""

        self.service_registry.register(
            "provider_manager",
            self.provider_manager,
        )

        self.service_registry.register(
            "memory_manager",
            self.memory_manager,
        )

        self.service_registry.register(
            "conversation_manager",
            self.conversation_manager,
        )

        self.service_registry.register(
            "capability_engine",
            self.capability_engine,
        )

        self.service_registry.register(
            "planning_engine",
            self.planning_engine,
        )

        self.service_registry.register(
            "ai_engine",
            self.ai_engine,
        )

        self.service_registry.register(
            "plugin_manager",
            self.plugin_manager,
        )

        self.service_registry.register(
            "event_bus",
            self.event_bus,
        )

        self.service_registry.register(
            "messaging_manager",
            self.messaging_manager,
        )

    def _register_providers(self) -> None:
        """Register AI providers."""

        self.provider_manager.register(
            self.provider,
        )

        self.provider_manager.set_default(
            self.provider.name,
        )

    def _register_capabilities(self) -> None:
        """Register all currently implemented capabilities."""

        self.capability_engine.register(
            OpenUrlCapability()
        )

        self.capability_engine.register(
            RefreshCapability()
        )

        self.capability_engine.register(
            BackCapability()
        )

        self.capability_engine.register(
            CreateFolderCapability()
        )

        self.capability_engine.register(
            DeleteFileCapability()
        )

        self.capability_engine.register(
            RenameFileCapability()
        )

    def _register_workflows(self) -> None:
        """Register Webster workflows."""

        pass

    # =====================================================
    # Lifecycle
    # =====================================================

    def start(self) -> None:
        """Start Webster."""

        if self._running:
            return

        if not self._initialized:
            self.initialize()

        self._runtime.start()
        self._running = True

    def shutdown(self) -> None:
        """Shutdown Webster."""

        if not self._running:
            return

        self.ai_engine.shutdown()
        self.planning_engine.shutdown()
        self.capability_engine.shutdown()
        self.provider_manager.shutdown()
        self.plugin_manager.shutdown()
        self.messaging_manager.shutdown()
        self.conversation_manager.shutdown()
        self.memory_manager.shutdown()
        self._runtime.shutdown()

        self._running = False

    def restart(self) -> None:
        """Restart Webster."""

        self.shutdown()
        self.start()

    # =====================================================
    # State
    # =====================================================

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    # =====================================================
    # Health
    # =====================================================

    def health(self) -> dict:
        """Return the overall health of Webster."""

        return {
            "initialized": self._initialized,
            "running": self._running,
            "runtime": self._runtime.health(),
            "providers": self.provider_manager.health(),
            "planning": self.planning_engine.health(),
            "capabilities": self.capability_engine.health(),
            "memory": self.memory_manager.health(),
            "conversation": self.conversation_manager.health(),
            "services": self.service_registry.health(),
            "plugins": self.plugin_manager.health(),
        }

    # =====================================================
    # Statistics
    # =====================================================

    @property
    def service_count(self) -> int:
        return self.service_registry.service_count

    @property
    def provider_count(self) -> int:
        return self.provider_manager.provider_count

    @property
    def capability_count(self) -> int:
        return self.capability_engine.capability_count()

    @property
    def workflow_count(self) -> int:
        return self.planning_engine.workflow_count

    @property
    def component_count(self) -> int:
        return (
            self.service_count
            + self.provider_count
            + self.capability_count
            + self.workflow_count
        )

    # =====================================================
    # Runtime Access
    # =====================================================

    @property
    def ai(self):
        return self.ai_engine

    @property
    def planner(self):
        return self.planning_engine

    @property
    def capabilities(self):
        return self.capability_engine

    @property
    def providers(self):
        return self.provider_manager

    @property
    def services(self):
        return self.service_registry

    @property
    def application(self):
        return self._runtime.application

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return (
            "Launcher("
            f"running={self._running}, "
            f"initialized={self._initialized}, "
            f"services={self.service_count}, "
            f"providers={self.provider_count}, "
            f"capabilities={self.capability_count}"
            ")"
        )
