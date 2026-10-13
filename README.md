# Mirishita Waydroid Manager (MWM)

Linux環境で「アイドルマスター ミリオンライブ！ シアターデイズ（以下、ミリシタ）」を高画質で動作させるためのプロジェクトです。Waydroid上で動作するミリシタを対象に高解像度描画、画面のアスペクト比変更、マウスのタッチ入力化、FPS・CPU／GPU使用率の表示などを設定できます。

本ツールは **ChatGPTおよびCodexを用いて作成・改修し、コード確認と実機検証を重ねて開発**しています。Mesa GLES Render Scale（RTScale）の技術公開と解説を行ったmogareta7731氏、Mesa・Waydroid・Gamescope・MangoHudをはじめとする上流プロジェクトの開発者に感謝します。

## 免責事項

MWMはミリシタの権利者や各ソフトウェアの開発元とは関係のない非公式ツールです。利用規約をご確認のうえ、ご自身の判断でご利用ください。動作や規約への適合は保証されません。利用に伴う不具合、データ消失、アカウントへの影響などについて、作者は法令上許容される範囲で責任を負いません。

MWMはWaydroidの描画ライブラリや表示・入力などを調整します。Mesa由来の描画ライブラリとMWM向けRTScale実装を導入します。本ツールはミリシタのAPKやゲームデータを同梱・改変せず、チートなどの不正な用途を目的としていません。

## 目的

- Waydroid上のミリシタで高解像度描画を実現する
- MVやライブの表示に合わせて画質や画面比率を調整する
- 描画・表示・操作の設定を一元管理する

## 主な機能

- RTScaleによる描画倍率（整数倍）の設定
- AMD FSR1によるアップスケーリングとシャープニング
- 描画アスペクト比の設定
- マウス操作のタッチ入力化
- FPS・CPU／GPU使用率などの表示
- RTScale Zoom Fixによる過度な拡大・描画ずれへの互換対応
- 診断ログの一括保存
- MWMの変更対象のバックアップと、アンインストール時の復元

## 主な構成要素

- CachyOS／Arch系Linux
- Waydroid
- Mesa GLES Render Scale（RTScale）とMWM独立実装
- Gamescope／AMD FSR1
- MWM HUD／MangoHud（MangoApp）
- Mirishita Waydroid Manager（MWM）

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

## v0.84 修正候補

Diamond Jokerの光源座標補正と、任意MSAA2によるx6のGPU負荷対策を実機検証しました。対応Mesaバイナリは検証ZIPで共有し、ソース・検証記録・適用／復元手順は[修正候補](experimental/diamond-joker/README.md)にまとめています。
