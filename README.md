# MLTD Waydroid Manager (MWM)

Linux + AMD GPU環境で「アイドルマスター ミリオンライブ！ シアターデイズ（以下、ミリシタ）」を高解像度描画するためのプロジェクトです。本ツールはChatGPTおよびCodexを用いて作成・改修し、CachyOSでの実機検証を重ねて開発しています。

## 謝辞

Mesa GLES Render Scale（以下、RTScale）の技術情報を公開した[mogareta7731氏](https://zenn.dev/mogareta7731)、ならびにMesa・Waydroid・Gamescope・MangoHudなどの開発者に感謝します。

MWMで使用するRTScaleは、mogareta7731氏が公開した技術情報をもとに独立実装したものです。

- [Mesa GLES Render Scale（Render Target Scale）について - note](https://note.com/mogareta7731/n/n4db668be92b5)
- [Mesa GLES Render Scaleの利用例 - note](https://note.com/mogareta7731/n/n80aebd523379)

## 免責事項

MWMはミリシタの権利者および各ソフトウェアの開発元とは関係のない非公式ツールです。WaydroidおよびGamescopeの描画・表示設定などを調整するもので、APKやゲームデータを改変せず、チートなどの不正行為を目的としたものではありません。

利用規約を確認のうえご自身の判断でご利用ください。利用に伴う不具合、データ消失、アカウントへの影響などについて、作者は法令上許容される範囲で責任を負いません。

## 描画比較

Gamescope・16:9で撮影した実機MVです。3D標準はRTScale OFF／x3、3D高画質はOFF／x6を比較しています。高画質の両側はFSR 150%・Sharp 10で固定しています。元の表示は標準1920×1080、高画質3840×2160で、以下は縮小プレビューです。OFF側もAndroid表示を1920×1080に固定した撮影条件で、通常のGUIのOFF既定表示とは異なります。

同じ編成・衣装・画質と近いカメラ・ポーズを合わせていますが、別再生のため髪・衣装・紙吹雪などに微小な時間差があります。性能測定ではなく見た目の参考です。

### 一旦愛して♡ — 3D標準

![一旦愛して♡：RTScale OFFとx3、黄色バック](docs/images/readme/ittan_aishite-comparison.webp)

同じ位置を切り出して200%表示した拡大比較です。最近傍補間を使用し、原寸PNGへ描画補正は加えていません。

![未来の拡大比較：RTScale OFFとx3](docs/images/readme/ittan-yellow-mirai-200pct.webp)

![杏奈の拡大比較：RTScale OFFとx3](docs/images/readme/ittan-yellow-anna-200pct.webp)

一旦愛して♡は[分割描画対応の修正候補](docs/graphics/half-height/README.md)で再録しました。この修正は公開済みv0.90の配布バイナリにはまだ含まれていません。4人並びに加え、4分割カットでも比較しています。

### 一旦愛して♡ — 4分割カット / 3D標準

![一旦愛して♡の4分割カット：RTScale OFFとx3](docs/images/readme/ittan-split-comparison.webp)

同じ位置を切り出した200%拡大比較です。こちらも分割描画対応の修正候補で撮影しています。

![杏奈の4分割カット拡大比較：RTScale OFFとx3](docs/images/readme/ittan-split-anna-200pct.webp)

![未来の4分割カット拡大比較：RTScale OFFとx3](docs/images/readme/ittan-split-mirai-200pct.webp)

### 蝶々むすび — 13人ライブ / 3D高画質

![蝶々むすび：RTScale OFFとx6 / FSR 150% / Sharp 10、髪型修正後](docs/images/readme/choucho_musubi-comparison.webp)

同じ位置を切り出した200%拡大比較です。FSR 150%・Sharp 10は両側で共通です。拡大は最近傍補間を使用し、原寸PNGへ描画補正は加えていません。

![麗花の拡大比較：RTScale OFFとx6 / FSR 150% / Sharp 10](docs/images/readme/choucho-reika-200pct.webp)

![ジュリアの拡大比較：RTScale OFFとx6 / FSR 150% / Sharp 10](docs/images/readme/choucho-julia-200pct.webp)

画像内のゲーム・キャラクター等の権利は各権利者に帰属します。

## 主な機能

- RTScaleによる内部描画解像度の高倍率化
- AMD FSR1によるアップスケーリングとシャープニング
- 描画アスペクト比の設定
- マウス操作のタッチ入力化
- FPS・CPU／GPU使用率などの表示
- RTScale Zoom Fixによる過度な拡大・描画ずれへの互換対応

## 使用技術

- CachyOS / Waydroid（Android 11）
- Mesa GLES Render Scale（RTScale）とMWM独立実装
- Gamescope / AMD FSR1
- 独自実装のMWM HUD / MangoHud（MangoApp）

## テスト環境

- **CPU**：AMD Ryzen 7 9700X
- **GPU**：AMD Radeon RX 6600 XT / RX 9060 XT 8GB
- **AMD BC250**：8コア16スレッド、GPU 24 CU / 40 CU構成
- **Display**：1920×1080 120Hz / 3840×2160 120Hz
- **OS**：CachyOS

## 導入と設定

インストールや更新、使い方などは[docs/SETUP.md](docs/SETUP.md)を参照してください。

## 開発状況

実験的な開発中のツールです。
