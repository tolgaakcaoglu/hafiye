# Implementation Decisions

These ADRs record implementation details only. They do not override `HAFIYE_MASTER_ROADMAP.md`.

## ADR-0001 — Preserve both initial Hafiye and Hermes histories

- Date: 2026-08-23
- Decision: Create the `hafiye/p0` branch from `upstream/main` and merge the existing Hafiye documentation history with `--allow-unrelated-histories`.
- Reason: The workspace initially contained Hafiye instructions without a usable Git checkout, while the product must preserve Hermes history. The resulting merge commit keeps both histories reachable and avoids rewriting upstream commits.
- Consequence: `AGENTS.md` is resolved to the Hafiye binding instruction file; the upstream source history remains the first-parent baseline.

## ADR-0002 — Use a user-space supported Python for baseline verification

- Date: 2026-08-23
- Decision: Use uv-managed CPython `3.13.15` in `.venv` rather than the system Python `3.14.4`.
- Reason: Hermes declares `>=3.11,<3.14`; installing system packages was not possible without interactive sudo.
- Consequence: This is a development-environment workaround, not a change to the product architecture or Python requirement.

## ADR-0003 — Use the latest released computer-use-linux binary for P0 diagnosis

- Date: 2026-08-23
- Decision: Run the real doctor with the released `@agent-sh/computer-use-linux@0.4.9` binary after the current source's `0.4.10` release asset returned HTTP 404.
- Reason: P0 requires a real readiness diagnostic, and the released package is the newest downloadable artifact verified by its installer checksums.
- Consequence: The result is diagnostic evidence only; Hafiye must not silently pin this as the final integration. The source/release mismatch remains in `KNOWN_ISSUES.md` and `UPSTREAM.md`.
