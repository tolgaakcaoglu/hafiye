"""Parser for Hafiye's managed local voice runtimes."""

from __future__ import annotations

from typing import Callable

from hermes_cli.local_runtime import BACKENDS
from hermes_cli.voice_runtime import DEFAULT_PIPER_VOICE, DEFAULT_WHISPER_MODEL


def build_voice_parser(subparsers, *, cmd_voice: Callable) -> None:
    parser = subparsers.add_parser(
        "voice",
        help="Manage Hafiye's local Turkish voice runtimes",
        description="Install and inspect managed whisper.cpp and Piper voice runtimes.",
    )
    commands = parser.add_subparsers(dest="voice_command")

    commands.add_parser("doctor", help="Inspect whisper.cpp and Piper readiness")

    whisper = commands.add_parser("install-whisper", help="Build whisper.cpp and install a multilingual model")
    whisper.add_argument("--backend", choices=BACKENDS, default="AUTO")
    whisper.add_argument("--source-ref", default="master")
    whisper.add_argument("--model", default=DEFAULT_WHISPER_MODEL)

    piper = commands.add_parser("install-piper", help="Install Piper in its managed venv and download a voice")
    piper.add_argument("--voice", default=DEFAULT_PIPER_VOICE)

    commands.add_parser("voices", help="List installed Piper voices")

    stt = commands.add_parser("stt", help="Run managed whisper.cpp STT")
    stt.add_argument("--input", required=True)
    stt.add_argument("--output-dir", required=True)
    stt.add_argument("--model", default=DEFAULT_WHISPER_MODEL)
    stt.add_argument("--language", default="tr")
    stt.add_argument("--backend", choices=BACKENDS, default="AUTO")

    speak = commands.add_parser("piper-speak", help="Run managed Piper synthesis")
    speak.add_argument("--text", required=True)
    speak.add_argument("--output", required=True)
    speak.add_argument("--voice", default=DEFAULT_PIPER_VOICE)

    parser.set_defaults(func=cmd_voice)


__all__ = ["build_voice_parser"]
