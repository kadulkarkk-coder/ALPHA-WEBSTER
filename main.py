"""Webster Alpha command-line entry point.

The UI layer is intentionally disabled while the core platform is stabilized.
Run ``python main.py`` for the terminal interface and diagnostics.
"""

from __future__ import annotations

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
    print(
        "Voice mode: ACTIVE"
        if voice_health.get("voice_loop_running")
        else "Voice mode: unavailable"
    )
    print("\nWEBSTER CHAT MODE")
    print("Type 'help' for commands.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            command = input("webster> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return

        if not command:
            continue

        lower = command.lower()

        if lower in ("exit", "quit"):
            print("Goodbye.")
            return

        if lower == "help":
            print(
                "\nCommands\n"
                "--------\n"
                "help\n"
                "status\n"
                "health\n"
                "voice\n"
                "voice devices\n"
                "voice test\n"
                "restart\n"
                "exit\n"
            )
            continue

        if lower == "voice":
            _print_voice_status(launcher)
            continue

        if lower == "voice devices":
            try:
                devices = launcher.voice_manager.devices()
                if not devices:
                    print("No input devices found.")
                    continue
                print("\nMicrophone devices:")
                for device in devices:
                    print(
                        f"[{device['index']}] {device['name']} "
                        f"(inputs={device['inputs']}, rate={device['samplerate']})"
                    )
                print()
            except Exception as exc:
                print(f"Voice device error: {exc}")
            continue

        if lower == "voice test":
            was_running = launcher.voice_manager.health().get("voice_loop_running")
            try:
                if was_running:
                    launcher.stop_voice()
                print("Speak now. Say a short sentence...")
                text = launcher.voice_manager.listen(ignore_wake_word=True)
                if text:
                    print(f"[VOICE TEST] You: {text}")
                    print("[VOICE TEST] Microphone + Whisper are working.")
                else:
                    print("[VOICE TEST] No speech was transcribed.")
            except Exception as exc:
                print(f"[VOICE TEST] Error: {exc}")
            finally:
                if was_running:
                    try:
                        launcher.start_voice()
                    except Exception as exc:
                        print(f"[VOICE TEST] Could not restart voice loop: {exc}")
            continue

        if lower == "status":
            try:
                print(application.status())
            except Exception as exc:
                print(f"Status error: {exc}")
            continue

        if lower == "health":
            try:
                print(application.health())
            except Exception as exc:
                print(f"Health error: {exc}")
            continue

        if lower == "restart":
            try:
                application.restart()
                print("Restart complete.")
            except Exception as exc:
                print(f"Restart error: {exc}")
            continue

        try:
            result = application.chat(command)
            print(result)
        except Exception as exc:
            print(f"Error: {exc}")


def main() -> None:
    launcher = Launcher()
    try:
        launcher.start()
        run_cli(launcher)
    finally:
        launcher.shutdown()


if __name__ == "__main__":
    main()
