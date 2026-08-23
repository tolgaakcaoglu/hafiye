# Hafiye State

Last updated: 2026-08-23

## Repository and commit state

- Branch: hafiye/p0
- origin: https://github.com/tolgaakcaoglu/hafiye.git
- upstream: https://github.com/NousResearch/hermes-agent.git
- Pinned upstream commit: f293e7206b4ddd66042329442c6afebc19a8808d
- Baseline merge commit: 2ac06b131a237916432503ac67bbcada6dbea39e
- Current Hafiye source HEAD: 34f1d8c2472e6b70b71bbdbfc9d3292761dbb67b

The three SHA values above are intentionally separate: the first is the
upstream source pin, the second is the history-preserving baseline merge, and
the third is the current Hafiye product source commit.

## Current phase

P0 — Fork, pin, verify environment: complete.

P1 — Hafiye external identity and data root: complete. The next incomplete
phase is P2 — Persistent gateway + Desktop connection.

## Verified working

- Git history, remotes, upstream pin, and baseline merge are preserved.
- Normal Hafiye CLI invocation is available as .venv/bin/hafiye.
- Normal POSIX roots resolve to:
  - ~/.config/hafiye
  - ~/.local/share/hafiye
  - ~/.local/state/hafiye
  - ~/.cache/hafiye
- Explicit HERMES_HOME and context/profile overrides retain upstream
  single-root behavior for compatibility.
- The one-time, non-destructive legacy-home migration command is implemented
  and tested.
- Desktop user-facing title, menus, Quick Entry, onboarding, notifications,
  update/bootstrap messages, app identifiers, and docs use Hafiye. Upstream
  IPC keys, Python module names, compatibility environment names, and legal
  attribution remain unchanged.
- Neutral H monogram assets are installed for Desktop.
- Desktop normal data and state roots follow the same XDG policy as Python.
- The pinned computer-use-linux source doctor remains accepted from P0:
  all four required readiness booleans are true and blockers is empty.

## Regression status

The post-Hafiye full backend run reported 36,905 passed, 6 failed, and
320 skipped. Four failures are the reduced ACCEPTED_UPSTREAM_BASELINE set
below. Two additional async tests timed out only in the full run but passed
when isolated; they are recorded as diagnostic flakiness, not accepted
baseline and not Hafiye regressions.

No Hafiye-specific regression remains in the P1 targeted tests or Desktop
suite.

## Active blockers

None for P1.

The accepted upstream failures, the two isolated-passing full-suite async
timeouts, npm audit warnings, missing pactl, and missing vulkaninfo are
documented warnings/diagnostics. They are not silently treated as passes.

## Last tests and commands

### Backend and P1 identity

- .venv/bin/python -m pytest -q tests/hermes_cli/test_hafiye_identity.py tests/test_hermes_constants.py tests/hermes_cli/test_gateway_service.py
  — 153 passed, 6 skipped.
- ./scripts/run_tests.sh
  — 36,905 passed, 6 failed, 320 skipped; exit 1 because of the documented
  baseline/diagnostic failures.
- .venv/bin/ruff check on all changed Python files
  — All checks passed.

### Desktop

- cd apps/desktop && npm run test
  — 691 test files passed, 1 skipped; 7,149 tests passed, 3 skipped.
- cd apps/desktop && npm run typecheck
  — passed.
- cd apps/desktop && npm run build
  — Vite, Electron main/preload bundle, native dependency staging, and
  assert-dist-built passed. The clean build stamp is 34f1d8c2472e.
- cd apps/desktop && npm run builder -- --dir --publish never
  — Linux unpacked package passed.
- file apps/desktop/release/linux-unpacked/hafiye-desktop
  — x86-64 ELF; resources/icon.ico exists and the executable bit is set.

### Real XDG CLI smoke

With HERMES_HOME unset and all four XDG base variables pointed at a temporary
directory:

- hafiye --help rendered Hafiye usage and command names.
- hafiye config set model.default smoke-test-model wrote config/hafiye/config.yaml.
- The command created the expected config, data, state, and cache roots.

### Computer-use-linux P0 acceptance

- Pinned source commit:
  94736dc3e0dca56acfc89752c26869fb9ed01202.
- ~/.local/bin/computer-use-linux doctor
  — can_register_mcp_tools=true,
  can_build_accessibility_tree=true,
  can_send_development_input=true,
  can_query_windows=true, blockers=[].
- ~/.local/bin/computer-use-linux windows
  — returned the focused real desktop window through the GNOME extension.

## ACCEPTED_UPSTREAM_BASELINE

The original five upstream failures were accepted before Hafiye source
changes. The post-Hafiye full run reduced the measured exact set to these
four, so the current regression baseline is updated accordingly:

1. tests/test_hermes_state.py::TestFTS5Search::test_search_projection_skips_context_enrichment_queries
2. tests/tools/test_execution_flag_detection.py::test_real_binaries_execute_leading_dash_program_payload[sort-args2-{bulk}-False]
3. tests/tools/test_termux_api_detection.py::TestDetectAudioEnvironmentTermuxFallback::test_inconclusive_probes_with_binary_does_not_emit_app_warning
4. tests/hermes_cli/test_doctor.py::test_doctor_reports_vercel_backend_diagnostics

The original browser-control failure
tests/gateway/test_browser_control_api.py::test_remote_api_uses_the_same_authenticated_noop_round_trip
passed in the current full run and in isolated checks; it is retained as
historical baseline evidence, not as a current failure. The upstream bugs are
not being fixed by Hafiye.

## Exact next actions

1. Start P2 from the first incomplete roadmap item.
2. Keep the four current accepted failures as the regression comparison set.
3. Preserve the Hafiye source commit, upstream pin, and separable patch groups
   during P2 gateway work.

## Environment changes

No new privileged environment change was required for P1. P1 only aligned the
Desktop and Python path resolvers with the already documented XDG policy.
P0's real Ubuntu, GNOME Wayland, NVIDIA/CUDA, PipeWire/WirePlumber, Python,
Node, Rust, systemd-user, AT-SPI, ydotool, and uinput observations remain in
ENVIRONMENT.md.
