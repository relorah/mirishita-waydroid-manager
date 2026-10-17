# RTScale 分割描画の修正候補

MWM独立実装に対するローカル修正。RTScaleの技術情報を公開したmogareta7731氏への謝辞と、Mesa／独立実装の各ライセンスは引き続き適用されます。

- https://zenn.dev/mogareta7731/articles/82f3f0d9567abc
- https://note.com/mogareta7731/n/n4db668be92b5

通常の720px高に加え、その半分の360px高の描画先と対応するScreenParamsを同じ倍率で拡大します。基準幅の上限、形式フィルター、OFF/x1の挙動は維持します。
一旦愛して♡の3D標準では1280×360／640×360と720px高のターゲットを実測し、分割カットで修正前の粗い輪郭が改善することを実画像で確認しました。画像加工による補正ではありません。

## ソースと再ビルド

既存配布のgraphics-sources.tar.zstを展開し、docs/graphics/depth-blit/README.md記載のMSAAおよびdepth-blit修正を適用したMesaソースを基準にします。本パッチはそのMesaソースルートで patch -p1 で適用できます。既存BUILD.mdと同じAPI30 / NDK r27c / LLVM21構成で再ビルドし、Mesonでステージ、anonymize-build-paths.py処理後に配布用ハッシュを更新します。

同じ通常ビルドの未変更ライブラリをステージ・正規化すると、既存配布f34d06ed52a6576dd1f558fc0c01b503f960e5933acf5be83e1e42611548a773と一致することを確認しました。撮影には別の検証用ビルドを使用しています。

テストソースは `packaging/tests/graphics/half-height/test-halfheight.c` にあります。

## 確認範囲

- 寸法変換・ScreenParams・幅の上限・対象外サイズ・OFFのCテスト通過。
- 一旦愛して♡の4分割カットと4人並びを実機で確認。
- 他楽曲、他GPU、全アスペクト比、全倍率の回帰検証は未完了。
- 本候補は公開済みv0.90へ未反映。ここには修正済み配布バイナリを含めません。
- 撮影後にゲームとWaydroidを停止し、元の描画ライブラリを復元しました。

Cテストは、リポジトリのルートで修正したgles_rtscale.cと同じヘッダーを指定してコンパイルします。

```bash
cc -I /path/to/mesa/src/mesa/main packaging/tests/graphics/half-height/test-halfheight.c /path/to/mesa/src/mesa/main/gles_rtscale.c -o test-halfheight
./test-halfheight
```

パッチ対象の独立実装とテストは0BSD。Mesa全体のライセンスや第三者ライセンスを置き換えるものではありません。
