# MWM 0.81 Setup Guide

MWM（Mirishita Waydroid Manager）は、Waydroidでミリシタをプレイできる環境に、RTScaleとGamescopeによる描画設定、表示設定、診断機能を追加するツールです。このガイドは独立RTScale実装版を対象とします。

## 配布フォルダー

ZIPの展開先は `MWM_v0.81/` です。展開先で `install.sh` を実行します。

| ファイル・フォルダー | 用途 |
| --- | --- |
| `install.sh` / `uninstall.sh` | インストール・アンインストールの入口 |
| `README.md` / `SETUP.md` / `RELEASE_NOTES.md` | 概要・使い方・変更履歴 |
| `MWM.py` | 展開先からアプリを開くための入口 |
| `mwm/` | アプリ本体・設定・内部処理 |
| `packaging/` | インストーラー用のroot helper・バックアップ処理 |
| `payload/` | 描画ライブラリ・初期設定・出典とチェックサム |
| `LICENSE` / `LICENSES/` | MWMと同梱部品のライセンス |
| `VERSION` | 配布版の番号 |

## 対象環境

- CachyOS／Arch系Linux、x86_64、Waylandセッション。
- Waydroid Android 11。Google Play、Native Bridge／ARM変換、ミリシタを準備し、通常起動でプレイできること。
- sudoによる管理者認証と、依存パッケージ取得用のネットワーク。
- 描画バックエンドはGamescope。開発時の主な確認環境はKDE Plasma／WaylandとAMD GPUです。

MWMは非公式の独立プロジェクトです。各サービスの規約への適合や動作を保証するものではありません。利用者の判断で使用し、重要なデータは事前に保全してください。

## 導入するものと変更範囲

インストーラーはホストへ依存パッケージを追加し、Waydroidの描画ファイルをoverlayとして導入します。MWMの設定反映では、Androidの表示寸法、入力、RTScale設定などを変更します。限定された管理処理を行うroot helperと、ユーザーごとのsudoers設定も導入します。

MWMでは、mogareta7731氏が公開したRTScaleの機能とライブラリの挙動を参考に、解析・再構成してMesaへ組み込んだ独立実装を使用します。各描画部品の出典と版、バイナリのチェックサムは `payload/manifests/graphics-stack.lock` に記録し、ライセンス文は `LICENSES/` に収録しています。対応する描画ソースと再ビルド手順は準備後に追加します。

## インストール

ゲームと既存のMWMを終了し、配布ファイルを展開したフォルダーで実行します。

```bash
chmod +x install.sh
./install.sh
```

インストーラーは同梱payloadのチェックサム、既存Waydroid、Android 11、ミリシタの存在を確認します。その後、変更対象のバックアップを取得し、描画ファイル、本体、root helper、ランチャーを導入します。既存の保存設定は保持します。

主な依存パッケージはpython、pyside6、gtk3、gtk-layer-shell、python-gobject、python-cairo、polkit、zstd、rsync、gamescope、qt6-toolsです。KDEでは利用可能なAURヘルパーを使ってkdotoolの導入を試みます。MangoApp用にmangohudの導入も試みます。

インストール後にGUIを開かない場合は次を使います。

```bash
./install.sh --no-gui
```

バックアップ取得に失敗した場合は、描画ファイルを変更する前に導入を中断します。表示された詳細を確認してください。

## 更新

描画ファイルも更新する場合は通常インストールを実行します。

```bash
./install.sh
```

本体、制御スクリプト、root helperを更新する場合は次を使います。

```bash
./install.sh --update-app
```

この更新は導入済みMWMを対象とし、既存の描画payloadと保存設定を保持します。初回バックアップは検証して再利用します。ISO由来の版から独立実装版へ切り替える場合は、通常インストールで描画ファイルも更新してください。

GUIを開かず更新する場合は次を使います。

```bash
./install.sh --update-app --no-gui
```

## 起動と基本操作

アプリメニューのMirishita Waydroid Manager、または次のコマンドで起動します。

```bash
~/.local/bin/mwm
```

1. HomeでRTScale、AMD FSR1、Aspect Ratio、FPS Counter、Optionsを設定します。
2. **Apply**を押して保存します。
3. **Start**を押して保存した設定で起動します。起動中の表示は**Restart**になります。
4. 初期設定では準備確認後にミリシタを自動起動し、MWMを最小化します。

Start／Restartの表示はGamescopeとWaydroidセッションの状態を確認して更新します。外部から終了した場合も、次の状態確認でStartへ戻ります。表示確認は通常2秒間隔です。

初期値はRTScale OFF、AMD FSR1 OFF、Aspect Ratio Auto、FPS Counter Offです。Verify Waydroid Startup、Auto Launch Mirishita、Mouse as Touch、RTScale Zoom FixはONです。

Reset to Defaultsは確認後に画面上の設定を初期値へ戻します。Applyで保存してください。CancelはMWMの設定画面を閉じます。保存済み設定と起動中の描画セッションは保持します。

## ApplyとStart／Restart

| 操作 | 保存・反映する内容 |
| --- | --- |
| Apply | RTScale、AMD FSR1、Aspect Ratio、FPS Counter、Optionsの選択をMWM設定へ保存。FPS Counterは起動状態に応じて表示を更新。 |
| Start／Restart | 保存した設定を基にGamescopeとWaydroidを起動・再起動し、Androidの表示・入力・RTScale設定を適用。Verifyの選択に応じて準備確認と自動起動を実行。 |

未保存の変更がある間はStart／Restartを無効にします。Apply後には約0.5秒の待機があります。RTScale、FSR、解像度などの変更をゲームへ反映するには、保存後にStart／Restartを押してください。

## Options

### Verify Waydroid Startup

初期値はONです。Androidの起動、設定の反映、解像度、表示、セッションの継続を確認します。準備中は日本語の案内を表示し、MWMの操作を制限します。

準備中に外部ショートカットやAndroidホームからミリシタを起動すると、その起動を検出して処理を中断します。設定が一部だけ反映されている可能性があるため、ミリシタを終了し、Start／Restartを押してやり直してください。

OFFは、RTScaleやFSRの切り替えなど、挙動を把握した利用者向けの確認用設定です。Start／Restartを押すと、実行中のMWM管理下のGamescopeとWaydroidセッションを終了して起動し直します。プレイ中のゲームも終了します。

OFFでもAndroidの起動と必須設定の書き込み・読み戻しを行います。その後の表示準備確認と安定待機を省略し、ミリシタは手動起動になります。Auto Launch Mirishitaはグレーアウトし、保存済みの選択は保持します。準備中・準備完了のポップアップは省略します。Android起動に要する時間は環境によって変わります。

### Auto Launch Mirishita

初期値はONです。VerifyがONの場合、設定反映と準備確認の後にミリシタを自動起動します。自動起動成功時はMWMを最小化します。

OFFでは準備完了の案内を確認後、Androidホームやショートカットからミリシタを手動起動してください。

### Mouse as Touch

Androidのfake_touch設定でマウス操作をタッチ入力として扱います。変更後はApply→Start／Restartで反映します。

### RTScale Zoom Fix

RTScale使用時に、一部の画面や演出が過度に拡大されたり、描画範囲がずれたりする問題への互換設定です。初期値はONです。

変更後はApply→Start／Restartで反映します。ミリシタや描画部品の更新によって効果や互換性が変わる可能性があります。

## 描画設定

### RTScale

OFF、x1～x10を選択します。設定はAndroid内の`/data/local/tmp/gles_rtscale.conf`へ反映し、読み戻して確認します。重い場面で問題があれば倍率を下げてください。

RTScale OFFでは高さ720、ONでは高さ1080相当のWaydroid表示寸法を使い、RTScale用の基準寸法は別に高さ720で管理します。OSのスケール、Waydroidの表示寸法、RTScale倍率はそれぞれ別の設定です。

### AMD FSR1

GamescopeによるFSR1の拡大処理（EASU）とシャープニング（RCAS）をまとめて有効にします。チェックOFFではUpscaleとSharpnessをグレーアウトします。

| RTScale | Upscale |
| --- | --- |
| OFF | 125%／150%／175%／200% |
| x1～x10 | 125%／150% |

Sharpnessは1～21です。1が最小強度、21が最大強度です。変更後はApply→Start／Restartで反映します。

RTScaleの倍率、FSR1のアップスケーリング倍率（EASU）、シャープニング強度（RCAS）が高い場合、描画の乱れやちらつき、フレーム落ちが発生することがあります。

## Display

Aspect RatioはAuto、32:9、21:9、16:9、4:3、3:2、Custom Widthを選択できます。Custom Widthの範囲は320～7680、基準高さは720です。RTScale ONでは高さ1080相当へ換算します。最終的な表示寸法はモニターとGamescopeの拡大処理にも依存します。

Super（Windows）＋Fで全画面とウインドウを切り替えます。ウインドウの比率保持とサイズ復帰は補助スクリプトで管理します。

### マルチディスプレイ

複数のディスプレイを使用している場合、Waydroidは起動時にマウスカーソルがあるディスプレイを対象として表示されます。使用したいディスプレイへカーソルを移してから、Start／Restartを押してください。起動処理中も、Waydroidの画面が表示されるまではカーソルをそのディスプレイに置いてください。

### FPS Counter

FPS CounterはOff、Minimal、Detailed、MangoAppから選択します。MinimalとDetailedはMWM HUD、MangoAppはGamescope内に表示するMangoHudのカウンターです。

0.80では、どの表示方式もAndroid内のミリシタ描画レイヤーを対象としたFPSを表示します。MWM HUDは直接取得し、MangoAppはMWMが取得した値を外部テキスト表示機能で読み込みます。表示の更新タイミングが異なるため、切替直後などは数値に差が出ることがあります。

| 表示値 | 取得・計算方法 |
| --- | --- |
| FPS：Minimal／Detailed | `dumpsys SurfaceFlinger --latency` のミリシタ描画レイヤーから、実表示時刻（actualPresentTime、第2列）を取得。直近最大30フレーム間隔から更新頻度を計算します。 |
| FPS：MangoApp | 上記と同じ計測処理の値を表示。Gamescope由来の標準FPS表示は無効にしています。 |
| Frametime：Detailed | 上記時刻列の最後の有効な2フレームの間隔をミリ秒で表示。平均FPSの逆数とは異なります。 |
| フレーム時間グラフ：MangoApp | GamescopeからMangoAppへ通知されるフレーム時間。Androidレイヤーを測るFPS欄とは計測箇所が異なります。 |
| CPU／GPU：MWM HUD | ホスト全体のCPU使用率（`/proc/stat`）と、検出したAMD GPUの使用率（`gpu_busy_percent`）。ミリシタ単体の使用率ではありません。 |
| CPU／GPU：MangoApp | MangoHudがホスト側から取得する負荷。取得方法や対象GPUはMangoHudの版と環境に依存します。 |

FPSはAndroid内でのゲームレイヤーの表示更新頻度です。ミリシタ内部のレンダリング回数や、物理モニターに最終表示されたFPSを直接計測するものではありません。取得できない場合は `--.--` と表示します。

0.77以前のMWM HUDは同じ時刻表の第1列（表示希望時刻）を使用し、MangoAppはGamescopeが通知する表示フレーム時間を使用していました。**従来のMWM HUDとMangoAppのFPSは別の指標であり、数値の一致は保証されません。**

取得項目の意味は[AOSPのFrameTracker](https://android.googlesource.com/platform/frameworks/native/+/ee4bf4c9660809e7fb967cccfd6bdcfc67b3b113/services/surfaceflinger/FrameTracker.cpp)、MangoAppの計測・外部テキスト表示は[MangoHudの実装](https://github.com/flightlessmango/MangoHud/tree/master/src)を参照してください。

MangoAppが導入済みの場合、Offで開始しても非表示のクライアントを用意し、Applyで表示を切り替えられます。既存クライアントがない場合はStart／Restartで起動し直してください。表示異常やクラッシュが起きる場合はMinimalまたはDetailedへ変更してください。

## Maintenanceと診断

DoctorでWaydroid、描画環境、設定などを確認します。Save Diagnostic Logは関連する診断情報を1ファイルへ保存します。

```text
~/.local/share/mwm/logs/mwm-yyyyMMdd-hhmmss.log
```

RTScale DebugではSummary、Runtime、Surface / Display、Mesa / Libraries、Full Logを選択し、Refresh、Copy、Clear Logで操作できます。

ログにはユーザー名、パス、プロセス情報などが含まれる場合があります。不具合報告では内容を確認した上で診断ログを送付してください。

| 内容 | 標準保存先 |
| --- | --- |
| 本体 | `~/.local/share/mwm` |
| MWM設定 | `~/.config/mwm` |
| 実行状態 | `~/.local/state/mwm` |
| 診断ログ | `~/.local/share/mwm/logs` |
| 変更対象のバックアップ | `/var/lib/mwm-backups/<UID>/baseline` |

XDGの保存先を変更している場合は、それぞれ指定された場所を使用します。Gamesタブは現在非表示です。

## 変更対象のバックアップ

初回導入時にMWMが書き換える描画ファイル、RTScale設定、表示・入力・音声の設定値を保存します。元のファイルの有無、内容、属性と、設定の元の値を記録します。アプリ・ゲームデータは現在の状態を保持します。

独立版は12点の描画ファイルを導入します。バックアップは移行元を復元するため16パスを対象とします。対象は描画ライブラリ、競合回避で退避するファイル、RTScale設定ファイルと、MWMが変更するAndroid設定値です。容量は元の描画ファイルの大きさに依存します。

バックアップはroot所有の非公開権限で保存し、最初の正常なバックアップを更新時も保持します。配布ファイルの展開先とは別の場所なので、展開フォルダーを削除しても保持されます。

## アンインストール

Maintenanceの**Uninstall MWM**を押します。ターミナルからは配布ファイルの展開先で実行できます。

```bash
chmod +x uninstall.sh
./uninstall.sh
```

- バックアップあり：確認後に、MWMが変更したファイルと設定を復元し、成功後にMWMを削除します。導入時に存在したファイルを復元し、MWMが追加したファイルを削除します。
- バックアップなし：「バックアップがありません。MWMのみ削除しますか？」の確認で削除できます。Waydroidの現在の設定・描画環境は保持します。
- バックアップ破損、対象環境不一致、復元失敗：エラーを表示して中断し、MWMを保持します。

削除対象はMWM本体、保存設定、ログ、ランチャー、専用生成物、ユーザー用sudoers設定です。root helperは他ユーザーのMWM利用がなければ削除します。共有の依存パッケージと復旧用バックアップは保持します。

復元直前にも同じ変更対象を保存します。復元に失敗した場合はその保存物で巻き戻しを試みます。巻き戻しにも失敗した場合は復旧記録を保持して停止します。

## 不具合が起きた場合

Save Diagnostic Logで診断ログを取得することができます。

## v0.81 MangoApp FPS表示に関する確認事項

MangoAppモードのFPS数値は`fps=0`で標準Gamescope FPSを無効にし、`exec`でAndroid側のミリシタ実測FPSを表示します。Gamescopeのフレームタイムグラフは別の指標です。MangoApp設定はMWMが起動時に生成するため、`~/.config/mwm/MangoApp.conf`を直接編集しても再生成時に上書きされます。今回の`legacy_layout=0`と表示領域指定の修正はテンプレート`mwm/config/MangoApp.conf`に適用しました。

BC250で最小設定によるFPS表示は確認しましたが、CPU/GPU項目を含むv0.81の全設定での表示、Verify ON/OFF、異なるGPU環境は未検証です。
