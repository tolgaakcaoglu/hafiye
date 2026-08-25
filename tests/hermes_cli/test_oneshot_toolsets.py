"""Tests for explicit oneshot toolset validation."""

from hermes_cli import oneshot


def test_validate_explicit_toolsets_accepts_managed_mcp(monkeypatch):
    """Managed MCP providers are selectable without a config.yaml entry."""
    from hermes_cli import tools_config

    managed_name = "hafiye-computer-use-linux"
    monkeypatch.setattr(
        "hermes_cli.config.read_raw_config",
        lambda: {"mcp_servers": {}},
    )
    monkeypatch.setattr(
        tools_config,
        "enabled_mcp_server_names",
        lambda _cfg: {managed_name},
    )

    assert oneshot._validate_explicit_toolsets(managed_name) == ([managed_name], None)
