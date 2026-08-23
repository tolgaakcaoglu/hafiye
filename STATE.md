# Hafiye State

Last updated: 2026-08-23

## Repository and commit state

- Branch: hafiye/p0
- origin: https://github.com/tolgaakcaoglu/hafiye.git
- upstream: https://github.com/NousResearch/hermes-agent.git
- Pinned upstream commit: f293e7206b4ddd66042329442c6afebc19a8808d
- Baseline merge commit: 2ac06b131a237916432503ac67bbcada6dbea39e
- Current Hafiye source HEAD: e33bb456d109 (P3 Composer/tray/autostart)

The three SHA values above are intentionally separate: the first is the
upstream source pin, the second is the history-preserving baseline merge, and
the third is the current Hafiye product source commit.

## Current phase

P0 — Fork, pin, verify environment: complete.

P1 — Hafiye external identity and data root: complete.

P2 — Persistent gateway + Desktop connection: complete.

P3 — Hafiye Composer + tray + autostart: complete with host warnings KI-012
and KI-013. The next incomplete phase is P4 — llama.cpp managed local runtime.

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
- The real user-scoped `hafiye-gateway.service` is enabled and active on
  `127.0.0.1:9120`; its owner-only token and descriptor are under
  `~/.local/state/hafiye/gateway/`.
- Desktop boot authenticated to the persistent backend, and closing the real
  Electron process left the service active with `NRestarts=0` and the endpoint
  reachable.
- An authenticated Desktop gateway restart request restarted the service and
  returned after the new backend PID was reachable.
- Hafiye Composer now owns the Desktop Quick Entry lifecycle with
  `HOTKEY_ONLY`, `SHOW_ON_LOGIN`, and `PINNED` modes; the mandated default is
  `Super+Shift+Space` and the setting remains configurable.
- The real Desktop creates a Hafiye tray and keeps running after the main
  window is closed with Alt+F4; the persistent gateway stayed active.
- The real XDG entry at `~/.config/autostart/hafiye.desktop` contains the
  development-safe Electron executable, app path, and `--hidden` flag. The
  exact entry command was launched successfully in the Wayland session.
- The tray's later-phase controls are visibly disabled and labeled; there are
  no fake privacy, microphone-mute, or computer-control toggles.

## Regression status

The post-Hafiye full backend run reported 36,905 passed, 6 failed, and
320 skipped. Four failures are the reduced ACCEPTED_UPSTREAM_BASELINE set
below. Two additional async tests timed out only in the full run but passed
when isolated; they are recorded as diagnostic flakiness, not accepted
baseline and not Hafiye regressions.

No Hafiye-specific regression remains in the P1/P2/P3 targeted tests or
Desktop suite. P3's only measured host issue is the GNOME-owned default
shortcut conflict documented below.

## Active blockers

None for the P3 source implementation. The user service is active in the
current session. `loginctl` reports `Linger=no`, and a full reboot was not
performed in this session; the exact autostart command was launched directly
with `--hidden` as the non-disruptive login-equivalent check. GNOME currently
owns `Super+Shift+Space` for input-source switching, so the default global
shortcut reports `taken` until the user changes that binding or chooses a
different configurable shortcut.

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

### P2 persistent gateway and Desktop connection

- `./scripts/run_tests.sh tests/hermes_cli/test_persistent_gateway.py -q`
  — 4 passed.
- `./scripts/run_tests.sh tests/hermes_cli/test_persistent_gateway.py tests/hermes_cli/test_dashboard_admin_endpoints.py tests/hermes_cli/test_spawn_gateway_restart_cooldown.py tests/hermes_cli/test_web_server_profile_unification.py -q`
  — 75 passed.
- `cd apps/desktop && npm exec vitest run electron/hafiye-paths.test.ts --project electron`
  — Electron project completed with 108 files, 1,546 passed, 3 skipped.
- `cd apps/desktop && npm run typecheck`
  — passed.
- `cd apps/desktop && npm run build`
  — Vite, Electron bundles, native staging, and assert-dist-built passed; the
  build stamp recorded `e2e22c10b49ec01ef7d8420f1158668718b03fa9`.
- `.venv/bin/hafiye gateway service install`
  — installed/enabled the real user service; systemd reported enabled, active,
  and `NRestarts=0` on loopback port 9120.
- Real authenticated HTTP/WS probe against `127.0.0.1:9120`
  — HTTP request succeeded, backend version `0.20.5` returned, and the
  authenticated WebSocket reached `OPEN`.
- Real Electron launch/close with `HERMES_DESKTOP_SKIP_QUIT_CONFIRM=1`
  — Desktop log recorded persistent backend readiness; service remained active
  and reachable after Electron exit.
- Authenticated `POST /api/gateway/restart`
  — returned success, systemd reported a new active backend PID, and the
  endpoint became reachable again.

### P3 Composer, tray, and autostart

- `cd apps/desktop && ../../node_modules/.bin/vitest run electron/quick-entry.test.ts electron/composer-lifecycle.test.ts --project electron`
  — 2 files, 29 passed.
- `cd apps/desktop && ../../node_modules/.bin/vitest run src/store/quick-entry.test.ts --project ui`
  — 1 file, 17 passed.
- `cd apps/desktop && npm run test:ui`
  — 578 files, 5,547 passed.
- `cd apps/desktop && npm run test:desktop:platforms`
  — 114 files, 1,609 passed, 3 skipped.
- `cd apps/desktop && npm run typecheck`
  — renderer, Electron, and E2E checks passed.
- `cd apps/desktop && npm run build`
  — clean Vite renderer, Electron bundles, native staging, and
  `assert-dist-built` passed; clean stamp `e33bb456d109`.
- Real Wayland launch with `HERMES_DESKTOP_SKIP_QUIT_CONFIRM=1`
  — Desktop log recorded `Hafiye tray ready`, `Super+Shift+Space is already
  taken`, and persistent backend readiness.
- Real `ydotool` Alt+F4 against the Hafiye window
  — Electron process remained resident and `hafiye-gateway.service` remained
  active/listening on `127.0.0.1:9120`.
- Exact `~/.config/autostart/hafiye.desktop` `Exec=` command with `--hidden`
  — launched successfully in the current Wayland session.

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

1. Start P4 — llama.cpp managed local runtime; preserve the fixed CUDA-first
   AUTO policy and GGUF requirement.
2. Keep the four current accepted failures as the regression comparison set.
3. Preserve the Hafiye source commit, upstream pin, and separable patch groups
   during the P4 work.

## Environment changes

P2 installed and enabled the user-scoped `hafiye-gateway.service`; P3 added
the owner-safe `~/.config/autostart/hafiye.desktop` entry and Composer settings
under the Desktop user-data root. No sudo, root, passwordless sudo, or NOPASSWD
sudoers change was made. User-manager linger remains disabled. P1's XDG
alignment and P0's real Ubuntu, GNOME
Wayland, NVIDIA/CUDA, PipeWire/WirePlumber, Python, Node, Rust, systemd-user,
AT-SPI, ydotool, and uinput observations remain in ENVIRONMENT.md.
