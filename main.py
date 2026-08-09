"""Webster Alpha entry point.

Desktop mode is the default. Use ``python main.py --cli`` for the legacy
terminal interface and diagnostics.
"""

from __future__ import annotations

import sys

from app.launcher import Launcher


def _print_voice_status(launcher: Launcher) -> None:
    health = launcher.voice_manager.health()
    print("\nVoice status:")
    for key, value in health.items():
        print(f"  {key}: {value}")
    print()


def run_cli(launcher: Launcher) -> None:
    application = launcher.application
    voice_health = launcher.voice_manager.health()
    print("\nWebster initialized successfully.")
    print("Voice mode: ACTIVE" if voice_health.get("voice_loop_running") else "Voice mode: unavailable")
    print("\nWEBSTER CHAT MODE\nType 'help' for commands.\nType 'exit' or 'quit' to stop.\n")
    while True:
        command = input("webster> ").strip()
        if not command:
            continue
        lower = command.lower()
        if lower in ("exit", "quit"):
            return
        if lower == "help":
            print("help\nstatus\nhealth\nvoice\nvoice devices\nvoice test\nrestart\nexit")
            continue
        if lower == "voice":
            _print_voice_status(launcher)
            continue
        if lower == "voice devices":
            for device in launcher.voice_manager.devices():
                print(f"[{device['index']}] {device['name']} (inputs={device['inputs']}, rate={device['samplerate']})")
            continue
        if lower == "voice test":
            was_running = launcher.voice_manager.health().get("voice_loop_running")
            if was_running:
                launcher.stop_voice()
            print("Speak now. Say a short sentence...")
            text = launcher.voice_manager.listen(ignore_wake_word=True)
            print(f"[VOICE TEST] You: {text}" if text else "[VOICE TEST] No speech was transcribed.")
            if was_running:
                launcher.start_voice()
            continue
        if lower == "status":
            print(application.status())
            continue
        if lower == "health":
            print(application.health())
            continue
        if lower == "restart":
            application.restart()
            print("Restart complete.")
            continue
        try:
            print(application.chat(command))
        except Exception as exc:
            print(f"Error: {exc}")


def main() -> None:
    launcher = Launcher()
    try:
        launcher.start()
        if "--cli" in sys.argv[1:]:
            run_cli(launcher)
            return

        from ui.app import run
        run(launcher.application, launcher)
    finally:
        launcher.shutdown()


if __name__ == "__main__":
    main()
