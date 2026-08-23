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
- AMD GPU: not present in `lspci` output.
- OpenGL: direct rendering enabled; renderer `NVIDIA GeForce RTX 3080/PCIe/SSE2`, OpenGL 4.6.0.
- Vulkan loader: `libvulkan.so.1` version package `1.4.341.0`; Mesa packages include `26.0.3-1ubuntu1` and Vulkan ICD files are installed.
- `vulkaninfo`: not installed, so a Vulkan device/feature report was not available.

## Audio and microphones

- Audio server: PipeWire `1.6.2` with WirePlumber `0.5.13` and `pipewire-pulse`.
- `wpctl` sees the active PipeWire graph; `pactl` is not installed.
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
| Rust / Cargo | unavailable |

## systemd user session

- `systemctl --user is-system-running`: `running`.
- User D-Bus and user service manager are available in the active GNOME session.
- `loginctl show-user`: `Linger=no`; the session is currently active. Persistent service work in P2 must explicitly handle the no-linger state.
- The main Hafiye process has not been installed or run as root.

## Computer-use-linux doctor

The real doctor command was run under the active Wayland session. See `docs/p0/computer-use-linux-doctor-report.json` for the normalized structured result.

- MCP registration: true.
- Portal input: available.
- Screenshots: GNOME Shell and portal paths available.
- AT-SPI bus exists, but accessibility is disabled (`org.a11y.Status IsEnabled=false`; toolkit accessibility is false).
- GNOME Shell window introspection: denied by D-Bus policy.
- GNOME window-control extension: not installed/registered.
- ydotool/ydotoold/xdotool: unavailable; `/dev/uinput` is not readable by the user.
- Doctor result: `can_build_accessibility_tree=false`, `can_query_windows=false`, `can_send_development_input=true`, with blockers.

## Environment changes made during P0

- Installed uv and CPython 3.13 in user-owned paths.
- Created `.venv` and installed upstream Python development dependencies.
- Installed root Node dependencies for the upstream Desktop build.
- Used temporary, checksum-verified computer-use-linux release binaries under `/tmp` only.
- No system packages were installed because non-interactive sudo is unavailable.
- No product source files were changed.
