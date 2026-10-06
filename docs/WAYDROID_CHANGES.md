# MWM 0.74：Waydroidへの変更内容

## 初回バックアップ

初回導入でMWMが変更するファイルと設定の元の状態を保存します。更新時は最初のバックアップを保持します。保存先は `/var/lib/mwm-backups/<UID>/baseline/` です。

対象は以下の描画ファイル15点と退避対象1点、Android内のRTScale設定ファイル、表示・入力・音量の設定値です。既存ファイルは元の内容へ復元し、新規追加ファイルは削除します。ゲームデータと他の設定は現在の状態を保持します。

## インストールで配置する描画ファイル

以下は `payload/manifests/overlay-SHA256SUMS` の15ファイルです。すべてホスト側の `/var/lib/waydroid/overlay/` を先頭につけた場所へ配置します。既存ファイルがあれば上書き、なければ追加になります。

| 用途 | overlay内の相対パス |
| --- | --- |
| GPU情報 | `vendor/etc/libdrm/amdgpu.ids` |
| 描画・バッファ共有 | `vendor/lib64/dri_gbm.so` |
| 描画・バッファ共有 | `vendor/lib64/hw/gralloc.gbm.so` |
| 描画・バッファ共有 | `vendor/lib64/libgbm_mesa.so` |
| EGL / OpenGL ES | `vendor/lib64/egl/libEGL_mesa.so` |
| EGL / OpenGL ES | `vendor/lib64/egl/libEGL_mwm_iso.so` |
| EGL / OpenGL ES | `vendor/lib64/egl/libGLESv1_CM_mesa.so` |
| EGL / OpenGL ES | `vendor/lib64/egl/libGLESv2_mesa.so` |
| Mesa描画ドライバー・コンパイラー | `vendor/lib64/libgallium_dri.so` |
| Mesa描画ドライバー・コンパイラー | `vendor/lib64/libLLVM.so` |
| Mesa描画ドライバー・コンパイラー | `vendor/lib64/libLLVM21.so` |
| DRMライブラリー | `vendor/lib64/libdrm.so` |
| DRMライブラリー | `vendor/lib64/libdrm_amdgpu.so` |
| DRMライブラリー | `vendor/lib64/libdrm_intel.so` |
| DRMライブラリー | `vendor/lib64/libdrm_radeon.so` |

Waydroidのvendor側で利用するライブラリーです。実際に読み込まれるドライバーはWaydroidのマウント状態や環境にも依存します。RTScaleバイナリーと10月4日版ISO・対応ソースの照合は継続中です。

既存の `/var/lib/waydroid/overlay/vendor/lib64/egl/libGLES_mesa.so` がある場合は、競合回避のため `${XDG_STATE_HOME:-$HOME/.local/state}/mwm-setup/iso-driver-backup/libGLES_mesa.so.<時刻>` へ退避します。アンインストール時は旧setup保存物を復旧用領域へ保全します。

## Android側の変更

Android側の設定はroot helperを通じて適用します。設定の保存とAndroidへ適用するタイミングは異なり、Waydroid Refreshで起動状態を確認して反映します。

| 対象 | 変更内容 |
| --- | --- |
| `/data/local/tmp/gles_rtscale.conf` | RTScaleの対象アプリ、基準幅・高さ、倍率、surfaceなどを書き込みます。OFFでは削除します。書き込み時は一時ファイルから置換します。 |
| `persist.waydroid.width` / `height` | 選択した描画経路とDisplay設定に基づく内部表示サイズ。 |
| `persist.waydroid.multi_windows` | 単一ウィンドウ向けにfalse。 |
| `persist.waydroid.uevent` | 入力設定としてfalse。 |
| `persist.waydroid.width_padding` / `height_padding` | 余白設定を空値へ調整。 |
| `persist.waydroid.fake_touch` | Mouse as Touch設定に応じて対象アプリなどを設定。 |
| Android `wm size` | 既存のサイズ上書きをリセットし、Waydroid側の表示サイズに合わせます。 |
| Android `settings system volume_music` | 音量調整処理で15へ設定。 |

`persist.*` とAndroid設定は保存されるため、MWMを閉じた後のWaydroid利用にも影響します。Androidの内部保存先はWaydroidのバージョンに依存するため、上表では設定キーと操作対象を示しています。

## ホスト側の関連変更

MWM本体・設定・ログ・ランチャー、root helper、専用sudoersを配置します。依存パッケージはパッケージ管理経由で導入し、音量処理はPipeWire側にも作用します。Gamescopeには起動引数と専用プロセス・生成物で設定を適用します。描画ライブラリーの配置先はWaydroid overlayで、ホストのMesa・カーネルとは別です。

アンインストールではMWMの専用ファイル・設定・ログ・権限設定を削除し、復旧用バックアップと共有依存パッケージを保持します。root helperは他ユーザーのMWM利用がなければ削除します。

## 確認範囲

ソース・マニフェスト照合、Python構文、模擬条件での復元・失敗時の保護を確認しています。Linux実機での初回導入、マウント解除、復元後の起動確認は別途必要です。
