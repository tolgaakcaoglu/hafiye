"""Compatibility adjustments for managed local model runtimes.

These helpers only change the request copy sent to a local endpoint.  The
persisted conversation and the user-visible transcript remain untouched.  The
boundary is intentionally narrow: Qwen3's ``/no_think`` control token is
needed for responsive tool turns on the managed local llama.cpp route, but it
must not be injected into cloud or remote self-hosted conversations.
"""

from __future__ import annotations

import re
from typing import Any

from agent.model_metadata import is_local_endpoint

_QWEN3_MODEL_RE = re.compile(r"(?:^|[/_.:-])qwen3(?:$|[/_.:-])", re.IGNORECASE)
_QWEN3_CONTROL_RE = re.compile(r"^\s*/(?:no_think|think)\b", re.IGNORECASE)


def is_local_qwen3_route(*, provider: Any, base_url: Any, model: Any) -> bool:
    """Return whether a route needs the local Qwen3 no-thinking hint.

    ``is_local_endpoint`` includes trusted private-network endpoints because
    Hafiye treats those as local-first runtimes.  Restricting the model family
    here keeps all other models and providers byte-for-byte unchanged.
    """

    provider_name = str(provider or "").strip().lower()
    if provider_name not in {"custom", "local"}:
        return False
    model_name = str(model or "").strip()
    return bool(model_name and _QWEN3_MODEL_RE.search(model_name) and is_local_endpoint(str(base_url or "")))


def apply_local_qwen3_no_think(content: Any) -> Any:
    """Prefix a string user turn with Qwen3's explicit no-thinking control.

    The operation is idempotent and preserves an explicit ``/think`` or
    ``/no_think`` choice.  Non-string/multimodal content is left alone because
    adding a raw string to a structured message would change its wire shape.
    """

    if not isinstance(content, str) or not content.strip() or _QWEN3_CONTROL_RE.match(content):
        return content
    return f"/no_think\n{content}"


__all__ = ["apply_local_qwen3_no_think", "is_local_qwen3_route"]
