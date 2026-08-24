"""Hafiye model-routing and privacy policy.

This module is deliberately independent of the provider clients.  Entrypoints
resolve a task into a route here, then pass the resulting provider/model to the
existing Hermes runtime resolver.  The agent also uses the policy at its
boundary as a defense-in-depth check, so a caller cannot bypass LOCAL_ONLY or
OFFLINE by constructing an agent directly.
"""

from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import re
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse


ROUTE_SLOTS: tuple[str, ...] = (
    "default",
    "fast",
    "reasoning",
    "coding",
    "vision",
    "long_context",
    "memory_aux",
    "compression_aux",
)

PRIVACY_MODES: tuple[str, ...] = ("NORMAL", "LOCAL_ONLY", "OFFLINE")

# Tools whose normal operation can make a network request or delegate one to a
# remote service.  This is intentionally a deny-list at the product boundary:
# terminal remains full host access by architecture, but Hafiye-managed web,
# browser, generation, MCP-install and remote-code surfaces are unavailable in
# OFFLINE mode.
OFFLINE_NETWORK_TOOLS: frozenset[str] = frozenset(
    {
        "web_search",
        "web_extract",
        "x_search",
        "browser_navigate",
        "browser_snapshot",
        "browser_click",
        "browser_type",
        "browser_scroll",
        "browser_back",
        "browser_press",
        "browser_download",
        "browser_native",
        "browser_get_images",
        "browser_vision",
        "browser_console",
        "browser_cdp",
        "browser_dialog",
        "browser_exec",
        "image_generate",
        "video_analyze",
        "video_generate",
        "xai_video_edit",
        "xai_video_extend",
        "text_to_speech",
        "bfl_flux3_text_to_video",
        "bfl_flux3_image_to_video",
        "bfl_flux3_keyframes_to_video",
        "bfl_flux3_video_continuation",
        "bfl_flux3_get_result",
        "bfl_flux3_prompting_guide",
        "setup_mcp",
        "execute_code",
        "tool_search",
        "tool_describe",
        "tool_call",
        "send_message",
        "message_agent",
        "delegate_task",
        "coding_delegate",
        "react_to_message",
        "drive_preview",
        "discord",
        "discord_admin",
        "vision_analyze",
    }
)

_LOCAL_PROVIDER_NAMES = frozenset(
    {
        "local",
        "llama.cpp",
        "llamacpp",
        "llama_cpp",
        "ollama",
        "vllm",
        "lmstudio",
        "lm-studio",
        "koboldcpp",
        "jan",
    }
)

_PRIVACY_RANK = {"NORMAL": 0, "LOCAL_ONLY": 1, "OFFLINE": 2}

_SLOT_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("fast", ("fast", "quick", "hızlı", "hizli", "çabuk", "cabuk")),
    ("reasoning", ("reasoning", "reason", "akıl yürüt", "akil yurut", "düşün", "dusun")),
    ("coding", ("coding", "code", "kodlama", "kod yaz", "programla")),
    ("vision", ("vision", "görsel", "gorsel", "resim", "image")),
    ("long_context", ("long context", "long-context", "uzun bağlam", "uzun baglam")),
    ("memory_aux", ("memory aux", "memory-aux", "bellek yardımcı", "bellek yardimci")),
    ("compression_aux", ("compression aux", "compression-aux", "sıkıştırma", "sikistirma")),
)


class HafiyePolicyError(RuntimeError):
    """Raised when a requested route violates the active Hafiye policy."""


@dataclass(frozen=True)
class TaskOverride:
    """Task-scoped hints extracted from the natural-language prompt."""

    mode: str | None = None
    slot: str | None = None
    provider: str | None = None
    kind: str | None = None


@dataclass(frozen=True)
class HafiyeRoute:
    """Resolved route metadata passed from an entrypoint to an AIAgent."""

    slot: str
    provider: str
    model: str
    privacy_mode: str
    source: str
    task_override: str | None = None
    fallback_providers: tuple[dict[str, Any], ...] = ()
    locality_policy: str = "NORMAL"

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-safe route description for diagnostics/UI state."""
        return {
            "slot": self.slot,
            "provider": self.provider,
            "model": self.model,
            "privacy_mode": self.privacy_mode,
            "source": self.source,
            "task_override": self.task_override,
            "fallback_providers": [dict(entry) for entry in self.fallback_providers],
            "locality_policy": self.locality_policy,
        }


def normalize_privacy_mode(value: Any) -> str:
    """Normalize a config or request mode; invalid values fail closed to NORMAL."""
    normalized = str(value or "NORMAL").strip().upper().replace("-", "_").replace(" ", "_")
    return normalized if normalized in PRIVACY_MODES else "NORMAL"


def _strongest_privacy_mode(*values: Any) -> str:
    """Combine policy layers without allowing a weaker layer to relax one."""
    normalized = [normalize_privacy_mode(value) for value in values]
    return max(normalized, key=lambda value: _PRIVACY_RANK[value])


def extract_task_override(text: Any) -> TaskOverride:
    """Extract an explicit, task-scoped routing/privacy hint from *text*.

    The parser only recognizes explicit words/phrases and never rewrites the
    persisted conversation.  It is therefore safe to run before constructing a
    turn-scoped agent without changing the conversation's cached prefix.
    """
    value = str(text or "").strip().casefold()
    if not value:
        return TaskOverride()

    mode: str | None = None
    if re.search(r"\b(?:offline|off-line|çevrimdışı|cevrimdisi)\b", value):
        mode = "OFFLINE"
    elif re.search(r"\b(?:local_only|local only|yerel|sadece yerel|sadece lokal)\b", value):
        mode = "LOCAL_ONLY"
    elif re.search(r"\b(?:normal mode|normal mod|normal)\b", value):
        mode = "NORMAL"

    provider: str | None = None
    kind: str | None = None
    if re.search(r"\b(?:gemini|google ai|google gemini)\b", value):
        provider = "gemini"
        kind = "gemini"
    elif re.search(r"\b(?:remote|cloud|uzak|bulut|bulutta)\b", value):
        kind = "remote"

    slot: str | None = None
    for candidate, patterns in _SLOT_PATTERNS:
        if any(pattern in value for pattern in patterns):
            slot = candidate
            break

    # A local/yerel task is a task-scoped privacy restriction.  It does not
    # mutate the installation-wide privacy mode; the next task uses config.
    if mode is None and re.search(r"\b(?:local|yerel|lokal)\b", value):
        mode = "LOCAL_ONLY"

    return TaskOverride(mode=mode, slot=slot, provider=provider, kind=kind)


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _section(config: Mapping[str, Any] | None) -> Mapping[str, Any]:
    raw = config.get("hafiye") if isinstance(config, Mapping) else None
    return raw if isinstance(raw, Mapping) else {}


def _route_entry(config: Mapping[str, Any] | None, slot: str) -> Mapping[str, Any]:
    section = _section(config)
    routes = section.get("route_slots")
    if not isinstance(routes, Mapping):
        return {}
    raw = routes.get(slot)
    return raw if isinstance(raw, Mapping) else {}


def _task_entry(config: Mapping[str, Any] | None, kind: str) -> Mapping[str, Any]:
    section = _section(config)
    overrides = section.get("task_overrides")
    if not isinstance(overrides, Mapping):
        return {}
    raw = overrides.get(kind)
    return raw if isinstance(raw, Mapping) else {}


def _fallback_entries(config: Mapping[str, Any] | None, entry: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    raw = entry.get("fallback_providers")
    if raw is None:
        raw = _section(config).get("fallback_providers")
    if not isinstance(raw, list):
        return ()
    result: list[dict[str, Any]] = []
    for candidate in raw:
        if not isinstance(candidate, Mapping):
            continue
        provider = _clean(candidate.get("provider"))
        model = _clean(candidate.get("model"))
        if provider and model:
            result.append(dict(candidate))
    return tuple(result)


def resolve_hafiye_route(
    config: Mapping[str, Any] | None,
    *,
    provider: Any = "",
    model: Any = "",
    base_url: Any = "",
    slot: str = "default",
    task_text: Any = "",
) -> HafiyeRoute:
    """Resolve the configured slot plus a task-scoped natural-language hint."""
    section = _section(config)
    configured_model = config.get("model") if isinstance(config, Mapping) else None
    configured_base_url = (
        configured_model.get("base_url")
        if isinstance(configured_model, Mapping)
        else ""
    )
    effective_base_url = _clean(base_url) or _clean(configured_base_url)
    configured_mode = normalize_privacy_mode(section.get("privacy_mode", "NORMAL"))
    override = extract_task_override(task_text)
    selected_slot = override.slot or slot or "default"
    if selected_slot not in ROUTE_SLOTS:
        selected_slot = "default"

    entry = _route_entry(config, selected_slot)
    selected_provider = _clean(entry.get("provider")) or _clean(provider)
    selected_model = _clean(entry.get("model")) or _clean(model)
    source = "config" if entry.get("provider") or entry.get("model") else "runtime"
    slot_locality_policy = normalize_privacy_mode(entry.get("locality_policy", "NORMAL"))
    task_kind = override.kind
    policy_base_url = effective_base_url

    if task_kind in {"gemini", "remote"}:
        task_entry = _task_entry(config, task_kind)
        if task_kind == "gemini":
            selected_provider = _clean(task_entry.get("provider")) or "gemini"
            selected_model = _clean(task_entry.get("model"))
            policy_base_url = _clean(task_entry.get("base_url"))
            if not selected_model:
                try:
                    from hermes_cli.models import get_default_model_for_provider

                    selected_model = get_default_model_for_provider(selected_provider)
                except Exception:
                    selected_model = "gemini-3.1-pro-preview"
        else:
            selected_provider = _clean(task_entry.get("provider")) or selected_provider
            selected_model = _clean(task_entry.get("model")) or selected_model
            policy_base_url = _clean(task_entry.get("base_url"))
            if not selected_provider or is_local_runtime(selected_provider, policy_base_url):
                raise HafiyePolicyError(
                    "Bu görev uzak/remote olarak istendi ancak aktif route yerel. "
                    "hafiye.task_overrides.remote.provider/model yapılandırılmalı."
                )
        source = f"task:{task_kind}"

    selected_mode = _strongest_privacy_mode(
        configured_mode,
        slot_locality_policy,
        override.mode,
    )
    if override.provider and task_kind not in {"gemini", "remote"}:
        selected_provider = override.provider
        source = "task:provider"

    if selected_mode in {"LOCAL_ONLY", "OFFLINE"}:
        # An empty provider/base URL means the existing Hermes resolver still
        # has to choose the runtime. Let the agent boundary validate it after
        # that resolution instead of rejecting a valid local config early.
        if (selected_provider or policy_base_url) and not is_local_runtime(
            selected_provider, policy_base_url
        ):
            raise HafiyePolicyError(
                f"Hafiye {selected_mode} policy forbids remote/cloud inference. "
                "Select a local llama.cpp-compatible endpoint first."
            )

    fallback = _fallback_entries(config, entry)
    if task_kind in {"gemini", "remote"}:
        fallback = _fallback_entries(config, _task_entry(config, task_kind)) or fallback

    return HafiyeRoute(
        slot=selected_slot,
        provider=selected_provider,
        model=selected_model,
        privacy_mode=selected_mode,
        source=source,
        task_override=task_kind or ("mode:" + override.mode if override.mode else None),
        fallback_providers=fallback,
        locality_policy=slot_locality_policy,
    )


def _hostname(base_url: Any) -> str:
    try:
        return (urlparse(_clean(base_url)).hostname or "").lower().rstrip(".")
    except Exception:
        return ""


def is_local_runtime(provider: Any, base_url: Any = "") -> bool:
    """Return whether a provider/base URL is local to this host."""
    provider_name = _clean(provider).casefold().replace("-", "_")
    host = _hostname(base_url)
    if host in {"localhost", "localhost.localdomain", "127.0.0.1", "::1", "0.0.0.0"}:
        return True
    try:
        if host and ipaddress.ip_address(host).is_loopback:
            return True
    except ValueError:
        pass

    # Provider aliases are useful when the endpoint is implicit (for example
    # a managed local runtime that has not published its loopback URL yet),
    # but an explicitly remote URL must win over a local-looking name. This
    # prevents LOCAL_ONLY/OFFLINE from being bypassed by naming an HTTPS cloud
    # endpoint "ollama" or "llama.cpp".
    if provider_name in {name.replace("-", "_") for name in _LOCAL_PROVIDER_NAMES}:
        return not host
    return False


def enforce_runtime_policy(
    privacy_mode: Any,
    *,
    provider: Any,
    base_url: Any,
    model: Any = "",
) -> None:
    """Fail closed when a resolved runtime violates LOCAL_ONLY/OFFLINE."""
    mode = normalize_privacy_mode(privacy_mode)
    if mode in {"LOCAL_ONLY", "OFFLINE"} and not is_local_runtime(provider, base_url):
        raise HafiyePolicyError(
            f"Hafiye {mode} policy blocked provider '{_clean(provider) or 'unknown'}' "
            f"at '{_clean(base_url) or 'unknown'}'."
        )


def filter_fallback_chain(entries: Iterable[Mapping[str, Any]], privacy_mode: Any) -> list[dict[str, Any]]:
    """Keep only fallback entries legal for the active privacy mode."""
    mode = normalize_privacy_mode(privacy_mode)
    result: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        if mode in {"LOCAL_ONLY", "OFFLINE"} and not is_local_runtime(
            entry.get("provider"), entry.get("base_url", "")
        ):
            continue
        result.append(dict(entry))
    return result


def filter_tool_definitions(tools: Iterable[Mapping[str, Any]], privacy_mode: Any) -> list[dict[str, Any]]:
    """Remove Hafiye-managed network tools from an OFFLINE schema."""
    mode = normalize_privacy_mode(privacy_mode)
    definitions = [dict(tool) for tool in tools]
    if mode != "OFFLINE":
        return definitions

    result: list[dict[str, Any]] = []
    for definition in definitions:
        function = definition.get("function") if isinstance(definition, Mapping) else None
        name = _clean(function.get("name") if isinstance(function, Mapping) else "")
        if is_offline_blocked_tool(name):
            continue
        result.append(definition)
    return result


def is_offline_blocked_tool(function_name: Any) -> bool:
    """Return whether a tool is forbidden by the OFFLINE product boundary."""
    name = _clean(function_name).casefold()
    return (
        name in OFFLINE_NETWORK_TOOLS
        or name.startswith("browser_")
        or name.startswith("mcp_")
        or name.startswith("mcp-")
        or name.startswith("ha_")
        or name.startswith("yb_")
        or name.startswith("feishu_")
        or name.startswith("kanban_")
    )


def offline_tool_block_message(function_name: Any) -> str | None:
    """Return the user/model-visible denial message for an OFFLINE tool."""
    if not is_offline_blocked_tool(function_name):
        return None
    return (
        f"Tool '{_clean(function_name)}' is unavailable in Hafiye OFFLINE mode. "
        "Use a local filesystem/process/desktop capability or switch privacy mode."
    )
