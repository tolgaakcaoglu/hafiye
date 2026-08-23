# Hafiye Current State

## Upstream base

- Repository: `https://github.com/tolgaakcaoglu/hafiye.git`
- Upstream: `https://github.com/NousResearch/hermes-agent.git`
- Pinned upstream commit: `f293e7206b4ddd66042329442c6afebc19a8808d`
- Hafiye branch: `hafiye/p0`
- Hafiye baseline merge commit: `2ac06b131a237916432503ac67bbcada6dbea39e`
- The baseline merge commit preserves the Hafiye documentation history and the upstream Hermes history; subsequent commits contain only P0 evidence documentation.

## Current phase

P0 — Fork, pin, verify environment. P0 is still open because the unmodified upstream baseline is not fully green and the real computer-use readiness report contains blockers.

## Verified working

- Git history was established from `upstream/main`; `origin` and `upstream` are configured as required.
- `uv 0.12.5` and a user-space Python `3.13.15` environment were installed because system Python `3.14.4` is outside Hermes' declared `>=3.11,<3.14` range.
- Upstream development dependencies installed into `.venv` with `uv pip install -e '.[all,dev]'`; provider test extras were then added in user space for a fuller baseline run.
- Initial upstream backend test runner completed with the lean `[all,dev]` environment: 3,210 files; 36,814 tests passed, 80 failed, 324 skipped.
- Full upstream backend rerun with the relevant optional provider SDKs completed: 3,210 files; 36,903 tests passed, 5 failed, 320 skipped; exit non-zero.
- Upstream Hermes Desktop baseline built successfully with `npm run build`.
- Desktop TypeScript typecheck passed.
- Desktop UI tests passed: 578 files, 5,545 tests.
- Desktop Electron/platform tests passed: 112 files, 1,598 tests, 3 skipped.
- Hermes CLI and `run_agent.py --help` start successfully from `.venv`.
- `@agent-sh/computer-use-linux` doctor command ran in the real Ubuntu GNOME Wayland session and produced a structured report at `docs/p0/computer-use-linux-doctor-report.json`.

## In progress

- P0 acceptance review and baseline failure classification.
- Required project-state documents are now being maintained from measured results.
- Hafiye-specific source changes have not started; P1 has not started.

## Failed / blockers

- The complete upstream backend suite still exits non-zero after optional SDK installation: 5 failures in 5 files. They are host/upstream-sensitive failures, listed with exact evidence in `KNOWN_ISSUES.md`.
- The real machine has Intel UHD 770 and NVIDIA RTX 3080 hardware, not an AMD GPU. The roadmap's AMD/Vulkan target cannot be verified on this host.
- `computer-use-linux doctor` reports AT-SPI disabled, GNOME window introspection denied, no GNOME window-control extension, no `ydotool`/`ydotoold`, no `xdotool`, and root-only `/dev/uinput`. Portal input and portal/shell screenshot paths are available.
- The current `computer-use-linux` source package reports version `0.4.10`, but its matching GitHub release asset returned HTTP 404. The diagnostic was therefore run with the released npm package `0.4.9`; this is recorded in `UPSTREAM.md`.
- `sudo` requires interactive authentication in this session, so system package installation was not performed automatically. Rust/Cargo, `vulkaninfo`, and `pactl` are not installed.

## Known regressions

- No Hafiye regression has been introduced: no upstream source file was changed during P0.
- The upstream baseline emits an existing thread warning in `tests/run_agent/test_run_agent.py`; it is recorded as baseline evidence, not attributed to Hafiye.

## Last tests

### Backend

Commands: `./scripts/run_tests.sh` before optional SDKs, then `./scripts/run_tests.sh` after installing `anthropic`, `fal-client`, `hindsight-client`, `daytona`, `modal`, and `parallel-web` into `.venv`.

Results: initial 3,210 files; 36,814 passed, 80 failed, 324 skipped. Final 3,210 files; 36,903 passed, 5 failed, 320 skipped; exit non-zero. Full details and grouping are in `TEST_MATRIX.md` and `KNOWN_ISSUES.md`.

### Desktop

- `cd apps/desktop && npm run build` — passed.
- `cd apps/desktop && npm run typecheck` — passed.
- `cd apps/desktop && npm run test:ui` — 5,545 passed.
- `cd apps/desktop && npm run test:desktop:platforms` — 1,598 passed, 3 skipped.

### Readiness

Command: `node /tmp/hafiye-computer-use-linux-npm/node_modules/@agent-sh/computer-use-linux/npm/bin/computer-use-linux.js doctor`

Result: command exited 0, but readiness blockers are present; see the saved report and `KNOWN_ISSUES.md`.

## Exact next actions

1. Resolve or explicitly baseline-classify the missing optional Hermes test dependencies and rerun the affected files.
2. Re-run the computer-use doctor after the required user/system prerequisites can be installed and AT-SPI/window targeting can be enabled.
3. Keep P0 open until the roadmap acceptance decision is supported by passing tests or documented, externally blocked checks; then begin P1 only if no blocker remains.

## Environment changes

- Added user-space `uv` at `/home/tolga/.local/bin/uv`.
- Installed CPython `3.13.15` through uv and created repository `.venv`.
- Installed upstream Python and Node dependencies for baseline verification.
- Installed upstream optional provider SDKs only in `.venv` to classify the full baseline; no dependency manifest or lockfile was changed.
- Installed only temporary diagnostic binaries under `/tmp`; no computer-use binary was added to the product tree.
- No Hafiye runtime, desktop, service, or provider source changes have been made.
