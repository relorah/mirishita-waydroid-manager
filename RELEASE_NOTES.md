# 未リリース：整数FPSと小さいFPS単位

- 表示は赤いFPSラベル、CPU/GPUと整数部分を揃えた数値、右上の小さいFPS単位。
- 表示だけ四捨五入。SurfaceFlinger実測値とキャッシュの精度は維持。
- 整数表示・座標テストと読込／設定生成／専用MangoApp選択の5テスト通過。
- 実機での最新表示は確認待ち。

# 未リリース：MangoApp FPS行の修正

- v0.80の幅285・高さ200・基本文字サイズ29を復元。
- 実測FPS取得経路を維持し、`custom_text=FPS`と数値のみの`exec`でラベル／数値を別列に配置。
- MangoHud 0.8.4のexec描画が使用する`font_size_secondary=29`を明示。
- キャッシュ異常・鮮度、設定生成、外部コマンド実行、パスの引用を回帰テスト。
- BC250での表示・切替・Verify ON/OFFは未検証。バージョン変更・push・Releaseなし。

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


追補：画像で文字サイズ・欠けの改善を確認。表示順はv0.80以前のGPU→CPU→FPS→グラフへ復元。


FPS途切れ対策：MangoHud 0.8.4のShell::readOutputは50ms後に非同期出力を読む。Python起動が遅れると空文字でFPS欄を上書きするため、execの読込を軽量Bashスクリプトmangoapp-fps-text.shへ変更。計測・キャッシュ生成は変更なし。開いたファイルの鮮度（2秒）と0超240以下の値を検証する。Bash 5とGNU statが必要（CachyOS対象）。50ms読込検証30回で空出力0回、回帰テスト4件通過。shellcheckは環境に未導入。実画面の連続動作は要確認。


起動待機の案内を「ミリシタが起動するまでお待ちください。」に変更。CPU/GPUはMWM HUDが小数点1桁、MangoHud 0.8.4標準欄は整数。FPSは実測値を小数点2桁で表示し、欠損・期限切れ時は--.--。


FPSの整数部分の右端をCPU/GPUの数値へ揃えるため、MWM専用のMangoApp v0.8.4ビルドを同梱。小数部分は右へ続けて描画します。システム版は置換しません。実フォントの座標テスト（9.99／60.00／120.00／240.00／--.--）通過。ソース・ライセンス・ビルド情報は`mwm/vendor/mangoapp/BUILD.md`参照。実測FPS取得とCPU/GPU整数表示は維持。実画面の確認は未完了。


表示更新：MangoAppのFPS数値は整数へ四捨五入し、右上に小さくFPSを表示します。整数部分の右端はCPU/GPUの数値へ揃えます。取得・キャッシュは従来どおり小数点2桁の実測値で、描画だけを変更。取得不能は-- FPS。


追加表示調整：赤いFPSラベル・整数実測FPS・右上の小さいFPS単位。2桁の数値を基準に、ラベル→数値と数値→温度の空白をそれぞれ80%へ縮小。外枠サイズと外側の余白は変更しません。座標・整数表示・間隔テスト通過、実画面は確認待ち。
