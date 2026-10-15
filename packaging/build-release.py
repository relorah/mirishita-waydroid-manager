#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build a traceable candidate from committed source; never publish a release."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import runpy
import subprocess
import time
import zipfile

GRAPHICS_BASE_SHA256='6ddc1e4dbf0c5663d2ed70df3c6eed406211cffad6c0f406f53c2e87b236d9dd'

def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def build(repo,out,graphics,label):
    if label!='release' and not re.fullmatch(r'rc[1-9][0-9]*',label):raise ValueError('Use rcN or release')
    subprocess.run(['git','diff','--exit-code','HEAD'],cwd=repo,check=True,stdout=subprocess.DEVNULL)
    untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=repo,text=True)
    if untracked.strip():raise ValueError('Commit new source files before packaging')
    if digest(graphics)!=GRAPHICS_BASE_SHA256:raise ValueError('Unexpected graphics base source archive')
    subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=repo/'payload',check=True,stdout=subprocess.DEVNULL)
    version=runpy.run_path(str(repo/'mwm/version.py'))['__version__']
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    timestamp=int(subprocess.check_output(['git','show','-s','--format=%ct','HEAD'],cwd=repo,text=True))
    prefix=f'MLTD_Waydroid_Manager_v{version}'+('' if label=='release' else '-'+label)
    out.mkdir(parents=True,exist_ok=True)
    target=out/(prefix+'.zip')
    if target.exists():raise ValueError('Candidate already exists; use a new label or output directory')
    subprocess.run(['git','archive','--format=zip',f'--prefix={prefix}/',f'--output={target}','HEAD'],cwd=repo,check=True)
    manifest={'version':version,'candidate':label,'source_commit':commit,'status':'packaged-not-published','graphics_base_sha256':GRAPHICS_BASE_SHA256,'graphics_base_requires_patches':['docs/graphics/msaa/mesa-msaa-storage2.patch','docs/graphics/depth-blit/mesa-depth-only-blit.patch'],'payload_sha256_file':'payload/SHA256SUMS'}
    with zipfile.ZipFile(target,'a',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for name,data in [('payload/sources/graphics-sources.tar.zst',graphics.read_bytes()),('RELEASE_MANIFEST.json',(json.dumps(manifest,indent=2)+'\n').encode())]:
            info=zipfile.ZipInfo(prefix+'/'+name,time.gmtime(max(timestamp,315532800))[:6]);info.create_system=3;info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_STORED if name.endswith('.zst') else zipfile.ZIP_DEFLATED
            archive.writestr(info,data)
        for entry in archive.infolist():
            p=PurePosixPath(entry.filename)
            if p.is_absolute() or '..' in p.parts:raise ValueError('Unsafe ZIP path')
            if any(x in p.parts for x in ('.git','__pycache__','updates')):raise ValueError('Unexpected development file in release')
        mode=archive.getinfo(prefix+'/install.sh').external_attr>>16
        if not mode&0o111:raise ValueError('Installer executable mode was lost')
        if archive.testzip():raise ValueError('ZIP integrity failure')
    (out/(target.name+'.sha256')).write_text(digest(target)+'  '+target.name+'\n')
    print(json.dumps(dict(file=str(target),sha256=digest(target),source_commit=commit)))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--graphics-sources',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--label',default='rc1')
    args=parser.parse_args()
    build(Path(__file__).resolve().parents[1],args.output.resolve(),args.graphics_sources.resolve(),args.label)
