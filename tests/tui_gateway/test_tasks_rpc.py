from __future__ import annotations

from tui_gateway import server
from tools.task_center import task_center


def test_tasks_list_rpc_returns_task_center_record():
    task_center.clear()
    task_center.create(
        task_id="rpc-task-1",
        goal="Inspect fixture",
        session_id="rpc-session",
        provider="gemini",
        model="gemini-flash-lite-latest",
    )

    response = server._methods["tasks.list"]("rpc-1", {})

    assert response["result"]["tasks"][0]["task_id"] == "rpc-task-1"
    assert response["result"]["tasks"][0]["state"] == "QUEUED"


def test_tasks_cancel_rpc_transitions_task_without_worker():
    task_center.clear()
    task_center.create(task_id="rpc-task-2", goal="Stop before spawn")

    response = server._methods["tasks.cancel"]("rpc-2", {"task_id": "rpc-task-2"})

    assert response["result"]["task"]["state"] == "CANCELLED"
    assert response["result"]["task"]["current_step_summary"] == (
        "Task cancelled before worker start"
    )
