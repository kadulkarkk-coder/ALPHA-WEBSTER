"""
Webster Alpha

Clipboard Capability
"""

from __future__ import annotations

import pyperclip

from core.capability.system.base import SystemCapability
from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import (
    CapabilityCategory,
    CapabilityPermission,
    CapabilityType,
)


class ClipboardCapability(SystemCapability):
    """
    Read from and write to the system clipboard.

    Supported actions:

    - copy
    - paste
    - clear
    """

    def __init__(self) -> None:

        super().__init__(
            name="clipboard",
            capability_type=CapabilityType.SYSTEM,
            category=CapabilityCategory.SYSTEM,
            permissions=(
                CapabilityPermission.SYSTEM,
            ),
        )

    def execute(
        self,
        request: CapabilityRequest,
    ) -> CapabilityResult:

        try:

            action = self.get_string(
                request,
                "action",
            ).lower()

            if action == "copy":

                text = self.get_string(
                    request,
                    "text",
                )

                pyperclip.copy(text)

                return CapabilityResult.success_result(
                    output=text,
                    action="copy",
                )

            if action == "paste":

                text = pyperclip.paste()

                return CapabilityResult.success_result(
                    output=text,
                    action="paste",
                )

            if action == "clear":

                pyperclip.copy("")

                return CapabilityResult.success_result(
                    output="",
                    action="clear",
                )

            return CapabilityResult.failure_result(
                error=f"Unknown clipboard action '{action}'.",
            )

        except Exception as error:

            return CapabilityResult.failure_result(
                error=str(error),
            )