"""
Webster Alpha

Web Search Capability
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


class WebSearchCapability(BrowserCapability):
    """
    Performs a web search using the selected
    search engine.
    """

    def __init__(self) -> None:

        super().__init__(
            name="web_search",
            capability_type=CapabilityType.WEB,
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

            query = self.get_query(request)

            engine = self.get_string(
                request,
                "engine",
            ) if "engine" in request.arguments else "google"

            url = self.build_search_url(
                query=query,
                engine=engine,
            )

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
                query=query,
                engine=engine,
                opened=True,
            )

        except Exception as error:

            return CapabilityResult.failure_result(
                error=str(error),
            )