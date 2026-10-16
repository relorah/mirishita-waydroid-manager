# RTScaleの修正・検証資料

MWM 0.90の描画ライブラリに含まれる修正と、確認できた範囲をまとめています。導入と操作は[SETUP.md](SETUP.md)を参照してください。

RTScaleの原機能の技術公開・解説はmogareta7731氏によるものです。MWMでは、その挙動を基に再構成した独立実装とMWM側の追加修正を使用します。原作者が公開したソースそのものではありません。

## 修正と確認結果

| 対象 | 原因・対応 | 確認範囲 |
| --- | --- | --- |
| RTScale Zoom Fix | 拡大した描画先と、その参照座標・寸法の整合を取る互換処理。基本実装は対応ソースのMesaツリーに含まれます。 | 対象条件での補正であり、全シーンの正常描画を保証するものではありません。 |
| 3D高画質で光が顔や髪に重なる問題 | 拡大済みの色バッファと`_ScreenRTSize.xy`の倍率不一致を補正。対応する色サンプラーが拡大済みの場合だけ適用し、zのカメラアスペクトは維持します。 | RX 9060 XT／Android 11、Diamond Jokerの両サビ終わりで顔・髪の見え方を比較。x6・元の4サンプルでも改善を確認。 |
| 高倍率時のMSAA負荷 | RTScaleで拡大したMSAA描画先に任意の2サンプル制限を追加し、サンプル参照も物理サンプル数に合わせます。 | 同環境のx6／FSR150で主要2回の測定が平均約60 FPS。4サンプルとは画質が異なり、他環境で同じ性能になる保証はありません。 |
| 深度・ステンシルの転送 | 色アタッチメントがない描画先でも、転送対象の深度・ステンシルから座標空間を判定します。 | 独立GLESプローブ230ケースと限定的な実ゲーム回帰確認。上記MVの光源異常やFPS低下の原因と確認された修正ではありません。 |

## 詳細資料の場所

GitHubおよび対応ソース版には以下を保存しています。

- [光源補正・MSAA制限の解説](https://github.com/relorah/mltd-waydroid-manager/blob/main/docs/graphics/msaa/README.md)
- [3D高画質の実機検証記録](https://github.com/relorah/mltd-waydroid-manager/blob/main/docs/graphics/msaa/VERIFICATION-JA.md)：比較条件、性能値、光源補正の根拠、回帰確認、未確認範囲
- [深度・ステンシル転送の解説と検証範囲](https://github.com/relorah/mltd-waydroid-manager/blob/main/docs/graphics/depth-blit/README.md)
- `docs/graphics/`：適用パッチ、独立検証の結果データ

通常ZIPにはこの要約とSETUPを収録します。上の詳細資料は[GitHubのdocs/graphics](https://github.com/relorah/mltd-waydroid-manager/tree/main/docs/graphics)または同じ版の対応ソース版を参照してください。

## 対応ソースからの再構成

[0.90の配布ページ](https://github.com/relorah/mltd-waydroid-manager/releases/tag/v0.90)の`MLTD_Waydroid_Manager_v0.90_sources.tar.zst`を使用します。GitHub自動生成のSource codeとは内容が異なります。

1. 対応ソース版の`BUILD.md`と、内包する`graphics-sources.tar.zst`の`BUILD.md`を確認します。
2. 統合済みMesaソースに`mesa-msaa-storage2.patch`、`mesa-depth-only-blit.patch`を順に適用します。前者には光源の座標補正も含まれます。
3. 指定のビルド・再リンク手順に従い、ライセンスと出典を保持します。統合済みソースに`integrate.py`を重ねて実行しないでください。

基本のZoom Fixは統合済みソース、追加の光源・MSAA・転送修正は上記パッチで追えます。`packaging/tests/graphics/`には独立検証用コードを収録しています。

ソースとパッチから変更内容を追跡できますが、検証時の全動画・比較画像・測定生データは同梱していません。全曲・全GPUの動作、ビルド結果のバイト単位での一致は未確認です。資料中の旧版番号や候補版の表現は検証当時の記録です。
