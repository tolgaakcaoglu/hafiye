"""Integration coverage for the deterministic project workspace tools."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from hermes_state import SessionDB
from tools.project_tools import project_create


def test_project_alias_and_session_context_survive_fresh_process(tmp_path, monkeypatch):
    """A project slug resolves its path after a backend-style process restart."""
    repo_root = Path(__file__).resolve().parents[2]
    hermes_home = tmp_path / "home"
    project_path = tmp_path / "pocket-world"
    project_path.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(hermes_home))

    created = json.loads(project_create("Pocket World", str(project_path)))
    assert created["success"] is True
    assert created["slug"] == "pocket-world"

    db = SessionDB(hermes_home / "state.db")
    db.create_session("p14-session", source="cli")
    db.append_message(
        "p14-session",
        role="user",
        content="Pocket World: en son testleri burada çalıştırıyorduk.",
    )
    db.append_message(
        "p14-session",
        role="assistant",
        content="Pocket World test planı ve son sonuçlar kaydedildi.",
    )
    db.close()

    child = """
import json
from pathlib import Path

from hermes_state import SessionDB
from tools.project_tools import project_switch
from tools.session_search_tool import session_search

switched = json.loads(project_switch("pocket-world"))
assert switched["success"] is True, switched
assert switched["primary_path"] == PROJECT_PATH, switched

db = SessionDB(Path(STATE_DB))
found = json.loads(session_search(query="Pocket World", db=db))
db.close()
assert found["success"] is True and found["count"] >= 1, found
print("P14_PROJECT_MEMORY_E2E_OK")
""".replace("PROJECT_PATH", repr(str(project_path))).replace(
        "STATE_DB", repr(str(hermes_home / "state.db"))
    )

    output = subprocess.check_output(
        [sys.executable, "-c", child],
        cwd=repo_root,
        env={**os.environ, "HERMES_HOME": str(hermes_home), "PYTHONPATH": str(repo_root)},
        text=True,
    )
    assert "P14_PROJECT_MEMORY_E2E_OK" in output
