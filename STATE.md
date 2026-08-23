# Hafiye State

Last updated: 2026-08-23

## Repository and commit state

- Branch: `hafiye/p0`
- `origin`: `https://github.com/tolgaakcaoglu/hafiye.git`
- `upstream`: `https://github.com/NousResearch/hermes-agent.git`
- Pinned Hermes upstream commit: `f293e7206b4ddd66042329442c6afebc19a8808d`
- Baseline merge commit: `2ac06b131a237916432503ac67bbcada6dbea39e`
- Current Hafiye HEAD at this state capture: `0b2febafcead545b208f1e91c237c9f40bab40f9`

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

- Pinned-source `computer-use-linux` official setup on the real Ubuntu GNOME Wayland session.
- Readiness acceptance must report all of the following as true and `blockers` as an empty array:
  `can_register_mcp_tools`, `can_build_accessibility_tree`, `can_send_development_input`, `can_query_windows`.
- Source checkout: `/tmp/hafiye-computer-use-linux.djXfCX/repo`, commit `94736dc3e0dca56acfc89752c26869fb9ed01202`.
- The released npm `0.4.9` binary is historical diagnostic evidence only; it is not the final setup path.

## Active blocker

The pre-setup doctor report has `can_register_mcp_tools=true` and `can_send_development_input=true`, but `can_build_accessibility_tree=false`, `can_query_windows=false`, and a non-empty blockers array. The official source setup still needs to configure AT-SPI, ydotool/ydotoold, GNOME Wayland window targeting, and user access to `/dev/uinput`. A logout/login may be required; P0 cannot close until the post-setup doctor is green.

`pactl` absence and `vulkaninfo` absence are recorded warnings/diagnostics, not P0 blockers. PipeWire/WirePlumber plus `wpctl` is accepted for audio enumeration, and Vulkan is a fallback rather than this host's primary compute backend.

## Known regressions

- No Hafiye source regression has been introduced; only repository instructions and P0 evidence documents have changed so far.
- The accepted five-failure set above is not attributed to Hafiye.
- Root-only `/dev/uinput`, missing Rust/Cargo before the source setup, and the unconfigured CUA desktop path remain environment/setup findings.

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
- Required final command after source setup: `~/.local/bin/computer-use-linux doctor | jq '.readiness'`.

## Exact next actions

1. Run the pinned source checkout's `./install.sh` official setup path with normal interactive sudo if requested.
2. Complete any required `computer-use-linux setup` and `computer-use-linux setup-window-targeting` steps, then follow the installer's logout/login instruction exactly if GNOME or group/device state requires it.
3. Rerun the source-built doctor and record all required readiness fields plus the empty blockers array.
4. If and only if the readiness acceptance is green, mark P0 complete with a clean completion commit and begin P1 external identity/data root work.

## Environment changes

- Installed user-space uv at `/home/tolga/.local/bin/uv`.
- Installed CPython `3.13.15` through uv and created repository `.venv`.
- Installed upstream Python dependencies and optional provider SDKs only in `.venv`; no dependency manifest or lockfile was changed.
- Installed root Node dependencies for the upstream Desktop baseline; the upstream lockfile was restored after verification.
- Inspected pinned `computer-use-linux` source; no final binary has yet been installed from the release channel.
