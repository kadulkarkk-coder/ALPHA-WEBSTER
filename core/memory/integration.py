"""Integration facade for WEBSTER's memory platform."""

from __future__ import annotations

from core.memory.context import MemoryContext, MemoryContextBuilder
from core.memory.manager import MemoryManager
from core.memory.service import MemoryService


class MemoryIntegration:
    """Single entry point for AI-facing memory operations."""

    def __init__(self, manager: MemoryManager) -> None:
        self.manager = manager
        self.service = MemoryService(manager)
        self.context_builder = MemoryContextBuilder(manager)

    def initialize(self) -> None:
        self.service.initialize()

    def remember_from_text(self, text: str) -> None:
        self.service.process_user_text(text)

    def context_for(self, text: str) -> MemoryContext:
        return self.context_builder.build(text)

    def health(self) -> dict:
        return self.service.health()
