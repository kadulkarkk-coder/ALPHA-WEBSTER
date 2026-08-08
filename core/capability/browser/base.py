"""
Webster Alpha

Browser Capability Base Class
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from core.capability.capability import Capability
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult


class BrowserCapability(
    Capability,
    ABC,
):
    """
    Base class for all browser capabilities.
    """

    @abstractmethod
    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        """
        Execute the browser capability.
        """
        raise NotImplementedError