from __future__ import annotations

from tools.task_center import TaskCenterRegistry


def test_task_center_exposes_summaries_without_transcript_content():
    registry = TaskCenterRegistry(":memory:")
    updates = []
    registry.subscribe(updates.append)

    created = registry.create(
        task_id="coding-1",
        goal="Fix the failing fixture test",
        session_id="session-1",
        provider="gemini",
        model="gemini-flash-lite-latest",
        repository_path="/tmp/fixture",
        subagent_state="QUEUED",
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
        subagent_state="RUNNING",
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
    assert completed["subagent_state"] == "COMPLETED"
    assert "transcript" not in completed
    assert updates[-1]["state"] == "COMPLETED"
    assert registry.list(session_id="session-1")[0]["task_id"] == "coding-1"


def test_task_center_cancel_is_an_explicit_state_transition():
    registry = TaskCenterRegistry(":memory:")
    registry.create(task_id="coding-2", goal="stop")
    cancelled = registry.cancel("coding-2")
    assert cancelled["state"] == "CANCELLING"
    assert cancelled["current_step_summary"] == "Cancellation requested"


def test_task_center_persists_completed_records_across_registry_instances(tmp_path):
    db_path = tmp_path / "task-center.db"
    first = TaskCenterRegistry(db_path)
    first.create(
        task_id="persistent-1",
        goal="Persist the task result",
        route="coding",
        provider="gemini",
        model="gemini-flash-lite-latest",
    )
    first.update(
        "persistent-1",
        state="COMPLETED",
        current_step_summary="Verification completed",
        result_summary="1 passed",
        changed_files=["bug.py"],
        command="pytest -q",
    )
    first.close()

    second = TaskCenterRegistry(db_path)
    persisted = second.get("persistent-1")

    assert persisted is not None
    assert persisted["state"] == "COMPLETED"
    assert persisted["result_summary"] == "1 passed"
    assert persisted["file_changes"] == ["bug.py"]
    assert persisted["commands"] == ["pytest -q"]
    second.close()


def test_task_center_recovers_interrupted_active_task_as_failed(tmp_path):
    db_path = tmp_path / "task-center-recovery.db"
    first = TaskCenterRegistry(db_path)
    first.create(task_id="active-before-restart", goal="Long task")
    first.update(
        "active-before-restart",
        state="RUNNING",
        current_step_summary="Worker running",
    )
    first.close()

    second = TaskCenterRegistry(db_path)
    recovered = second.get("active-before-restart")

    assert recovered is not None
    assert recovered["state"] == "FAILED"
    assert recovered["subagent_state"] == "INTERRUPTED_BY_GATEWAY_RESTART"
    assert recovered["current_step_summary"] == "Task interrupted by gateway restart"
    assert "Gateway restarted" in recovered["error"]
    second.close()
