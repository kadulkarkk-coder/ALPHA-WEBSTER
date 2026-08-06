"""
WEBSTER ALPHA

Application Launcher
"""

from __future__ import annotations

from app.runtime import Runtime

from core.container.service_registry import ServiceRegistry

from core.capability.engine import CapabilityEngine
from core.capability.manager import CapabilityManager

from core.planning.engine import PlanningEngine
from core.planning.manager import PlanningManager
from core.planning.planner import Planner
from core.planning.validator import Validator
from core.planning.executor import Executor

from core.ai.engine import AIEngine
from core.ai.router import AIRouter
from core.memory.manager import MemoryManager
from core.conversation.manager import ConversationManager
from core.plugins.manager import PluginManager
from core.events.event_bus import EventBus
from core.messaging.manager import MessagingManager


class Launcher:
    """
    Responsible for constructing and initializing
    every runtime subsystem used by Webster.
    """

    def __init__(self) -> None:

        self._initialized = False

        # -----------------------------
        # Runtime
        # -----------------------------

        self._runtime = Runtime()

        # -----------------------------
        # Core Registries / Managers
        # -----------------------------

        self._services = ServiceRegistry()
        self._capability_manager = CapabilityManager()

        self._planning_manager = PlanningManager()

        # extra managers
        self._events = EventBus()

        self._memory_manager = MemoryManager(event_bus=self._events)

        self._conversation_manager = ConversationManager(self._memory_manager, event_bus=self._events)

        self._ai_router = AIRouter()

        self._ai_engine = AIEngine(router=self._ai_router, event_bus=self._events)

        self._plugin_manager = PluginManager()

        self._messaging = MessagingManager()

    # =====================================================
    # Properties
    # =====================================================

    @property
    def runtime(self) -> Runtime:

        return self._runtime

    @property
    def initialized(self) -> bool:

        return self._initialized

    @property
    def capability_manager(self) -> CapabilityManager:

        return self._capability_manager

    @property
    def planning_manager(self) -> PlanningManager:

        return self._planning_manager

    # =====================================================
    # Initialization
    # =====================================================

    def initialize(self) -> None:
        """
        Initialize Webster.
        """

        if self._initialized:
            return


        # create and register services and engines
        self._initialize_services()

        self._initialize_capabilities()

        self._initialize_planning()

        self._initialized = True

    # -----------------------------------------------------

    def start(self) -> None:
        """
        Start Webster.
        """

        print("Starting Webster...")

        self.initialize()

        print("Webster initialized successfully.")

    # =====================================================
    # Internal Initialization
    # =====================================================

    def _initialize_capabilities(self) -> None:
        """
        Initialize the capability subsystem.
        """

        capability_engine = CapabilityEngine(
            manager=self.capability_manager,
            event_bus=self._events,
        )

        # populate runtime
        self.runtime.capability_engine = capability_engine

        # register engine as a service
        if self.runtime.services is not None:
            self.runtime.services.register(
                "capability_engine",
                capability_engine,
                description="Capability Engine",
            )

        # Discover and register capability packs from core.capability.packs
        try:
            import pkgutil
            import importlib

            from core.capability.packs.pack import CapabilityPack
            import core.capability.packs as packs_pkg

            for finder, name, ispkg in pkgutil.iter_modules(packs_pkg.__path__):
                try:
                    module_name = f"{packs_pkg.__name__}.{name}"
                    module = importlib.import_module(module_name)

                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)

                        try:
                            if isinstance(attr, type) and issubclass(attr, CapabilityPack) and attr is not CapabilityPack:
                                pack = attr()

                                if pack.enabled:
                                    try:
                                        capability_engine.discover_and_register(pack.register)
                                    except Exception:
                                        # fallback: call register directly on manager
                                        try:
                                            pack.register(self.capability_manager.registry)
                                        except Exception:
                                            pass
                        except Exception:
                            continue
                except Exception:
                    continue
        except Exception:
            # capability pack discovery is best-effort; ignore failures
            pass

    # -----------------------------------------------------

    def _initialize_planning(self) -> None:
        """
        Initialize the planning subsystem.
        """


        # Build planner/validator/executor/analyzer/decomposer with DI
        planner = Planner(self.capability_manager.registry)

        validator = Validator(self.capability_manager.registry)

        executor = Executor(self.runtime.capabilities)

        from core.planning.analyzer import GoalAnalyzer

        from core.planning.decomposer import TaskDecomposer

        analyzer = GoalAnalyzer()

        decomposer = TaskDecomposer()

        planning_engine = PlanningEngine(
            capability_engine=self.runtime.capabilities,
            manager=self.planning_manager,
            planner=planner,
            validator=validator,
            executor=executor,
            analyzer=analyzer,
            decomposer=decomposer,
            event_bus=self._events,
        )

        self.runtime.planning_engine = planning_engine

        # register
        if self.runtime.services is not None:
            self.runtime.services.register(
                "planning_engine",
                planning_engine,
                description="Planning Engine",
            )
            # register analyzer and decomposer services
            self.runtime.services.register(
                "goal_analyzer",
                analyzer,
                description="Goal Analyzer",
            )

            self.runtime.services.register(
                "task_decomposer",
                decomposer,
                description="Task Decomposer",
            )

    # =====================================================
    # Shutdown
    # =====================================================

    def shutdown(self) -> None:
        """
        Shutdown Webster.
        """

        if not self._initialized:
            return

        self._shutdown_planning()

        self._shutdown_capabilities()

        # clear services
        if self.runtime.services is not None:
            self.runtime.services.unregister("planning_engine")
            self.runtime.services.unregister("capability_engine")
            self.runtime.services.unregister("ai_engine")

        self.runtime.ai = None
        self.runtime.planning_engine = None
        self.runtime.capability_engine = None

        self._initialized = False

    # -----------------------------------------------------

    def _shutdown_planning(self) -> None:
        """
        Shutdown the planning subsystem.
        """

        self.runtime.planning_engine = None

    # -----------------------------------------------------

    def _shutdown_capabilities(self) -> None:
        """
        Shutdown the capability subsystem.
        """

        self.runtime.capability_engine = None

        if self.runtime.services is not None:
            self.runtime.services.unregister("ai_engine")

    # -----------------------------------------------------

    def _initialize_services(self) -> None:
        """
        Initialize the central service registry and populate runtime.
        """

        self.runtime.services = self._services

        # register the registry itself
        self.runtime.services.register(
            "service_registry",
            self._services,
            description="Central service registry",
        )
        # register additional core services
        self.runtime.services.register("memory_manager", self._memory_manager, description="Memory Manager")
        self.runtime.services.register("conversation_manager", self._conversation_manager, description="Conversation Manager")
        self.runtime.services.register("ai_engine", self._ai_engine, description="AI Engine")
        self.runtime.services.register("plugin_manager", self._plugin_manager, description="Plugin Manager")
        self.runtime.services.register("event_bus", self._events, description="Event Bus")
        self.runtime.services.register("messaging", self._messaging, description="Messaging Manager")

        # populate runtime shortcuts
        self.runtime.memory = self._memory_manager
        self.runtime.conversation = self._conversation_manager
        self.runtime.ai = self._ai_engine
        self.runtime.plugins = self._plugin_manager
        self.runtime.events = self._events
        self.runtime.messaging = self._messaging

    # =====================================================
    # Runtime Statistics
    # =====================================================

    @property
    def component_count(self) -> int:
        """
        Total registered components.
        """

        return 0

    # -----------------------------------------------------

    @property
    def service_count(self) -> int:
        """
        Total registered services.
        """

        return 0

    # -----------------------------------------------------

    @property
    def provider_count(self) -> int:
        """
        Total registered providers.
        """

        if self._ai_router is None:
            return 0

        return self._ai_router.count

    # -----------------------------------------------------

    @property
    def capability_count(self) -> int:
        """
        Total registered capabilities.
        """

        engine = self.runtime.capabilities

        if engine is None:
            return 0

        if hasattr(engine, "count"):
            return engine.count

        if hasattr(engine, "capability_count"):
            return engine.capability_count

        if hasattr(engine, "manager"):

            manager = engine.manager

            if hasattr(manager, "count"):
                return manager.count

        return 0

    # -----------------------------------------------------

    @property
    def workflow_count(self) -> int:
        """
        Total active workflows.
        """

        planning = self.runtime.planning

        if planning is None:
            return 0

        if hasattr(planning, "workflow_count"):
            return planning.workflow_count

        if hasattr(planning, "manager"):

            manager = planning.manager

            if hasattr(manager, "workflow_count"):
                return manager.workflow_count

        return 0

    # -----------------------------------------------------

    @property
    def plan_count(self) -> int:
        """
        Total active plans.
        """

        planning = self.runtime.planning

        if planning is None:
            return 0

        if hasattr(planning, "plan_count"):
            return planning.plan_count

        if hasattr(planning, "manager"):

            manager = planning.manager

            if hasattr(manager, "plan_count"):
                return manager.plan_count

        return 0

    # =====================================================
    # Runtime Status
    # =====================================================

    @property
    def ready(self) -> bool:
        """
        Returns True when Webster is ready.
        """

        return (
            self.initialized
            and self.runtime.capabilities is not None
            and self.runtime.planning is not None
            and self.runtime.ai is not None
            and self.runtime.events is not None
        )

    # -----------------------------------------------------

    def health(self) -> dict:
        """
        Returns launcher health information.
        """

        return {

            "initialized": self.initialized,

            "ready": self.ready,

            "runtime": {

                "components": self.component_count,

                "services": self.service_count,

                "providers": self.provider_count,

                "capabilities": self.capability_count,

                "ai": self.runtime.ai.health() if self.runtime.ai is not None else None,

                "memory": {
                    "count": self.runtime.memory.count if self.runtime.memory is not None else 0,
                    "active": self.runtime.memory.active if self.runtime.memory is not None else 0,
                    "archived": self.runtime.memory.archived if self.runtime.memory is not None else 0,
                },

                "events": self.runtime.events.subscriber_count if self.runtime.events is not None else 0,

            },

            "planning": {

                "plans": self.plan_count,

                "workflows": self.workflow_count,

            },

        }