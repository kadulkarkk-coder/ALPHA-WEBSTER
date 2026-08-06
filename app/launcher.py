"""
WEBSTER ALPHA

Application Launcher
"""

from __future__ import annotations

from app.runtime import Runtime

from core.capability.browser.back import BackCapability
from core.capability.browser.base import OpenUrlCapability
from core.capability.browser.refresh import RefreshCapability
from core.capability.file.create_folder import CreateFolderCapability
from core.capability.file.delete import DeleteFileCapability
from core.capability.file.rename import RenameFileCapability
from core.container.service_registry import ServiceRegistry

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
    Responsible for constructing and initializing
    every runtime subsystem used by Webster.
    """

    def __init__(self) -> None:
        """
        Create the Webster launcher and instantiate every
        long-lived subsystem.

        Heavy initialization is performed later by start().
        """

        #
        # Runtime
        #

        self.runtime = Runtime()

        #
        # Core Managers
        #

        self.service_registry = ServiceRegistry()

        self.provider_manager = ProviderManager()

        self.plugin_manager = PluginManager()

        self.memory_manager = MemoryManager()

        self.conversation_manager = ConversationManager()

        self.messaging_manager = MessagingManager()

        self.event_bus = EventBus()

        #
        # AI Components
        #

        self.intent_router = IntentRouter()

        self.goal_builder = GoalBuilder()

        self.response_builder = ResponseBuilder()

        #
        # Core Engines
        #

        self.capability_engine = CapabilityEngine()

        self.planning_engine = PlanningEngine()

        self.ai_engine = AIEngine(

            provider_manager=self.provider_manager,

            planning_engine=self.planning_engine,

            conversation_manager=self.conversation_manager,

            memory_manager=self.memory_manager,

            router=self.intent_router,

            goal_builder=self.goal_builder,

            response_builder=self.response_builder,

        )

        #
        # Runtime Registration
        #

        self.runtime.services = self.service_registry

        self.runtime.capability_engine = self.capability_engine

        self.runtime.planning_engine = self.planning_engine

        self.runtime.ai = self.ai_engine

        self.runtime.memory = self.memory_manager

        self.runtime.conversation = self.conversation_manager

        self.runtime.plugins = self.plugin_manager

        self.runtime.events = self.event_bus

        self.runtime.messaging = self.messaging_manager

        #
        # State
        #

        self.running = False
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

    # ---------------------------------------------------------
    # Application
    # ---------------------------------------------------------

    @property
    def application(self):

        return self.runtime.application

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------

    def initialize(
        self,
    ) -> None:
        """
        Initialize every Webster subsystem.

        This method is safe to call multiple times.
        """

        if self.initialized:

            return

        #
        # Runtime
        #

        self.runtime.initialize()

        #
        # Core Managers
        #

        self.service_registry.initialize()

        self.provider_manager.initialize()

        self.plugin_manager.initialize()

        self.memory_manager.initialize()

        self.conversation_manager.initialize()

        self.messaging_manager.initialize()

        self.event_bus.initialize()

        #
        # Engines
        #

        self.capability_engine.initialize()

        self.planning_engine.initialize()

        self.ai_engine.initialize()

        #
        # Registration
        #

        self._register_services()

        self._register_providers()

        self._register_capabilities()

        self._register_workflows()

        self._register_providers()
        
        #
        # Runtime References
        #

        self.runtime.services = self.service_registry

        self.runtime.providers = self.provider_manager

        self.runtime.capabilities = self.capability_engine

        self.runtime.planning = self.planning_engine

        self.runtime.ai = self.ai_engine

        self.runtime.memory = self.memory_manager

        self.runtime.conversation = self.conversation_manager

        self.runtime.plugins = self.plugin_manager

        self.runtime.events = self.event_bus

        self.runtime.messaging = self.messaging_manager

        #
        # Status
        #

        self.initialized = True

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def _register_services(
        self,
    ) -> None:
        """
        Register all Webster services.
        """

        #
        # Core Services
        #

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

            "messaging_manager",

            self.messaging_manager,

        )

        self.service_registry.register(

            "plugin_manager",

            self.plugin_manager,

        )

        self.service_registry.register(

            "event_bus",

            self.event_bus,

        )

        #
        # Engines
        #

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

    # ---------------------------------------------------------

    def _register_providers(
        self,
    ) -> None:
        """
        Register all AI providers.
        """

        #
        # Local Providers
        #

        self.provider_manager.register(

            OllamaProvider(),

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

        if self.running:

            return

        if not self.initialized:

            self.initialize()

        #
        # Runtime
        #

        self.runtime.start()

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

        self.running = True

    # ---------------------------------------------------------

    def shutdown(
        self,
    ) -> None:
        """
        Shutdown Webster.
        """

        if not self.running:

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

        self.runtime.shutdown()

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

        return self.initialized

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

            "initialized": self.initialized,

            "running": self.running,

            "runtime": self.runtime.health(),

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

            f"running={self.running}, "

            f"initialized={self.initialized}, "

            f"services={self.service_count}, "

            f"providers={self.provider_count}, "

            f"capabilities={self.capability_count}"

            ")"

        )