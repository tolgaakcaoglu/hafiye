# Known Issues

These are measured issues in the P0 baseline. They are not silently treated as passing.

## KI-001 — Upstream backend baseline is not fully green

- Status: BLOCKER for a clean P0 baseline.
- Initial evidence with the lean `[all,dev]` environment: `./scripts/run_tests.sh` completed 3,210 files with 36,814 passed, 80 failed, and 324 skipped. Most of those failures were optional SDK import gates.
- After installing the relevant optional SDKs into `.venv` and rerunning the same canonical command, the final baseline completed 3,210 files with 36,903 passed, 5 failed, and 320 skipped; exit non-zero.
- The five remaining failures are: `tests/gateway/test_browser_control_api.py` (remote API controller round-trip timeout), `tests/test_hermes_state.py` (SQLite trace-query expectation), `tests/tools/test_execution_flag_detection.py` (`sort` host behavior), `tests/tools/test_termux_api_detection.py` (container warning changes availability), and `tests/hermes_cli/test_doctor.py` (Vercel diagnostic expectation).
- The failures occurred before any Hafiye source change. They need upstream fixes, host-specific classification, or an explicit acceptance decision before P0 can close.

## KI-002 — System Python is outside the Hermes constraint

- Status: WORKAROUND ACTIVE.
- Evidence: system Python is `3.14.4`; upstream `pyproject.toml` declares `requires-python = ">=3.11,<3.14"`.
- Workaround: uv-managed CPython `3.13.15` in repository `.venv`.

## KI-003 — Host GPU does not match the roadmap hardware assumption

- Status: ENVIRONMENT BLOCKER for AMD-specific verification.
- Evidence: PCI has Intel UHD 770 and NVIDIA GeForce RTX 3080; no AMD display controller is present. OpenGL uses NVIDIA driver `595.84`.
- Consequence: the roadmap's default AMD/Vulkan path cannot be validated on this machine in P0.

## KI-004 — computer-use-linux readiness is incomplete on the real desktop

- Status: BLOCKER for real desktop-control readiness.
- Evidence from the saved doctor report: AT-SPI is disabled; GNOME Shell `GetWindows` is denied; the optional GNOME window-control extension is absent; `ydotool`, `ydotoold`, and `xdotool` are unavailable; `/dev/uinput` is root-only.
- Available paths: session DBus, desktop/RemoteDesktop/Screencast/Screenshot portals, GNOME Shell screenshot, AT-SPI bus presence, and portal input capability.
- `setup` and `setup-window-targeting` were not run in P0 because they mutate the user's desktop configuration; the diagnostic result is recorded for the next prerequisite step.

## KI-005 — computer-use-linux source/release version mismatch

- Status: UPSTREAM PACKAGING BLOCKER.
- Evidence: current `agent-sh/computer-use-linux` source advertises `0.4.10`, but its expected GitHub release binary URL returns HTTP 404. The doctor run used released npm `0.4.9`.

## KI-006 — Non-root development prerequisites are incomplete

- Status: ENVIRONMENT BLOCKER.
- Evidence: `sudo -n -v` requires interactive authentication; `cargo`/`rustc`, `vulkaninfo`, and `pactl` are unavailable.
- Consequence: system package installation and source builds requiring Rust cannot be completed unattended from this session.

## KI-007 — Baseline npm audit reports vulnerabilities

- Status: UPSTREAM BASELINE WARNING.
- Evidence: root `npm install` completed but reported 3 high-severity vulnerabilities and several deprecated packages.
- No `npm audit fix` was run because it could rewrite the upstream lockfile and dependencies during P0.

## KI-008 — No Hafiye regression evidence yet

- Status: INFORMATIONAL.
- P0 has not modified runtime or Desktop source. Any failures above are baseline/environment findings until a later change proves otherwise.
