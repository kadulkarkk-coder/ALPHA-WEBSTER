# Sprint 34.5 — Core Integration & Intelligence Repair

## Goal
Make the existing Webster core execute natural-language commands through the real capability registry instead of falling through to the text provider or producing empty plans.

## Completed

- Expanded `IntentRouter` for natural file commands such as `delete read.txt`.
- Added deterministic vision intents: enable, disable, status, and screen inspection.
- Aligned `GoalAnalyzer` with the router's capability names.
- Improved `TaskDecomposer` argument extraction for plain filenames and website aliases.
- Prevented `AIPlanningBridge` from sending unresolved action intents into empty plans.
- Wired `VisionManager` into `Launcher` and the service registry.
- Added Windows screen capture through Pillow's `ImageGrab` backend.
- Added registered vision capabilities:
  - `vision_enable`
  - `vision_disable`
  - `vision_status`
  - `vision_screen`
- Fixed the launcher import to use the actual `core.capability.file.delete` module.
- Added vision status/diagnostics to the CLI.
- Added integration tests for routing, planning arguments, URL aliases, and vision state.
- Added Pillow to runtime dependencies.

## Expected command path

```text
User / Voice
    ↓
IntentRouter
    ↓
CommandEngine (known capability)
    ↓
TaskDecomposer
    ↓
Planner
    ↓
Validator
    ↓
Executor
    ↓
CapabilityEngine
    ↓
Real capability
```

Unknown action requests no longer become empty plans. They return a routing error that identifies the missing capability instead.

## Vision

`activate vision` enables the shared vision manager. `vision status` reports the configured capture/analysis pipeline. `can you see my screen` captures the Windows desktop through the registered `vision_screen` capability.

The repository currently has an analyzer abstraction and OCR abstraction but no built-in multimodal model provider. Screen capture is therefore functional independently of a multimodal provider; semantic visual descriptions require a provider to be injected later.

## Validation

Run:

```powershell
python -m unittest core.tests.test_core_integration
python -m unittest core.tests.test_microphone
python main.py
```

Then smoke-test:

```text
capabilities
activate vision
vision status
can you see my screen
open google
delete read.txt
```

Deletion should request confirmation before execution.
