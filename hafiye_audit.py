"""Canonical, redacted Hafiye product audit stream."""

from __future__ import annotations

import datetime as dt
import json
import os
import threading
from pathlib import Path
from typing import Any

from hermes_constants import get_hafiye_state_home


_LOCK = threading.Lock()


def audit_path() -> Path:
    return get_hafiye_state_home() / "logs" / "audit.log"


def _safe_value(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        if isinstance(value, str):
            try:
                from agent.redact import redact_sensitive_text

                return redact_sensitive_text(value, force=True, redact_url_credentials=True)
            except Exception:
                return value[:2000]
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [_safe_value(item) for item in value[:100]]
    if isinstance(value, dict):
        return {
            str(key): _safe_value(item)
            for key, item in list(value.items())[:100]
            if str(key).lower() not in {"token", "api_key", "password", "secret", "authorization"}
        }
    return str(value)[:2000]


def record_audit(event: str, **fields: Any) -> None:
    """Append one owner-only JSONL event; auditing never breaks execution."""

    entry = {
        "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
        "event": str(event),
        **{str(key): _safe_value(value) for key, value in fields.items()},
    }
    path = audit_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with _LOCK:
            fd = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
            try:
                os.fchmod(fd, 0o600)
                os.write(fd, (json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n").encode())
            finally:
                os.close(fd)
    except Exception:
        return


__all__ = ["audit_path", "record_audit"]
