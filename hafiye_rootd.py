"""Hafiye's privileged-operation broker.

The normal Hafiye gateway is deliberately a non-root process.  This module is
the small, local-only root boundary required by the Hafiye roadmap: a root
systemd service accepts one length-prefixed JSON request per Unix-socket
connection, authenticates the peer with ``SO_PEERCRED``, validates a strict
operation schema, executes only the named structured operation, and records a
redacted audit event.

The broker is intentionally implemented with the Python standard library so
the system service does not depend on the user's provider configuration or on
optional Hermes packages.  ``RootBrokerClient`` is the client boundary used by
Hafiye code and by the diagnostic CLI.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import os
import pwd
import re
import shutil
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


SERVICE_NAME = "hafiye-rootd"
SERVICE_UNIT = f"{SERVICE_NAME}.service"
DEFAULT_SOCKET_PATH = Path("/run/hafiye/root.sock")
DEFAULT_AUDIT_LOG = Path("/var/log/hafiye/rootd-audit.log")
MAX_FRAME_BYTES = 1 * 1024 * 1024
MAX_REQUEST_BYTES = 256 * 1024
MAX_COMMAND_BYTES = 64 * 1024
MAX_CONTENT_BYTES = 4 * 1024 * 1024
MAX_OUTPUT_BYTES = 4 * 1024 * 1024
DEFAULT_REQUEST_TIMEOUT = 30.0
MAX_REQUEST_TIMEOUT = 180.0
_FRAME_HEADER = struct.Struct("!I")
_SO_PEERCRED = getattr(socket, "SO_PEERCRED", 17)
ESTOP_FILENAME = "ESTOP"
_SAFE_ID = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_SAFE_PACKAGE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9+_.:@-]{0,127}$")
_SAFE_UNIT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.@:-]{0,127}(?:\.service|\.socket|\.target|\.mount|\.timer|\.path)?$")
_SAFE_ENV_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,127}$")
_ALLOWED_OPERATIONS = frozenset(
    {
        "package.install",
        "package.remove",
        "service.start",
        "service.stop",
        "service.restart",
        "file.write_privileged",
        "power.action",
        "root.exec",
    }
)
_POWER_ACTIONS = {
    "shutdown": "poweroff",
    "reboot": "reboot",
    "suspend": "suspend",
    "hibernate": "hibernate",
}
_SENSITIVE_ENV_KEYS = {
    "API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "SUDO_PASSWORD",
}


class RootBrokerError(RuntimeError):
    """A protocol, authorization, validation, or execution error."""

    def __init__(self, message: str, *, code: str = "broker_error") -> None:
        super().__init__(message)
        self.code = code


class _MalformedRequest(RootBrokerError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="malformed_request")


@dataclass(frozen=True)
class RootBrokerPaths:
    socket_path: Path
    audit_log: Path
    unit_path: Path


def _default_socket_path() -> Path:
    return Path(os.environ.get("HAFIYE_ROOTD_SOCKET", str(DEFAULT_SOCKET_PATH)))


def _default_audit_log() -> Path:
    return Path(os.environ.get("HAFIYE_ROOTD_AUDIT_LOG", str(DEFAULT_AUDIT_LOG)))


def _default_estop_path(allowed_uid: int | None = None) -> Path:
    """Resolve the durable ESTOP path shared with the non-root Hafiye process."""
    explicit = os.environ.get("HAFIYE_ESTOP_PATH", "").strip()
    if explicit:
        return Path(explicit).expanduser()
    hermes_home = os.environ.get("HERMES_HOME", "").strip()
    if hermes_home:
        return Path(hermes_home).expanduser() / ESTOP_FILENAME
    if allowed_uid is not None:
        try:
            user_home = Path(pwd.getpwuid(allowed_uid).pw_dir)
        except KeyError:
            user_home = Path.home()
    else:
        user_home = Path.home()
    return user_home / ".local" / "share" / "hafiye" / ESTOP_FILENAME


def paths() -> RootBrokerPaths:
    return RootBrokerPaths(
        socket_path=_default_socket_path(),
        audit_log=_default_audit_log(),
        unit_path=Path("/usr/lib/systemd/system") / SERVICE_UNIT,
    )


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON value is not allowed: {value}")


def _object_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _loads_strict(payload: bytes, *, limit: int = MAX_REQUEST_BYTES) -> Any:
    if len(payload) > limit:
        raise _MalformedRequest("JSON payload exceeds the maximum frame size")
    try:
        return json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_object_no_duplicates,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError) as exc:
        raise _MalformedRequest(f"invalid JSON request: {exc}") from exc


def _send_frame(connection: socket.socket, payload: dict[str, Any]) -> None:
    try:
        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise RootBrokerError(f"cannot encode broker response: {exc}", code="protocol_error") from exc
    if len(encoded) > MAX_FRAME_BYTES:
        raise RootBrokerError("broker response exceeds the maximum frame size", code="protocol_error")
    connection.sendall(_FRAME_HEADER.pack(len(encoded)) + encoded)


def _recv_exact(connection: socket.socket, size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining:
        chunk = connection.recv(remaining)
        if not chunk:
            raise _MalformedRequest("connection closed before the complete frame arrived")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _receive_frame(connection: socket.socket) -> dict[str, Any]:
    header = _recv_exact(connection, _FRAME_HEADER.size)
    (length,) = _FRAME_HEADER.unpack(header)
    if length == 0 or length > MAX_FRAME_BYTES:
        raise _MalformedRequest("invalid request frame length")
    request = _loads_strict(_recv_exact(connection, length))
    if not isinstance(request, dict):
        raise _MalformedRequest("request must be a JSON object")
    if set(request) != {"id", "op", "args"}:
        raise _MalformedRequest("request must contain exactly id, op, and args")
    request_id = request["id"]
    operation = request["op"]
    args = request["args"]
    if not isinstance(request_id, str) or not _SAFE_ID.fullmatch(request_id):
        raise _MalformedRequest("request id must be a short safe string")
    if not isinstance(operation, str) or operation not in _ALLOWED_OPERATIONS:
        raise _MalformedRequest("unsupported broker operation")
    if not isinstance(args, dict):
        raise _MalformedRequest("request args must be an object")
    return {"id": request_id, "op": operation, "args": args}


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _bounded_string(value: Any, *, name: str, limit: int) -> str:
    if not isinstance(value, str):
        raise RootBrokerError(f"{name} must be a string", code="invalid_args")
    if "\x00" in value:
        raise RootBrokerError(f"{name} must not contain NUL", code="invalid_args")
    if len(value.encode("utf-8")) > limit:
        raise RootBrokerError(f"{name} is too large", code="invalid_args")
    return value


def _bounded_timeout(value: Any) -> float:
    if value is None:
        return DEFAULT_REQUEST_TIMEOUT
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RootBrokerError("timeout must be a number", code="invalid_args")
    timeout = float(value)
    if not 0.1 <= timeout <= MAX_REQUEST_TIMEOUT:
        raise RootBrokerError(
            f"timeout must be between 0.1 and {MAX_REQUEST_TIMEOUT:g} seconds",
            code="invalid_args",
        )
    return timeout


def _validate_no_unknown_args(args: dict[str, Any], allowed: set[str]) -> None:
    unknown = sorted(set(args) - allowed)
    if unknown:
        raise RootBrokerError(
            f"unknown argument(s): {', '.join(unknown)}", code="invalid_args"
        )


def _validate_package_names(args: dict[str, Any]) -> list[str]:
    _validate_no_unknown_args(args, {"packages", "timeout"})
    packages = args.get("packages")
    if not isinstance(packages, list) or not packages or len(packages) > 64:
        raise RootBrokerError("packages must be a non-empty list of at most 64 names", code="invalid_args")
    validated: list[str] = []
    for package in packages:
        if not isinstance(package, str) or not _SAFE_PACKAGE.fullmatch(package):
            raise RootBrokerError("package names contain an unsafe value", code="invalid_args")
        validated.append(package)
    _bounded_timeout(args.get("timeout"))
    return validated


def _package_manager() -> str:
    for candidate in ("apt-get", "dnf", "pacman", "zypper"):
        path = shutil.which(candidate)
        if path:
            return path
    raise RootBrokerError("no supported system package manager was found", code="unavailable")


def _package_command(operation: str, packages: list[str]) -> list[str]:
    manager = _package_manager()
    name = Path(manager).name
    if name == "apt-get":
        action = "install" if operation == "package.install" else "remove"
        command = [manager, action, "-y"]
        if action == "install":
            command.append("--no-install-recommends")
        return [*command, *packages]
    if name == "dnf":
        return [manager, "-y", "install" if operation == "package.install" else "remove", *packages]
    if name == "pacman":
        return [manager, "--noconfirm", "-S" if operation == "package.install" else "-R", *packages]
    return [manager, "--non-interactive", "install" if operation == "package.install" else "remove", *packages]


def _validate_unit_args(args: dict[str, Any]) -> str:
    _validate_no_unknown_args(args, {"unit", "timeout"})
    unit = _bounded_string(args.get("unit"), name="unit", limit=128)
    if not _SAFE_UNIT.fullmatch(unit):
        raise RootBrokerError("unit name contains an unsafe value", code="invalid_args")
    _bounded_timeout(args.get("timeout"))
    return unit


def _validate_path(path_value: Any) -> Path:
    raw = _bounded_string(path_value, name="path", limit=4096)
    path = Path(raw)
    if not path.is_absolute():
        raise RootBrokerError("path must be absolute", code="invalid_args")
    return path


def _decode_file_content(args: dict[str, Any]) -> bytes:
    content = args.get("content")
    encoding = args.get("encoding", "utf-8")
    if encoding == "utf-8":
        text = _bounded_string(content, name="content", limit=MAX_CONTENT_BYTES)
        return text.encode("utf-8")
    if encoding != "base64":
        raise RootBrokerError("encoding must be utf-8 or base64", code="invalid_args")
    encoded = _bounded_string(content, name="content", limit=MAX_CONTENT_BYTES * 2)
    try:
        decoded = base64.b64decode(encoded.encode("ascii"), validate=True)
    except (UnicodeEncodeError, binascii.Error) as exc:
        raise RootBrokerError("content is not valid base64", code="invalid_args") from exc
    if len(decoded) > MAX_CONTENT_BYTES:
        raise RootBrokerError("decoded content is too large", code="invalid_args")
    return decoded


def _validate_mode(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 0o777:
        raise RootBrokerError("mode must be an integer between 0 and 0777", code="invalid_args")
    return value


def _write_privileged_file(args: dict[str, Any]) -> dict[str, Any]:
    _validate_no_unknown_args(args, {"path", "content", "encoding", "mode", "create_parents"})
    path = _validate_path(args.get("path"))
    content = _decode_file_content(args)
    mode = _validate_mode(args.get("mode"))
    create_parents = args.get("create_parents", False)
    if not isinstance(create_parents, bool):
        raise RootBrokerError("create_parents must be a boolean", code="invalid_args")
    parent = path.parent
    if create_parents:
        parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    if not parent.is_dir():
        raise RootBrokerError("file parent directory does not exist", code="execution_error")
    try:
        existing = path.lstat()
    except FileNotFoundError:
        existing = None
    if existing is not None and not stat_is_regular(existing.st_mode):
        raise RootBrokerError("refusing to replace a non-regular file", code="invalid_args")
    effective_mode = mode if mode is not None else (existing.st_mode & 0o777 if existing else 0o644)
    temporary_path: str | None = None
    descriptor: int | None = None
    try:
        descriptor, temporary_path = tempfile.mkstemp(prefix=".hafiye-rootd-", dir=parent)
        os.fchmod(descriptor, effective_mode)
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = None
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary_path:
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass
    return {
        "path": str(path),
        "bytes_written": len(content),
        "sha256": _sha256_bytes(content),
        "mode": f"{effective_mode:04o}",
    }


def stat_is_regular(mode: int) -> bool:
    return (mode & 0o170000) == 0o100000


def _validate_power_args(args: dict[str, Any]) -> str:
    _validate_no_unknown_args(args, {"action", "timeout"})
    action = _bounded_string(args.get("action"), name="action", limit=32).lower()
    if action not in _POWER_ACTIONS:
        raise RootBrokerError("unsupported power action", code="invalid_args")
    _bounded_timeout(args.get("timeout"))
    return action


def _validate_root_exec_args(args: dict[str, Any]) -> tuple[list[str], str | None, float, str | None, dict[str, str]]:
    _validate_no_unknown_args(args, {"argv", "command", "cwd", "timeout", "stdin", "env"})
    argv = args.get("argv")
    command = args.get("command")
    if (argv is None) == (command is None):
        raise RootBrokerError("provide exactly one of argv or command", code="invalid_args")
    if argv is not None:
        if not isinstance(argv, list) or not argv or len(argv) > 256:
            raise RootBrokerError("argv must be a non-empty list of at most 256 items", code="invalid_args")
        validated_argv: list[str] = []
        for index, item in enumerate(argv):
            validated_argv.append(_bounded_string(item, name=f"argv[{index}]", limit=MAX_COMMAND_BYTES))
        command_text = None
    else:
        command_text = _bounded_string(command, name="command", limit=MAX_COMMAND_BYTES)
        if not command_text.strip():
            raise RootBrokerError("command must not be empty", code="invalid_args")
        validated_argv = []
    cwd_value = args.get("cwd")
    cwd: str | None = None
    if cwd_value is not None:
        cwd_path = _validate_path(cwd_value)
        if not cwd_path.is_dir():
            raise RootBrokerError("cwd must be an existing directory", code="invalid_args")
        cwd = str(cwd_path)
    timeout = _bounded_timeout(args.get("timeout"))
    stdin_value = args.get("stdin")
    stdin_text = None
    if stdin_value is not None:
        stdin_text = _bounded_string(stdin_value, name="stdin", limit=MAX_CONTENT_BYTES)
    env_value = args.get("env", {})
    if not isinstance(env_value, dict) or len(env_value) > 128:
        raise RootBrokerError("env must be an object with at most 128 entries", code="invalid_args")
    env: dict[str, str] = {}
    for key, value in env_value.items():
        if not isinstance(key, str) or not _SAFE_ENV_KEY.fullmatch(key):
            raise RootBrokerError("env contains an unsafe key", code="invalid_args")
        env[key] = _bounded_string(value, name=f"env[{key}]", limit=4096)
    return validated_argv, command_text, timeout, cwd, env | {}


def _scrubbed_root_environment(overrides: dict[str, str]) -> dict[str, str]:
    environment = {
        key: value
        for key, value in os.environ.items()
        if key not in _SENSITIVE_ENV_KEYS and not key.endswith("_API_KEY")
    }
    environment.setdefault("HOME", "/root")
    environment.setdefault("PATH", "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")
    environment.update(overrides)
    return environment


def _kill_process_group(process: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (OSError, ProcessLookupError):
        try:
            process.kill()
        except OSError:
            pass


def _run_command(
    argv: list[str],
    *,
    shell_command: str | None = None,
    cwd: str | None = None,
    timeout: float = DEFAULT_REQUEST_TIMEOUT,
    stdin_text: str | None = None,
    env_overrides: dict[str, str] | None = None,
) -> dict[str, Any]:
    effective_argv = ["/bin/bash", "-lc", shell_command] if shell_command is not None else argv
    process = subprocess.Popen(
        effective_argv,
        cwd=cwd,
        env=_scrubbed_root_environment(env_overrides or {}),
        stdin=subprocess.PIPE if stdin_text is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(
            input=stdin_text.encode("utf-8") if stdin_text is not None else None,
            timeout=timeout,
        )
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        _kill_process_group(process)
        stdout, stderr = process.communicate()
        timed_out = True
        if exc.stdout:
            stdout = exc.stdout if not stdout else stdout
        if exc.stderr:
            stderr = exc.stderr if not stderr else stderr
    stdout_truncated = len(stdout) > MAX_OUTPUT_BYTES
    stderr_truncated = len(stderr) > MAX_OUTPUT_BYTES
    return {
        "returncode": 124 if timed_out else int(process.returncode or 0),
        "stdout": stdout[:MAX_OUTPUT_BYTES].decode("utf-8", errors="replace"),
        "stderr": stderr[:MAX_OUTPUT_BYTES].decode("utf-8", errors="replace"),
        "timed_out": timed_out,
        "stdout_truncated": stdout_truncated,
        "stderr_truncated": stderr_truncated,
    }


def _dispatch_operation(operation: str, args: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return ``(result, redacted_audit_summary)`` for a validated operation."""
    if operation in {"package.install", "package.remove"}:
        packages = _validate_package_names(args)
        timeout = _bounded_timeout(args.get("timeout"))
        command = _package_command(operation, packages)
        result = _run_command(command, timeout=timeout)
        summary = {"packages": packages, "command_sha256": _sha256_text("\0".join(command))}
        return result, summary

    if operation in {"service.start", "service.stop", "service.restart"}:
        unit = _validate_unit_args(args)
        timeout = _bounded_timeout(args.get("timeout"))
        action = operation.rsplit(".", 1)[1]
        result = _run_command(["/bin/systemctl", action, unit], timeout=timeout)
        return result, {"unit": unit, "action": action}

    if operation == "power.action":
        action = _validate_power_args(args)
        timeout = _bounded_timeout(args.get("timeout"))
        result = _run_command(["/bin/systemctl", _POWER_ACTIONS[action]], timeout=timeout)
        return result, {"action": action}

    if operation == "file.write_privileged":
        result = _write_privileged_file(args)
        return result, {"path": result["path"], "bytes_written": result["bytes_written"], "sha256": result["sha256"]}

    if operation == "root.exec":
        argv, command, cwd, timeout, stdin_text, env = _root_exec_for_dispatch(args)
        result = _run_command(
            argv,
            shell_command=command,
            cwd=cwd,
            timeout=timeout,
            stdin_text=stdin_text,
            env_overrides=env,
        )
        summary: dict[str, Any] = {
            "cwd": cwd,
            "timeout": timeout,
            "command_sha256": _sha256_text(command) if command is not None else None,
            "argv_sha256": _sha256_text("\0".join(argv)) if command is None else None,
            "env_keys": sorted(env),
        }
        return result, summary

    raise RootBrokerError("unsupported broker operation", code="invalid_args")


def _root_exec_for_dispatch(args: dict[str, Any]) -> tuple[list[str], str | None, str | None, float, str | None, dict[str, str]]:
    argv, command, timeout, cwd, env = _validate_root_exec_args(args)
    return argv, command, cwd, timeout, args.get("stdin"), env


def _audit_record(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o750)
    encoded = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o640)
    try:
        os.fchmod(descriptor, 0o640)
        with os.fdopen(descriptor, "ab") as stream:
            descriptor = -1
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _audit_summary_args(operation: str, args: dict[str, Any]) -> dict[str, Any]:
    if operation == "root.exec":
        command = args.get("command")
        argv = args.get("argv")
        return {
            "cwd": args.get("cwd"),
            "command_sha256": _sha256_text(command) if isinstance(command, str) else None,
            "argv_sha256": _sha256_text("\0".join(argv)) if isinstance(argv, list) and all(isinstance(v, str) for v in argv) else None,
            "env_keys": sorted(args.get("env", {}).keys()) if isinstance(args.get("env", {}), dict) else [],
        }
    if operation == "file.write_privileged":
        path = args.get("path")
        content = args.get("content")
        return {
            "path": path if isinstance(path, str) else None,
            "content_sha256": _sha256_text(content) if isinstance(content, str) else None,
            "encoding": args.get("encoding", "utf-8"),
        }
    if operation in {"package.install", "package.remove"}:
        packages = args.get("packages")
        return {"packages": packages if isinstance(packages, list) else []}
    if operation.startswith("service."):
        return {"unit": args.get("unit")}
    return {"action": args.get("action")}


class RootBrokerServer:
    """Threaded one-request-per-connection Unix-socket broker."""

    def __init__(
        self,
        *,
        socket_path: Path | str | None = None,
        allowed_uid: int | None = None,
        audit_log: Path | str | None = None,
        estop_path: Path | str | None = None,
        io_timeout: float = DEFAULT_REQUEST_TIMEOUT,
    ) -> None:
        self.socket_path = Path(socket_path) if socket_path is not None else _default_socket_path()
        self.audit_log = Path(audit_log) if audit_log is not None else _default_audit_log()
        self.io_timeout = float(io_timeout)
        if not 0.1 <= self.io_timeout <= MAX_REQUEST_TIMEOUT:
            raise ValueError("io_timeout is outside the supported range")
        self.allowed_uid = os.getuid() if allowed_uid is None and os.geteuid() != 0 else allowed_uid
        if self.allowed_uid is None or self.allowed_uid < 0:
            raise ValueError("allowed_uid must be configured for a root broker")
        self.estop_path = (
            Path(estop_path) if estop_path is not None else _default_estop_path(self.allowed_uid)
        )
        self._listener: socket.socket | None = None
        self._stop = threading.Event()

    def _estop_engaged(self) -> bool:
        """Fail closed when the durable emergency-stop state is unreadable."""
        try:
            return self.estop_path.exists()
        except OSError:
            return True

    def _peer_credentials(self, connection: socket.socket) -> tuple[int, int, int]:
        try:
            payload = connection.getsockopt(socket.SOL_SOCKET, _SO_PEERCRED, struct.calcsize("3i"))
        except OSError as exc:
            raise RootBrokerError(f"cannot read Unix peer credentials: {exc}", code="peer_auth_error") from exc
        pid, uid, gid = struct.unpack("3i", payload)
        return pid, uid, gid

    def _prepare_socket(self) -> socket.socket:
        if sys.platform != "linux":
            raise RuntimeError("hafiye-rootd requires Linux Unix-socket peer credentials")
        self.socket_path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
        try:
            mode = self.socket_path.stat().st_mode
        except FileNotFoundError:
            pass
        else:
            if not stat_is_socket(mode):
                raise RuntimeError(f"refusing to replace non-socket path: {self.socket_path}")
            self.socket_path.unlink()
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        listener.settimeout(1.0)
        try:
            listener.bind(str(self.socket_path))
            os.chmod(self.socket_path, 0o600)
            if os.geteuid() == 0:
                try:
                    target_gid = pwd.getpwuid(self.allowed_uid).pw_gid
                except KeyError as exc:
                    raise RuntimeError(f"allowed UID {self.allowed_uid} is not a local user") from exc
                os.chown(self.socket_path, self.allowed_uid, target_gid)
            listener.listen(32)
        except Exception:
            listener.close()
            try:
                self.socket_path.unlink()
            except FileNotFoundError:
                pass
            raise
        return listener

    def _audit(self, record: dict[str, Any]) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": SERVICE_NAME,
            **record,
        }
        _audit_record(self.audit_log, record)

    def _handle_connection(self, connection: socket.socket) -> None:
        started = time.monotonic()
        request_id: str | None = None
        operation: str | None = None
        peer_pid = peer_uid = peer_gid = None
        try:
            connection.settimeout(self.io_timeout)
            peer_pid, peer_uid, peer_gid = self._peer_credentials(connection)
            if peer_uid != self.allowed_uid:
                self._audit(
                    {
                        "event": "request",
                        "status": "rejected",
                        "reason": "unauthorized_peer",
                        "peer_pid": peer_pid,
                        "peer_uid": peer_uid,
                        "peer_gid": peer_gid,
                    }
                )
                raise RootBrokerError("unauthorized Unix-socket peer", code="unauthorized_peer")
            request = _receive_frame(connection)
            request_id = request["id"]
            operation = request["op"]
            args = request["args"]
            if self._estop_engaged():
                self._audit(
                    {
                        "event": "request",
                        "status": "rejected",
                        "reason": "emergency_stop",
                        "request_id": request_id,
                        "operation": operation,
                        "peer_pid": peer_pid,
                        "peer_uid": peer_uid,
                    }
                )
                raise RootBrokerError(
                    "privileged operations are paused by emergency stop",
                    code="emergency_stop",
                )
            self._audit(
                {
                    "event": "request",
                    "status": "accepted",
                    "request_id": request_id,
                    "operation": operation,
                    "peer_pid": peer_pid,
                    "peer_uid": peer_uid,
                    "args": _audit_summary_args(operation, args),
                }
            )
            result, summary = _dispatch_operation(operation, args)
            elapsed = int((time.monotonic() - started) * 1000)
            self._audit(
                {
                    "event": "result",
                    "status": "success" if result.get("returncode", 0) == 0 else "command_failed",
                    "request_id": request_id,
                    "operation": operation,
                    "peer_uid": peer_uid,
                    "duration_ms": elapsed,
                    "result": summary,
                }
            )
            _send_frame(connection, {"id": request_id, "ok": True, "result": result})
        except RootBrokerError as exc:
            try:
                self._audit(
                    {
                        "event": "result",
                        "status": "rejected",
                        "request_id": request_id,
                        "operation": operation,
                        "peer_pid": peer_pid,
                        "peer_uid": peer_uid,
                        "error_code": exc.code,
                        "error": str(exc),
                    }
                )
            except OSError:
                pass
            self._send_error(connection, request_id, exc)
        except (OSError, subprocess.SubprocessError, ValueError) as exc:
            error = RootBrokerError(str(exc), code="execution_error")
            try:
                self._audit(
                    {
                        "event": "result",
                        "status": "error",
                        "request_id": request_id,
                        "operation": operation,
                        "peer_pid": peer_pid,
                        "peer_uid": peer_uid,
                        "error_code": error.code,
                        "error": str(error),
                    }
                )
            except OSError:
                pass
            self._send_error(connection, request_id, error)
        except Exception as exc:  # noqa: BLE001 - broker must return a bounded protocol error
            error = RootBrokerError(str(exc), code="internal_error")
            try:
                self._audit(
                    {
                        "event": "result",
                        "status": "error",
                        "request_id": request_id,
                        "operation": operation,
                        "peer_pid": peer_pid,
                        "peer_uid": peer_uid,
                        "error_code": error.code,
                        "error": str(error),
                    }
                )
            except OSError:
                pass
            self._send_error(connection, request_id, error)
        finally:
            try:
                self._audit(
                    {
                        "event": "connection",
                        "status": "closed",
                        "request_id": request_id,
                        "operation": operation,
                        "peer_pid": peer_pid,
                        "peer_uid": peer_uid,
                        "duration_ms": int((time.monotonic() - started) * 1000),
                    }
                )
            except OSError:
                pass
            connection.close()

    def _send_error(self, connection: socket.socket, request_id: str | None, error: RootBrokerError) -> None:
        try:
            _send_frame(
                connection,
                {
                    "id": request_id,
                    "ok": False,
                    "error": {"code": error.code, "message": str(error)},
                },
            )
        except (OSError, RootBrokerError):
            pass

    def serve_forever(self) -> None:
        self.audit_log.parent.mkdir(parents=True, exist_ok=True, mode=0o750)
        self._listener = self._prepare_socket()
        try:
            while not self._stop.is_set():
                try:
                    connection, _ = self._listener.accept()
                except socket.timeout:
                    continue
                except OSError:
                    if self._stop.is_set():
                        break
                    raise
                thread = threading.Thread(
                    target=self._handle_connection,
                    args=(connection,),
                    name="hafiye-rootd-request",
                    daemon=True,
                )
                thread.start()
        finally:
            self.close()

    def close(self) -> None:
        self._stop.set()
        if self._listener is not None:
            self._listener.close()
            self._listener = None
        try:
            self.socket_path.unlink()
        except FileNotFoundError:
            pass


def stat_is_socket(mode: int) -> bool:
    return (mode & 0o170000) == 0o140000


class RootBrokerClient:
    """Strict client for the local Hafiye root broker."""

    def __init__(
        self,
        socket_path: Path | str | None = None,
        *,
        timeout: float = DEFAULT_REQUEST_TIMEOUT,
    ) -> None:
        self.socket_path = Path(socket_path) if socket_path is not None else _default_socket_path()
        self.timeout = _bounded_timeout(timeout)

    def request(self, operation: str, args: dict[str, Any] | None = None, *, timeout: float | None = None) -> dict[str, Any]:
        if operation not in _ALLOWED_OPERATIONS:
            raise RootBrokerError("unsupported broker operation", code="invalid_args")
        request = {"id": uuid.uuid4().hex, "op": operation, "args": args or {}}
        encoded = json.dumps(request, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
        if len(encoded) > MAX_REQUEST_BYTES:
            raise RootBrokerError("request exceeds the maximum frame size", code="invalid_args")
        effective_timeout = self.timeout if timeout is None else _bounded_timeout(timeout)
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(effective_timeout)
            try:
                connection.connect(str(self.socket_path))
                connection.sendall(_FRAME_HEADER.pack(len(encoded)) + encoded)
                response = _receive_response(connection)
            except FileNotFoundError as exc:
                raise RootBrokerError(
                    f"hafiye-rootd socket is unavailable: {self.socket_path}", code="unavailable"
                ) from exc
            except ConnectionRefusedError as exc:
                raise RootBrokerError("hafiye-rootd refused the connection", code="unavailable") from exc
            except TimeoutError as exc:
                raise RootBrokerError("hafiye-rootd request timed out", code="timeout") from exc
        if response.get("id") != request["id"]:
            raise RootBrokerError("broker response id did not match request", code="protocol_error")
        if not response.get("ok"):
            error = response.get("error")
            try:
                from hafiye_audit import record_audit

                record_audit(
                    "root_rpc",
                    operation=operation,
                    status="rejected",
                    error_code=error.get("code") if isinstance(error, dict) else "broker_error",
                )
            except Exception:
                pass
            if isinstance(error, dict):
                raise RootBrokerError(str(error.get("message", "broker request failed")), code=str(error.get("code", "broker_error")))
            raise RootBrokerError("broker request failed", code="broker_error")
        result = response.get("result")
        if not isinstance(result, dict):
            raise RootBrokerError("broker result must be an object", code="protocol_error")
        try:
            from hafiye_audit import record_audit

            record_audit(
                "root_rpc",
                operation=operation,
                status="ok",
                command=(args or {}).get("command") if operation == "root.exec" else None,
            )
        except Exception:
            pass
        return result

    def exec(self, command: str, **kwargs: Any) -> dict[str, Any]:
        return self.request("root.exec", {"command": command, **kwargs})


def _receive_response(connection: socket.socket) -> dict[str, Any]:
    header = _recv_exact(connection, _FRAME_HEADER.size)
    (length,) = _FRAME_HEADER.unpack(header)
    if length == 0 or length > MAX_FRAME_BYTES:
        raise RootBrokerError("invalid broker response frame length", code="protocol_error")
    payload = _loads_strict(_recv_exact(connection, length), limit=MAX_FRAME_BYTES)
    if not isinstance(payload, dict) or set(payload) != {"id", "ok", "result"} and set(payload) != {"id", "ok", "error"}:
        raise RootBrokerError("malformed broker response", code="protocol_error")
    return payload


def _current_uid() -> int:
    return os.getuid()


def _systemctl(*arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(["systemctl", *arguments], text=True, capture_output=True, check=False)
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RootBrokerError(f"systemctl {' '.join(arguments)} failed: {detail}", code="service_error")
    return result


def generate_systemd_unit(
    *,
    python_executable: str | Path = sys.executable,
    rootd_script: str | Path | None = None,
    socket_path: str | Path = DEFAULT_SOCKET_PATH,
    audit_log: str | Path = DEFAULT_AUDIT_LOG,
    allowed_uid: int,
    estop_path: str | Path | None = None,
) -> str:
    """Generate the root service unit without embedding a secret."""
    if allowed_uid < 0:
        raise ValueError("allowed_uid must be non-negative")
    script = Path(__file__).resolve() if rootd_script is None else Path(rootd_script)
    effective_estop_path = (
        Path(estop_path) if estop_path is not None else _default_estop_path(allowed_uid)
    )
    return (
        "[Unit]\n"
        "Description=Hafiye privileged operation broker\n"
        "After=local-fs.target\n\n"
        "[Service]\n"
        "Type=simple\n"
        "User=root\n"
        f"ExecStart={shlex_quote(str(python_executable))} {shlex_quote(str(script))} --serve"
        f" --socket {shlex_quote(str(socket_path))}"
        f" --audit-log {shlex_quote(str(audit_log))}"
        f" --estop-path {shlex_quote(str(effective_estop_path))}"
        f" --allowed-uid {allowed_uid}\n"
        "RuntimeDirectory=hafiye\n"
        "RuntimeDirectoryMode=0755\n"
        "Restart=on-failure\n"
        "RestartSec=2\n"
        "TimeoutStartSec=15\n"
        "TimeoutStopSec=15\n"
        "UMask=0077\n"
        "StandardOutput=journal\n"
        "StandardError=journal\n\n"
        "[Install]\n"
        "WantedBy=multi-user.target\n"
    )


def shlex_quote(value: str) -> str:
    """Small local quote helper to keep this module's imports stdlib-only."""
    import shlex

    return shlex.quote(value)


def _run_sudo_install(arguments: list[str]) -> int:
    sudo = shutil.which("sudo")
    if not sudo:
        raise RootBrokerError("sudo is required to install hafiye-rootd.service", code="unavailable")
    # Use the absolute module file when crossing the sudo boundary. A Debian
    # package intentionally keeps the backend on PYTHONPATH rather than
    # installing it as a system distribution; sudo may scrub that PYTHONPATH,
    # so ``python -m hafiye_rootd`` would fail even though the caller can
    # import the module. The source-checkout path remains equivalent.
    result = subprocess.run(
        [sudo, sys.executable, str(Path(__file__).resolve()), *arguments],
        check=False,
    )
    return result.returncode


def install_system_service(
    *, allowed_uid: int | None = None, estop_path: str | Path | None = None
) -> int:
    """Install and start the root unit, prompting through normal sudo once."""
    uid = _current_uid() if allowed_uid is None else int(allowed_uid)
    if os.geteuid() != 0:
        effective_estop_path = (
            Path(estop_path) if estop_path is not None else _default_estop_path(uid)
        )
        return _run_sudo_install(
            [
                "--install-system",
                "--allowed-uid",
                str(uid),
                "--estop-path",
                str(effective_estop_path),
            ]
        )
    if sys.platform != "linux":
        raise RootBrokerError("hafiye-rootd.service requires Linux", code="unsupported_platform")
    service_paths = paths()
    service_paths.unit_path.parent.mkdir(parents=True, exist_ok=True)
    service_paths.audit_log.parent.mkdir(parents=True, exist_ok=True, mode=0o750)
    service_paths.audit_log.touch(mode=0o640, exist_ok=True)
    service_paths.audit_log.chmod(0o640)
    unit = generate_systemd_unit(
        python_executable=sys.executable,
        rootd_script=Path(__file__).resolve(),
        socket_path=service_paths.socket_path,
        audit_log=service_paths.audit_log,
        allowed_uid=uid,
        estop_path=estop_path,
    )
    temporary = service_paths.unit_path.with_suffix(f".service.{os.getpid()}.tmp")
    temporary.write_text(unit, encoding="utf-8")
    temporary.chmod(0o644)
    os.replace(temporary, service_paths.unit_path)
    _systemctl("daemon-reload")
    _systemctl("enable", SERVICE_UNIT)
    # ``enable --now`` starts an inactive unit but deliberately leaves an
    # already-active process untouched. Always restart after replacing the
    # unit so a package/source provenance change takes effect immediately.
    _systemctl("restart", SERVICE_UNIT)
    return 0


def uninstall_system_service() -> int:
    if os.geteuid() != 0:
        return _run_sudo_install(["--uninstall-system"])
    _systemctl("disable", "--now", SERVICE_UNIT, check=False)
    service_paths = paths()
    service_paths.unit_path.unlink(missing_ok=True)
    _systemctl("daemon-reload", check=False)
    return 0


def root_broker_command(args: argparse.Namespace) -> int:
    command = getattr(args, "root_command", None) or "status"
    if command == "install":
        return install_system_service(
            estop_path=getattr(args, "estop_path", None),
        )
    if command == "uninstall":
        return uninstall_system_service()
    if command in {"start", "stop", "restart", "status"}:
        if command == "status":
            result = _systemctl("status", SERVICE_UNIT, "--no-pager", check=False)
        else:
            result = _systemctl(command, SERVICE_UNIT, check=False)
        output = (result.stdout or result.stderr).strip()
        if output:
            print(output)
        return result.returncode
    if command == "exec":
        command_text = " ".join(getattr(args, "root_exec_command", []))
        if not command_text:
            raise RootBrokerError("root exec requires a command", code="invalid_args")
        result = RootBrokerClient().exec(command_text)
        sys.stdout.write(result.get("stdout", ""))
        if result.get("stderr"):
            sys.stderr.write(result["stderr"])
        return int(result.get("returncode", 1))
    raise RootBrokerError(f"unknown root command: {command}", code="invalid_args")


def build_root_parser(parent: argparse._SubParsersAction, *, cmd_root: Callable[[argparse.Namespace], int]) -> None:
    root = parent.add_parser(
        "root",
        help="Manage the Hafiye privileged root broker",
        description=(
            "Manage hafiye-rootd.service. The normal Hafiye process remains "
            "non-root; privileged operations cross the local Unix socket."
        ),
    )
    subparsers = root.add_subparsers(dest="root_command")
    for action, help_text in (
        ("install", "Install and enable hafiye-rootd.service (may prompt for sudo)"),
        ("uninstall", "Disable and remove hafiye-rootd.service (may prompt for sudo)"),
        ("start", "Start hafiye-rootd.service"),
        ("stop", "Stop hafiye-rootd.service"),
        ("restart", "Restart hafiye-rootd.service"),
        ("status", "Show hafiye-rootd.service status"),
    ):
        subparsers.add_parser(action, help=help_text)
    execute = subparsers.add_parser("exec", help="Execute a command through rootd")
    execute.add_argument("root_exec_command", nargs=argparse.REMAINDER, help="Command and arguments")
    root.set_defaults(func=cmd_root)


def _build_standalone_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Hafiye's root broker")
    parser.add_argument("--serve", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--install-system", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--uninstall-system", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--socket", default=str(_default_socket_path()), help=argparse.SUPPRESS)
    parser.add_argument("--audit-log", default=str(_default_audit_log()), help=argparse.SUPPRESS)
    parser.add_argument("--estop-path", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--allowed-uid", type=int, default=None, help=argparse.SUPPRESS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_standalone_parser().parse_args(argv)
    if args.serve:
        allowed_uid = args.allowed_uid
        if allowed_uid is None:
            raise SystemExit("--allowed-uid is required for --serve")
        server = RootBrokerServer(
            socket_path=args.socket,
            audit_log=args.audit_log,
            allowed_uid=allowed_uid,
            estop_path=args.estop_path,
        )
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.close()
        return 0
    if args.install_system:
        return install_system_service(
            allowed_uid=args.allowed_uid,
            estop_path=args.estop_path,
        )
    if args.uninstall_system:
        return uninstall_system_service()
    _build_standalone_parser().error("one of --serve, --install-system, or --uninstall-system is required")
    return 2


__all__ = [
    "DEFAULT_AUDIT_LOG",
    "DEFAULT_SOCKET_PATH",
    "RootBrokerClient",
    "RootBrokerError",
    "RootBrokerPaths",
    "RootBrokerServer",
    "SERVICE_NAME",
    "SERVICE_UNIT",
    "build_root_parser",
    "generate_systemd_unit",
    "install_system_service",
    "main",
    "paths",
    "root_broker_command",
    "uninstall_system_service",
]


if __name__ == "__main__":
    raise SystemExit(main())
