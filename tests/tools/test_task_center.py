from __future__ import annotations

from tools.task_center import TaskCenterRegistry


def test_task_center_exposes_summaries_without_transcript_content():
    registry = TaskCenterRegistry()
    updates = []
    registry.subscribe(updates.append)

    created = registry.create(
        task_id="coding-1",
        goal="Fix the failing fixture test",
        session_id="session-1",
        provider="gemini",
        model="gemini-flash-lite-latest",
        repository_path="/tmp/fixture",
    )
    assert created["state"] == "QUEUED"

    running = registry.update(
        "coding-1",
        state="RUNNING",
        current_step_summary="OpenHands: ToolCallEvent",
        event_name="ToolCallEvent",
        tool_name="terminal",
        source="agent",
        command="openhands_worker",
    )
    completed = registry.update(
        "coding-1",
        state="COMPLETED",
        result_summary="Tests passed",
        changed_files=["bug.py"],
    )

    assert running["progress_events"] == 1
    assert completed["file_changes"] == ["bug.py"]
    assert completed["result_summary"] == "Tests passed"
    assert "transcript" not in completed
    assert updates[-1]["state"] == "COMPLETED"
    assert registry.list(session_id="session-1")[0]["task_id"] == "coding-1"


def test_task_center_cancel_is_an_explicit_state_transition():
    registry = TaskCenterRegistry()
    registry.create(task_id="coding-2", goal="stop")
    cancelled = registry.cancel("coding-2")
    assert cancelled["state"] == "CANCELLING"
    assert cancelled["current_step_summary"] == "Cancellation requested"
