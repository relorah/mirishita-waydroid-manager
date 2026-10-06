# 同梱描画資産の確認状況

対象：MWM 0.74。これは確定済みの再ビルド手順・ライセンス監査結果ではありません。

## 出典

RTScale原機能の作者はmogareta7731氏です。利用者報告では今回も同氏の10月4日版ISOに内包されたライブラリを利用しています。
参考記事：https://zenn.dev/mogareta7731/articles/94204fa83b239b

payload/manifests/graphics-stack.lockのISO SHA256は49cd1c90d19173774a0d79aa891f7d527949515e2b9c162a4cfc80261edbcdf8です。これは既存記録であり、今回原ISOを入手して照合した結果ではありません。

## 同梱範囲

payload/graphicsにはMesa runtime、Mesa RTScale、LLVM 21、libdrm、GBM/grallocの5 overlayがあります。各アーカイブの同一性はpayload/SHA256SUMSで確認します。バイナリの元版・変更箇所・対応ソースは別途照合が必要です。

docs/graphics-build/iso-asset-adapterは追加ラッパーのソースです。ISO内Mesa/RTScaleの全ソースではありません。9/8版の独立復元・Mesa再ビルド・libelf静的リンクの旧説明を今回のISO版の確定情報として流用しません。

## 公開前の残件

- 原ISOの取得元・正式版・ハッシュと採用ライブラリを対応付ける。
- 実バイナリと対応ソース・パッチ・ビルド条件を照合する。
- 各成果物のライセンスと必要な通知・ソース提供条件を確認する。
- 必要な対応ソースの提供場所を案内する。MWMの軽量ZIPへ全ソースを同梱するかは、この確認後に判断する。

旧版専用ビルド資料は今回の配布から外しています。原ソースの確認不足を、資料の削除で解消したとは扱いません。
