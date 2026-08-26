"""Resolve the external product identity without renaming Hermes internals."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def is_hafiye_invocation() -> bool:
    """Return whether this process was entered through a Hafiye surface."""

    executable = Path(sys.argv[0] or "").name.lower()
    return (
        executable.startswith("hafiye")
        or bool(os.environ.get("HAFIYE_PACKAGE_ROOT", "").strip())
        or os.environ.get("HAFIYE_PRODUCT", "").strip().lower() in {"1", "true", "yes", "on"}
    )


def command_name() -> str:
    return "hafiye" if is_hafiye_invocation() else "hermes"


def product_name() -> str:
    return "Hafiye" if is_hafiye_invocation() else "Hermes"


def externalize(text: str) -> str:
    """Translate upstream identity references only at the Hafiye UI boundary."""

    if not is_hafiye_invocation():
        return text
    return (
        text.replace("Hermes Agent", "Hafiye")
        .replace("hermes-yuanbao", "Yuanbao integration")
        .replace("Hermes-managed", "Hafiye-managed")
        .replace("Hermes databases", "Hafiye databases")
        .replace("Hermes containers", "Hafiye containers")
        .replace("Hermes a custom", "Hafiye özel bir")
        .replace("`hermes", "`hafiye")
        .replace("'hermes", "'hafiye")
        .replace(" hermes ", " hafiye ")
    )


__all__ = ["command_name", "externalize", "is_hafiye_invocation", "product_name"]
