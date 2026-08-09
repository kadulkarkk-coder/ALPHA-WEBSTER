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

        # Launcher.start() already starts the hands-free voice loop after
        # wiring the AI processor. Do not start it a second time here.
        launcher.start()

        application = launcher.application
        voice_health = launcher.voice_manager.health()
        voice_started = voice_health["voice_loop_running"]

        print("Webster initialized successfully.")
        if voice_started:
            print("Voice mode: ACTIVE — say 'Webster' to wake me.")
        else:
            print("Voice mode: unavailable — use 'voice' for diagnostics.")
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
                print(f"  loop:       {health['voice_loop_running']}")
                print(f"  input:      {health['input_backend']}")
                print(f"  available:  {health['input_available']}")
                print(f"  listening:  {health['listening']}")
                print(f"  wake word:  {health['wake_word']}")
                print(f"  last heard: {health.get('last_heard') or '<nothing transcribed yet>'}")
                print(f"  output:     {health['output_backend']}")
                print(f"  speaker:    {health['output_available']}")
                if health.get("input_error"):
                    print(f"  input err:  {health['input_error']}")
                if health.get("output_error"):
                    print(f"  output err: {health['output_error']}")
                if health.get("last_error"):
                    print(f"  manager err:{health['last_error']}")
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
