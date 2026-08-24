"""Persistent Hafiye Desktop backend service.

Hermes has an upstream messaging gateway service.  Hafiye also needs a
long-lived local JSON-RPC/WebSocket backend for Desktop, so closing the
Electron shell does not terminate the agent core or an active task.  This
module owns only that second lifecycle and deliberately leaves
``hermes-gateway.service`` untouched.

The service is user-scoped, loopback-only, and authenticated with a local
owner-readable session token.  Provider credentials are not stored here; the
token only authenticates Desktop to the local backend process.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shlex
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from hermes_constants import get_hafiye_state_home, get_hermes_home_override
from tools.environments.local import build_subprocess_env


SERVICE_NAME = "hafiye-gateway"
SERVICE_UNIT = f"{SERVICE_NAME}.service"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 9120
TOKEN_BYTES = 32
TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]{32,128}$")


@dataclass(frozen=True)
class PersistentGatewayPaths:
    state_dir: Path
    token_file: Path
    descriptor_file: Path
    unit_file: Path


def _state_dir() -> Path:
    override = os.environ.get("HAFIYE_GATEWAY_STATE_DIR", "").strip()
    if override:
        return Path(override).expanduser()
    return get_hafiye_state_home() / "gateway"


def paths() -> PersistentGatewayPaths:
    state_dir = _state_dir()
    return PersistentGatewayPaths(
        state_dir=state_dir,
        token_file=state_dir / "session-token",
        descriptor_file=state_dir / "connection.json",
        unit_file=Path.home() / ".config" / "systemd" / "user" / SERVICE_UNIT,
    )


def _port() -> int:
    raw = os.environ.get("HAFIYE_GATEWAY_PORT", "").strip()
    if not raw:
        return DEFAULT_PORT
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError("HAFIYE_GATEWAY_PORT must be an integer") from exc
    if not 1024 <= value <= 65535:
        raise ValueError("HAFIYE_GATEWAY_PORT must be between 1024 and 65535")
    return value


def _ensure_private_directory(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        directory.chmod(0o700)
    except OSError:
        pass


def _read_private_token(token_file: Path) -> str | None:
    try:
        file_stat = token_file.stat()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise RuntimeError(f"Cannot inspect persistent gateway token: {exc}") from exc

    current_uid = getattr(os, "getuid", lambda: None)()
    if not stat.S_ISREG(file_stat.st_mode) or (
        current_uid is not None and file_stat.st_uid != current_uid
    ):
        raise RuntimeError("Persistent gateway token is not a regular file owned by this user")
    if file_stat.st_mode & 0o077:
        raise RuntimeError("Persistent gateway token has unsafe permissions; expected mode 0600")

    token = token_file.read_text(encoding="utf-8").strip()
    if not TOKEN_PATTERN.fullmatch(token):
        raise RuntimeError("Persistent gateway token has an invalid format")
    return token


def _write_private_file(path: Path, contents: str) -> None:
    _ensure_private_directory(path.parent)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            fd = -1
            stream.write(contents)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        try:
            path.chmod(0o600)
        except OSError:
            pass
    finally:
        if fd >= 0:
            os.close(fd)
        try:
            Path(temporary).unlink(missing_ok=True)
        except OSError:
            pass


def ensure_session_token(targets: PersistentGatewayPaths | None = None) -> str:
    targets = targets or paths()
    existing = _read_private_token(targets.token_file)
    if existing:
        return existing
    token = secrets.token_urlsafe(TOKEN_BYTES)
    _write_private_file(targets.token_file, f"{token}\n")
    return token


def write_connection_descriptor(targets: PersistentGatewayPaths | None = None) -> dict[str, object]:
    targets = targets or paths()
    descriptor = {
        "schema": 1,
        "service": SERVICE_UNIT,
        "host": DEFAULT_HOST,
        "port": _port(),
    }
    _write_private_file(
        targets.descriptor_file,
        json.dumps(descriptor, sort_keys=True, separators=(",", ":")) + "\n",
    )
    return descriptor


def read_connection_descriptor(targets: PersistentGatewayPaths | None = None) -> dict[str, object] | None:
    targets = targets or paths()
    try:
        payload = json.loads(targets.descriptor_file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Cannot read persistent gateway descriptor: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Persistent gateway descriptor must be a JSON object")
    if payload.get("service") != SERVICE_UNIT or payload.get("host") != DEFAULT_HOST:
        raise RuntimeError("Persistent gateway descriptor has an unexpected service or host")
    try:
        port = int(payload["port"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError("Persistent gateway descriptor has an invalid port") from exc
    if not 1024 <= port <= 65535:
        raise RuntimeError("Persistent gateway descriptor port is out of range")
    return {**payload, "port": port}


def connection_descriptor(targets: PersistentGatewayPaths | None = None) -> dict[str, object]:
    targets = targets or paths()
    descriptor = read_connection_descriptor(targets) or write_connection_descriptor(targets)
    # Keep the descriptor aligned with a changed internal port setting.
    if int(descriptor["port"]) != _port():
        descriptor = write_connection_descriptor(targets)
    return descriptor


def _unit_environment_value(value: str | Path) -> str:
    # systemd Environment= accepts quoted values.  We do not place the token
    # itself in the unit, only paths and the non-secret port.
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


def generate_systemd_unit(targets: PersistentGatewayPaths | None = None) -> str:
    targets = targets or paths()
    repo_root = Path(__file__).resolve().parents[1]
    # Keep the normal installation on the XDG-compatible Hafiye roots.  An
    # explicit HERMES_HOME is still propagated for legacy/profile-scoped
    # installs, where upstream's single-root semantics are intentional.
    explicit_home = os.environ.get("HERMES_HOME", "").strip() or get_hermes_home_override()
    hermes_home_line = (
        f'Environment="HERMES_HOME={_unit_environment_value(explicit_home)}"\n'
        if explicit_home
        else ""
    )
    # Do not resolve a venv's interpreter symlink.  uv-created venvs commonly
    # point `.venv/bin/python` at a shared interpreter; resolving it removes
    # the venv prefix and makes systemd skip the venv site-packages.
    python = Path(sys.executable)
    exec_start = " ".join(
        (
            shlex.quote(str(python)),
            "-m",
            "hermes_cli.persistent_gateway",
            "run",
            "--foreground",
        )
    )
    unit = (
        "[Unit]\n"
        "Description=Hafiye persistent Desktop backend\n"
        "After=graphical-session.target\n"
        "PartOf=graphical-session.target\n\n"
        "[Service]\n"
        "Type=simple\n"
        f"WorkingDirectory={shlex.quote(str(repo_root))}\n"
        f"ExecStart={exec_start}\n"
    )
    unit += hermes_home_line
    unit += (
        f'Environment="HAFIYE_GATEWAY_STATE_DIR={_unit_environment_value(targets.state_dir)}"\n'
        f'Environment="HAFIYE_GATEWAY_PORT={_port()}"\n'
        "Environment=HERMES_DESKTOP=1\n"
        "Environment=HAFIYE_PERSISTENT_GATEWAY=1\n"
        "Restart=always\n"
        "RestartSec=2\n"
        "TimeoutStopSec=15\n"
        "NoNewPrivileges=true\n\n"
        "[Install]\n"
        "WantedBy=default.target\n"
    )
    return unit


def _require_linux() -> None:
    if sys.platform != "linux":
        raise RuntimeError("hafiye-gateway.service is currently supported on Linux only")


def _systemctl(*arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    _require_linux()
    try:
        result = subprocess.run(
            ["systemctl", "--user", *arguments],
            check=False,
            text=True,
            capture_output=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("systemctl was not found") from exc
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"systemctl --user {' '.join(arguments)} failed: {detail}")
    return result


def install_service(*, start_now: bool = True, enable: bool = True) -> PersistentGatewayPaths:
    _require_linux()
    targets = paths()
    ensure_session_token(targets)
    write_connection_descriptor(targets)
    targets.unit_file.parent.mkdir(parents=True, exist_ok=True)
    unit = generate_systemd_unit(targets)
    temporary = targets.unit_file.with_suffix(f".service.{os.getpid()}.tmp")
    temporary.write_text(unit, encoding="utf-8")
    try:
        temporary.chmod(0o644)
        os.replace(temporary, targets.unit_file)
    finally:
        temporary.unlink(missing_ok=True)
    _systemctl("daemon-reload")
    if enable:
        _systemctl("enable", SERVICE_UNIT)
    if start_now:
        _systemctl("restart" if _service_exists_and_active() else "start", SERVICE_UNIT)
    return targets


def _service_exists_and_active() -> bool:
    result = _systemctl("is-active", SERVICE_UNIT, check=False)
    return result.returncode == 0 and result.stdout.strip() == "active"


def service_action(action: str, *, start_now: bool = True, enable: bool = True) -> int:
    if action == "install":
        targets = install_service(start_now=start_now, enable=enable)
        print(f"Installed {SERVICE_UNIT}: {targets.unit_file}")
        print(f"Endpoint: http://{DEFAULT_HOST}:{_port()}")
        return 0
    if action == "start":
        targets = paths()
        ensure_session_token(targets)
        write_connection_descriptor(targets)
        _systemctl("start", SERVICE_UNIT)
        print(f"Started {SERVICE_UNIT}")
        return 0
    if action == "stop":
        _systemctl("stop", SERVICE_UNIT)
        print(f"Stopped {SERVICE_UNIT}")
        return 0
    if action == "restart":
        targets = paths()
        ensure_session_token(targets)
        write_connection_descriptor(targets)
        _systemctl("restart", SERVICE_UNIT)
        print(f"Restarted {SERVICE_UNIT}")
        return 0
    if action == "status":
        result = _systemctl("status", SERVICE_UNIT, "--no-pager", check=False)
        output = (result.stdout or result.stderr).strip()
        if output:
            print(output)
        return 0 if result.returncode == 0 else 3
    if action == "uninstall":
        _systemctl("disable", SERVICE_UNIT, check=False)
        _systemctl("stop", SERVICE_UNIT, check=False)
        _systemctl("daemon-reload", check=False)
        targets = paths()
        targets.unit_file.unlink(missing_ok=True)
        print(f"Removed {SERVICE_UNIT}")
        return 0
    raise ValueError(f"Unknown persistent gateway action: {action}")


def run_foreground() -> None:
    """Replace this wrapper with the long-lived headless backend."""
    targets = paths()
    token = ensure_session_token(targets)
    write_connection_descriptor(targets)
    environment = build_subprocess_env(
        scrub_secrets=False,
        inherit_profile_home=False,
        extra={
            "HERMES_DASHBOARD_SESSION_TOKEN": token,
            "HERMES_DESKTOP": "1",
            "HAFIYE_PERSISTENT_GATEWAY": "1",
        },
    )
    argv = [
        sys.executable,
        "-m",
        "hermes_cli.main",
        "serve",
        "--host",
        DEFAULT_HOST,
        "--port",
        str(_port()),
    ]
    os.execvpe(sys.executable, argv, environment)


def persistent_gateway_command(args: argparse.Namespace) -> int:
    action = getattr(args, "gateway_service_command", None) or "status"
    if action == "run":
        run_foreground()
        return 0
    return service_action(
        action,
        start_now=not getattr(args, "no_start_now", False),
        enable=not getattr(args, "no_enable", False),
    )


def build_service_parser(parent: argparse._SubParsersAction) -> None:
    service = parent.add_parser(
        "service",
        help="Manage the persistent Hafiye Desktop backend service",
        description=(
            "Manage hafiye-gateway.service, the user-scoped persistent JSON-RPC "
            "backend used by Hafiye Desktop. This is separate from the upstream "
            "messaging gateway service."
        ),
    )
    subparsers = service.add_subparsers(dest="gateway_service_command")
    for action, help_text in (
        ("install", "Install and enable the persistent backend service"),
        ("start", "Start the persistent backend service"),
        ("stop", "Stop the persistent backend service"),
        ("restart", "Restart the persistent backend service"),
        ("status", "Show persistent backend service status"),
        ("uninstall", "Disable and remove the persistent backend service"),
    ):
        subparsers.add_parser(action, help=help_text)
    install = subparsers.choices["install"]
    install.add_argument("--no-start-now", action="store_true", help="Install without starting the service")
    install.add_argument("--no-enable", action="store_true", help="Install without enabling at login")
    start = subparsers.choices["start"]
    start.add_argument("--no-start-now", action="store_true", help=argparse.SUPPRESS)
    subparsers.add_parser("run", help=argparse.SUPPRESS).set_defaults(gateway_service_command="run")


__all__ = [
    "DEFAULT_HOST",
    "DEFAULT_PORT",
    "SERVICE_NAME",
    "SERVICE_UNIT",
    "PersistentGatewayPaths",
    "build_service_parser",
    "connection_descriptor",
    "generate_systemd_unit",
    "paths",
    "persistent_gateway_command",
    "read_connection_descriptor",
    "run_foreground",
    "service_action",
]


def _build_standalone_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Hafiye's persistent Desktop backend")
    subparsers = parser.add_subparsers(dest="gateway_service_command", required=True)
    for action, help_text in (
        ("install", "Install and enable the persistent backend service"),
        ("start", "Start the persistent backend service"),
        ("stop", "Stop the persistent backend service"),
        ("restart", "Restart the persistent backend service"),
        ("status", "Show persistent backend service status"),
        ("uninstall", "Disable and remove the persistent backend service"),
    ):
        subparsers.add_parser(action, help=help_text)
    install = subparsers.choices["install"]
    install.add_argument("--no-start-now", action="store_true")
    install.add_argument("--no-enable", action="store_true")
    run = subparsers.add_parser("run", help=argparse.SUPPRESS)
    run.add_argument("--foreground", action="store_true", help=argparse.SUPPRESS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_standalone_parser().parse_args(argv)
    return persistent_gateway_command(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError) as exc:
        print(f"hafiye-gateway: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
