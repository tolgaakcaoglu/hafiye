"""``hermes model`` subcommand parser.

Extracted verbatim from ``hermes_cli/main.py:main()`` (god-file Phase 2).
Handler injected to avoid importing ``main``.
"""

from __future__ import annotations

import argparse
from typing import Callable

from hermes_cli.local_runtime import BACKENDS, DEFAULT_CONTEXT_SIZE, DEFAULT_PORT


def build_model_parser(
    subparsers,
    *,
    cmd_model: Callable,
    cmd_hafiye_model: Callable | None = None,
) -> argparse.ArgumentParser:
    """Attach the ``model`` subcommand to ``subparsers``."""
    # =========================================================================
    # model command
    # =========================================================================
    model_parser = subparsers.add_parser(
        "model",
        help="Select default model and provider",
        description="Interactively select your inference provider and default model",
    )
    model_parser.add_argument(
        "--refresh",
        action="store_true",
        help="Wipe the model picker disk cache and re-fetch every provider's live /v1/models list.",
    )
    model_parser.add_argument(
        "--portal-url",
        help="Portal base URL for Nous login (default: production portal)",
    )
    model_parser.add_argument(
        "--inference-url",
        help="Inference API base URL for Nous login (default: production inference API)",
    )
    model_parser.add_argument(
        "--client-id",
        default=None,
        help="OAuth client id to use for Nous login (default: hermes-cli)",
    )
    model_parser.add_argument(
        "--scope", default=None, help="OAuth scope to request for Nous login"
    )
    model_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not attempt to open the browser automatically during Nous login",
    )
    model_parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="HTTP request timeout in seconds for Nous login (default: 15)",
    )
    model_parser.add_argument(
        "--ca-bundle", help="Path to CA bundle PEM file for Nous TLS verification"
    )
    model_parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS verification for Nous login (testing only)",
    )
    if cmd_hafiye_model is not None:
        model_actions = model_parser.add_subparsers(dest="model_action")
        load = model_actions.add_parser(
            "load",
            help="Load a registered GGUF model in llama-server",
        )
        load.add_argument("model_id", nargs="?", help="Registered model id (optional when unambiguous)")
        load.add_argument("--backend", choices=BACKENDS, default="AUTO")
        load.add_argument("--context-size", type=int, default=DEFAULT_CONTEXT_SIZE)
        load.add_argument("--gpu-layers", type=int)
        load.add_argument("--port", type=int, default=DEFAULT_PORT)
        load.add_argument("--json", action="store_true")
        load.set_defaults(func=cmd_hafiye_model)

        unload = model_actions.add_parser(
            "unload",
            help="Stop llama-server and unload the active model",
        )
        unload.add_argument("--json", action="store_true")
        unload.set_defaults(func=cmd_hafiye_model)

    model_parser.set_defaults(func=cmd_model)
    return model_parser
