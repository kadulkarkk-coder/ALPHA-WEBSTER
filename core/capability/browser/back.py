"""
Webster Alpha

Back Browser Capability
"""

from __future__ import annotations

from core.capability.browser.base import BrowserCapability
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityCategory,
    CapabilityPermission,
    CapabilityType,
)


class BackCapability(BrowserCapability):
    """
    Navigate back in the active browser tab.

    Note:
        The default browser backend (Python's
        webbrowser module) cannot control
        existing browser tabs.

        This capability exists so the API
        remains stable until a controllable
        backend (Playwright, Selenium, CDP)
        is introduced.
    """

    def __init__(self) -> None:

        super().__init__(
            name="browser_back",
            capability_type=CapabilityType.BROWSER,
            category=CapabilityCategory.NETWORK,
            permissions=(
                CapabilityPermission.NETWORK,
            ),
        )

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:

        return CapabilityResult.failure_result(
            error=(
                "The current browser backend does not "
                "support browser navigation."
            ),
        )