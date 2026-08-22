"""Backend adapter for microphone device discovery and capture."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from core.microphone.types import MicrophoneDevice


class MicrophoneBackend:
    """Small adapter around sounddevice with a dependency-free fallback."""

    name = "unavailable"

    def __init__(self) -> None:
        self.error: str | None = None
        self._stream: Any = None
        self._sounddevice: Any = None
        try:
            import sounddevice as sd

            self._sounddevice = sd
            self.name = "sounddevice"
        except Exception as exc:
            self.error = str(exc)

    @property
    def available(self) -> bool:
        return self._sounddevice is not None

    def devices(self) -> list[MicrophoneDevice]:
        if not self.available:
            return []
        try:
            result: list[MicrophoneDevice] = []
            default_input = int(self._sounddevice.default.device[0])
            for index, info in enumerate(self._sounddevice.query_devices()):
                channels = int(info.get("max_input_channels", 0))
                if channels <= 0:
                    continue
                result.append(
                    MicrophoneDevice(
                        index=index,
                        name=str(info.get("name", f"Input {index}")),
                        channels=channels,
                        sample_rate=float(info.get("default_samplerate", 0.0) or 0.0),
                        default=index == default_input,
                    )
                )
            self.error = None
            return result
        except Exception as exc:
            self.error = str(exc)
            return []

    def start(self, callback: Callable[..., None], *, device: int | None = None,
              samplerate: float = 16000.0, channels: int = 1, blocksize: int = 0) -> bool:
        if not self.available:
            return False
        try:
            self._stream = self._sounddevice.InputStream(
                device=device,
                samplerate=samplerate,
                channels=channels,
                blocksize=blocksize,
                callback=callback,
            )
            self._stream.start()
            self.error = None
            return True
        except Exception as exc:
            self.error = str(exc)
            self._stream = None
            return False

    def stop(self) -> None:
        if self._stream is None:
            return
        try:
            self._stream.stop()
            self._stream.close()
        except Exception as exc:
            self.error = str(exc)
        finally:
            self._stream = None
