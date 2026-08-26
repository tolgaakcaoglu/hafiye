from __future__ import annotations

import json

import hafiye_audit


def test_audit_is_private_redacted_and_jsonlines(monkeypatch, tmp_path):
    monkeypatch.setattr(hafiye_audit, "get_hafiye_state_home", lambda: tmp_path)

    hafiye_audit.record_audit(
        "shell_command",
        command="curl 'https://example.test/?token=secret-value'",
        exit_code=0,
    )

    path = tmp_path / "logs/audit.log"
    entry = json.loads(path.read_text(encoding="utf-8"))
    assert entry["event"] == "shell_command"
    assert entry["exit_code"] == 0
    assert "secret-value" not in path.read_text(encoding="utf-8")
    assert path.stat().st_mode & 0o777 == 0o600
