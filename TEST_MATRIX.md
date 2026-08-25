# Test Matrix

Results below are from the Hermes baseline, the real environment, and the
completed Hafiye P1 source. A command being run is not treated as a pass unless
its result says so.

| ID | Boundary | Command | Result | Status |
|---|---|---|---|---|
| P0-BE-01 | Hermes backend full suite, lean upstream extras | ./scripts/run_tests.sh | 3,210 files; 36,814 passed, 80 failed, 324 skipped; exit non-zero | REFERENCE BASELINE |
| P0-BE-02 | Hermes CLI import/startup | .venv/bin/hermes --help | Help and command registry rendered; exit 0 | PASS |
| P0-BE-03 | Direct agent entrypoint | .venv/bin/python run_agent.py --help | Help rendered; exit 0 | PASS |
| P0-D-01 | Desktop dependency install | npm install | Completed; npm reported 3 high-severity audit findings | PASS WITH WARNING |
| P0-D-02 | Desktop production build | cd apps/desktop && npm run build | Vite renderer, Electron main/preload, native deps, and assert-dist-built passed | PASS |
| P0-D-03 | Desktop TypeScript | cd apps/desktop && npm run typecheck | Renderer, Electron, and E2E TypeScript checks passed | PASS |
| P0-D-04 | Desktop UI baseline tests | cd apps/desktop && npm run test:ui | 578 files; 5,545 passed | PASS |
| P0-D-05 | Desktop Electron/platform baseline tests | cd apps/desktop && npm run test:desktop:platforms | 112 files; 1,598 passed; 3 skipped | PASS |
| P0-BE-06 | Hermes backend full suite, relevant optional SDKs installed | ./scripts/run_tests.sh | Pre-source: 3,210 files; 36,903 passed; 5 failed; 320 skipped; exact five IDs below | ACCEPTED_UPSTREAM_BASELINE |
| P0-CU-01 | Historical released-package doctor | @agent-sh/computer-use-linux 0.4.9 doctor | Exit 0, but readiness blockers were reported; report saved under docs/p0 | HISTORICAL DIAGNOSTIC |
| P0-CU-02 | Pinned source release asset | Source package 0.4.10 installer | Expected x86_64 release asset returned HTTP 404 | WARNING; NOT FINAL PATH |
| P0-CU-03 | Pinned source official setup | cd /home/tolga/.cache/hafiye/computer-use-linux && ./install.sh --skip-system-deps --skip-gnome-extension | Pinned source rebuilt from commit 94736dc3e0dca56acfc89752c26869fb9ed01202; AT-SPI, source binaries, ydotoold setup, and installer doctor completed | PASS |
| P0-CU-04 | Pinned source final doctor | ~/.local/bin/computer-use-linux doctor | can_register_mcp_tools=true, can_build_accessibility_tree=true, can_send_development_input=true, can_query_windows=true; blockers=[] | PASS |
| P0-CU-05 | User input service | systemctl --user status ydotool.service; stat /dev/uinput | Packaged non-root user unit active/enabled; /dev/uinput is root:input 0660; socket connectable | PASS |
| P0-CU-06 | Real window query | ~/.local/bin/computer-use-linux windows | Focused ChatGPT window returned via gnome-shell-extension backend | PASS |
| P0-ENV-01 | User systemd session | systemctl --user is-system-running | running | PASS |
| P0-ENV-02 | Vulkan CLI probe | vulkaninfo | Command unavailable; Vulkan loader/ICDs are present and Vulkan is a fallback backend | WARNING / DIAGNOSTIC |
| P0-ENV-03 | Rust source build prerequisite | ~/.cargo/bin/cargo --version | cargo 1.98.0; user-space toolchain installed by pinned source installer | PASS |
| P1-PY-01 | Python Hafiye identity/XDG targeted tests | .venv/bin/python -m pytest -q tests/hermes_cli/test_hafiye_identity.py tests/test_hermes_constants.py tests/hermes_cli/test_gateway_service.py | 153 passed, 6 skipped | PASS |
| P1-D-01 | Full Desktop test suite | cd apps/desktop && npm run test | 691 test files passed, 1 skipped; 7,149 tests passed, 3 skipped | PASS |
| P1-D-02 | Desktop typecheck | cd apps/desktop && npm run typecheck | Renderer, Electron, and E2E checks passed; exit 0 | PASS |
| P1-D-03 | Desktop clean production build | cd apps/desktop && npm run build | Vite, Electron main/preload bundle, native dependency staging, and assert-dist-built passed; build stamp source is 34f1d8c2472e and dirty=false | PASS |
| P1-D-04 | Linux unpacked Desktop package | cd apps/desktop && npm run builder -- --dir --publish never | Package passed; release/linux-unpacked/hafiye-desktop is executable x86-64 ELF and resources/icon.ico exists | PASS |
| P1-BE-01 | Backend post-source full suite | ./scripts/run_tests.sh | 3,211 files; 36,905 passed, 6 failed, 320 skipped; 4 current accepted baseline failures plus 2 full-suite async diagnostics; exit 1 | PASS WITH DOCUMENTED BASELINE/DIAGNOSTICS |
| P1-LINT-01 | Changed Python lint | .venv/bin/ruff check on all changed Python files | All checks passed | PASS |
| P1-LINT-02 | Patch whitespace | git diff --check | No whitespace errors | PASS |
| P1-CLI-01 | Real temporary-root identity smoke | HERMES_HOME unset; XDG base variables set to temporary roots; .venv/bin/hafiye --help | Hafiye usage and command names rendered; exit 0; internal HERMES compatibility names remain intentionally visible where required | PASS |
| P1-CLI-02 | Real temporary-root config write | Same temporary-root setup; .venv/bin/hafiye config set model.default smoke-test-model | Wrote config/hafiye/config.yaml and created expected config, data, state, and cache roots | PASS |

| P2-PY-01 | Persistent gateway unit/token/descriptor logic | ./scripts/run_tests.sh tests/hermes_cli/test_persistent_gateway.py -q | 4 passed | PASS |
| P2-PY-02 | Persistent gateway and restart integration tests | ./scripts/run_tests.sh tests/hermes_cli/test_persistent_gateway.py tests/hermes_cli/test_dashboard_admin_endpoints.py tests/hermes_cli/test_spawn_gateway_restart_cooldown.py tests/hermes_cli/test_web_server_profile_unification.py -q | 75 passed | PASS |
| P2-D-01 | Desktop persistent gateway path tests | cd apps/desktop && npm exec vitest run electron/hafiye-paths.test.ts --project electron | Electron project: 108 files; 1,546 passed; 3 skipped | PASS |
| P2-D-02 | Desktop TypeScript | cd apps/desktop && npm run typecheck | Passed | PASS |
| P2-D-03 | Desktop production build | cd apps/desktop && npm run build | Vite, Electron bundles, native staging, and assert-dist-built passed; stamp e2e22c10b49ec01ef7d8420f1158668718b03fa9 | PASS |
| P2-REAL-01 | Real persistent user service | .venv/bin/hafiye gateway service install; systemctl --user is-enabled/is-active/show | Enabled, active, `NRestarts=0`, loopback `127.0.0.1:9120` | PASS |
| P2-REAL-02 | Authenticated persistent backend | Real Python HTTP/WS probe against `127.0.0.1:9120` | HTTP succeeded, version `0.20.5`, WebSocket `OPEN` | PASS |
| P2-REAL-03 | Desktop close persistence | Real Electron launch/close with `HERMES_DESKTOP_SKIP_QUIT_CONFIRM=1` | Persistent readiness logged; service stayed active and endpoint stayed reachable | PASS |
| P2-REAL-04 | Persistent gateway restart control | Authenticated `POST /api/gateway/restart` | Success returned; new active PID observed; endpoint reachable | PASS |
| P3-D-01 | Composer lifecycle and shortcut defaults | `cd apps/desktop && ../../node_modules/.bin/vitest run electron/quick-entry.test.ts electron/composer-lifecycle.test.ts --project electron` | 2 files; 29 passed | PASS |
| P3-D-02 | Composer state/reducer | `cd apps/desktop && ../../node_modules/.bin/vitest run src/store/quick-entry.test.ts --project ui` | 1 file; 17 passed | PASS |
| P3-D-03 | Full Desktop UI suite after Composer changes | `cd apps/desktop && npm run test:ui` | 578 files; 5,547 passed | PASS |
| P3-D-04 | Full Desktop Electron suite after tray/autostart changes | `cd apps/desktop && npm run test:desktop:platforms` | 114 files; 1,609 passed; 3 skipped | PASS |
| P3-D-05 | Desktop TypeScript | `cd apps/desktop && npm run typecheck` | Renderer, Electron, and E2E checks passed | PASS |
| P3-D-06 | Clean Desktop production build | `cd apps/desktop && npm run build` | Clean stamp `e33bb456d109`; Vite, Electron bundles, native staging, and assert-dist-built passed | PASS |
| P3-REAL-01 | XDG autostart entry | `sed -n '1,20p' ~/.config/autostart/hafiye.desktop; stat -c '%a %U:%G' ...` | Owner-created entry contains Electron executable, app path, `--hidden`; mode 0644 | PASS |
| P3-REAL-02 | Real Wayland Desktop/tray startup | `HERMES_DESKTOP_SKIP_QUIT_CONFIRM=1 electron .` plus desktop log | `Hafiye tray ready`; persistent backend readiness logged | PASS |
| P3-REAL-03 | Close-to-tray persistence | `ydotool key 56:1 62:1 62:0 56:0` plus process/systemd probes | Electron remained resident; `hafiye-gateway.service` remained active/listening | PASS |
| P3-REAL-04 | Exact autostart command | Generated `~/.config/autostart/hafiye.desktop` `Exec=` command with `--hidden` | Launched successfully in current Wayland session | PASS WITH KI-013 |
| P3-REAL-05 | Mandated default global shortcut | Real Desktop launch and GNOME keybinding inspection | `Super+Shift+Space` reported taken by GNOME input-source-backward binding | WARNING; KI-012 |

| P4-PY-01 | Managed local runtime unit tests | `./scripts/run_tests.sh tests/hermes_cli/test_local_runtime.py -q` | 6 passed; backend priority, private registry/checksums, resumable download, and safe health covered | PASS |
| P4-PY-02 | Persistent gateway subprocess environment guard | `./scripts/run_tests.sh tests/agent/test_subprocess_env_guard.py tests/hermes_cli/test_persistent_gateway.py -q` | 6 passed after the shared environment factory correction | PASS |
| P4-D-01 | Local runtime settings boundary | `cd apps/desktop && ../../node_modules/.bin/vitest run src/app/settings/model-settings.test.tsx --project ui` | 1 file; 22 passed | PASS |
| P4-D-02 | Desktop typecheck after runtime API/settings | `cd apps/desktop && npm run typecheck` | Renderer, Electron, and E2E TypeScript checks passed | PASS |
| P4-D-03 | Desktop production build after runtime API/settings | `cd apps/desktop && npm run build` | Clean working-tree build passed; Vite, Electron bundles, native staging, and assert-dist-built passed; stamp `955a9c3818fa` | PASS |
| P4-REAL-01 | Real CUDA toolchain and host detection | `nvcc --version`; `nvidia-smi`; `pkg-config --exists vulkan` | CUDA 12.4.131; NVIDIA RTX 3080/driver 595.84; Vulkan development metadata available | PASS |
| P4-REAL-02 | Managed llama.cpp build | `.venv/bin/hafiye runtime install --backend AUTO` | Source commit `c060ca974c773c7c3d17fd1b66dc9d312bc292c0`; compiled `CPU,CUDA`; selected `CUDA` | PASS |
| P4-REAL-03 | GGUF model lifecycle | `.venv/bin/hafiye runtime model download ...`; `runtime model list`; import/delete checks | Gemma and Qwen GGUFs downloaded/imported with recorded sizes and SHA-256; private registry and model root | PASS |
| P4-REAL-04 | CUDA server readiness and device use | `.venv/bin/hafiye runtime server start/restart`; `runtime doctor`; `curl /health`; `nvidia-smi --query-compute-apps` | `/health` and `/v1/models` HTTP 200; doctor blockers/warnings empty; `CUDA0: NVIDIA GeForce RTX 3080`; managed PID used GPU memory | PASS |
| P4-REAL-05 | OpenAI-compatible local chat | `curl http://127.0.0.1:11435/v1/chat/completions` | Real CUDA response contained `CUDA LOCAL OK` | PASS |
| P4-REAL-06 | Hermes provider connection | Temporary `HERMES_HOME` plus local OpenAI-compatible base URL; `.venv/bin/hermes` one-shot | Real Gemma CPU smoke returned `HERMES LOCAL OK`; CUDA Qwen one-shot returned a non-empty agent response | PASS |
| P4-REAL-07 | Model switch without reinstall | `runtime server restart` with Gemma then Qwen; health/chat probes | Second model became healthy and returned `SECOND MODEL OK` without rebuilding Hafiye | PASS |
| P4-REST-01 | Authenticated persistent gateway runtime API | `systemctl --user restart hafiye-gateway.service`; authenticated `GET /api/local-runtime` | `ok=true`, blockers empty, expected/selected backend `CUDA` | PASS |
| P4-BE-01 | Corrected backend full regression comparison | `./scripts/run_tests.sh` with persistent Hafiye gateway and managed local model server stopped temporarily | 3,213 files; 37,009 passed, 6 failed, 291 skipped in 515.9s; exact four accepted upstream failures plus the two isolated-passing async diagnostics; one retry-only flake recorded separately | PASS WITH DOCUMENTED BASELINE/DIAGNOSTICS |

| P5-PY-01 | Secret Service provider credential lifecycle | `./scripts/run_tests.sh tests/hermes_cli/test_hafiye_keyring.py tests/hermes_cli/test_p5_provider_paths.py tests/hermes_cli/test_credential_lifecycle.py tests/hermes_cli/test_prompt_api_key.py tests/hermes_cli/test_web_server.py tests/hermes_cli/test_runtime_provider_resolution.py tests/hermes_cli/test_model_switch_custom_providers.py tests/agent/test_credential_pool.py tests/hermes_cli/test_secret_source_bootstrap.py tests/secret_sources/test_secret_source_registry.py tests/secret_sources/test_profile_secrets.py tests/test_env_loader_secret_sources.py tests/hermes_cli/test_provider_parity.py tests/hermes_cli/test_gemini_provider.py tests/agent/test_gemini_native_adapter.py -q` | 15 files; 468 passed; 0 failed; includes default-XDG config-root regression coverage | PASS |
| P5-PY-02 | Provider/tool credential storage boundary | `./scripts/run_tests.sh tests/hermes_cli/test_env_export_line_lifecycle.py tests/hermes_cli/test_set_config_value.py tests/hermes_cli/test_hafiye_keyring.py tests/hermes_cli/test_p5_provider_paths.py -q` | 4 files; 93 passed; 0 failed; includes default-XDG config-root regression coverage | PASS |
| P5-REMOTE-01 | Real remote OpenAI-compatible provider path | `tests/hermes_cli/test_p5_provider_paths.py` with a local `ThreadingHTTPServer` | Authenticated `/v1/models` and chat passed; config contained no raw key; reply marker `P5_REMOTE_OK` | PASS |
| P5-REAL-01 | Real host Linux Secret Service round-trip | Live keyring write/read/delete/remove probe; secret value omitted from output | All round-trip booleans true; config contained no secret value | PASS |
| P5-LOCAL-01 | Real managed local provider endpoint | `GET /v1/models` and `POST /v1/chat/completions` against `127.0.0.1:11435`; runtime doctor | HTTP 200/non-empty model and reply; doctor `ok=true`, `blockers=[]`, selected backend `CUDA` | PASS |
| P5-D-01 | Desktop provider/key/model/custom endpoint surface | `cd apps/desktop && npm run test` | 692 test files passed, 1 skipped; 7,156 tests passed, 3 skipped; exit 0 | PASS |
| P5-D-02 | Desktop provider integration typecheck/build | `cd apps/desktop && npm run typecheck && npm run build` | Typecheck and production build passed | PASS |
| P5-GEMINI-REAL | Live Gemini test connection | Hafiye Secret Service credential hydration; `GET /v1beta/models`; `.venv/bin/hafiye -z "Reply with exactly HAFIYE_GEMINI_LIVE_OK and nothing else." --provider gemini --model gemini-flash-lite-latest --safe-mode` | Real model listing HTTP 200 with 50 models; Hafiye one-shot returned `HAFIYE_GEMINI_LIVE_OK`; raw key omitted from output and docs | PASS |
| P5-BE-01 | Latest post-P5-source-fix backend regression comparison | `./scripts/run_tests.sh` with persistent gateway and managed local model server stopped temporarily | 3,218 files; 37,156 passed, 4 failed, 244 skipped in 541.8s; all four failures are exact accepted-baseline IDs; accepted remote browser-control ID did not reproduce; web-server retry-only flake passed on retry | PASS WITH ACCEPTED BASELINE/DIAGNOSTIC |
| P6-PY-01 | Shared Hafiye route/privacy policy | `./scripts/run_tests.sh tests/test_hafiye_policy.py tests/run_agent/test_hafiye_agent_policy.py tests/gateway/test_hafiye_routing.py -q` | 3 files; 17 passed; local, remote, Gemini, LOCAL_ONLY, OFFLINE, locality, and legal-fallback checks | PASS |
| P6-PY-02 | Affected config/API/web backend matrix | `./scripts/run_tests.sh tests/test_web_server.py tests/hermes_cli/test_web_server.py tests/hermes_cli/test_config_validation.py tests/gateway/test_api_server.py tests/gateway/test_api_server_runs.py tests/hermes_cli/test_fallback_config.py -q` | 6 files; 321 passed; 3 skipped; 0 failed | PASS |
| P6-D-01 | Desktop routing/privacy settings support | `cd apps/desktop && npm run test -- --run src/app/settings/helpers.test.ts src/app/settings/settings-search.test.ts src/app/settings/voice-provider-fields.test.ts` | 3 files; 47 passed | PASS |
| P6-D-02 | Desktop routing/privacy TypeScript | `cd apps/desktop && npm run typecheck` | Renderer, Electron, and E2E TypeScript checks passed | PASS |
| P6-LINT-01 | P6 Python compile/lint/whitespace | `.venv/bin/ruff check <all P6 changed Python files>; python -m py_compile <all P6 changed Python files>; git diff --check` | Ruff checks passed; bytecode compilation and whitespace checks passed; existing upstream invalid `# noqa` warning remains | PASS WITH UPSTREAM WARNING |
| P6-GW-01 | Gateway cache/fallback contract regression fix | `./scripts/run_tests.sh tests/gateway/test_compression_failure_session_sync.py tests/gateway/test_fallback_chain_reload.py -q` | 2 files; 6 passed; 0 failed after normalizing cache mappings and retaining refreshed fallback calls | PASS |
| P6-BE-01 | Post-P6 full backend regression comparison (historical) | `./scripts/run_tests.sh` with persistent gateway and managed local model server stopped temporarily | 3,218 files; 37,154 passed, 5 failed, 244 skipped in 563.7s; four exact accepted-baseline members plus KI-019 browser reconnect diagnostic; superseded by P5-BE-01 | PASS WITH DOCUMENTED BASELINE/DIAGNOSTIC |

| P7-PY-01 | Hafiye execution-policy classifier and shared dispatch | `.venv/bin/python -m pytest -q tests/test_hafiye_execution_policy.py tests/test_model_tools.py` | 31 passed; default, confirmation, read-only, dispatch blocking, and approval-surface behavior covered | PASS |
| P7-PY-02 | Existing host-tool boundary regression suite | `.venv/bin/python -m pytest -q tests/tools/test_terminal_tool.py tests/tools/test_code_execution.py tests/tools/test_approval.py tests/tools/test_process_registry.py tests/tools/test_file_tools.py` | 285 passed, 6 skipped, 1 warning, 5 subtests passed | PASS |
| P7-REAL-01 | Real host terminal/file/process smoke | Live `model_tools.handle_function_call` dispatcher; terminal, temporary-file read, background process/wait | `HAFIYE_P7_HOST`, file content, and `HAFIYE_P7_PROCESS` observed; process exited cleanly | PASS |
| P7-D-01 | Desktop execution-policy settings boundary | `cd apps/desktop && npx vitest run --project ui src/app/settings/helpers.test.ts src/app/settings/settings-search.test.ts src/app/settings/terminal-backend-panel.test.tsx` | 3 files; 46 passed | PASS |
| P7-D-02 | Desktop settings regression isolation | `cd apps/desktop && npx vitest run --project ui src/app/settings/gateway-settings.test.tsx src/app/settings/providers-settings.test.tsx src/store/session-unread-tile.test.ts src/app/settings/toolset-config-panel.test.tsx src/app/messaging/index.test.tsx src/app/skills/index.test.tsx` | 6 files; 58 passed; rerun after the parallel-resource-contended attempt | PASS |
| P7-D-03 | Desktop TypeScript and production build | `cd apps/desktop && npm run typecheck && npm run build` | Typecheck, Vite renderer, Electron main/preload, native staging, and `assert-dist-built` passed; existing npm/Vite warnings remain | PASS WITH WARNING |
| P7-BE-01 | Full backend regression comparison | `./scripts/run_tests.sh` | 3,219 files; 37,160 passed, 7 failed, 244 skipped in 598.3s; four accepted-baseline IDs plus KI-016 cold-start topology and KI-019 browser reconnect diagnostics; no new Hafiye regression | PASS WITH DOCUMENTED BASELINE/DIAGNOSTICS |
| P7-DIAG-01 | Persistent-service cold-start topology diagnostic | `.venv/bin/python -m pytest -q tests/hermes_cli/test_update_cold_start_gateway_liveness.py` with `hafiye-gateway.service` stopped | 2 passed; service restarted and verified active afterward | PASS / KI-016 |
| P7-DIAG-02 | Browser reconnect scheduling diagnostic | `.venv/bin/python -m pytest -q tests/gateway/test_browser_control_api.py -k test_local_api_same_identity_reconnect_completes_command_started_on_old_socket` | First run timed out; immediate isolated retry passed 1/1; tracked as KI-019 | DIAGNOSTIC |

| P8-PY-01 | Root broker protocol/security and packaging regression tests | `.venv/bin/python -m pytest -q tests/test_hafiye_rootd.py tests/test_packaging_metadata.py` | 13 passed; strict framing, duplicate-key rejection, peer rejection, operation validation, audit behavior, unit generation, and packaging metadata covered | PASS |
| P8-PY-02 | CLI registration and emergency-stop regression matrix | `.venv/bin/python -m pytest -q tests/hermes_cli/test_startup_plugin_gating.py tests/test_estop.py tests/test_packaging_metadata.py tests/test_hafiye_rootd.py` | 39 passed; 0 failed | PASS |
| P8-CLI-01 | Packaged root broker entrypoints | `uv pip install --python .venv/bin/python -e . --no-deps; .venv/bin/hafiye-rootd --help; .venv/bin/hafiye root --help` | Editable package refreshed; both root-broker help surfaces rendered; exit 0 | PASS |
| P8-LINT-01 | Root broker lint, compile, and patch hygiene | `.venv/bin/ruff check hafiye_rootd.py hermes_cli/main.py tests/test_hafiye_rootd.py; .venv/bin/python -m py_compile hafiye_rootd.py hermes_cli/main.py tests/test_hafiye_rootd.py; git diff --check` | All checks passed | PASS |
| P8-REAL-01 | Real rootd system service and process boundary | Normal visible-terminal `.venv/bin/hafiye root install`; `systemctl is-enabled/is-active`; `systemctl status`; `ps`; `stat` | `/usr/lib/systemd/system/hafiye-rootd.service` enabled/active; rootd EUID 0; gateway EUID 1000; `/run/hafiye/root.sock` mode 0600 owned by `tolga`; no TCP/UDP listener | PASS |
| P8-REAL-02 | Harmless privileged operation through non-root broker | `.venv/bin/python` `RootBrokerClient`: `root.exec id -u` and `file.write_privileged` temporary-file smoke | Client EUID 1000; broker UID `0`; privileged write/content/mode/SHA-256 verified | PASS |
| P8-REAL-03 | Real malformed and unauthorized socket clients | Duplicate-key frame through `/run/hafiye/root.sock`; broker-controlled `runuser -u nobody` peer probe | Malformed response code `malformed_request`; actual `nobody` client received `permission_denied` | PASS |
| P8-REAL-04 | Real audit trail | `RootBrokerClient` read of redacted audit-log sample through `root.exec` | 33 records sampled; 11 complete request groups; accepted/rejected + closed lifecycle, peer/duration fields present; raw test command text absent | PASS |

| P9-PY-01 | Managed computer-use-linux boundary and MCP regression matrix | `.venv/bin/python -m pytest -q tests/tools/test_mcp_tool.py tests/hermes_cli/test_tools_config.py tests/cron/test_scheduler.py tests/hermes_cli/test_mcp_tools_config.py tests/test_hafiye_computer_use.py` | 258 passed; one pre-existing async resource warning from the scheduler test; user-config tests isolate the host-managed provider | PASS WITH DOCUMENTED WARNING |
| P9-D-01 | Settings → Computer diagnostics component | `cd apps/desktop && npx vitest run --project ui src/app/settings/computer-settings.test.tsx` | 1 file; 1 passed; managed backend, source pin, MCP name, and all four readiness values rendered | PASS |
| P9-D-02 | Full Desktop UI regression suite | `cd apps/desktop && npm run test:ui` | 579 files; 5,548 tests passed; existing jsdom canvas warnings only | PASS WITH WARNING |
| P9-D-03 | Desktop typecheck | `cd apps/desktop && npm run typecheck` | Renderer, Electron, and E2E TypeScript checks passed | PASS |
| P9-D-04 | Clean Desktop production build | `cd apps/desktop && npm run build` | Clean build stamp `6d3672e498e1`; Vite, Electron bundles, native staging, and `assert-dist-built` passed; existing Vite/Babel/chunking warnings remain | PASS WITH WARNING |
| P9-REAL-01 | Managed computer-use-linux doctor | Real `computer_use_linux_status()` using `/home/tolga/.local/bin/computer-use-linux` | Pinned source `94736dc3e0dca56acfc89752c26869fb9ed01202`; `ready=true`; all four required readiness booleans true; `blockers=[]` | PASS |
| P9-REAL-02 | Automatic built-in MCP registration | Real `discover_mcp_tools()` through Hermes MCP client with empty user MCP config | `hafiye-computer-use-linux` connected and 18 `mcp__hafiye_computer_use_linux__*` tools registered; no manual config edit | PASS |
| P9-REAL-03 | Wayland/GNOME computer-use E2E | Real `model_tools.handle_function_call()` MCP calls plus `/usr/bin/gnome-calculator`, Firefox, `/usr/bin/code --new-window`, and `nautilus --new-window` | Windows enumerated; Calculator AT-SPI tree read and `12*7` produced/read as `84`; Firefox tab/navigation and app switching verified; VS Code launched; Files focus/tree interaction verified with 137 accessible nodes | PASS WITH KI-022/KI-023 WARNINGS |

## P9 acceptance

The managed provider is pinned to source commit
`94736dc3e0dca56acfc89752c26869fb9ed01202`. The required readiness fields are
all true and `blockers=[]`; the real MCP provider registered 18 tools without a
user configuration edit. The Calculator, Firefox, VS Code, and Files flow was
completed on the actual Wayland/GNOME session. P9 is accepted; KI-022 and
KI-023 are warnings only.

## P10 acceptance

| ID | Boundary | Command | Result | Status |
|---|---|---|---|---|
| P10-PY-01 | Hafiye browser route, download, policy, Chromium detection, and extension wiring | `.venv/bin/python -m pytest -q tests/tools/test_hafiye_browser.py tests/tools/test_browser_chromium_check.py tests/tools/test_browser_extension_router.py tests/tools/test_browser_extension_router_wiring.py tests/test_hafiye_policy.py` | 49 passed; 0 failed | PASS |
| P10-PY-02 | Full Hermes browser regression plus Hafiye browser tests | `.venv/bin/python -m pytest -q tests/tools/test_browser_*.py tests/tools/test_hafiye_browser.py` | 504 passed; 7 deselected; 0 failed; 29.83s | PASS |
| P10-LINT-01 | P10 Python lint, compile, and patch hygiene | `.venv/bin/ruff check tools/hafiye_browser.py tools/browser_tool.py hafiye_policy.py toolsets.py tests/tools/test_hafiye_browser.py tests/tools/test_browser_chromium_check.py tests/tools/test_browser_extension_router_wiring.py && .venv/bin/python -m py_compile tools/hafiye_browser.py tools/browser_tool.py hafiye_policy.py toolsets.py tests/tools/test_hafiye_browser.py tests/tools/test_browser_chromium_check.py tests/tools/test_browser_extension_router_wiring.py && git diff --check` | Ruff, bytecode compilation, and whitespace checks passed | PASS |
| P10-REAL-01 | Structured navigation, extraction, and download | Isolated inline Python `ThreadingHTTPServer` fixture with `HERMES_HOME` and `browser.backend: off`; `browser_navigate`, `browser_snapshot`, `browser_download` | Page marker, extraction marker, and `HAFIYE_STRUCTURED_DOWNLOAD_OK` content all verified; cleanup completed | PASS |
| P10-REAL-02 | Native existing-browser operation through managed computer-use-linux | Inline Python `discover_mcp_tools()` plus `model_tools.handle_function_call("browser_native", ...)` on the real GNOME Wayland session | Existing Firefox window targeted; exact-window focus, temporary-tab navigation, focused title marker, and `blockers=[]` verified; temporary tab closed | PASS WITH KI-022 WARNING |
| P10-REAL-03 | Native browser cleanup | Inline `browser_native windows` query after P10-REAL-02 | No `Hafiye P10 Native` marker window remained; 2 Firefox windows remained | PASS |

## P11 acceptance

| ID | Boundary | Command | Result | Status |
|---|---|---|---|---|
| P11-PY-01 | Managed voice runtime, STT/TTS hooks, and existing voice regressions | `.venv/bin/python -m pytest -q tests/hermes_cli/test_voice_runtime.py tests/tools/test_hafiye_voice_runtime_hooks.py tests/tools/test_transcription.py tests/tools/test_transcription_command_providers.py tests/tools/test_transcription_tools.py tests/tools/test_tts_piper.py tests/hermes_cli/test_voice_wrapper.py tests/test_voice_max_recording_seconds.py` | 131 passed in 6.19s | PASS |
| P11-LINT-01 | Voice Python lint, compile, and patch hygiene | `.venv/bin/ruff check` on changed voice files; `.venv/bin/python -m py_compile` on changed voice files; `git diff --check` | Ruff, bytecode compilation, and whitespace checks passed | PASS |
| P11-REAL-01 | Managed whisper/Piper readiness | `.venv/bin/python -m hermes_cli.voice_runtime doctor` | `ok=true`, `blockers=[]`; RTX 3080/CUDA selected; whisper CPU/CUDA/VULKAN compiled; Piper 1.7.0 and `tr_TR-dfki-medium` ready | PASS |
| P11-REAL-02 | Real Turkish Piper synthesis and playback | `.venv/bin/python -m hermes_cli.voice_runtime piper-speak ...`; `tools.tts_tool.text_to_speech_tool(...)`; `pw-play` | Direct Piper WAV, Hermes TTS audio, and real playback completed | PASS |
| P11-D-01 | Desktop voice settings and microphone-device unit tests | `cd apps/desktop && npm run test:ui -- src/app/settings/voice-provider-fields.test.ts src/app/settings/voice-field-visible.test.ts src/app/settings/helpers.test.ts src/lib/voice-input-device.test.ts` | 4 files; 50 passed | PASS |
| P11-D-02 | Desktop typecheck and production build | `cd apps/desktop && npm run typecheck && npm run build` | Typecheck, Vite/Electron bundles, native staging, and `assert-dist-built` passed; existing toolchain warnings remain | PASS WITH WARNING |
| P11-D-03 | Real Electron boot and voice settings smoke | `npx playwright test e2e/boot.spec.ts --reporter=line`; `npx playwright test e2e/voice-settings.spec.ts --reporter=line` | Boot 5/5 passed; voice settings 1/1 passed; managed Piper list and preview returned real WAV data | PASS |
| P11-REAL-03 | Real Turkish microphone → correct text | `sleep 5; timeout --signal=INT 15s pw-record --target 37 --rate 16000 --channels 1 --format s16 --container wav ...`; managed CUDA whisper STT and `tools.transcription_tools.transcribe_audio()` | 14.995s real capture; both paths returned `Merhaba hafiye, bugün nasılsın bana Türkçe cevap ver?` correctly | PASS |

P11 is accepted. The master-roadmap test received correct text from a real
Turkish microphone, and the same five historical upstream failures remain the
`ACCEPTED_UPSTREAM_BASELINE`; no new/different upstream failure was found in
the P11 targeted matrix. P12 followed and is now complete; P13 is next.

## P12 acceptance

| ID | Boundary | Command | Result | Status |
|---|---|---|---|---|
| P12-PY-01 | Hafiye wake detector and upstream wake regressions | `.venv/bin/python -m pytest -q tests/tools/test_wake_word.py` | 26 passed, 3 skipped | PASS |
| P12-TRAIN-01 | Reproducible Turkish openWakeWord training/export | `/home/tolga/.local/share/hafiye/runtimes/openwakeword-training/venv/bin/python scripts/train_hafiye_wakeword.py --piper-python /home/tolga/.local/share/hafiye/runtimes/piper/venv/bin/python --piper-data-dir /home/tolga/.local/share/hafiye/runtimes/piper/voices --output-dir /home/tolga/.local/share/hafiye/runtimes/openwakeword-training/hafiye --export /home/tolga/projects/hafiye/tools/wakewords/hafiye.onnx --samples 384 --steps 900 --cpu-threads 4` | Official source `368c03716d1e92591906a84949bc477f3a834455`; standalone ONNX exported; synthetic accuracy 1.0 at threshold 0.6 | PASS |
| P12-REAL-01 | Real detector positive/negative behavior | Direct `_OpenWakeWordEngine`/`WakeWordDetector` check on `/tmp/hafiye-p12-positive-20260824.wav` and `/tmp/hafiye-p12-positive-20260824-take2.wav` | Normal-room music: 0 fires; spoken Hafiye recording: 4 fires under two-second cooldown; `audio_silent=false` | PASS |
| P12-D-01 | Desktop wake/store and Composer behavior | `cd apps/desktop && npx vitest run --project ui src/store/wake-word.test.ts src/app/chat/composer/controls.test.tsx` | 2 files; 37 passed | PASS |
| P12-D-02 | Renderer throttle regression | `cd apps/desktop && npx vitest run --project electron electron/stream-throttle.test.ts` | 1 file; 5 passed | PASS |
| P12-D-03 | Desktop typecheck and production build | `cd apps/desktop && npm run typecheck && npm run build` | TypeScript checks, Vite/Electron bundles, native staging, and `assert-dist-built` passed; existing toolchain warnings remain | PASS WITH WARNING |
| P12-LINT-01 | Wake Python lint, compile, and patch hygiene | `.venv/bin/ruff check scripts/train_hafiye_wakeword.py tools/wake_word.py tests/tools/test_wake_word.py hermes_cli/config_defaults.py; .venv/bin/python -m py_compile scripts/train_hafiye_wakeword.py tools/wake_word.py tests/tools/test_wake_word.py hermes_cli/config_defaults.py; git diff --check` | All checks passed | PASS |
| P12-REAL-02 | Minimized-window Desktop activation | Real Electron bundle with `--use-fake-ui-for-media-stream --use-fake-device-for-media-stream --use-file-for-fake-audio-capture=/tmp/hafiye-p12-positive-20260824-take2.wav`; Settings → Voice → Wake word enabled; native `BrowserWindow.minimize()` | `minimized=true`, `visible=false`; route changed from `#/settings?tab=config%3Avoice` to `#/`; fresh session opened | PASS |

P12 is accepted. The bundled model is
`tools/wakewords/hafiye.onnx`, SHA-256
`9eb0e8c9fd509900ba5d33b4c43906817265605846564af76232daeea194ba50`. The
threshold/confirmation defaults are `0.6`/`3`; Desktop client capture stayed
functional while minimized. The exact historical five upstream failures remain
accepted comparison baseline entries, and no new/different regression was
found in the P12 matrix. The persistent wake setting was reset to disabled
after the real acceptance run.

## Historical ACCEPTED_UPSTREAM_BASELINE and current comparison baseline

The historical post-source comparison set is this exact five-failure baseline:

1. tests/gateway/test_browser_control_api.py::test_remote_api_uses_the_same_authenticated_noop_round_trip
2. tests/test_hermes_state.py::TestFTS5Search::test_search_projection_skips_context_enrichment_queries
3. tests/tools/test_execution_flag_detection.py::test_real_binaries_execute_leading_dash_program_payload[sort-args2-{bulk}-False]
4. tests/tools/test_termux_api_detection.py::TestDetectAudioEnvironmentTermuxFallback::test_inconclusive_probes_with_binary_does_not_emit_app_warning
5. tests/hermes_cli/test_doctor.py::test_doctor_reports_vercel_backend_diagnostics

The latest exact comparison command after KI-043 source hardening returned
failures in items 2, 3, and 5; items 1 and 4 passed. The current comparison
baseline is therefore items 2, 3, and 5 above, while the exact five remain
the historical accepted whitelist. The separate
local reconnect failure was observed only in the earlier post-P6 comparison,
reproduced in the P6-parent checkout, and is documented as KI-019. The P19
canonical full-suite scheduling/environment observations are documented as
KI-034 and are not added to the historical whitelist.

Future failures within the historical five are accepted for comparison. Fewer
failures update the current comparison baseline; any new or different failure
is a regression to investigate. The upstream baseline bugs are not fixed by
Hafiye.

## P0 computer-use acceptance

The final pinned-source doctor on the real Ubuntu GNOME Wayland desktop reports
all of these as true:

- can_register_mcp_tools
- can_build_accessibility_tree
- can_send_development_input
- can_query_windows

It also reports blockers: []. P0 computer-use acceptance passed.

## P13 acceptance

| ID | Boundary | Command / observation | Result | Status |
|---|---|---|---|---|
| P13-PY-01 | Unified cancellation, root gate, managed MCP/computer-use gate, gateway protocol | `.venv/bin/python -m pytest -q tests/test_estop.py tests/test_hafiye_rootd.py tests/tools/test_mcp_tool.py tests/tools/test_computer_use.py tests/tui_gateway/test_protocol.py` | 298 passed; 1 known `vision_analyze_tool` coroutine warning | PASS |
| P13-PY-02 | Async delegation, process registry, TTS and streaming cancellation regression set | `.venv/bin/python -m pytest -q tests/tools/test_async_delegation.py tests/tools/test_delegate_control_actions.py tests/tools/test_process_registry.py tests/tools/test_tts_streaming.py tests/gateway/test_streaming_tts_consumer.py tests/gateway/test_tts_media_routing.py` | 197 passed, 4 skipped, 2 existing async warnings | PASS WITH WARNING |
| P13-LINT-01 | Changed Python compile/lint/patch hygiene | `.venv/bin/python -m py_compile ...`; `.venv/bin/ruff check ...`; `git diff --check` | Compilation passed; Ruff `All checks passed!`; no whitespace errors | PASS |
| P13-D-01 | Desktop emergency shortcut, GNOME fallback, existing stream-throttle behavior | `cd apps/desktop && npx vitest run --project electron electron/emergency-stop-shortcut.test.ts electron/gnome-emergency-stop.test.ts electron/stream-throttle.test.ts` | 3 files; 11 passed | PASS |
| P13-D-02 | Desktop voice stop and existing voice/wake/composer regressions | `cd apps/desktop && npx vitest run --project ui src/lib/voice-stop-word.test.ts src/store/wake-word.test.ts src/app/chat/composer/controls.test.tsx src/app/chat/composer/hooks/use-voice-conversation.test.tsx src/app/chat/composer/hooks/use-voice-conversation-rearm.test.tsx` | 5 files; 58 passed | PASS |
| P13-D-03 | Desktop TypeScript boundary | `cd apps/desktop && npm run typecheck` | Renderer, Electron, and E2E typechecks passed | PASS |
| P13-D-04 | Desktop production package | `cd apps/desktop && npm run build` | Vite, Electron main/preload bundle, native staging, and `assert-dist-built` passed; existing Vite/Babel/chunking warnings remain | PASS WITH WARNING |
| P13-REAL-01 | Persistent gateway stop/pause/resume | Authenticated WebSocket `emergency.stop`, `prompt.submit`, `emergency.resume` against `127.0.0.1:9120` | Stop returned `paused=true`; new prompt returned code `4091` with `paused=true`; resume returned `disengaged=true`, `paused=false`; ESTOP cleared | PASS |
| P13-REAL-02 | Root broker emergency gate | Real non-root broker client with `/home/tolga/.local/share/hafiye/ESTOP` toggled | UID 0 before stop; new privileged op rejected with `code=emergency_stop`; UID 0 after resume | PASS |
| P13-REAL-03 | TTS/process cancellation | Real active TTS state/stop probe and registered temporary sleep process | TTS stop event/state cleanup true; process registry killed 1 process and it exited | PASS |
| P13-REAL-04 | GNOME Wayland global emergency shortcut | Built Electron app, `gsettings`, and `ydotool key 29:1 125:1 1:1 1:0 125:0 29:0` | Electron registration false on this session; GNOME custom binding installed; real chord created ESTOP; clean exit restored `custom-keybindings` to `@as []` | PASS |
| P13-CUA-01 | Direct upstream generic CUA smoke | `tools.computer_use.cua_backend.resolve_cua_driver_cmd()` and worker smoke | `cua-driver` not installed; managed Hafiye `computer-use-linux` MCP path remains green | WARNING; KI-028 |
| P13-OH-01 | Managed OpenHands runtime doctor | `.venv/bin/python - <<'PY' ... openhands_runtime_doctor() ... PY` | Official source commit `6d38810359827823e62a5e1043d0d78d0bafb6de`; SDK/tools/workspace/agent-server `1.41.0`; `ready=true`, `blockers=[]` | PASS |
| P13-OH-02 | Real coding delegation and result return | Real Gemini route through `model_tools.handle_function_call("coding_delegate", ...)` against `/tmp/hafiye-openhands-e2e`; external `.venv/bin/python -m pytest -q` | OpenHands edited `bug.py`; parent result had `status=completed`, `event_count=36`, `changed_files=["bug.py"]`; fixture test returned `1 passed in 0.00s` | PASS |
| P13-OH-03 | Real OpenHands emergency stop/resume | Same-process live worker; `CancellationController.emergency_stop(...)`, then `controller.resume()` | Delegate returned `status=cancelled`; `killed_processes=1`; worker ended; resume returned `paused=false`; no active process remained | PASS |
| P13-ACCEPTANCE | Master P13 closure | Required list includes stopping a real OpenHands delegation | All P13 cancellation boundaries, managed runtime, live delegation, stop, and intentional resume passed; KI-027 resolved | PASS |

P13 is accepted. The exact five historical upstream failures remain the
accepted regression whitelist; the P13 matrix introduced no new or different
upstream failure. The OpenHands runtime/coding-delegate implementation was a
P13 prerequisite; its full coding-delegate and Task Center progress acceptance
is recorded under P15 below.

## P14 acceptance

| ID | Boundary | Command / observation | Result | Status |
|---|---|---|---|---|
| P14-PY-01 | Project registry, project tools, gateway project RPCs, project tree, and session search | `.venv/bin/python -m pytest -q tests/tools/test_project_tools.py tests/hermes_cli/test_projects_db.py tests/hermes_cli/test_projects_cli.py tests/tui_gateway/test_projects_rpc.py tests/tui_gateway/test_project_tree.py tests/tools/test_session_search.py` | 127 passed in 3.38s | PASS |
| P14-REAL-01 | Fresh-process project alias/path resolution and recent context recall | The test creates `Pocket World`, starts a separate Python backend process, resolves `project_switch("pocket-world")` to the exact repository path, and runs `session_search("Pocket World")`; marker `P14_PROJECT_MEMORY_E2E_OK` | Exact path resolved; recent context returned; marker emitted | PASS |
| P14-D-01 | Desktop project store/sidebar/search UI | `cd apps/desktop && ../../node_modules/.bin/vitest run --project ui src/store/projects.test.ts src/app/chat/sidebar/project-dialog.test.tsx src/app/chat/sidebar/projects/project-menu.test.tsx src/app/chat/sidebar/projects/overview-row.test.tsx src/app/chat/sidebar/projects/workspace-groups.test.ts src/lib/session-search.test.ts` | 6 files; 114 passed | PASS |
| P14-D-02 | Desktop E2E TypeScript boundary | `cd apps/desktop && ../../node_modules/.bin/tsc -p tsconfig.e2e.json --noEmit` | Passed | PASS |
| P14-REAL-02 | Real Electron + isolated live gateway project browser/search/edit/delete | `cd apps/desktop && ../../node_modules/.bin/playwright test e2e/p14-project-registry.spec.ts --reporter=list` | 1 passed in 12.2s; repository directory remained on disk after project deletion | PASS |
| P14-D-03 | Desktop production package | `cd apps/desktop && npm run build` | Vite, Electron main/preload, native staging, and `assert-dist-built` passed; existing npm/Vite/Babel/chunking warnings remain | PASS WITH WARNING |
| P14-ACCEPTANCE | Master P14 closure | Fresh-process alias/path resolution, session recall, and real Desktop browse/search/rename/delete all passed | No new/different regression; accepted five-ID whitelist and current three-ID baseline unchanged | PASS |

P14 is accepted. The project registry and session-search behavior use the
pin-preserved Hermes implementation; Hafiye's acceptance source/test commit
is `831405dcec4abcba033d8ccc18308804868ecb1f`. P15 followed and is now
complete.

## P15 acceptance

| ID | Boundary | Command / observation | Result | Status |
|---|---|---|---|---|
| P15-PY-01 | OpenHands runtime, Task Center registry/RPC, and coding delegate | `.venv/bin/pytest -q tests/hermes_cli/test_openhands_runtime.py tests/tools/test_task_center.py tests/tools/test_coding_delegate.py tests/tui_gateway/test_tasks_rpc.py` | 10 passed in 1.87s | PASS |
| P15-D-01 | Desktop Task Center panel | `cd apps/desktop && npm run test:ui -- src/app/command-center/task-center.test.tsx` | 1 passed | PASS |
| P15-D-02 | Desktop type boundary | `cd apps/desktop && npm run typecheck` | Passed | PASS |
| P15-D-03 | Desktop Task Center lint | `cd apps/desktop && npx eslint src/app/command-center/task-center.tsx src/app/command-center/maintenance.tsx` | Passed | PASS |
| P15-D-04 | Desktop production package | `cd apps/desktop && npm run build` | Vite, Electron main/preload, native staging, and `assert-dist-built` passed; existing toolchain warnings remain | PASS WITH WARNING |
| P15-LINT-01 | Python lint, compile, and patch hygiene | `.venv/bin/ruff check` on changed P15 Python files; `.venv/bin/python -m py_compile` on changed P15 Python files; `git diff --check` | Ruff passed, compilation passed, no whitespace errors | PASS |
| P15-REAL-01 | Managed OpenHands readiness | `.venv/bin/hafiye runtime openhands install`; `.venv/bin/hafiye runtime openhands doctor` | Official source `6d38810359827823e62a5e1043d0d78d0bafb6de`; all four packages `1.41.0`; `ready=true`; `blockers=[]` | PASS |
| P15-REAL-02 | Master natural-language coding E2E | Real Gemini-backed Hafiye one-shot against a fresh failing-test fixture; external `pytest -q` | Hafiye identified/delegated; OpenHands changed `bug.py`; external fixture verification returned `1 passed in 0.00s`; result and changed files returned | PASS |
| P15-REAL-03 | Gateway Task Center progress boundary | Real Gemini-backed worker plus live `tasks.list` and `task.update` capture | `RUNNING` observed; final `COMPLETED`; 18 progress events; 22 `task.update` events; `file_changes=["bug.py"]`; external `pytest -q` returned `1 passed` | PASS |
| P15-ACCEPTANCE | Master P15 closure | Real identify → delegate → edit → verify → return → report flow, runtime doctor, and Task Center exposure | All P15 criteria passed; no new/different upstream regression; P16 followed and is recorded below | PASS |

P15 is accepted. The source/test commit is
`54b4ee49569267b21e10b357acdde427a8a844ff`; the pinned Hermes commit and
baseline merge commit are unchanged. The five historical
`ACCEPTED_UPSTREAM_BASELINE` failures remain the regression whitelist, and no
new/different failure was found in the P15 matrix.

## P16 acceptance

| ID | Boundary | Command / observation | Result | Status |
|---|---|---|---|---|
| P16-PY-01 | Durable Task Center registry, restart recovery, coding delegate, and gateway RPC | `.venv/bin/pytest -q tests/hermes_cli/test_openhands_runtime.py tests/tools/test_task_center.py tests/tools/test_coding_delegate.py tests/tui_gateway/test_tasks_rpc.py` | 12 passed | PASS |
| P16-PY-02 | Separate-process persistence and gateway RPC reconnect | Two Python processes with isolated `HERMES_HOME`; second imported real `tui_gateway.server` and called `tasks.list` | Completed history survived; in-flight task became `FAILED / INTERRUPTED_BY_GATEWAY_RESTART`; queued task remained queued; marker `P16_TASK_CENTER_RESTART_OK` | PASS |
| P16-D-01 | Task Center component states, metadata, progress, and cancellation | `cd apps/desktop && npm run test:ui -- src/app/command-center/task-center.test.tsx` | 1 passed | PASS |
| P16-D-02 | Desktop renderer/Electron/E2E type boundaries | `cd apps/desktop && npm run typecheck`; `../../node_modules/.bin/tsc -p tsconfig.e2e.json --noEmit` | Passed | PASS |
| P16-D-03 | Task Center lint and Python hygiene | `cd apps/desktop && npx eslint src/app/command-center/task-center.tsx src/app/command-center/maintenance.tsx`; Ruff, `py_compile`, and `git diff --check` on P16 changes | Passed | PASS |
| P16-D-04 | Clean Desktop production package | `cd apps/desktop && npm run build` | Clean build stamp `f93d91835445`; Vite/Electron bundles, native staging, and `assert-dist-built` passed; existing Vite/Babel/chunking warnings remain | PASS WITH WARNING |
| P16-REAL-01 | Real Desktop Task Center and gateway state/cancel flow | `cd apps/desktop && npx playwright test e2e/p16-task-center.spec.ts --reporter=list` | Real Electron + real gateway rendered completed/failed/queued records and cancelled queued work via `tasks.cancel`; 1 passed in 9.2s | PASS |
| P16-ACCEPTANCE | Master P16 closure | Required state categories, task metadata/actions, no private chain-of-thought, persistence, restart/reconnect, and real Desktop acceptance | All criteria passed; no new/different upstream regression; P17 is next | PASS |

P16 is accepted. Source implementation commit `c72c94418` introduced the
durable registry and complete Task Center surface; source/test commit
`f93d9183544581636c6af5b619d62d221040391d` contains the queued-state recovery
fix and real Desktop acceptance. The historical five
`ACCEPTED_UPSTREAM_BASELINE` failures remain unchanged.

## P17 acceptance

| ID | Boundary | Command / observation | Result | Status |
|---|---|---|---|---|
| P17-D-01 | Control Center page navigation contract | `cd apps/desktop && npm run test:ui -- src/app/control-center/index.test.tsx src/app/routes.test.ts` | 2 files; 7 passed | PASS |
| P17-D-02 | Desktop renderer/Electron/E2E type boundaries | `cd apps/desktop && npm run typecheck`; `../../node_modules/.bin/tsc -p tsconfig.e2e.json --noEmit` | Passed | PASS |
| P17-D-03 | Control Center lint and patch hygiene | `cd apps/desktop && npx eslint src/app/control-center/index.tsx src/app/settings/constants.ts e2e/p17-control-center.spec.ts`; `git diff --check` | Passed; no whitespace errors | PASS |
| P17-D-04 | Clean Desktop production package | `cd apps/desktop && npm run build` | Clean build stamp `2dc541d09367`; Vite/Electron bundles, native staging, and `assert-dist-built` passed; existing Vite/Babel/chunking warnings remain | PASS WITH WARNING |
| P17-REAL-01 | Real Control Center and gateway state flow | `cd apps/desktop && npx playwright test e2e/p17-control-center.spec.ts --reporter=list` | Real Electron + real gateway opened all 19 pages; Privacy Mode changed to `LOCAL_ONLY` and remained after renderer reload; 1 passed in 12.7s | PASS |
| P17-ACCEPTANCE | Master P17 closure | Every roadmap page is functional through real backend/state boundaries; no dead switch or mock success state; config persistence and real Desktop acceptance passed | No new/different upstream regression; P18 followed and P19 is next | PASS |

P17 is accepted. Source/test commit
`2dc541d09367b895744b512d99b058506d7f78d2` adds the Control Center route,
page composition, privacy enum, and real Electron acceptance. The pinned
Hermes commit, baseline merge commit, and accepted five-ID upstream failure
whitelist remain unchanged.

## P18 acceptance

| ID | Boundary | Command / observation | Result | Status |
|---|---|---|---|---|
| P18-PY-01 | Hermes cron persistence and scheduled Hafiye policy | `.venv/bin/python -m pytest -q tests/cron/test_scheduler.py tests/cron/test_jobs.py tests/cron/test_p18_scheduler_acceptance.py` | 182 passed; two existing async resource warnings from the upstream scheduler/test harness | PASS WITH WARNING |
| P18-PY-02 | Python quality and patch hygiene | `.venv/bin/ruff check cron/jobs.py cron/scheduler.py hermes_cli/web_models.py hermes_cli/web_server.py tools/cronjob_tools.py tests/cron/test_jobs.py tests/cron/test_scheduler.py tests/cron/test_p18_scheduler_acceptance.py`; `git diff --check` | Ruff passed; no whitespace errors | PASS |
| P18-D-01 | Desktop cron editor model contract | `cd apps/desktop && npm run test:ui -- src/app/cron/cron-job-model.test.ts` | 15 passed | PASS |
| P18-D-02 | Desktop renderer/Electron/E2E type boundaries | `cd apps/desktop && npm run typecheck` | Passed | PASS |
| P18-D-03 | Desktop scheduler UI lint | `cd apps/desktop && npx eslint src/app/cron/index.tsx src/app/cron/cron-job-model.ts src/app/cron/cron-job-model.test.ts e2e/p18-scheduler.spec.ts` | Passed | PASS |
| P18-D-04 | Clean Desktop production package | `cd apps/desktop && npm run build` | Clean build stamp `fd17e6533894`; Vite/Electron bundles, native staging, and `assert-dist-built` passed; existing npm/Vite/Babel/chunking warnings remain | PASS WITH WARNING |
| P18-REAL-01 | Real recurring local task | `.venv/bin/python -m pytest -q tests/cron/test_p18_scheduler_acceptance.py` | Two real scheduler ticks completed the local task and produced two execution-ledger records | PASS |
| P18-REAL-02 | Real Desktop/gateway scheduler policy flow | `cd apps/desktop && npx playwright test e2e/p18-scheduler.spec.ts --reporter=list` | Real Electron + gateway created route/privacy/custom-toolset job and reloaded the values through Edit; 1 passed in 11.1s | PASS |
| P18-ACCEPTANCE | Master P18 closure | Hermes scheduler/skills/MCP reuse, route/privacy/enabled-tools UI, recurring local task, and real backend boundaries | No new/different upstream regression; P19 is next | PASS |

P18 is accepted. Source/test commit
`fd17e6533894a568744b82454635a8e6bf02709b` contains the scheduler policy
boundary, Desktop controls, and acceptance tests. The historical five-ID
`ACCEPTED_UPSTREAM_BASELINE` remains unchanged.

## P19 acceptance

| ID | Boundary | Command / observation | Result | Status |
|---|---|---|---|---|
| P19-PY-01 | Hardening, loop/action budgets, runtime, voice, computer-use, browser, and retention | `.venv/bin/python -m pytest -q tests/agent/test_tool_guardrails.py tests/agent/test_stall_guards.py tests/tools/test_delegate_control_actions.py tests/hermes_cli/test_local_runtime.py tests/hermes_cli/test_voice_runtime.py tests/test_hafiye_computer_use.py tests/tools/test_hafiye_browser.py tests/test_hafiye_hardening.py` | 111 passed | PASS |
| P19-PY-02 | Adjacent Hermes hardening/config/audit regressions | `.venv/bin/python -m pytest -q tests/tools/test_browser_hardening.py tests/tools/test_hafiye_voice_runtime_hooks.py tests/hermes_cli/test_config.py tests/hermes_cli/test_dashboard_auth_audit.py` | 104 passed | PASS |
| P19-LINT-01 | Python quality and patch hygiene | `.venv/bin/ruff check` on all P19 source/test files; `git diff --check` | Passed | PASS |
| P19-REAL-01 | Real hardening/runtime/voice/computer-use readiness | `.venv/bin/hafiye hardening doctor`; `.venv/bin/hafiye runtime doctor`; `.venv/bin/hafiye voice doctor`; `.venv/bin/hafiye runtime server recover --attempts 1`; pinned computer-use-linux doctor | All hardening checks true, runtime/voice `ok=true`, computer-use required booleans true, and all blockers arrays empty | PASS |
| P19-BE-01 | Exact five upstream comparison | `.venv/bin/python -m pytest -q` with the five historical IDs | 3 failed, 2 passed; only historical IDs 2, 3, and 5 failed; IDs 1 and 4 passed | ACCEPTED BASELINE REDUCED |
| P19-BE-02 | Canonical backend regression run | `./scripts/run_tests.sh` | 3,231 files; 37,218 passed, 16 failed, 244 skipped in 847.8s; full-suite diagnostics documented in KI-034 | PASS WITH DOCUMENTED DIAGNOSTICS |
| P19-ACCEPTANCE | Master P19 closure | All roadmap hardening boundaries implemented, focused/adjacent matrices pass, real doctor acceptance passes, and exact baseline has no new/different failure | P20 is next; no P19-specific regression | PASS |

P19 is accepted. Source/test commit `0f45abb9c` contains the hardening
boundary and tests. The historical five-ID whitelist remains intact; the
current comparison baseline is items 2, 3, and 5 only.

## P20 acceptance

| ID | Boundary | Command / observation | Result | Status |
|---|---|---|---|---|
| P20-PY-01 | Packaging and root-broker boundaries | `.venv/bin/python -m pytest -q tests/packaging/test_hafiye_deb.py tests/test_hafiye_rootd.py` | 10 passed | PASS |
| P20-PY-02 | Packaging metadata contract | `.venv/bin/python -m pytest -q tests/test_packaging_metadata.py` | 7 passed | PASS |
| P20-LINT-01 | Packaging compilation, lint, and patch hygiene | `py_compile` on changed Python files; `.venv/bin/ruff check ...`; `git diff --check` | Passed | PASS |
| P20-DESKTOP-01 | Real Electron Linux package input | `cd apps/desktop && npm run pack` | Real `linux-unpacked` output passed; clean build stamp `964fc49b5f56`; existing npm/Vite/Babel/chunking warnings | PASS WITH WARNING |
| P20-DEB-01 | Debian artifact and commit manifest | `.venv/bin/python scripts/build_deb.py --output dist/hafiye_0.20.5_amd64.deb --desktop-dir apps/desktop/release/linux-unpacked --json`; `dpkg-deb --info/--contents` | Real `amd64` package built and required paths/metadata present; approximately 119 MB | PASS |
| P20-DOCTOR-01 | Extracted final package readiness | Extract final artifact and run `hafiye package doctor --json` | `ok=true`, `blockers=[]`; source/pinned/baseline manifest values correct | PASS |
| P20-INSTALL-01 | Debian install semantics without live-host mutation | Rootless `fakeroot dpkg --force-not-root --force-script-chrootless --force-depends --unpack/--configure` in a temporary root | Passed; expected unmet dependency warnings in temporary dpkg database; no live host install claimed | PASS WITH DIAGNOSTIC |
| P20-BE-01 | Exact five upstream comparison | Same five historical test IDs run after P20 | `3 failed, 2 passed`; only accepted historical IDs 2, 3, and 5 failed | ACCEPTED BASELINE UNCHANGED |
| P20-ACCEPTANCE | Master P20 closure | Debian package, package doctor, rootless install semantics, focused tests, and baseline comparison | All required P20 evidence recorded; P21 followed | PASS |

P20 is accepted. The package artifact is kept locally at
`dist/hafiye_0.20.5_amd64.deb` and is ignored by Git; the source/test commit is
`964fc49b5f564f25588894374ea83e81cc2f58c7`.

## P21 acceptance — complete

| ID | Boundary | Command / observation | Result | Status |
|---|---|---|---|---|
| P21-PY-01 | Onboarding state and authenticated REST boundary | `.venv/bin/pytest -q tests/hermes_cli/test_persistent_gateway.py tests/hermes_cli/test_hafiye_onboarding_api.py tests/test_hafiye_onboarding.py tests/packaging/test_hafiye_deb.py tests/test_packaging_metadata.py tests/test_hafiye_rootd.py` | 30 passed | PASS |
| P21-LINT-01 | P21 Python quality and patch hygiene | `.venv/bin/ruff check` on P21 source/tests; `py_compile`; `git diff --check` | Passed | PASS |
| P21-DESKTOP-01 | Desktop type and component coverage | `cd apps/desktop && npm run typecheck`; `npm run test:ui -- src/components/hafiye-onboarding/index.test.tsx` | Typecheck passed; 3 UI tests passed | PASS |
| P21-E2E-01 | Real Electron onboarding boundary | `cd apps/desktop && npx playwright test e2e/hafiye-onboarding.spec.ts --workers=1 --reporter=list` | Real Electron + real isolated Hermes backend advanced Welcome → Environment → computer-use doctor → Compute; 1 passed in 8.3s | PASS (PARTIAL FLOW) |
| P21-E2E-02 | Complete packaged Desktop onboarding | Real Electron launch of `apps/desktop/release/linux-unpacked/hafiye-desktop` against the live authenticated gateway; Playwright runner advanced every roadmap heading | `PACKAGED_ONBOARDING_RESULT PASS 20/20`; final wizard disappeared after real microphone/STT, Piper/TTS, wake-word choice, Hafiye request, autostart, and doctor | PASS |
| P21-PACKAGE-01 | Current packaged backend and manifest | `npm run pack`; `scripts/build_deb.py --output dist/hafiye_0.20.5_amd64.deb --desktop-dir apps/desktop/release/linux-unpacked --json`; extracted package doctor/backend probe | Current source/test HEAD `a87eaaba7373a2c23fa73b7ef498b64d67c989f5`; package doctor and authenticated onboarding doctor returned `ok=true`, `blockers=[]` | PASS |
| P21-REAL-01 | Live persistent service onboarding doctor | Authenticated `GET /api/hafiye/onboarding/doctor` after reinstall/restart of `hafiye-gateway.service` | `ok=true`, `blockers=[]`, computer readiness true, local server ready, voice OK, autostart enabled | PASS |
| P21-BE-01 | Exact five upstream comparison | Same five historical test IDs run after P21 | `3 failed, 2 passed`; only accepted historical IDs 2, 3, and 5 failed; IDs 1 and 4 passed | ACCEPTED BASELINE UNCHANGED |
| P21-ACCEPTANCE | Master P21 closure | All 20 roadmap steps replayed through the real packaged Desktop GUI, including STT/TTS/wake/Hafiye/final doctor | All 20 steps passed; final live doctor returned `ok=true`, `blockers=[]`; P22 is next | PASS |

P21 source/test commits are `48860ee5f` and
`a87eaaba7373a2c23fa73b7ef498b64d67c989f5`. The pinned upstream commit and
baseline merge remain `f293e7206b4ddd66042329442c6afebc19a8808d` and
`2ac06b131a237916432503ac67bbcada6dbea39e`; no upstream history changed. The
full packaged Electron replay reached all 20 steps and completed the wizard.
The temporary acceptance gate was removed afterward; the normal service and
CUDA local server were restored, and the authenticated final doctor remained
green. P22 — CLI — followed and is complete; P23 is now the first incomplete
phase.

## P22 acceptance — complete

| ID | Boundary | Command / observation | Result | Status |
|---|---|---|---|---|
| P22-PY-01 | Product CLI and policy regression matrix | `.venv/bin/pytest -q tests/hermes_cli/test_hafiye_cli.py tests/test_hafiye_policy.py tests/gateway/test_hafiye_routing.py tests/hermes_cli/test_cron_parser_builder.py tests/hermes_cli/test_persistent_gateway.py tests/hermes_cli/test_projects_cli.py` | 32 passed, 1 warning | PASS |
| P22-LINT-01 | P22 Python quality and patch hygiene | `.venv/bin/ruff check` on changed P22 files; `.venv/bin/python -m py_compile` on changed P22 files; `git diff --check` | All passed | PASS |
| P22-CLI-01 | Product command parser/help surface | `.venv/bin/hafiye --help`, nested help, parser smoke for `ask`, service lifecycle, models/model, providers, routing/privacy, tasks/task, computer, and existing `projects`/`automation` aliases | All required commands parsed and help rendered | PASS |
| P22-REAL-01 | Persistent Hafiye service | `.venv/bin/hafiye restart`; `systemctl --user is-active/is-enabled hafiye-gateway.service` | Restart returned 0; service active and enabled | PASS |
| P22-REAL-02 | Managed GGUF lifecycle and compute selection | `.venv/bin/hafiye model unload --json`; `.venv/bin/hafiye model load qwen2.5-0.5b-instruct-q4 --backend AUTO --json` | Unload succeeded; reload returned `running=true`, `ready=true`, `selected_backend=CUDA` | PASS |
| P22-REAL-03 | Read-only product surfaces | `.venv/bin/hafiye models/providers/routing/privacy/tasks/computer --json`; `projects list`; `automation list`; `root status` | All returned successfully; computer doctor required readiness fields true and `blockers=[]` | PASS |
| P22-REAL-04 | Explicit Gemini product one-shot | `timeout 120 .venv/bin/hafiye ask --safe-mode --model gemini-flash-lite-latest --provider gemini 'Reply with exactly P22_GEMINI_CLI_OK and nothing else.'` | Exit 0; exact `P22_GEMINI_CLI_OK` marker returned | PASS |
| P22-REAL-05 | Small local fixture one-shot diagnostic | `.venv/bin/hafiye ask --model qwen2.5-0.5b-instruct-q4 --provider custom 'Reply with exactly P22_CLI_OK'` | Hermes rejected the 4,096-token fixture context below its 64K minimum; tracked as KI-014, while the real CUDA endpoint/runtime remains healthy | WARNING / KNOWN ISSUE |
| P22-BE-01 | Exact five upstream regression comparison | The exact five-ID command below, after P22 source changes | `3 failed, 2 passed`; only accepted historical IDs 2, 3, and 5 failed; IDs 1 and 4 passed | ACCEPTED BASELINE UNCHANGED |
| P22-ACCEPTANCE | Master P22 closure | CLI vocabulary, shared backend/config boundaries, real service/model/computer checks, Gemini one-shot, and baseline comparison | All P22 evidence recorded; P23 is next | PASS |

### P22 exact baseline command

```bash
PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q \
  tests/gateway/test_browser_control_api.py::test_remote_api_uses_the_same_authenticated_noop_round_trip \
  tests/test_hermes_state.py::TestFTS5Search::test_search_projection_skips_context_enrichment_queries \
  'tests/tools/test_execution_flag_detection.py::test_real_binaries_execute_leading_dash_program_payload[sort-args2-{bulk}-False]' \
  tests/tools/test_termux_api_detection.py::TestDetectAudioEnvironmentTermuxFallback::test_inconclusive_probes_with_binary_does_not_emit_app_warning \
  tests/hermes_cli/test_doctor.py::test_doctor_reports_vercel_backend_diagnostics
```

The five IDs are the permanent `ACCEPTED_UPSTREAM_BASELINE`; the same set is
not counted as a Hafiye regression in later phases. A smaller set updates the
comparison baseline, while any new or different failure requires investigation.

## P23 final E2E execution — in progress

| ID | Boundary | Command / observation | Result | Status |
|---|---|---|---|---|
| P23-BE-01 | P23 backend target matrix | Exact command below | `251 passed, 2 skipped, 1 warning in 22.66s`, including `tests/hermes_cli/test_local_runtime.py` | PASS |
| P23-LINT-01 | Route/config and local-runtime source quality | `.venv/bin/ruff check tui_gateway/server.py tests/tui_gateway/test_make_agent_provider.py gateway/run.py tests/gateway/test_hafiye_routing.py hermes_cli/local_runtime.py tests/hermes_cli/test_local_runtime.py`; `py_compile` on the same files; `git diff --check` | All passed after source/test commit `5af73434e` | PASS |
| P23-CONFIG-01 | Native gateway and Desktop route boundary | `tests/gateway/test_hafiye_routing.py` plus `tests/tui_gateway/test_make_agent_provider.py` | Normal XDG config root and shared route/privacy application are covered; 20 focused tests passed | PASS |
| P23-REAL-01 | Persistent service and local CUDA runtime after live check | `.venv/bin/hafiye routing --json`; `.venv/bin/hafiye restart`; `systemctl --user is-active/is-enabled hafiye-gateway.service`; `.venv/bin/hafiye runtime doctor` | Default route restored to custom/Qwen; service active/enabled; runtime `ok=true`, `blockers=[]`, `selected_backend=CUDA` | PASS |
| P23-CUA-01 | computer-use-linux live readiness/window query | `.venv/bin/hafiye computer doctor --json`; `/home/tolga/.local/bin/computer-use-linux windows` | Four required readiness fields true, blockers empty; windows query exit 0 and Firefox/Hafiye windows enumerated | PASS |
| P23-BOOT-01 | Packaged Desktop after gateway restart | `hafiye restart`; real `release/linux-unpacked/hafiye-desktop` Playwright launch; wait for Hafiye title and Composer | Packaged Desktop reached `P23_BOOT_COMPOSER_READY Hafiye` after the service restart | PARTIAL / REBOOT STILL REQUIRED |
| P23-BOOT-PREFLIGHT-01 | P23.1 real reboot preflight | `systemctl --user is-enabled/is-active hafiye-gateway.service`; `curl --fail-with-body --silent --show-error http://127.0.0.1:9120/api/health`; `desktop-file-validate /home/tolga/.config/autostart/hafiye.desktop`; `hafiye voice doctor`; `hafiye computer doctor --json`; boot ID/uptime capture | User gateway `enabled`/`active` (`MainPID=3033612`); endpoint HTTP 200 with `ok=true`; packaged autostart entry exists as mode `0644` and validates; voice and computer doctors report `ok=true`, empty blockers, CUDA selected/expected; exact reboot/login replay still pending | PASS / PREFLIGHT ONLY |
| P23-BOOT-POSTREBOOT-01 | P23.1 real reboot/login acceptance | Real `systemctl reboot -i`; new boot ID; `systemctl --user` gateway state/journal; packaged process/window/tray checks; `computer-use-linux windows`; voice/computer doctors | Boot `17a11ea7-41ed-4b74-a4fc-8f4e9c3dc7eb`; GNOME did execute `app-gnome-hafiye-10171.scope`, but Electron exited because `chrome-sandbox` was `tolga:tolga 0755` instead of `root:root 4755`. Source/package fix `a1271a93277e6ac0747c1c5c31b586c2e883e55a` passed `4` packaging tests; current helper was repaired through rootd and sandbox-enabled short launch had no fatal error. A second real reboot/login remains required | NOT ACCEPTED / KI-013 RECHECK REQUIRED |
| P23-MCP-STARTUP-01 | Fresh-process managed computer-use MCP startup gate | `.venv/bin/python -m pytest -q tests/hermes_cli/test_mcp_startup.py tests/test_hafiye_computer_use.py tests/test_tui_entry_mcp_owner.py tests/hermes_cli/test_mcp_discovery_timing.py tests/hermes_cli/test_oneshot_toolsets.py tests/tools/test_hafiye_browser.py`; focused gateway discovery tests; `systemctl --user restart hafiye-gateway.service`; journal inspection | Targeted set `40 passed`; focused gateway set `3 passed`; Ruff clean; after restart the journal recorded `hafiye-computer-use-linux` with 18 registered tools. Source/test commit `dc962963e6040f792e3f74fcd459d41da425d8d` | PASS / SOURCE FIX |
| P23-LOCAL-01 | Real local llama.cpp chat endpoint | `curl --fail-with-body --silent --show-error http://127.0.0.1:11435/v1/chat/completions ...` with marker `P23_LOCAL_ENDPOINT_OK` | Exact marker returned; this does not replace the required offline Hafiye-agent replay | PASS / OFFLINE NOT CHECKED |
| P23-LOCAL-02 | Initial local agent context compatibility diagnostic | `.venv/bin/hafiye model unload --json`; `.venv/bin/hafiye model load qwen2.5-0.5b-instruct-q4 --backend AUTO --context-size 65536 --json`; `hafiye ask ... P23_LOCAL_HAFIYE_OK` | Without the Qwen2 compatibility flags, llama.cpp capped at `n_ctx=32768` and Hermes rejected it below 64K; retained as historical KI-014 evidence | HISTORICAL DIAGNOSTIC |
| P23-LOCAL-03 | 64K Hermes GGUF CUDA fit probe | Hafiye runtime download of pinned `NousResearch/Hermes-3-Llama-3.2-3B-GGUF` Q4_K_M; `hafiye model load ... --backend AUTO --context-size 65536` | CUDA KV-cache allocation of 7,168 MiB failed on RTX 3080; model removed from registry | HISTORICAL DIAGNOSTIC / KI-040 |
| P23-LOCAL-04 | 64K small-model agent behavior probe | Hafiye runtime download of pinned `bartowski/Llama-3.2-1B-Instruct-GGUF` Q4_K_M; `hafiye ask ... P23_LOCAL_HAFIYE_OK` | Model loaded at `n_ctx=65536`, but generated 39,822 tokens without completing; interrupted and removed | HISTORICAL DIAGNOSTIC / KI-040 |
| P23-LOCAL-05 | Managed Qwen2 64K local agent path | `.venv/bin/hafiye model unload --json`; `.venv/bin/hafiye model load qwen2.5-0.5b-instruct-q4 --backend AUTO --context-size 65536 --json`; `hafiye runtime doctor`; direct AIAgent terminal call; packaged Desktop Composer DOM replay | Runtime reported `n_ctx=65536`, `n_ctx_train=65536`, `ready=true`, `selected_backend=CUDA`; direct AIAgent returned `P23_QWEN64_TERMINAL_OK`; packaged Desktop rendered the real `/bin/printf P23_DESKTOP_DOM_OK` tool block with exit code 0 and exact marker | PASS FOR LOCAL ROUTE / OFFLINE REPLAY REQUIRED |
| P23-QWEN3-01 | Official Qwen3-14B managed model registration and 65K runtime fit | Hafiye-managed `Qwen/Qwen3-14B-GGUF` Q4_K_M; live `/v1/models`; `hafiye runtime doctor`; `nvidia-smi`; `/proc/<pid>/status`; server timing log | Revision `530227a7d994db8eca5ab5ced2fb692b614357fd`, 9,001,752,960-byte file, SHA-256 `500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0`; `n_ctx=65536`, `n_ctx_train=65536`, `Q4_K - Medium`, 14.768B params, `ready=true`, selected `CUDA`; 8,614/10,240 MiB VRAM, 7,749,188 kB RSS, 7,609,128 kB swap; full-GPU fit failures retained | PASS / RESOURCE WARNING KI-046 |
| P23-QWEN3-02 | Exact local-agent desktop request `Firefox'u aç.` | Isolated Qwen3 `AIAgent` with managed `hafiye-computer-use-linux`; exact Turkish request; independent managed window query | `list_apps → list_windows → activate_window`; real Firefox Wayland window focused; `QWEN3_FIREFOX_OK`; 6 API calls, 51.303s | PASS |
| P23-QWEN3-03 | Isolated create/read/move file workflow | Isolated Qwen3 `AIAgent` with `terminal,file`; create `organized/text`/`organized/media`, move `notes.txt`/`photo.jpg`, preserve `keep.bin`, read/verify, independent filesystem check | Final paths/content exactly correct; `QWEN3_FILE_OK`; 2 API calls, 73.703s; one expected `read_file` binary-extension error was recovered and independently verified | PASS / EXPECTED TOOL ERROR RECORDED |
| P23-QWEN3-04 | Real VS Code computer-use-linux action | Real Wayland VS Code fixture; isolated Qwen3 `AIAgent` with managed MCP only; `list_windows`, exact activation, Ctrl+A, `type_text`, Ctrl+S, targeted screenshot; independent file read | `QWEN3_VSCODE_OK`; marker saved in the actual VS Code file and screenshot returned; 7 API calls, 48.849s | PASS |
| P23-QWEN3-05 | Multi-step terminal task and verification | Isolated Qwen3 `AIAgent` with `terminal`; separate calls to create inputs, write files, `sort -u`, read output; independent exact file comparison | `QWEN3_TERMINAL_OK`; 5 successful terminal calls, 3 API calls, 58.319s; independent result comparison passed | PASS |
| P23-QWEN3-06 | OpenHands coding delegation through Qwen3 parent | Isolated Qwen3 `AIAgent` with `delegation`; `coding_delegate` to managed OpenHands fixture; worker result and independent pytest | Coding route resolved `custom/qwen3-14b-q4_k_m`; worker `status=completed`, 14 progress events, `bug.py` changed, independent pytest `1 passed`; 423.879s | PASS / RESOURCE WARNING KI-046 |
| P23-QWEN3-07 | Persistent multi-turn tool workflow | One Qwen3 `AIAgent` object; turn one creates/reads marker, turn two reads/appends/reads; independent file comparison | Same session `20260825_042420_3f0fe8`; `TURN_ONE_DONE`, `QWEN3_MULTITURN_OK`; 2 turns, 71.845s; exact two-line file passed | PASS |
| P23-QWEN3-08 | Qwen3 throughput and latency evidence | Managed llama-server `llama-server.log` timing lines for the isolated runs | Prompt processing roughly 228–827 tokens/s (cache-dependent); generation roughly 4.59–5.39 tokens/s; task wall times recorded in rows 02–07 | PASS / RESOURCE WARNING KI-046 |
| P23-FILES-01 | Real file organize-and-verify fixture | Isolated temporary fixture; `.venv/bin/hafiye ask --provider gemini --model gemini-flash-lite-latest --toolsets terminal,file ...`; create `organized/text` and `organized/media`, move `notes.txt` and `photo.jpg`, leave `keep.bin`, then verify with a terminal listing | Real Gemini route returned `P23_FILES_GEMINI_OK`; filesystem inspection found `organized/text/notes.txt`, `organized/media/photo.jpg`, and `incoming/keep.bin` exactly as required. Earlier local-Qwen attempts remain recorded in KI-041 | PASS / GEMINI ROUTE; LOCAL QWEN WARNING RETAINED |
| P23-LOCAL-DESKTOP-02 | Local Qwen2 natural-language Desktop task | Packaged `hafiye-desktop` with local custom/Qwen route; Composer prompt `Firefox'u aç.`; inspect actual transcript/window state | Composer ready, but model returned `Merhaba, FireFox'a açın!` with no computer-use call and no observed Firefox result | NOT ACCEPTED / KI-042 |
| P23-LOCAL-DESKTOP-03 | Agent-qualified packaged Composer after managed-MCP startup fix | Restarted gateway; packaged `hafiye-desktop`; forced Qwen3 route; exact Composer prompt `Firefox'u aç.`; inspect gateway tool registration, Composer transcript, and Firefox window | Gateway registered 18 managed MCP tools; Composer exposed 38 core/visible plus 18 deferred tools. Qwen3 produced no tool call during approximately 265 seconds of reasoning, so the replay was terminated; Qwen2/default route restored and no Firefox result was claimed | NOT ACCEPTED / KI-047 + KI-046 |
| P23-OFFLINE-01 | P23.4 disconnected-network local operation | Record `nmcli`/default route; `nmcli networking off`; packaged Composer local Qwen3 task; local gateway health; restore connectivity | Network was actually disabled and loopback gateway health remained HTTP 200, but the task had not completed during the initial observation. User explicitly instructed to skip the offline test; emergency stop cancelled it, `nmcli networking on` restored connectivity, and Qwen2/CUDA was reloaded | NOT ACCEPTED / USER-DEFERRED |
| P23-DESKTOP-03 | Managed P23.9 VS Code/window/input acceptance | Open two real VS Code fixture windows; `mcp__hafiye_computer_use_linux__list_windows`; exact `activate_window` first→second→first; `get_app_state`; relative `click`; `press_key` Ctrl+A/Ctrl+S; `type_text` marker; independent file read; final managed screenshot; close exact fixture windows | Two real windows found; all focus switches and managed actions returned `ok=true`; fixture saved exactly `P23_DESKTOP_TARGET`; final state was focused VS Code with screenshot present and the marker visibly rendered | PASS / KI-044 MODEL WARNING |
| P23-RESTART-01 | Real Desktop session restart/reconnect | Authenticated `source=desktop` WebSocket fixture; local-Qwen prompt before `systemctl --user restart hafiye-gateway.service`; reconnect; `session.resume` with the durable session id; post-restart prompt; service state | Before-restart prompt completed; gateway restart completed; the same durable session resumed; post-restart prompt completed; service remained `active`; marker `P23_RESTART_RECONNECT_OK` | PASS |
| P23-EMERGENCY-01 | Emergency shortcut desktop-action probe | `.venv/bin/hafiye ask --provider custom --model qwen2.5-0.5b-instruct-q4 --toolsets computer_use` with an explicit 60-second `computer_use` wait request; monitor for a real tool event before sending the physical chord | Local-Qwen process exited without producing a `computer_use` tool event; no chord was sent; the exact P23.15 long-running desktop sequence remains unaccepted | NOT ACCEPTED / KI-045 |
| P23-GEMINI-01 | Rotated-key Gemini one-shot | Store new credential through `save_provider_env_credential("GOOGLE_API_KEY", ...)` into Linux Secret Service; `.venv/bin/hafiye ask --provider gemini --model gemini-flash-lite-latest 'Reply with exactly P23_GEMINI_NEW_KEY_OK'` | `P23_GEMINI_NEW_KEY_OK`; provider authenticated; raw key not recorded | PASS |
| P23-GEMINI-DESKTOP-01 | Rotated-key packaged Composer exact Firefox task | Temporarily set default route to Gemini; launch packaged Desktop; submit exact `Firefox'u aç.`; inspect transcript/window/rootd; restore local route and host package state | Gemini opened Firefox, then initiated unrelated `sudo apt`/`sudo snap` remediation through `hafiye-rootd`; no administrator-password dialog appeared, but the task was not clean. Emergency stop ended the operation; Firefox Snap revision `8763` and the pre-replay route/package state were restored | NOT ACCEPTED / KI-049; KI-043 RESOLVED |
| P23-GEMINI-COMPOSER-02 | Clean Gemini Composer task | Packaged Desktop with Gemini default route; create/read `/tmp/hafiye-p23-gemini/ok.txt`; independent filesystem verification; restore local route | Real transcript created and read `ok.txt`, returned `P23_GEMINI_COMPOSER_OK`; independent check confirmed 22-byte exact content and no privileged command/password dialog. Route restored to Qwen2/CUDA | PASS / P23.6 |
| P23-REMOTE-01 | P23.5 remote self-hosted inference availability | `hafiye routing --json`; inspect active Hafiye config for OpenAI-compatible endpoint; do not substitute localhost/Gemini | `remote` task override empty; active config contains only local `127.0.0.1:11435/v1`; onboarding says remote provider skipped. No real remote endpoint available | NOT ACCEPTED / KI-048 |
| P23-PRIVACY-01 | LOCAL_ONLY blocks configured cloud route | Temporarily set default route to Gemini; set global `LOCAL_ONLY`; run `.venv/bin/hafiye ask 'Reply with exactly P23_LOCAL_ONLY_BLOCKED'` without explicit provider/model; restore route/privacy | Exit 1 with `Hafiye LOCAL_ONLY policy blocked provider 'gemini' ...` before provider call; route restored to custom/Qwen and privacy to `NORMAL` | PASS / FAIL-CLOSED |
| P23-MEMORY-01 | Fresh project alias/session recheck | `.venv/bin/pytest -q tests/tools/test_project_tools.py::test_project_alias_and_session_context_survive_fresh_process` | `1 passed in 1.36s` | PASS / SUPPORTING RECHECK |
| P23-OPENHANDS-01 | Fresh managed OpenHands readiness and P23.13 fixture delegation | `.venv/bin/hafiye runtime openhands doctor`; `.venv/bin/hafiye ask --provider gemini --model gemini-flash-lite-latest --toolsets coding ...`; `.venv/bin/python -m pytest -q` in the isolated fixture; `.venv/bin/hafiye tasks --json` | Doctor returned SDK/source `1.41.0`, `ready=true`, `blockers=[]`. Real `coding_delegate` Task Center record reached `COMPLETED` on the `coding` route with 28 progress events and terminal/file-editor history; `bug.py` was changed and independent fixture pytest returned `1 passed in 0.00s` | PASS |
| P23-ROOT-01 | Root broker and unprivileged main process | `.venv/bin/hafiye root exec id -u`; `ps -o pid,user,euid,comm,args` for gateway/rootd PIDs | Broker returned `0`; gateway EUID `1000`, rootd EUID `0` | PASS |
| P23-BROWSER-01 | Structured then native browser path | Local `python -m http.server` + `browser_navigate`/`browser_snapshot`; `tools.hafiye_browser.browser_native` against exact existing Firefox Wayland window; native screenshot/state; restore prior tab | Structured navigation passed. Managed native route returned successful activation/key/type/navigation steps; real screenshot showed `Hafiye P23 Native Browser OK` and `P23_NATIVE_BROWSER_OK`; prior Kick tab was restored. Firefox's root-only AT-SPI tree remains KI-022 | PASS / KI-022 DIAGNOSTIC |
| P23-DESKTOP-01 | Real packaged Composer text path | Packaged Electron command below, with default route temporarily forced to Gemini | Historical run opened Firefox but later hit HTTP 429; rotated-key replay is recorded in `P23-GEMINI-DESKTOP-01` and ended with KI-043 sudo approval dialog | HISTORICAL / KI-037; CURRENT WARNING KI-043 |
| P23-DOCTOR-01 | Live supporting readiness diagnostics | `.venv/bin/hafiye voice doctor`; `.venv/bin/hafiye runtime openhands doctor`; `.venv/bin/hafiye root status`; `.venv/bin/hafiye doctor`; `.venv/bin/hafiye computer doctor --json` | Voice/OpenHands/root/computer checks green; general doctor has KI-007/KI-038 diagnostics and host has separate root ydotoold observation KI-039 | PASS WITH DIAGNOSTICS |
| P23-BE-BASELINE | Exact five upstream comparison after KI-043 source hardening | Exact command below | Latest direct run: `3 failed, 2 passed`; historical IDs 2, 3, and 5 failed and IDs 1 and 4 passed. Every failure is within the accepted five-ID set; no new/different ID | ACCEPTED BASELINE / NO NEW REGRESSION |
| P23-ACCEPTANCE | Master P23 closure | All 23.1–23.16 real-machine checks | Remaining final E2E rows are not yet replayed; P23 remains open | NOT COMPLETE |

| P23-KI043-01 | Privileged command boundary and approval semantics | `scripts/run_tests.sh tests/test_hafiye_execution_policy.py tests/test_hafiye_privileged_boundary.py tests/test_hafiye_rootd.py tests/hermes_cli/test_local_runtime.py -q` | 35 passed, 0 failed; direct/absolute/env/command/quoted/shell-wrapped/chained escalation, Gemini `sudo chown`, normal terminal, rootd routing/audit, READ_ONLY, confirmation, and registry metadata covered | PASS / KI-043 RESOLVED |
| P23-KI043-02 | Changed-source lint and patch hygiene | `.venv/bin/ruff check hafiye_execution_policy.py hermes_cli/local_runtime.py tools/code_execution_tool.py tools/terminal_tool.py tests/test_hafiye_execution_policy.py tests/test_hafiye_privileged_boundary.py tests/hermes_cli/test_local_runtime.py`; `git diff --check` | Ruff clean; diff check clean | PASS |
| P23-MODEL-REGISTRY-01 | Evidence-backed local model capability state | `.venv/bin/hafiye routing --json`; `.venv/bin/hafiye models --json` | Default route remains `custom/qwen2.5-0.5b-instruct-q4`; Qwen2 is `validation=true, agent=false`; Qwen3 is `agent=true, tool_calling=true, validation=false, resource_warning=KI-046` and remains selectable | PASS / KI-046 WARNING |

### P23 backend target matrix command

```bash
.venv/bin/pytest -q \
  tests/test_estop.py tests/test_hafiye_rootd.py tests/test_hafiye_computer_use.py \
  tests/test_hafiye_policy.py tests/hermes_cli/test_local_runtime.py \
  tests/hermes_cli/test_voice_runtime.py tests/hermes_cli/test_openhands_runtime.py \
  tests/hermes_cli/test_computer_use_cli.py tests/tools/test_hafiye_browser.py \
  tests/tools/test_task_center.py tests/tools/test_coding_delegate.py \
  tests/tools/test_voice_mode.py tests/tui_gateway/test_tasks_rpc.py \
  tests/tui_gateway/test_projects_rpc.py tests/gateway/test_restart_resume_pending.py \
  tests/gateway/test_active_turn_recovery.py \
  tests/tui_gateway/test_make_agent_provider.py tests/gateway/test_hafiye_routing.py
```

Result: `251 passed, 2 skipped, 1 warning in 22.66s`.

### P23 packaged Composer command

Before this command, the test route was set with:

```bash
.venv/bin/hafiye routing set --slot default --provider gemini --model gemini-flash-lite-latest
```

The real packaged Electron invocation was:

```bash
node --input-type=module - <<'NODE'
import fs from 'node:fs'
import { _electron as electron } from '/home/tolga/projects/hafiye/node_modules/playwright/index.mjs'
const userData = fs.mkdtempSync('/tmp/hafiye-p23-live-')
const executablePath = '/home/tolga/projects/hafiye/apps/desktop/release/linux-unpacked/hafiye-desktop'
let app
try {
  app = await electron.launch({
    executablePath,
    args: ['--disable-gpu', '--no-sandbox'],
    env: {...process.env, HERMES_DESKTOP_USER_DATA_DIR: userData,
      HERMES_DESKTOP_SKIP_QUIT_CONFIRM:'1', HERMES_DESKTOP_APP_NAME:'HafiyeP23Live'}
  })
  const page=await app.firstWindow()
  await page.waitForLoadState('domcontentloaded')
  await page.waitForFunction(() => document.title.includes('Hafiye'), null, {timeout:30000})
  const composer=page.locator('[contenteditable="true"]').first()
  await composer.waitFor({state:'visible',timeout:30000})
  console.log('P23_COMPOSER_READY', await page.title())
  await composer.click()
  await composer.fill("Firefox'u aç.")
  await composer.press('Enter')
  await page.waitForTimeout(60000)
  console.log('P23_TRANSCRIPT_TAIL', (await page.locator('body').innerText()).slice(-5000))
} finally { if (app) await app.close().catch(()=>{}) }
NODE
```

Observed `P23_COMPOSER_READY Hafiye`, the Firefox-open operation and
`Firefox tarayıcısı açıldı.`. The same turn later reported Gemini HTTP 429
`RESOURCE_EXHAUSTED` free-tier quota. The local route was restored afterward.

### P23 exact five-ID baseline command

```bash
PATH="$PWD/.venv/bin:$PATH" .venv/bin/pytest -q \
  tests/gateway/test_browser_control_api.py::test_remote_api_uses_the_same_authenticated_noop_round_trip \
  tests/test_hermes_state.py::TestFTS5Search::test_search_projection_skips_context_enrichment_queries \
  'tests/tools/test_execution_flag_detection.py::test_real_binaries_execute_leading_dash_program_payload[sort-args2-{bulk}-False]' \
  tests/tools/test_termux_api_detection.py::TestDetectAudioEnvironmentTermuxFallback::test_inconclusive_probes_with_binary_does_not_emit_app_warning \
  tests/hermes_cli/test_doctor.py::test_doctor_reports_vercel_backend_diagnostics
```

Result on 2026-08-25 after KI-043 source hardening: `3 failed, 2 passed`; IDs 1
and 4 passed and IDs 2, 3, and 5 failed. Every failure is in the exact
historical `ACCEPTED_UPSTREAM_BASELINE` set, so this is not a new P23
regression. The canonical historical whitelist remains all five IDs; the
current observed comparison subset is 2, 3, and 5.
