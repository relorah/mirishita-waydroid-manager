# Setup Guide

CachyOS + Waydroid Android 11 環境で  
「アイドルマスター ミリオンライブ！ シアターデイズ (ミリシタ)」を起動し、
Mesa GLES Render Scale (RTScale) を利用するまでのセットアップ手順です。

> [!WARNING]
> このプロジェクトは現在 Experimental / Work in progress です。  
> 未検証または手順確定前の項目は `TODO` として記載しています。

## Target Environment

### Host

- OS: CachyOS
- Architecture: x86_64
- Shell: Bash
- Desktop: Wayland
- GPU: AMD Radeon を主な検証対象とする

### Waydroid

- Android 11
- Mirishita package:

```text
com.bandainamcoent.imas_millionlive_theaterdays
```

### Reference Configuration

- Waydroid Android 11
- Houdini
- test_libnb
- Mesa GLES Render Scale (RTScale)

---

# 1. Required Packages

CachyOS を最新状態にします。

```bash
sudo pacman -Syu
```

基本的なビルドツールを導入します。

```bash
sudo pacman -S --needed \
  git \
  base-devel \
  python \
  python-pip \
  python-virtualenv \
  meson \
  ninja \
  cmake \
  pkgconf
```

追加パッケージについては、Waydroid / test_libnb / Mesa RTScale の実機検証後に固定します。

---

# 2. Install Waydroid Android 11

Waydroid Android 11 を導入します。

TODO:

- CachyOS への Waydroid 導入手順
- Android 11 image の取得方法
- 必要な Waydroid 設定

インストール後に状態を確認します。

```bash
waydroid status
```

Android version:

```bash
sudo waydroid shell getprop ro.build.version.release
```

期待値:

```text
11
```

Waydroid container を起動します。

```bash
sudo systemctl start waydroid-container
```

session を開始します。

```bash
waydroid session start
```

Waydroid UI が正常に起動することを確認します。

---

# 3. Install Houdini

ミリシタの ARM native code を x86_64 Waydroid 上で実行するため、Houdini を導入します。

Houdini の導入には `casualsnek/waydroid_script` または本プロジェクト用 fork を使用します。

Houdini binary や WSA image 自体はこの repository には含めません。

TODO:

- 使用する waydroid_script fork
- 動作確認済み revision
- Houdini 11 のインストールコマンド

導入後に NativeBridge の状態を確認します。

```bash
sudo waydroid shell getprop ro.dalvik.vm.native.bridge
```

Houdini の配置確認:

```bash
sudo waydroid shell \
  'ls -l /system/lib*/libhoudini* 2>/dev/null'
```

---

# 4. Build / Install test_libnb

test_libnb を導入します。

test_libnb は NativeBridge wrapper として使用し、Houdini をミリシタ実行環境で利用するための補助を行います。

TODO:

- 使用する test_libnb fork
- 動作確認済み revision
- build dependencies
- 32-bit build
- 64-bit build
- install destination
- Waydroid Android 11 向け patch / configuration

test_libnb を変更する場合は upstream 由来のコードと本プロジェクト側の変更を区別します。

導入後:

```bash
sudo waydroid shell \
  'ls -l /system/lib*/libnb.so 2>/dev/null'
```

NativeBridge:

```bash
sudo waydroid shell getprop ro.dalvik.vm.native.bridge
```

---

# 5. Install Mirishita

ミリシタを Waydroid にインストールします。

Package name:

```text
com.bandainamcoent.
