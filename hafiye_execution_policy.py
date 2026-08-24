"""Hafiye host execution policy.

The policy is deliberately a small boundary around Hermes' existing host
tools.  It does not create a second terminal or filesystem implementation;
it classifies the calls that already reach those tools and lets the existing
Hermes approval surfaces handle confirmation when required.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
import hashlib
import json
import re
import shlex
from typing import Any, Iterator, Mapping


EXECUTION_POLICIES: tuple[str, ...] = (
    "FULL_AUTONOMOUS",
    "PRIVILEGED_CONFIRM",
    "WRITE_CONFIRM",
    "READ_ONLY",
)
DEFAULT_EXECUTION_POLICY = "FULL_AUTONOMOUS"

_READ_TOOLS = frozenset({"read_file", "search_files"})
_PROCESS_READ_ACTIONS = frozenset({"list", "poll", "log", "wait"})
_PROCESS_MUTATING_ACTIONS = frozenset({"kill", "write", "submit", "close"})

# This is intentionally conservative.  A command is read-only only when it
# is a single shell command with a known non-mutating executable.  Unknown
# commands, shell composition, redirection, and command substitution require
# WRITE_CONFIRM (or are blocked by READ_ONLY).
_READ_ONLY_COMMANDS = frozenset(
    {
        "basename",
        "date",
        "df",
        "dirname",
        "du",
        "file",
        "find",
        "git",
        "grep",
        "head",
        "hostname",
        "id",
        "ls",
        "lsattr",
        "namei",
        "pwd",
        "readlink",
        "realpath",
        "rg",
        "sed",
        "stat",
        "systemctl",
        "tail",
        "test",
        "tree",
        "true",
        "false",
        "type",
        "uname",
        "uptime",
        "wc",
        "which",
        "whoami",
    }
)
_READ_ONLY_GIT_SUBCOMMANDS = frozenset(
    {
        "branch",
        "describe",
        "diff",
        "log",
        "ls-files",
        "remote",
        "rev-parse",
        "show",
        "status",
        "tag",
    }
)
_SHELL_MUTATION_MARKERS = re.compile(r"(?:[;&|]|>>?|<<?|`|\$\(|\n|\r)")
_PRIVILEGED_COMMAND = re.compile(
    r"(?:^|\s|[;&|])(?:[\w./-]+/)?(?:sudo|sudoedit|doas|pkexec|su|runuser)(?:\s|$)",
    re.IGNORECASE,
)
_PRIVILEGED_EXECUTABLES = frozenset(
    {
        "apt",
        "apt-get",
        "chmod",
        "chown",
        "dnf",
        "groupadd",
        "groupdel",
        "insmod",
        "modprobe",
        "mount",
        "pacman",
        "passwd",
        "rmmod",
        "service",
        "setfacl",
        "snap",
        "systemctl",
        "umount",
        "useradd",
        "userdel",
        "usermod",
        "visudo",
        "yum",
        "zypper",
    }
)
_READ_ONLY_SYSTEMCTL_ACTIONS = frozenset(
    {"cat", "is-active", "is-enabled", "list-dependencies", "list-unit-files", "list-units", "show", "status"}
)

_policy_approval_grant: ContextVar[int] = ContextVar(
    "hafiye_policy_approval_grant", default=0
)


@dataclass(frozen=True)
class ExecutionDecision:
    """Classification and enforcement decision for one host-tool call."""

    policy: str
    tool_name: str
    operation: str
    allowed: bool
    requires_confirmation: bool
    reason: str = ""
    confirmation_key: str = ""
    confirmation_command: str = ""

    @property
    def warning(self) -> tuple[str, str] | None:
        if not self.requires_confirmation:
            return None
        return (self.confirmation_key, self.reason)


def normalize_execution_policy(value: Any) -> str:
    """Normalize config input and fail closed to the installation default."""
    normalized = str(value or DEFAULT_EXECUTION_POLICY).strip().upper()
    normalized = normalized.replace("-", "_").replace(" ", "_")
    return normalized if normalized in EXECUTION_POLICIES else DEFAULT_EXECUTION_POLICY


def resolve_execution_policy(config: Mapping[str, Any] | None = None) -> str:
    """Read the live Hafiye policy from config without caching a stale value."""
    if config is None:
        try:
            from hermes_cli.config import load_config_readonly

            config = load_config_readonly()
        except Exception:
            config = {}
    section = config.get("hafiye") if isinstance(config, Mapping) else None
    value = section.get("execution_policy") if isinstance(section, Mapping) else None
    return normalize_execution_policy(value)


def _is_read_only_shell_command(command: Any) -> bool:
    if not isinstance(command, str):
        return False
    text = command.strip()
    if not text or _SHELL_MUTATION_MARKERS.search(text):
        return False
    try:
        tokens = shlex.split(text, posix=True)
    except ValueError:
        return False
    if not tokens:
        return False

    # Environment assignment and the common command wrappers do not change
    # the classification of the wrapped command.
    while tokens and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", tokens[0]):
        tokens.pop(0)
    while tokens and tokens[0] in {"command", "env", "time", "timeout"}:
        tokens.pop(0)
        if not tokens:
            return False
        if tokens[0].startswith("-"):
            tokens.pop(0)
    if not tokens:
        return False

    executable = tokens[0].rsplit("/", 1)[-1]
    if executable not in _READ_ONLY_COMMANDS:
        return False
    if executable == "sed" and any(
        token == "--in-place" or token == "-i" or token.startswith("-i")
        for token in tokens[1:]
    ):
        return False
    if executable == "find" and any(
        token in {"-delete", "-exec", "-execdir", "-ok", "-okdir"}
        or token.startswith("-exec")
        for token in tokens[1:]
    ):
        return False
    if executable == "git":
        try:
            subcommand = next(token for token in tokens[1:] if not token.startswith("-"))
        except StopIteration:
            return False
        if subcommand not in _READ_ONLY_GIT_SUBCOMMANDS:
            return False
        if subcommand in {"branch", "tag"} and any(
            token in {"-a", "-A", "-c", "-C", "-d", "-D", "-f", "-m", "-M", "-s"}
            for token in tokens[1:]
        ):
            return False
        if subcommand == "remote":
            remote_actions = {
                token for token in tokens[tokens.index(subcommand) + 1:]
                if not token.startswith("-")
            }
            if remote_actions and not remote_actions.issubset({"get-url", "show"}):
                return False
        if any(token in {"-o", "--output"} or token.startswith("--output=") for token in tokens[1:]):
            return False
    if executable == "systemctl":
        try:
            action = next(token for token in tokens[1:] if not token.startswith("-"))
        except StopIteration:
            return False
        if action not in _READ_ONLY_SYSTEMCTL_ACTIONS:
            return False
    return True


def _is_privileged_command(command: Any) -> bool:
    if not isinstance(command, str):
        return False
    if _PRIVILEGED_COMMAND.search(command):
        return True
    if _SHELL_MUTATION_MARKERS.search(command):
        return False
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        return False
    if not tokens:
        return False
    executable = tokens[0].rsplit("/", 1)[-1]
    if executable not in _PRIVILEGED_EXECUTABLES:
        return False
    if executable in {"systemctl", "service"}:
        try:
            action = next(token for token in tokens[1:] if not token.startswith("-"))
        except StopIteration:
            return True
        return action not in _READ_ONLY_SYSTEMCTL_ACTIONS
    return True


def _operation_for_call(tool_name: str, args: Mapping[str, Any]) -> str | None:
    if tool_name in _READ_TOOLS:
        return "read"
    if tool_name in {"write_file", "patch"}:
        return "write"
    if tool_name == "execute_code":
        # Arbitrary Python can spawn processes, write files, and invoke sudo;
        # it is therefore treated as privileged for the stricter policy.
        return "privileged"
    if tool_name == "process":
        action = str(args.get("action") or "").strip().lower()
        if action in _PROCESS_READ_ACTIONS:
            return "read"
        if action in _PROCESS_MUTATING_ACTIONS:
            return "write"
        return "write"
    if tool_name == "terminal":
        command = args.get("command")
        if _is_privileged_command(command):
            return "privileged"
        if bool(args.get("background")):
            return "write"
        return "read" if _is_read_only_shell_command(command) else "write"
    return None


def _confirmation_key(policy: str, tool_name: str, operation: str, args: Mapping[str, Any]) -> str:
    # Keep approval persistence keys stable for the same operation while not
    # putting file contents, scripts, or commands into config/state files.
    material = json.dumps(dict(args), sort_keys=True, default=str, ensure_ascii=False)
    digest = hashlib.sha256(material.encode("utf-8", errors="replace")).hexdigest()[:16]
    return f"hafiye-policy:{policy}:{operation}:{tool_name}:{digest}"


def _confirmation_command(tool_name: str, args: Mapping[str, Any]) -> str:
    if tool_name == "terminal":
        return str(args.get("command") or "terminal command")
    if tool_name == "write_file":
        return f"write_file path={args.get('path', '')}"
    if tool_name == "patch":
        return f"patch path={args.get('path', '')}"
    if tool_name == "process":
        return f"process action={args.get('action', '')} session_id={args.get('session_id', '')}"
    if tool_name == "execute_code":
        return "execute_code (script contents hidden)"
    return tool_name


def evaluate_tool_call(
    tool_name: str,
    args: Mapping[str, Any] | None = None,
    *,
    config: Mapping[str, Any] | None = None,
) -> ExecutionDecision | None:
    """Evaluate a host-tool call; return ``None`` for unrelated tools."""
    call_args = args if isinstance(args, Mapping) else {}
    operation = _operation_for_call(tool_name, call_args)
    if operation is None:
        return None

    policy = resolve_execution_policy(config)
    if policy == "FULL_AUTONOMOUS" or operation == "read":
        return ExecutionDecision(
            policy=policy,
            tool_name=tool_name,
            operation=operation,
            allowed=True,
            requires_confirmation=False,
        )

    if policy == "READ_ONLY":
        return ExecutionDecision(
            policy=policy,
            tool_name=tool_name,
            operation=operation,
            allowed=False,
            requires_confirmation=False,
            reason=(
                f"Hafiye execution policy READ_ONLY blocks {tool_name} "
                f"because it is a {operation} operation."
            ),
        )

    requires_confirmation = policy == "WRITE_CONFIRM" or (
        policy == "PRIVILEGED_CONFIRM" and operation == "privileged"
    )
    if not requires_confirmation:
        return ExecutionDecision(
            policy=policy,
            tool_name=tool_name,
            operation=operation,
            allowed=True,
            requires_confirmation=False,
        )

    reason = (
        f"Hafiye execution policy {policy} requires confirmation for "
        f"{operation} operation {tool_name}."
    )
    return ExecutionDecision(
        policy=policy,
        tool_name=tool_name,
        operation=operation,
        allowed=False,
        requires_confirmation=True,
        reason=reason,
        confirmation_key=_confirmation_key(policy, tool_name, operation, call_args),
        confirmation_command=_confirmation_command(tool_name, call_args),
    )


@contextmanager
def policy_approval_scope(granted: bool) -> Iterator[None]:
    """Pass one policy approval to a direct tool handler without new args."""
    current = _policy_approval_grant.get()
    token = _policy_approval_grant.set(current + 1 if granted else current)
    try:
        yield
    finally:
        _policy_approval_grant.reset(token)


def consume_policy_approval_grant() -> bool:
    """Consume one approval granted by the model-tool dispatch boundary."""
    current = _policy_approval_grant.get()
    if current <= 0:
        return False
    _policy_approval_grant.set(current - 1)
    return True
