"""Tests for the WEBSTER microphone service."""
from __future__ import annotations

import unittest

from core.microphone.diagnostics import microphone_health
from core.microphone.manager import MicrophoneManager
from core.microphone.types import MicrophoneDevice, MicrophoneState


class FakeBackend:
    name = "fake"
    available = True
    error = None

    def __init__(self):
        self.started = False
        self.stopped = False
        self.items = [MicrophoneDevice(0, "Test Microphone", 1, 16000.0, True)]

    def devices(self):
        return self.items

    def start(self, callback, **kwargs):
        self.started = True
        return True

    def stop(self):
        self.stopped = True


class MicrophoneManagerTests(unittest.TestCase):
    def test_initialize_selects_default_device(self):
        manager = MicrophoneManager(FakeBackend())
        self.assertTrue(manager.initialize())
        self.assertEqual(manager.state, MicrophoneState.READY)
        self.assertEqual(manager.selected_device.name, "Test Microphone")

    def test_capture_lifecycle(self):
        backend = FakeBackend()
        manager = MicrophoneManager(backend)
        self.assertTrue(manager.start(lambda *args: None))
        self.assertEqual(manager.state, MicrophoneState.CAPTURING)
        manager.stop()
        self.assertTrue(backend.stopped)

    def test_health_is_safe_and_structured(self):
        manager = MicrophoneManager(FakeBackend())
        manager.initialize()
        health = microphone_health(manager)
        self.assertEqual(health["backend"], "fake")
        self.assertEqual(health["device_index"], 0)
        self.assertTrue(health["available"])


if __name__ == "__main__":
    unittest.main()
