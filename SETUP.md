# Mirishita Waydroid Manager (MWM) Setup Guide

Mirishita Waydroid Manager (MWM) の導入と基本設定について説明します。GitHubの既存ガイドを基に、**v0.70**の実装に合わせて説明を更新・追記しています（2026年10月5日）。

MWM は、**Waydroid 上ですでにミリシタが正常起動する環境**を対象としています。

Mesa GLES Render Scale / Render Target Scale（RTScale）の技術を公開した **mogareta7731 氏**に感謝します。[Zennの技術解説](https://zenn.dev/mogareta7731/articles/82f3f0d9567abc)と[noteの概要](https://note.com/mogareta7731/n/n4db668be92b5)を参照しています。v0.70同梱版は独立復元・追加修正版で、元作者のソースや配布バイナリと同一とは主張しません。

---

## 免責事項

MWM は非公式の独立したプロジェクトであり、ゲーム提供元、Waydroid、Mesa、KDE、Google / Android などから公認・後援されたものではありません。

MWM は実験的なソフトウェアであり、Waydroid およびホスト側の設定やファイルを変更します。環境や組み合わせによっては、起動失敗、設定の破損、データの消失、その他の予期しないトラブルが発生する可能性があります。重要なデータや設定は事前にバックアップしてください。

MWM および Mesa GLES Render Scale の利用が、各アプリケーションやサービスに適用される利用規約・ポリシー等に適合することを保証するものではありません。利用者自身で適用される規約等を確認してください。

MWM の利用は利用者自身の判断と責任で行ってください。作者およびコントリビューターは、適用法令で認められる範囲において、MWM の利用または利用不能によって生じた損害・トラブルについて責任を負いません。

---

## v0.70での変更点

| 項目 | 既存ガイドからの変更・補足 |
| --- | --- |
| 起動モード | High Quality / NormalともGamescope経由。旧KWin直接起動の説明は適用しない |
| 設定反映 | Applyで保存、Restartで再起動。Apply & Refreshの一体操作から変更 |
| RTScale | GUIはOFF / x2〜x10。基準サイズ1316×720固定という旧説明を更新 |
| FSR | High Qualityはx6以下で最大150%、x7以上はOFF。Normalは最大200% |
| HUD | FPS CounterのOff / Compact / Detailedへ変更。旧Text / Graphとは異なる |
| 音量 | 起動時に自動調整。旧Waydroid Audio LevelのON/OFF操作は使用しない |
| 入力 | Waydroid fake_touchを使用。現インストーラーはuinput設定を追加しない |
| payload | 単一rtscale-vendor-overlayから5つの描画アーカイブへ変更 |
| 更新 | --update-appはアプリ更新用。描画payloadを更新しない |
| 配布 | 軽量な実行用ZIPと対応ソースを別配布。ソース収集・照合は未完 |

---

## 重要

MWM は、ミリシタ本体（APK）やゲームプログラム自体に変更を加えるツールではありません。Waydroid側の描画ライブラリ、表示・入力設定とホスト側の起動・表示補助を扱います。

v0.70の描画payloadは `payload/graphics/` 内の以下5アーカイブです。

- `mesa-runtime-overlay.tar.zst`
- `mesa-rtscale-overlay.tar.zst`
- `llvm21-overlay.tar.zst`
- `libdrm-overlay.tar.zst`
- `gbm-gralloc-overlay.tar.zst`

RTScale追加部分とMesa、LLVM、libdrm、GBM/gralloc等にはそれぞれのライセンスが適用されます。一式をmogareta7731氏だけの著作物として扱いません。

---

## 動作要件

| 項目 | 条件 |
| --- | --- |
| ホスト | CachyOS / Arch Linux系、x86_64 |
| デスクトップ | KDE Plasma / Wayland |
| Android | 初期設定済みWaydroid Android 11、x86_64 |
| ゲーム | ミリシタがインストール済みで、MWMなしで起動・通信・入力ができること |
| ARM互換環境 | ゲームを動かすNative Bridgeが構築済みであること |
| 権限・ネットワーク | 通常ユーザーのsudo権限、依存パッケージ取得用ネットワーク |

主なゲーム表示確認はAMD Radeon RX 6600 XTで行われています。Ryzen 7 9700X内蔵GPU等での描画部品検証は、ゲーム全機能の検証とは別です。Intel/NVIDIA実機、Android 11以外、新規環境での導入全工程、長時間・全演出の確認は未完了です。BC250を含む各機材の性能保証はありません。

MWMはミリシタAPKやゲームプログラムを変更するツールではありません。ホスト・Waydroidの設定とAndroid用描画ライブラリを変更します。

対象パッケージ：

```text
com.bandainamcoent.imas_millionlive_theaterdays
```

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

## 導入前に用意する環境

Waydroid Android 11、Google Play、Native Bridge、ミリシタの導入を済ませ、MWMなしでゲームが起動できることを確認してください。初期環境構築の手順は本書の対象外です。

Android側Mesaとホスト側Mesaは別です。MWM同梱のAndroid用Mesa 26.3.0-develベースという記載を、ホストMesaの指定版として扱わないでください。ホストWaydroid・Mesa・Gamescopeのパッケージ版は現インストーラーで固定していません。

---

## インストール

ミリシタの引き継ぎ情報と、ホスト・Waydroidを復元できるバックアップを用意してください。MWMのBackupは設定等が対象で、Android userdataやゲームデータ全体のバックアップではありません。

Waydroid起動中に確認します。

```bash
echo "$XDG_SESSION_TYPE"
uname -m
waydroid status
sudo waydroid shell -- getprop ro.build.version.release
sudo waydroid shell -- getprop ro.dalvik.vm.native.bridge
sudo waydroid shell -- pm path com.bandainamcoent.imas_millionlive_theaterdays
```

Wayland、x86_64、Android 11を確認します。最後に`package:`から始まるパスが出ても、ゲームの正常起動までは証明できません。MWM導入前にゲームを実際に起動してください。

### ZIPの確認と導入

配布元からZIPと対応する外部SHA256ファイルを取得します。外部SHA256がある場合はZIPの隣で検査してください。内部ハッシュだけで配布元の真正性は証明できません。

ZIPを新しい空フォルダーへ展開し、展開した`MWM_v0.70`へ移動します。古い版のファイルを混ぜないでください。

```bash
cd /path/to/MWM_v0.70
(cd payload && sha256sum -c SHA256SUMS)
chmod +x install.sh
./install.sh
```

`payload/SHA256SUMS`のパスはpayloadフォルダーが基準です。すべてOKになることを確認します。失敗したら導入せず、配布元・ZIPを確認してください。

**通常ユーザーで実行します。`sudo ./install.sh`は使いません。** 必要なところで管理者認証が行われます。GUIを自動起動しない場合は`./install.sh --no-gui`を使用します。

通常導入は依存パッケージの導入、既存環境の確認、描画overlayの配置とハッシュ検証、root helper・sudo設定・ランチャーの登録、MWM設定の初期化、最終確認を行います。KDE向けkdotoolの取得に設定済みのparu/yayを使う場合があります。

主な変更先は`/var/lib/waydroid/overlay/`、`/usr/local/libexec/mwm-root-helper`、`/etc/sudoers.d/`、`~/.local/share/mwm/`、`~/.local/bin/mwm`、`~/.local/share/applications/`、`~/.config/mwm/`です。XDG変数の設定によってユーザー側の場所は変わります。

通常導入はMWM設定を初期化します。Android userdataやゲームデータを削除する処理ではありませんが、バックアップの代わりにはなりません。

### Installer が行う処理

1. 同梱payloadのハッシュ検査。
2. 必要なホストパッケージの導入と、既存Waydroid / Android 11 / ミリシタの確認。
3. 描画overlay一式の配置と、配置後のハッシュ検査。
4. 限定された操作だけを許可するroot helperとsudo設定の登録。
5. MWM本体・ランチャーの導入とMWM設定の初期化。
6. Waydroid起動、Display / RTScale設定・ゲームパッケージの最終確認。

この最終確認は全MV・音声・入力の実機確認を意味しません。現インストーラーに `/dev/uinput` のアクセス設定を新設する処理はありません。

---

## 起動

アプリメニューのMirishita Waydroid Manager、または端末から起動します。

```bash
mwm
```

コマンドが見つからない場合は`~/.local/bin/mwm`またはアプリメニューを使用してください。複数版の設定画面を同時に操作しないでください。

---

## 初期設定

1. Mode、RTScale、FSR、Display、Mouse as Touch等を選ぶ。
2. **Apply**で保存する。
3. 約0.5秒後に有効になる**Restart**を押す。
4. Waydroidとミリシタの起動完了を待つ。

描画・比率・入力・Abnormal Zoom Fixの設定はRestartで反映します。未保存の変更があるときは先にApplyします。導入直後はHigh Quality、RTScale x3、FSR OFF、Sharpness OFF、Display Auto、FPS Counter Off、Mouse as Touch ONが既定です。初回はRTScale OFFまたはx2から確認しても構いません。

---

## Mesa GLES Render Scale

High Quality (Mesa RTScale)で使用します。GUIの選択肢は **OFF / x2〜x10**、通常導入時の既定値はx3です。NormalではRTScaleを使用しません。変更後はApply → Restartで反映します。

RTScaleはMesa段で対象の描画先を拡大する処理です。倍率はMSAAのサンプル数ではありません。画面比率や描画負荷によって適した倍率が変わるため、初回はOFFまたは低い倍率で確認してください。

旧ガイドの `1316x720` 固定という説明はv0.70に適用しません。High QualityはAndroid表示を1080高に設定し、そこから720高相当のRTScale基準幅を求めます。例えば16:9では基準1280×720になります。

MWMが管理する設定の16:9・x3時の例：

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

これは全プリセット共通の固定値ではありません。通常はGUIで設定し、手動で基準幅を固定しないでください。設定はroot helperがAndroid側へ書き込み、読み戻して確認します。

設定ファイルのホスト側標準パスは `~/.local/share/waydroid/data/local/tmp/gles_rtscale.conf` です。環境により異なる場合はRTScale Log Viewer / Doctorで確認してください。

---

## 描画モード・FSR・Sharpness

| 設定 | v0.70の動作 |
| --- | --- |
| High Quality | RTScaleとGamescopeを使用 |
| Normal | RTScaleを使用しないGamescope経路 |
| High QualityのFSR | RTScale x6以下は100 / 125 / 150%。x7〜x10はOFF固定 |
| NormalのFSR | 100 / 125 / 150 / 175 / 200% |
| Sharpness | FSRと独立してON/OFF、0〜100% |

FSR1はGamescope段の拡大処理、CASは経路に応じた最終表示のシャープニングです。FSR OFFでもSharpnessを使用できます。高い値が常に画質・速度の改善につながるとは限りません。

---

## Display

| Preset | NormalのAndroid表示 | High QualityのAndroid表示 |
| --- | ---: | ---: |
| Auto | ホスト画面の比率から720高へ換算 | 同じ比率で1080高へ換算 |
| 32:9 | 2560×720 | 3840×1080 |
| 21:9 | 1680×720 | 2520×1080 |
| 16:9 | 1280×720 | 1920×1080 |
| 4:3 | 960×720 | 1440×1080 |
| 3:2 | 1080×720 | 1620×1080 |
| Custom Width | WIDTH×720 | WIDTHの約1.5倍×1080（偶数幅へ調整） |

Custom Widthは320〜7680を指定できます。UIの基準高さ720と、High QualityのAndroid表示高さ1080を区別してください。Displayの比率、RTScale対象の描画サイズ、FSR処理サイズ、ホスト出力は別の値です。

WaydroidのDisplayプロパティを使い、既存の `wm size` overrideをリセットします。手動のoverrideやmulti-window modeを併用しないでください。

Gamescopeは全画面で起動し、**Super（Windowsキー）＋F**で窓表示へ切り替えます。KDE/KWin上で比率維持と画面内に収まる窓操作を補助します。ゲーム側の黒帯やUI余白は残る場合があります。旧Window Placementの選択肢はv0.70の機能として扱いません。

---

## Mouse as Touch

Mouse as TouchをONにすると、Waydroidの `fake_touch` を使ってマウス操作をタッチとして扱います。変更後はApply → Restartで反映します。

旧ガイドのMWM Virtual Touchscreen / uinput座標補正を現行経路の必須機能として扱わないでください。v0.70の起動処理は古いtouch mapperを停止し、fake_touchの設定を適用します。

---

## Performance Overlay / FPS Counter

FPS CounterはOff / Compact / Detailedです。ゲーム起動中でもApplyで切り替わり、設定画面を閉じてもHUDは維持されます。MWMからゲームを停止するとHUDも終了します。

FPS・フレームタイムはゲームのフレーム履歴から取得します。CPUはホスト全体、GPUは取得できたGPU全体の値であり、ゲームだけの利用率ではありません。取得できない温度等は欠測です。v0.70はフレーム生成を提供しません。

---

## Waydroid Audio Level

MWMの起動処理はAndroidメディア音量を15/15へ設定し、検出したWaydroidのPipeWireストリームをミュート解除・100%へ調整します。ホストの全体音量や他アプリの音量は変更しません。初回は再生機器側の音量を控えめにしてください。音ズレや出力先の問題を一括修復する処理ではありません。

---

## Maintenance

- **Doctor**：OS、Waydroid、描画・入力・起動状態を診断。
- **Backup / Restore**：MWM設定、ゲーム登録、取得できるRTScale設定を保存・復元。
- **Export Logs**：診断情報をローカルへ出力。
- **RTScale Debug / Log Viewer**：Summary、Runtime、Surface、Libraries、Full Log等で情報を確認。Refresh、Copy、Clear Logで操作。
- **Abnormal Zoom Fix**：RTScale有効時の既知の描画範囲問題への互換処理。既定ON。変更後はApply → Restart。

Gamesタブでは起動中Androidアプリの検出・登録を扱います。ゲームデータやアカウントのバックアップ機能ではありません。

タイトル・事務所・ライブ等の確認記録と、x7でアイドル詳細の立ち絵・スペシャルトレーニングの確認があります。ログインボーナス受取と新規SSR獲得演出は未確認です。全場面・長時間の安定動作を保証しません。

ログにはユーザー名、ファイルパス、システム情報、アプリ名が含まれる場合があります。共有前に確認してください。ログとセキュリティ（配布ZIP内の `docs/SECURITY.md`）

---

## 更新

MWMを閉じ、新しい版の展開先で実行します。

```bash
./install.sh --update-app
```

この方法はアプリ・root helper・ランチャーを更新し、保存設定と描画payloadを保持します。Mesa / RTScaleバイナリは更新しません。初回導入には使えません。

描画payloadも更新する場合は、リリース説明に従い通常導入します。設定初期化に備え、必要なMWM設定をBackupして内容を控えます。復旧時にはホスト・Waydroid全体のバックアップも必要です。

---

## 動作確認

以下は状態確認用です。Waydroidが起動している状態で実行します。

```bash
sudo waydroid shell -- pm path com.bandainamcoent.imas_millionlive_theaterdays
sudo waydroid shell -- getprop ro.build.version.release
sudo waydroid shell -- getprop ro.dalvik.vm.native.bridge
waydroid prop get persist.waydroid.width
waydroid prop get persist.waydroid.height
sudo waydroid shell -- wm size
cat ~/.local/share/waydroid/data/local/tmp/gles_rtscale.conf
sudo waydroid shell -- logcat -d -s GLES_RTSCALE
```

`wm size`だけでRTScale対象の内部描画サイズやGamescope出力サイズを判断しないでください。Normal / RTScale OFFでは設定ファイルが存在しない場合があります。ゲームパッケージの存在や設定ログの出力だけでは、実際のゲーム・入力・音声が正常とは確認できません。

初回はタイトル・事務所・ライブで、表示、マウス入力、音声、比率、FPS Counter、終了・再起動を確認します。取得できた設定と実際の挙動を分けて記録してください。

---

## トラブルシューティング

| 症状 | 確認すること |
| --- | --- |
| 設定が反映されない | 正しい版、Apply、Restart完了 |
| 起動失敗 | 導入前の単体動作、Android 11、Native Bridge、Doctor |
| ちらつき・FPS低下 | Sharpness、FSR、RTScaleを一つずつ下げて比較 |
| 極端なズーム | Abnormal Zoom Fix、Apply → Restart、再現場面 |
| HUDが出ない | Off以外を選んでApply、必要ならRestart |
| 窓操作やHUD追従が不自然 | KDE Wayland、kdotool、qdbus6の状態 |
| 音が出ない | ホスト出力先、Android音量、Waydroidストリーム |

```bash
waydroid status
systemctl status waydroid-container.service --no-pager
journalctl -u waydroid-container.service -b --no-pager -n 100
uname -r
pacman -Q waydroid mesa vulkan-radeon gamescope
```

報告にはMWM版、OS/カーネル/Gamescope、CPU/GPU、Mode・倍率・比率、再現手順、発生場面を添えてください。診断ログは内容を確認してから共有します。

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

MWM に同梱する `payload/graphics/` の描画アーカイブ には、Mesa のほか libdrm、LLVM、GBM / gralloc 系の第三者由来バイナリも含まれます。これらの著作権・ライセンスは各上流プロジェクトおよび各権利者に帰属します。

配布ZIP内の `docs/THIRD_PARTY_NOTICES.md`、`docs/GRAPHICS_COMPONENTS.md`、`docs/graphics-build/SOURCE-PROVENANCE.md`、`LICENSES/` に出典・個別通知があります。MWM独自部分のMIT LicenseはZIP内の `LICENSE` を参照してください。MWMのMIT Licenseで第三者コードを再ライセンスするものではありません。

同梱MesaにはAndroid libelf等の静的リンク部分があるため、MesaのMIT通知だけで一式の条件を判断できません。対応ソース・ビルド/再リンク入力を含めて確認します。

---

## 配布構成と対応ソース

実行用ZIPは約36.4MBの軽量構成です。起動に必要なPython・シェルコード、描画バイナリ、ハッシュ、ライセンス、出典・小さなビルド資料を収録し、開発用tests / tools / GitHub Actions、旧版資料、キャッシュ、Git管理情報を除外しています。

数百MBの対応ソースは、通常利用者が一緒にダウンロードする必要のない**別の配布物**として提供する方針です。

**公開候補の未完事項：** 独立復元RTScaleの基礎ソース4ファイルと大きな対応ソースアーカイブは、このZIPには含まれません。ユーザー報告ではサブ1のローカルに保管されていますが、収集・v0.70との照合・公開先の案内は未完です。上流Mesaと同梱パッチだけでは完全に再ビルドできません。必要な対応ソースと再リンク入力の提供方法を揃えてから正式公開します。

このSETUP.mdのGitHub更新は、v0.70バイナリの正式リリースを意味しません。GitHubの他の文書が旧版のままの場合は、本書のv0.70説明と配布候補の実装を区別してください。
