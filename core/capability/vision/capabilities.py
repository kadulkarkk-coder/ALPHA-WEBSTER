"""Concrete vision capabilities exposed through Webster's registry."""

from __future__ import annotations

from core.capability.request import CapabilityRequest
from core.capability.result import CapabilityResult
from core.capability.types import CapabilityCategory, CapabilityPermission, CapabilityType
from core.vision.manager import VisionManager

from .base import VisionCapability


class VisionEnableCapability(VisionCapability):
    def __init__(self, manager: VisionManager) -> None:
        super().__init__(
            name="vision_enable",
            capability_type=CapabilityType.VISION,
            category=CapabilityCategory.MULTIMEDIA,
            permissions=(CapabilityPermission.NONE,),
        )
        self._vision = manager

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        self._vision.enabled = True
        health = self._vision.health()
        return CapabilityResult.success_result(
            output="Vision activated. Webster can now use the configured visual capture pipeline.",
            enabled=True,
            **health,
        )


class VisionDisableCapability(VisionCapability):
    def __init__(self, manager: VisionManager) -> None:
        super().__init__(
            name="vision_disable",
            capability_type=CapabilityType.VISION,
            category=CapabilityCategory.MULTIMEDIA,
            permissions=(CapabilityPermission.NONE,),
        )
        self._vision = manager

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        self._vision.enabled = False
        return CapabilityResult.success_result(
            output="Vision deactivated.",
            enabled=False,
        )


class VisionStatusCapability(VisionCapability):
    def __init__(self, manager: VisionManager) -> None:
        super().__init__(
            name="vision_status",
            capability_type=CapabilityType.VISION,
            category=CapabilityCategory.MULTIMEDIA,
            permissions=(CapabilityPermission.NONE,),
        )
        self._vision = manager

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        health = self._vision.health()
        return CapabilityResult.success_result(
            output=(
                f"Vision {'enabled' if health['enabled'] else 'disabled'}. "
                f"Screen capture={'ready' if health['screen_capture'] else 'unavailable'}; "
                f"camera={'ready' if health['camera_capture'] else 'unavailable'}; "
                f"analysis provider={'ready' if health['vision_provider'] else 'OCR/fallback mode'}."
            ),
            **health,
        )


class VisionScreenCapability(VisionCapability):
    def __init__(self, manager: VisionManager) -> None:
        super().__init__(
            name="vision_screen",
            capability_type=CapabilityType.VISION,
            category=CapabilityCategory.MULTIMEDIA,
            permissions=(CapabilityPermission.SYSTEM_CONTROL,),
        )
        self._vision = manager

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        try:
            question = self.get_string(request, "question", "")
            result = self._vision.capture_and_analyze_screen(question or None)
            ocr = [item.text for item in result.text if item.text]
            description = result.description.strip()
            if not description:
                description = f"Screen captured successfully ({result.metadata.get('width', 'unknown')}x{result.metadata.get('height', 'unknown')})."
            if ocr:
                description += "\nVisible text:\n" + "\n".join(f"• {line}" for line in ocr)
            else:
                description += "\nNo OCR text was detected by the configured provider."
            return CapabilityResult.success_result(
                output=description,
                source=result.source.value,
                ocr_count=len(ocr),
                metadata=result.metadata,
            )
        except Exception as exc:
            return CapabilityResult.failure_result(error=str(exc))
