"""
Webster Alpha

Browser Capability Pack
"""

from __future__ import annotations

from core.capability.packs.pack import CapabilityPack
from core.capability.registry import CapabilityRegistry

from core.capability.browser.open_url import OpenUrlCapability
from core.capability.browser.web_search import WebSearchCapability
from core.capability.browser.open_tab import OpenTabCapability
from core.capability.browser.refresh import RefreshCapability
from core.capability.browser.back import BackCapability
from core.capability.browser.forward import ForwardCapability
from core.capability.browser.close_tab import CloseTabCapability


class BrowserPack(CapabilityPack):
    """
    Registers browser capabilities.
    """

    @property
    def name(self) -> str:
        return "browser"

    @property
    def version(self) -> str:
        return "1.0.0"

    def register(
        self,
        registry: CapabilityRegistry,
    ) -> None:

        registry.register(OpenUrlCapability())
        registry.register(WebSearchCapability())
        registry.register(OpenTabCapability())
        registry.register(RefreshCapability())
        registry.register(BackCapability())
        registry.register(ForwardCapability())
        registry.register(CloseTabCapability())