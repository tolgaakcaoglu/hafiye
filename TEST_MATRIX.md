# P0 Test Matrix

Results below are from the unmodified Hermes baseline plus environment diagnostics. A command being run is not treated as a pass unless its result says so.

| ID | Boundary | Command | Result | Status |
|---|---|---|---|---|
| P0-BE-01 | Hermes backend full suite, lean upstream extras | `./scripts/run_tests.sh` | 3,210 files; 36,814 passed, 80 failed, 324 skipped; exit non-zero | BLOCKED |
| P0-BE-02 | Hermes CLI import/startup | `.venv/bin/hermes --help` | Help and command registry rendered; exit 0 | PASS |
| P0-BE-03 | Direct agent entrypoint | `.venv/bin/python run_agent.py --help` | Help rendered; exit 0 | PASS |
| P0-D-01 | Desktop dependency install | `npm install` | Completed; npm reported 3 high-severity audit findings | PASS WITH WARNING |
| P0-D-02 | Desktop production build | `cd apps/desktop && npm run build` | Vite renderer, Electron main/preload, native deps, and `assert-dist-built` passed | PASS |
| P0-D-03 | Desktop TypeScript | `cd apps/desktop && npm run typecheck` | Renderer, Electron, and E2E TypeScript checks passed | PASS |
| P0-D-04 | Desktop UI tests | `cd apps/desktop && npm run test:ui` | 578 files; 5,545 passed | PASS |
| P0-D-05 | Desktop Electron/platform tests | `cd apps/desktop && npm run test:desktop:platforms` | 112 files; 1,598 passed; 3 skipped | PASS |
| P0-BE-06 | Hermes backend full suite, optional SDKs installed | `./scripts/run_tests.sh` after installing `anthropic`, `fal-client`, `hindsight-client`, `daytona`, `modal`, and `parallel-web` into `.venv` | 3,210 files; 36,903 passed, 5 failed, 320 skipped; exit non-zero | BLOCKED |
| P0-CU-01 | computer-use-linux doctor | released npm `@agent-sh/computer-use-linux@0.4.9` `doctor` | Command exit 0; readiness blockers reported | BLOCKED |
| P0-CU-02 | computer-use-linux current source release | source package `0.4.10` installer | Expected x86_64 asset returned HTTP 404 | BLOCKED |
| P0-ENV-01 | User systemd session | `systemctl --user is-system-running` | `running` | PASS |
| P0-ENV-02 | Vulkan CLI probe | `vulkaninfo` | command unavailable | NOT RUN / BLOCKED |
| P0-ENV-03 | Rust source build prerequisite | `cargo --version` | command unavailable | NOT RUN / BLOCKED |

## P0 acceptance

P0 is not marked complete. The upstream Desktop build is green, but the full backend baseline and the prescribed real desktop readiness check still have unresolved blockers.
