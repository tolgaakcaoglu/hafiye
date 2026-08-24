"""Tests for the Hafiye product-level CLI adapters."""

from __future__ import annotations

import argparse

from hermes_cli._parser import build_top_level_parser
from hermes_cli.hafiye_cli import (
    build_hafiye_cli_parser,
    cmd_hafiye_ask,
    cmd_hafiye_computer,
    cmd_hafiye_model,
    cmd_hafiye_privacy,
    cmd_hafiye_providers,
    cmd_hafiye_routing,
    cmd_hafiye_service,
    cmd_hafiye_task,
)
from hermes_cli.subcommands.model import build_model_parser


def _parser():
    parser, subparsers, _chat = build_top_level_parser()
    build_model_parser(
        subparsers,
        cmd_model=lambda _args: 0,
        cmd_hafiye_model=cmd_hafiye_model,
    )
    build_hafiye_cli_parser(subparsers)
    return parser


def test_product_command_surface_parses() -> None:
    parser = _parser()

    cases = {
        ("ask", "hello"): "cmd_hafiye_ask",
        ("start",): "cmd_hafiye_service",
        ("models", "list", "--json"): "cmd_hafiye_models",
        ("providers", "--json"): "cmd_hafiye_providers",
        ("routing", "set", "--slot", "fast", "--model", "m", "--json"):
            "cmd_hafiye_routing",
        ("privacy", "LOCAL_ONLY"): "cmd_hafiye_privacy",
        ("tasks", "--json"): "cmd_hafiye_tasks",
        ("task", "cancel", "task-1", "--json"): "cmd_hafiye_task",
        ("computer", "doctor", "--json"): "cmd_hafiye_computer",
        ("model", "load", "local-model", "--backend", "AUTO"):
            "cmd_hafiye_model",
        ("model", "unload"): "cmd_hafiye_model",
    }

    for argv, expected in cases.items():
        args = parser.parse_args(list(argv))
        assert args.func.__name__ == expected, argv


def test_ask_reuses_oneshot_business_path(monkeypatch) -> None:
    calls = []

    def fake_run(prompt, **kwargs):
        calls.append((prompt, kwargs))
        return 0

    monkeypatch.setattr("hermes_cli.oneshot.run_oneshot", fake_run)
    args = argparse.Namespace(
        prompt=["first", "request"],
        model="model-a",
        provider="custom",
        toolsets="hermes-cli",
        skills=["skill-a"],
        usage_file="usage.json",
    )

    assert cmd_hafiye_ask(args) == 0
    assert calls == [
        (
            "first request",
            {
                "model": "model-a",
                "provider": "custom",
                "toolsets": "hermes-cli",
                "skills": ["skill-a"],
                "usage_file": "usage.json",
            },
        )
    ]


def test_model_load_and_unload_reuse_local_runtime(monkeypatch) -> None:
    class FakeManager:
        def __init__(self):
            self.calls = []

        def health(self):
            return {"model_id": ""}

        def models(self):
            return [{"id": "local-model"}]

        def start_server(self, model_id, **kwargs):
            self.calls.append(("load", model_id, kwargs))
            return {"running": True, "model_id": model_id}

        def stop_server(self):
            self.calls.append(("unload",))
            return {"ok": True, "stopped": True}

    manager = FakeManager()
    monkeypatch.setattr("hermes_cli.local_runtime.runtime_manager", lambda: manager)

    load_args = argparse.Namespace(
        model_action="load",
        model_id=None,
        backend="AUTO",
        context_size=2048,
        gpu_layers=None,
        port=11435,
        json=True,
    )
    unload_args = argparse.Namespace(model_action="unload", json=True)

    assert cmd_hafiye_model(load_args) == 0
    assert cmd_hafiye_model(unload_args) == 0
    assert manager.calls == [
        (
            "load",
            "local-model",
            {
                "backend": "AUTO",
                "context_size": 2048,
                "gpu_layers": None,
                "port": 11435,
            },
        ),
        ("unload",),
    ]


def test_service_adapter_targets_persistent_hafiye_gateway(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(
        "hermes_cli.persistent_gateway.service_action",
        lambda action: calls.append(action) or 0,
    )

    assert cmd_hafiye_service(argparse.Namespace(hafiye_service_command="restart")) == 0
    assert calls == ["restart"]


def test_routing_and_privacy_write_shared_config(monkeypatch) -> None:
    config = {
        "hafiye": {
            "privacy_mode": "NORMAL",
            "route_slots": {"default": {"provider": "", "model": ""}},
        }
    }
    saved = []
    monkeypatch.setattr("hermes_cli.config.load_config", lambda: config)
    monkeypatch.setattr("hermes_cli.config.save_config", lambda value, **kwargs: saved.append((value, kwargs)))

    routing_args = argparse.Namespace(
        routing_command="set",
        slot="default",
        provider="custom",
        model="local-model",
        locality_policy="LOCAL_ONLY",
        json=True,
    )
    privacy_args = argparse.Namespace(mode="OFFLINE", json=True)

    assert cmd_hafiye_routing(routing_args) == 0
    assert cmd_hafiye_privacy(privacy_args) == 0
    assert config["hafiye"]["route_slots"]["default"] == {
        "provider": "custom",
        "model": "local-model",
        "locality_policy": "LOCAL_ONLY",
    }
    assert config["hafiye"]["privacy_mode"] == "OFFLINE"
    assert len(saved) == 2
    assert all(options == {"merge_existing": True} for _value, options in saved)


def test_provider_listing_deduplicates_plugin_rows(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "hermes_cli.models.list_available_providers",
        lambda: [
            {"id": "custom", "label": "Custom", "authenticated": True, "aliases": []},
            {"id": "custom", "label": "Custom", "authenticated": True, "aliases": []},
            {"id": "gemini", "label": "Gemini", "authenticated": False, "aliases": []},
        ],
    )

    assert cmd_hafiye_providers(argparse.Namespace(json=True)) == 0
    assert capsys.readouterr().out.count('"id": "custom"') == 1


def test_task_cancel_uses_durable_task_center(monkeypatch) -> None:
    class FakeTasks:
        def __init__(self):
            self.calls = []

        def get(self, task_id):
            return {"task_id": task_id, "state": "RUNNING"}

        def cancel(self, task_id):
            self.calls.append(task_id)
            return {"task_id": task_id, "state": "CANCELLING"}

    fake = FakeTasks()
    monkeypatch.setattr("tools.task_center.task_center", fake)

    assert cmd_hafiye_task(
        argparse.Namespace(task_command="cancel", task_id="task-1", json=True)
    ) == 0
    assert fake.calls == ["task-1"]


def test_computer_command_returns_doctor_status(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "hafiye_computer_use.run_doctor",
        lambda: {"ok": True, "blockers": [], "readiness": {"can_query_windows": True}},
    )

    assert cmd_hafiye_computer(argparse.Namespace(json=True, computer_command="doctor")) == 0
    assert '"ok": true' in capsys.readouterr().out
