# Upstream Hermes State

## Remotes

origin   https://github.com/tolgaakcaoglu/hafiye.git
upstream https://github.com/NousResearch/hermes-agent.git

## Separate commit identities

- Pinned upstream commit:
  f293e7206b4ddd66042329442c6afebc19a8808d
- Baseline merge commit:
  2ac06b131a237916432503ac67bbcada6dbea39e
- Current Hafiye HEAD (latest product/source commit):
  34f1d8c2472e6b70b71bbdbfc9d3292761dbb67b

These SHA values are intentionally separate. The first is the Hermes source
pin, the second is the history-preserving Hafiye baseline merge, and the third
is the latest Hafiye product source commit. Documentation closure commits
after the source commit do not change the product source pin.

## Pinned Hermes base

- Upstream ref: upstream/main
- Pinned commit subject:
  fix(dashboard): detect stale code after hermes update and refuse model picker
  with clear 503 (#86207)
- Last fetch: 2026-08-23
- Hafiye development branch: hafiye/p0

The branch was created from upstream/main and merged with the original Hafiye
documentation history using --allow-unrelated-histories. Both histories remain
reachable; Hermes history is not rewritten.

## Sync and conflicts

- The initial merge had one add/add conflict in AGENTS.md. The current file
  carries the Hafiye binding instructions first and preserves the upstream
  Hermes development guide below them.
- Hafiye source implementation was added after the P0 baseline in separable
  commits; no upstream commit was rewritten.
- The working branch tracks upstream/main for upstream visibility; origin
  remains the Hafiye repository.
- Internal Hermes names remain where they are part of upstream compatibility:
  Python module names, IPC keys, HERMES_* environment names, the legacy Hermes
  protocol scheme, and the upstream npm package name.

## Hafiye patch groups

The current Hafiye source commit contains these separable logical groups:

- branding: normal user-facing CLI and Desktop identity boundary.
- xdg-paths: shared Hafiye config, data, state, and cache roots.
- legacy-migration: conservative non-destructive import from ~/.hermes.
- desktop-assets: neutral H monogram assets and package identity.
- desktop-remote-roots: Desktop and remote lifecycle root alignment.

Future changes should remain separable under the roadmap groups:

- persistent-gateway
- local-model-runtime
- routing
- linux-computer-use
- root-broker
- voice-local-stack
- hafiye-wakeword
- project-registry
- openhands
- control-center
- packaging

## Accepted upstream test baseline

Before Hafiye source changes, the canonical backend suite with relevant
optional SDKs completed with 36,903 passed, 5 failed, and 320 skipped. The
exact five test IDs were:

1. tests/gateway/test_browser_control_api.py::test_remote_api_uses_the_same_authenticated_noop_round_trip
2. tests/test_hermes_state.py::TestFTS5Search::test_search_projection_skips_context_enrichment_queries
3. tests/tools/test_execution_flag_detection.py::test_real_binaries_execute_leading_dash_program_payload[sort-args2-{bulk}-False]
4. tests/tools/test_termux_api_detection.py::TestDetectAudioEnvironmentTermuxFallback::test_inconclusive_probes_with_binary_does_not_emit_app_warning
5. tests/hermes_cli/test_doctor.py::test_doctor_reports_vercel_backend_diagnostics

After Hafiye source changes, the same five are not regressions. The current
full run measured 36,905 passed, 6 failed, and 320 skipped. The browser-control
failure now passes, so the current exact ACCEPTED_UPSTREAM_BASELINE is the
remaining four IDs listed in KNOWN_ISSUES.md and STATE.md. The two additional
full-run async timeouts pass in isolation and are tracked as diagnostics, not
as accepted baseline. Hafiye does not fix the upstream bugs.

## Computer-use-linux pinned source

- Repository: https://github.com/agent-sh/computer-use-linux
- Pinned source commit:
  94736dc3e0dca56acfc89752c26869fb9ed01202
- Source checkout used for final setup:
  /home/tolga/.cache/hafiye/computer-use-linux
- Source package version: 0.4.10
- Official final P0 setup path: the pinned checkout's ./install.sh flow,
  including its official system-dependency, Rust, build, AT-SPI, ydotoold, and
  GNOME extension steps. The setup and setup-window-targeting commands remain
  available where the installer or doctor requires them.
- Setup result: ./install.sh --package-manager apt installed required Debian
  packages, Rustup stable/Cargo 1.98.0, source-built binaries, AT-SPI,
  ydotool/ydotoold, and the GNOME window-targeting extension. After relogin,
  the checkout reran ./install.sh --skip-system-deps
  --skip-gnome-extension; source build, AT-SPI, user-service setup, and doctor
  passed.
- sudo usermod -aG input tolga was completed; /dev/uinput is root:input 0660
  and read/write access is verified in the new session.
- Ubuntu's packaged /usr/lib/systemd/user/ydotool.service was already active
  and owns the ydotool socket. The duplicate generated ydotoold.service was
  disabled/removed after its same-socket collision; a separate root
  user-manager ydotoold instance was also disabled.
- The source's expected 0.4.10 GitHub release asset returned HTTP 404. Released
  npm 0.4.9 was used only for historical diagnostic evidence and is not the
  final setup path.
- Historical and final doctor reports are saved under docs/p0:
  computer-use-linux-doctor-report.json,
  computer-use-linux-source-setup-doctor-report.json, and
  computer-use-linux-final-doctor-report.json.
- Final pinned-source doctor output has all required readiness booleans true and
  blockers=[]; a real computer-use-linux windows query returned the focused
  desktop window through gnome-shell-extension.

P0 computer-use acceptance requires:

- can_register_mcp_tools = true
- can_build_accessibility_tree = true
- can_send_development_input = true
- can_query_windows = true
- blockers = []

## P1 source validation

- Current source commit: 34f1d8c2472e6b70b71bbdbfc9d3292761dbb67b.
- Python identity/XDG targeted tests: 153 passed, 6 skipped.
- Desktop full suite: 691 files passed, 7,149 tests passed, 3 skipped.
- Desktop typecheck, clean production build, and Linux unpacked packaging passed.
- The clean Desktop build stamp records the current source commit and dirty=false.
- The source changes are limited to the P1 identity/path boundary and tests;
  upstream internal compatibility identifiers remain intentionally intact.

## Baseline divergence

The upstream Hermes baseline contains its own cua-driver computer-use
integration. Hafiye has not changed or replaced it in P0; the roadmap-
prescribed agent-sh/computer-use-linux integration remains a later Hafiye
phase.
