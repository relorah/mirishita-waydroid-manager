# MWM v0.84 追加枠・実機検証レポート

記録日時：2026-10-14T07:00:10+09:00。追加枠は2026-10-14 04:59 JSTに開始。完了した測定だけを掲載する。

## 結果

Thank You!39人版の約0.5秒の空白は、読み込み終盤を含む旧20〜140秒集計で観測したものだった。演奏中の遅延として扱った記録を訂正する。RTScale x1・設定完全OFFでも500〜517msが再現し、GPU平均は約12%。別映像では26秒までNow Loading、28秒でステージ導入、35秒で歌唱。歌唱中40〜140秒に500msの空白はなく、x5/x6は約59.96〜59.99FPS、x1/OFFは約60FPSだった。

起動・更新の確認済み修正は[PR #3](https://github.com/relorah/mirishita-waydroid-manager/pull/3)と[PR #4](https://github.com/relorah/mirishita-waydroid-manager/pull/4)。新しい深度Blitの独立API修正は[Draft PR #5](https://github.com/relorah/mirishita-waydroid-manager/pull/5)で共有するが、ゲーム側の原因とは確認されていない。初回候補起動のNative Bridge SIGSEGVが未確定のため、新しい描画バイナリは配布しない。現機は元のv0.84描画ライブラリを使用する。

## 環境・計測方法

RX 9060 XT 8GB（PCI03:00、card1/renderD128）、Ryzen 7 9700X、Boost ONを読取り確認。CPU75度制限はユーザー報告で、制限設定自体は未確認。CPU電力・クロック・電圧・温度上限は変更していない。ゲームとGamescopeの描画GPUは9060 XT。統合610Mはcard0/renderD129で、計測GPUの取り違えによるFPS低下の証拠はない。

Thank You!、MV、39人モード、3D高画質、編成・衣装を維持。グループA/B/C各13人（上段5＋下段8のON STAGEカード）を実画面で再確認し、実映像の多段ステージに大人数が描画されることも確認。旧5人版は39人結果から除外し、原始記録を保全した。

FSR150、Android1920×1080、RTScale基準1280×720を読戻し確認。AGENTSの固定1316×720という記述との不一致は未整理で、基準値を変更していない。FSR内側1920×1080→2880×1620、外側起動引数2648×1490。KDEの4K出力はlogical2649×1490・scale1.45で、実Gamescope surface bufferの物理ピクセル数は未確認。OFF対照はrender-mode=rtscaleと同じ表示条件を維持し、Android RTScale設定ファイルだけを完全に無効化したもの。

SurfaceFlingerのactualPresentTimeを重複除去し、歌唱中の40〜140秒を集計。GPU/VRAM・CPU・RAM、DRM engineを併記する。提示間隔はGPU shader単体時間や最終モニター走査の全フレーム検査ではない。1秒窓には59/61の境界差があり、HUDの平滑FPSと同一視しない。MangoApp無効時のキャッシュ0をゲームFPSとして使わない。主測定中は画面取得・操作・ビルドを挟まない。

## 歌唱区間の再集計

| 条件・試行 | 平均提示FPS | p99 ms | 最大ms | 25ms超 | GPU平均 | 最大VRAM GiB |
|---|---:|---:|---:|---:|---:|---:|
| actual39-off-default-run1 | 59.999 | 20.73 | 21.05 | 0 | 12.2% | 1.97 |
| actual39-x1-default-run1 | 60.001 | 20.74 | 20.96 | 0 | 12.5% | 1.99 |
| actual39-x5-default-fsr150-run1 | 59.989 | 20.80 | 33.57 | 1 | 52.3% | 3.28 |
| actual39-x6-default-fsr150-run1 | 59.972 | 20.84 | 33.35 | 12 | 67.4% | 3.75 |
| actual39-x6-msaa2-fsr150-run1 | 59.958 | 20.87 | 33.46 | 4 | 46.5% | 3.28 |
| actual39-x6-msaa2-fsr150-run2 | 59.976 | 20.75 | 33.36 | 2 | 45.9% | 3.28 |

x1の再再生でも序盤500msを確認したが、その試行は約70秒で1秒のperf権限テストを行ったため、厳密な主比較表から除外した。元の20〜140秒集計・原始JSONLも削除せず同梱し、読み込みを含む値と歌唱中の値を区別する。前枠の表は「演奏中のFPS」として使わない。

## 読み込み区間のCPU診断

別のOFF診断で25.301〜25.801秒に499.983msの空白を再現。周辺約0.7秒でUnityMainのCPU実行は約92%/1core、runqueue待ちは約0.7ms。UnityGfxDeviceWは約2.3%実行でfutex待機が中心だった。55 CPU-clockサンプルの約87%はUnityMainのlibtcb.so／匿名コード領域。GPU描画の持続的飽和より、演奏開始前の主スレッド側処理として切り分けられる。

具体的なゲーム処理・GC・資産読み込み・Native Bridge内部処理のどれかは未特定。プロファイルの負荷があるため、この診断を主FPS比較に混ぜない。23秒のNow Loading、27秒の黒い遷移画面、35秒の歌唱を同じ診断で記録した。根拠のないCPU設定変更やゲームプログラム修正はしない。

## 連続再生とメモリ

元のv0.84、x5/FSR150/MSAA明示指定なしで10回の39人MVを正常に再生。現在の記録範囲は約34.6分。毎回曲・MV・39人モードの画像ガードを通し、想定外画面なら操作を止める。PSSは正確なパッケージ名に一致するゲームプロセス群の再生後の値で、共有ページを単純なRSS合算で二重計上しない。VRAMはGPU全体の値。再生中ピークと終了後の値を区別する。

| 再生 | 歌唱平均FPS | 最大提示ms | 25ms超 | 終了後PSS MiB | 終了後VRAM GiB |
|---|---:|---:|---:|---:|---:|
| 1 | 59.999 | 21.11 | 0 | 2064.6 | 1.74 |
| 2 | 59.989 | 33.33 | 1 | 2050.0 | 1.73 |
| 3 | 59.978 | 33.32 | 2 | 2057.9 | 1.74 |
| 4 | 59.989 | 33.30 | 1 | 2063.0 | 1.77 |
| 5 | 60.001 | 21.12 | 0 | 2049.3 | 1.77 |
| 6 | 59.999 | 20.97 | 0 | 2048.1 | 1.76 |
| 7 | 59.999 | 21.28 | 0 | 2070.0 | 1.74 |
| 8 | 59.999 | 21.30 | 0 | 2066.1 | 1.74 |
| 9 | 59.979 | 33.32 | 2 | 2056.1 | 1.74 |
| 10 | 59.989 | 33.33 | 1 | 2067.9 | 1.74 |

この記録範囲での推移を評価する。より長い連続稼働、他曲、衣装変更後、異なる設定でのメモリ安定性まで保証するものではない。

## 独立した深度Blit不具合

COLOR0がないフレームバッファの拡大判定が欠落し、MSAA色＋深度sourceから深度のみdestinationへのコピーがGL_INVALID_OPERATION 0x502になることを現行v0.84で再現。両端が深度のみならエラーなしで一部領域だけがコピーされる。独立GLES試験の最終ソース候補v2は230/230件PASS：x1/x3/x5/x6、標準MSAA/MSAA2、Texture/Renderbuffer、depth/stencil/両方、MSAA/単一サンプル、左右の全物理領域とコピーしないplane保持。 baselineの旧packed試験scaled54件は期待した失敗として保全している。さらにDEPTH24_STENCIL8をステンシルだけに添付し、存在しない深度bitを含めたmaskで最初の候補の部分コピーを再現。空の深度添付を飛ばして有効なステンシル添付を確認する形へ修正し、既存200件＋この12件＋DEPTH_COMPONENT16 Renderbuffer12件＋非拡大STENCIL_INDEX8の6件を通した。単独STENCIL_INDEX8を拡大対象と誤って期待した最初の試験は前提不成立として保全・除外し、非拡大の正しい対照で確認した。

Waydroid外側CLIは子プログラム失敗でも0を返したため、実Androidプログラムの終了コードをMWM_PROBE_RCで読み取り、pixel assertとPASSマーカーを確認する。CLIの0だけで検証済みとは判定しない。

39人OFF対照の150秒API追跡ではBlit/CopyImageを記録せず、独立Blit陽性対照ではmask256の1回を記録して追跡動作を確認。CopyImage familyの個別陽性対照は未実施。追加したkernel traceイベントは全て削除した。このAPI修正は読み込み中500msやDiamond Joker FPSの原因には含めない。

第一候補7e027d...の初回起動はlibhoudini.so内のSIGSEGVで終了。元04c12b...を戻すと正常起動し、候補2回目は39人MVを完走（59.945FPS、最大33.37ms）。因果関係は未確定で、描画バイナリ配布は保留、現機は元04c12b...へ戻した。新しいプロトタイプを安定版や推奨FPS修正として扱わない。

最終v2のバイナリcdf5ad1e...は隔離GLES試験だけで確認し、ゲームに入れていない。ゲーム回帰230件という意味ではなく、新描画バイナリの配布は引き続き保留する。

原本graphics-sources.tar.zst（6ddc1e4...）のMesa11,692ファイルを比較し、既存v0.84修正6ファイル＋blitの7だけが変更。2patch再適用で全7ファイルのバイト一致を確認。修正なし再ビルドは元のv0.84ライブラリとバイト一致。Mesa acbb4f6...、NDK r27c/API30、LLVM21 ABI checks ON、11ドライバを保持。Mesa MIT・復元0BSD・LLVM・LGPL libelfの出典と再リンク要件を維持する。ソース候補ZIPに新しいMesaバイナリ・ゲームshader・APK・Native Bridge payloadは含めない。

## MWM起動・更新修正の状態

PR #3：インストール先のversion.py import失敗、成功後の二重guard cleanupによるexit1を修正。PR #4：既存非対話sudoアクセスがある場合にsudo -vで無人更新が止まる問題を修正。既存権限を確認するだけで、新しい権限は追加しない。

前枠でPython23件、新規5件の回帰、Bash構文・diff検査PASS。実機高速x5↔x6でAndroid/Gamescopeのプロセスを保ってexit0、MSAA切替の完全再起動、Auto Start/Verify Startup OFF、不正MSAA拒否、設定ロック・中断設定保護、通常/app-only更新、全保存設定・14管理対象ファイルの照合も確認。対話パスワード入力は未確認。今回コードを変更していないので同じテストを無意味に繰り返さない。

## 復元・共有・未確認

開始時のRTScale x5・FSR150・MSAA明示指定なしへ戻す。高速Refreshの確認済み2スクリプトは保持するが、Mesaは開始時の6a77eba981aa1163edf3351f15be38752a9a0da7ecd2a04ee273f388cb8b7116。復元照合結果は同梱のround4-restoration-proof.jsonに記録。全項目PASS。

ゲームデータの削除・初期化、APK/ゲームプログラム/Native Bridgeの変更は行っていない。新規Release・公開v0.84差替え・追加mainマージなし。作業ブランチ・Draft PR・ZIPで共有する。使用量リセットクレジットは使っていない。

[高速Refresh ZIP](https://drive.google.com/file/d/1VjoZ8ZZfsgnFA_XPrbn_7hMEWVYf8Oua/view)、[installer ZIP](https://drive.google.com/file/d/1ZV4T5Mtw2gquAQE7EWHS5uiuxYTBinX9/view)、[深度ソース候補ZIP（描画バイナリなし）](https://drive.google.com/file/d/1OLdba_uO2NVfGfEPRIMo9JZ-wxDmSSUa/view)。最終MD/TXT・検証と修正ZIPはDriveルートへ、更新ZIPはGitへ保存する。

未確認：Native Bridge初回SIGSEGVの原因、読み込み内部処理の詳細、他GPU/全GLES適合性/今回以外のdepth format/部分・反転矩形、より長い連続稼働、実surface pixel数、HUD最大約2FPS差。確認できた範囲と未確認事項を混ぜて修正しない。
