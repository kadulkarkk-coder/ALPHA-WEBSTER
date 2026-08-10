"""
Webster Alpha

Open URL Capability
"""

from __future__ import annotations

import re
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
    """Opens a URL or common website name in the user's default browser."""

    _SITE_ALIASES = {
        "google": "google.com",
        "youtube": "youtube.com",
        "github": "github.com",
        "facebook": "facebook.com",
        "instagram": "instagram.com",
        "x": "x.com",
        "twitter": "x.com",
        "reddit": "reddit.com",
        "wikipedia": "wikipedia.org",
        "amazon": "amazon.com",
        "gmail": "gmail.com",
        "google maps": "maps.google.com",
        "maps": "maps.google.com",
    }

    def __init__(self) -> None:
        super().__init__(
            name="open_url",
            capability_type=CapabilityType.WEB,
            category=CapabilityCategory.INTERNET,
            permissions=(CapabilityPermission.NETWORK,),
        )

    @classmethod
    def _clean_spoken_url(cls, value: str) -> str:
        """Convert natural spoken website names into a browser-safe URL."""
        text = " ".join(value.strip().split())
        if not text:
            raise ValueError("URL cannot be empty.")

        # The voice layer may already have consumed the wake word, but older
        # command paths can still concatenate it with the command.
        text = re.sub(r"^webster\s*", "", text, flags=re.IGNORECASE).strip()
        if not text:
            raise ValueError("URL cannot be empty after removing the wake word.")

        lowered = text.lower()
        if lowered in cls._SITE_ALIASES:
            return cls._SITE_ALIASES[lowered]

        # Spoken punctuation: "google dot com" -> "google.com".
        text = re.sub(r"\s+dot\s+", ".", text, flags=re.IGNORECASE)
        text = re.sub(r"\s+(slash)\s+", "/", text, flags=re.IGNORECASE)
        text = re.sub(r"\s+", "", text)

        # If the voice parser concatenated the wake word, recover the command
        # for common domains, e.g. "WebsteropenGoogle" -> "google.com".
        compact = lowered.replace(" ", "")
        for spoken_name, domain in cls._SITE_ALIASES.items():
            alias_compact = spoken_name.replace(" ", "")
            if compact.startswith("webster" + alias_compact):
                suffix = compact[len("webster" + alias_compact):]
                return domain + suffix

        # Natural "open google" may reach this capability without an alias
        # match if a new site is used. Treat the final phrase as a hostname.
        return text

    @classmethod
    def _normalize_url(cls, value: str) -> str:
        url = cls._clean_spoken_url(value)
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        return url

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        url: str | None = None
        try:
            # Capability.get_string reads request.arguments correctly.
            raw_url = self.get_string(request, "url").strip()
            url = self._normalize_url(raw_url)

            opened = webbrowser.open(url, new=2)
            if not opened:
                raise RuntimeError("Failed to open the browser.")

            return CapabilityResult.success_result(
                output=url,
                url=url,
                opened=True,
            )

        except Exception as error:
            return CapabilityResult.failure_result(
                error=str(error),
                url=url,
            )

    def __repr__(self) -> str:
        return "OpenUrlCapability(name='open_url')"
