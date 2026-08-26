import json
import os
from pathlib import Path


def _module(monkeypatch, tmp_path):
    monkeypatch.setenv("HAFIYE_GATEWAY_STATE_DIR", str(tmp_path / "gateway"))
    monkeypatch.setenv("HAFIYE_GATEWAY_PORT", "9234")
    from hermes_cli import persistent_gateway

    return persistent_gateway


def test_token_and_descriptor_are_private_and_stable(monkeypatch, tmp_path):
    gateway = _module(monkeypatch, tmp_path)

    first = gateway.paths()
    token = gateway.ensure_session_token(first)
    descriptor = gateway.connection_descriptor(first)
    second = gateway.ensure_session_token(first)

    assert token == second
    assert len(token) >= 32
    assert descriptor == {
        "schema": 1,
        "service": "hafiye-gateway.service",
        "host": "127.0.0.1",
        "port": 9234,
    }
    assert stat_mode(first.state_dir) == 0o700
    assert stat_mode(first.token_file) == 0o600
    assert stat_mode(first.descriptor_file) == 0o600
    assert json.loads(first.descriptor_file.read_text()) == descriptor


def test_token_rejects_group_or_world_access(monkeypatch, tmp_path):
    gateway = _module(monkeypatch, tmp_path)
    targets = gateway.paths()
    gateway.ensure_session_token(targets)
    targets.token_file.chmod(0o640)

    try:
        gateway.ensure_session_token(targets)
    except RuntimeError as exc:
        assert "unsafe permissions" in str(exc)
    else:
        raise AssertionError("unsafe token permissions were accepted")


def test_systemd_unit_is_loopback_user_service(monkeypatch, tmp_path):
    gateway = _module(monkeypatch, tmp_path)
    monkeypatch.delenv("HERMES_HOME", raising=False)
    unit = gateway.generate_systemd_unit(gateway.paths())

    assert "Description=Hafiye persistent Desktop backend" in unit
    assert "ExecStart=" in unit and "persistent_gateway run --foreground" in unit
    assert "Environment=HERMES_DESKTOP=1" in unit
    assert "Environment=HAFIYE_PERSISTENT_GATEWAY=1" in unit
    assert "HAFIYE_GATEWAY_PORT=9234" in unit
    assert 'Environment="HERMES_HOME=' not in unit
    assert "WantedBy=default.target" in unit
    assert "NoNewPrivileges=true" in unit


def test_systemd_unit_preserves_explicit_hermes_home(monkeypatch, tmp_path):
    gateway = _module(monkeypatch, tmp_path)
    explicit_home = tmp_path / "legacy-hermes-home"
    monkeypatch.setenv("HERMES_HOME", str(explicit_home))

    unit = gateway.generate_systemd_unit(gateway.paths())

    assert f'Environment="HERMES_HOME={explicit_home}"' in unit


def test_systemd_unit_uses_packaged_runner_without_checkout_coupling(monkeypatch, tmp_path):
    gateway = _module(monkeypatch, tmp_path)
    package_root = tmp_path / "package"
    runner = package_root / "bin" / "hafiye-gateway-run"
    runner.parent.mkdir(parents=True)
    runner.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setenv("HAFIYE_PACKAGE_ROOT", str(package_root))

    unit = gateway.generate_systemd_unit(gateway.paths())

    assert f"ExecStart={runner}" in unit
    assert f'Environment="HAFIYE_PACKAGE_ROOT={package_root}"' in unit
    assert "WorkingDirectory=" not in unit
    assert "hermes_cli.persistent_gateway" not in unit


def test_persistent_restart_targets_user_service(monkeypatch):
    from hermes_cli import web_server

    class FakeProcess:
        pid = 1234

        def poll(self):
            return 0

    spawned = []

    def spawn():
        spawned.append(True)
        return FakeProcess()

    monkeypatch.setenv("HAFIYE_PERSISTENT_GATEWAY", "1")
    monkeypatch.setattr(web_server, "_spawn_persistent_gateway_restart", spawn)
    monkeypatch.setattr(web_server, "_ACTION_PROCS", {})
    monkeypatch.setattr(web_server, "_LAST_GATEWAY_RESTART", None)

    process, reused = web_server._spawn_gateway_restart()

    assert process.pid == 1234
    assert reused is False
    assert spawned == [True]
    assert web_server._LAST_GATEWAY_RESTART[2] == (
        "systemctl",
        "--user",
        "restart",
        "hafiye-gateway.service",
    )


def stat_mode(path: Path) -> int:
    return os.stat(path).st_mode & 0o777
