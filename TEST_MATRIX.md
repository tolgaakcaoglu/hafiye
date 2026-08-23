# P0 Test Matrix

Results below are from the unmodified Hermes baseline plus real environment diagnostics. A command being run is not treated as a pass unless its result says so.

| ID | Boundary | Command | Result | Status |
|---|---|---|---|---|
| P0-BE-01 | Hermes backend full suite, lean upstream extras | `./scripts/run_tests.sh` | 3,210 files; 36,814 passed, 80 failed, 324 skipped; exit non-zero | REFERENCE BASELINE |
| P0-BE-02 | Hermes CLI import/startup | `.venv/bin/hermes --help` | Help and command registry rendered; exit 0 | PASS |
| P0-BE-03 | Direct agent entrypoint | `.venv/bin/python run_agent.py --help` | Help rendered; exit 0 | PASS |
| P0-D-01 | Desktop dependency install | `npm install` | Completed; npm reported 3 high-severity audit findings | PASS WITH WARNING |
| P0-D-02 | Desktop production build | `cd apps/desktop && npm run build` | Vite renderer, Electron main/preload, native deps, and `assert-dist-built` passed | PASS |
| P0-D-03 | Desktop TypeScript | `cd apps/desktop && npm run typecheck` | Renderer, Electron, and E2E TypeScript checks passed | PASS |
| P0-D-04 | Desktop UI tests | `cd apps/desktop && npm run test:ui` | 578 files; 5,545 passed | PASS |
| P0-D-05 | Desktop Electron/platform tests | `cd apps/desktop && npm run test:desktop:platforms` | 112 files; 1,598 passed; 3 skipped | PASS |
| P0-BE-06 | Hermes backend full suite, relevant optional SDKs installed | `./scripts/run_tests.sh` after installing `anthropic`, `fal-client`, `hindsight-client`, `daytona`, `modal`, and `parallel-web` into `.venv` | 3,210 files; 36,903 passed; 5 failed; 320 skipped; exit 1; exact five test IDs below | ACCEPTED_UPSTREAM_BASELINE |
| P0-CU-01 | Historical released-package doctor | released npm `@agent-sh/computer-use-linux@0.4.9` `doctor` | Exit 0, but readiness blockers were reported; report saved under `docs/p0` | HISTORICAL DIAGNOSTIC |
| P0-CU-02 | Pinned source release asset | source package `0.4.10` installer | Expected x86_64 release asset returned HTTP 404 | WARNING; NOT FINAL PATH |
| P0-CU-03 | Pinned source official setup | `cd /tmp/hafiye-computer-use-linux.djXfCX/repo && ./install.sh --package-manager apt` | System dependencies, Rustup/Cargo 1.98.0, source build, AT-SPI, ydotool/ydotoold packages, and GNOME extension installation completed with normal interactive sudo | PASS WITH RELOGIN |
| P0-CU-04 | Pinned source post-setup doctor before relogin | `~/.local/bin/computer-use-linux doctor | jq '{readiness: .readiness, accessibility: .accessibility, windowing: .windowing, input: .input}'` | `can_register_mcp_tools=true`, `can_build_accessibility_tree=true`, `can_send_development_input=true`; `can_query_windows=false`; one window-introspection blocker | BLOCKED — RELOGIN REQUIRED |
| P0-ENV-01 | User systemd session | `systemctl --user is-system-running` | `running` | PASS |
| P0-ENV-02 | Vulkan CLI probe | `vulkaninfo` | Command unavailable; Vulkan loader/ICDs are present and Vulkan is a fallback backend | WARNING / DIAGNOSTIC |
| P0-ENV-03 | Rust source build prerequisite | `~/.cargo/bin/cargo --version` | `cargo 1.98.0`; user-space toolchain installed by the pinned source installer | PASS |

## Accepted upstream baseline failure set

The five `P0-BE-06` failures are:

1. `tests/gateway/test_browser_control_api.py::test_remote_api_uses_the_same_authenticated_noop_round_trip`
2. `tests/test_hermes_state.py::TestFTS5Search::test_search_projection_skips_context_enrichment_queries`
3. `tests/tools/test_execution_flag_detection.py::test_real_binaries_execute_leading_dash_program_payload[sort-args2-{bulk}-False]`
4. `tests/tools/test_termux_api_detection.py::TestDetectAudioEnvironmentTermuxFallback::test_inconclusive_probes_with_binary_does_not_emit_app_warning`
5. `tests/hermes_cli/test_doctor.py::test_doctor_reports_vercel_backend_diagnostics`

This exact set is the future regression baseline. The same set after Hafiye source changes is accepted; fewer failures updates the baseline; any new or different failure is investigated. These upstream failures are not fixed in P0.

## P0 computer-use acceptance

P0 is not marked complete yet. The final pinned-source doctor must report all of these as true:

- `can_register_mcp_tools`
- `can_build_accessibility_tree`
- `can_send_development_input`
- `can_query_windows`

It must also report `blockers: []`. Until that real post-setup command passes, KI-004 remains the only P0 blocker.
