"""Hafiye product CLI surface.

The upstream Hermes CLI remains available, but the Hafiye product also owns a
small, stable command vocabulary.  This module only adapts that vocabulary to
the existing Hafiye business-logic boundaries; it does not create a second
configuration store, runtime manager, task registry, or computer controller.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from typing import Any


class HafiyeCLIError(RuntimeError):
    """A user-facing Hafiye CLI validation error."""


def _print_result(value: Any, *, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if isinstance(item, (dict, list, tuple)):
                print(f"{key}: {json.dumps(item, ensure_ascii=False, sort_keys=True)}")
            else:
                print(f"{key}: {item}")
        return
    print(value)


def _hafiye_section(config: dict[str, Any]) -> dict[str, Any]:
    section = config.get("hafiye")
    if not isinstance(section, dict):
        section = {}
        config["hafiye"] = section
    return section


def _route_snapshot(config: Mapping[str, Any]) -> dict[str, Any]:
    section = config.get("hafiye")
    section = section if isinstance(section, Mapping) else {}
    return {
        "privacy_mode": section.get("privacy_mode", "NORMAL"),
        "route_slots": section.get("route_slots", {}),
        "task_overrides": section.get("task_overrides", {}),
    }


def _default_local_model(manager) -> str:
    """Resolve a useful local model for ``hafiye model load``.

    A running server's model wins, then the configured default route, then a
    sole registered model.  Ambiguity is surfaced instead of silently loading
    an arbitrary GGUF.
    """
    health = manager.health()
    active = str(health.get("model_id") or "").strip()
    if active:
        return active

    from hermes_cli.config import load_config

    config = load_config()
    section = config.get("hafiye") if isinstance(config, dict) else None
    routes = section.get("route_slots") if isinstance(section, dict) else None
    default_route = routes.get("default") if isinstance(routes, dict) else None
    if isinstance(default_route, dict):
        configured = str(default_route.get("model") or "").strip()
        if configured and any(item.get("id") == configured for item in manager.models()):
            return configured

    model_config = config.get("model") if isinstance(config, dict) else None
    if isinstance(model_config, dict):
        configured = str(
            model_config.get("default") or model_config.get("model") or ""
        ).strip()
        if configured and any(item.get("id") == configured for item in manager.models()):
            return configured

    models = [str(item.get("id") or "") for item in manager.models()]
    models = [model for model in models if model]
    if len(models) == 1:
        return models[0]
    if not models:
        raise HafiyeCLIError(
            "Kayıtlı GGUF model yok; önce `hafiye runtime model import` veya "
            "`hafiye runtime model download` çalıştırın."
        )
    raise HafiyeCLIError(
        "Birden fazla GGUF model kayıtlı; `hafiye model load MODEL_ID` belirtin."
    )


def cmd_hafiye_ask(args: argparse.Namespace) -> int:
    """Run a one-shot request through the existing Hafiye agent path."""
    from hermes_cli.oneshot import run_oneshot

    prompt = " ".join(args.prompt).strip()
    if not prompt:
        raise HafiyeCLIError("hafiye ask bir istek metni gerektirir")
    return run_oneshot(
        prompt,
        model=args.model,
        provider=args.provider,
        toolsets=args.toolsets,
        skills=args.skills,
        usage_file=args.usage_file,
    )


def cmd_hafiye_service(args: argparse.Namespace) -> int:
    """Manage the persistent Hafiye backend, not Hermes messaging adapters."""
    from hermes_cli.persistent_gateway import service_action

    return service_action(args.hafiye_service_command)


def cmd_hafiye_models(args: argparse.Namespace) -> int:
    from hermes_cli.local_runtime import LocalRuntimeError, runtime_manager

    try:
        manager = runtime_manager()
        models = manager.models()
        if args.models_command in (None, "list", "ls"):
            if args.json:
                _print_result({"models": models}, as_json=True)
            elif not models:
                print("Kayıtlı GGUF model yok.")
            else:
                for item in models:
                    availability = "ready" if item.get("available") else "missing"
                    print(f"{item.get('id', '')}\t{availability}\t{item.get('path', '')}")
            return 0
        raise HafiyeCLIError(f"Bilinmeyen models komutu: {args.models_command}")
    except (LocalRuntimeError, HafiyeCLIError) as exc:
        print(f"hafiye models: {exc}", file=sys.stderr)
        return 1


def cmd_hafiye_model(args: argparse.Namespace) -> int:
    from hermes_cli.local_runtime import LocalRuntimeError, runtime_manager

    try:
        manager = runtime_manager()
        action = args.model_action
        if action == "unload":
            result = manager.stop_server()
        elif action == "load":
            model_id = args.model_id or _default_local_model(manager)
            result = manager.start_server(
                model_id,
                backend=args.backend,
                context_size=args.context_size,
                gpu_layers=args.gpu_layers,
                port=args.port,
            )
        else:
            raise HafiyeCLIError("hafiye model için `load` veya `unload` kullanın")
        _print_result(result, as_json=args.json)
        return 0
    except (LocalRuntimeError, HafiyeCLIError) as exc:
        print(f"hafiye model: {exc}", file=sys.stderr)
        return 1


def cmd_hafiye_providers(args: argparse.Namespace) -> int:
    from hermes_cli.models import list_available_providers

    # Plugins can contribute a provider row that is also present in the
    # canonical list.  Keep the product CLI deterministic without changing
    # the upstream picker/catalog behavior.
    providers = []
    seen: set[str] = set()
    for provider in list_available_providers():
        provider_id = str(provider.get("id") or "")
        if provider_id in seen:
            continue
        seen.add(provider_id)
        providers.append(provider)
    if args.json:
        _print_result({"providers": providers}, as_json=True)
    else:
        for provider in providers:
            marker = "configured" if provider.get("authenticated") else "not configured"
            aliases = ", ".join(provider.get("aliases") or [])
            suffix = f" (aliases: {aliases})" if aliases else ""
            print(f"{provider.get('id', '')}\t{marker}\t{provider.get('label', '')}{suffix}")
    return 0


def cmd_hafiye_routing(args: argparse.Namespace) -> int:
    from hafiye_policy import PRIVACY_MODES, ROUTE_SLOTS
    from hermes_cli.config import load_config, save_config

    config = load_config()
    action = getattr(args, "routing_command", None)
    if action in (None, "show"):
        _print_result(_route_snapshot(config), as_json=args.json)
        return 0

    if action != "set":
        raise HafiyeCLIError(f"Bilinmeyen routing komutu: {action}")
    if args.locality_policy and args.locality_policy not in PRIVACY_MODES:
        raise HafiyeCLIError("Geçersiz locality policy")
    if args.provider is None and args.model is None and args.locality_policy is None:
        raise HafiyeCLIError("routing set en az bir değer gerektirir")

    section = _hafiye_section(config)
    slots = section.get("route_slots")
    if not isinstance(slots, dict):
        slots = {}
        section["route_slots"] = slots
    slot = slots.get(args.slot)
    if not isinstance(slot, dict):
        slot = {}
        slots[args.slot] = slot
    if args.provider is not None:
        slot["provider"] = args.provider
    if args.model is not None:
        slot["model"] = args.model
    if args.locality_policy is not None:
        slot["locality_policy"] = args.locality_policy
    save_config(config, merge_existing=True)
    from hafiye_audit import record_audit

    record_audit(
        "provider_model_switch",
        route_slot=args.slot,
        provider=slot.get("provider", ""),
        model=slot.get("model", ""),
        locality_policy=slot.get("locality_policy", "NORMAL"),
    )
    _print_result(_route_snapshot(config), as_json=args.json)
    return 0


def cmd_hafiye_privacy(args: argparse.Namespace) -> int:
    from hafiye_policy import PRIVACY_MODES, normalize_privacy_mode
    from hermes_cli.config import load_config, save_config

    config = load_config()
    if args.mode is not None:
        mode = normalize_privacy_mode(args.mode)
        if mode not in PRIVACY_MODES:
            raise HafiyeCLIError(f"Geçersiz privacy mode: {args.mode}")
        section = _hafiye_section(config)
        section["privacy_mode"] = mode
        save_config(config, merge_existing=True)
        from hafiye_audit import record_audit

        record_audit("privacy_mode_change", privacy_mode=mode)
    else:
        mode = normalize_privacy_mode(_route_snapshot(config)["privacy_mode"])
    _print_result({"privacy_mode": mode}, as_json=args.json)
    return 0


def cmd_hafiye_tasks(args: argparse.Namespace) -> int:
    from tools.task_center import task_center

    tasks = task_center.list(session_id=args.session_id)
    if args.json:
        _print_result({"tasks": tasks}, as_json=True)
    elif not tasks:
        print("Hafiye Task Center boş.")
    else:
        for task in tasks:
            print(
                f"{task.get('task_id', '')}\t{task.get('state', '')}\t"
                f"{task.get('goal', '')}"
            )
    return 0


def cmd_hafiye_task(args: argparse.Namespace) -> int:
    from tools.task_center import task_center

    task = task_center.get(args.task_id)
    if task is None:
        print(f"hafiye task: bulunamadı: {args.task_id}", file=sys.stderr)
        return 1
    if args.task_command == "cancel":
        try:
            task = task_center.cancel(args.task_id)
        except (KeyError, ValueError) as exc:
            print(f"hafiye task: {exc}", file=sys.stderr)
            return 1
        from hafiye_audit import record_audit

        record_audit("task_cancellation", task_id=args.task_id, state=task.get("state"))
    _print_result(task, as_json=args.json)
    return 0


def cmd_hafiye_computer(args: argparse.Namespace) -> int:
    from hafiye_computer_use import run_doctor

    result = run_doctor()
    _print_result(result, as_json=args.json)
    return 0 if result.get("ok") else 1


def build_hafiye_cli_parser(subparsers) -> None:
    """Register the product-level CLI vocabulary."""
    ask = subparsers.add_parser(
        "ask",
        help="Send one request and print the final response",
        description="Run one request through the same Hafiye agent path used by Desktop.",
    )
    ask.add_argument("prompt", nargs="+", help="Request text")
    ask.add_argument("--model", default=None)
    ask.add_argument("--provider", default=None)
    ask.add_argument("--toolsets", default=None)
    ask.add_argument("--skill", dest="skills", action="append", default=None)
    ask.add_argument("--usage-file", default=None)
    ask.add_argument(
        "--safe-mode",
        action="store_true",
        help="Ignore user config/rules for this request (use with explicit provider/model)",
    )
    ask.set_defaults(func=cmd_hafiye_ask)

    for action, help_text in (
        ("start", "Start the persistent Hafiye backend service"),
        ("stop", "Stop the persistent Hafiye backend service"),
        ("restart", "Restart the persistent Hafiye backend service"),
    ):
        lifecycle = subparsers.add_parser(action, help=help_text)
        lifecycle.set_defaults(hafiye_service_command=action, func=cmd_hafiye_service)

    models = subparsers.add_parser(
        "models", help="List managed local GGUF models", description="Inspect Hafiye's local GGUF registry."
    )
    models_sub = models.add_subparsers(dest="models_command")
    models_list = models_sub.add_parser("list", aliases=["ls"], help="List registered models")
    models_list.add_argument("--json", action="store_true", default=argparse.SUPPRESS)
    models.add_argument("--json", action="store_true")
    models.set_defaults(func=cmd_hafiye_models)

    providers = subparsers.add_parser("providers", help="List available inference providers")
    providers.add_argument("--json", action="store_true")
    providers.set_defaults(func=cmd_hafiye_providers)

    routing = subparsers.add_parser("routing", help="Show or update Hafiye route slots")
    routing_sub = routing.add_subparsers(dest="routing_command")
    routing_show = routing_sub.add_parser("show", help="Show route slots")
    routing_show.add_argument("--json", action="store_true", default=argparse.SUPPRESS)
    routing_set = routing_sub.add_parser("set", help="Update one route slot")
    from hafiye_policy import PRIVACY_MODES, ROUTE_SLOTS

    routing_set.add_argument("--slot", choices=ROUTE_SLOTS, default="default")
    routing_set.add_argument("--provider")
    routing_set.add_argument("--model")
    routing_set.add_argument("--locality-policy", choices=PRIVACY_MODES)
    routing_set.add_argument("--json", action="store_true", default=argparse.SUPPRESS)
    routing.add_argument("--json", action="store_true")
    routing.set_defaults(func=cmd_hafiye_routing)

    privacy = subparsers.add_parser("privacy", help="Show or set Hafiye privacy mode")
    privacy.add_argument("mode", nargs="?", choices=PRIVACY_MODES)
    privacy.add_argument("--json", action="store_true")
    privacy.set_defaults(func=cmd_hafiye_privacy)

    tasks = subparsers.add_parser("tasks", help="List durable Hafiye Task Center records")
    tasks.add_argument("--session-id", default=None)
    tasks.add_argument("--json", action="store_true")
    tasks.set_defaults(func=cmd_hafiye_tasks)

    task = subparsers.add_parser("task", help="Inspect or cancel one Hafiye task")
    task_sub = task.add_subparsers(dest="task_command")
    for action, help_text in (("show", "Show a task"), ("cancel", "Request task cancellation")):
        action_parser = task_sub.add_parser(action, help=help_text)
        action_parser.add_argument("task_id")
        action_parser.add_argument("--json", action="store_true")
    task.set_defaults(func=cmd_hafiye_task)

    computer = subparsers.add_parser(
        "computer",
        help="Run the managed computer-use-linux readiness check",
        description="Check the Hafiye-managed Linux desktop controller.",
    )
    computer_sub = computer.add_subparsers(dest="computer_command")
    computer_doctor = computer_sub.add_parser("doctor", help="Run the readiness check")
    computer_doctor.add_argument("--json", action="store_true", default=argparse.SUPPRESS)
    computer.add_argument("--json", action="store_true")
    computer.set_defaults(func=cmd_hafiye_computer)


__all__ = [
    "HafiyeCLIError",
    "build_hafiye_cli_parser",
    "cmd_hafiye_ask",
    "cmd_hafiye_computer",
    "cmd_hafiye_model",
    "cmd_hafiye_models",
    "cmd_hafiye_privacy",
    "cmd_hafiye_providers",
    "cmd_hafiye_routing",
    "cmd_hafiye_service",
    "cmd_hafiye_task",
    "cmd_hafiye_tasks",
]
