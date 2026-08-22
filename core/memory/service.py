"""High-level memory service used by AI and conversation layers."""

from __future__ import annotations

from core.memory.extraction import MemoryExtractor
from core.memory.manager import MemoryManager
from core.memory.policy import MemoryDecision, MemoryPolicy


class MemoryService:
    """Coordinates extraction, policy and persistence."""

    def __init__(
        self,
        manager: MemoryManager,
        extractor: MemoryExtractor | None = None,
        policy: MemoryPolicy | None = None,
    ) -> None:
        self.manager = manager
        self.extractor = extractor or MemoryExtractor()
        self.policy = policy or MemoryPolicy()

    def initialize(self) -> None:
        if not self.manager.initialized:
            self.manager.initialize()

    def process_user_text(self, text: str) -> list[MemoryDecision]:
        self.initialize()
        decisions: list[MemoryDecision] = []
        for candidate in self.extractor.extract(text):
            decision = self.policy.evaluate(candidate)
            decisions.append(decision)
            if decision.store:
                self.manager.remember(
                    candidate.memory_type,
                    candidate.topic,
                    candidate.value,
                    source="conversation",
                    confidence=candidate.confidence,
                    metadata={"reason": candidate.reason, "importance": decision.importance},
                )
        return decisions

    def health(self) -> dict:
        return {
            "healthy": self.manager.ready,
            "memory": self.manager.health(),
            "extractor": self.extractor.__class__.__name__,
            "policy": self.policy.__class__.__name__,
        }
