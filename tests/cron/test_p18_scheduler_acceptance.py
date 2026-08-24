"""P18 acceptance: a real local recurring task fires more than once.

This deliberately uses Hermes' supported ``no_agent`` local-script mode so the
acceptance does not depend on a cloud credential or a test-only scheduler stub.
Both ticks go through the real cron store, claim, script runner, execution
ledger, and recurring next-run update.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest


@pytest.fixture
def p18_home(tmp_path, monkeypatch):
    home = tmp_path / ".hermes"
    (home / "scripts").mkdir(parents=True)
    (home / "cron" / "output").mkdir(parents=True)
    monkeypatch.setenv("HERMES_HOME", str(home))

    import cron.jobs as jobs
    import cron.scheduler as scheduler

    monkeypatch.setattr(jobs, "CRON_DIR", home / "cron")
    monkeypatch.setattr(jobs, "JOBS_FILE", home / "cron" / "jobs.json")
    monkeypatch.setattr(jobs, "OUTPUT_DIR", home / "cron" / "output")
    monkeypatch.setattr(scheduler, "_hermes_home", home)
    return home


def test_recurring_local_task_survives_two_real_ticks(p18_home, monkeypatch):
    import cron.executions as executions
    import cron.jobs as jobs
    import cron.scheduler as scheduler

    executions.EXECUTIONS_FILE = p18_home / "cron" / "executions.db"

    script = p18_home / "scripts" / "p18-local-task.py"
    script.write_text("print('p18 local recurring task')\n", encoding="utf-8")

    job = jobs.create_job(
        prompt=None,
        schedule="every 1m",
        script=script.name,
        no_agent=True,
        deliver="local",
        route="default",
        privacy_mode="LOCAL_ONLY",
    )
    due = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    jobs.update_job(job["id"], {"next_run_at": due})

    assert scheduler.tick(verbose=False, sync=True) == 1
    first = executions.latest_execution(job["id"])
    assert first is not None
    assert first["status"] == "completed"

    jobs.update_job(job["id"], {"next_run_at": due})
    assert scheduler.tick(verbose=False, sync=True) == 1
    second = executions.latest_execution(job["id"])
    assert second is not None
    assert second["status"] == "completed"
    assert second["id"] != first["id"]

    persisted = jobs.get_job(job["id"])
    assert persisted["enabled"] is True
    assert persisted["state"] == "scheduled"
    assert persisted["route"] == "default"
    assert persisted["privacy_mode"] == "LOCAL_ONLY"
