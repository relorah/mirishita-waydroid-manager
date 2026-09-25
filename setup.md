# Setup Guide

CachyOS + Waydroid Android 11 環境で  
「アイドルマスター ミリオンライブ！ シアターデイズ (ミリシタ)」を起動し、Mesa GLES Render Scale (RTScale) を利用するまでのセットアップ手順です。

> [!WARNING]
> このプロジェクトは現在 Experimental / Work in progress です。  
> test_libnb や Mesa overlay の変更前にはバックアップを作成します。

## Reference Environment

### Host

- OS: CachyOS
- Architecture: x86_64
- Desktop: Wayland
- Shell: Bash

### GPU

主な検証対象:

- AMD Radeon RX 6600 XT
- AMD Radeon RX 9060 XT
- AMD BC250 / Cyan Skillfish

その他:

- Intel GPU: Experimental / unverified
- NVIDIA GPU: Unsupported / unverified

CPU vendor は NativeBridge / RTScale の選択条件として固定しません。

### Waydroid

- Android 11
- LineageOS 18.1
- x86_64
- GApps

### Runtime

- Houdini 11 / 38765
- patched test_libnb
- Mesa GLES Render Scale (RTScale)

Mirishita package:

```text
com.bandainamcoent.imas_millionlive_theaterdays
```

---

# 1. Download This Repository

GitHub から `mirishita-waydroid` を ZIP でダウンロードし、任意の場所へ展開します。

例:

```text
~/Downloads/mirishita-waydroid-main/
```

以降のコマンドは、展開した repository のルートディレクトリで端末を開いて実行することを前提とします。

例:

```bash
cd ~/Downloads/mirishita-waydroid-main
```

確認:

```bash
pwd
ls
```

少なくとも以下が見えることを確認します。

```text
README.md
AGENTS.md
docs/
runtime/
config/
```

---

# 2. Install Required Packages

CachyOS を更新します。

```bash
sudo pacman -Syu
```

必要パッケージをインストールします。

```bash
sudo pacman -S --needed \
  waydroid \
  git \
  curl \
  unzip \
  lzip \
  python \
  python-pip
```

test_libnb と RTScale 対応 Mesa は、本プロジェクトでビルド・検証したバイナリを使用します。

通常の利用者は NDK / CMake / Meson / Ninja を使用してビルドする必要はありません。

---

# 3. Install Waydroid Android 11 GApps

本プロジェクトでは Waydroid の最新自動取得 image ではなく、動作環境を固定するため Android 11 / LineageOS 18.1 を使用します。

基準 image:

```text
System:
lineage-18.1-20250621-GAPPS-waydroid_x86_64-system.zip

Vendor:
lineage-18.1-20250621-MAINLINE-waydroid_x86_64-vendor.zip
```

Waydroid の配布元から両方をダウンロードしてください。

custom image directory を作成します。

```bash
sudo mkdir -p /etc/waydroid-extra/images
```

ダウンロードした directory へ移動します。

例:

```bash
cd ~/Downloads
```

System image:

```bash
sudo unzip \
  lineage-18.1-20250621-GAPPS-waydroid_x86_64-system.zip \
  -d /etc/waydroid-extra/images
```

Vendor image:

```bash
sudo unzip \
  lineage-18.1-20250621-MAINLINE-waydroid_x86_64-vendor.zip \
  -d /etc/waydroid-extra/images
```

確認:

```bash
ls -lh /etc/waydroid-extra/images
```

以下が存在することを確認します。

```text
system.img
vendor.img
```

Waydroid を初期化します。

```bash
sudo waydroid init -f
```

> [!WARNING]
> 既存の Waydroid 環境を再初期化する場合は、必要なユーザーデータを事前に退避してください。

---

# 4. Start Waydroid

container を起動します。

```bash
sudo systemctl enable --now waydroid-container
```

session を起動します。

```bash
waydroid session start
```

別の端末から Full UI を起動します。

```bash
waydroid show-full-ui
```

Android version:

```bash
sudo waydroid shell getprop ro.build.version.release
```

期待値:

```text
11
```

SDK:

```bash
sudo waydroid shell getprop ro.build.version.sdk
```

期待値:

```text
30
```

---

# 5. Google Play Setup

GApps版を使用するため、Google Play Store が利用できます。

初回起動時に Google Play Protect の端末認証が必要になる場合は、Waydroid の Android ID を登録してください。

認証後、Google Account へログインします。

---

# 6. Install Houdini

ARM native application を実行するため Houdini 11 を導入します。

作業用 directory:

```bash
mkdir -p ~/Projects
cd ~/Projects
```

`waydroid_script` を取得します。

```bash
git clone https://github.com/casualsnek/waydroid_script.git
cd waydroid_script
```

Python environment:

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

Waydroid を停止します。

```bash
waydroid session stop
sudo systemctl stop waydroid-container
```

Android 11用 Houdini をインストールします。

```bash
sudo venv/bin/python3 main.py -a 11 install libhoudini
```

本プロジェクトでは Houdini 11 / 38765 を基準とします。

インストール後、repository root に戻ります。

例:

```bash
cd ~/Downloads/mirishita-waydroid-main
```

実際の展開場所が異なる場合は適宜変更してください。

---

# 7. Backup Before test_libnb

patched test_libnb を適用する前に、現在の Waydroid NativeBridge 関連設定を保存します。

Waydroid を停止します。

```bash
waydroid session stop
sudo systemctl stop waydroid-container
```

バックアップ directory を作成します。

```bash
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/mirishita-waydroid"
BACKUP_DIR="$STATE_DIR/backups/$(date +%Y%m%d-%H%M%S)-pre-libnb"

mkdir -p "$BACKUP_DIR"
```

Waydroid configuration:

```bash
sudo cp -a \
  /var/lib/waydroid/waydroid.cfg \
  "$BACKUP_DIR/" 2>/dev/null || true

sudo cp -a \
  /var/lib/waydroid/waydroid_base.prop \
  "$BACKUP_DIR/" 2>/dev/null || true
```

既存の libnb overlay が存在する場合も保存します。

```bash
sudo cp -a \
  /var/lib/waydroid/overlay/system/lib/libnb.so \
  "$BACKUP_DIR/libnb.so.x86.previous" 2>/dev/null || true

sudo cp -a \
  /var/lib/waydroid/overlay/system/lib64/libnb.so \
  "$BACKUP_DIR/libnb.so.x86_64.previous" 2>/dev/null || true
```

バックアップを通常ユーザーから参照できるようにします。

```bash
sudo chown -R "$USER:$USER" "$BACKUP_DIR"
```

確認:

```bash
echo "$BACKUP_DIR"
ls -la "$BACKUP_DIR"
```

---

# 8. Install patched test_libnb

本 repository に含まれるビルド済み test_libnb を使用します。

想定配置:

```text
runtime/
└── libnb/
    ├── x86/
    │   └── libnb.so
    └── x86_64/
        └── libnb.so
```

overlay directory:

```bash
sudo mkdir -p \
  /var/lib/waydroid/overlay/system/lib \
  /var/lib/waydroid/overlay/system/lib64
```

32-bit:

```bash
sudo install -m0644 \
  runtime/libnb/x86/libnb.so \
  /var/lib/waydroid/overlay/system/lib/libnb.so
```

64-bit:

```bash
sudo install -m0644 \
  runtime/libnb/x86_64/libnb.so \
  /var/lib/waydroid/overlay/system/lib64/libnb.so
```

## NativeBridge configuration

`waydroid.cfg`:

```bash
sudo python3 - <<'PY'
import configparser

path = "/var/lib/waydroid/waydroid.cfg"

cfg = configparser.ConfigParser()
cfg.optionxform = str
cfg.read(path)

if "properties" not in cfg:
    cfg["properties"] = {}

cfg["properties"]["ro.dalvik.vm.native.bridge"] = "libnb.so"

with open(path, "w") as f:
    cfg.write(f, space_around_delimiters=True)
PY
```

`waydroid_base.prop`:

```bash
if sudo grep -q '^ro\.dalvik\.vm\.native\.bridge=' \
  /var/lib/waydroid/waydroid_base.prop; then

  sudo sed -i \
    's/^ro\.dalvik\.vm\.native\.bridge=.*/ro.dalvik.vm.native.bridge=libnb.so/' \
    /var/lib/waydroid/waydroid_base.prop

else
  echo 'ro.dalvik.vm.native.bridge=libnb.so' \
    | sudo tee -a /var/lib/waydroid/waydroid_base.prop >/dev/null
fi
```

---

# 9. Verify NativeBridge

Waydroid を起動します。

```bash
sudo systemctl start waydroid-container
waydroid session start
```

NativeBridge:

```bash
sudo waydroid shell getprop ro.dalvik.vm.native.bridge
```

期待値:

```text
libnb.so
```

ABI:

```bash
sudo waydroid shell getprop ro.product.cpu.abilist
```

libnb:

```bash
sudo waydroid shell \
  'ls -l /system/lib/libnb.so /system/lib64/libnb.so'
```

---

# 10. Install Mirishita

Waydroid の Google Play Store から、

**アイドルマスター ミリオンライブ！ シアターデイズ**

をインストールします。

本 repository ではミリシタの APK を配布しません。

インストール確認:

```bash
sudo waydroid shell pm list packages \
  | grep com.bandainamcoent.imas_millionlive_theaterdays
```

期待値:

```text
package:com.bandainamcoent.imas_millionlive_theaterdays
```

---

# 11. Launch Mirishita Before RTScale

RTScale を導入する前に、通常状態でミリシタを起動します。

```bash
waydroid app launch \
  com.bandainamcoent.imas_millionlive_theaterdays
```

最低限、以下を確認します。

- アプリが起動する
- タイトル画面まで進める
- データをダウンロードできる
- 3D Live / PV を再生できる
- 音声が正常に再生される
- 異常終了しない

ここで問題がある場合は、RTScale の導入へ進まないでください。

---

# 12. Backup Before RTScale Mesa

RTScale対応 Mesa を配置する前に、既存vendor overlayをバックアップします。

Waydroid を停止します。

```bash
waydroid session stop
sudo systemctl stop waydroid-container
```

新しいバックアップ directory:

```bash
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/mirishita-waydroid"
BACKUP_DIR="$STATE_DIR/backups/$(date +%Y%m%d-%H%M%S)-pre-rtscale"

mkdir -p "$BACKUP_DIR"
```

既存 Gallium overlay:

```bash
sudo cp -a \
  /var/lib/waydroid/overlay/vendor/lib64/libgallium_dri.so \
  "$BACKUP_DIR/libgallium_dri.so.previous" 2>/dev/null || true
```

既存 GLES overlay:

```bash
sudo cp -a \
  /var/lib/waydroid/overlay/vendor/lib64/egl/libGLES_mesa.so \
  "$BACKUP_DIR/libGLES_mesa.so.previous" 2>/dev/null || true
```

既存 RTScale configuration:

```bash
sudo cp -a \
  /var/lib/waydroid/data/local/tmp/gles_rtscale.conf \
  "$BACKUP_DIR/gles_rtscale.conf.previous" 2>/dev/null || true
```

バックアップを通常ユーザー所有へ変更します。

```bash
sudo chown -R "$USER:$USER" "$BACKUP_DIR"
```

確認:

```bash
echo "$BACKUP_DIR"
ls -la "$BACKUP_DIR"
```

---

# 13. Install RTScale-enabled Mesa

repository に含まれる RTScale対応 Mesa は、

```text
Waydroid Android 11
LineageOS 18.1
20250621 vendor
x86_64
```

を基準としてビルドしたものを使用します。

想定配置:

```text
runtime/
└── mesa-rtscale/
    └── vendor/
        └── lib64/
            ├── libgallium_dri.so
            └── egl/
                └── libGLES_mesa.so
```

主な検証対象:

```text
AMD Radeon RX 6600 XT
AMD Radeon RX 9060 XT
AMD BC250 / Cyan Skillfish
```

Intel GPU:

```text
Experimental / unverified
```

vendor overlay directory:

```bash
sudo mkdir -p \
  /var/lib/waydroid/overlay/vendor/lib64/egl
```

Gallium:

```bash
sudo install -m0644 \
  runtime/mesa-rtscale/vendor/lib64/libgallium_dri.so \
  /var/lib/waydroid/overlay/vendor/lib64/libgallium_dri.so
```

GLES:

```bash
sudo install -m0644 \
  runtime/mesa-rtscale/vendor/lib64/egl/libGLES_mesa.so \
  /var/lib/waydroid/overlay/vendor/lib64/egl/libGLES_mesa.so
```

Waydroid を起動します。

```bash
sudo systemctl start waydroid-container
waydroid session start
```

Androidから確認:

```bash
sudo waydroid shell ls -l \
  /vendor/lib64/libgallium_dri.so \
  /vendor/lib64/egl/libGLES_mesa.so
```

---

# 14. Verify RTScale Mesa with RTScale OFF

RTScale対応Mesaを入れた直後は、設定ファイルを置かずに動作確認します。

既存のRTScale設定がある場合は削除します。

```bash
sudo rm -f \
  /var/lib/waydroid/data/local/tmp/gles_rtscale.conf
```

ミリシタを起動します。

```bash
waydroid app launch \
  com.bandainamcoent.imas_millionlive_theaterdays
```

以下を確認します。

- 正常起動
- 3D描画
- PV再生
- 音声
- 異常終了しない

ここまで正常なら、RTScale対応Mesa自体は最低限動作しています。

---

# 15. Enable RTScale

現在の基準設定は以下です。

```text
Base resolution: 1316x720
Scale: 3
Surface: 1
Texel size adjustment: 0
```

> [!NOTE]
> 1316x720 および scale=3 は現在の暫定基準です。
> 今後の実機検証によって変更される可能性があります。
>
> RTScale倍率の変更方法についても、環境依存性を含めて今後検証します。
> 現時点では複数倍率の切り替えを正式仕様とはしません。

repository には現在の基準設定として以下の1ファイルを配置します。

```text
config/
└── gles_rtscale.conf
```

内容:

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

設定 directory を作成します。

```bash
sudo mkdir -p \
  /var/lib/waydroid/data/local/tmp
```

設定を配置します。

```bash
sudo install -m0644 \
  config/gles_rtscale.conf \
  /var/lib/waydroid/data/local/tmp/gles_rtscale.conf
```

ミリシタを停止します。

```bash
sudo waydroid shell am force-stop \
  com.bandainamcoent.imas_millionlive_theaterdays
```

再起動します。

```bash
waydroid app launch \
  com.bandainamcoent.imas_millionlive_theaterdays
```

PVを再生し、RTScale OFF時と比較して描画解像度が変化していることを確認します。

---

# 16. Verify RTScale

現在の設定:

```bash
sudo waydroid shell cat \
  /data/local/tmp/gles_rtscale.conf
```

期待値:

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

RTScale関連ログを確認する場合:

```bash
sudo waydroid shell logcat -d \
  | grep GLES_RTSCALE
```

PVで以下を確認します。

- RTScale OFF時より描画品質が変化する
- 3D描画が正常
- UIが正常
- 異常終了しない
- GPU負荷が異常でない

---

# 17. Disable RTScale

RTScale configuration を削除します。

```bash
sudo rm -f \
  /var/lib/waydroid/data/local/tmp/gles_rtscale.conf
```

ミリシタを停止します。

```bash
sudo waydroid shell am force-stop \
  com.bandainamcoent.imas_millionlive_theaterdays
```

再起動します。

```bash
waydroid app launch \
  com.bandainamcoent.imas_millionlive_theaterdays
```

RTScale対応Mesa自体はoverlayに残りますが、`gles_rtscale.conf` が存在しないためRender Scale処理は無効になります。

---

# 18. RTScale Scale Changes

RTScaleの倍率変更は今後検証します。

検証予定:

- base resolution と scale の関係
- Waydroid viewportとの関係

検証完了後、必要に応じて複数のprofileまたはMWMからの倍率変更機能を追加します。

現時点では手動での倍率変更を正式な利用手順には含めません。

---

# 19. Backup Location

本手順で作成したバックアップは以下へ保存されます。

```text
~/.local/state/mirishita-waydroid/backups/
```

確認:

```bash
find \
  "${XDG_STATE_HOME:-$HOME/.local/state}/mirishita-waydroid/backups" \
  -maxdepth 2 \
  -type f \
  -print
```

将来的にはbackup / restore処理を `scripts/` および Mirishita Waydroid Manager (MWM) から自動実行できるようにします。

---

# 20. Final Check

Android:

```bash
sudo waydroid shell getprop ro.build.version.release
```

期待値:

```text
11
```

NativeBridge:

```bash
sudo waydroid shell getprop ro.dalvik.vm.native.bridge
```

期待値:

```text
libnb.so
```

Mirishita:

```bash
sudo waydroid shell pm list packages \
  | grep com.bandainamcoent.imas_millionlive_theaterdays
```

RTScale:

```bash
sudo waydroid shell cat \
  /data/local/tmp/gles_rtscale.conf
```

設定ファイルが存在しない場合:

```text
RTScale OFF
```

現在の基準設定が存在する場合:

```text
RTScale ON
Base: 1316x720
Scale: 3
```

最終構成:

```text
CachyOS
  ↓
Waydroid Android 11 / GApps
  ↓
Houdini 11 / 38765
  ↓
patched test_libnb
  ↓
Google Play Store
  ↓
Mirishita
  ↓
RTScale-enabled Mesa
  ↓
RTScale OFF / current reference configuration
```

# Status

This document is currently a work in progress.

RTScale Mesa は Android 11 / LineageOS 18.1 / 20250621 vendor を基準として再ビルド・検証したものを repository に追加する予定です。

現在の RTScale 基準値は `1316x720 / scale=3` ですが、今後の検証結果によって変更する可能性があります。

AMD Radeon RX 6600 XT / RX 9060 XT / BC250 を主な検証環境とします。

Intel GPU は現時点では Experimental / unverified です。
