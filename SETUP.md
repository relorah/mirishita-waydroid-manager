# MWM 0.74 Setup Guide

## 対象環境

MWMは、既存のWaydroidでミリシタを正常にプレイできる環境を対象とします。

- CachyOS／Arch系、KDE Plasma／Wayland、x86_64
- Waydroid Android 11。Google Play・Native Bridge／ARM変換は利用者側で準備
- sudo権限、依存パッケージ取得用ネットワーク
- 描画バックエンド：Gamescope

Ryzen 7 9700X + RX 6600 XT、およびAMD BC250でテストしています。

## 免責と変更範囲

MWMは非公式の独立プロジェクトです。各サービスの規約への適合や動作を保証しません。利用者の判断で使用し、重要なデータは事前に保全してください。

インストーラーはWaydroid側の描画ライブラリをoverlayとして導入し、Androidの表示・入力・RTScale設定などを変更します。root helperと限定したsudoers設定を導入します。依存パッケージはホストへ追加します。

Mesa GLES Render Scale (Render Target Scale、以下 RTScale)はmogareta7731氏の原機能を利用しています。今回のISO由来ライブラリとMWMの追加ラッパーは別の成果物です。詳細は[描画資産](docs/GRAPHICS_COMPONENTS.md)を参照してください。

## インストール

MWMを終了し、ZIPを新しい空フォルダーへ展開します。旧版のファイルを混ぜないでください。展開先で通常ユーザーとして実行します。

```bash
chmod +x install.sh
./install.sh
```

インストーラーが追加する主なパッケージは、python、pyside6、gtk3、gtk-layer-shell、python-gobject、python-cairo、polkit、zstd、rsync、gamescope、qt6-toolsです。表示ウィンドウの確認用としてkdotoolの導入を試みます。

インストーラーは既存Waydroidの起動・ゲームの存在・payloadチェックサムを確認します。通常インストールはMWMの変更対象をバックアップした後に描画overlayを導入し、本体・helperを更新します。既存MWM設定は保存します。導入前にWaydroid、Androidイメージ、Googleサービス、ARM変換、ミリシタの動作環境を用意してください。

### 本体のみ更新

```bash
./install.sh --update-app
```

既存のMWM本体・helper・ランチャーを更新し、保存設定と導入済みの描画ファイルを保持します。初回導入は通常の `./install.sh` を使用してください。

### インストール後にGUIを開かない

```bash
./install.sh --no-gui
./install.sh --update-app --no-gui
```

## 初回操作

アプリメニューのMirishita Waydroid Manager、または以下で起動します。

```bash
~/.local/bin/mwm
```

1. Gamescopeで使うRTScale・AMD FSR1・Display設定を選ぶ。
2. RTScale・AMD FSR1・出力アスペクト比などを設定。
3. ミリシタを終了し、Applyで保存してWaydroid Refresh。
4. 「Waydroidの準備が完了しました」の通知でOKを押した後、ミリシタを手動起動。

準備中はAndroid起動、解像度確認、必須設定反映、表示とセッションの継続確認を行います。MWMの操作は制限されますが、OSのAlt+Tabや外部ショートカットまでは遮断できません。途中起動を検出するとRefreshを中断します。設定が一部反映された可能性があるため、ミリシタを終了してRefreshをやり直してください。

| 操作 | 保存・反映する内容 |
| --- | --- |
| Apply | RTScale、AMD FSR1、Upscale、Sharpness、Display、Mouse as Touch、FPS Counter、Abnormal Zoom Fixの選択を保存。FPS Counterは起動状態に応じてその場で更新します。 |
| Waydroid Refresh | 保存済みの設定でGamescope／Waydroidを起動し、Android側の表示・入力・RTScale設定を反映・確認します。 |

Android側やGamescopeの設定を適用するにはWaydroid Refreshが必要です。未保存の変更がある場合は先にApplyを押してください。

## 設定

### 描画バックエンド

- Gamescope：Waydroid画面を別の描画環境に入れ、FSRと最終表示サイズを扱う。

### RTScale

OFF、x1-x10を選択します。設定はAndroid側のgles_rtscale.confへ書き込み、読み戻しを確認します。倍率選択や設定読取の成功だけでは、全シーンの描画改善・品質・安定性を証明できません。重い場面で問題があれば倍率を下げてください。

GamescopeのRTScale経路ではAndroid表示を1080高とし、RTScale用の720高の基準寸法を別に求めます。OSスケール、表示サイズ、RTScale倍率は別の設定です。

### AMD FSR1

GamescopeでFSR1の拡大（EASU）とシャープニング（RCAS）をまとめて切り替えます。チェックOFFでUpscaleとSharpnessをグレーアウトします。

| 項目 | 選択肢 |
| --- | --- |
| Upscale：RTScale ON | 125% / 150% |
| Upscale：RTScale OFF | 125% / 150% / 175% / 200% |
| Sharpness | 1-21 |

Sharpness 1は最小強度であり、完全無効ではありません。21が最大です。

### Display

Auto、32:9、21:9、16:9、4:3、3:2、Custom Width。Custom Widthの指定範囲は320-7680、基準高さ720です。GamescopeのRTScale経路では表示寸法を1080高へ換算します。

### Play Assist / FPS Counter

Mouse as TouchはAndroidのfake_touch設定を使用します。

FPS CounterはOff／Compact／Detailedから選択します。MWMのlayer-shell HUDでFPSやシステム負荷を表示します。表示値の欠測や対応GPUは実機確認が必要です。

### Maintenance / RTScale Debug

Doctorで状態を確認します。「診断ログを保存」で複数の診断情報を1ファイルにまとめます。保存先は通常以下です。

```text
~/.local/share/mwm/logs/mwm-yyyyMMdd-hhmmss.log
```

XDG_DATA_HOMEを変更している場合は、その配下のmwm/logsです。ログにはユーザー名・パス・プロセス情報などが含まれることがあります。

RTScale DebugはSummary／Runtime／Surface／Libraries／Full Logの表示とRefresh／Copy／Clear Logを提供します。Abnormal Zoom Fixは互換処理の切替です。変更後はApply→Waydroid Refreshで反映します。

## RTS倍率だけの高速反映

ミリシタを終了して倍率を変更し、Apply→Waydroid Refreshを押します。前回正常反映時と次の状態が一致すると、Waydroidと描画環境を維持して倍率だけを更新します。

- RTScaleがONのままで倍率だけが変更されている
- MWMの他の保存設定・版が同じ
- モニター、論理サイズ、OSスケールが同じ
- Androidのsystem_serverの起動識別情報と必須設定が同じ
- Waydroid解像度、描画プロセス、実際の表示ウィンドウ、Android内のRTScale設定が同じ

高速反映の表示確認にはkdotoolを使用します。利用できない場合は通常Refreshになります。

初回、RTScale ON/OFF、FSR変更、解像度変更、セッション変更、状態不明では通常Refreshに戻ります。設定を書き込んだ後に失敗した場合は、成功とは表示せず中断します。途中起動検出と3秒の継続確認は維持します。高速化時の実際の所要時間とゲーム再起動時の設定読み直しはLinux実機で未確認です。

## 初回導入時のバックアップ

MWMが変更する描画ファイルとAndroid設定の元の状態を、変更前に保存します。対象は描画ファイル15点、競合回避で退避する既存ファイル1点、RTScale設定ファイル、表示・入力・音量の設定値です。[対象ファイル一覧](docs/WAYDROID_CHANGES.md)を参照してください。

保存先は `/var/lib/mwm-backups/<UID>/baseline/` です。最初の正常なバックアップを更新時も保持します。容量は元の描画ファイルのサイズに依存します。root所有・非公開権限で保存します。

バックアップには、各ファイルの有無と内容、属性、各設定の元の値を記録します。アプリ・ゲームデータは現在の状態を保持します。取得失敗時は描画ファイルの変更前に導入を中断します。

## アンインストール

Maintenanceの「アンインストール」を押します。

- バックアップあり：確認でOKを押すと、MWMが変更したファイル・設定だけを復元し、成功後にMWMを削除します。導入時に存在したファイルは復元し、MWMが追加したファイルは削除します。
- バックアップなし：「バックアップがありません。MWMのみ削除しますか？」のYesでMWMを削除します。Waydroidの現在の設定・描画環境を保持します。
- バックアップ破損・対象環境不一致・復元失敗：エラーを表示し、MWMを保持して中断します。

MWM本体、保存設定、ログ、ランチャー、専用生成物、ユーザー用sudoersを削除します。root helperは他ユーザーのMWM利用がなければ削除します。共有の依存パッケージと復旧用バックアップは保持します。

ターミナルからは展開先で実行できます。

```bash
chmod +x uninstall.sh
./uninstall.sh
```

復元直前にも同じ変更対象だけを保存します。復元失敗時はこの保存物で巻き戻しを試みます。巻き戻しにも失敗した場合は復旧記録を保持して停止します。

旧版の環境全体バックアップを検出した場合は形式不一致として中断します。元の保存物を保全してから内容を確認してください。

バックアップ作成・復元・アンインストールは構文と模擬条件で確認しています。Linux実機での検証は継続中です。
