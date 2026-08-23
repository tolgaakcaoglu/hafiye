# Hafiye State

Last updated: 2026-08-23

## Repository and commit state

- Branch: `hafiye/p0`
- `origin`: `https://github.com/tolgaakcaoglu/hafiye.git`
- `upstream`: `https://github.com/NousResearch/hermes-agent.git`
- Pinned Hermes upstream commit: `f293e7206b4ddd66042329442c6afebc19a8808d`
- Baseline merge commit: `2ac06b131a237916432503ac67bbcada6dbea39e`
- Current Hafiye HEAD at this state capture: `80ba038475eedf8effb32590896237bfebe3ad7b`

The baseline merge preserves both the original Hafiye documentation history and the Hermes upstream history. The current repository instructions combine the Hafiye binding instructions with the preserved upstream Hermes development guide.

## Current phase

P0 — Fork, pin, verify environment. P0 remains open only for the real `computer-use-linux` readiness acceptance. The upstream Hermes five-failure set is an accepted baseline and is not a P0 blocker.

## Verified working

- Remotes and the pinned Hermes commit are configured and recorded.
- Upstream backend baseline before Hafiye source changes:
  `./scripts/run_tests.sh` — 3,210 files; 36,814 passed; 80 failed; 324 skipped.
- Upstream backend baseline after installing the relevant optional SDKs:
  `./scripts/run_tests.sh` — 3,210 files; 36,903 passed; 5 failed; 320 skipped; exit 1.
- The exact five remaining failures are documented as `ACCEPTED_UPSTREAM_BASELINE` below and in `KNOWN_ISSUES.md`/`TEST_MATRIX.md`.
- `.venv/bin/hermes --help` and `.venv/bin/python run_agent.py --help` exit 0.
- Hermes Desktop baseline: build, typecheck, UI tests, and desktop/platform tests pass.
- Real host environment is documented in `ENVIRONMENT.md`.
- `wpctl` enumerates the active PipeWire/WirePlumber graph; missing `pactl` is diagnostic only.
- NVIDIA RTX 3080 and driver `595.84` are present; the amended compute policy expects CUDA as this host's primary backend, with Vulkan and CPU fallback.
- The pinned source installer completed its system-dependency, Rust, source-build, and AT-SPI steps. Rust/Cargo 1.98.0 is available at `/home/tolga/.cargo/bin`.
- `/home/tolga/.local/bin/computer-use-linux` and its COSMIC helper are source-built from commit `94736dc3e0dca56acfc89752c26869fb9ed01202`.
- `computer-use-linux setup-window-targeting` wrote the GNOME extension and enabled it for the next GNOME Shell load.
- `ydotool`/`ydotoold` and the `root:input 0660` `/dev/uinput` device are installed/configured. The current session has not reloaded the new `input` group membership yet.
- No Hafiye runtime, Desktop, gateway, provider, or product source changes have been made.

## ACCEPTED_UPSTREAM_BASELINE

These exact failures existed before Hafiye source changes and are the regression comparison set:

1. `tests/gateway/test_browser_control_api.py::test_remote_api_uses_the_same_authenticated_noop_round_trip`
2. `tests/test_hermes_state.py::TestFTS5Search::test_search_projection_skips_context_enrichment_queries`
3. `tests/tools/test_execution_flag_detection.py::test_real_binaries_execute_leading_dash_program_payload[sort-args2-{bulk}-False]`
4. `tests/tools/test_termux_api_detection.py::TestDetectAudioEnvironmentTermuxFallback::test_inconclusive_probes_with_binary_does_not_emit_app_warning`
5. `tests/hermes_cli/test_doctor.py::test_doctor_reports_vercel_backend_diagnostics`

After Hafiye source changes, the same five failures are not new regressions. If the count decreases, the accepted baseline is updated. Any new or different failure must be investigated as a regression. These upstream bugs are not being fixed in P0.

## In progress

- Post-setup source doctor now reports `can_register_mcp_tools=true`, `can_build_accessibility_tree=true`, and `can_send_development_input=true`. Only `can_query_windows=false` remains.
- The GNOME extension files are installed, but the current GNOME Shell has not reloaded them. The input group membership is also not present in this pre-relogin process.
- Source checkout: `/tmp/hafiye-computer-use-linux.djXfCX/repo`, commit `94736dc3e0dca56acfc89752c26869fb9ed01202`.
- The released npm `0.4.9` binary is historical diagnostic evidence only; it is not the final setup path.

## Active blocker

The official source setup is complete, but the post-setup doctor in the old GNOME session still has `can_query_windows=false` and one window-introspection blocker. `setup-window-targeting` explicitly requires a GNOME Shell reload, and the new `input` group membership requires a new login. P0 cannot close until the doctor is rerun after logout/login and reports all four required booleans true with `blockers=[]`.

`pactl` absence and `vulkaninfo` absence are recorded warnings/diagnostics, not P0 blockers. PipeWire/WirePlumber plus `wpctl` is accepted for audio enumeration, and Vulkan is a fallback rather than this host's primary compute backend.

## Known regressions

- No Hafiye source regression has been introduced; only repository instructions and P0 evidence documents have changed so far.
- The accepted five-failure set above is not attributed to Hafiye.
- The current process still cannot access `/dev/uinput` because group membership is pending relogin; this is an active setup finding, not permission hardening work.

## Last tests and commands

### Backend

- `./scripts/run_tests.sh` with the lean `[all,dev]` environment: 36,814 passed, 80 failed, 324 skipped.
- `uv pip install --python .venv/bin/python -e '[anthropic,fal,hindsight,daytona,modal]'`
- `uv pip install --python .venv/bin/python -e '[parallel-web]'`
- `./scripts/run_tests.sh` with the optional SDKs: 36,903 passed, 5 accepted baseline failures, 320 skipped; exit 1.

### Desktop

- `npm install` — completed; upstream audit reported 3 high-severity findings.
- `cd apps/desktop && npm run build` — passed.
- `cd apps/desktop && npm run typecheck` — passed.
- `cd apps/desktop && npm run test:ui` — 578 files; 5,545 passed.
- `cd apps/desktop && npm run test:desktop:platforms` — 112 files; 1,598 passed; 3 skipped.

### Readiness

- Historical diagnostic: `node /tmp/hafiye-computer-use-linux-npm/node_modules/@agent-sh/computer-use-linux/npm/bin/computer-use-linux.js doctor` — exit 0 with blockers; saved in `docs/p0/computer-use-linux-doctor-report.json`.
- Pinned-source post-setup diagnostic: `~/.local/bin/computer-use-linux doctor | jq '{readiness: .readiness, accessibility: .accessibility, windowing: .windowing, input: .input}'` — accessibility tree true, query windows false, one blocker; saved in `docs/p0/computer-use-linux-source-setup-doctor-report.json`.

## Exact next actions

1. Log out of the GNOME session and log back in once so the GNOME extension and `input` group membership are loaded.
2. Rerun the source-built doctor and record all required readiness fields plus the empty blockers array.
3. If and only if the readiness acceptance is green, mark P0 complete with a clean completion commit and begin P1 external identity/data root work.

## Environment changes

- Installed user-space uv at `/home/tolga/.local/bin/uv`.
- Installed CPython `3.13.15` through uv and created repository `.venv`.
- Installed upstream Python dependencies and optional provider SDKs only in `.venv`; no dependency manifest or lockfile was changed.
- Installed root Node dependencies for the upstream Desktop baseline; the upstream lockfile was restored after verification.
- Ran the pinned source checkout's official `./install.sh --package-manager apt` with normal interactive sudo.
- Installed Rustup stable 1.98.0, built the two source binaries, and installed them under `/home/tolga/.local/bin`.
- Enabled GNOME toolkit accessibility, installed `ydotool`, and installed/enabled the CUA GNOME extension for the next shell load.
- Added `tolga` to the `input` group. The current process requires relogin before that membership is active.
