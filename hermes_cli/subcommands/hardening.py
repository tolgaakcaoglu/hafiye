"""Parser for Hafiye's P19 hardening diagnostics and retention maintenance."""

from __future__ import annotations

from typing import Callable


def build_hardening_parser(subparsers, *, cmd_hardening: Callable) -> None:
    parser = subparsers.add_parser(
        "hardening",
        help="Inspect Hafiye safety/recovery boundaries and enforce retention",
        description=(
            "Inspect Hafiye's prompt-injection, redaction, recovery, loop, "
            "checkpoint, config, audit, and disk hardening boundaries."
        ),
    )
    commands = parser.add_subparsers(dest="hardening_command")
    commands.add_parser("doctor", help="Run the non-invasive hardening doctor")
    commands.add_parser(
        "prune",
        help="Run configured audit-log and checkpoint retention maintenance",
    )
    parser.set_defaults(func=cmd_hardening)


__all__ = ["build_hardening_parser"]
