"""Durable, process-safe records for Hafiye's operator-facing Task Center.

The registry is the shared business-logic boundary between delegated workers,
the gateway, and Desktop. It stores only operator-safe metadata: lifecycle
state, summaries, tool names, commands, and file-change names. OpenHands
messages, workspace output, credentials, and private chain-of-thought never
enter a Task Center record.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import threading
import time
from typing import Any, Callable

from hermes_constants import get_hafiye_state_home


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
# QUEUED tasks have not acquired a worker yet and may legitimately survive a
# gateway reconnect. Only states that imply an in-flight worker are marked
# interrupted when a fresh gateway process opens the store.
_RECOVERABLE_ACTIVE_STATES = {
    "PLANNING",
    "RUNNING",
    "WAITING",
    "PAUSED",
    "CANCELLING",
}
_MAX_STEP_LENGTH = 1000
_MAX_SUMMARY_LENGTH = 12000
_MAX_ERROR_LENGTH = 4000
_MAX_HISTORY = 200
_DEFAULT_DB_NAME = "task_center.db"


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
    """Thread-safe task lifecycle registry backed by a small SQLite store.

    The default database is under Hafiye's XDG state root. Tests and isolated
    callers can pass ``":memory:"`` or an explicit path. A fresh registry
    marks in-flight records as interrupted when they came from a previous
    process: an old worker cannot be reported as still running after a gateway
    restart, while unstarted QUEUED work remains queued.
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        self._db_path = None if db_path == ":memory:" else Path(
            db_path or (get_hafiye_state_home() / _DEFAULT_DB_NAME)
        )
        self._tasks: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._listeners: set[Callable[[dict[str, Any]], None]] = set()
        self._connection: sqlite3.Connection | None = None
        with self._lock:
            self._open_locked()

    def _open_locked(self) -> None:
        if self._db_path is None:
            connection = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            connection = sqlite3.connect(
                str(self._db_path),
                check_same_thread=False,
                timeout=10,
            )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=10000")
        if self._db_path is not None:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=NORMAL")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS task_center_tasks (
                task_id TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                session_id TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                record_json TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_task_center_created "
            "ON task_center_tasks(created_at DESC)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_task_center_session "
            "ON task_center_tasks(session_id, created_at DESC)"
        )
        connection.commit()
        self._connection = connection
        self._load_locked()

    def _load_locked(self) -> None:
        assert self._connection is not None
        rows = self._connection.execute(
            "SELECT record_json FROM task_center_tasks ORDER BY created_at DESC"
        ).fetchall()
        recovered: list[dict[str, Any]] = []
        for row in rows:
            try:
                task = json.loads(str(row["record_json"]))
            except (TypeError, ValueError, json.JSONDecodeError):
                continue
            if not isinstance(task, dict):
                continue
            task_id = _text(task.get("task_id"), 256)
            if not task_id:
                continue
            normalized = self._normalize_record(task)
            if normalized["state"] in _RECOVERABLE_ACTIVE_STATES:
                now = time.time()
                normalized.update(
                    {
                        "state": "FAILED",
                        "completed_at": normalized.get("completed_at") or now,
                        "updated_at": now,
                        "current_step_summary": "Task interrupted by gateway restart",
                        "error": normalized.get("error")
                        or "Gateway restarted before the task completed",
                        "subagent_state": "INTERRUPTED_BY_GATEWAY_RESTART",
                    }
                )
                recovered.append(normalized)
            self._tasks[task_id] = normalized
        for task in recovered:
            self._persist_locked(task)
        if recovered:
            self._connection.commit()

    @staticmethod
    def _normalize_record(task: dict[str, Any]) -> dict[str, Any]:
        defaults: dict[str, Any] = {
            "task_id": "",
            "session_id": "",
            "parent_task_id": "",
            "goal": "",
            "state": "FAILED",
            "created_at": time.time(),
            "started_at": None,
            "completed_at": None,
            "route": "coding",
            "provider": "",
            "model": "",
            "privacy_mode": "NORMAL",
            "current_step_summary": "",
            "result_summary": "",
            "error": "",
            "repository_path": "",
            "process_id": "",
            "subagent_state": "",
            "progress_events": 0,
            "tool_history": [],
            "commands": [],
            "file_changes": [],
            "updated_at": time.time(),
        }
        for key, default in defaults.items():
            task.setdefault(key, default)
        task["task_id"] = _text(task["task_id"], 256)
        task["session_id"] = _text(task["session_id"], 256)
        task["parent_task_id"] = _text(task["parent_task_id"], 256)
        task["goal"] = _text(task["goal"], _MAX_SUMMARY_LENGTH)
        task["state"] = _text(task["state"], 32).upper()
        if task["state"] not in TASK_STATES:
            task["state"] = "FAILED"
        task["route"] = _text(task["route"], 80)
        task["provider"] = _text(task["provider"], 120)
        task["model"] = _text(task["model"], 240)
        task["privacy_mode"] = _text(task["privacy_mode"], 40)
        task["current_step_summary"] = _text(task["current_step_summary"], _MAX_STEP_LENGTH)
        task["result_summary"] = _text(task["result_summary"], _MAX_SUMMARY_LENGTH)
        task["error"] = _text(task["error"], _MAX_ERROR_LENGTH)
        task["repository_path"] = _text(task["repository_path"], 2000)
        task["process_id"] = _text(task["process_id"], 256)
        task["subagent_state"] = _text(task["subagent_state"], 240)
        task["commands"] = _names(task.get("commands"), _MAX_HISTORY)
        task["file_changes"] = _names(task.get("file_changes"))
        history = task.get("tool_history")
        task["tool_history"] = history[-_MAX_HISTORY:] if isinstance(history, list) else []
        try:
            task["progress_events"] = max(0, int(task.get("progress_events") or 0))
        except (TypeError, ValueError):
            task["progress_events"] = 0
        return task

    def _persist_locked(self, task: dict[str, Any]) -> None:
        assert self._connection is not None
        self._connection.execute(
            """
            INSERT INTO task_center_tasks
                (task_id, state, session_id, created_at, updated_at, record_json)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(task_id) DO UPDATE SET
                state=excluded.state,
                session_id=excluded.session_id,
                created_at=excluded.created_at,
                updated_at=excluded.updated_at,
                record_json=excluded.record_json
            """,
            (
                task["task_id"],
                task["state"],
                task["session_id"],
                float(task.get("created_at") or 0),
                float(task.get("updated_at") or 0),
                json.dumps(task, ensure_ascii=False, separators=(",", ":")),
            ),
        )
        self._connection.commit()

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
        subagent_state: str = "",
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
            "current_step_summary": "Queued for worker",
            "result_summary": "",
            "error": "",
            "repository_path": _text(repository_path, 2000),
            "process_id": "",
            "subagent_state": _text(subagent_state, 240),
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
            self._persist_locked(task)
            snapshot = self._snapshot_locked(task)
        self._notify(task)
        return snapshot

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
        subagent_state: str | None = None,
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
                if subagent_state is None:
                    task["subagent_state"] = normalized_state
            if current_step_summary is not None:
                task["current_step_summary"] = _text(current_step_summary, _MAX_STEP_LENGTH)
            if result_summary is not None:
                task["result_summary"] = _text(result_summary, _MAX_SUMMARY_LENGTH)
            if error is not None:
                task["error"] = _text(error, _MAX_ERROR_LENGTH)
            if process_id is not None:
                task["process_id"] = _text(process_id, 256)
            if subagent_state is not None:
                task["subagent_state"] = _text(subagent_state, 240)
            if changed_files is not None:
                task["file_changes"] = _names(
                    [*task.get("file_changes", []), *_names(changed_files)]
                )
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
            self._persist_locked(task)
            snapshot = self._snapshot_locked(task)
        self._notify(task)
        return snapshot

    def cancel(self, task_id: str) -> dict[str, Any]:
        return self.update(
            task_id,
            state="CANCELLING",
            current_step_summary="Cancellation requested",
            subagent_state="CANCELLING",
        )

    def delete(self, task_id: str) -> bool:
        with self._lock:
            task_id = str(task_id or "")
            existed = task_id in self._tasks
            self._tasks.pop(task_id, None)
            if self._connection is not None:
                self._connection.execute(
                    "DELETE FROM task_center_tasks WHERE task_id = ?", (task_id,)
                )
                self._connection.commit()
            return existed

    def clear(self, *, delete_persisted: bool = True) -> None:
        """Clear records; callers can retain the durable store explicitly."""
        with self._lock:
            self._tasks.clear()
            if delete_persisted and self._connection is not None:
                self._connection.execute("DELETE FROM task_center_tasks")
                self._connection.commit()

    def close(self) -> None:
        with self._lock:
            if self._connection is not None:
                self._connection.close()
                self._connection = None


task_center = TaskCenterRegistry()


__all__ = ["TASK_STATES", "TaskCenterRegistry", "task_center"]
