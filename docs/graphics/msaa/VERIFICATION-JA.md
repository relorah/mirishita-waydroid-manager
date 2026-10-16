MWM v0.84 Diamond Joker 実機検証・修正候補（2026-10-13）
正本：https://github.com/relorah/mltd-waydroid-manager
Draft PR：https://github.com/relorah/mltd-waydroid-manager/pull/1
対象：RX 9060 XT 8GB、Waydroid Android11 x86_64、RTScale x6、FSR150、3D高画質。

確認・保全
開始main 2bca8b06762d7b13d5861618d3facd0262aa088e。再開時および最終確認の最新main bb7ebcc0c5c19146311f8cd82120bb9da17a4973。AGENTS.md・ライセンス・最新差分を確認。元のMWM/Mesaソースに未コミット／未push変更なし。設定・インストール済み配布物・元ライブラリ・Git bundleを保全。実機の比較は保全したv0.83構成を使用。新mainの構成変更は検証中の実機へ混在させない。

測定方法と比較
同じDiamond Joker、同じ描画対象の4人と衣装。各MV開始後20〜145秒。元条件のユニットchicAAmor 12/18（恵美・まつり・翼・貴音、控え海美）。3回目と最終映像ではユーザーがユニット名と控えを可奈へ変更。4人MVの描画対象と衣装は同一で、控えは出ない。開始・終了画面を確認。2回目後にUI選択が別の曲へ変わったため2回目は補足とし、主要結果は1回目と、操作が重ならない状態を確認した3回目。
SurfaceFlinger actual-present履歴を重複除去してゲームの提示間隔を計測。HUD FPSはSF実提示ベース。HUDフレーム時間グラフはGamescope側であり、ゲームGPUシェーダー実行時間ではない。映像撮影・大量診断・ビルド・自作GLESプローブは性能測定と分けた。平均FPSが60を少し上回る値は窓計測・丸めによる。

条件                         平均FPS     最低FPS     p99提示間隔    25ms超
元 x6 FSR150 第1回             58.54       44.16        33.32ms       265
元 x6 FSR150 第2回             58.74       41.45        33.34ms       216
元 x6 FSRなし                 59.61       50.00        26.41ms        92
元 x3 FSR150                  59.99       59.50        20.72ms         0
元 x3 FSRなし                 60.00       60.00        16.68ms         0
光源補正のみ x6 FSR150 MSAA4   57.98       42.01        34.25ms       342
最終候補 x6 FSR150 MSAA2 第1回 60.00       59.51        20.80ms         0
最終候補 x6 FSR150 MSAA2 第3回 60.01       59.52        20.72ms         0
補足の第2回：平均59.99、最低59.47 FPS、p99 20.74ms、25ms超0。
最終主要2回の最大提示間隔は21.319/22.048ms。元x6第2回は47.064ms。

GPU・VRAM・メモリ
ゲーム、Gamescope、HUDの実描画ノードはRX9060XT renderD128/card1。HUD GPU0は9060XT、GPU1は610M。610Mは計測中0%。GPU誤選択の証拠なし。
元x6 FSR150のGPU平均87.66/88.01%、最大100%。最終主要2回58.73/62.24%。x3は約27%。元x6のVRAM最大4.64〜4.72GiB/7.95GiB、最終候補約3.44〜3.51GiB。元条件RAM空き最小21.0GiB、候補約21GiB以上、Swap約2MiB。容量不足を示さない。初回に単一CPUコア100%の一時値があるが、再測定でもFPS低下し単一コア最大54%だった。候補CPU平均約9.8%。CPUの一時影響を完全否定せず、継続するGPU負荷と区別した。カード別負荷・VRAM/GTT・RAM・電力・温度・クロック・プロセス別gfx/computeの生データを同梱。

性能低下の原因と対策
x6で主要RTが1280x720から7680x4320へ昇格し、4x MSAAと光源・ポスト処理でGPUを飽和。x3は画素数が1/4で安定し、FSRを切ってもx6は低下した。FSR単独原因・VRAM/RAM容量不足・別GPU描画を主因とする証拠はない。帯域、フィルレート、個々のシェーダーの寄与を厳密に分離するGPUタイマー測定は未実施。
任意設定msaa_samples=2で、RTScaleにより昇格したMSAA格納を2サンプルに制限。物理サンプル数が2の場合だけsample indexをwrapし、fragmentとvertex等の共通variantへ適用。x6のRT寸法は保つ。GLES広告上限は変更しない。0/設定なしは元のMSAA要求どおり。Zoom Fix必須。AA品質変更を伴い、4サンプルと画質完全同一ではない。

光源がキャラへ被る問題
1回目サビ終わりの4人カットと2回目サビ終わりをRTSなし(x1)・元x6・性能だけ変更した候補で比較。元x6では顔や髪へ黄色／白の光が被り、2回目は上部の大きな白い帯になった。RTSなしでは顔や髪が見える。MSAAだけ2へ変更しても光源問題は残る。
原因：昇格した_ColorBufferのTexelSize寸法は6倍だが、_ScreenRTSize.xy の逆数寸法が論理解像度のままで、対応する座標計算に6倍の不整合が生じる。実描画ログと独立UVプローブで確認。補正は対応する色サンプラーが拡大済みの場合のみxyを倍率で割り、zのカメラaspect（4分割の幅も含む）は保持する。拡大しない描画先・RTSなしへは適用しない。
x6・元の4MSAAを維持した光源補正のみの全曲映像で、両サビ終わりの顔・髪が戻ることを確認。撮影はAndroid側（Gamescope FSR前）でも差を再現するため、この見え方をFSRだけへ帰属しない。
最終配布バイナリ＋MSAA2でも全曲映像を撮影し、両サビ終わりの同ポーズで顔・髪が見えることを確認。比較画像を同梱。最終動画内の対応フレームは1回目57.8秒、2回目115.8秒。
比較画像の時刻は収録開始からの時刻であり、ロード時間差があるため曲の秒数とは同一ではない。元の同じポーズを照合する。静止画HUD60を性能測定の代わりにしない。

修正候補と回帰検証
全11 Galliumドライバ構成、API30、NDK r27c、LLVM21 Android ABI checks ON。最終libgallium_dri.so SHA256：
6a77eba981aa1163edf3351f15be38752a9a0da7ecd2a04ee273f388cb8b7116
診断コード・RUNPATHなし。既存EGL/GLES/LLVMを保持。
色／深度MSAA texture、renderbuffer、物理解像度、FBO completeness、4-index色resolve、左右別depth occlusion、vertex sample2 fetchをMSAA2／既定0／scale1で実機合格。UV・aspectプローブは通常幅、4分割幅、小さい非拡大描画先、scale1で合格。helper 5件、parser 7件、Bash構文、diffチェック、元ソース＋パッチから変更6ファイルの完全再構成が合格。
旧中間ZIPのfragmentだけの補正はvertex sample2プローブで不合格で、今回の候補で修正済み。旧中間版より今回を優先する。
独立プローブでdepth-only blit・CopyImageSubDataの不具合も確認したが、このMVで利用ログがないため今回の原因や修正候補に含めない。未採用の試験コード・ゲームの非公開シェーダー/IRは配布しない。

未確認事項と配布範囲
対象実機と対象MVの4人カット・性能は検証。他GPU、他Android環境、全曲、異なる描画先のbinding順序は未検証。全11ドライバはコンパイル済みでも、実機検証はradeonsiのみ。4MSAAと完全同一の画質で60FPSを保つ最適化は未実施。光源補正だけでAA品質を保つモードは使用可能だが、元のGPU負荷によるFPS低下は残った。
MWM MIT、独立RTScale/自作プローブ0BSD、Mesaのファイル別通知、LLVM Apache例外、静的libelf LGPLv3と対応ソース・再リンク手順を同梱。フル対応ソースアーカイブ＋適用パッチ・BUILD.mdから再ビルド可能。integrate.pyを重ねて実行しない。ビット単位の再現性は未検証。ゲームデータ・APK・Houdini・ゲームシェーダーは含めない。

復元・保存
最終候補の適用・復元実機試験：合格。終了時に元ライブラリ678c0b...、helper、設定スクリプト、全MWM設定、Android設定を保全時とバイト一致で復元。x6・FSR150、msaa_samples設定ファイルなし、debug property復元、診断マーカー削除を確認。
Release公開、ゲームデータ削除・初期化は行わない。バージョン正本mwm/version.pyを0.84へ改定し、検証済みライブラリをGitのMesa payloadへ反映。通常installer/GUI全体の再インストールは未実施で、実機は検証済み候補の適用・復元で確認。変更は作業ブランチ／Draft PRで共有。ZIPは候補ライブラリ、helper/設定スクリプト、適用・復元手順、ソース／ライセンス、測定生データ／集計、比較画像を含む。ZIP CRCとSHA256、Driveの保存先フォルダとサイズを確認して最終保存する。依頼の「5時間枠2回」は許可された作業枠であり、10時間連続計測を行ったという記録ではない。
