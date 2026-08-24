from __future__ import annotations

import json
import os
import socket
import struct
import threading
import time

import pytest

from hafiye_rootd import (
    MAX_FRAME_BYTES,
    RootBrokerClient,
    RootBrokerError,
    RootBrokerServer,
    _FRAME_HEADER,
    _receive_response,
    generate_systemd_unit,
)


def _start_server(tmp_path, *, allowed_uid: int | None = None):
    socket_path = tmp_path / "run" / "root.sock"
    audit_log = tmp_path / "log" / "rootd.jsonl"
    server = RootBrokerServer(
        socket_path=socket_path,
        allowed_uid=os.getuid() if allowed_uid is None else allowed_uid,
        audit_log=audit_log,
        io_timeout=2,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    deadline = time.monotonic() + 2
    while not socket_path.exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    assert socket_path.exists()
    return server, thread, socket_path, audit_log


def _stop_server(server: RootBrokerServer, thread: threading.Thread) -> None:
    server.close()
    thread.join(timeout=2)


def _raw_request(socket_path, request: bytes):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(2)
        connection.connect(str(socket_path))
        connection.sendall(_FRAME_HEADER.pack(len(request)) + request)
        return _receive_response(connection)


def test_root_exec_uses_strict_client_and_audits_without_command_text(tmp_path):
    server, thread, socket_path, audit_log = _start_server(tmp_path)
    try:
        result = RootBrokerClient(socket_path, timeout=2).exec(
            "printf HAFIYE_ROOTD_OK"
        )
        assert result["returncode"] == 0
        assert result["stdout"] == "HAFIYE_ROOTD_OK"
        records = [json.loads(line) for line in audit_log.read_text().splitlines()]
        assert any(record.get("status") == "accepted" for record in records)
        assert any(record.get("status") == "success" for record in records)
        assert all("printf HAFIYE_ROOTD_OK" not in line for line in audit_log.read_text().splitlines())
    finally:
        _stop_server(server, thread)


def test_file_write_privileged_supports_base64_and_reports_digest(tmp_path):
    server, thread, socket_path, _ = _start_server(tmp_path)
    target = tmp_path / "etc" / "hafiye-test.conf"
    try:
        result = RootBrokerClient(socket_path, timeout=2).request(
            "file.write_privileged",
            {
                "path": str(target),
                "content": "SEFGSVlFX1JPT1REX0ZJTEU=",
                "encoding": "base64",
                "create_parents": True,
                "mode": 0o640,
            },
        )
        assert result["bytes_written"] == len(b"HAFIYE_ROOTD_FILE")
        assert target.read_bytes() == b"HAFIYE_ROOTD_FILE"
        assert target.stat().st_mode & 0o777 == 0o640
        assert result["sha256"]
    finally:
        _stop_server(server, thread)


def test_malformed_duplicate_key_request_is_rejected(tmp_path):
    server, thread, socket_path, _ = _start_server(tmp_path)
    try:
        response = _raw_request(
            socket_path,
            b'{"id":"x","op":"root.exec","op":"root.exec","args":{}}',
        )
        assert response["ok"] is False
        assert response["error"]["code"] == "malformed_request"
    finally:
        _stop_server(server, thread)


def test_unauthorized_peer_is_rejected_before_dispatch(tmp_path):
    alternate_uid = 65534 if os.geteuid() == 0 else os.getuid() + 1
    server, thread, socket_path, _ = _start_server(tmp_path, allowed_uid=alternate_uid)
    try:
        response = _raw_request(
            socket_path,
            json.dumps({"id": "x", "op": "root.exec", "args": {"command": "id"}}).encode(),
        )
        assert response["ok"] is False
        assert response["error"]["code"] == "unauthorized_peer"
    finally:
        _stop_server(server, thread)


def test_unknown_args_and_oversized_frame_fail_closed(tmp_path):
    server, thread, socket_path, _ = _start_server(tmp_path)
    try:
        with pytest.raises(RootBrokerError, match="unknown argument"):
            RootBrokerClient(socket_path, timeout=2).request(
                "root.exec", {"command": "true", "unexpected": True}
            )
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(2)
            connection.connect(str(socket_path))
            connection.sendall(_FRAME_HEADER.pack(MAX_FRAME_BYTES + 1))
            response = _receive_response(connection)
            assert response["ok"] is False
            assert response["error"]["code"] == "malformed_request"
    finally:
        _stop_server(server, thread)


def test_systemd_unit_is_root_only_and_socket_based():
    unit = generate_systemd_unit(
        python_executable="/opt/hafiye/.venv/bin/python",
        socket_path="/run/hafiye/root.sock",
        audit_log="/var/log/hafiye/rootd-audit.log",
        allowed_uid=1000,
    )
    assert "User=root" in unit
    assert "--allowed-uid 1000" in unit
    assert "hafiye_rootd.py --serve" in unit
    assert "--socket /run/hafiye/root.sock" in unit
    assert "--audit-log /var/log/hafiye/rootd-audit.log" in unit
    assert "ListenStream=" not in unit
