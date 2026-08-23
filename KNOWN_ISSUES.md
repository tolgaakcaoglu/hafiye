# Known Issues

These are measured issues and accepted baseline findings. They are not silently treated as passing.

## KI-001 — ACCEPTED_UPSTREAM_BASELINE: five Hermes backend failures

- Status: `ACCEPTED_UPSTREAM_BASELINE`; not a Hafiye P0 blocker.
- The lean pre-change run of `./scripts/run_tests.sh` completed 3,210 files with 36,814 passed, 80 failed, and 324 skipped.
- After the relevant optional SDKs were installed into `.venv`, the canonical pre-change run completed 3,210 files with 36,903 passed, 5 failed, and 320 skipped; exit 1.
- The exact accepted failure set is:
  1. `tests/gateway/test_browser_control_api.py::test_remote_api_uses_the_same_authenticated_noop_round_trip`
  2. `tests/test_hermes_state.py::TestFTS5Search::test_search_projection_skips_context_enrichment_queries`
  3. `tests/tools/test_execution_flag_detection.py::test_real_binaries_execute_leading_dash_program_payload[sort-args2-{bulk}-False]`
  4. `tests/tools/test_termux_api_detection.py::TestDetectAudioEnvironmentTermuxFallback::test_inconclusive_probes_with_binary_does_not_emit_app_warning`
  5. `tests/hermes_cli/test_doctor.py::test_doctor_reports_vercel_backend_diagnostics`
- These failures existed before Hafiye source changes. Hafiye P0 does not fix them.
- Future comparison rule: the same five failures are not new regressions; fewer failures updates this baseline; a new or different failure is a regression to investigate.

## KI-002 — System Python is outside the Hermes constraint

- Status: `WORKAROUND ACTIVE`.
- Evidence: system Python is `3.14.4`; upstream `pyproject.toml` declares `requires-python = ">=3.11,<3.14"`.
- Workaround: uv-managed CPython `3.13.15` in repository `.venv`.

## KI-003 — Compute hardware differs from the superseded AMD assumption

- Status: `ARCHITECTURE AMENDMENT APPLIED`; not a P0 blocker.
- Evidence: the host has Intel UHD 770 and NVIDIA GeForce RTX 3080 with driver `595.84`; no AMD GPU is present.
- The binding policy is now `AUTO`: NVIDIA + CUDA when available, otherwise Vulkan, otherwise CPU. Managed llama.cpp and whisper.cpp use CUDA primary with Vulkan/CPU fallback. This host is expected to select CUDA.
- `nvidia-smi` and NVIDIA OpenGL are working. Managed CUDA inference itself remains a later runtime verification task.

## KI-004 — computer-use-linux readiness was incomplete before relogin

- Status: `RESOLVED — P0 acceptance passed`.
- Pinned source: `agent-sh/computer-use-linux` commit `94736dc3e0dca56acfc89752c26869fb9ed01202`.
- The official pinned-source setup has now enabled AT-SPI (`can_build_accessibility_tree=true`), installed ydotool/ydotoold, wrote the GNOME window-targeting extension, and changed `/dev/uinput` to `root:input 0660`.
- After logout/login, the final doctor reports `can_register_mcp_tools=true`, `can_build_accessibility_tree=true`, `can_send_development_input=true`, `can_query_windows=true`, and `blockers=[]`.
- A real `computer-use-linux windows` command returned the focused ChatGPT window using the GNOME extension backend.

## KI-005 — computer-use-linux release asset mismatch

- Status: `UPSTREAM PACKAGING WARNING`; not the final setup path.
- The pinned source is version `0.4.10`, but its expected GitHub release asset returned HTTP 404.
- The released npm `@agent-sh/computer-use-linux@0.4.9` was used only for historical diagnostic evidence. It must not be used as the final P0 setup path.
- The final P0 setup path is the pinned source checkout's official `./install.sh` flow and any official setup commands it invokes.

## KI-006 — Optional diagnostic tools and source-build prerequisites

- Status: `SETUP COMPLETE; diagnostic warnings remain`.
- `pactl` is absent, but PipeWire `1.6.2`, WirePlumber `0.5.13`, and `wpctl` are present and enumerate microphones. This is an audio diagnostic warning, not a P0 blocker.
- `vulkaninfo` is absent. The Vulkan loader/ICD packages are present, but Vulkan is now a fallback on this host rather than the primary backend. This is a compute diagnostic warning, not a P0 blocker.
- The official source setup provisioned Rust/Cargo 1.98.0 under `/home/tolga/.cargo/bin` and built the pinned source successfully.
- Ubuntu's packaged `ydotool.service` is enabled and active in the current user session. The duplicate generated `ydotoold.service` was disabled/removed after its same-socket collision, and the root user-manager ydotoold instance was disabled; the doctor and socket remain healthy through the non-root packaged unit.
- `sudo` requires normal interactive authentication (`sudo -n -v` fails). No passwordless sudo or `NOPASSWD` sudoers change is permitted; an interactive prompt is expected.

## KI-007 — Baseline npm audit reports vulnerabilities

- Status: `UPSTREAM BASELINE WARNING`.
- Root `npm install` completed but reported 3 high-severity vulnerabilities and several deprecated packages.
- No `npm audit fix` was run because it could rewrite the upstream lockfile and dependencies during P0.

## KI-008 — No Hafiye source regression evidence yet

- Status: `INFORMATIONAL`.
- P0 has changed repository instructions and evidence documents only; no Hafiye runtime/Desktop source change has been made.
- The accepted upstream baseline is not attributed to Hafiye.
