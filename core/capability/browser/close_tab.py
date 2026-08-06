"""
Webster Alpha

Close Tab Capability
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


class CloseTabCapability(BrowserCapability):
    """
    Closes the active browser tab.

    Note:
        The default browser backend (Python's
        webbrowser module) cannot control
        existing browser tabs.

        This capability exists so the API
        remains stable until Webster adopts
        a controllable browser backend such
        as Playwright or Chrome DevTools.
    """

    def __init__(self) -> None:

        super().__init__(
            name="close_tab",
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
                "support closing browser tabs."
            ),
        )