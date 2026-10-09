#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Root-owned backup of MWM modification targets. Fixed system target, no arbitrary restore path."""
import configparser,fcntl,hashlib,json,os,pwd,shutil,subprocess,sys,time
from pathlib import Path
import mwm_targeted_backup as targeted
WD=Path('/var/lib/waydroid')
BASE=Path('/var/lib/mwm-backups')
def run(args,**kw):return subprocess.run(args,check=True,**kw)
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
 return h.hexdigest()
def member_path(p):
 return Path(*p.parts[1:])

def safe_user_path(p,home,name):
 p=Path(p)
 if not p.is_absolute() or p.name!=name or p.is_symlink() or p.resolve()!=p.absolute() or not p.resolve().is_relative_to(home) or p.resolve()==home:
  raise RuntimeError('Unsupported user path: '+str(p))
 return p
def identity(user):
 if WD.is_symlink() or WD.resolve()!=WD or not WD.is_dir() or (WD/'waydroid.cfg').is_symlink():raise RuntimeError('Waydroid directory is missing or redirected')
 cfg=configparser.ConfigParser();cfg.read(WD/'waydroid.cfg')
 images=Path(cfg.get('waydroid','images_path',fallback=str(WD/'images')))
 if not images.is_absolute() or images.is_symlink() or images.resolve()!=images:raise RuntimeError('Image path is redirected')
 hashes={}
 for name in ('system.img','vendor.img'):
  p=images/name
  if p.is_symlink() or not p.is_file():raise RuntimeError('Image missing or redirected: '+str(p))
  hashes[str(p)]=digest(p)
 st=WD.stat()
 return {'directory':[st.st_dev,st.st_ino],'images':hashes,'userdata':str(user),'config_images_path':str(images)}
def offline(user):
 # Stop first; mounted images/bind mounts must not enter the backup.
 targeted.stop_backup_session()
 run(['systemctl','stop','waydroid-container.service'])
 paths=run(['findmnt','-rn','-o','TARGET'],capture_output=True,text=True).stdout.splitlines()
 for p in paths:
  p=Path(p)
  if p==WD or p.is_relative_to(WD) or p==user or p.is_relative_to(user):
   raise RuntimeError('Mounted/shared Waydroid path; backup/restore aborted: '+str(p))
def load(folder,verify=True):
 return targeted.load(folder,verify,sys.modules[__name__])

def restore(folder,home):
 return targeted.restore(folder,home,sys.modules[__name__])

def main():
 if os.geteuid()!=0:raise RuntimeError('root required')
 uid=os.environ.get('SUDO_UID','')
 if not uid.isdigit() or int(uid)==0:raise RuntimeError('Invoke through sudo as the installing user')
 home=Path(pwd.getpwuid(int(uid)).pw_dir).resolve()
 BASE.mkdir(mode=0o700,exist_ok=True)
 if BASE.is_symlink() or BASE.stat().st_uid!=0:raise RuntimeError('Unsafe backup root')
 os.chmod(BASE,0o700)
 action=sys.argv[1];slot=BASE/uid
 if slot.is_symlink():raise RuntimeError('Unsafe backup owner directory')
 slot.mkdir(mode=0o700,exist_ok=True)
 if slot.stat().st_uid!=0:raise RuntimeError('Backup directory is not root owned')
 os.chmod(slot,0o700);folder=slot/'baseline'
 if folder.is_symlink():raise RuntimeError('Unsafe baseline directory')
 with (BASE/'operation.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  if (slot/'restore-transaction.json').exists():raise RuntimeError('Interrupted restore; inspect recovery before proceeding')
  if action=='create':
   user=safe_user_path(sys.argv[2],home,'waydroid');app=safe_user_path(sys.argv[3],home,'mwm')
   if folder.exists():
    meta=load(folder)
    if identity(user)!=meta['identity']:raise RuntimeError('Existing backup belongs to a different environment')
    print('Original backup retained: '+str(folder));return
   origin='existing-MWM' if (app/'VERSION').exists() or (WD/'overlay/vendor/lib64/egl/libEGL_mwm_iso.so').exists() else 'before-first-MWM'
   temporary=slot/'baseline.incomplete'
   if temporary.exists():raise RuntimeError('Incomplete backup exists; inspect before retry')
   targeted.create(temporary,user,origin,sys.modules[__name__]);temporary.rename(folder)
   print('MWM modification backup saved: '+str(folder)+' / '+origin)
  elif action=='cleanup-setup':
   setup=safe_user_path(sys.argv[2],home,'mwm-setup')
   if setup.exists():
    # Preserve any old ISO recovery files in the backup area before cleanup.
    archive=slot/('legacy-setup-'+time.strftime('%Y%m%d-%H%M%S')+'.tar.zst')
    run(['tar','--zstd','--acls','--xattrs','--numeric-owner','-cpf',str(archive),'-C',str(setup.parent),'--',setup.name])
    os.chmod(archive,0o600);shutil.rmtree(setup)
  elif action=='status':
   if not folder.exists():print('MWM_BACKUP_NONE');sys.exit(3)
   meta=load(folder,verify=False);print(json.dumps(meta,ensure_ascii=False))
  elif action=='restore':restore(folder,home)
  else:raise RuntimeError('Invalid action')
if __name__=='__main__':
 try:main()
 except Exception as e:print('MWM backup: '+str(e),file=sys.stderr);sys.exit(1)
