"""Locale-aware user messages; keep technical diagnostic output unchanged."""
TRANSLATIONS = {
 'Could not stop Mirishita. Settings have not been applied.':'ミリシタを終了できなかったため、設定の反映を中止しました。',
 'Could not verify Mirishita stopped. Settings have not been applied.':'ミリシタの終了を確認できなかったため、設定の反映を中止しました。',
 'Mirishita is still running. Settings have not been applied.':'ミリシタが終了しなかったため、設定の反映を中止しました。',
 'Stopping Mirishita...':'ミリシタを終了しています…',
 'Close Mirishita before Waydroid Refresh to change the RTScale multiplier.':'RTScaleの倍率を変更するには、ミリシタを終了してからStart／Restartを押してください。',
 'Uninstall MWM':'MWMのアンインストール', 'Waydroid Refresh':'Waydroidの再起動',
 'Backend mismatch':'描画環境の確認エラー', 'Detect Running Game':'起動中ゲームの検出',
 'Diagnostic Log':'診断ログ', 'RTScale Debug':'RTScaleの診断',
 'Could not detect the foreground Android app.':'前面のAndroidアプリを取得できませんでした。',
 'Could not clear log':'ログを消去できませんでした。',
 'Could not create the startup state folder.':'起動状態の保存先を作成できませんでした。',
 'Recovered an interrupted settings save. Please review your settings.':'中断された設定保存を復旧しました。設定内容を確認してください。',
 'Waydroid Refresh failed':'Waydroidの再起動に失敗しました。',
 'Could not verify the selected backend':'選択した描画環境を確認できませんでした',
 'against the restart result':'再起動結果',
 'The selected custom width is invalid.':'指定した横幅が不正です。',
 'Another MWM instance may already be running.':'別のMWMが起動している可能性があります。',
 'Could not acquire the startup lock.':'起動用ロックを取得できませんでした。',

 'Another operation is in progress.':'別の処理を実行中です。',
 'Save your settings with Apply first.':'先にApplyを押して設定を保存してください。',
 'Wait for the current operation to finish.':'現在の処理が完了してから実行してください。',
 'Discard unsaved changes and close?':'未保存の変更を破棄して閉じますか？',
 'Unsaved Changes':'未保存の変更',
 'Waydroid Ready':'Waydroidの準備が完了しました',
 'No Backup Found':'バックアップがありません',
 'No backup was found. Remove MWM only?':'バックアップがありません。MWMのみ削除しますか？',
 'Current Waydroid settings, graphics files, and game data will be retained.':'Waydroidの現在の設定・描画ファイル・ゲームデータは保持します。',
 'MWM settings, logs, launchers, and permission rules will be removed.':'MWMの設定・ログ・ランチャー・権限設定を削除します。',
 'Restore the files and settings modified by MWM, then remove MWM.':'MWMが変更したファイルと設定を復元して、MWMを削除します。',
 'Only MWM modification targets will be restored. Current game data will be retained.':'MWMの変更対象だけを復元します。ゲームデータは現在の状態を保持します。',
 'Backup date: ':'バックアップ日時：',
 'Saved settings have been applied and the display and session have been verified.':'保存した設定を反映し、表示と起動状態を確認しました。',
 'Click OK, then launch Mirishita from the Android home screen.':'OKを押してから、Androidホームでミリシタを起動してください。',
 'Settings are applied and Mirishita has started.':'設定を反映し、ミリシタを起動しました。',
 'Could not save settings: ':'設定の保存に失敗しました：',
 'Could not verify saved settings: ':'保存済み設定を確認できません：',
 'Settings were saved, but the FPS counter could not be updated. Check the log.':'設定は保存しましたが、FPSの反映に失敗しました。ログを確認してください。',
 'Waydroid Refresh Interrupted':'Waydroidの設定反映を中断しました',
 'Waydroid Refresh was interrupted because Mirishita launched while settings were being applied.':'設定反映中にミリシタの起動を検出したため、処理を中断しました。',
 'Some settings may have been applied.':'設定が一部だけ反映されている可能性があります。',
 'Close Mirishita and run Waydroid Refresh again.':'ミリシタを終了し、Start／Restartを押してやり直してください。',
 'Could not open a terminal.':'ターミナルを起動できませんでした。',
 'Could not verify the backup. Check its permissions and status.':'バックアップを確認できません。権限と状態を確認してください。',
 'Could not read the backup metadata.':'バックアップの記録を確認できません。',
 'Uninstaller files are missing. Update MWM from the distribution ZIP.':'アンインストール用ファイルがありません。配布ZIPから更新してください。',
 'Open a terminal and run ./uninstall.sh from the extracted distribution folder.':'ターミナルを開き、配布ZIPの展開先で ./uninstall.sh を実行してください。',
 'Diagnostic Log Saved':'診断ログを保存しました',
 'Send this single file when reporting a problem.':'不具合報告時はこの1ファイルを送付してください。',
 'Could not collect diagnostic logs.':'診断ログの取得に失敗しました。',
 'This app is already registered.':'このアプリは登録済みです。',
 'MWM is already running. Use the existing MWM window.':'MWMは起動済みです。開いている画面をご利用ください。',
 'Could not verify the settings state. Start MWM after the current operation finishes or the issue is resolved.':'設定状態を確認できません。処理の完了または問題の解消後に起動してください。',
}
def translate(text,japanese):
 if not japanese or not isinstance(text,str):return text
 for original,replacement in sorted(TRANSLATIONS.items(),key=lambda pair:len(pair[0]),reverse=True):text=text.replace(original,replacement)
 return text

class LocalizedMessageBox:
 def __init__(self,native,japanese):self.native=native;self.japanese=japanese
 def __getattr__(self,name):
  target=getattr(self.native,name)
  if name not in ('information','warning','question','critical'):return target
  def show(parent,title,message,*args,**kwargs):
   localized=translate(message,self.japanese)
   if self.japanese and localized==message and name in ('warning','critical') and not any('\u3040' <= c <= '\u9fff' for c in message):
    localized='処理を完了できませんでした。以下の詳細を確認してください。\n\n'+message
   if not self.japanese:
    return target(parent,title,message,*args,**kwargs)
   box=self.native(parent)
   box.setWindowTitle({'Apply':'設定の保存','FPS Counter':'FPSカウンター','Waydroid':'Waydroid','MWM':'MWM'}.get(title,translate(title,True)))
   box.setText(localized)
   icons={'information':self.native.Icon.Information,'warning':self.native.Icon.Warning,'question':self.native.Icon.Question,'critical':self.native.Icon.Critical}
   box.setIcon(icons[name])
   buttons=args[0] if args else kwargs.get('buttons', self.native.StandardButton.Yes | self.native.StandardButton.No if name=='question' else self.native.StandardButton.Ok)
   box.setStandardButtons(buttons)
   default=args[1] if len(args)>1 else kwargs.get('defaultButton',self.native.StandardButton.NoButton)
   if default!=self.native.StandardButton.NoButton:box.setDefaultButton(default)
   for key,label in [('Ok','OK'),('Yes','はい'),('No','いいえ'),('Cancel','キャンセル'),('Close','閉じる')]:
    button=box.button(getattr(self.native.StandardButton,key))
    if button is not None:button.setText(label)
   return self.native.StandardButton(box.exec())
  return show
