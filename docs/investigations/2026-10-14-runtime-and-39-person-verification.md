# MWM v0.84 追加実機検証・現枠レポート

記録日時：2026-10-14T03:05:05+09:00。検証継続中。追加5時間枠の続行をユーザーが許可済み。

## 追加枠による計測区間の訂正（2026-10-14）

前枠の20〜140秒はMV読み込み終盤を含んでいた。下の旧集計表の約500msを演奏中の遅延として扱わない。別の映像確認で26秒までNow Loading、28秒でステージ導入、35秒で歌唱を確認。40〜140秒の再集計はx5/x6約59.96〜59.99FPS、x1/OFF約60FPS。元データと旧集計は保全し、読み込みと歌唱を別評価する。

[区間訂正の記録](https://drive.google.com/file/d/16q8zD_OxfmoGM-uTG-gFrotlvYkxdULi/view)。追加枠は検証継続中。

## 確認・修正した不具合

1. インストール先の rts-fast-state.py がアプリ直下の version.py を読み込めず ModuleNotFoundError になる。アプリのディレクトリを読み込み経路へ追加して修正。
2. 高速Refresh成功後の二重guard cleanupが、解除済み変数を参照し exit 1 になる。実機で修正前を再現し、重複cleanupを削除。修正後はAndroid/Compositorの同一プロセスを維持したx5↔x6のRefreshが exit 0。
3. 既に非対話sudo権限がある環境でもinstall.shのsudo -vがパスワードを要求し無人更新がexit 1。sudo -n trueで既存アクセスを確認し、利用できない場合のみ従来のsudo -vへ進む。権限を追加・拡大する修正ではない。

Git共有： [高速Refresh PR #3](https://github.com/relorah/mirishita-waydroid-manager/pull/3)、[管理者アクセス確認 PR #4](https://github.com/relorah/mirishita-waydroid-manager/pull/4)。どちらもDraft。追加修正のmainへのマージ、新規Release公開、公開v0.84の差替えは行っていない。

修正ZIP： [高速Refresh](https://drive.google.com/file/d/1VjoZ8ZZfsgnFA_XPrbn_7hMEWVYf8Oua/view)、[管理者アクセス](https://drive.google.com/file/d/1ZV4T5Mtw2gquAQE7EWHS5uiuxYTBinX9/view)。両ZIPは各Git作業ブランチのupdatesディレクトリにも保存済み。描画ライブラリ変更は含まない。

## 修正と設定分岐の検証

新規5件を含むPython unittest 23件 PASS、Bash構文とgit diff --check PASS。shellcheckは未導入。MSAA標準↔2は完全再起動に切替わり、Android側設定の読戻しにも成功。不正MSAA値はAndroidを書き換える前にexit 2。Auto Start OFFではゲームを起動せず、通常/高速Refreshとも正常終了。Verify Startup OFFは検証を省略して手動ゲーム起動へ進む。設定保存ロックと中断設定の保護も、各exit 75/78を確認。

アプリのみ更新・通常インストールは実機で正常終了。最初は認証部分のみ差し替えた検証用コピーを使い、その後はPR #4の修正installerをそのまま使用して両手順を確認した。全保存設定のバイト一致、管理対象ライブラリ・root helperのSHA256一致、既存baseline backupの保持を確認。通常のパスワード入力が必要な環境での対話入力は未確認。

## 実39人版の旧集計（読み込みを含む20〜140秒）

RX 9060 XT 8GB、Ryzen 7 9700X（8core/16thread）、Boost ONを読取り確認。CPU75度制限はユーザー報告で、制限設定自体の読戻しは未実施。実測Tctlは概ね76度付近。CPU設定・電力・クロック制御は変更していない。

Thank You!、39人モード、グループA/B/C各13人、3D高画質。編成と衣装を維持。実映像の多段ステージで大人数の描画を確認。FSR150、Android1920×1080、RTScale基準はAndroid読戻しで1280×720。AGENTSの固定1316×720という記述との不一致は未整理で、検証のために基準値そのものを変更していない。内部FSR1920×1080→2880×1620→起動引数上は外側2648×1490へのlinear fit。KDEのfractional scalingと実surface bufferのピクセル数の関係は追加確認対象。現在のGamescope出力は以前の測定条件と同一とは扱わない。

ゲームのactualPresentTimeを重複除去し、MV再生操作後20〜140秒を集計。ゲーム側の提示間隔であり、直接のshader GPU実行時間や最終モニター走査の全フレーム検査ではない。1秒提示数は窓境界により59/61になることがあり、HUDの平滑FPSと直接同一視しない。MangoAppが無効なときのキャッシュ0はゲームFPSとして使わない。曲終了・読み込みを含む140秒後の大きな間隔は別扱い。主測定中は画面取得・操作・ビルドを挟んでいない。

| 条件・試行 | 平均実測FPS | 最低1秒提示数 | p99 ms | 最大ms | 25ms超 | GPU平均 | 最大VRAM GiB |
|---|---:|---:|---:|---:|---:|---:|---:|
| actual39-x5-default-fsr150-run1 | 59.457 | 29 | 20.83 | 500.01 | 15 | 51.3% | 3.28 |
| actual39-x6-default-fsr150-run1 | 59.408 | 21 | 20.85 | 516.66 | 25 | 66.4% | 3.78 |
| actual39-x6-msaa2-fsr150-run1 | 59.522 | 20 | 20.85 | 499.97 | 13 | 46.1% | 3.32 |
| actual39-x6-msaa2-fsr150-run2 | 59.580 | 19 | 20.97 | 499.97 | 9 | 46.1% | 3.32 |

MSAA2では約0.5秒の提示間隔が序盤に2回の試行とも再現し、標準MSAAでも同程度の遅延が再現し、RTScale x5の標準MSAAでも再現した。MSAA2だけに固有の現象ではない。継続的なGPU飽和やVRAM容量不足を原因とする証拠は得ていない。CPU・読み込み・ゲーム側処理・計測対象・描画APIの切り分けは未完了。平均値だけで遅延が解消したと判定しない。

## 誤選択記録の訂正

最初の追加ライブ測定はモード切替ボタンを逆に読み取り、5人版だった。実映像の引きの絵で5人と分かり、39人評価からすべて除外した。ファイルはthankyou5-*へ改名して保全し、five-versus-39-correction.jsonに変更履歴を記録。以前のcommentaryの39人という説明は訂正済み。上表は訂正後のactual39-*だけを使用。起動・更新修正の検証はこの誤選択と独立して有効。

## 保全・復元・続行

検証開始時のアプリ0.84、全設定、helper、ライブラリ、Android RTScale設定を保全。ゲームデータの削除・初期化、APKやゲームプログラムの変更は行っていない。Mesaライブラリは開始時の6a77eba981aa1163edf3351f15be38752a9a0da7ecd2a04ee273f388cb8b7116を使用し、新しい描画バイナリは導入していない。

現枠の区切りで開始時のRTScale x5・FSR150・MSAA明示指定なしへ復元済み。全17設定のバイト一致、追加設定なし、Android RTScale設定のバイト一致、MesaライブラリSHA256一致を確認した。高速Refreshの検証済み2スクリプト修正は実機に保持している。設定復元とアプリ修正保持は区別して記録する。

追加枠で、序盤の約0.5秒の遅延を拡大なし等の対照・CPU/GPU/API証拠で切り分ける。連続再生・繰り返し起動によるメモリ増加と安定性も未完了。以前の独立GLES試験で見つけた深度のみBlit/CopyImageの問題は、Diamond Jokerの原因には含めていない。今回の39人版で使われているかも未確認であり、未検証の追加修正を現機の標準へ混ぜない。HUDの最大約2FPS差の原因も未確定で、現在は優先度を下げている。

このチャットへ追加枠の1回のみの再開フォローアップを登録済み（04:59）。使用量リセットクレジットは使用していない。次枠でも上限前にレポートと検証済み候補ZIPをDriveルート・Gitへ保存する。
