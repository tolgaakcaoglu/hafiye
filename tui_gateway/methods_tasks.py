"""Gateway RPC handlers for the P15 coding-task Task Center surface."""

from .method_ctx import HandlerRegistry

_registry = HandlerRegistry()
method = _registry.method


@method("tasks.list")
def _(rid, params: dict) -> dict:
    """Return safe task summaries; no OpenHands transcript is exposed."""
    try:
        from tools.task_center import task_center

        session_id = str(params.get("session_id") or "").strip()
        return _ok(
            rid,
            {
                "tasks": task_center.list(session_id=session_id or None),
            },
        )
    except Exception as exc:
        return _err(rid, 5010, str(exc))


@method("tasks.cancel")
def _(rid, params: dict) -> dict:
    """Cancel a registered task through its existing process boundary."""
    task_id = str(params.get("task_id") or "").strip()
    if not task_id:
        return _err(rid, 4012, "task_id required")

    try:
        from tools.process_registry import process_registry
        from tools.task_center import task_center

        task = task_center.get(task_id)
        if task is None:
            return _err(rid, 4044, f"no such task: {task_id}")
        if task.get("state") in {"COMPLETED", "FAILED", "CANCELLED"}:
            return _ok(rid, {"task": task, "process": None})

        task_center.cancel(task_id)
        process_id = str(task.get("process_id") or "")
        if not process_id:
            task = task_center.update(
                task_id,
                state="CANCELLED",
                current_step_summary="Task cancelled before worker start",
            )
            return _ok(rid, {"task": task, "process": None})

        process = process_registry.kill_process(
            process_id,
            source="task_center.cancel",
            consume_output=True,
        )
        if isinstance(process, dict) and process.get("status") in {
            "exited",
            "killed",
            "cancelled",
        }:
            task = task_center.update(
                task_id,
                state="CANCELLED",
                current_step_summary="Task cancelled",
                subagent_state="CANCELLED",
            )
        return _ok(rid, {"task": task_center.get(task_id), "process": process})
    except Exception as exc:
        return _err(rid, 5010, str(exc))


def register(server) -> None:
    _registry.install(server)


__all__ = ["register"]
