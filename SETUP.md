# Mirishita Waydroid Manager (MWM) Setup Guide

Mirishita Waydroid Manager (MWM) の導入と基本設定について説明します。

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

MWM に同梱する `payload/rtscale-vendor-overlay.tar.zst` は、**mogareta7731 氏**が公開している Mesa GLES Render Scale / Render Target Scale (RTScale) の実装・ビルド情報を参照し、Waydroid 上で利用するための vendor overlay としてまとめたものです。

この overlay には RTScale を組み込んだ Mesa 由来バイナリに加え、動作に必要な libdrm、LLVM、GBM / gralloc 系などの第三者由来コンポーネントが含まれます。`rtscale-vendor-overlay.tar.zst` 全体を mogareta7731 氏の著作物として扱うものではなく、RTScale 追加部分および各上流コンポーネントには、それぞれのライセンスが適用されます。

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

正常な場合は `package:` で始まるパスが表示されます。

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

MWM を展開し、ディレクトリ内で以下を実行します。

```bash
chmod +x install.sh
./install.sh
```

インストール時には管理者権限が必要です。

### Installer が行う処理

インストーラーは主に以下を行います。

1. 必要なホスト側ツールの確認
2. Waydroid / Android 11 / ミリシタ環境の確認
3. `/dev/uinput` のアクセス設定
4. Mesa GLES Render Scale vendor overlay の導入
5. MWM 用の制限付き root helper の導入
6. MWM 本体のインストール
7. KDE アプリケーションランチャーの作成
8. 最終動作確認

主なシステム側の変更先:

```text
/etc/udev/rules.d/
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

MWM の root helper は、MWM が必要とする限定された処理のみを実行するためのものです。

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

---

## 初期設定

初回は以下の設定から開始できます。

```text
Mesa GLES Render Scale: x3
Display: Auto (Full Screen)

Performance Overlay: OFF
Mouse as Touch: ON
Waydroid Audio Level: ON
```

`x3` は Mesa GLES Render Scale の暫定的な初期値です。

最適な倍率はハードウェアや表示内容によって異なるため、環境に応じて調整してください。

設定後、**Apply & Refresh** を押すと設定を反映し、Waydroid を再起動してミリシタが起動します。

**Cancel** は変更を適用せず MWM を閉じます。

---

## Mesa GLES Render Scale

MWM では Mesa GLES Render Scale の倍率を変更できます。

```text
OFF
x1
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

MWM では、Waydroid 環境下のミリシタ基準解像度を以下に固定しています。

```text
1316x720
```

この値は Waydroid の表示解像度とは独立しています。

設定ファイル:

```text
~/.local/share/waydroid/data/local/tmp/gles_rtscale.conf
```

基本設定:

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

MWM の Render Scale 設定では、主に `scale=` の値を変更します。

Render Scale の変更は Waydroid の再起動後に反映されます。

---

## Display

MWM では以下の表示プリセットを使用できます。

| Preset | Waydroid Display |
| --- | ---: |
| Auto (Full Screen) | ホスト画面に追従 |
| 32:9 | 2560x720 |
| 21:9 | 1680x720 |
| 16:9 | 1280x720 |
| 4:3 | 960x720 |
| 3:2 | 1080x720 |
| Custom Width | WIDTH x 720 |

### Auto (Full Screen)

ホスト側の表示サイズに追従します。

### Fixed Presets

固定プリセットでは縦解像度を `720` に固定し、横幅を変更します。

### Custom Width

任意の横幅を設定できます。

```text
320 - 7680 px
```

縦解像度は常に以下の値となります。

```text
720 px
```

MWM は Android の `wm size` override を使用せず、Waydroid の Display 設定を利用します。

Mesa GLES Render Scale の基準解像度 `1316x720` と、ここで設定する Waydroid の表示解像度とは別の設定です。

---

## Mouse as Touch

`Mouse as Touch` を ON にすると、ミリシタでマウス操作をタッチ入力として扱えるようになります。

MWM では以下を利用します。

- Waydroid の `fake_touch`
- `/dev/uinput`
- MWM Virtual Touchscreen

固定幅の Display プリセットでは、表示サイズに合わせてタッチ座標を補正します。

仮想入力デバイス名:

```text
MWM Virtual Touchscreen
```

`Auto (Full Screen)` では固定解像度向けの座標補正は行いません。

---

## Performance Overlay

`Performance Overlay` を ON にすると、ミリシタの動作確認に利用する以下の情報を画面左上へ表示します。

```text
FPS
CPU
GPU
```

表示内容:

- **FPS** ミリシタの描画 FPS
- **CPU** CachyOS ホスト全体の CPU 使用率（`/proc/stat`）
- **GPU** AMD GPU 全体の使用率（`gpu_busy_percent`）

更新間隔は `0.2 秒` です。

Performance Overlay のチェックボックス右側で `Text / Graph` を選択できます。  
Overlay が OFF の場合、この選択欄は無効化されます。

### Text

3 項目を縦に並べたコンパクトな表示です。

```text
FPS  60.00
CPU  18.2%
GPU  42.0%
```

### Graph

FPS / CPU / GPU を縦 3 段に並べ、現在値と直近の推移を折れ線グラフで表示します。

MWM の標準更新間隔では、およそ直近 12 秒分を表示します。

Overlay はクリック操作を妨げず、ミリシタ側へフォーカスを維持するように動作します。

AMD GPU の使用率を取得できない環境では、GPU 値は取得不可として表示されます。

---

## Waydroid Audio Level

`Waydroid Audio Level` はミリシタ起動時の Waydroid の音量状態を揃えるための補助機能です。

ON の場合、以下を設定します。

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

MWM は対象ストリームを確認してから音量設定を適用します。

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

作成済みのバックアップから MWM 関連設定を復元します。

### Export Logs

トラブルシューティング用のログを出力します。

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
sudo waydroid shell -- wm size
```

### Mesa GLES Render Scale configuration

```bash
cat ~/.local/share/waydroid/data/local/tmp/gles_rtscale.conf
```

Render Scale の読み込みログ:

```bash
sudo waydroid shell -- logcat -d | grep 'GLES_RTSCALE'
```

例えば `x3` の場合、ミリシタから以下のようなログが確認できます。

```text
GLES_RTSCALE: scale=3 base=1316x720 surface=1 texelsize=0
```

ほかの Android プロセスから以下のようなログが出力される場合があります。

```text
GLES_RTSCALE: scale=1 base=1280x720 surface=0 texelsize=0
```

これらはミリシタとは別のプロセスによるものです。

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

MWM に同梱する `rtscale-vendor-overlay.tar.zst` には、Mesa のほか libdrm、LLVM、GBM / gralloc 系の第三者由来バイナリも含まれます。これらの著作権・ライセンスは各上流プロジェクトおよび各権利者に帰属します。

MWM および同梱する第三者由来コンポーネントの詳細:

- [CREDITS.md](docs/CREDITS.md)
- [THIRD_PARTY_NOTICES.md](docs/THIRD_PARTY_NOTICES.md)
- [LICENSES/](LICENSES/)

MWM 独自部分については [LICENSE](LICENSE) を参照してください。

---
