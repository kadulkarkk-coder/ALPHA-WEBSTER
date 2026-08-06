"""
Webster Alpha

Open URL Capability
"""

from __future__ import annotations

import webbrowser


from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityCategory,
    CapabilityPermission,
    CapabilityType,
)


class OpenUrlCapability(BrowserCapability):
    """
    Opens a URL in the user's default browser.
    """

    def __init__(self) -> None:

        super().__init__(
            name="open_url",
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

            url = self.get_string(
                request,
                "url",
            ).strip()

            if not url:
                raise ValueError(
                    "URL cannot be empty."
                )

            if not (
                url.startswith("http://")
                or url.startswith("https://")
            ):
                url = f"https://{url}"

            opened = webbrowser.open(
                url,
                new=2,
            )

            if not opened:
                raise RuntimeError(
                    "Failed to open the browser."
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