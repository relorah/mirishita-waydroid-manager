# Mirishita Waydroid Manager (MWM)

CachyOS + AMD GPU環境で「アイドルマスター ミリオンライブ！ シアターデイズ（以下、ミリシタ）」を高解像度描画するためのプロジェクトです。本ツールはChatGPTおよびCodexを用いて作成・改修し、コード確認と実機検証を重ねて開発しています。

Mesa GLES Render Scale（以下、RTScale）の技術情報を公開した[mogareta7731氏](https://zenn.dev/mogareta7731)、ならびにMesa・Waydroid・Gamescope・MangoHudなどの開発者に感謝します。

## 描画比較

### 3D標準

| RTScale OFF | RTScale x3 + FSR |
| --- | --- |
| 準備中 | 準備中 |

### 3D高画質

| RTScale OFF | RTScale x3 + FSR |
| --- | --- |
| 準備中 | 準備中 |

RTScale x3 / FSR 150% / Sharpness 11

※ 比較画像は準備中です。

## 免責事項

MWMは権利者および各ソフトウェア開発元とは関係のない非公式ツールです。利用規約を確認のうえ、自己責任でご利用ください。

## 主な機能

- RTScaleによる内部描画解像度の高倍率化
- AMD FSR1によるアップスケーリングとシャープニング
- 描画アスペクト比の設定
- マウス操作のタッチ入力化
- FPS・CPU／GPU使用率などの表示
- RTScale Zoom Fixによる過度な拡大・描画ずれへの互換対応

## 主な構成要素

- CachyOS / AMD GPU
- Waydroid（Android 11）
- Mesa GLES Render Scale（RTScale）とMWM独立実装
- Gamescope / AMD FSR1
- 独自実装のMWM HUD / MangoHud（MangoApp）
- Mirishita Waydroid Manager（MWM）

## RTScaleについて

MWMでは、mogareta7731氏が公開したRTScaleの技術情報を参考に、Waydroid向けに独立実装・調整を行っています。

- [RTScaleの技術解説 — mogareta7731氏](https://note.com/mogareta7731/n/n4db668be92b5)
- [RTScaleの利用例 — mogareta7731氏](https://note.com/mogareta7731/n/n80aebd523379)

## テスト環境

- **CPU**：AMD Ryzen 7 9700X
- **GPU**：AMD Radeon RX 6600 XT / RX 9060 XT 8GB
- **AMD BC250**：8コア16スレッド、GPU 24 CU / 40 CU構成
- **Display**：1920×1080 120Hz / 3840×2160 120Hz
- **OS**：CachyOS

## 導入と設定

インストール、更新、各設定の使い方、バックアップとアンインストールは[docs/SETUP.md](docs/SETUP.md)を参照してください。

## 開発状況

実験的な開発中のツールです。
