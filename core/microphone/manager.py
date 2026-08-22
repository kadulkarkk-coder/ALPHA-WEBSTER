"""High-level microphone service manager."""
from __future__ import annotations

from collections.abc import Callable

from core.microphone.backend import MicrophoneBackend
from core.microphone.types import MicrophoneDevice, MicrophoneSnapshot, MicrophoneState


class MicrophoneManager:
    """Owns microphone discovery, selection and capture lifecycle."""

    def __init__(self, backend: MicrophoneBackend | None = None) -> None:
        self.backend = backend or MicrophoneBackend()
        self.state = MicrophoneState.UNINITIALIZED
        self.selected_device: MicrophoneDevice | None = None
        self.sample_rate = 16000.0
        self.channels = 1
        self._error: str | None = None

    def initialize(self) -> bool:
        if self.state in {MicrophoneState.READY, MicrophoneState.CAPTURING}:
            return self.available
        self._error = None
        devices = self.devices()
        self.selected_device = next((d for d in devices if d.default), devices[0] if devices else None)
        self.state = MicrophoneState.READY if self.selected_device else MicrophoneState.ERROR
        if self.selected_device:
            self.sample_rate = self.selected_device.sample_rate or self.sample_rate
            self.channels = max(1, min(self.selected_device.channels, 2))
        else:
            self._error = self.backend.error or "No microphone input device is available."
        return self.available

    @property
    def available(self) -> bool:
        return self.selected_device is not None and self.backend.available

    @property
    def error(self) -> str | None:
        return self._error or self.backend.error

    def devices(self) -> list[MicrophoneDevice]:
        return self.backend.devices()

    def select(self, device: int | MicrophoneDevice) -> MicrophoneDevice:
        devices = self.devices()
        index = device.index if isinstance(device, MicrophoneDevice) else int(device)
        selected = next((item for item in devices if item.index == index), None)
        if selected is None:
            raise ValueError(f"Microphone device {index} is not available")
        if self.state == MicrophoneState.CAPTURING:
            self.stop()
        self.selected_device = selected
        self.sample_rate = selected.sample_rate or self.sample_rate
        self.channels = max(1, min(selected.channels, 2))
        self.state = MicrophoneState.READY
        self._error = None
        return selected

    def start(self, callback: Callable[..., None]) -> bool:
        if not self.initialize() and not self.available:
            return False
        device_index = self.selected_device.index if self.selected_device else None
        ok = self.backend.start(
            callback,
            device=device_index,
            samplerate=self.sample_rate,
            channels=self.channels,
        )
        self.state = MicrophoneState.CAPTURING if ok else MicrophoneState.ERROR
        self._error = None if ok else self.backend.error
        return ok

    def stop(self) -> None:
        self.backend.stop()
        self.state = MicrophoneState.STOPPED if self.selected_device else MicrophoneState.UNINITIALIZED

    def snapshot(self) -> MicrophoneSnapshot:
        return MicrophoneSnapshot(
            state=self.state,
            available=self.available,
            device=self.selected_device,
            error=self.error,
            sample_rate=self.sample_rate,
            channels=self.channels,
        )

    def shutdown(self) -> None:
        self.stop()
        self.selected_device = None
        self.state = MicrophoneState.UNINITIALIZED
