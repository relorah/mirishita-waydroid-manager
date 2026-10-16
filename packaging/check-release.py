#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Offline checks for the tracked release tree; does not install or publish."""
import argparse,ast,hashlib,json,os,subprocess,tarfile
from pathlib import Path,PurePosixPath

def check(root):
 files=subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0')[:-1]
 forbidden={'.git','__pycache__','.aws','.codex','.agents','updates','investigations'}
 for name in files:
  path=PurePosixPath(name)
  if forbidden.intersection(path.parts) or path.suffix.lower() in {'.apk','.obb','.aab'}:raise ValueError('Unwanted distribution file: '+name)
  if (root/name).is_symlink():raise ValueError('Review source symlink before release: '+name)
 python=0;shell=0
 for name in files:
  p=root/name
  if p.suffix=='.py':ast.parse(p.read_text(encoding='utf8'),filename=name);python+=1
  if p.suffix=='.sh':subprocess.run(['bash','-n',str(p)],check=True);shell+=1
 for name in ('install.sh','uninstall.sh','mwm/scripts/mangoapp-native/mangoapp','mwm/scripts/mangoapp-native/bc250-gpu-probe'):
  if not os.access(root/name,os.X_OK):raise ValueError('Missing executable permission: '+name)
 for line in (root/'packaging/payload/SHA256SUMS').read_text(encoding='utf8').splitlines():
  value,name=line.split(maxsplit=1)
  with (root/'packaging/payload'/name.lstrip('*')).open('rb') as stream:
   if hashlib.file_digest(stream,'sha256').hexdigest()!=value:raise ValueError('Payload checksum mismatch: '+name)
 expected={row.split()[1]:row.split()[0] for row in (root/'packaging/payload/manifests/overlay-SHA256SUMS').read_text().splitlines() if row.strip()}
 observed={}
 for archive in sorted((root/'packaging/payload/graphics').glob('*.tar.zst')):
  proc=None;source=None
  try:import zstandard
  except ImportError:
   proc=subprocess.Popen(['zstd','-dc',str(archive)],stdout=subprocess.PIPE);stream=proc.stdout
  else:
   source=archive.open('rb');stream=zstandard.ZstdDecompressor().stream_reader(source)
  try:
   with tarfile.open(fileobj=stream,mode='r|') as tar:
    for member in tar:
     path=PurePosixPath(member.name)
     if path.is_absolute() or '..' in path.parts or path.parts[0]!='vendor':raise ValueError('Unsafe overlay member')
     if member.isfile():observed[member.name]=hashlib.file_digest(tar.extractfile(member),'sha256').hexdigest()
  finally:
   stream.close()
   if source:source.close()
   if proc and proc.wait()!=0:raise ValueError('Archive decompression failed')
 for name,value in expected.items():
  if observed.get(name)!=value:raise ValueError('Overlay checksum mismatch: '+name)
 return dict(tracked_files=len(files),python_syntax=python,bash_syntax=shell,payload_files=len(expected),status='passed')

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path);args=parser.parse_args()
 result=json.dumps(check(Path(__file__).resolve().parents[1]),indent=2)+'\n'
 if args.output:args.output.write_text(result)
 print(result,end='')
