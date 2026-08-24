"""Parser for Hafiye's managed local llama.cpp runtime."""

from __future__ import annotations

import argparse
from typing import Callable

from hermes_cli.local_runtime import BACKENDS, DEFAULT_CONTEXT_SIZE, DEFAULT_PORT


def build_runtime_parser(subparsers, *, cmd_runtime: Callable) -> None:
    parser = subparsers.add_parser(
        "runtime",
        help="Manage Hafiye's local GGUF runtime",
        description="Install and operate Hafiye's managed llama.cpp server and local GGUF models.",
    )
    commands = parser.add_subparsers(dest="runtime_command")

    install = commands.add_parser("install", help="Clone/build the managed llama.cpp runtime")
    install.add_argument("--backend", choices=BACKENDS, default="AUTO")
    install.add_argument("--source-ref", default="master", help="llama.cpp branch/tag/commit to build")

    commands.add_parser("version", help="Show installed llama-server version and pinned source commit")
    commands.add_parser("doctor", help="Inspect runtime, backend, model, and server readiness")

    openhands = commands.add_parser(
        "openhands",
        help="Install or inspect Hafiye's managed OpenHands coding runtime",
    )
    openhands_commands = openhands.add_subparsers(dest="runtime_openhands_command")
    openhands_commands.add_parser(
        "install",
        aliases=["setup"],
        help="Install the pinned OpenHands source checkout and package runtime",
    )
    openhands_commands.add_parser(
        "doctor",
        help="Inspect the pinned OpenHands coding runtime readiness",
    )

    model = commands.add_parser("model", help="Manage local GGUF models")
    model_commands = model.add_subparsers(dest="runtime_model_command")
    model_import = model_commands.add_parser("import", help="Import a local .gguf file")
    model_import.add_argument("path")
    model_import.add_argument("--id", dest="model_id")
    model_download = model_commands.add_parser("download", help="Download a .gguf from Hugging Face")
    model_download.add_argument("repo_id")
    model_download.add_argument("filename")
    model_download.add_argument("--revision", default="main")
    model_download.add_argument("--id", dest="model_id")
    model_download.add_argument("--sha256")
    model_commands.add_parser("list", aliases=["ls"], help="List registered GGUF models")
    model_delete = model_commands.add_parser("delete", help="Delete a registered GGUF model")
    model_delete.add_argument("model_id")

    server = commands.add_parser("server", help="Start/stop the local OpenAI-compatible server")
    server_commands = server.add_subparsers(dest="runtime_server_command")
    start = server_commands.add_parser("start", help="Load a model and start llama-server")
    start.add_argument("model_id")
    start.add_argument("--backend", choices=BACKENDS, default="AUTO")
    start.add_argument("--context-size", type=int, default=DEFAULT_CONTEXT_SIZE)
    start.add_argument("--gpu-layers", type=int)
    start.add_argument("--port", type=int, default=DEFAULT_PORT)
    server_commands.add_parser("stop", help="Stop llama-server")
    restart = server_commands.add_parser("restart", help="Restart llama-server with a model")
    restart.add_argument("model_id")
    restart.add_argument("--backend", choices=BACKENDS, default="AUTO")
    restart.add_argument("--context-size", type=int, default=DEFAULT_CONTEXT_SIZE)
    restart.add_argument("--gpu-layers", type=int)
    restart.add_argument("--port", type=int, default=DEFAULT_PORT)
    server_commands.add_parser("health", help="Show server health, active model, and log tail")
    recover = server_commands.add_parser(
        "recover",
        help="Recover a crashed/unhealthy llama-server from its saved state",
    )
    recover.add_argument(
        "--attempts",
        type=int,
        default=1,
        choices=range(1, 4),
        help="Bounded recovery attempts (1-3; default: 1)",
    )
    server_commands.add_parser("unload", help="Stop llama-server and unload the active model")

    parser.set_defaults(func=cmd_runtime)


__all__ = ["build_runtime_parser"]
