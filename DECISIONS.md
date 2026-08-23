# Implementation Decisions

These ADRs record implementation details only. They do not override `HAFIYE_MASTER_ROADMAP.md`.

## ADR-0001 — Preserve both initial Hafiye and Hermes histories

- Date: 2026-08-23
- Decision: Create the `hafiye/p0` branch from `upstream/main` and merge the existing Hafiye documentation history with `--allow-unrelated-histories`.
- Reason: The workspace initially contained Hafiye instructions without a usable Git checkout, while the product must preserve Hermes history. The resulting merge commit keeps both histories reachable and avoids rewriting upstream commits.
- Consequence: `AGENTS.md` carries the Hafiye binding instructions first and preserves the upstream Hermes development guide below them; the upstream source history remains the first-parent baseline.

## ADR-0002 — Use a user-space supported Python for baseline verification

- Date: 2026-08-23
- Decision: Use uv-managed CPython `3.13.15` in `.venv` rather than the system Python `3.14.4`.
- Reason: Hermes declares `>=3.11,<3.14`; installing system packages was not possible without interactive sudo.
- Consequence: This is a development-environment workaround, not a change to the product architecture or Python requirement.

## ADR-0003 — Use the pinned computer-use-linux source checkout for final P0 setup

- Date: 2026-08-23
- Decision: Use source commit `94736dc3e0dca56acfc89752c26869fb9ed01202` and its official `./install.sh`/setup flow for the final P0 readiness path.
- Reason: The source commit is the mandated upstream state, while the matching `0.4.10` release asset is unavailable. The released `0.4.9` package is retained only as historical diagnostic evidence.
- Consequence: No release-channel substitute is treated as the final setup. The source/release mismatch remains a warning in `KNOWN_ISSUES.md` and `UPSTREAM.md`.
