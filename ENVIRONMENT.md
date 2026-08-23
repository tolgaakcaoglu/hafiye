# Hafiye Development Environment

Captured on `2026-08-23T17:29:15+03:00` in `/home/tolga/projects/hafiye`.

## Operating system and session

| Item | Observed value |
|---|---|
| OS | Ubuntu 26.04 LTS (Resolute Raccoon) |
| Kernel | `7.0.0-29-generic`, x86_64, PREEMPT_DYNAMIC |
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
- NVIDIA/CUDA is the expected primary backend for this host. A managed llama.cpp/whisper.cpp CUDA runtime has not yet been built in Hafiye.
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
| ripgrep | `15.2.0` |
| ffmpeg | `8.0.1` |
| jq | `1.8.1` |
| Rust / Cargo | Rustup stable, Cargo/Rustc `1.98.0` at `/home/tolga/.cargo/bin`; user-space PATH reload may be needed |

## systemd user session

- `systemctl --user is-system-running`: `running`.
- User D-Bus and the user service manager are available in the active GNOME session.
- `loginctl show-user`: `Linger=no`; the session is active. Persistent service work in P2 must explicitly handle the no-linger state.
- The main Hafiye process has not been installed or run as root.

## Computer-use-linux pinned source readiness

- Source repository: `agent-sh/computer-use-linux`.
- Pinned source commit: `94736dc3e0dca56acfc89752c26869fb9ed01202`.
- Checkout: `/tmp/hafiye-computer-use-linux.djXfCX/repo`.
- The released npm `0.4.9` doctor result is historical evidence only. The final P0 setup uses the pinned source checkout's official `./install.sh` flow.
- Official source setup completed system dependencies, Rust/Cargo, source build, AT-SPI, ydotool/ydotoold packages, and GNOME extension installation. `setup-window-targeting` requires a GNOME Shell reload.
- Current post-setup/pre-relogin doctor: MCP registration true; AT-SPI/toolkit accessibility true; accessibility tree true; `can_send_development_input=true`; GNOME window introspection/extension service unavailable; `can_query_windows=false`; one blocker.
- `/dev/uinput` is `root:input 0660`. `tolga` was added to the `input` group, but the active session has not reloaded that membership; ydotoold user-service verification is pending.
- Final acceptance requires all four booleans true and `blockers=[]` after source setup.

## Environment changes made during P0

- Installed uv and CPython 3.13 in user-owned paths.
- Created `.venv` and installed upstream Python development dependencies plus optional SDKs.
- Installed root Node dependencies for the upstream Desktop build; no product lockfile change was retained.
- Ran the pinned CUA source checkout's official installer and built/installed `/home/tolga/.local/bin/computer-use-linux`.
- Ran `computer-use-linux setup-window-targeting`; extension files are installed and queued for the next GNOME Shell load.
- Added `tolga` to the `input` group using normal interactive sudo. Logout/login is required before the current session sees it.
- No passwordless sudo or `NOPASSWD` sudoers rule was created.
- `pactl` and `vulkaninfo` remain absent as diagnostic warnings; `wpctl` and the Vulkan loader/ICDs are present.
