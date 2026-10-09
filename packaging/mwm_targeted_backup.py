#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Save only MWM overlay targets and individual Android settings."""
import base64, json, os, re, shutil, subprocess, tarfile, time
from pathlib import Path

FILES = '''vendor/etc/libdrm/amdgpu.ids
vendor/lib64/dri_gbm.so
vendor/lib64/egl/libEGL_mesa.so
vendor/lib64/egl/libEGL_mwm_iso.so
vendor/lib64/egl/libGLESv1_CM_mesa.so
vendor/lib64/egl/libGLESv2_mesa.so
vendor/lib64/egl/libGLES_mesa.so
vendor/lib64/hw/gralloc.gbm.so
vendor/lib64/libLLVM.so
vendor/lib64/libLLVM21.so
vendor/lib64/libdrm.so
vendor/lib64/libdrm_amdgpu.so
vendor/lib64/libdrm_intel.so
vendor/lib64/libdrm_radeon.so
vendor/lib64/libgallium_dri.so
vendor/lib64/libgbm_mesa.so'''.splitlines()
PROPS = ['persist.waydroid.' + k for k in ('width','height','multi_windows','uevent','fake_touch','width_padding','height_padding')]
CONF='/data/local/tmp/gles_rtscale.conf'

def wd(*args,input=None,timeout=25):
 return subprocess.run(['waydroid','shell','--',*args],input=input,capture_output=True,text=True,check=True,timeout=timeout).stdout.replace('\r','').strip()

def session_command(action, background=False):
 import pwd, stat, tempfile
 uid_text=os.environ.get('SUDO_UID','')
 if not uid_text.isdigit() or int(uid_text)==0:
  raise RuntimeError('Backup session requires the installing user identity')
 uid=int(uid_text);account=pwd.getpwuid(uid)
 runtime=Path('/run/user')/uid_text
 if runtime.is_symlink() or not runtime.is_dir() or runtime.stat().st_uid!=uid:
  raise RuntimeError('Installing user has no active desktop runtime')
 sockets=[]
 for candidate in runtime.glob('wayland-*'):
  try:
   st=candidate.lstat()
   if stat.S_ISSOCK(st.st_mode) and st.st_uid==uid:sockets.append(candidate.name)
  except OSError:pass
 requested=os.environ.get('WAYLAND_DISPLAY','')
 if requested in sockets:display=requested
 elif len(sockets)==1:display=sockets[0]
 else:raise RuntimeError('Could not uniquely identify the desktop Wayland socket for backup')
 env={'PATH':'/usr/local/bin:/usr/bin:/bin','HOME':account.pw_dir,
      'USER':account.pw_name,'LOGNAME':account.pw_name,
      'XDG_RUNTIME_DIR':str(runtime),'WAYLAND_DISPLAY':display,
      'DBUS_SESSION_BUS_ADDRESS':'unix:path='+str(runtime/'bus')}
 command=['/usr/bin/waydroid','session',action]
 options=dict(env=env,cwd=account.pw_dir,user=uid,group=account.pw_gid,
              extra_groups=os.getgrouplist(account.pw_name,account.pw_gid),
              stdin=subprocess.DEVNULL,start_new_session=True,close_fds=True)
 if background:
  log=tempfile.TemporaryFile(mode='w+b')
  try:process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,**options)
  except Exception:log.close();raise
  return process,log
 return subprocess.run(command,capture_output=True,text=True,timeout=30,check=True,**options)

def stop_backup_session():
 session_command('stop')

def ready():
 subprocess.run(['systemctl','start','waydroid-container.service'],check=True,timeout=30)
 try:
  if wd('getprop','sys.boot_completed',timeout=5)=='1':return
 except (subprocess.SubprocessError,OSError):pass
 process,log=session_command('start',background=True)
 last_error=''
 deadline=time.monotonic()+120
 try:
  while time.monotonic()<deadline:
   try:
    if wd('getprop','sys.boot_completed',timeout=5)=='1':return
   except (subprocess.SubprocessError,OSError) as error:last_error=str(error)
   if process.poll() not in (None,0):break
   time.sleep(1)
  log.seek(0);details=log.read().decode('utf-8',errors='replace')[-2500:]
  raise RuntimeError('Android settings unavailable after user session start; backup/restore aborted\n'+details+'\n'+last_error)
 finally:
  # The session must remain available until capture/apply finishes. offline()
  # explicitly stops it as the same user before stopping the container.
  if process.poll() not in (None,0):process.wait()
  log.close()


def capture_android():
 ready()
 present=wd('sh','-c',f'if [ -e {CONF} ]; then echo yes; else echo no; fi')
 if present not in ('yes','no'):raise RuntimeError('Cannot identify RTScale configuration')
 conf=None
 if present=='yes':
  conf={'data':wd('base64',CONF),'attributes':wd('stat','-c','%a:%u:%g',CONF)}
 size=wd('wm','size');override=re.search(r'^Override size:\s*(\d+x\d+)\s*$',size,re.M)
 if not re.search(r'^Physical size:\s*\d+x\d+',size,re.M):raise RuntimeError('Cannot read Android display override')
 return {'props':{k:wd('getprop',k) for k in PROPS},'wm_size':override.group(1) if override else None,'volume_music':wd('settings','get','system','volume_music'),'conf':conf}

def apply_android(state):
 ready()
 if set(state['props'])!=set(PROPS):raise RuntimeError('Invalid property backup')
 for key in PROPS:
  wd('setprop',key,state['props'][key])
  if wd('getprop',key)!=state['props'][key]:raise RuntimeError('Property restore verification failed: '+key)
 value=state['wm_size']
 if value is not None and not re.fullmatch(r'\d+x\d+',value):raise RuntimeError('Invalid saved display size')
 wd('wm','size',value or 'reset')
 volume=state['volume_music']
 if volume=='null':wd('settings','delete','system','volume_music')
 else:
  if not re.fullmatch(r'\d+',volume):raise RuntimeError('Invalid saved volume')
  wd('settings','put','system','volume_music',volume)
 conf=state['conf']
 if conf is None:wd('rm','-f',CONF)
 else:
  if not re.fullmatch(r'[0-7]{3,4}:\d+:\d+',conf['attributes']):raise RuntimeError('Invalid RTScale file attributes')
  base64.b64decode(conf['data'],validate=False)
  mode,uid,gid=conf['attributes'].split(':')
  wd('sh','-c',f'base64 -d > {CONF}.mwm-restore && chmod {mode} {CONF}.mwm-restore && chown {uid}:{gid} {CONF}.mwm-restore && mv -f {CONF}.mwm-restore {CONF} && restorecon {CONF}',input=conf['data']+'\n')
 actual=capture_android()
 if actual!=state:raise RuntimeError('Android restoration verification failed')

def safe_target(wdroot,name):
 if name not in FILES:raise RuntimeError('Unknown backup target')
 target=wdroot/'overlay'/name
 for parent in target.parents:
  if parent==wdroot:break
  if parent.is_symlink():raise RuntimeError('Redirected overlay directory: '+str(parent))
 if target.exists() and not (target.is_file() or target.is_symlink()):raise RuntimeError('Unsupported overlay target')
 return target

def save_files(folder,wdroot):
 present=[]
 with tarfile.open(folder/'files.tar','w',format=tarfile.PAX_FORMAT) as archive:
  for name in FILES:
   p=safe_target(wdroot,name)
   if p.exists() or p.is_symlink():
    info=archive.gettarinfo(p,arcname=name)
    for key in os.listxattr(p,follow_symlinks=False):
     info.pax_headers['MWM.xattr.'+key]=base64.b64encode(os.getxattr(p,key,follow_symlinks=False)).decode('ascii')
    if info.isfile():
     with p.open('rb') as stream:archive.addfile(info,stream)
    else:archive.addfile(info)
    present.append(name)
 os.chmod(folder/'files.tar',0o600)
 return present

def restore_files(folder,wdroot,present):
 if len(set(present))!=len(present) or not set(present)<=set(FILES):raise RuntimeError('Invalid saved file list')
 stage=folder/'file-stage'
 if stage.exists():shutil.rmtree(stage)
 stage.mkdir(mode=0o700)
 try:
  with tarfile.open(folder/'files.tar') as archive:
   members=archive.getmembers()
   if {m.name for m in members}!=set(present) or len(members)!=len(present):raise RuntimeError('Archive target mismatch')
   if any(not (m.isfile() or m.issym()) for m in members):raise RuntimeError('Unsupported archive member')
   # Fixed allowlist; no directory or hardlink members. Symlinks are leaves.
   for member in members:
    archive.extract(member,stage,filter='fully_trusted')
    for key,value in member.pax_headers.items():
     if key.startswith('MWM.xattr.'):
      os.setxattr(stage/member.name,key[len('MWM.xattr.'):],base64.b64decode(value,validate=True),follow_symlinks=False)
  for name in FILES:
   target=safe_target(wdroot,name)
   if name in present:
    target.parent.mkdir(parents=True,exist_ok=True)
    os.replace(stage/name,target)
   elif target.exists() or target.is_symlink():target.unlink()
 finally:shutil.rmtree(stage)

def create(folder,user,origin,api):
 android=capture_android();api.offline(user)
 folder.mkdir(mode=0o700)
 try:
  present=save_files(folder,api.WD)
  meta={'format':2,'uid':os.environ['SUDO_UID'],'created':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'origin':origin,'identity':api.identity(user),'present':present,'android':android,'archive_sha256':api.digest(folder/'files.tar')}
  (folder/'metadata.json').write_text(json.dumps(meta,indent=2));os.chmod(folder/'metadata.json',0o600)
 except Exception:shutil.rmtree(folder);raise

def load(folder,verify,api):
 meta=json.loads((folder/'metadata.json').read_text())
 if meta.get('format')!=2:raise RuntimeError('Legacy full-environment backup; targeted restore requires a format-2 baseline. Preserve the old backup and inspect before proceeding.')
 if meta.get('uid')!=os.environ['SUDO_UID']:raise RuntimeError('Backup owner mismatch')
 if verify and api.digest(folder/'files.tar')!=meta['archive_sha256']:raise RuntimeError('Backup checksum mismatch')
 return meta

def restore(folder,home,api):
 meta=load(folder,True,api);user=api.safe_user_path(meta['identity']['userdata'],home,'waydroid')
 if api.identity(user)!=meta['identity']:raise RuntimeError('Waydroid target environment changed')
 recovery=folder.parent/('before-restore-'+time.strftime('%Y%m%d-%H%M%S'))
 create(recovery,user,'pre-restore targeted recovery',api)
 current=load(recovery,True,api)
 journal=folder.parent/'restore-transaction.json'
 journal.write_text(json.dumps({'backup':str(folder),'recovery':str(recovery),'scope':'MWM targets only'}))
 try:
  apply_android(meta['android']);api.offline(user)
  restore_files(folder,api.WD,meta['present'])
 except Exception:
  try:
   apply_android(current['android']);api.offline(user)
   restore_files(recovery,api.WD,current['present'])
   journal.unlink()
  except Exception:raise RuntimeError('Restore and rollback failed; retain MWM and recovery journal')
  raise
 journal.unlink()
 print('MWM-modified files and settings restored; application data retained.')
