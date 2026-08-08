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
from core.capability.packs import application
from core.capability.registry import CapabilityRegistry
from core.container.service_registry import ServiceRegistry
from core.planning import analyzer, decomposer
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
from core.memory.manager import MemoryManager
from core.conversation.manager import ConversationManager
from core.plugins.manager import PluginManager
from core.events.event_bus import EventBus
from core.messaging.manager import MessagingManager
from core.provider.ollama import OllamaProvider
from core.provider.manager import ProviderManager

# =====================================================
# AI COMPONENTS
# =====================================================

from core.ai.router import IntentRouter

from core.ai.goal_builder import GoalBuilder

from core.ai.response_builder import ResponseBuilder

from core.ai.engine import AIEngine

from core.provider.ollama import OllamaProvider



class Launcher:
    """
    Responsible for constructing and bootstrapping
    every Webster runtime subsystem.
    """

    # =====================================================
    # Construction
    # =====================================================
    # =====================================================
    # Construction
    # =====================================================

    def __init__(
        self,
    ) -> None:
        """
        Construct every long-lived Webster object.

        Objects are CREATED here only.

        Registration and initialization happen
        inside initialize().
        """

        #
        # -------------------------------------------------
        # State
        # -------------------------------------------------
        #

        self._initialized = False

        self._running = False

        #
        # -------------------------------------------------
        # Runtime
        # -------------------------------------------------
        #

        self._runtime = Runtime()

        self._application = None

        #
        # -------------------------------------------------
        # Infrastructure
        # -------------------------------------------------
        #

        self.event_bus = EventBus()

        self.service_registry = ServiceRegistry()

        self.plugin_manager = PluginManager()

        self.messaging_manager = MessagingManager()

        #
        # -------------------------------------------------
        # Memory & Conversation
        # -------------------------------------------------
        #

        self.memory_manager = MemoryManager(

            event_bus=self.event_bus,

        )

        self.conversation_manager = ConversationManager(

            memory=self.memory_manager,

            event_bus=self.event_bus,

        )

        #
        # -------------------------------------------------
        # Capability System
        # -------------------------------------------------
        #

        self.capability_registry = CapabilityRegistry()

        self.capability_manager = CapabilityManager(
            registry=self.capability_registry,
        )

        self.capability_engine = CapabilityEngine(

            registry=self.capability_registry,
            
            manager=self.capability_manager,

            event_bus=self.event_bus,

        )

        #
        # -------------------------------------------------
        # Planning System
        # -------------------------------------------------
        #

        self.plan_registry = CapabilityRegistry()

        self.planning_manager = PlanningManager()

        self._planner = Planner(

            registry=self.plan_registry,

        )

        self.validator = Validator(registry=self.plan_registry)

        self.executor = Executor(capability_engine=self.capability_engine)

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
            registry=self.plan_registry

        )

        #
        # -------------------------------------------------
        # Provider System
        # -------------------------------------------------
        #

        self.provider_manager = ProviderManager()
        self.provider = OllamaProvider()

        #
        # -------------------------------------------------
        # AI Components
        # -------------------------------------------------
        #

        self.intent_router = IntentRouter()

        self.goal_builder = GoalBuilder()

        self.response_builder = ResponseBuilder()

        #
        # -------------------------------------------------
        # AI Engine
        # -------------------------------------------------
        #

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

        #
        # -------------------------------------------------
        # Runtime Wiring
        # -------------------------------------------------
        #

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

    def initialize(
        self,
    ) -> None:
        """
        Initialize Webster.

        This method performs all registrations and
        subsystem initialization exactly once.
        """

        if self._initialized:

            return

        #
        # Runtime
        #

        self._runtime.initialize()

        self.service_registry.initialize()

        self.provider_manager.initialize()

        self.plugin_manager.initialize()

        self.memory_manager.initialize()

        self.conversation_manager.initialize()

        self.messaging_manager.initialize()

        self.event_bus.initialize()

        self.capability_engine.initialize()

        self.planning_engine.initialize()

        self.ai_engine.initialize()


        #
        # Register Core Services
        #

        self._register_services()

        #
        # Register Providers
        #

        self._register_providers()

        #
        # Register Capabilities
        #

        self._register_capabilities()

        #
        # Register Workflows
        #

        self._register_workflows()

        #
        # Runtime Wiring
        #

        self._runtime.services = self.service_registry

        self._runtime.memory = self.memory_manager

        self._runtime.conversation = self.conversation_manager

        self._runtime.plugins = self.plugin_manager

        self._runtime.events = self.event_bus

        self._runtime.messaging = self.messaging_manager

        self._runtime.capability_engine = self.capability_engine

        self._runtime.planning_engine = self.planning_engine

        self._runtime.ai = self.ai_engine

        #
        # Application
        #

        if getattr(

            self._runtime,

            "application",

            None,

        ) is None:

            from app.application import Application

            self.application = Application(

                runtime=self._runtime,

            )

        #
        # Finished
        #

        self._initialized = True

    # =====================================================
    # Registration
    # =====================================================

    def _register_services(
        self,
    ) -> None:
        """
        Register all Webster services.
        """

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

    # -----------------------------------------------------

    def _register_providers(
        self,
    ) -> None:
        """
        Register AI providers.
        """

        from core.provider.ollama import OllamaProvider

        provider = OllamaProvider()

        self.provider_manager.register(

            provider,

        )

        self.provider_manager.set_default(

            provider.name,

        )

        #
        # Future Providers
        #

        # self.provider_manager.register(
        #     GeminiProvider(...)
        # )

        # self.provider_manager.register(
        #     OpenAIProvider(...)
        # )

    # ---------------------------------------------------------

    def _register_capabilities(
        self,
    ) -> None:
        """
        Register all capabilities.
        """

        #
        # Browser
        #

        self.capability_engine.register(
            OpenUrlCapability()
        )

        self.capability_engine.register(
            RefreshCapability()
        )

        self.capability_engine.register(
            BackCapability()
        )

        #
        # File
        #

        self.capability_engine.register(
            CreateFolderCapability()
        )

        self.capability_engine.register(
            DeleteFileCapability()
        )

        self.capability_engine.register(
            RenameFileCapability()
        )

        #
        # System
        #

        # self.capability_engine.register(
        #     ShutdownCapability()
        # )

        # self.capability_engine.register(
        #     RestartCapability()
        # )

    # ---------------------------------------------------------

    def _register_workflows(
        self,
    ) -> None:
        """
        Register Webster workflows.
        """

        #
        # Reserved for Sprint 36+
        #

        pass

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def start(
        self,
    ) -> None:
        """
        Start Webster.
        """

        if self._running:

            return

        if not self._initialized:

            self.initialize()

        #
        # Runtime
        #

        self._runtime.start()

        #
        # Managers
        #

        self.provider_manager.initialize()

        self.memory_manager.initialize()

        self.conversation_manager.initialize()

        self.messaging_manager.initialize()

        self.plugin_manager.initialize()

        #
        # Engines
        #

        self.capability_engine.initialize()

        self.planning_engine.initialize()

        self.ai_engine.initialize()

        #
        # Status
        #

        self._running = True

    # ---------------------------------------------------------

    def shutdown(
        self,
    ) -> None:
        """
        Shutdown Webster.
        """

        if not self._running:

            return

        #
        # AI
        #

        self.ai_engine.shutdown()

        #
        # Engines
        #

        self.planning_engine.shutdown()

        self.capability_engine.shutdown()

        #
        # Managers
        #

        self.provider_manager.shutdown()

        self.plugin_manager.shutdown()

        self.messaging_manager.shutdown()

        self.conversation_manager.shutdown()

        self.memory_manager.shutdown()

        #
        # Runtime
        #

        self._runtime.shutdown()

        #
        # Status
        #

        self.running = False

    # ---------------------------------------------------------

    def restart(
        self,
    ) -> None:
        """
        Restart Webster.
        """

        self.shutdown()

        self.start()

    # ---------------------------------------------------------

    @property
    def is_running(
        self,
    ) -> bool:

        return self.running

    @property
    def is_initialized(
        self,
    ) -> bool:

        return self._initialized

    # ---------------------------------------------------------
    # Health
    # ---------------------------------------------------------

    def health(
        self,
    ) -> dict:
        """
        Return the overall health of Webster.
        """

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

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    @property
    def service_count(
        self,
    ) -> int:

        return self.service_registry.service_count

    @property
    def provider_count(
        self,
    ) -> int:

        return self.provider_manager.provider_count

    @property
    def capability_count(
        self,
    ) -> int:

        return self.capability_engine.capability_count

    @property
    def workflow_count(
        self,
    ) -> int:

        return self.planning_engine.workflow_count

    @property
    def component_count(
        self,
    ) -> int:

        return (

            self.service_count

            + self.provider_count

            + self.capability_count

            + self.workflow_count

        )

    # ---------------------------------------------------------
    # Runtime Access
    # ---------------------------------------------------------

    @property
    def ai(
        self,
    ):

        return self.ai_engine

    @property
    def planner(
        self,
    ):

        return self.planning_engine

    @property
    def capabilities(
        self,
    ):

        return self.capability_engine

    @property
    def providers(
        self,
    ):

        return self.provider_manager

    @property
    def services(
        self,
    ):

        return self.service_registry

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return (

            "Launcher("

            f"running={self._running}, "

            f"initialized={self._initialized}, "

            f"services={self.service_count}, "

            f"providers={self.provider_count}, "

            f"capabilities={self.capability_count}"

            ")"

        )