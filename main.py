"""Webster Alpha command-line entry point."""
from __future__ import annotations
from app.launcher import Launcher

def _print_voice_status(launcher):
    health=launcher.voice_manager.health(); print("\nVoice status:")
    for key,value in health.items(): print(f"  {key}: {value}")
    print()

def _print_voice_diagnostics(launcher):
    d=launcher.voice_manager.voice_diagnostics()
    print("\n╔════════════════ WEBSTER VOICE DIAGNOSTICS ═══════════════╗")
    print(f"║ Status           : {d['status']}")
    i=d['input']; print(f"║ Microphone       : {'OK' if i['available'] else 'FAIL'} ({i['backend']})")
    print(f"║ Device           : {i['device']}")
    print(f"║ Listening        : {i['listening']}")
    print(f"║ RMS / threshold  : {i['rms']} / {i['threshold']}")
    print(f"║ STT latency      : {d['stt']['latency_ms']} ms")
    w=d['wake_word']; print(f"║ Wake word        : {w['word']} | detected={w['detected']} | score={w['score']}")
    c=d['conversation']; print(f"║ Conversation     : active={c['active']} | turns={c['turns']}")
    b=d['barge_in']; print(f"║ Barge-in         : enabled={b['enabled']} | ready={b['ready']} | interrupted={b['last_interrupted']}")
    o=d['output']; print(f"║ TTS              : {'OK' if o['available'] else 'FAIL'} ({o['backend']}) | {o['tts_latency_ms']} ms")
    print(f"║ Round trip       : {d['round_trip_ms']} ms")
    if d['errors']: print(f"║ Errors           : {'; '.join(d['errors'])}")
    print("╚══════════════════════════════════════════════════════════╝\n")

def run_cli(launcher):
    application=launcher.application
    print("\nWebster initialized successfully.\nCore command engine: ACTIVE\n\nWEBSTER CHAT MODE\nType 'help' for commands.\nType 'exit' or 'quit' to stop.\n")
    while True:
        try: command=input("webster> ").strip()
        except (EOFError,KeyboardInterrupt): print("\nGoodbye."); return
        if not command: continue
        lower=command.lower()
        if lower in ("exit","quit"): print("Goodbye."); return
        if lower=="help":
            print("\nCommands\n--------\nhelp\nstatus\nhealth\ncapabilities\nvoice\nvoice diagnostics\nvoice devices\nvoice test\nrestart\nexit\n"); continue
        if lower=="capabilities":
            print("\nRegistered capabilities:")
            for name in launcher.capability_engine.names(): print(f"  - {name}")
            print(); continue
        if lower=="voice": _print_voice_status(launcher); continue
        if lower=="voice diagnostics": _print_voice_diagnostics(launcher); continue
        if lower=="voice devices":
            try:
                devices=launcher.voice_manager.devices()
                if not devices: print("No input devices found."); continue
                print("\nMicrophone devices:")
                for device in devices: print(f"[{device['index']}] {device['name']} (inputs={device['inputs']}, rate={device['samplerate']})")
                print()
            except Exception as exc: print(f"Voice device error: {exc}")
            continue
        if lower=="voice test":
            was_running=launcher.voice_manager.health().get("voice_loop_running")
            try:
                if was_running: launcher.stop_voice()
                print("Speak now. Say a short sentence...")
                text=launcher.voice_manager.listen(ignore_wake_word=True)
                print(f"[VOICE TEST] You: {text}" if text else "[VOICE TEST] No speech was transcribed.")
                if text: print("[VOICE TEST] Microphone + Whisper are working.")
            except Exception as exc: print(f"[VOICE TEST] Error: {exc}")
            finally:
                if was_running:
                    try: launcher.start_voice()
                    except Exception as exc: print(f"[VOICE TEST] Could not restart voice loop: {exc}")
            continue
        if lower=="status":
            try: print(application.status())
            except Exception as exc: print(f"Status error: {exc}")
            continue
        if lower=="health":
            try: print(launcher.health())
            except Exception as exc: print(f"Health error: {exc}")
            continue
        if lower=="restart":
            try: application.restart(); print("Restart complete.")
            except Exception as exc: print(f"Restart error: {exc}")
            continue
        try: print(application.chat(command))
        except Exception as exc: print(f"Error: {exc}")

def main():
    launcher=Launcher()
    try: launcher.start(); run_cli(launcher)
    finally: launcher.shutdown()

if __name__=="__main__": main()
