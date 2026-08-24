"""Hafiye's OpenHands V1 coding delegation tool."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
import shlex
import subprocess
import time
import uuid
from typing import Any

from hafiye_policy import (
    enforce_runtime_policy,
    normalize_privacy_mode,
    resolve_hafiye_route,
)
from hermes_cli.config import load_config
from hermes_cli.openhands_runtime import (
    get_openhands_runtime_paths,
    openhands_runtime_ready,
    openhands_runtime_doctor,
)
from tools.interrupt import is_interrupted
from tools.process_registry import process_registry
from tools.registry import registry, tool_error


logger = logging.getLogger(__name__)

CODING_DELEGATE_SCHEMA = {
    "description": (
        "Delegate a coding task to the Hafiye-managed OpenHands V1 specialist. "
        "OpenHands edits the supplied local host repository and reports the "
        "verification result. The Hafiye coding route is selected automatically."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "goal": {
                "type": "string",
                "description": "The concrete coding goal to complete.",
            },
            "repository_path": {
                "type": "string",
                "description": "Absolute local host path of the repository to edit.",
            },
            "constraints": {
                "type": "string",
                "description": "Implementation, scope, or safety constraints.",
            },
            "model_route": {
                "type": "string",
                "description": (
                    "Optional route label for audit/context. The Hafiye coding "
                    "route remains authoritative."
                ),
            },
            "network_policy": {
                "type": "string",
                "enum": ["NORMAL", "LOCAL_ONLY", "OFFLINE"],
                "description": "Network/privacy policy for the coding task.",
            },
            "expected_verification": {
                "type": "string",
                "description": "Tests or verification commands OpenHands must run.",
            },
            "max_iterations": {
                "type": "integer",
                "minimum": 1,
                "maximum": 500,
                "description": "Maximum OpenHands agent iterations for this task.",
            },
        },
        "required": ["goal", "repository_path"],
    },
}


def check_coding_delegate_requirements() -> bool:
    return openhands_runtime_ready()


def _parent_credential(parent_agent: Any) -> str:
    value = getattr(parent_agent, "api_key", None)
    if not value:
        client_kwargs = getattr(parent_agent, "_client_kwargs", None)
        if isinstance(client_kwargs, dict):
            value = client_kwargs.get("api_key")
    if hasattr(value, "get_secret_value"):
        value = value.get_secret_value()
    return str(value or "").strip()


def _parent_route(parent_agent: Any) -> tuple[dict[str, Any], str]:
    if parent_agent is None:
        raise RuntimeError("coding_delegate requires an active Hafiye agent route")
    config = load_config() or {}
    route = resolve_hafiye_route(
        config,
        provider=getattr(parent_agent, "provider", ""),
        model=getattr(parent_agent, "model", ""),
        base_url=getattr(parent_agent, "base_url", ""),
        slot="coding",
    )
    entry = (
        ((config.get("hafiye") or {}).get("route_slots") or {}).get("coding")
        if isinstance(config, dict)
        else {}
    )
    base_url = ""
    if isinstance(entry, dict):
        base_url = str(entry.get("base_url") or "").strip()
    base_url = base_url or str(getattr(parent_agent, "base_url", "") or "").strip()
    return (
        {
            "provider": route.provider,
            "model": route.model,
            "base_url": base_url,
            "privacy_mode": route.privacy_mode,
            "slot": route.slot,
            "source": route.source,
            "route_hint": route.as_dict(),
        },
        _parent_credential(parent_agent),
    )


def _resolve_repository(raw: Any, parent_agent: Any) -> Path:
    value = str(raw or "").strip()
    if not value:
        raise ValueError("repository_path is required")
    path = Path(value).expanduser()
    if not path.is_absolute():
        base = (
            getattr(parent_agent, "terminal_cwd", None)
            or getattr(parent_agent, "cwd", None)
            or os.getcwd()
        )
        path = Path(base) / path
    path = path.resolve()
    if not path.is_dir():
        raise ValueError(f"repository_path is not a directory: {path}")
    return path


def _result_lines(output: str) -> tuple[dict[str, Any] | None, int]:
    result: dict[str, Any] | None = None
    progress_count = 0
    for line in output.splitlines():
        try:
            record = json.loads(line)
        except (TypeError, ValueError):
            continue
        if not isinstance(record, dict):
            continue
        if record.get("type") == "progress":
            progress_count += 1
        elif record.get("type") == "result":
            result = record
    return result, progress_count


def _wait_for_process(session_id: str, max_seconds: int = 7200) -> dict[str, Any]:
    deadline = time.monotonic() + max(1, max_seconds)
    while time.monotonic() < deadline:
        status = process_registry.poll(session_id)
        if status.get("status") == "exited":
            if status.get("completion_reason") == "killed" or str(
                status.get("termination_source") or ""
            ).startswith("emergency_stop"):
                status["status"] = "cancelled"
            return status
        if is_interrupted():
            process_registry.kill_process(
                session_id,
                source="coding_delegate.interrupt",
                consume_output=True,
            )
            return {
                "status": "cancelled",
                "completion_reason": "interrupted",
            }
        time.sleep(0.25)
    process_registry.kill_process(
        session_id,
        source="coding_delegate.timeout",
        consume_output=True,
    )
    return {"status": "timeout", "completion_reason": "timeout"}


def _handle_coding_delegate(args: dict[str, Any], **kwargs: Any) -> str:
    parent_agent = kwargs.get("parent_agent")
    if not openhands_runtime_ready():
        return tool_error(
            "OpenHands managed runtime is not ready: "
            + "; ".join(openhands_runtime_doctor().get("blockers", []))
        )

    try:
        repository = _resolve_repository(args.get("repository_path"), parent_agent)
        route, credential = _parent_route(parent_agent)
        requested_policy = normalize_privacy_mode(args.get("network_policy") or route["privacy_mode"])
        enforce_runtime_policy(
            requested_policy,
            provider=route["provider"],
            base_url=route["base_url"],
            model=route["model"],
        )
        goal = str(args.get("goal") or "").strip()
        if not goal:
            raise ValueError("goal is required")
    except Exception as exc:
        return tool_error(f"coding_delegate validation failed: {type(exc).__name__}: {exc}")

    paths = get_openhands_runtime_paths()
    request_id = f"coding_{uuid.uuid4().hex[:16]}"
    paths.request_root.mkdir(parents=True, exist_ok=True)
    request_path = paths.request_root / f"{request_id}.json"
    payload = {
        "request_id": request_id,
        "goal": goal,
        "repository_path": str(repository),
        "constraints": str(args.get("constraints") or "").strip(),
        "model_route": str(args.get("model_route") or "").strip(),
        "network_policy": requested_policy,
        "expected_verification": str(args.get("expected_verification") or "").strip(),
        "provider": route["provider"],
        "model": route["model"],
        "base_url": route["base_url"],
        "max_iterations": int(args.get("max_iterations") or 100),
    }
    request_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    try:
        request_path.chmod(0o600)
    except OSError:
        pass

    runtime_python = paths.python
    command = shlex.join(
        [
            str(runtime_python),
            str(Path(__file__).resolve().with_name("openhands_worker.py")),
            "--request",
            str(request_path),
        ]
    )
    env_vars = {
        "OPENHANDS_SUPPRESS_BANNER": "1",
        "ALLOW_SHORT_CONTEXT_WINDOWS": "1",
    }
    if credential:
        # The local environment sanitizer strips provider secret names.  The
        # force prefix is the reviewed escape hatch for this private, one-shot
        # boundary; the worker consumes it immediately and removes it before
        # OpenHands' terminal subprocesses are created.
        env_vars["_HERMES_FORCE_HAFIYE_OPENHANDS_CREDENTIAL"] = credential

    task_id = str(kwargs.get("task_id") or f"hafiye-{request_id}")
    session_key = str(kwargs.get("session_id") or "")
    session = None
    try:
        session = process_registry.spawn_local(
            command,
            cwd=str(repository),
            task_id=task_id,
            session_key=session_key,
            env_vars=env_vars,
        )
        logger.info(
            "OpenHands coding delegation started: process_id=%s route=%s/%s repo=%s",
            session.id,
            route["provider"],
            route["model"],
            repository,
        )
        wait_result = _wait_for_process(session.id)
        log_result = process_registry.read_log(session.id, offset=0, limit=10000)
        output = str(log_result.get("output") or "")
        worker_result, progress_count = _result_lines(output)
        if wait_result.get("status") == "cancelled":
            return json.dumps(
                {
                    "status": "cancelled",
                    "process_id": session.id,
                    "progress_events": progress_count,
                },
                ensure_ascii=False,
            )
        if worker_result is None:
            try:
                from agent.redact import redact_sensitive_text

                output_tail = redact_sensitive_text(output[-2000:], code_file=True)
            except Exception:
                output_tail = output[-2000:]
            return tool_error(
                "OpenHands worker exited without a result. "
                f"process_id={session.id}; exit={wait_result.get('exit_code')}; "
                f"output_tail={output_tail}"
            )
        worker_result.update(
            {
                "process_id": session.id,
                "route": {
                    "provider": route["provider"],
                    "model": route["model"],
                    "privacy_mode": requested_policy,
                    "slot": route["slot"],
                },
                "progress_events": progress_count,
            }
        )
        return json.dumps(worker_result, ensure_ascii=False)
    except Exception as exc:
        if session is not None:
            try:
                process_registry.kill_process(
                    session.id,
                    source="coding_delegate.error",
                    consume_output=True,
                )
            except Exception:
                pass
        logger.exception("OpenHands coding delegation failed")
        return tool_error(f"OpenHands coding delegation failed: {type(exc).__name__}: {exc}")
    finally:
        try:
            request_path.unlink(missing_ok=True)
        except OSError:
            pass


registry.register(
    name="coding_delegate",
    toolset="delegation",
    schema=CODING_DELEGATE_SCHEMA,
    handler=_handle_coding_delegate,
    check_fn=check_coding_delegate_requirements,
    emoji="🛠️",
    max_result_size_chars=100_000,
)


__all__ = ["CODING_DELEGATE_SCHEMA", "check_coding_delegate_requirements"]
