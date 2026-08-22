"""Base classes for Webster vision capabilities."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.capability.capability import Capability
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult


class VisionCapability(Capability, ABC):
    """Base class for capabilities backed by the shared VisionManager."""

    @abstractmethod
    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        raise NotImplementedError
