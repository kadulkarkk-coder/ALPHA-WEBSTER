"""
Webster Alpha

Open Tab Capability
"""

from __future__ import annotations

import webbrowser

from core.capability.browser.base import BrowserCapability
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityCategory,
    CapabilityPermission,
    CapabilityType,
)


class OpenTabCapability(BrowserCapability):
    """
    Opens a new browser tab.
    """

    def __init__(self) -> None:

        super().__init__(
            name="open_tab",
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

        try:

            if "url" in request.arguments:
                url = self.get_url(request)
            else:
                url = "about:blank"

            opened = webbrowser.open_new_tab(url)

            if not opened:
                raise RuntimeError(
                    "Failed to open a new browser tab."
                )

            return CapabilityResult.success_result(
                output=url,
                url=url,
                opened=True,
            )

        except Exception as error:

            return CapabilityResult.failure_result(
                error=str(error),
            )