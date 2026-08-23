# HAFİYE
## Definitive Architecture & Codex Execution Roadmap

**Status:** AUTHORITATIVE  
**Target:** Ubuntu/Linux personal desktop AI operator  
**Developer:** Codex  
**Runtime intelligence:** Local-first LLMs, remote self-hosted LLMs and explicitly configured cloud providers  
**Supersedes:** Every previous Jarvis/Hafiye roadmap or architecture draft  
**Date:** 2026-08-23

---

# 0. CODEX: READ THIS FIRST

This document is not a brainstorming document.

The product decisions have already been made.

Your job is to **implement them**.

Do not replace a prescribed technology with another technology because you prefer it.
Do not turn a fixed decision into an “evaluation phase”.
Do not create an options matrix unless this document explicitly requests diagnostic data.
Do not ask the user to choose between implementation technologies that are already fixed here.
Do not redesign the product architecture.

You may inspect upstream documentation to determine the correct current API, command, package name, build flag or configuration syntax.

That is implementation research, not architecture selection.

If an upstream API has changed:

1. keep the architecture in this document;
2. adapt the implementation to the new API;
3. document the compatibility change;
4. continue.

If a prescribed upstream project has become genuinely unusable, removed, abandoned, incompatible or impossible to build, stop that specific integration and record a **BLOCKER** with evidence. Do not silently replace it.

---

# 1. PRODUCT

The product name is:

# **Hafiye**

Hafiye is a personal AI operating layer for the user's Linux desktop.

It is not:

- a chatbot;
- a terminal-only coding agent;
- a browser-only agent;
- a voice-command launcher;
- a demo.

Hafiye must be able to:

- receive typed natural-language instructions;
- receive Turkish spoken instructions;
- speak responses;
- wake hands-free when the user says “Hafiye”;
- operate the real Linux desktop;
- use keyboard and mouse;
- inspect accessibility trees and screenshots;
- open and operate applications;
- use the terminal;
- access the full user filesystem;
- manage processes;
- use the browser;
- use the user's current desktop session;
- perform privileged system operations through a root broker;
- remember projects and prior work;
- run scheduled jobs;
- use MCP tools and skills;
- delegate coding work to OpenHands;
- use a local LLM by default;
- connect to remote self-hosted LLM endpoints;
- use Gemini when configured;
- route tasks between models;
- continue functioning without cloud inference;
- expose all important configuration through a Linux desktop GUI;
- also expose CLI management.

Example final interaction:

> “Hafiye, Pocket World'ü aç. Son kaldığımız işi hatırla. Testleri çalıştır. Kodlama gerekiyorsa OpenHands'e ver. Local model yeterli olmazsa evdeki GPU sunucusunu kullan. Bu görevde cloud kullanma. Bitince bana söyle.”

Hafiye must perform the work, verify the result and report completion.

---

# 2. CORE ARCHITECTURE DECISIONS

These decisions are final.

## 2.1 Agent foundation: Hermes Agent

Hafiye SHALL be built as a **maintained fork of NousResearch/hermes-agent**.

Do not write a new generic agent runtime.

Reuse Hermes for:

- agent loop;
- conversations and sessions;
- tool execution;
- provider support;
- provider fallback infrastructure;
- persistent memory;
- session search;
- skills;
- MCP;
- cron/scheduling;
- subagents;
- browser tooling;
- voice infrastructure;
- wake-word infrastructure;
- CLI/TUI foundations;
- gateway/server protocol.

Repository:

`https://github.com/NousResearch/hermes-agent`

License at architecture freeze: MIT.

Preserve the upstream Git history.

Configure Git remotes as:

```text
origin   = Hafiye repository
upstream = NousResearch/hermes-agent
```

Hafiye-specific changes must be kept as separable patches/modules whenever possible so upstream merges remain feasible.

---

## 2.2 Internal naming strategy

Do **not** perform a mass rename of every internal Hermes Python/TypeScript symbol.

That would create needless upstream merge conflicts.

External product surfaces become Hafiye:

- application name;
- binary/launcher;
- window title;
- tray;
- product copy;
- user-facing paths;
- config;
- service names;
- desktop file;
- package names where practical;
- branding.

Internal upstream module names may remain `hermes_*` where changing them provides no user-visible benefit.

This is intentional.

---

## 2.3 Desktop UI: fork Hermes Desktop

Do not build a new Tauri application.

Use and extend the existing Hermes Desktop application:

- Electron;
- React;
- TypeScript;
- Vite;
- Hermes `serve` JSON-RPC/WebSocket backend.

Hafiye Desktop must be a forked/rebranded evolution of Hermes Desktop.

Reuse:

- chat UI;
- streaming tool output;
- sessions;
- provider/model settings;
- voice UI;
- file previews;
- settings foundations;
- Quick Entry;
- gateway communication.

Add the Hafiye-specific Control Center defined later in this document.

---

## 2.4 Persistent runtime topology

Hermes Desktop currently has the ability to launch its own backend.

Hafiye must instead use a **persistent user service as the primary local runtime**.

Create:

```text
hafiye-gateway.service
```

as a systemd **user** service.

It launches the Hafiye/Hermes backend in server mode.

Desktop connects to this already-running gateway.

Closing the Desktop window must not kill Hafiye.

Long tasks must be able to continue when the main window is closed.

---

## 2.5 Local LLM runtime: llama.cpp

The canonical built-in local inference engine is:

# **llama.cpp**

Do not use Jan as the built-in local runtime.

Do not use Ollama as the built-in local runtime.

Additional OpenAI-compatible local runtimes may be connected as custom providers, but Hafiye's own managed local engine is llama.cpp.

Model format:

```text
GGUF
```

Server:

```text
llama-server
```

API contract:

```text
OpenAI-compatible HTTP API
```

The local server binds only to loopback by default.

---

## 2.6 Compute backend policy

The default compute backend is:

```text
AUTO
```

`AUTO` selects the first available backend in this order:

1. NVIDIA is present and CUDA is available → CUDA;
2. otherwise Vulkan is available → Vulkan;
3. otherwise → CPU.

The managed local runtime backends are fixed as follows:

- llama.cpp: primary CUDA, fallback Vulkan, then CPU;
- whisper.cpp: primary CUDA, fallback Vulkan, then CPU.

The current Hafiye development machine has an NVIDIA RTX 3080, so its expected primary backend is CUDA. This does not remove Vulkan and CPU fallback support.

Future Hafiye Desktop settings shall expose:

```text
Auto / CUDA / Vulkan / CPU
```

The local LLM engine remains llama.cpp and the local model format remains GGUF. The local STT engine remains whisper.cpp.

---

## 2.7 Local model management

Hafiye must manage llama.cpp itself.

Add a Hafiye local-model manager inside the backend.

Responsibilities:

- model registry;
- GGUF model download;
- checksum/size metadata;
- local storage;
- start llama-server;
- stop llama-server;
- restart;
- health;
- active model;
- context configuration;
- GPU-layer configuration;
- process logs;
- memory use;
- graceful unload;
- model deletion;
- interrupted-download recovery.

Store models beneath:

```text
~/.local/share/hafiye/models/
```

Store managed runtimes beneath:

```text
~/.local/share/hafiye/runtimes/
```

Do not hard-code a specific LLM model as part of the product architecture.

Models are user-selectable runtime data.

---

## 2.8 Remote self-hosted models

Remote self-hosted LLM integration uses:

# **OpenAI-compatible HTTP endpoints**

A remote provider has:

```text
name
base_url
api_key/credential reference
model id
capabilities
timeout
priority
enabled
```

This supports remote servers running:

- vLLM;
- SGLang;
- llama.cpp;
- compatible gateways.

Hafiye does not SSH into the remote LLM server to perform desktop tools.

The remote LLM performs inference only.

All computer/tool execution remains on the Hafiye machine.

---

## 2.9 Gemini

Gemini is a first-class cloud provider in Hafiye.

Reuse Hermes's native Gemini provider support.

The Hafiye GUI must allow:

- credential entry;
- model selection;
- test connection;
- enable/disable;
- routing assignment;
- cost-sensitive use.

Do not make Gemini mandatory.

---

## 2.10 Model routing

Reuse Hermes provider/fallback infrastructure, but add a Hafiye routing layer with explicit task slots.

The slots are:

```text
default
fast
reasoning
coding
vision
long_context
memory_aux
compression_aux
```

Each slot stores:

```text
provider
model
fallback chain
locality policy
```

The router receives:

- task classification;
- required capabilities;
- context size;
- user override;
- privacy mode;
- provider health;
- local model availability.

The user may override routing in natural language:

> “Bu görevde Gemini kullan.”

> “Bu tamamen local çalışsın.”

> “Remote GPU'yu kullan.”

Overrides are task-scoped unless the user explicitly asks to change a default.

---

## 2.11 Privacy modes

Implement exactly three global privacy modes:

```text
NORMAL
LOCAL_ONLY
OFFLINE
```

### NORMAL

Configured router and fallback policy applies.

### LOCAL_ONLY

No cloud inference.
No external remote inference.
Local inference and local tools are allowed.

### OFFLINE

No network-based inference.
No web/network tools.
Local LLM, desktop, shell, files, memory and local automation continue.

A `LOCAL_ONLY` task may never silently fall back to Gemini or a remote endpoint.

---

## 2.12 Linux desktop control: computer-use-linux

The primary desktop-control implementation is:

# **agent-sh/computer-use-linux**

Repository:

`https://github.com/agent-sh/computer-use-linux`

Integrate it as a **managed built-in MCP server/tool provider**.

Do not use CUA as the primary driver.

Reason:

- Hafiye targets Linux;
- computer-use-linux is Linux-specific;
- it is Wayland-first;
- it uses AT-SPI;
- it supports GNOME/KDE and real Linux compositor paths;
- it exposes screenshots, accessibility trees, windows, mouse and keyboard through MCP.

The installer must run its diagnostic readiness command and make missing Linux prerequisites explicit.

---

## 2.13 Computer action priority

Hafiye must not use GUI automation when a deterministic local tool is superior.

Action priority is:

```text
1. native structured API
2. deterministic shell/filesystem/process tool
3. browser structured automation
4. accessibility-tree desktop action
5. visual screenshot/click fallback
```

Examples:

Moving a file:
use filesystem tool.

Starting a service:
use system/root tool.

Clicking a button in an application with no API:
use computer-use-linux.

---

## 2.14 Browser

Reuse Hermes browser automation.

Support two paths:

```text
STRUCTURED BROWSER AUTOMATION
NATIVE DESKTOP BROWSER CONTROL
```

Use native desktop browser control when a task explicitly requires the user's already-authenticated normal browser session and structured automation cannot safely reuse it.

---

## 2.15 Coding specialist: OpenHands

OpenHands is Hafiye's coding specialist.

Use the current OpenHands V1 SDK/runtime architecture.

Do not use OpenHands as Hafiye's main agent.

Expose it through a Hafiye/Hermes tool:

```text
coding_delegate
```

Request schema:

```text
goal
repository_path
constraints
model route
network policy
expected verification
```

For the user's chosen Full Autonomous mode, OpenHands runs against the local workspace/host path without an artificial Docker-only restriction.

The Hafiye router supplies the coding model/provider to OpenHands.

---

## 2.16 Full host access

Hafiye's final operating model is full host access.

The main agent runs as the user's normal Linux account.

Hermes local terminal/process/filesystem tools must use the real host.

Do not confine final execution to a workspace sandbox.

Do not place Hafiye in Docker as its primary local runtime.

---

## 2.17 Privileged access: hafiye-rootd

Do not run the entire Hafiye process as root.

Create a dedicated system service:

```text
hafiye-rootd.service
```

Binary/service name:

```text
hafiye-rootd
```

Communication:

```text
Unix domain socket
/run/hafiye/root.sock
```

The service must:

- listen on no TCP/UDP port;
- verify peer credentials using Linux Unix-socket peer credentials;
- allow only the configured local user UID;
- use strict request framing;
- have timeouts;
- write an audit trail;
- reject malformed requests.

Supported RPC includes structured privileged operations and:

```text
root.exec
```

for arbitrary privileged command execution when the execution policy is `FULL_AUTONOMOUS`.

The user's requirement is genuine full access.

The broker is a process-boundary safety design, not an artificial capability restriction.

---

## 2.18 Execution policies

Expose exactly these user-selectable policies:

```text
FULL_AUTONOMOUS
PRIVILEGED_CONFIRM
WRITE_CONFIRM
READ_ONLY
```

Default for this installation:

```text
FULL_AUTONOMOUS
```

The user must be able to change the policy in the GUI.

Policy changes take effect without reinstalling Hafiye.

---

# 3. VOICE DECISIONS

## 3.1 Reuse Hermes voice pipeline

Do not create an independent voice-assistant framework.

Reuse Hermes's existing:

- desktop microphone capture;
- voice sessions;
- wake-word ownership;
- barge-in infrastructure;
- TTS hooks;
- stop phrase handling.

Modify and fix it for Hafiye.

---

## 3.2 Wake word: openWakeWord

Wake-word engine:

# **openWakeWord**

Final trigger phrase:

# **Hafiye**

Create and bundle a custom Hafiye openWakeWord model:

```text
hafiye.onnx
```

The final product must not require “Hey Hermes”, “Jarvis” or a cloud wake-word service.

The wake detector remains fully local.

During development, training utilities may be used to produce the model, but the shipped runtime uses the bundled Hafiye model.

---

## 3.3 STT: whisper.cpp

Do not use faster-whisper as Hafiye's default local STT.

The local STT runtime is:

# **whisper.cpp**

Backend:

```text
CUDA primary; Vulkan, then CPU fallback
```

Language default:

```text
tr
```

Use Hermes's supported custom-local-STT command hook to route local transcription through the managed whisper.cpp binary.

Managed path:

```text
~/.local/share/hafiye/runtimes/whisper.cpp/
```

Provide Vulkan and CPU fallback if CUDA initialization fails.

Cloud STT providers may remain optional, but default Hafiye voice transcription is local whisper.cpp.

---

## 3.4 Fix Desktop transcription routing

The fork must ensure Desktop microphone transcription respects the configured STT provider.

Do not permit a hard-coded OpenAI Whisper endpoint in the Hafiye Desktop microphone path.

Desktop recording must send audio to the Hafiye backend and the backend must apply the configured STT provider.

---

## 3.5 Microphone selection

Add microphone selection to Hafiye Desktop.

Settings must:

- enumerate audio input devices;
- show labels after permission is granted;
- persist selected device;
- fall back to OS default if removed;
- respond to device hot-plug events.

Use the selected device for:

- push-to-talk;
- continuous voice conversation;
- desktop-side wake audio path when applicable.

---

## 3.6 TTS: Piper

Default local TTS engine:

# **OHF-Voice Piper**

Run Piper as a separate managed runtime/process.

Do not link GPL Piper code into Hafiye application libraries.

Hafiye invokes Piper through its process/CLI/HTTP boundary.

Default language:

```text
Turkish / tr_TR
```

Expose installed voices in the GUI.

Allow voice selection and preview.

Store runtime beneath:

```text
~/.local/share/hafiye/runtimes/piper/
```

---

## 3.7 Barge-in

Barge-in is mandatory.

While Hafiye is speaking, the microphone remains capable of detecting interruption.

When the user says:

> “Hafiye dur.”

Hafiye must:

1. stop current audio playback immediately;
2. cancel or pause the active voice turn;
3. stop generating further TTS for that answer;
4. return to listening/idle according to current mode.

The Stop button and emergency hotkey must use the same cancellation path.

---

# 4. DESKTOP PRODUCT DECISIONS

## 4.1 Main application

The main application is the forked Hermes Desktop Electron/React app rebranded as Hafiye.

User-facing product name:

```text
Hafiye
```

Linux application ID:

```text
com.hafiye.desktop
```

Primary launcher:

```text
hafiye-desktop
```

CLI:

```text
hafiye
```

---

## 4.2 Quick Entry becomes Hafiye Composer

Hermes Quick Entry is the foundation.

Rename/rework it into:

# **Hafiye Composer**

Default global hotkey:

```text
Super + Shift + Space
```

Do not use `Super + Space` as the default because GNOME commonly uses it for input-source switching.

The shortcut remains configurable.

Composer modes:

```text
HOTKEY_ONLY
SHOW_ON_LOGIN
PINNED
```

Default:

```text
SHOW_ON_LOGIN
```

At login, Composer appears briefly as “Hafiye hazır”, then collapses.

---

## 4.3 Composer UI

Minimum states:

```text
IDLE
LISTENING
TRANSCRIBING
THINKING
WORKING
SPEAKING
ERROR
PAUSED
```

The compact composer contains:

- Hafiye mark;
- prompt text area;
- microphone button;
- send button;
- active state indicator;
- stop button while active.

When work is running it may expand to show:

- current task;
- current tool;
- progress summary;
- selected model;
- cancel.

Do not dump chain-of-thought.

Display operational state and tool activity only.

---

## 4.4 Tray

System tray is mandatory.

Menu:

```text
Hafiye
● Running

Open Composer
Open Hafiye
New Task

Mute Microphone
Pause Voice
Pause Computer Control
Privacy Mode >

Recent Tasks >

Settings
Logs

Restart Hafiye
Quit Desktop
Stop Hafiye Core
```

Closing the main window minimizes to tray unless the user explicitly quits.

---

## 4.5 Control Center

The Hafiye Desktop settings/navigation must contain:

```text
Overview
Chat
Tasks
Models
Providers
Routing
Voice
Computer
Browser
Coding
Memory
Skills
MCP
Automation
Permissions
Privacy
Logs
Developer
About
```

These are functional pages, not decorative placeholders.

---

# 5. GUI SETTINGS CONTRACT

Every setting in this section must be backed by real backend state.

## 5.1 General

```text
Start Hafiye at login
Start gateway at login
Show Composer at login
Composer mode
Global shortcut
Notifications
Launch minimized
Language
```

---

## 5.2 Models

Show:

```text
Installed local models
Active local model
Download model
Import GGUF
Delete model
Load model
Unload model
Context size
GPU offload
Health
Runtime logs
```

---

## 5.3 Providers

Provider types:

```text
LOCAL_LLAMA
OPENAI_COMPATIBLE
GEMINI
OTHER_HERMES_PROVIDER
```

UI actions:

```text
Add
Edit
Enable
Disable
Test
Delete
List models
Set priority
```

Secrets are never displayed after storage.

---

## 5.4 Routing

Configure:

```text
default
fast
reasoning
coding
vision
long_context
memory_aux
compression_aux
```

Each displays:

```text
primary provider/model
fallbacks
locality
enabled
```

---

## 5.5 Voice

```text
Voice enabled
Wake word enabled
Wake phrase = Hafiye
Microphone device
STT enabled
STT model
STT backend = Auto/CUDA/Vulkan/CPU
TTS enabled
TTS voice
TTS speed
Always-listening mode
Barge-in
Stop phrases
```

---

## 5.6 Computer

Feature switches:

```text
Computer Control
Screen Capture
Accessibility Tree
Mouse
Keyboard
Clipboard
Application Control
Terminal
Filesystem
Process Control
Browser
Root Broker
```

Switches alter the actual tool registry.

---

## 5.7 Coding

```text
OpenHands enabled
Automatic coding delegation
Coding model route
Repository editing
Run tests
Run builds
Package installation
Network access
```

---

## 5.8 Memory

```text
Memory enabled
User memory
Project memory
Task history
Session recall
Skill learning
```

Actions:

```text
Browse
Search
Edit
Pin
Forget
Delete
Export
```

---

## 5.9 Permissions

```text
FULL_AUTONOMOUS
PRIVILEGED_CONFIRM
WRITE_CONFIRM
READ_ONLY
```

Show explanation and current policy.

---

## 5.10 Privacy

Buttons/modes:

```text
NORMAL
LOCAL_ONLY
OFFLINE
```

Also display current provider/network implications.

---

# 6. SECRETS

Do not use `.env` as Hafiye's normal user-facing secret store.

Implement Linux Secret Service through Python `keyring`/Secret Service integration.

Secrets include:

- API keys;
- provider tokens;
- remote endpoint credentials.

The Hafiye configuration stores only secret references.

If Hermes internals require environment variables, populate them in-process from the secret store at runtime.

Do not write retrieved secrets to logs.

---

# 7. MEMORY

Use Hermes built-in memory/session-search infrastructure as the conversational memory base.

Add a deterministic Hafiye project registry.

Table/model:

```text
project_id
name
aliases
path
created_at
last_opened_at
last_task_id
metadata
```

Natural-language example:

> “Bu klasörü Pocket World olarak hatırla.”

must create/update the project registry.

After restart:

> “Pocket World'ü aç.”

must resolve deterministically to the saved path.

Do not depend solely on an LLM guessing a path from prose memory.

---

# 8. TASK MODEL

Hafiye needs a user-visible Task layer above individual low-level tool calls.

Task fields:

```text
task_id
session_id
parent_task_id
goal
state
created_at
started_at
completed_at
route
provider
model
privacy_mode
current_step_summary
result_summary
error
```

States:

```text
QUEUED
PLANNING
RUNNING
WAITING
PAUSED
CANCELLING
COMPLETED
FAILED
CANCELLED
```

Task Center shows:

- active tasks;
- completed tasks;
- failed tasks;
- current step;
- tool history;
- file changes;
- commands;
- model;
- elapsed time;
- cancellation.

---

# 9. EMERGENCY STOP

Emergency stop is mandatory.

Implement a single cancellation mechanism exposed through:

```text
GUI Stop
Composer Stop
Tray Pause/Stop
Voice “Hafiye dur”
CLI
Global keyboard shortcut
```

Default emergency shortcut:

```text
Ctrl + Super + Escape
```

When fired:

- stop TTS;
- stop future desktop actions;
- cancel active cancellable task;
- signal subagents;
- block new root RPC;
- enter PAUSED state.

---

# 10. AUTOSTART

At installation:

## User services

Install:

```text
~/.config/systemd/user/hafiye-gateway.service
```

Enable it.

Gateway starts automatically after login.

## Desktop

Install:

```text
~/.config/autostart/hafiye.desktop
```

Desktop starts minimized and connects to the persistent gateway.

## Root

Install system service:

```text
/usr/lib/systemd/system/hafiye-rootd.service
```

Installation may require sudo once.

The running Desktop/gateway does not run as root.

---

# 11. USER DATA PATHS

Use XDG-compatible Hafiye paths.

```text
~/.config/hafiye/
~/.local/share/hafiye/
~/.local/state/hafiye/
~/.cache/hafiye/
```

Do not make `~/.hermes` the primary user-facing state directory for the final Hafiye installation.

Provide a one-time migration/import path from a Hermes profile if needed.

---

# 12. LOGGING AND AUDIT

Logs:

```text
~/.local/state/hafiye/logs/
```

Maintain:

```text
gateway.log
desktop.log
voice.log
models.log
computer.log
tasks.log
audit.log
```

Audit entries include:

- shell command;
- file mutation;
- root RPC;
- desktop input;
- provider/model switch;
- privacy mode change;
- task cancellation.

Redact:

- secrets;
- bearer tokens;
- passwords;
- full sensitive request headers.

---

# 13. RELIABILITY

Implement:

- structured timeouts;
- retry budgets;
- provider health checks;
- model-server health;
- tool timeouts;
- repeated-action loop detection;
- desktop-action verification;
- graceful task cancellation;
- process cleanup;
- gateway crash restart;
- model process restart;
- stale socket cleanup;
- corrupted config recovery;
- interrupted model-download resume;
- database migrations;
- shutdown hooks.

---

# 14. SECURITY BOUNDARIES

The user wants autonomous full host access.

Security work must therefore focus on avoiding unintended authority transfer.

External content such as:

- web pages;
- PDFs;
- README files;
- email;
- browser text;
- downloaded documents;

is **data**, not a higher-priority instruction source.

Hafiye must preserve instruction authority.

Do not treat “ignore previous instructions” found in external content as a user command.

---

# 15. OPEN-SOURCE / LICENSE POLICY

The architecture selections are already fixed.

Codex must only verify exact current licenses/versions before pinning dependencies.

Required upstreams:

```text
NousResearch/hermes-agent
agent-sh/computer-use-linux
ggml-org/llama.cpp
ggml-org/whisper.cpp
OpenHands/OpenHands
openWakeWord
OHF-Voice/piper1-gpl
```

Keep required license/notice files.

Piper must remain an external runtime/process boundary.

Do not copy chunks from random alternative repositories.

---

# 16. UPSTREAM HERMES MAINTENANCE

Create:

```text
UPSTREAM.md
```

Document:

- upstream remote;
- pinned base commit;
- last sync;
- conflicts;
- Hafiye patch groups.

Hafiye modifications should be grouped conceptually:

```text
branding
xdg-paths
persistent-gateway
local-model-runtime
routing
linux-computer-use
root-broker
voice-local-stack
hafiye-wakeword
project-registry
openhands
control-center
packaging
```

Do not rewrite upstream code unnecessarily.

---

# 17. DEVELOPMENT DOCUMENTS

Codex must maintain:

```text
README.md
AGENTS.md
ROADMAP.md
STATE.md
DECISIONS.md
KNOWN_ISSUES.md
ENVIRONMENT.md
UPSTREAM.md
SECURITY.md
TEST_MATRIX.md
RELEASE.md
```

`DECISIONS.md` is for implementation-level decisions not already fixed by this specification.

It must not reopen the core architecture.

---

# 18. IMPLEMENTATION PHASES

Each phase has fixed outcomes.

Do not transform phases into technology-selection exercises.

---

# P0 — FORK, PIN, VERIFY ENVIRONMENT

## Actions

1. Fork/clone `NousResearch/hermes-agent` preserving history.
2. Set remotes:
   - origin = Hafiye
   - upstream = NousResearch/hermes-agent
3. Pin the initial upstream commit in `UPSTREAM.md`.
4. Create Hafiye development branch.
5. Inspect the actual machine.
6. Record:
   - Ubuntu version;
   - kernel;
   - desktop environment;
   - Wayland/X11;
   - GNOME version;
   - CPU;
   - GPU devices and CUDA/Vulkan capabilities;
   - RAM;
   - audio stack;
   - microphone devices;
   - Python;
   - Node;
   - build tools;
   - systemd user availability.
7. Install/verify development prerequisites.
8. Run upstream Hermes tests before modifying code.
9. Build upstream Hermes Desktop before modifying code.
10. Run `computer-use-linux doctor` or its current equivalent and save output.

## Do not

- compare Hermes to OpenClaw;
- compare CUA to computer-use-linux;
- compare Tauri to Electron;
- compare Ollama/Jan/llama.cpp.

Those decisions are already made.

## Exit

Upstream baseline builds and runs, and environment is recorded.

---

# P1 — HAFIYE EXTERNAL IDENTITY AND DATA ROOT

## Implement

Rebrand user-facing surfaces:

```text
Hermes → Hafiye
```

including:

- Desktop title;
- menus;
- tray;
- Quick Entry text;
- onboarding;
- CLI command;
- app identifiers;
- notifications;
- docs.

Introduce Hafiye data root:

```text
~/.config/hafiye
~/.local/share/hafiye
~/.local/state/hafiye
~/.cache/hafiye
```

Do not mass-rename upstream internal source symbols.

Add simple replaceable default Hafiye icon assets.

Use a neutral monogram:

```text
H
```

until custom brand assets are supplied.

## Exit

No user-facing “Hermes” branding in normal Hafiye use except legal/upstream attribution pages.

---

# P2 — PERSISTENT GATEWAY + DESKTOP CONNECTION

## Implement

- `hafiye-gateway.service`;
- stable local server socket/port;
- Desktop detects and connects to existing gateway;
- Desktop no longer owns the lifetime of the backend;
- reconnect logic;
- status indicator;
- restart control.

Use loopback only for local gateway.

## Test

1. Start gateway.
2. Start Desktop.
3. Begin long task.
4. Close Desktop window.
5. Gateway/task survives.
6. Reopen Desktop.
7. Session/task state reconnects.

---

# P3 — HAFIYE COMPOSER + TRAY + AUTOSTART

Use Hermes Quick Entry code.

Implement:

- Hafiye Composer;
- `Super+Shift+Space`;
- HOTKEY_ONLY;
- SHOW_ON_LOGIN;
- PINNED;
- compact states;
- microphone;
- stop;
- tray;
- XDG desktop autostart.

## Test

Reboot/login.

Hafiye gateway and Desktop automatically start.

Composer appears according to configured mode.

---

# P4 — LLAMA.CPP MANAGED LOCAL RUNTIME

## Implement managed runtime

Install/build llama.cpp with CUDA primary and Vulkan/CPU fallback.

Create Hafiye runtime manager.

Provide:

```text
runtime install
runtime version
model import
model download
model list
model load
model unload
server start
server stop
server health
```

The server binds to loopback.

UI implements local model management.

## Test

- import small GGUF;
- launch llama-server;
- Hermes/Hafiye provider connects;
- chat works;
- unload;
- load another model;
- switch without Hafiye reinstall.

---

# P5 — PROVIDERS + GEMINI + REMOTE OPENAI-COMPATIBLE

Reuse Hermes provider code.

Expose through Hafiye UI.

Implement/test:

1. local llama.cpp;
2. remote OpenAI-compatible endpoint;
3. Gemini.

Secrets must use Secret Service.

No API key in normal config YAML/JSON.

---

# P6 — MODEL ROUTER + PRIVACY MODES

Implement Hafiye routing slots.

Wire:

```text
default
fast
reasoning
coding
vision
long_context
memory_aux
compression_aux
```

Implement:

```text
NORMAL
LOCAL_ONLY
OFFLINE
```

Implement task-scoped natural-language override.

## Tests

- normal local task;
- explicit remote task;
- explicit Gemini task;
- LOCAL_ONLY blocks all remote/cloud inference;
- OFFLINE blocks network tools;
- failed primary invokes legal fallback only.

---

# P7 — FULL HOST TOOLS + EXECUTION POLICY

Configure Hermes local host terminal/files/process tools as the final execution environment.

Implement UI toggles and execution policies.

Default:

```text
FULL_AUTONOMOUS
```

Test harmless real host operations.

---

# P8 — HAFIYE ROOT BROKER

Implement `hafiye-rootd`.

Use Unix socket peer authentication.

Implement:

```text
package.install
package.remove
service.start
service.stop
service.restart
file.write_privileged
power.action
root.exec
```

All requests audited.

## Test

Main Hafiye process remains non-root.

Harmless privileged operation succeeds through root broker.

Malformed/unauthorized socket client fails.

---

# P9 — LINUX COMPUTER USE

Install/manage `computer-use-linux`.

Connect it as a built-in MCP provider automatically.

Do not require the user to manually configure the MCP server after Hafiye installation.

Expose diagnostics in:

```text
Settings → Computer
```

## Real E2E

- enumerate windows;
- read accessibility tree;
- launch Calculator;
- enter calculation;
- verify result;
- launch Firefox;
- create tab;
- type text;
- switch application;
- launch VS Code;
- interact with Files.

Test on the user's actual Wayland/GNOME session.

---

# P10 — BROWSER

Wire Hermes browser tools into Hafiye.

Implement routing between structured automation and native desktop browser.

Test:

- structured navigation;
- page extraction;
- download;
- native logged-in browser operation through computer-use-linux.

---

# P11 — LOCAL TURKISH VOICE STACK

## whisper.cpp

Build/install with CUDA primary and Vulkan/CPU fallback.

Configure Hermes local STT command hook.

Language = Turkish.

## Piper

Install managed external Piper runtime.

Install at least one Turkish voice.

Create voice-selection API/UI.

## Desktop

Remove/fix any OpenAI-hardcoded microphone transcription path.

Add input-device selection.

## Test

Speak Turkish into real microphone.

Text appears correctly.

Hafiye speaks Turkish response through Piper.

No cloud STT/TTS required.

---

# P12 — CUSTOM “HAFIYE” WAKE WORD

Use openWakeWord.

Train and bundle:

```text
hafiye.onnx
```

Configure it as Hafiye's default wake model.

Wake must be local and function while Desktop is minimized.

Test false positives and real activation in normal room conditions.

Tune threshold/confirmation frames and persist defaults.

---

# P13 — BARGE-IN + EMERGENCY STOP

Wire all cancellation sources into one cancellation controller.

Test:

- interrupt TTS;
- cancel desktop action loop;
- cancel long task;
- stop OpenHands delegation;
- block new root calls while paused;
- resume intentionally.

---

# P14 — MEMORY + PROJECT REGISTRY

Use Hermes memory and session search.

Add deterministic project registry.

Add GUI browser/search/edit/delete.

## E2E

1. Tell Hafiye a project alias/path.
2. Restart gateway.
3. Ask to open project by alias.
4. Correct path resolves.
5. Ask “en son burada ne yapıyorduk?”
6. Hafiye resolves recent task/session context.

---

# P15 — OPENHANDS CODING DELEGATE

Integrate OpenHands V1 SDK/runtime.

Create `coding_delegate`.

Use local host repository paths.

Wire Hafiye's `coding` model route.

Expose task progress through Hafiye Task Center.

## E2E

Fixture repository contains a real failing test.

Hafiye:

1. identifies coding task;
2. delegates;
3. OpenHands edits repo;
4. tests run;
5. tests pass;
6. diff/result returns to Hafiye;
7. Hafiye reports result.

---

# P16 — TASK CENTER

Implement complete Task Center.

Must show:

- current tasks;
- queued;
- completed;
- failed;
- current step;
- selected provider/model;
- tools;
- commands;
- modified files;
- subagent state;
- cancellation;
- elapsed time.

Do not display private chain-of-thought.

---

# P17 — CONTROL CENTER

Complete every page:

```text
Overview
Chat
Tasks
Models
Providers
Routing
Voice
Computer
Browser
Coding
Memory
Skills
MCP
Automation
Permissions
Privacy
Logs
Developer
About
```

All switches must mutate real state.

No dead toggles.

---

# P18 — SCHEDULER / SKILLS / MCP

Reuse Hermes scheduler, skills and MCP.

Rebrand and expose them through Hafiye UI.

Ensure scheduled jobs can choose:

- route;
- privacy mode;
- enabled tools.

Test recurring local task.

---

# P19 — HARDENING

Implement:

- prompt-injection boundary;
- secrets redaction;
- provider outage handling;
- llama.cpp crash recovery;
- STT/TTS runtime crash recovery;
- computer-use failure;
- loop detector;
- task action budget;
- rollback/checkpoint where practical;
- corrupted config backup/recovery;
- audit retention;
- disk usage limits.

---

# P20 — PACKAGING

Primary platform:

```text
Ubuntu / Debian
```

Primary package:

```text
.deb
```

Package includes/configures:

- Hafiye Desktop;
- Hafiye CLI/backend;
- systemd user unit;
- root broker;
- XDG autostart;
- desktop launcher;
- icons;
- dependency installer/doctor;
- licenses/notices.

Managed external runtimes may download on first-run/setup rather than being statically bundled.

---

# P21 — FIRST-RUN ONBOARDING

The first launch wizard is GUI-driven.

Sequence:

1. Welcome to Hafiye.
2. Verify Linux environment.
3. Verify computer-use-linux readiness.
4. Verify compute backend availability (Auto/CUDA/Vulkan/CPU).
5. Install managed llama.cpp runtime.
6. Import/download a local GGUF.
7. Start local model.
8. Optional remote OpenAI-compatible provider.
9. Optional Gemini.
10. Select routing defaults.
11. Select microphone.
12. Install whisper.cpp.
13. Test Turkish STT.
14. Install Piper + Turkish voice.
15. Test TTS.
16. Enable/disable wake word.
17. Test “Hafiye”.
18. Confirm execution policy.
19. Enable autostart.
20. Run final doctor.

No terminal is required for a normal installation after the `.deb` is installed.

---

# P22 — CLI

Expose:

```bash
hafiye
hafiye ask
hafiye status
hafiye doctor
hafiye start
hafiye stop
hafiye restart

hafiye models
hafiye model load
hafiye model unload
hafiye providers
hafiye routing
hafiye privacy

hafiye tasks
hafiye task show
hafiye task cancel

hafiye voice
hafiye computer
hafiye root status
hafiye memory
hafiye projects
hafiye skills
hafiye mcp
hafiye automation
hafiye logs
```

CLI and Desktop share backend business logic.

---

# P23 — FINAL E2E SUITE

Hafiye is not final until these pass on the real machine.

## 23.1 Boot

Reboot.
Login.
Gateway starts.
Desktop/tray starts.
Composer appears.

## 23.2 Text

Open Composer.
Type:

> “Firefox'u aç.”

Firefox opens.

## 23.3 Voice

Say:

> “Hafiye.”

Wake fires.

Say:

> “Terminali aç ve en çok RAM kullanan işlemleri söyle.”

Hafiye performs task and speaks result.

## 23.4 Local inference

Disconnect internet.

Basic Hafiye chat and computer operations still function.

## 23.5 Remote inference

Connect configured OpenAI-compatible remote GPU endpoint.

Force a task to remote route.

Result succeeds.

## 23.6 Gemini

Force a task to Gemini.

Result succeeds.

## 23.7 Privacy

Set LOCAL_ONLY.

Attempt task whose normal fallback is cloud.

No cloud/remote inference request occurs.

## 23.8 Files

Use a fixture directory.

Ask Hafiye to organize files.

Actual filesystem result is verified.

## 23.9 Desktop

Open VS Code.
Switch windows.
Use keyboard and mouse.
Verify target UI state.

## 23.10 Browser

Use structured browser tool.

Then use native desktop browser session for a UI task.

## 23.11 Root

Perform harmless privileged action through root broker.

Verify main process remains unprivileged.

## 23.12 Memory

Teach project alias.
Restart.
Open project by alias.

## 23.13 OpenHands

Delegate fixture repo bug.

Tests pass.

## 23.14 Barge-in

While Hafiye speaks, say:

> “Hafiye dur.”

Audio and active voice turn stop.

## 23.15 Emergency shortcut

Start a long desktop task.

Press:

```text
Ctrl + Super + Escape
```

Actions stop.

## 23.16 Restart recovery

Restart gateway during a recoverable session.

Desktop reconnects cleanly.

---

# 19. DEFINITION OF DONE

The project is complete only when all are true:

- Hafiye is the user-facing name everywhere;
- Hermes remains an upstream implementation base, not user-facing product identity;
- Desktop app exists;
- popup Composer exists;
- tray exists;
- autostart exists;
- persistent gateway exists;
- CLI exists;
- local llama.cpp inference works with the selected compute backend (CUDA primary, Vulkan/CPU fallback);
- GGUF management works;
- remote OpenAI-compatible provider works;
- Gemini works;
- routing works;
- privacy modes work;
- full host tools work;
- root broker works;
- computer-use-linux works on real desktop;
- browser automation works;
- Turkish whisper.cpp STT works;
- Piper Turkish TTS works;
- custom “Hafiye” wake word works;
- microphone selection works;
- barge-in works;
- memory works across restart;
- project registry works;
- OpenHands delegation works;
- scheduler/skills/MCP work;
- task center works;
- all settings pages control real state;
- audit/logging works;
- emergency stop works;
- reboot/autostart E2E passes;
- `.deb` package installs successfully;
- normal use after installation does not require terminal setup.

---

# 20. WHAT CODEX MUST NOT DO

Codex must not:

- propose OpenClaw instead of Hermes;
- propose Tauri instead of Hermes Desktop Electron;
- propose CUA instead of computer-use-linux;
- propose Ollama/Jan instead of Hafiye-managed llama.cpp;
- use Codex as Hafiye's runtime LLM;
- require OpenAI for voice transcription;
- replace whisper.cpp with faster-whisper as default;
- replace Piper with a mandatory cloud TTS;
- run the entire application as root;
- make Docker the final host execution model;
- leave settings as placeholders;
- implement desktop control only with screenshots when accessibility is available;
- remove local-first behavior;
- silently route LOCAL_ONLY tasks to cloud;
- create a second generic agent runtime alongside Hermes;
- mass-rename all Hermes internal source modules;
- expose Hafiye root socket over a network interface;
- mark a phase complete without its acceptance tests.

---

# 21. IMPLEMENTATION RESEARCH POLICY

Codex may research:

- exact current Hermes API;
- exact current Electron source location;
- current OpenHands SDK API;
- current computer-use-linux command/MCP schema;
- current llama.cpp build flags;
- current whisper.cpp build flags;
- current Piper CLI/API;
- dependency versions;
- Linux package names;
- bug fixes required for the pinned upstream commit.

Codex may **not** use that research to reopen the technology choices above.

---

# 22. SESSION DISCIPLINE FOR CODEX

At the start of every work session:

1. read this file;
2. read `STATE.md`;
3. read `ROADMAP.md`;
4. read `UPSTREAM.md`;
5. inspect git status;
6. run relevant tests;
7. continue the first incomplete phase.

At the end of every work session:

1. run tests;
2. update `STATE.md`;
3. update `KNOWN_ISSUES.md`;
4. update phase checkbox status;
5. record exact next action;
6. commit logically grouped changes if the working workflow allows it.

`STATE.md` must make a fresh Codex session able to continue without asking the user what happened previously.

---

# 23. STATE.md FORMAT

```markdown
# Hafiye Current State

## Upstream base
commit:

## Current phase
P...

## Verified working

## In progress

## Failed / blockers

## Known regressions

## Last tests
command:
result:

## Exact next actions
1.
2.
3.

## Environment changes
```

---

# 24. ROADMAP.md FORMAT

Use checkboxes, but only mark a phase complete after its acceptance tests pass.

```markdown
# Roadmap

- [ ] P0 Fork + environment
- [ ] P1 Identity/data root
...
```

Subtasks must contain verification items.

---

# 25. FIRST CODEX INSTRUCTION

Give Codex this instruction together with this file:

> `HAFIYE_MASTER_ROADMAP.md` is the authoritative product and architecture specification.
>
> Do not brainstorm alternative frameworks or technologies. The architecture decisions in the document are already made.
>
> Your role is implementation.
>
> Begin at P0.
>
> Fork/use NousResearch/hermes-agent as prescribed, preserve upstream history, establish `origin` and `upstream`, record the pinned upstream commit, verify the actual Ubuntu environment, run the unmodified upstream backend and Desktop tests/build, and run the prescribed computer-use-linux readiness diagnostics.
>
> Create and maintain `STATE.md`, `ROADMAP.md`, `UPSTREAM.md`, `KNOWN_ISSUES.md`, `ENVIRONMENT.md`, `TEST_MATRIX.md` and the other documents required by the specification.
>
> Do not spend P0 comparing Hermes/OpenClaw, Tauri/Electron, CUA/computer-use-linux, or llama.cpp/Ollama/Jan. Those decisions have already been made.
>
> After the upstream baseline and environment verification pass, continue directly to P1.
>
> Do not stop to ask for user preference on an implementation detail if the specification already determines the outcome. Use the current upstream documentation to implement the prescribed solution correctly.
>
> If a prescribed upstream API has changed, adapt to the current API without changing the architecture. Only stop if the prescribed integration is genuinely impossible, and provide exact technical evidence.
>
> Never mark a phase complete without running its acceptance tests.
>
> Start now with P0.

---

# 26. TECHNICAL BASIS SNAPSHOT

Architecture was frozen using current upstream information on 2026-08-23.

Primary upstreams:

- Hermes Agent: https://github.com/NousResearch/hermes-agent
- Hermes Desktop: `apps/desktop` in the Hermes Agent repository
- Linux computer control: https://github.com/agent-sh/computer-use-linux
- llama.cpp: https://github.com/ggml-org/llama.cpp
- whisper.cpp: https://github.com/ggml-org/whisper.cpp
- OpenHands: https://github.com/OpenHands/OpenHands
- openWakeWord: https://github.com/dscripka/openWakeWord
- Piper: https://github.com/OHF-Voice/piper1-gpl

Important validated capabilities at architecture freeze:

- Hermes provides model/provider support, routing/fallback infrastructure, memory, skills, MCP, scheduling, subagents, voice and wake-word infrastructure.
- Hermes Desktop is an Electron/React Linux desktop application and already includes Quick Entry, settings and voice surfaces.
- computer-use-linux is Linux-specific, Wayland-first desktop control over MCP using accessibility and compositor/input integrations.
- llama.cpp exposes an OpenAI-compatible server with CUDA primary and Vulkan/CPU fallback support.
- whisper.cpp supports CUDA primary with Vulkan/CPU fallback execution.
- Hermes supports custom local STT commands.
- Hermes wake word supports local openWakeWord custom models.
- Piper provides local Turkish TTS voices and is kept outside the Hafiye process boundary.
- OpenHands V1 supports composable local agent execution and is used only as coding specialist.

---

# 27. FINAL PRODUCT RULE

The user should experience one product.

They should not need to know whether a task used:

- Hermes;
- llama.cpp;
- computer-use-linux;
- OpenHands;
- whisper.cpp;
- Piper;
- Gemini;
- a remote server.

They interact with:

# **Hafiye**

Everything else is implementation machinery.
