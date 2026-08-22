# Sprint 34 — Microphone Service

## Goal
Create a UI-independent microphone service that can be reused by voice, automation, diagnostics, and the future UI.

## Delivered
- `core/microphone/types.py` — device, state, and diagnostic models.
- `core/microphone/backend.py` — isolated `sounddevice` adapter with graceful fallback.
- `core/microphone/manager.py` — initialization, discovery, device selection, capture lifecycle, and shutdown.
- `core/microphone/diagnostics.py` — safe health information for logs and future UI.
- `core/tests/test_microphone.py` — backend-independent lifecycle and health tests.

## Architecture
The microphone service is intentionally separate from the UI and from a specific speech-to-text engine. The voice layer can inject or consume it later without coupling the core to a desktop interface.

## Safety / Reliability
- No microphone is accessed merely by importing the package.
- Device discovery fails gracefully when no input device or backend is available.
- Device selection validates the requested device.
- Capture resources are stopped and closed through the manager lifecycle.

## Next
Phase 3 is complete after Sprint 34. Phase 4 begins with the Skills & Plugins architecture.
