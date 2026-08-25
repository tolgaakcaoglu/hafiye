"""Hafiye host execution policy.

The policy is deliberately a small boundary around Hermes' existing host
tools.  It does not create a second terminal or filesystem implementation;
it classifies the calls that already reach those tools and lets the existing
Hermes approval surfaces handle confirmation when required.
"""

from __future__ import annotations

import ast
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
_PRIVILEGE_ESCALATION_BINARIES = frozenset(
    {"sudo", "sudoedit", "su", "pkexec", "doas", "runuser"}
)
_SHELL_TOKEN_PUNCTUATION = ";|&()<>$"
_SHELL_WRAPPERS = frozenset(
    {"command", "env", "exec", "nice", "nohup", "setsid", "stdbuf", "time", "timeout", "xargs"}
)
_SHELL_INTERPRETERS = frozenset({"bash", "dash", "fish", "ksh", "sh", "zsh"})
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
    requires_root_broker: bool = False

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


def _shell_tokens(command: str) -> list[str] | None:
    """Tokenize enough shell syntax to inspect wrapped command words.

    This is deliberately not a shell parser and is never used to execute a
    command.  Quoting is handled by ``shlex``; punctuation is kept as tokens
    so a chained command cannot hide an escalation binary after the first
    command word.
    """
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=_SHELL_TOKEN_PUNCTUATION)
        lexer.whitespace_split = True
        return list(lexer)
    except ValueError:
        return None


def _without_assignments(tokens: list[str]) -> list[str]:
    remaining = list(tokens)
    while remaining and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", remaining[0]):
        remaining.pop(0)
    return remaining


def _wrapped_command(tokens: list[str], executable: str) -> list[str]:
    """Return the likely child command after a common shell wrapper."""
    remaining = list(tokens[1:])
    if executable == "env":
        while remaining:
            if remaining[0] == "--":
                remaining.pop(0)
                break
            if remaining[0].startswith("-"):
                remaining.pop(0)
                continue
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", remaining[0]):
                remaining.pop(0)
                continue
            break
        return remaining
    if executable == "timeout":
        while remaining and remaining[0].startswith("-"):
            remaining.pop(0)
        if remaining:
            remaining.pop(0)  # duration
        return remaining
    if executable == "nice":
        if remaining and remaining[0] in {"-n", "--adjustment"}:
            remaining = remaining[2:]
        return remaining
    if executable == "stdbuf":
        while remaining and remaining[0].startswith("-"):
            remaining.pop(0)
        return remaining
    if executable in {"command", "exec", "nohup", "setsid", "time"}:
        while remaining and remaining[0].startswith("-"):
            remaining.pop(0)
        if remaining and remaining[0] == "--":
            remaining.pop(0)
        return remaining
    if executable == "xargs":
        while remaining and remaining[0].startswith("-"):
            remaining.pop(0)
        return remaining
    return remaining


def _contains_privilege_escalation_tokens(tokens: list[str], *, depth: int = 0) -> bool:
    if not tokens or depth > 8:
        return False

    # A shell separator starts a new command word.  Parentheses and command
    # substitution punctuation are treated as boundaries as well, while
    # quoted punctuation remains part of one shlex token.
    separators = {";", "&&", "||", "|", "&", "(", ")", "$", "<", ">", ">>", "<<"}
    segments: list[list[str]] = []
    segment: list[str] = []
    for token in tokens:
        if token in separators:
            segments.append(segment)
            segment = []
        else:
            segment.append(token)
    segments.append(segment)

    for segment in segments:
        segment = _without_assignments(segment)
        if not segment:
            continue
        executable = segment[0].rsplit("/", 1)[-1].lower()
        if executable in _PRIVILEGE_ESCALATION_BINARIES:
            return True

        if executable in _SHELL_INTERPRETERS:
            for index, token in enumerate(segment[1:], start=1):
                if token == "--":
                    continue
                is_command_flag = token in {"-c", "--command"}
                if not is_command_flag and token.startswith("-") and not token.startswith("--"):
                    is_command_flag = "c" in token[1:]
                if is_command_flag and index + 1 < len(segment):
                    nested = _shell_tokens(segment[index + 1])
                    if nested is None:
                        return bool(re.search(r"(?:^|[^A-Za-z0-9_])(?:sudo|sudoedit|su|pkexec|doas|runuser)(?:$|[^A-Za-z0-9_])", segment[index + 1], re.IGNORECASE))
                    if _contains_privilege_escalation_tokens(nested, depth=depth + 1):
                        return True
                    break
            continue

        if executable in _SHELL_WRAPPERS and _contains_privilege_escalation_tokens(
            _wrapped_command(segment, executable), depth=depth + 1
        ):
            return True
    return False


def contains_privilege_escalation(command: Any) -> bool:
    """Return whether a shell command visibly invokes an escalation binary.

    Detection is token- and wrapper-aware rather than a string-prefix check.
    It intentionally ignores ordinary arguments such as ``echo 'sudo'`` while
    recognizing absolute paths, assignments, command wrappers, quoted
    executables, shell ``-c`` payloads, and command chaining.
    """
    if not isinstance(command, str) or not command.strip():
        return False
    tokens = _shell_tokens(command)
    if tokens is None:
        return bool(re.search(
            r"(?:^|[^A-Za-z0-9_])(?:sudo|sudoedit|su|pkexec|doas|runuser)(?:$|[^A-Za-z0-9_])",
            command,
            re.IGNORECASE,
        ))
    return _contains_privilege_escalation_tokens(tokens)


def contains_obvious_python_privilege_escalation(code: Any) -> bool:
    """Detect direct subprocess/os command launches of escalation binaries."""
    if not isinstance(code, str) or not code.strip():
        return False
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return bool(re.search(
            r"(?:subprocess|os)\.[A-Za-z_]+\s*\([^\n]*(?:sudo|sudoedit|pkexec|doas|runuser|(?:^|\W)su(?:\W|$))",
            code,
            re.IGNORECASE,
        ))

    process_call_names = {
        "os.execv", "os.execve", "os.execl", "os.execlp", "os.execlpe",
        "os.execle", "os.system", "os.popen", "subprocess.call",
        "subprocess.check_call", "subprocess.check_output", "subprocess.Popen",
        "subprocess.run",
    }

    def call_name(node: ast.Call) -> str:
        parts: list[str] = []
        current: ast.AST = node.func
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))

    def literal_text(node: ast.AST) -> str | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, (ast.List, ast.Tuple)):
            values: list[str] = []
            for item in node.elts:
                if not isinstance(item, ast.Constant) or not isinstance(item.value, str):
                    return None
                values.append(item.value)
            return " ".join(values)
        return None

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or call_name(node) not in process_call_names:
            continue
        if node.args and contains_privilege_escalation(literal_text(node.args[0])):
            return True
    return False


def _is_privileged_command(command: Any) -> bool:
    if not isinstance(command, str):
        return False
    if contains_privilege_escalation(command):
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
    requires_root_broker = tool_name == "terminal" and operation == "privileged"
    root_broker_reason = (
        "Direct privileged execution through the normal terminal is blocked; "
        "use the hafiye-rootd broker boundary."
    )

    if requires_root_broker and policy == "FULL_AUTONOMOUS":
        return ExecutionDecision(
            policy=policy,
            tool_name=tool_name,
            operation=operation,
            allowed=False,
            requires_confirmation=False,
            reason=root_broker_reason,
            confirmation_command=_confirmation_command(tool_name, call_args),
            requires_root_broker=True,
        )

    if operation == "read":
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
            requires_root_broker=requires_root_broker,
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
        requires_root_broker=requires_root_broker,
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
