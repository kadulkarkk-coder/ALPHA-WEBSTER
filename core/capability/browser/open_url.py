"""
Webster Alpha

Open URL Capability
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


class OpenUrlCapability(BrowserCapability):
    """
    Opens a URL in the user's default browser.
    """

    def __init__(
        self,
    ) -> None:

        super().__init__(
            name="open_url",
            capability_type=CapabilityType.WEB,
            category=CapabilityCategory.INTERNET,
            permissions=(
                CapabilityPermission.NETWORK,
            ),
        )

    # =====================================================
    # Execution
    # =====================================================

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:
        """
        Open the requested URL in the default browser.
        """

        try:

            #
            # Extract URL
            #

            url = self.get_string(
                request,
                "url",
            ).strip()

            if not url:

                raise ValueError(
                    "URL cannot be empty."
                )

            #
            # Normalize URL
            #

            if not (
                url.startswith("http://")
                or url.startswith("https://")
            ):

                url = f"https://{url}"

            #
            # Open browser
            #

            opened = webbrowser.open(
                url,
                new=2,
            )

            if not opened:

                raise RuntimeError(
                    "Failed to open the browser."
                )

            #
            # Success
            #

            return CapabilityResult.success_result(

                output=url,

                url=url,

                opened=True,

            )

        except Exception as error:

            #
            # Failure
            #

            return CapabilityResult.failure_result(

                error=str(error),

                url=(
                    url
                    if "url" in locals()
                    else None
                ),

            )

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (
            "OpenUrlCapability("
            "name='open_url'"
            ")"
        )