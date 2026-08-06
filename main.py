"""
Webster Alpha

Main Entry Point
"""

from __future__ import annotations

from app.launcher import Launcher


def main() -> None:
    """
    Webster entry point.
    """

    launcher = Launcher()

    try:

        print()

        print("=" * 60)

        print("Starting Webster Alpha...")

        print("=" * 60)

        print()

        launcher.start()

        application = launcher.application

        print("Webster initialized successfully.")

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

            #
            # Exit
            #

            if lower in ("exit", "quit"):

                break

            #
            # Help
            #

            if lower == "help":

                print()

                print("Commands")

                print("--------")

                print("help")

                print("status")

                print("health")

                print("restart")

                print("exit")

                print()

                continue

            #
            # Status
            #

            if lower == "status":

                print()

                print(application.status())

                print()

                continue

            #
            # Health
            #

            if lower == "health":

                print()

                print(application.health())

                print()

                continue

            #
            # Restart
            #

            if lower == "restart":

                print()

                print("Restarting Webster...")

                application.restart()

                print("Restart complete.")

                print()

                continue

            #
            # AI
            #

            try:

                response = application.chat(

                    command

                )

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