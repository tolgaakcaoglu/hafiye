"""Subprocess entrypoint for one local OpenHands V1 coding conversation.

The Hafiye process owns routing, cancellation, and process tracking.  This
worker owns only the official OpenHands SDK conversation.  It communicates
with the parent through redacted JSON-lines progress/result records; raw
OpenHands events and tool output are deliberately not printed because they can
contain workspace data or credentials.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


_SECRET_ENV = "HAFIYE_OPENHANDS_CREDENTIAL"


def _emit(kind: str, **payload: Any) -> None:
    record = {"type": kind, **payload}
    print(json.dumps(record, ensure_ascii=False, separators=(",", ":")), flush=True)


def _model_name(provider: str, model: str) -> str:
    provider = (provider or "").strip().lower().replace("-", "_")
    model = (model or "").strip()
    if not model:
        raise ValueError("Hafiye coding route did not resolve a model")
    if provider in {"gemini", "google", "google_ai", "google_genai"}:
        return model if model.startswith("gemini/") else f"gemini/{model}"
    if provider in {"anthropic", "claude"}:
        return model if model.startswith("anthropic/") else f"anthropic/{model}"
    if provider == "openrouter":
        return model if model.startswith("openrouter/") else f"openrouter/{model}"
    if provider in {"openai", "custom", "local", "llama_cpp", "llamacpp", "vllm", "lmstudio"}:
        return model if model.startswith("openai/") else f"openai/{model}"
    if "/" in model:
        return model
    return model


def _base_url(provider: str, value: str) -> str | None:
    # Native Gemini routing is selected by the LiteLLM model prefix.  The
    # Hafiye provider URL is not an OpenAI-compatible api_base and passing it
    # as one would turn a valid Gemini route into a malformed request.
    normalized = (provider or "").strip().lower().replace("-", "_")
    if normalized in {"gemini", "google", "google_ai", "google_genai"}:
        return None
    return value.strip() or None


def _message_text(event: Any) -> str:
    message = getattr(event, "llm_message", None)
    content = getattr(message, "content", None) if message is not None else None
    if content is None:
        return ""
    try:
        from openhands.sdk.llm import content_to_str

        return "".join(str(part) for part in content_to_str(content) if part).strip()
    except (TypeError, ValueError):
        return ""


def _safe_error(exc: BaseException) -> str:
    text = f"{type(exc).__name__}: {exc}"
    for marker in ("Bearer ", "api_key=", "api-key=", "key="):
        if marker in text:
            text = text.split(marker, 1)[0] + marker + "[REDACTED]"
    return text[-1000:]


def _changed_files(repository: Path) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=repository,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()][:500]


def run_request(request_path: Path) -> int:
    request = json.loads(request_path.read_text(encoding="utf-8"))
    repository = Path(str(request.get("repository_path", ""))).expanduser().resolve()
    if not repository.is_dir():
        raise ValueError(f"repository_path is not a directory: {repository}")

    goal = str(request.get("goal", "")).strip()
    if not goal:
        raise ValueError("goal is required")
    constraints = str(request.get("constraints", "")).strip()
    verification = str(request.get("expected_verification", "")).strip()
    provider = str(request.get("provider", "")).strip()
    model = _model_name(provider, str(request.get("model", "")))
    base_url = _base_url(provider, str(request.get("base_url", "")))
    api_key = os.environ.pop(_SECRET_ENV, "").strip() or None
    os.environ.pop("_HERMES_FORCE_HAFIYE_OPENHANDS_CREDENTIAL", None)
    os.environ["OPENHANDS_SUPPRESS_BANNER"] = "1"
    os.environ.setdefault("ALLOW_SHORT_CONTEXT_WINDOWS", "1")

    from pydantic import SecretStr
    from openhands.sdk import Agent, Conversation, LLM
    from openhands.tools.preset.default import get_default_agent

    llm = LLM(
        usage_id="hafiye-coding",
        model=model,
        api_key=SecretStr(api_key) if api_key else None,
        base_url=base_url,
    )
    agent: Agent = get_default_agent(llm=llm, cli_mode=True)

    def on_event(event: Any) -> None:
        tool_name = getattr(event, "tool_name", None)
        source = getattr(event, "source", None)
        _emit(
            "progress",
            event=type(event).__name__,
            source=str(source) if source is not None else "",
            tool=str(tool_name) if tool_name else "",
        )

    conversation = Conversation(
        agent=agent,
        workspace=repository,
        callbacks=[on_event],
        max_iteration_per_run=max(1, min(int(request.get("max_iterations", 100)), 500)),
    )
    prompt_parts = [
        "You are Hafiye's coding specialist. Work only in the supplied local repository.",
        f"Goal:\n{goal}",
    ]
    if constraints:
        prompt_parts.append(f"Constraints:\n{constraints}")
    if verification:
        prompt_parts.append(
            "Expected verification (run it when appropriate and report the exact result):\n"
            + verification
        )
    prompt_parts.append(
        "Inspect the repository before editing. Make the smallest maintainable change, "
        "run the requested verification, and finish with a concise summary."
    )
    try:
        conversation.send_message("\n\n".join(prompt_parts))
        _emit("started", model=model, provider=provider, repository=str(repository))
        conversation.run()

        status = getattr(
            conversation.state.execution_status,
            "value",
            conversation.state.execution_status,
        )
        status = str(status)
        summary = ""
        for event in reversed(getattr(conversation.state, "events", [])):
            source = getattr(event, "source", None)
            source_value = getattr(source, "value", source)
            if str(source_value).lower() == "agent":
                summary = _message_text(event)
                if not summary:
                    action = getattr(event, "action", None)
                    action_message = getattr(action, "message", None)
                    if isinstance(action_message, str):
                        summary = action_message.strip()
                if not summary and type(event).__name__ == "MessageEvent":
                    try:
                        visualization = getattr(event, "visualize", None)
                        summary = str(
                            getattr(visualization, "plain", visualization) or ""
                        ).strip()
                    except Exception:
                        summary = ""
                if summary:
                    break

        changed_files = _changed_files(repository)
        if not summary and status == "finished":
            changed_label = ", ".join(changed_files) if changed_files else "none"
            summary = f"OpenHands completed the run. Changed files: {changed_label}."

        _emit(
            "result",
            status="completed" if status == "finished" else status,
            execution_status=status,
            summary=summary[-12000:],
            changed_files=changed_files,
            event_count=len(getattr(conversation.state, "events", [])),
        )
        return 0 if status == "finished" else 1
    finally:
        conversation.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one Hafiye OpenHands coding request")
    parser.add_argument("--request", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        return run_request(args.request)
    except KeyboardInterrupt:
        _emit("result", status="cancelled", execution_status="cancelled")
        return 130
    except Exception as exc:  # pragma: no cover - exercised by real runtime failures
        _emit("result", status="error", error=_safe_error(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
