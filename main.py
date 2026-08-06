"""
Webster V2 Entry Point
"""

from __future__ import annotations

import sys

from app.launcher import Launcher


def main() -> None:
    """
    Start Webster.
    """
    launcher = Launcher()

    try:
        launcher.start()

        if sys.stdin.isatty():
            print()
            print("WEBSTER CHAT MODE")
            print("Type 'exit' or 'quit' to stop.")
            print()

            while True:
                try:
                    prompt = input("webster> ")
                except EOFError:
                    break

                command = prompt.strip()

                if not command:
                    continue

                if command.lower() in {"exit", "quit", "q"}:
                    break

                if command.lower() in {"status", "status help", "help status"}:
                    print("Available status commands: status, status health, status ready, status initialized")
                    continue

                if command.lower() == "status":
                    print("Webster is running and ready." if launcher.ready else "Webster is initialized." if launcher.initialized else "Webster is not initialized.")
                    continue

                if command.lower() == "status health":
                    print(launcher.health())
                    continue

                if command.lower() == "status ready":
                    print(f"ready={launcher.ready}")
                    continue

                if command.lower() == "status initialized":
                    print(f"initialized={launcher.initialized}")
                    continue

                print(f"You entered: {command}")

    finally:
        launcher.shutdown()


if __name__ == "__main__":
    main()