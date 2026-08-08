"""
Webster Alpha

Refresh Browser Capability
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


class RefreshCapability(BrowserCapability):
    """
    Refresh the active browser tab.

    Note:
        The default browser backend used by Webster Alpha
        (Python's webbrowser module) does not support
        controlling existing browser tabs.

        This capability is implemented so the API remains
        stable and can later be backed by Playwright,
        Selenium, or the Chrome DevTools Protocol.
    """

    def __init__(self) -> None:

        super().__init__(
            name="refresh",
            capability_type=CapabilityType.WEB,
            category=CapabilityCategory.INTERNET,
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
                "support refreshing an existing tab."
            ),
        )