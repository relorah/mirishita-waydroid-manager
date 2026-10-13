# Mirishita Waydroid Manager (MWM) 0.83 Setup Guide

MWMは、Waydroid上のミリシタの描画・表示・入力設定を管理するツールです。

## 対象環境

- CachyOS／Arch系Linux、x86_64、Wayland。
- Waydroid Android 11、Google Play、Native Bridge／ARM変換を導入済みで、ミリシタが正常動作すること。
- sudo権限と、依存パッケージ取得用のネットワーク。

描画バックエンドはGamescopeです。主な動作確認環境はKDE Plasma／WaylandとAMD GPUです。

## 導入するもの

ホストへ依存パッケージ、本体、ランチャー、限定した管理処理を行うroot helperとsudoers設定を導入します。Waydroidには描画ライブラリをoverlayとして導入し、表示・入力・RTScaleなどの設定を変更します。

RTScaleは、mogareta7731氏が公開した原機能とライブラリの挙動を参考に解析・再構成し、Mesaへ組み込んだMWM独立実装を使用します。描画部品の出典・版は `payload/manifests/graphics-stack.lock`、ライセンスは `LICENSES/` に記載しています。

MWMは非公式ツールです。動作や利用規約への適合を保証しません。利用者の判断で使用し、重要なデータは事前に保全してください。

## インストール・更新

ゲームとMWMを終了し、配布ファイルを展開したフォルダーで実行します。

```bash
chmod +x install.sh
./install.sh
```

既存環境と同梱ファイルを確認し、変更対象をバックアップしてから導入します。更新時は保存設定と初回バックアップを保持します。バックアップ取得に失敗した場合は、描画ファイルを変更する前に中断します。

描画ライブラリも更新する場合は上記を、本体・制御スクリプト・root helperのみ更新する場合は次を使います。

```bash
./install.sh --update-app
```

導入後にGUIを開かない場合は `--no-gui` を追加します。必要な依存パッケージはインストーラーが導入します。

## 基本操作

アプリメニューのMirishita Waydroid Manager、または `~/.local/bin/mwm` で起動します。

1. Homeで描画・表示・Optionsを設定します。
2. **Apply**で保存します。
3. **Start**で起動します。起動中は**Restart**になります。

ApplyはMWMの設定保存と、起動状態に応じたFPS Counterの更新を行います。AndroidとGamescopeへ描画・表示設定を反映するには、Start／Restartを押してください。Restartはプレイ中のゲームも終了します。未保存の変更がある間はStart／Restartを押せません。

初期値はRTScale OFF、AMD FSR1 OFF、Aspect Ratio Auto、FPS Counter Offです。Optionsの4項目はONです。準備確認後にミリシタを自動起動し、MWMを最小化します。

Reset to Defaultsは画面上の設定を初期値へ戻します。Applyで保存してください。Cancelは設定画面を閉じます。

## 描画・表示設定

| 項目 | 内容 |
| --- | --- |
| RTScale | OFF／x1～x10。重い場面では倍率を下げてください。 |
| AMD FSR1 | Gamescopeによる拡大（EASU）とシャープニング（RCAS）。OFFで下位項目をグレーアウトします。 |
| Upscale | 125%／150%／175%／200%。初期選択は150%。RTScale併用時の175%／200%は実機確認待ちです。 |
| Sharpness | 1～21。1が最小強度、21が最大です。 |
| Aspect Ratio | Auto／32:9／21:9／16:9／4:3／3:2／Custom Width。Custom Widthは320～7680、基準高さ720。 |

RTScale ONではWaydroid表示を高さ1080相当とし、RTScaleの基準寸法は別に高さ720で管理します。OSスケール、表示寸法、RTScale倍率は別の設定です。

拡大倍率を高くすると負荷が増え、描画の乱れやフレーム落ちが発生することがあります。シャープニングを強くすると輪郭の強調やちらつきが目立つ場合があります。

Super（Windows）＋Fで全画面とウィンドウを切り替えます。複数モニターでは、Waydroid起動時にカーソルがある画面へ表示されます。使用したい画面にカーソルを移してStart／Restartを押し、表示されるまでその画面に置いてください。

## Options

| 項目 | 内容 |
| --- | --- |
| Verify Waydroid Startup | Android起動・設定反映・解像度・表示の継続を確認します。OFFでは必須設定の反映後、表示確認と安定待機を省略します。 |
| Auto Launch Mirishita | 準備確認後にミリシタを自動起動します。Verify OFFではグレーアウトし、手動起動になります。 |
| Mouse as Touch | マウス操作をAndroidのタッチ入力として扱います。 |
| RTScale Zoom Fix | RTScale使用時の過度な拡大や描画範囲のずれへの互換設定です。 |

Verify ONの準備中はMWMの操作を制限します。途中でミリシタを手動起動すると処理を中断するため、ゲームを終了してStart／Restartをやり直してください。Auto Launch OFFでは準備完了後に手動起動します。

Optionsの変更もApply→Start／Restartで反映します。

## FPS Counter

Off／Minimal／Detailed／MangoAppから選択します。MinimalとDetailedはMWM HUD、MangoAppはGamescope内のカウンターです。

| 数値 | 計測対象 |
| --- | --- |
| FPS：全方式 | SurfaceFlingerのミリシタ描画レイヤーの実表示時刻から計算する、Android側の表示更新頻度。MangoAppは整数に丸めます。 |
| Frametime：Detailed | Android側の直近の有効なフレーム間隔。 |
| グラフ：MangoApp | Gamescope側のフレーム時間。FPS欄とは計測箇所が異なります。 |
| CPU／GPU | ホスト側の負荷。ミリシタ単体の使用率ではありません。 |

FPSはゲーム内部の描画回数やモニターの最終表示FPSとは区別されます。更新タイミングにより表示値が異なる場合があります。取得できない場合はMWM HUDで `--.--`、MangoAppで `--` を表示します。

MWM専用MangoAppを同梱しています。表示順はGPU→CPU→FPS→グラフです。対応セッションでは起動中に表示方式を切り替えられます。設定ファイルの直接編集は起動・切り替え時に上書きされます。ソース・ライセンス・ビルド方法は `mwm/vendor/mangoapp/BUILD.md` を参照してください。

### BC250のGPU使用率（試験機能）

標準値が655%などになる環境向けに、GPU全体の活動率を推定する計測機能があります。MWM HUDとMangoAppが同じ計測キャッシュを使用し、更新時も有効化状態を保持します。

手動で有効にする場合は次を実行し、HUDを起動し直してください。無効にする場合は同じファイルを削除します。

```bash
mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}/mwm"
touch "${XDG_CONFIG_HOME:-$HOME/.config}/mwm/bc250-gpu-test"
```

## 診断ログ

MaintenanceのDoctorで環境を確認できます。**Save Diagnostic Log**で診断情報を1ファイルへ保存できます。

```text
~/.local/share/mwm/logs/mwm-yyyyMMdd-hhmmss.log
```

RTScale Debugでは診断情報の表示・更新・コピー・クリアができます。ログにはユーザー名・パスなどが含まれるため、共有前に内容をご確認ください。XDGの保存先を変更している場合は、その配下へ保存します。

## バックアップ・アンインストール

初回導入時に、MWMが変更する描画ファイルと表示・入力・音声・RTScale設定を保存します。バックアップ先は `/var/lib/mwm-backups/<UID>/baseline/` です。更新や配布フォルダーの削除後も保持します。復元対象はMWMによる変更箇所で、アプリ・ゲームデータは保持します。

Maintenanceの**Uninstall MWM**を押すか、配布ファイルの展開先で実行します。

```bash
chmod +x uninstall.sh
./uninstall.sh
```

- バックアップあり：変更したファイル・設定を復元し、成功後にMWMを削除します。
- バックアップなし：確認後にMWMのみ削除します。Waydroidの現在の描画環境・設定は保持します。
- バックアップ破損・環境不一致・復元失敗：エラーを表示し、MWMを保持して中断します。

MWM本体、設定、ログ、ランチャー、専用生成物、ユーザー用sudoers設定を削除します。root helperは他ユーザーが利用していなければ削除します。共有の依存パッケージと復旧用バックアップは保持します。
