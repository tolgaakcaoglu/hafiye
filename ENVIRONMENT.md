# Hafiye Development Environment

Captured on `2026-08-23T23:28:36+03:00` in `/home/tolga/projects/hafiye`.

## Operating system and session

| Item | Observed value |
|---|---|
| OS | Ubuntu 26.04 LTS (Resolute Raccoon) |
| Kernel | `7.0.0-30-generic`, x86_64, PREEMPT_DYNAMIC |
| Desktop | Ubuntu GNOME |
| GNOME Shell / session | GNOME Shell `50.1`, gnome-session `50.1` |
| Display protocol | Wayland (`XDG_SESSION_TYPE=wayland`, `WAYLAND_DISPLAY=wayland-0`) |
| X compatibility | Xwayland display `:0` is available |
| D-Bus | `unix:path=/run/user/1000/bus` |
| Runtime directory | `/run/user/1000` |

## CPU, memory and graphics

- CPU: 12th Gen Intel Core i5-12600K, 10 cores / 16 threads, max 4.9 GHz.
- Memory: `free -h` reports 14 GiB total physical memory, 7.5 GiB available at capture time, and 49 GiB swap.
- GPU 1: Intel Alder Lake-S UHD Graphics 770, `i915`.
- GPU 2: NVIDIA GA102 GeForce RTX 3080, proprietary NVIDIA driver `595.84`, 10,240 MiB dedicated VRAM, `nvidia` kernel driver.
- No AMD GPU is present.
- `nvidia-smi` succeeds and NVIDIA OpenGL direct rendering succeeds with renderer `NVIDIA GeForce RTX 3080/PCIe/SSE2`, OpenGL 4.6.0.
- NVIDIA/CUDA is the expected primary backend for this host. The managed
  Hafiye llama.cpp runtime is now built with CUDA and AUTO selects CUDA on the
  RTX 3080. The whisper.cpp runtime remains a later phase.
- Vulkan loader: `libvulkan.so.1` package `1.4.341.0`; Mesa packages include `26.0.3-1ubuntu1` and Vulkan ICD files.
- `vulkaninfo` is not installed. This is a diagnostic warning, not a P0 blocker, because Vulkan is the fallback backend on this machine.

## Compute backend policy

- Default: `AUTO`.
- Selection order: NVIDIA present + CUDA available → CUDA; otherwise Vulkan available → Vulkan; otherwise CPU.
- Managed llama.cpp: CUDA primary, Vulkan fallback, CPU fallback.
- Managed whisper.cpp: CUDA primary, Vulkan fallback, CPU fallback.
- Future Desktop selector: Auto / CUDA / Vulkan / CPU.
- The expected primary backend on this machine is CUDA.

## Audio and microphones

- Audio server: PipeWire `1.6.2` with WirePlumber `0.5.13` and `pipewire-pulse`.
- `wpctl` sees the active PipeWire graph; `pactl` is not installed. PipeWire/WirePlumber plus `wpctl` is the accepted audio enumeration path for P0.
- Capture devices observed:
  - `Trust GXT 232 Microphone Mono` — current default source.
  - `V-Z632 Analog Stereo` — USB audio capture device.
  - `Built-in Audio Analog Stereo` — onboard capture source.
- ALSA capture enumeration also exposes the Trust microphone, V-Z632 USB Audio, and onboard ALC897 inputs.

## Language runtimes and build tools

| Tool | Version / status |
|---|---|
| System Python | `3.14.4` (outside upstream constraint) |
| Repository Python selector | `.python-version` is `3.11` (upstream convention) |
| Hermes Python | CPython `3.13.15` in `.venv` |
| uv | `0.12.5` at `/home/tolga/.local/bin/uv` |
| Node | `v22.22.1` |
| npm / npx | `11.19.0` |
| Git | `2.53.0` |
| make | GNU Make `4.4.1` |
| gcc / g++ | `15.2.0` |
| clang | Ubuntu clang `21.1.8` |
| cmake | `4.2.3` |
| ninja | `1.13.2` |
| pkg-config | `2.5.1` |
| NVIDIA CUDA toolkit | `nvcc 12.4.131`; CUDA development build available at `/usr/bin/nvcc` |
| Vulkan development | `libvulkan-dev` installed; `pkg-config --exists vulkan` succeeds |
| ripgrep | `15.2.0` |
| ffmpeg | `8.0.1` |
| jq | `1.8.1` |
| Rust / Cargo | Rustup stable, Cargo/Rustc `1.98.0` at `/home/tolga/.cargo/bin`; user-space PATH reload may be needed |

The repository's `.python-version` remains the upstream `3.11` selector, but
the active `.venv` is explicitly created/synchronized with `uv ... --python
3.13` because this host's supported Hermes baseline is CPython 3.13 and the
system Python 3.14 is outside the declared `<3.14` range. The active venv
contains `keyring 25.7.0` for the Hafiye provider Secret Service boundary.

## systemd user session

- `systemctl --user is-system-running`: `running`.
- User D-Bus and the user service manager are available in the active GNOME session.
- `loginctl show-user`: `Linger=no`; the session is active. Persistent service work in P2 must explicitly handle the no-linger state.
- The main Hafiye process has not been installed or run as root.

## P8 privileged root broker

- Installed with normal interactive sudo from a visible system terminal; no
  passwordless sudo or `NOPASSWD` sudoers rule was created.
- System unit: `/usr/lib/systemd/system/hafiye-rootd.service`.
- Runtime state: `hafiye-rootd.service` is enabled and active as root EUID 0;
  the main `hafiye-gateway.service` remains the normal user EUID 1000.
- Socket: `/run/hafiye/root.sock`, Unix stream only, mode `0600`, owned by
  `tolga:tolga`; no TCP/UDP listener is configured.
- The broker audit log is `/var/log/hafiye/rootd-audit.log`, root-owned with
  restricted permissions. Audit records include peer identity, lifecycle
  status, duration, and redacted arguments.
- Real host checks passed for non-root `root.exec`, privileged temporary-file
  write, malformed duplicate-key rejection, and an actual `nobody` peer
  receiving `permission_denied`.

## Computer-use-linux pinned source readiness

- Source repository: `agent-sh/computer-use-linux`.
- Pinned source commit: `94736dc3e0dca56acfc89752c26869fb9ed01202`.
- Checkout: `/home/tolga/.cache/hafiye/computer-use-linux`.
- The released npm `0.4.9` doctor result is historical evidence only. The final P0 setup uses the pinned source checkout's official `./install.sh` flow.
- Official source setup completed system dependencies, Rust/Cargo, source build, AT-SPI, ydotool/ydotoold packages, and GNOME extension installation. After relogin, the extension is serving the window-control DBus API.
- Final source doctor: all four mandated readiness booleans are true, `blockers=[]`, AT-SPI/toolkit accessibility is true, the GNOME extension backend can list/focus windows, and ydotool/uinput input is read/write-ready.
- `/dev/uinput` is `root:input 0660`; `tolga` is in the `input` group in the current session.
- Ubuntu's packaged `ydotool.service` is enabled and active for `tolga`; the duplicate generated `ydotoold.service` was removed after its same-socket collision, and the root user-manager ydotoold instance was disabled.

## Environment changes made during P0

- Installed uv and CPython 3.13 in user-owned paths.
- Created `.venv` and installed upstream Python development dependencies plus optional SDKs.
- Installed root Node dependencies for the upstream Desktop build; no product lockfile change was retained.
- Ran the pinned CUA source checkout's official installer and built/installed `/home/tolga/.local/bin/computer-use-linux`.
- Ran `computer-use-linux setup-window-targeting`; extension files are installed and active after relogin.
- Added `tolga` to the `input` group using normal interactive sudo, then verified the new session has `/dev/uinput` read/write access.
- Verified `systemctl --user status ydotool.service` as active/enabled; removed the duplicate generated unit and disabled the root user-manager daemon so only the non-root user service remains.
- No passwordless sudo or `NOPASSWD` sudoers rule was created.
- `pactl` and `vulkaninfo` remain absent as diagnostic warnings; `wpctl` and the Vulkan loader/ICDs are present.
- After P0, the user installed `nvidia-cuda-toolkit`, `libvulkan-dev`, and
  `pkg-config` through a normal visible terminal. No sudoers policy was
  changed. `nvcc --version` reports CUDA 12.4.131.

## P5 provider credential and optional dependency validation

- The real Linux/GNOME Secret Service backend is available through `keyring
  25.7.0`. A live round-trip wrote, read, deleted, and removed a provider
  secret reference without recording the secret value; Hafiye config contained
  no raw provider secret.
- The live Gemini credential is stored in Linux Secret Service; its raw value
  is not recorded in this file, `.env`, or repository configuration. The live
  model-list and Hafiye connection tests passed as recorded in STATE.md.
- `uv sync --locked --all-extras --no-extra wake --no-extra matrix --python
  3.13` completed with the relevant optional SDKs. The `wake` exclusion is
  required because `tflite-runtime==2.14.0` has no compatible CPython 3.13
  wheel; `matrix` is excluded because `python-olm==3.2.16` fails against the
  current CMake toolchain's legacy minimum-version requirement. These are
  upstream optional packaging/toolchain warnings, not P5 blockers.

## P1 path and build validation

- With HERMES_HOME unset and all four XDG base variables pointed at a
  temporary directory, .venv/bin/hafiye --help rendered Hafiye usage and
  .venv/bin/hafiye config set model.default smoke-test-model wrote
  config/hafiye/config.yaml.
- The same smoke test created the expected temporary config, data, state, and
  cache roots without modifying the real home.
- Desktop normal data and state resolution now follows the same Hafiye policy:
  data under ~/.local/share/hafiye and logs/state under ~/.local/state/hafiye.
- The clean Desktop build recorded source commit
  34f1d8c2472e6b70b71bbdbfc9d3292761dbb67b with dirty=false.
- The Linux unpacked package produced an executable x86-64
  release/linux-unpacked/hafiye-desktop and included resources/icon.ico.
- No new privileged environment change was required for P1. The P0
  systemd-user, AT-SPI, GNOME Wayland, ydotool, uinput, CUDA, and audio
  observations above remain the active host evidence.

## P4 managed llama.cpp validation

- Managed runtime data root: `~/.local/share/hafiye/runtimes/llama.cpp/`.
- Managed model root: `~/.local/share/hafiye/models/`.
- Runtime state/log root: `~/.local/state/hafiye/local-runtime/`.
- Source repository: `https://github.com/ggml-org/llama.cpp.git`.
- Pinned managed source commit: `c060ca974c773c7c3d17fd1b66dc9d312bc292c0`.
- The real `AUTO` build compiled `CPU` and `CUDA`; the runtime manifest records
  `expected_auto_backend=CUDA` and `selected_backend=CUDA`.
- `llama-server` is managed as a non-root user process, binds only to
  `127.0.0.1:11435`, and is exposed to Desktop through the authenticated
  persistent Hafiye gateway at `127.0.0.1:9120`.
- Real `--list-devices` output identified `CUDA0: NVIDIA GeForce RTX 3080`;
  `nvidia-smi` observed the managed server using GPU memory during chat.
- `pactl` and `vulkaninfo` are still absent. PipeWire/WirePlumber plus `wpctl`
  remains the accepted audio path, and Vulkan remains a fallback/diagnostic
  path rather than this host's primary compute backend.

## P10 browser validation (2026-08-24)

- `npx --yes agent-browser@^0.26.0 install` completed without sudo and
  installed the managed Chrome payload in the user cache
  `~/.agent-browser/browsers/chrome-152.0.7977.54`.
- Hermes structured browser acceptance used the current explicit
  `browser.backend: off` configuration to exercise the built-in
  `browser_*` lane; navigation, extraction, and download passed against a
  local `ThreadingHTTPServer` fixture.
- Native browser acceptance used the existing Firefox Wayland window through
  the pinned managed computer-use-linux MCP provider. It opened and closed
  only a temporary test tab; existing Firefox windows and authenticated state
  were not inspected.
- No sudo, system package, systemd, group, device-permission, or password
  change was required for P10.

## P11 local Turkish voice validation (2026-08-24)

- The user installed the missing Vulkan shader build prerequisites
  `glslc`, `spirv-tools`, and `spirv-headers` through the visible terminal.
- Managed whisper.cpp source: `~/.local/share/hafiye/runtimes/whisper.cpp/source`;
  source commit `c122757fddf358397bb7f33b6ac3aab24a5bca04`.
- Real binaries: `build-cpu/bin/whisper-cli`, `build-cuda/bin/whisper-cli`, and
  `build-vulkan/bin/whisper-cli`; model:
  `models/ggml-base.bin`. The managed doctor reported all three compiled and
  selected CUDA for `AUTO` on the NVIDIA GeForce RTX 3080.
- Managed Piper runtime: `~/.local/share/hafiye/runtimes/piper/`, Python
  `venv/bin/python`, package `piper-tts==1.7.0`, installed voice
  `voices/tr_TR-dfki-medium.onnx` with its JSON metadata.
- `.venv/bin/python -m hermes_cli.voice_runtime doctor` returned `ok=true`,
  `blockers=[]`, and no warnings.
- The current PipeWire source used for the accepted real capture was node 37,
  `Trust GXT 232 Microphone Mono`, the default unmuted source at volume 1.00.
  After a five-second countdown, a 14.995-second `pw-record` capture at 16 kHz,
  mono, signed 16-bit WAV was correctly transcribed by CUDA whisper.cpp as
  `Merhaba hafiye, bugün nasılsın bana Türkçe cevap ver?`. Hafiye's own
  `transcribe_audio()` hook returned the same text with `provider:
  local_command`.
- Direct Piper synthesis, the Hafiye TTS tool, and `pw-play` completed real
  Turkish audio playback. No cloud STT/TTS was used for this acceptance.

## P12 custom Hafiye wake word validation (2026-08-24)

- Official openWakeWord source checkout:
  `/home/tolga/.local/share/hafiye/runtimes/openwakeword-training/source` at
  commit `368c03716d1e92591906a84949bc477f3a834455` (package version 0.6.0).
- Training venv: `/home/tolga/.local/share/hafiye/runtimes/openwakeword-training/venv`,
  Python 3.13.15. The source package was installed with `--no-deps` because
  its PyPI metadata requires `tflite-runtime`, which has no compatible CPython
  3.13 wheel here; the ONNX path uses the installed ONNX runtime instead.
- The managed Turkish Piper voice `tr_TR-dfki-medium` generated the positive
  training samples. The command used was:

  `/home/tolga/.local/share/hafiye/runtimes/openwakeword-training/venv/bin/python scripts/train_hafiye_wakeword.py --piper-python /home/tolga/.local/share/hafiye/runtimes/piper/venv/bin/python --piper-data-dir /home/tolga/.local/share/hafiye/runtimes/piper/voices --output-dir /home/tolga/.local/share/hafiye/runtimes/openwakeword-training/hafiye --export /home/tolga/projects/hafiye/tools/wakewords/hafiye.onnx --samples 384 --steps 900 --cpu-threads 4`

- The bundled standalone model is
  `/home/tolga/projects/hafiye/tools/wakewords/hafiye.onnx`, 216,102 bytes,
  SHA-256 `9eb0e8c9fd509900ba5d33b4c43906817265605846564af76232daeea194ba50`.
  Synthetic validation at threshold 0.6 reached accuracy 1.0; negative max
  score was 0.04943939670920372 and positive minimum was 0.9991450309753418.
- Real audio checks used `/tmp/hafiye-p12-positive-20260824.wav` as a
  normal-room music negative and
  `/tmp/hafiye-p12-positive-20260824-take2.wav` as the Turkish Hafiye positive.
  The first produced zero detector fires; the second produced four direct
  detector fires under the two-second cooldown.
- The real Desktop check used the built Electron bundle with Chromium flags
  `--use-fake-ui-for-media-stream`, `--use-fake-device-for-media-stream`, and
  `--use-file-for-fake-audio-capture=/tmp/hafiye-p12-positive-20260824-take2.wav`.
  After arming through the persistent gateway, the native Electron window
  reported `minimized=true`, `visible=false`, and a new session route opened.
- `sounddevice` in the repository venv still reports `PortAudio library not
  found`, so local backend capture remains a warning. PipeWire/WirePlumber and
  the Desktop browser client capture path are available; P12 acceptance uses
  that client path and does not claim local PortAudio readiness. No sudo,
  system package, systemd, group, device-permission, or password change was
  required for P12.

## P13 cancellation and emergency-stop validation (2026-08-24)

- The active session remains Ubuntu GNOME 50.1 on Wayland with
  `XDG_CURRENT_DESKTOP=ubuntu:GNOME`, `DESKTOP_SESSION=ubuntu`,
  `WAYLAND_DISPLAY=wayland-0`, and user D-Bus available.
- `hafiye-gateway.service` was restarted and remained active on loopback. The
  authenticated WebSocket sequence `emergency.stop → prompt.submit →
  emergency.resume` returned `paused=true`, prompt error code `4091`, and a
  successful resumed state. The ESTOP file was removed after the intentional
  resume.
- `hafiye-rootd.service` remains active as root with the explicit ESTOP path
  `/home/tolga/.local/share/hafiye/ESTOP`. A real root-broker request returned
  UID 0 before the stop, was rejected with `code=emergency_stop` while the
  sentinel existed, and returned UID 0 after resume. The main gateway remains
  non-root.
- A real TTS pipeline smoke observed an active playback state, then confirmed
  the stop event and state cleanup. A real registered sleep process was killed
  by the process-registry emergency-stop path.
- Electron's `globalShortcut` could not register `Control+Super+Escape` in
  this Wayland session. Hafiye therefore installed the private GNOME custom
  keybinding at
  `/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/hafiye-emergency-stop/`.
  The binding was observed through `gsettings`, a real `ydotool` chord created
  the temporary HERMES_HOME ESTOP sentinel, and clean Electron shutdown
  restored `custom-keybindings` to `@as []`. Existing custom bindings were
  preserved.
- The generic upstream `cua-driver` executable is absent. This is a warning
  for the upstream generic lane only; the managed pinned
  `computer-use-linux` MCP path remains the accepted Linux implementation and
  its P0/P9 readiness and real GNOME E2E remain green.
- No sudo, passwordless sudo, NOPASSWD rule, system package, group, or device
  permission change was performed for P13. The current host ESTOP sentinel is
  clear after validation.

## P15 OpenHands managed runtime validation (2026-08-24)

- Official source repository: `https://github.com/OpenHands/software-agent-sdk/`.
- Managed source checkout:
  `/home/tolga/.local/share/hafiye/runtimes/openhands/source`.
- Pinned source commit:
  `6d38810359827823e62a5e1043d0d78d0bafb6de`.
- Managed Python:
  `/home/tolga/.local/share/hafiye/runtimes/openhands/venv/bin/python`,
  Python `3.13.15`.
- Exact managed package pins: `openhands-sdk==1.41.0`,
  `openhands-tools==1.41.0`, `openhands-workspace==1.41.0`, and
  `openhands-agent-server==1.41.0`.
- The real command `.venv/bin/hafiye runtime openhands install` completed
  successfully without sudo. A subsequent
  `.venv/bin/hafiye runtime openhands doctor` returned `ready=true` and
  `blockers=[]`; the manifest is under
  `/home/tolga/.local/share/hafiye/runtimes/openhands/manifest.json`.
- No API key or other credential is recorded in this environment document.
- P15 Task Center progress is process-local. Durable generic task history is
  intentionally deferred to P16.

## P16 Task Center persistence validation (2026-08-24)

- Task Center durable state is stored at
  `/home/tolga/.local/state/hafiye/task_center.db` on the normal XDG
  installation. Explicit `HERMES_HOME` test sandboxes use that root for
  isolation.
- The database uses SQLite WAL and is owned by the non-root Hafiye process;
  no sudo, system package, systemd, group, device-permission, or password
  change was required.
- The persisted record contains task metadata and redacted operator history
  only. It does not contain API keys, OpenHands transcripts, workspace output,
  or private chain-of-thought.
- A real separate-process gateway/RPC smoke and a real Electron + gateway E2E
  verified completed/failed/queued display, queued cancellation, and restart
  recovery on this host's Linux Desktop environment.

## P17 Control Center validation (2026-08-24)

- The clean Desktop build used source/test commit
  `2dc541d09367b895744b512d99b058506d7f78d2`; Vite, Electron main/preload,
  native staging, and `assert-dist-built` passed.
- A real Electron process connected to an isolated real `hermes serve`
  gateway and opened all 19 Control Center pages. Privacy Mode was changed
  through the Desktop selector to `LOCAL_ONLY`, then verified after a renderer
  reload from the sandbox gateway config.
- The E2E used a temporary `HERMES_HOME` and user-data directory. The actual
  `hafiye-gateway.service`, host credentials, system packages, sudo rules,
  device permissions, and persistent host state were not modified.
- Existing Vite/Babel/chunking warnings remain diagnostic build warnings; no
  new P17 host blocker or upstream regression was observed.
