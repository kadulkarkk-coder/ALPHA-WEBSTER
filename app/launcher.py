"""WEBSTER ALPHA - Application Launcher"""

from __future__ import annotations

from app.runtime import Runtime
from core.capability.browser.back import BackCapability
from core.capability.browser.open_url import OpenUrlCapability
from core.capability.browser.refresh import RefreshCapability
from core.capability.file.create import CreateFileCapability
from core.capability.file.create_folder import CreateFolderCapability
from core.capability.file.delete_file import DeleteFileCapability
from core.capability.file.rename import RenameFileCapability
from core.capability.file.copy import CopyFileCapability
from core.capability.file.move import MoveFileCapability
from core.capability.file.read import ReadFileCapability
from core.capability.file.write import WriteFileCapability
from core.capability.file.list_directory import ListDirectoryCapability
from core.capability.file.search import SearchFilesCapability
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
from core.commands.engine import CommandEngine
from core.memory.manager import MemoryManager
from core.conversation.manager import ConversationManager
from core.plugins.manager import PluginManager
from core.events.event_bus import EventBus
from core.messaging.manager import MessagingManager
from core.provider.gemini import GeminiProvider
from core.provider.ollama import OllamaProvider
from core.provider.manager import ProviderManager
from core.voice.manager import VoiceManager
from core.file.manager import FileManager


class Launcher:
    """Construct, wire, initialize, and run Webster's core subsystems."""

    def __init__(self) -> None:
        self._initialized = False
        self._running = False
        self._runtime = Runtime()
        self.event_bus = EventBus()
        self.service_registry = ServiceRegistry()
        self.plugin_manager = PluginManager()
        self.messaging_manager = MessagingManager()
        self.memory_manager = MemoryManager(event_bus=self.event_bus)
        self.conversation_manager = ConversationManager(memory=self.memory_manager, event_bus=self.event_bus)
        self.capability_registry = CapabilityRegistry()
        self.capability_manager = CapabilityManager(registry=self.capability_registry)
        self.capability_engine = CapabilityEngine(manager=self.capability_manager, registry=self.capability_registry, event_bus=self.event_bus)
        self.planning_manager = PlanningManager()
        self._planner = Planner(registry=self.capability_registry)
        self.validator = Validator(registry=self.capability_registry)
        self.executor = Executor(capability_engine=self.capability_engine)
        self.goal_analyzer = GoalAnalyzer()
        self.task_decomposer = TaskDecomposer(registry=self.capability_registry)
        self.planning_engine = PlanningEngine(capability_engine=self.capability_engine, manager=self.planning_manager, planner=self._planner, validator=self.validator, executor=self.executor, analyzer=self.goal_analyzer, decomposer=self.task_decomposer, event_bus=self.event_bus, registry=self.capability_registry)
        self.provider_manager = ProviderManager()
        self.gemini_provider = GeminiProvider()
        self.ollama_provider = OllamaProvider()
        self.provider = self.gemini_provider
        self.intent_router = IntentRouter()
        self.goal_builder = GoalBuilder()
        self.response_builder = ResponseBuilder()
        self.command_engine = CommandEngine(router=self.intent_router, decomposer=self.task_decomposer, planner=self._planner, validator=self.validator, executor=self.executor, capability_engine=self.capability_engine, response_builder=self.response_builder)
        self.ai_engine = AIEngine(provider_manager=self.provider_manager, planning_engine=self.planning_engine, capability_engine=self.capability_engine, memory_manager=self.memory_manager, conversation_manager=self.conversation_manager, router=self.intent_router, goal_builder=self.goal_builder, response_builder=self.response_builder, command_engine=self.command_engine)
        self.voice_manager = VoiceManager()
        self.file_manager = FileManager()
        self._runtime.ai = self.ai_engine
        self._runtime.memory = self.memory_manager
        self._runtime.conversation = self.conversation_manager
        self._runtime.capability_engine = self.capability_engine
        self._runtime.planning_engine = self.planning_engine
        self._runtime.plugins = self.plugin_manager
        self._runtime.events = self.event_bus
        self._runtime.messaging = self.messaging_manager
        self._runtime.services = self.service_registry
        self._runtime.provider = self.provider_manager
        self._runtime.voice = self.voice_manager
        self._runtime.file_manager = self.file_manager

    def initialize(self) -> None:
        if self._initialized:
            return
        self._runtime.initialize()
        self.service_registry.initialize(); self.provider_manager.initialize(); self.plugin_manager.initialize(); self.memory_manager.initialize(); self.conversation_manager.initialize(); self.messaging_manager.initialize(); self.event_bus.initialize(); self.voice_manager.initialize(); self.file_manager.initialize()
        self._register_services(); self._register_providers(); self._register_capabilities(); self._register_workflows()
        self.capability_engine.initialize(); self.planning_engine.initialize(); self.ai_engine.initialize()
        # Some subsystem initializers may rebuild internal state. Reconcile the
        # authoritative registry after every initializer and before commands are used.
        self._ensure_core_capabilities()
        self.voice_manager.set_processor(self.ai_engine.chat)
        from app.application import Application
        if self._runtime.application is None:
            self._runtime.application = Application(runtime=self._runtime)
        self._initialized = True

    def _register_services(self) -> None:
        services = {"provider_manager": self.provider_manager, "memory_manager": self.memory_manager, "conversation_manager": self.conversation_manager, "capability_engine": self.capability_engine, "planning_engine": self.planning_engine, "command_engine": self.command_engine, "ai_engine": self.ai_engine, "plugin_manager": self.plugin_manager, "event_bus": self.event_bus, "messaging_manager": self.messaging_manager, "voice_manager": self.voice_manager, "file_manager": self.file_manager}
        for name, service in services.items(): self.service_registry.register(name, service)

    def _register_providers(self) -> None:
        if not self.provider_manager.has(self.gemini_provider.name): self.provider_manager.register(self.gemini_provider)
        if not self.provider_manager.has(self.ollama_provider.name): self.provider_manager.register(self.ollama_provider)
        self.provider_manager.set_default(self.gemini_provider.name)

    def _capability_objects(self):
        objects = [OpenUrlCapability(), RefreshCapability(), BackCapability()]
        for capability_type in (CreateFileCapability, CreateFolderCapability, DeleteFileCapability, RenameFileCapability, CopyFileCapability, MoveFileCapability, ReadFileCapability, WriteFileCapability, ListDirectoryCapability, SearchFilesCapability):
            objects.append(capability_type(file_manager=self.file_manager))
        return objects

    def _register_capabilities(self) -> None:
        """Register all built-in capabilities without failing on duplicates."""
        for capability in self._capability_objects():
            if not self.capability_engine.exists(capability.name):
                self.capability_engine.register(capability)

    def _ensure_core_capabilities(self) -> None:
        """Repair the shared registry if a subsystem removed a built-in capability."""
        self._register_capabilities()
        required = {"open_url", "create_file", "create_folder", "delete_file", "rename_file", "copy_file", "move_file", "read_file", "write_file", "list_directory", "search_files", "refresh", "back"}
        missing = sorted(name for name in required if not self.capability_engine.exists(name))
        if missing:
            raise RuntimeError("Core capability registration failed: " + ", ".join(missing))

    def _register_workflows(self) -> None:
        pass

    def start(self) -> None:
        if self._running: return
        if not self._initialized: self.initialize()
        self._ensure_core_capabilities()
        self._runtime.start(); self.voice_manager.start()
        application = self._runtime.application
        if application is not None and not application.running: application.start()
        self._running = True
        if self.voice_manager.config.enabled and self.voice_manager.config.listen_enabled: self.voice_manager.start_voice_loop()

    def voice_chat_once(self) -> str | None:
        if not self._running: self.start()
        return self.voice_manager.converse_once()

    def start_voice(self) -> bool:
        if not self._running: self.start()
        return self.voice_manager.start_voice_loop()

    def stop_voice(self) -> None: self.voice_manager.stop_voice_loop()

    def shutdown(self) -> None:
        if not self._running: return
        application = self._runtime.application
        if application is not None and application.running: application.shutdown()
        self.voice_manager.shutdown(); self.file_manager.shutdown(); self.ai_engine.shutdown(); self.planning_engine.shutdown(); self.capability_engine.shutdown(); self.provider_manager.shutdown(); self.plugin_manager.shutdown(); self.messaging_manager.shutdown(); self.conversation_manager.shutdown(); self.memory_manager.shutdown(); self.service_registry.shutdown(); self._runtime.shutdown(); self._running=False; self._initialized=False

    def restart(self) -> None:
        self.shutdown(); self.start()
    @property
    def is_running(self) -> bool: return self._running
    @property
    def is_initialized(self) -> bool: return self._initialized
    def health(self) -> dict:
        return {"initialized": self._initialized, "running": self._running, "runtime": self._runtime.health(), "providers": self.provider_manager.health(), "planning": self.planning_engine.health(), "commands": self.command_engine.health(), "capabilities": self.capability_engine.health(), "memory": self.memory_manager.health(), "conversation": self.conversation_manager.health(), "services": self.service_registry.health(), "plugins": self.plugin_manager.health(), "voice": self.voice_manager.health(), "files": self.file_manager.health()}
    @property
    def service_count(self) -> int: return self.service_registry.service_count
    @property
    def provider_count(self) -> int: return self.provider_manager.provider_count
    @property
    def capability_count(self) -> int: return self.capability_engine.capability_count()
    @property
    def workflow_count(self) -> int: return self.planning_engine.workflow_count
    @property
    def component_count(self) -> int: return self.service_count + self.provider_count + self.capability_count + self.workflow_count
    @property
    def ai(self): return self.ai_engine
    @property
    def planner(self): return self.planning_engine
    @property
    def capabilities(self): return self.capability_engine
    @property
    def providers(self): return self.provider_manager
    @property
    def services(self): return self.service_registry
    @property
    def voice(self): return self.voice_manager
    @property
    def files(self): return self.file_manager
    @property
    def application(self): return self._runtime.application
