"""
Webster Alpha

Main Entry Point
"""

from __future__ import annotations

from app.launcher import Launcher


def main() -> None:
    """Webster entry point."""
    launcher = Launcher()

    try:
        print()
        print("=" * 60)
        print("Starting Webster Alpha...")
        print("=" * 60)
        print()

        launcher.start()

        # Start hands-free voice mode after the complete runtime has been
        # initialized and the AI processor has been connected.
        voice_started = launcher.voice_manager.start_voice_loop()

        application = launcher.application

        print("Webster initialized successfully.")
        if voice_started:
            print("Voice mode: ACTIVE — say 'Webster' to wake me.")
        else:
            print("Voice mode: unavailable — use 'health' for diagnostics.")
        print()
        print("WEBSTER CHAT MODE")
        print("Type 'help' for commands.")
        print("Type 'exit' or 'quit' to stop.")
        print()

        while True:
            command = input("webster> ").strip()

            if not command:
                continue

            lower = command.lower()

            if lower in ("exit", "quit"):
                break

            if lower == "help":
                print()
                print("Commands")
                print("--------")
                print("help")
                print("status")
                print("health")
                print("voice")
                print("restart")
                print("exit")
                print()
                continue

            if lower == "voice":
                health = launcher.voice_manager.health()
                print()
                print("Voice status:")
                print(f"  loop:      {health['voice_loop_running']}")
                print(f"  input:     {health['input_backend']}")
                print(f"  available: {health['input_available']}")
                print(f"  listening: {health['listening']}")
                print(f"  wake word: {health['wake_word']}")
                if health.get("input_error"):
                    print(f"  error:     {health['input_error']}")
                print()
                continue

            if lower == "status":
                print()
                print(application.status())
                print()
                continue

            if lower == "health":
                print()
                print(application.health())
                print()
                continue

            if lower == "restart":
                print()
                print("Restarting Webster...")
                application.restart()
                print("Restart complete.")
                print()
                continue

            try:
                response = application.chat(command)
                print()
                print(response)
                print()
            except Exception as exc:
                print()
                print(f"Error: {exc}")
                print()

    finally:
        launcher.shutdown()
        print()
        print("Goodbye.")


if __name__ == "__main__":
    main()
