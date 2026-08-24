"""Process-safe task records for Hafiye's operator-facing Task Center.

This is the narrow P15 boundary between a delegated coding worker and the
gateway/Desktop.  It deliberately stores progress summaries, tool names,
commands, and file-change names only; OpenHands messages and workspace output
never enter the Task Center record.
"""

from __future__ import annotations

from copy import deepcopy
import threading
import time
from typing import Any, Callable


TASK_STATES = (
    "QUEUED",
    "PLANNING",
    "RUNNING",
    "WAITING",
    "PAUSED",
    "CANCELLING",
    "COMPLETED",
    "FAILED",
    "CANCELLED",
)
_TERMINAL_STATES = {"COMPLETED", "FAILED", "CANCELLED"}
_MAX_STEP_LENGTH = 1000
_MAX_SUMMARY_LENGTH = 12000
_MAX_ERROR_LENGTH = 4000
_MAX_HISTORY = 200


def _text(value: Any, limit: int) -> str:
    return str(value or "").strip()[:limit]


def _names(values: Any, limit: int = 500) -> list[str]:
    if not isinstance(values, (list, tuple, set)):
        return []
    result: list[str] = []
    for value in values:
        name = _text(value, 500)
        if name and name not in result:
            result.append(name)
        if len(result) >= limit:
            break
    return result


class TaskCenterRegistry:
    """Thread-safe in-memory task lifecycle registry.

    P15 needs live process progress and result exposure.  Durable task history
    and the complete generic task model remain P16 work; the record shape here
    already follows the master task model so the later persistence boundary can
    be added without changing the coding delegate contract.
    """

    def __init__(self) -> None:
        self._tasks: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._listeners: set[Callable[[dict[str, Any]], None]] = set()

    def subscribe(self, listener: Callable[[dict[str, Any]], None]) -> Callable[[], None]:
        with self._lock:
            self._listeners.add(listener)

        def dispose() -> None:
            with self._lock:
                self._listeners.discard(listener)

        return dispose

    def _snapshot_locked(self, task: dict[str, Any]) -> dict[str, Any]:
        return deepcopy(task)

    def _notify(self, task: dict[str, Any]) -> None:
        with self._lock:
            listeners = tuple(self._listeners)
            snapshot = self._snapshot_locked(task)
        for listener in listeners:
            try:
                listener(snapshot)
            except Exception:
                # A gateway/UI observer must never break worker completion.
                continue

    def create(
        self,
        *,
        task_id: str,
        goal: str,
        session_id: str = "",
        parent_task_id: str = "",
        route: str = "coding",
        provider: str = "",
        model: str = "",
        privacy_mode: str = "NORMAL",
        repository_path: str = "",
    ) -> dict[str, Any]:
        task_id = _text(task_id, 256)
        if not task_id:
            raise ValueError("task_id is required")
        now = time.time()
        task = {
            "task_id": task_id,
            "session_id": _text(session_id, 256),
            "parent_task_id": _text(parent_task_id, 256),
            "goal": _text(goal, _MAX_SUMMARY_LENGTH),
            "state": "QUEUED",
            "created_at": now,
            "started_at": None,
            "completed_at": None,
            "route": _text(route, 80),
            "provider": _text(provider, 120),
            "model": _text(model, 240),
            "privacy_mode": _text(privacy_mode, 40),
            "current_step_summary": "Queued for OpenHands",
            "result_summary": "",
            "error": "",
            "repository_path": _text(repository_path, 2000),
            "process_id": "",
            "progress_events": 0,
            "tool_history": [],
            "commands": [],
            "file_changes": [],
            "updated_at": now,
        }
        with self._lock:
            if task_id in self._tasks:
                raise ValueError(f"task already exists: {task_id}")
            self._tasks[task_id] = task
        self._notify(task)
        return deepcopy(task)

    def get(self, task_id: str) -> dict[str, Any] | None:
        with self._lock:
            task = self._tasks.get(str(task_id or ""))
            return self._snapshot_locked(task) if task is not None else None

    def list(self, *, session_id: str | None = None) -> list[dict[str, Any]]:
        wanted_session = _text(session_id, 256) if session_id else ""
        with self._lock:
            tasks = [
                self._snapshot_locked(task)
                for task in self._tasks.values()
                if not wanted_session or task["session_id"] == wanted_session
            ]
        tasks.sort(key=lambda task: float(task.get("created_at") or 0), reverse=True)
        return tasks

    def update(
        self,
        task_id: str,
        *,
        state: str | None = None,
        current_step_summary: str | None = None,
        result_summary: str | None = None,
        error: str | None = None,
        process_id: str | None = None,
        event_name: str | None = None,
        tool_name: str | None = None,
        source: str | None = None,
        changed_files: Any = None,
        command: str | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            task = self._tasks.get(str(task_id or ""))
            if task is None:
                raise KeyError(f"unknown task: {task_id}")
            now = time.time()
            if state is not None:
                normalized_state = _text(state, 32).upper()
                if normalized_state not in TASK_STATES:
                    raise ValueError(f"unknown task state: {normalized_state}")
                task["state"] = normalized_state
                if normalized_state in {"RUNNING", "WAITING", "PAUSED"} and not task["started_at"]:
                    task["started_at"] = now
                if normalized_state in _TERMINAL_STATES:
                    task["completed_at"] = task["completed_at"] or now
            if current_step_summary is not None:
                task["current_step_summary"] = _text(current_step_summary, _MAX_STEP_LENGTH)
            if result_summary is not None:
                task["result_summary"] = _text(result_summary, _MAX_SUMMARY_LENGTH)
            if error is not None:
                task["error"] = _text(error, _MAX_ERROR_LENGTH)
            if process_id is not None:
                task["process_id"] = _text(process_id, 256)
            if changed_files is not None:
                task["file_changes"] = _names(changed_files)
            if command:
                value = _text(command, 1000)
                if value and value not in task["commands"]:
                    task["commands"].append(value)
                    task["commands"] = task["commands"][-_MAX_HISTORY:]
            if event_name or tool_name or source:
                event = {
                    "event": _text(event_name, 240),
                    "tool": _text(tool_name, 240),
                    "source": _text(source, 240),
                    "at": now,
                }
                task["tool_history"].append(event)
                task["tool_history"] = task["tool_history"][-_MAX_HISTORY:]
                task["progress_events"] = int(task.get("progress_events") or 0) + 1
            task["updated_at"] = now
            snapshot = self._snapshot_locked(task)
        self._notify(task)
        return snapshot

    def cancel(self, task_id: str) -> dict[str, Any]:
        return self.update(
            task_id,
            state="CANCELLING",
            current_step_summary="Cancellation requested",
        )

    def clear(self) -> None:
        with self._lock:
            self._tasks.clear()


task_center = TaskCenterRegistry()


__all__ = ["TASK_STATES", "TaskCenterRegistry", "task_center"]
