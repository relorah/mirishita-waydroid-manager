# Mirishita Waydroid Manager (MWM) Setup Guide

Mirishita Waydroid Manager (MWM) の導入と基本設定について説明します。本書は **v0.70** を対象としています。

MWM は、**Waydroid 上ですでにミリシタが正常起動する環境**を対象としています。

## 免責事項

MWM は非公式の独立したプロジェクトであり、ゲーム提供元、Waydroid、Mesa、KDE、Google / Android などから公認・後援されたものではありません。

MWM は実験的なソフトウェアであり、Waydroid およびホスト側の設定やファイルを変更します。環境や組み合わせによっては、起動失敗、設定の破損、データの消失、その他の予期しないトラブルが発生する可能性があります。重要なデータや設定は事前にバックアップしてください。

MWM および Mesa GLES Render Scale の利用が、各アプリケーションやサービスに適用される利用規約・ポリシー等に適合することを保証するものではありません。利用者自身で適用される規約等を確認してください。

MWM の利用は利用者自身の判断と責任で行ってください。作者およびコントリビューターは、適用法令で認められる範囲において、MWM の利用または利用不能によって生じた損害・トラブルについて責任を負いません。

---

## 重要

MWM は、ミリシタ本体（APK）やゲームプログラム自体に変更を加えるツールではありません。

高解像度描画、画面比率変更、タッチ操作、Performance Overlay、音量調整などは、主に CachyOS / Waydroid / Mesa 側の設定や補助機能によって実現します。

MWM の描画overlayは、**mogareta7731 氏**が公開した Mesa GLES Render Scale / Render Target Scale (RTScale) の技術情報と既存バイナリを比較基準に、Waydroid向けに独立復元・追加修正したものです。元作者のソースや配布バイナリと同一とは主張しません。

v0.70では `payload/graphics/` 内に以下の5アーカイブを収録しています。

- `mesa-runtime-overlay.tar.zst`
- `mesa-rtscale-overlay.tar.zst`
- `llvm21-overlay.tar.zst`
- `libdrm-overlay.tar.zst`
- `gbm-gralloc-overlay.tar.zst`

この overlay には RTScale を組み込んだ Mesa 由来バイナリに加え、動作に必要な libdrm、LLVM、GBM / gralloc 系などの第三者由来コンポーネントが含まれます。この描画overlay全体を mogareta7731 氏の著作物として扱うものではなく、RTScale 追加部分および各上流コンポーネントには、それぞれのライセンスが適用されます。

RTScale の技術情報およびライセンスについては、作者本人による Zenn / note の資料と、後述の [クレジット / ライセンス](#クレジット--ライセンス) を参照してください。

---

## 動作要件

MWM を導入する前に、以下の環境を準備してください。

- CachyOS + KDE Plasma / Wayland
- Waydroid Android 11 (x86_64) 環境
- ARM アプリの実行に必要な Native Bridge 環境が構築済み（test_libnb）
- ミリシタが Waydroid 上で正常起動する環境

対象パッケージ:

```text
com.bandainamcoent.imas_millionlive_theaterdays
```

ミリシタのインストール確認:

```bash
sudo waydroid shell -- pm path com.bandainamcoent.imas_millionlive_theaterdays
```

インストールされている場合は `package:` で始まるパスが表示されます。パッケージの存在だけで正常動作までは確認できないため、MWM導入前にゲームの起動・通信・入力・音声を実際に確認してください。

主なゲーム表示確認はAMD Radeon RX 6600 XTで行われています。Ryzen 7 9700X内蔵GPU等での描画部品検証は、ゲーム全機能の確認とは別です。Intel/NVIDIA実機、Android 11以外、新規環境での全導入工程、長時間・全演出の確認は未完了です。BC250を含む各機材の性能保証はありません。

Android側Mesaとホスト側Mesaは別です。MWM同梱のAndroid用Mesaは26.3.0-develベースですが、これをホストMesaの指定版として扱わないでください。ホストWaydroid・Mesa・Gamescopeの版は現インストーラーで固定していません。

### MWM の対象外

MWM では、以下の初期環境構築は行いません。

- Waydroid 本体のインストール
- Waydroid Android イメージの初期化
- Google Play の導入・設定
- Waydroid の初期ネットワーク設定・接続トラブル対応
- Native Bridge（test_libnb）の導入
- ミリシタ本体のインストール

公開 MWM パッケージには、ミリシタ本体および Native Bridge バイナリを含みません。

---

## インストール

ミリシタの引き継ぎ情報と、ホスト・Waydroidを復元できるバックアップを用意してください。MWMのBackupは設定等が対象で、Android userdataやゲームデータ全体のバックアップではありません。

ZIPと対応するSHA256ファイルを取得し、同じフォルダーで確認します。ファイル名は取得した配布物に合わせてください。

```bash
sha256sum -c MWM_v0.70_candidate.zip.sha256
```

ZIPを新しい空フォルダーへ展開し、`MWM_v0.70` ディレクトリ内で以下を実行します。古い版のファイルは混ぜないでください。

```bash
(cd payload && sha256sum -c SHA256SUMS)
chmod +x install.sh
./install.sh
```

**通常ユーザーで実行します。`sudo ./install.sh` は使用しません。** 必要なところで管理者認証が行われます。

ハッシュ検査が失敗した場合は導入せず、ZIPと配布元を確認してください。内部ハッシュだけで配布元の真正性は証明できません。

GUIを自動起動しない場合は `./install.sh --no-gui` を使用できます。通常導入はMWM設定を初期化します。Android userdataやゲームデータを削除する処理ではありませんが、バックアップの代わりにはなりません。

### Installer が行う処理

インストーラーは主に以下を行います。

1. 同梱payloadのハッシュ検査。
2. 必要なホスト側パッケージの導入。
3. Waydroid / Android 11 / ミリシタ環境の確認。
4. Mesa GLES Render Scaleを含む描画overlay一式の導入とハッシュ検証。
5. MWM用の制限付きroot helperとsudo設定の導入。
6. MWM設定の初期化と本体のインストール。
7. KDEアプリケーションランチャーの作成。
8. Waydroid起動・Display / RTScale設定・ゲームパッケージの最終確認。

現インストーラーは `/dev/uinput` のアクセス設定を追加しません。最終確認は全MV・音声・入力の実機確認を意味しません。

導入する主なホストパッケージは `python`、`pyside6`、`gtk3`、`gtk-layer-shell`、`python-gobject`、`python-cairo`、`polkit`、`zstd`、`rsync`、`gamescope`、`qt6-tools` です。KDEの窓位置取得を補助する `kdotool` は、設定済みのparu/yayがあれば取得を試みます。取得できない場合はHUD追従等に制限があります。

主なシステム側の変更先:

```text
/usr/local/libexec/mwm-root-helper
/etc/sudoers.d/
/var/lib/waydroid/overlay/
```

ユーザー側の主な導入先:

```text
~/.local/share/mwm/
~/.local/bin/mwm
~/.local/share/applications/
~/.local/share/waydroid/data/local/tmp/gles_rtscale.conf
~/.config/mwm/
```

MWM の root helper は、MWM が必要とする限定された処理のみを実行するためのものです。XDG環境変数の設定によってユーザー側の保存場所は変わります。

---

## 起動

KDE のアプリケーションメニューから:

```text
Mirishita Waydroid Manager
```

ターミナルから:

```bash
mwm
```

見つからない場合は `~/.local/bin/mwm` またはアプリメニューから起動してください。複数版の設定画面を同時に操作しないでください。

---

## 初期設定

初回は以下の設定から開始できます。

```text
Mode: High Quality (Mesa RTScale)
Mesa GLES Render Scale: x3
FSR Scale: OFF
Sharpness: OFF
Display: Auto

FPS Counter: Off
Mouse as Touch: ON
```

`x3` は Mesa GLES Render Scale の暫定的な初期値です。

最適な倍率はハードウェアや表示内容によって異なるため、環境に応じて調整してください。

設定後、**Apply** で保存し、約0.5秒後に有効になる **Restart** を押すとWaydroidを再起動してミリシタが起動します。描画・比率・入力・Abnormal Zoom Fixの変更はRestartで反映します。FPS Counterはゲーム起動中でもApplyで切り替わります。

初回はRTScale OFFまたはx2から確認しても構いません。

**Cancel** は変更を適用せず MWM を閉じます。

---

## Mesa GLES Render Scale

MWM のHigh Qualityモードでは Mesa GLES Render Scale の倍率を変更できます。NormalモードではRTScaleを使用しません。両モードともGamescope経由で起動します。

```text
OFF
x2
x3
...
x10
```

初期値:

```text
x3
```

倍率によって内部描画解像度や動作特性が変化します。

環境や表示内容によって適した倍率は異なるため、複数の倍率を比較しながら調整してください。

RTScaleはMesa段で対象の描画先を拡大します。倍率はMSAAのサンプル数ではありません。

v0.70では基準解像度を `1316x720` に固定しません。High QualityではAndroid表示を1080高に設定し、その幅から720高相当のRTScale基準幅を求めます。例えば16:9なら基準は1280×720です。Display設定、内部描画サイズ、Gamescope出力サイズは別の値です。

設定ファイル:

```text
~/.local/share/waydroid/data/local/tmp/gles_rtscale.conf
```

16:9・x3時の設定例（全プリセット共通の固定値ではありません）:

```ini
schema_version=1

[application.0]
name=com.bandainamcoent.imas_millionlive_theaterdays
base_width=1280
base_height=720
scale=3
surface=1
texelsize=0
zoom_fix=1
```

MWMは倍率・基準幅・互換設定をAndroid側へ書き込み、読み戻して確認します。通常はGUIで変更し、設定ファイルの基準幅を手動で固定しないでください。

Render Scale の変更はApply → Restartで反映されます。

### FSR Scale / Sharpness

FSR1はGamescope段の拡大処理、CASは経路に応じた最終表示のシャープニングです。

| 設定 | 選択範囲 |
| --- | --- |
| High QualityのFSR | RTScale x6以下は100 / 125 / 150%。x7〜x10はOFF固定 |
| NormalのFSR | 100 / 125 / 150 / 175 / 200% |
| Sharpness | FSRと独立してON/OFF、0〜100% |

FSR OFFでもSharpnessを使用できます。高い値が常に画質やFPSの改善につながるとは限りません。

---

## Display

MWM では以下の表示プリセットを使用できます。

| Preset | NormalのAndroid表示 | High QualityのAndroid表示 |
| --- | ---: | ---: |
| Auto | ホスト画面の比率で720高へ換算 | 同じ比率で1080高へ換算 |
| 32:9 | 2560×720 | 3840×1080 |
| 21:9 | 1680×720 | 2520×1080 |
| 16:9 | 1280×720 | 1920×1080 |
| 4:3 | 960×720 | 1440×1080 |
| 3:2 | 1080×720 | 1620×1080 |
| Custom Width | WIDTH×720 | WIDTHの約1.5倍×1080（偶数幅へ調整） |

### Auto (Full Screen)

ホスト画面から比率を求め、選択モードの高さへ換算します。ホストの物理解像度をそのままAndroid表示に設定する意味ではありません。

### Fixed Presets

固定プリセットでは比率に応じて横幅を変更します。Normalは720高、High Qualityは1080高です。

### Custom Width

任意の横幅を設定できます。

```text
320 - 7680 px
```

UIで指定する基準高さは720です。High Qualityでは幅を約1.5倍へ換算し、高さ1080に設定します。

MWM は Waydroid の Display 設定を利用し、既存のAndroid `wm size` overrideをリセットします。手動のoverrideを併用しないでください。

RTScale対象の基準サイズとAndroid表示サイズ、FSR処理サイズ、ディスプレイ出力は区別してください。

Gamescopeは全画面で起動し、**Super（Windowsキー）＋F**で窓表示に切り替えます。KDE/KWin上で比率維持と画面内の窓操作を補助します。ゲームが描く黒帯や余白は残る場合があります。v0.70に旧KWin直接起動・Window Placementの選択肢はありません。

---

## Mouse as Touch

`Mouse as Touch` をONにすると、Waydroidの `fake_touch` を使い、ミリシタでマウス操作をタッチ入力として扱います。変更後はApply → Restartで反映します。

v0.70の起動処理は旧touch mapperを停止します。`MWM Virtual Touchscreen` や `/dev/uinput` による座標補正を、現行起動経路の必須機能として扱わないでください。

---

## Performance Overlay

v0.70のGUIでは **FPS Counter** の **Off / Compact / Detailed** を選択します。旧Text / Graphの選択肢から変更されています。

ゲーム起動中でもApplyで切り替わり、MWMの設定画面を閉じてもHUDは維持されます。MWMからゲームを停止するとHUDも終了します。

### Compact

FPS / CPU / GPUの3項目と、小型のFPSグラフを表示します。

### Detailed

CPU / GPUの温度と、数値のフレームタイム等を加えた表示です。取得できない情報は欠測として扱います。

### 表示値と確認範囲

- **FPS / フレームタイム**：ゲームのフレーム履歴から取得。
- **CPU**：ホスト全体のCPU使用率。
- **GPU**：取得できたGPU全体の使用率。ゲーム単体の使用率ではありません。

HUDは操作を妨げず、ゲーム側のフォーカスを維持するように動作します。KDEの窓位置取得が利用できない場合は画面隅へ表示するなど制限があります。

v0.70はフレーム生成を提供しません。FPS値はFG後のフレーム数ではありません。

---

## Waydroid Audio Level

Waydroid Audio Levelはミリシタ起動時のWaydroid音量を揃える内部処理です。v0.70ではGUIのON/OFF選択ではなく、自動実行します。

以下を設定します。

```text
Android media volume = 15 / 15
Waydroid PipeWire stream = Unmuted
Waydroid PipeWire stream volume = 100%
```

対象となるのは以下です。

- Android 側のメディア音量
- CachyOS / PipeWire 側の Waydroid 再生ストリーム

以下の音量設定は変更しません。

- KDE 全体のマスター音量
- 他アプリの音量
- DAC 本体の音量

PipeWire の Waydroid 再生ストリームは、Waydroid やミリシタの起動後に作成される場合があります。

MWM は対象ストリームを確認してから音量設定を適用します。初回は再生機器側の音量を控えめにしてください。音ズレや出力先の問題を一括修復する処理ではありません。

---

## Maintenance

`Maintenance` タブでは、MWM 環境の確認や設定の保守を行えます。

### Doctor

MWM / Waydroid 環境の状態を確認します。

主な確認対象:

- Waydroid
- Android version
- ミリシタ package
- Native Bridge
- Mesa GLES Render Scale
- Display
- ミリシタの起動状態
- MWM 関連設定

Native Bridge は状態確認のみ行い、MWM から導入や変更は行いません。

### Backup

MWM 関連設定をバックアップします。

### Restore

作成済みのバックアップから MWM 関連設定を復元します。Backup / RestoreはAndroid userdataやゲームアカウント全体の保存・復元ではありません。

### Export Logs

トラブルシューティング用のログを出力します。ユーザー名、ファイルパス、システム情報、アプリ名が含まれる場合があるため、共有前に内容を確認してください。

### RTScale Debug / Log Viewer

Summary、Runtime、Surface、Libraries、Full Log等で情報を確認し、Refresh、Copy、Clear Logで操作できます。

### Abnormal Zoom Fix

RTScale有効時の既知の描画範囲問題への互換処理です。既定ON。変更後はApply → Restartで反映します。

タイトル・事務所・ライブ等の確認記録と、x7でアイドル詳細の立ち絵・スペシャルトレーニングの確認があります。ログインボーナス受取と新規SSR獲得演出は未確認です。全場面・長時間の安定動作を保証しません。

### Gamesタブ

起動中Androidアプリの検出・登録を扱います。ゲームデータやアカウントのバックアップ機能ではありません。

---

## 動作確認

### Mirishita package

```bash
sudo waydroid shell -- pm path com.bandainamcoent.imas_millionlive_theaterdays
```

### Android version

```bash
sudo waydroid shell -- getprop ro.build.version.release
```

### Native Bridge

```bash
sudo waydroid shell -- getprop ro.dalvik.vm.native.bridge
```

### Waydroid display size

```bash
waydroid prop get persist.waydroid.width
waydroid prop get persist.waydroid.height
sudo waydroid shell -- wm size
```

`wm size`だけでRTScaleの内部描画サイズやGamescopeの出力サイズを判断しないでください。

### Mesa GLES Render Scale configuration

```bash
cat ~/.local/share/waydroid/data/local/tmp/gles_rtscale.conf
```

Normal / RTScale OFFでは設定ファイルが存在しない場合があります。環境によりパスが異なる場合はDoctor / Log Viewerで確認してください。

Render Scale の読み込みログ:

```bash
sudo waydroid shell -- logcat -d | grep 'GLES_RTSCALE'
```

ログの形式や値は描画ライブラリ・設定によって変わります。版、アプリ名、倍率、基準サイズを確認してください。設定ログの存在だけで正常描画までは確認できません。

---

## 更新

MWMを閉じ、新しい版を別の空フォルダーへ展開して実行します。

```bash
./install.sh --update-app
```

アプリ・root helper・ランチャーを更新し、保存設定と描画payloadを保持します。Mesa / RTScaleバイナリは更新しません。初回導入には使えません。

描画payloadも更新する場合はリリース説明に従い通常導入します。設定初期化に備え、Backupと設定の控えを用意してください。

---

## トラブルシューティング

| 症状 | 確認すること |
| --- | --- |
| 設定が反映されない | 使用版、Apply、Restart完了 |
| 起動失敗 | 導入前の単体動作、Android 11、Native Bridge、Doctor |
| ちらつき・FPS低下 | Sharpness、FSR、RTScaleを一つずつ下げて比較 |
| 極端なズーム | Abnormal Zoom Fix、再現場面、Apply → Restart |
| HUDが出ない | Off以外を選びApply、必要ならRestart |
| 窓操作・HUD追従が不自然 | KDE Wayland、kdotool、qdbus6 |
| 音が出ない | ホスト出力先、Android音量、Waydroidストリーム |

報告にはMWM版、OS・カーネル・Gamescope、CPU / GPU、Mode・倍率・比率、発生場面と再現手順を添えてください。Linux実機の再検証と、配布文書・ZIPの確認は区別しています。

---

## 注意事項

- 現在の主な検証対象は Android 11 の Waydroid 環境です。
- AMD GPU / Mesa 環境を中心に検証しています。
- Performance Overlay の CPU / GPU 値は、ミリシタ単体ではなく CachyOS ホスト全体の使用率です。
- Mesa GLES Render Scale の適した倍率はハードウェアや表示内容によって異なります。
- Waydroid の Display 解像度と Mesa GLES Render Scale の基準解像度は別々の設定です。
- MWM は Waydroid の multi-window mode を前提としていません。
- 固定 Display プリセットと Android の `wm size` override は併用しないでください。

---

## クレジット / ライセンス

Mesa GLES Render Scale / Render Target Scale (RTScale) は **mogareta7731 氏**による成果を基盤としています。

MWM では、作者本人による以下の資料を Mesa GLES Render Scale の主要な技術情報源として参照しています。

- [Zenn: Mesa GLES Render Scale (Render Target Scale) for Android-x86](https://zenn.dev/mogareta7731/articles/82f3f0d9567abc) 技術仕様、実装・ビルド方法、ライセンス
- [note: Mesa GLES Render Scale（Render Target Scale）について](https://note.com/mogareta7731/n/n4db668be92b5) 日本語による概要、設定方法、ライセンス

作者の公開資料では、RTScale のために追加された部分は 0BSD、既存 Mesa 由来部分はそれぞれ元の Mesa ライセンスが継続して適用されるとされています。

MWM に同梱する描画overlayには、Mesa のほか libdrm、LLVM、GBM / gralloc 系の第三者由来バイナリも含まれます。これらの著作権・ライセンスは各上流プロジェクトおよび各権利者に帰属します。

MWM および同梱する第三者由来コンポーネントの詳細:

配布ZIP内の以下のファイルを参照してください。

- `docs/THIRD_PARTY_NOTICES.md`
- `docs/GRAPHICS_COMPONENTS.md`
- `docs/graphics-build/SOURCE-PROVENANCE.md`
- `LICENSES/`

MWM 独自部分のMIT LicenseはZIP内の `LICENSE` を参照してください。MWMのMIT Licenseで第三者コードを再ライセンスするものではありません。

### 実行用ZIPと対応ソース

実行用ZIPは起動に必要なコード・描画バイナリ・ハッシュ・ライセンス・出典と小さな再ビルド資料を収録した軽量構成です。開発用tests / tools / GitHub Actions、旧版資料、キャッシュ、Git管理情報は含みません。

数百MBの対応ソースは実行用ZIPと分けて提供する方針です。同梱MesaにはAndroid libelf等の静的リンク部分もあり、個々のライセンスに応じた対応ソース・ビルド/再リンク入力の確認が必要です。

**公開候補の未完事項：** 独立復元RTScaleの基礎ソース4ファイルと大きな対応ソースアーカイブは今回のZIPに含まれません。ユーザー報告ではサブ1に保管されていますが、収集・v0.70との照合・入手先の案内は未完です。上流Mesaと同梱パッチだけでは完全に再ビルドできません。必要な提供方法を揃えてから正式公開します。

SETUP.mdのGitHub更新は、v0.70バイナリの正式リリースを意味しません。

---
