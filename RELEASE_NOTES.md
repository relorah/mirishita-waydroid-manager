# MWM 0.80

## 0.80：配布構成の整理

- root helperとバックアップ処理をpackaging/へ移動し、インストーラーの参照先を更新。
- 配布ZIPからGit管理用ファイルと開発者向けAGENTS.mdを除外。
- アプリのバージョン番号は0.80を維持。


- RTScale x1-x10 can combine with FSR1 125% or 150%.
- MWM HUD FPS now uses Android game-layer actual presentation timestamps instead of desired timestamps.
- MangoApp displays the same Android-layer FPS measurement through its external-text element; its frametime graph remains Gamescope-derived.
- SETUP describes measurement differences, RTScale provenance, and high-setting rendering limitations.
- Linux runtime validation of the changed MangoApp presentation remains pending.

## MWM 0.77

- Based on the independent RTScale build with the revised Home and Maintenance UI.
- Verify Waydroid Startup is in Options (default ON); OFF disables automatic game launch and skips presentation verification.
- Start/Restart follows the live Gamescope and Waydroid session status.
- Games tab is hidden.
- README and SETUP guide updated.
- Linux runtime validation of these changes remains pending.

## Baseline development notes

# MWM 0.75.2

Options: Auto Launch Mirishita, Mouse as Touch, RTScale Zoom Fix.
Auto launch runs only after settings and display verification. Existing saved choice is retained; missing choice defaults to ON.
Targeted backup, uninstall, and MangoApp integration retained.
Linux runtime verification pending.

Successful automatic launch minimizes MWM without a completion popup. Manual mode and failure notifications are retained.

Independent RTScale test: source-built graphics stack, preserving0.75.2 application changes. Not a full equivalence claim or public release.
