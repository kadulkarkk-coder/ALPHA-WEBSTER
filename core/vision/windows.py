"""Windows screen capture provider for Webster vision."""

from __future__ import annotations

from io import BytesIO

from core.vision.types import VisionFrame, VisionSource


class WindowsScreenProvider:
    """Capture the primary desktop using Pillow's Windows ImageGrab backend."""

    def capture(self) -> VisionFrame:
        try:
            from PIL import ImageGrab
        except ImportError as exc:
            raise RuntimeError(
                "Screen capture requires Pillow. Install dependencies with: pip install -r requirements.txt"
            ) from exc

        try:
            image = ImageGrab.grab(all_screens=True)
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            return VisionFrame(
                source=VisionSource.SCREEN,
                data=buffer.getvalue(),
                width=image.width,
                height=image.height,
                format="png",
                metadata={"provider": "windows_imagegrab"},
            )
        except Exception as exc:
            raise RuntimeError(f"Unable to capture the Windows screen: {exc}") from exc
