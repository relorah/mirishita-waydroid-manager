# AGENTS.md

## Project Scope

This repository is for **Mirishita Waydroid Manager (MWM)**.

MWM manages an **already working** Mirishita environment on Waydroid. It is not a general Waydroid installer and it must not absorb initial Android / Google Play / Native Bridge setup into the public manager.

The expected starting state is:

- CachyOS
- KDE Plasma / Wayland
- x86_64 host
- Waydroid Android 11 (x86_64)
- working Waydroid network connectivity
- working Native Bridge environment
- Mirishita already installed and able to launch
- Mirishita package:
  `com.bandainamcoent.imas_millionlive_theaterdays`

Public MWM must **not**:

- install Waydroid itself,
- initialize or download Waydroid Android images,
- configure Google Play,
- install Mirishita,
- install or bundle proprietary Native Bridge payloads,
- bundle Houdini binaries,
- solve initial Waydroid network setup as an MWM runtime feature.

Initial-environment tooling, if developed, belongs outside the public MWM runtime.

## Shell / Host Environment

- Shell examples and scripts must use **Bash**.
- Do not write fish-specific commands.
- Use:

```bash
#!/usr/bin/env bash
```

- For non-trivial scripts, prefer:

```bash
set -Eeuo pipefail
```

when appropriate.

After modifying Bash scripts:

- run `bash -n`,
- run `shellcheck` when available,
- fix meaningful warnings or document why a warning is intentionally ignored.

## Waydroid / Android

Current MWM target:

- Waydroid Android 11
- x86_64
- Mirishita package:
  `com.bandainamcoent.imas_millionlive_theaterdays`

MWM should detect the actual state before making changes.

Do not use Android `wm size` override for MWM display presets.

MWM display handling should use Waydroid display properties and keep `multi_windows=false`.

## Mesa GLES Render Scale

The project uses **Mesa GLES Render Scale / Render Target Scale (RTScale)** based on work by **mogareta7731**.

Primary upstream references:

- https://zenn.dev/mogareta7731/articles/82f3f0d9567abc
- https://note.com/mogareta7731/n/n4db668be92b5

Rules:

- Preserve upstream attribution and license information.
- Do not present upstream RTScale work as original MWM work.
- Keep project-owned code clearly separated from upstream-derived components.
- Document local modifications and build provenance.
- Preserve relevant upstream LICENSE / NOTICE / copyright information.
- Do not describe the entire vendor overlay as a work authored by mogareta7731.
- Treat each bundled upstream component according to its own license.

### MWM RTScale profile

Mirishita RTScale base resolution is fixed at:

```text
1316x720
```

This is independent of the Waydroid display resolution.

Supported scale choices:

```text
OFF
x1
x2
x3
x4
x5
x6
x7
x8
x9
x10
```

Current initial value:

```text
x3
```

Do not describe x3 as universally optimal. Suitable scale depends on hardware and content.

Expected Mirishita profile:

```ini
schema_version=1

[application.0]
name=com.bandainamcoent.imas_millionlive_theaterdays
base_width=1316
base_height=720
scale=3
surface=1
texelsize=0
```

Render Scale changes require a Waydroid restart for reliable application.

## RTScale Vendor Overlay

The public package may contain:

```text
payload/rtscale-vendor-overlay.tar.zst
```

This overlay is built / assembled for Waydroid using the RTScale implementation and build information published by mogareta7731 together with upstream third-party components.

Current overlay provenance must be documented for bundled components such as:

- Mesa-derived libraries,
- libdrm / libdrm_amdgpu,
- LLVM,
- GBM / gralloc-related components.

Do not assume a single license covers the full archive.

Where possible, record for each binary:

- upstream project,
- source repository,
- source commit / tag,
- build procedure,
- license,
- SHA256.

If exact provenance of a binary is unknown, say so explicitly. Do not invent a source revision or license conclusion.

## Display

MWM display presets:

```text
Auto (Full Screen)
32:9 (2560x720)
21:9 (1680x720)
16:9 (1280x720)
4:3 (960x720)
3:2 (1080x720)
Custom Width (x720)
```

Rules:

- fixed presets always use height `720`,
- custom mode changes width only,
- custom width range is currently `320-7680`,
- `Auto (Full Screen)` follows the host display,
- do not use Android `wm size` override,
- do not confuse Waydroid display resolution with the RTScale base `1316x720`.

## Mouse as Touch

MWM uses:

- Waydroid `persist.waydroid.fake_touch`,
- `/dev/uinput`,
- `MWM Virtual Touchscreen`.

For fixed display presets, touch coordinates may require mapping to the selected Waydroid display size.

For `Auto (Full Screen)`, do not apply the fixed-preset coordinate correction.

Do not silently replace or reconfigure unrelated host input devices.

## Performance Overlay

The GUI option is named:

```text
Performance Overlay
```

It replaces the older FPS-only concept.

Displayed metrics, in this order:

```text
FPS
CPU
GPU
```

Definitions:

- **FPS**: Mirishita rendering FPS.
- **CPU**: CachyOS host-wide CPU utilization, derived from `/proc/stat`.
- **GPU**: AMD GPU-wide utilization, using `gpu_busy_percent` when available.

These are not Mirishita-only CPU / GPU utilization values.

Update interval:

```text
0.2 sec
```

Display modes:

- `Text`
- `Graph`

Text mode shows three vertical lines.

Graph mode shows FPS / CPU / GPU as three vertical history rows and keeps roughly 12 seconds of history at the standard update interval.

GUI layout:

- `Performance Overlay` checkbox,
- `Text / Graph` selector on the same row,
- selector is disabled / greyed out while the overlay checkbox is OFF.

Position and text size are fixed in the MWM GUI unless a future requirement explicitly changes this.

Do not add heavy plotting dependencies for the runtime overlay. Prefer the existing GTK / Cairo path.

For AMD multi-GPU systems, do not blindly assume `card0`. Detect the appropriate amdgpu device where practical.

## Waydroid Audio Level

The GUI option is named:

```text
Waydroid Audio Level
```

Do not call it `Waydroid Audio Fix`.

When enabled, it normalizes only the Waydroid-related audio levels:

```text
Android media volume = 15 / 15
Waydroid PipeWire stream = unmuted
Waydroid PipeWire stream volume = 100%
```

It must not change:

- KDE global master volume,
- unrelated application volumes,
- DAC / hardware volume.

The PipeWire stream may appear only after Waydroid / Mirishita starts, so the implementation may wait for the target stream before applying values.

## Network

Initial Waydroid networking problems are outside the MWM runtime scope.

Do not add a `Waydroid Network Fix` checkbox to MWM.

Network diagnostics may be useful for troubleshooting, but public MWM should assume that network connectivity already works because Mirishita installation and initial setup happen before MWM.

## UI Conventions

Current main UI concepts include:

- Mesa GLES Render Scale
- Display
- Performance Overlay
- Mouse as Touch
- Waydroid Audio Level
- Maintenance

Keep actual MWM setting / tab names in English in user documentation when they correspond directly to GUI labels.

Bottom buttons:

- left: `Apply & Refresh`
- right: `Cancel`

`Apply & Refresh` applies settings, restarts Waydroid as required, and launches Mirishita.

Avoid unnecessary completion popups.

Keep the interface compact.

## sudo / Root

Use elevated privileges only when required.

MWM uses a restricted helper:

```text
/usr/local/libexec/mwm-root-helper
```

Passwordless sudo is acceptable **only** for this narrowly scoped, validated helper through a dedicated sudoers rule.

Rules:

- never grant broad `NOPASSWD` access to Python, shell, tar, arbitrary commands, or user-controlled command lines,
- validate helper actions and arguments,
- keep the allowed operation set small,
- do not use unrestricted passwordless sudo,
- use `sudo -n /usr/local/libexec/mwm-root-helper ...` for approved runtime operations,
- inspect existing state before modifying it.

Installer-time `sudo -v` may be used while privileged installation work is active.

## Installer

The public MWM installer is for an existing working environment.

It may:

- verify Waydroid / Android 11,
- verify Mirishita package presence,
- verify Native Bridge state,
- configure `/dev/uinput` access,
- install the RTScale vendor overlay,
- install the restricted root helper,
- install MWM,
- install the KDE launcher,
- perform final verification.

It must not:

- initialize Waydroid,
- download Android images,
- install Google Play,
- install Native Bridge,
- install Mirishita,
- bundle proprietary Native Bridge binaries.

Installer changes should be idempotent where practical.

## Native Bridge

Native Bridge is a prerequisite, not an MWM-managed component.

MWM may detect and report Native Bridge state.

The public repository must not bundle proprietary Houdini binaries or other proprietary ARM-translation payloads.

`test_libnb` may be detected and documented, but installation of the Native Bridge environment is outside public MWM setup.

Do not imply that MWM authors own or license proprietary Native Bridge components.

## Hardware Tuning

Do not add general CPU / GPU clock, voltage, governor, or power-limit control to MWM.

For BC250 systems, hardware tuning should be handled by `bc250-toolkit`.

MWM may report performance metrics but should not become a hardware tuning frontend.

## Safety / Reversibility

Prefer reversible changes.

Before replacing or modifying important Waydroid / overlay / configuration state:

- inspect current state,
- create or verify a backup where appropriate,
- preserve a restore path.

Do not silently delete user data.

Do not overwrite a known-working configuration without a recovery path.

## Backup / Restore

MWM backup / restore should cover MWM-managed settings only unless explicitly documented otherwise.

Do not imply that MWM backup is a full Waydroid / Android application-data backup.

When adding a setting, consider whether it must also be added to backup / restore.

## Diagnostics

Prefer detection over assumptions.

Where practical, Doctor / diagnostics should report:

- Waydroid status,
- Android version,
- Mirishita installation status,
- Android / application ABI,
- Native Bridge status,
- Mesa / RTScale status,
- RTScale multiplier,
- display configuration,
- Mirishita launch / foreground state,
- MWM configuration state.

Do not install or repair Native Bridge from Doctor.

## Documentation

Canonical user-facing documentation should distinguish:

- confirmed behavior,
- unverified behavior,
- experimental behavior.

The public documentation should clearly state:

- MWM does not modify the Mirishita APK / game program itself,
- MWM is unofficial and unaffiliated with the game provider and upstream projects,
- MWM is experimental and may modify host / Waydroid configuration,
- use is at the user's own risk,
- upstream components retain their own licenses.

Keep the short RTScale attribution near the beginning of SETUP documentation and detailed credits / license information later in the document.

Primary RTScale source references should include both the Zenn and note articles listed above.

Repository and packaged documentation should use the same canonical `README.md` / `SETUP.md` content where practical.

## Git / Development Workflow

Keep changes small and reviewable.

Before considering a task complete:

- run relevant validation / tests,
- run `git status`,
- review `git diff`,
- summarize what changed,
- state what could not be tested.

Do not:

- mix unrelated changes into one task,
- rewrite Git history,
- force-push,

unless explicitly requested.

## Dependencies

Prefer pinned or known-working revisions for critical dependencies.

For third-party components, preserve:

- upstream origin,
- version / revision where known,
- license,
- build provenance,
- local modifications.

Do not add a binary dependency to a public release without documenting where it came from and under what terms it is redistributed.
