"""Webster Alpha - Main Entry Point."""

from __future__ import annotations

from app.launcher import Launcher


def _print_voice_status(launcher: Launcher) -> None:
    health = launcher.voice_manager.health()
    print()
    print("Voice status:")
    print(f"  loop:       {health['voice_loop_running']}")
    print(f"  input:      {health['input_backend']}")
    print(f"  available:  {health['input_available']}")
    print(f"  device:     {health.get('input_device') or '<default>'}")
    print(f"  listening:  {health['listening']}")
    print(f"  wake word:  {health['wake_word']}")
    print(f"  last heard: {health.get('last_heard') or '<nothing transcribed yet>'}")
    print(f"  RMS:        {health.get('input_rms', 0.0):.5f}")
    print(f"  threshold:  {health.get('input_threshold', 0.0):.5f}")
    print(f"  output:     {health['output_backend']}")
    print(f"  speaker:    {health['output_available']}")
    if health.get("input_error"):
        print(f"  input err:  {health['input_error']}")
    if health.get("output_error"):
        print(f"  output err: {health['output_error']}")
    if health.get("last_error"):
        print(f"  manager err:{health['last_error']}")
    print()


def main() -> None:
    launcher = Launcher()

    try:
        print()
        print("=" * 60)
        print("Starting Webster Alpha...")
        print("=" * 60)
        print()

        launcher.start()
        application = launcher.application
        voice_health = launcher.voice_manager.health()

        print("Webster initialized successfully.")
        if voice_health["voice_loop_running"]:
            print("Voice mode: ACTIVE — say 'Webster' to wake me.")
        else:
            print("Voice mode: unavailable — type 'voice' for diagnostics.")
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
                print("voice devices")
                print("voice test")
                print("restart")
                print("exit")
                print()
                continue

            if lower == "voice":
                _print_voice_status(launcher)
                continue

            if lower == "voice devices":
                devices = launcher.voice_manager.devices()
                print()
                if not devices:
                    print("No microphone input devices were found.")
                else:
                    print("Microphone devices:")
                    for device in devices:
                        print(
                            f"  [{device['index']}] {device['name']} "
                            f"(inputs={device['inputs']}, "
                            f"rate={device['samplerate']})"
                        )
                print()
                continue

            if lower == "voice test":
                print()
                # The normal hands-free loop must be paused so the diagnostic
                # test is the only owner of the microphone stream.
                was_running = launcher.voice_manager.health()["voice_loop_running"]
                if was_running:
                    launcher.stop_voice()
                print("Speak now. Say a short sentence...")
                text = launcher.voice_manager.listen(ignore_wake_word=True)
                if text:
                    print(f"[VOICE TEST] You: {text}")
                    print("[VOICE TEST] Microphone + Whisper are working.")
                else:
                    print("[VOICE TEST] No speech was transcribed.")
                    _print_voice_status(launcher)
                if was_running:
                    launcher.start_voice()
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
