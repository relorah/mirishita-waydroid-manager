# AGENTS.md

## Environment

- Target host OS: CachyOS
- Shell examples and scripts must use Bash.
- Do not write fish-specific commands.
- Target Android environment: Waydroid Android 11.
- Mirishita package:
  `com.bandainamcoent.imas_millionlive_theaterdays`
- Primary GPU target: AMD Radeon.
- BC250 may also be used for testing.

## Display / Rendering

- Target display refresh rate: 120 Hz.
- Mirishita target frame rate: 60 fps.
- If frame generation is used, prefer 60 → 120 fps (2x).
- RTScale test range:
  - OFF
  - x2
  - x3
  - x4
  - x5
  - x6

## NativeBridge

Reference configuration:

- Houdini
- test_libnb

Treat Houdini as the currently supported ARM translation path.

Do not include proprietary Houdini binaries or WSA images in this repository.

libndk_translation may be investigated later, but treat it as experimental unless explicitly documented otherwise.

## RTScale

The project uses Mesa GLES Render Scale (RTScale) based on work by mogareta7731.

- Preserve upstream attribution and license information.
- Keep upstream-derived code clearly separated from project-owned code.
- Document local modifications.
- Do not present upstream RTScale work as original work of this repository.

## Hardware Tuning

Do not add general CPU/GPU clock, voltage, governor, or power-limit control to this project.

For BC250 systems, hardware tuning should be handled by `bc250-toolkit`.

## Safety

Prefer reversible changes.

Before replacing or modifying:

- Waydroid system/vendor images
- Mesa libraries or overlays
- NativeBridge libraries
- test_libnb
- configuration files

create or verify a backup first.

Do not silently delete user data.

Do not overwrite a known-working configuration without a restore path.

## sudo / Root

Use elevated privileges only when required.

- Do not assume passwordless sudo.
- Do not add `NOPASSWD` rules.
- Keep privileged operations narrow.
- Inspect existing state before modifying it.

## Bash

Use:

```bash
#!/usr/bin/env bash
```

For non-trivial scripts, prefer:

```bash
set -Eeuo pipefail
```

when appropriate.

After modifying Bash scripts:

- Run `bash -n`.
- Run `shellcheck` if available.
- Fix meaningful warnings or document why they are intentionally ignored.

## Git

Keep changes small and reviewable.

Before considering a task complete:

- Run relevant validation or tests.
- Run `git status`.
- Review `git diff`.
- Summarize what changed.
- State what could not be tested.

Do not:

- mix unrelated changes into one task,
- rewrite Git history,
- force-push,

unless explicitly requested.

## Dependencies

Prefer pinned or known-working revisions for critical dependencies.

Possible external dependencies include:

- Waydroid
- waydroid_script
- test_libnb
- Mesa
- Mesa GLES Render Scale (RTScale)

Keep upstream origin and license information documented.

## Documentation

Documentation must distinguish between:

- confirmed behavior,
- unverified behavior,
- experimental behavior.

When a procedure is successfully validated, update the relevant documentation.

## MWM

Mirishita Waydroid Manager (MWM) should be a frontend for tested backend operations.

Prefer this order:

1. Document the manual procedure.
2. Implement and test the backend operation.
3. Make it reversible and idempotent where practical.
4. Expose it through MWM.

Do not place critical setup logic only inside the GUI.

## Diagnostics

Prefer detection over assumptions.

Where practical, diagnostics should report:

- Waydroid status
- Android version
- Mirishita installation status
- Android / application ABI
- NativeBridge status
- Houdini status
- test_libnb status
- Mesa renderer
- RTScale status and multiplier
- display refresh rate
- relevant logs
