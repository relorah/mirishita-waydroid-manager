# Mirishita Waydroid Manager (MWM)

「アイドルマスター ミリオンライブ！ シアターデイズ（以下、ミリシタ）」をCachyOS + AMD GPU環境で高解像度描画するためのプロジェクトです。Waydroid上のミリシタを対象に、描画解像度、画面比率、マウス入力、HUDなどを設定できます。

本ツールは **ChatGPTおよびCodexを用いて作成・改修し、コード確認と実機検証を重ねて開発**しています。Mesa GLES Render Scale（以下、RTScale）の[技術公開と解説を行ったmogareta7731氏](https://note.com/mogareta7731/n/n4db668be92b5)と、Mesa・Waydroid・Gamescope・MangoHudなどの開発者に感謝します。

## 免責事項

MWMはミリシタの権利者および各ソフトウェアの開発元とは関係のない非公式ツールです。利用規約を確認のうえ、自己責任でご利用ください。ミリシタのAPKやゲームデータは同梱・改変しません。

## 目的

- Waydroid上でミリシタの高解像度描画を実現する

## 主な機能

- RTScaleによる内部描画解像度の高倍率化
- AMD FSR1によるアップスケーリングとシャープニング
- 描画アスペクト比の設定
- マウス操作のタッチ入力化
- FPS・CPU／GPU使用率などの表示
- RTScale Zoom Fixによる過度な拡大・描画ずれへの互換対応

## 主な構成要素

- CachyOS／Arch系Linux
- Waydroid（Android 11）
- Mesa GLES Render Scale（RTScale）とMWM独立実装
- Gamescope／AMD FSR1
- MWM HUD／MangoHud（MangoApp）
- Mirishita Waydroid Manager（MWM）

## 描画比較

同一場面をRTScale OFFとRTScale x3 + FSR 150% / Sharpness 11で比較する画像枠です。画像は未提供のため、以下はプレースホルダーです。

| 画質設定 | RTScale OFF | RTScale x3 + FSR 150% / Sharpness 11 |
| --- | --- | --- |
| 3D標準 | 画像未提供（プレースホルダー） | 画像未提供（プレースホルダー） |
| 3D高画質 | 画像未提供（プレースホルダー） | 画像未提供（プレースホルダー） |

## テスト環境

以下は開発・動作確認に使用した環境です。

- CPU：AMD Ryzen 7 9700X
- GPU：AMD Radeon RX 6600 XT／RX 9060 XT 8GB
- AMD BC250：8コア16スレッド構成、GPU 24 CU／40 CU構成
- ディスプレイ：1920×1080 120Hz、3840×2160 120Hz

## 導入と設定

インストール、更新、各設定の使い方、バックアップとアンインストールは[SETUP.md](docs/SETUP.md)を参照してください。

## 開発状況

実験的な開発中のツールです。

