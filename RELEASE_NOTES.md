# MWM 0.82

## 0.82：MangoAppレイアウトを0.80系へ寄せる（実機検証待ち）

- v0.80の固定サイズ・3列レイアウトを復元し、幅320・高さ230へ拡大して文字の重なりを軽減する意図の調整。
- v0.81で動作確認した`legacy_layout=0`と`exec`によるミリシタ実測FPS表示を維持。
- 文字サイズは24で統一。GPU使用率の655%等のBC250固有の異常値は別問題として未修正。
- BC250実機での変更後レイアウト、Verify ON/OFFの回帰テストは未実施。GitHub Releaseは未作成。

# MWM 0.81

## 0.81：MangoApp実測FPS表示の修正（実機再検証待ち）

- MangoAppの`legacy_layout=0`を明示し、Android実測FPSを`exec`で表示する経路を維持。
- BC250上の最小設定で、MangoAppの固定文字列とミリシタ実測FPS（60.06 FPS）が表示できることを確認。
- 以前の固定幅・高さ・3列設定を外し、数値表示領域が制限されないよう調整。CPU/GPU情報とフレームタイムグラフは維持。
- Verify Waydroid Startup ON/OFFでFPS欄が欠落した現象への対応。変更後のフル設定を使った実機回帰テストは未実施。
- GitHubソース更新であり、GitHub Releaseや安定版の宣言ではない。

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
