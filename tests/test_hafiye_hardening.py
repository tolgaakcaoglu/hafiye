from __future__ import annotations

import os
from pathlib import Path

import hafiye_hardening as hardening


def test_provider_outage_recovery_uses_structured_failover_policy():
    class ProviderError(RuntimeError):
        status_code = 503

    result = hardening.provider_outage_recovery(
        ProviderError("upstream temporarily unavailable"),
        provider="local-openai-compatible",
        model="local-model",
    )

    assert result["reason"] in {"overloaded", "server_error"}
    assert result["retryable"] is True
    assert result["backoff_seconds"] > 0
    assert result["action"] in {"backoff_retry", "backoff_retry_then_fallback"}


def test_prune_audit_logs_removes_old_rotated_files_and_keeps_active(tmp_path: Path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    active = log_dir / "action-security-audit.log"
    rotated = log_dir / "action-security-audit.log.1"
    active.write_text("active audit record\n")
    rotated.write_text("old audit record\n")
    old = 1_000_000.0
    os.utime(rotated, (old, old))

    result = hardening.prune_audit_logs(
        log_dir,
        retention_days=1,
        max_total_size_mb=1,
        now=old + 2 * 86400,
    )

    assert result["deleted"] == 1
    assert not rotated.exists()
    assert active.exists()


def test_hardening_doctor_reports_all_p19_boundaries():
    result = hardening.hardening_doctor()

    assert result["ok"] is True
    assert result["blockers"] == []
    assert set(result["checks"]) == {
        "prompt_injection_boundary",
        "secrets_redaction",
        "provider_outage_handling",
        "llama_crash_recovery",
        "voice_runtime_recovery",
        "computer_use_failure",
        "loop_detector",
        "task_action_budget",
        "checkpoint_rollback",
        "config_recovery",
        "audit_retention",
        "disk_usage_limits",
    }
    assert all(check["ok"] for check in result["checks"].values())
