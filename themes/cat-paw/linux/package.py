#!/usr/bin/env python3
"""Create a deterministic, ready-to-install Linux archive (no build dependencies)."""
from pathlib import Path
import gzip
import hashlib
import tarfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
DEST=ROOT/'dist/CatPaw-0.5.1-Linux.tar.gz'

def package():
    required=['Install.sh','install.py','README.md','manifest.json','validation.json','installer-validation.json']
    for name in required:
        if not (HERE/name).is_file(): raise FileNotFoundError(name)
    if len(list((HERE/'themes').glob('CatPaw-*')))!=8: raise RuntimeError('Build all eight themes before packaging')
    DEST.parent.mkdir(parents=True,exist_ok=True)
    entries=[(HERE/name,'CatPaw-Linux/'+name) for name in required]
    entries+=[(ROOT/'preview/Cat Paw Linux Roles.png','CatPaw-Linux/Preview.png')]
    entries+=[(p,'CatPaw-Linux/'+p.relative_to(HERE).as_posix()) for p in sorted((HERE/'themes').rglob('*'))]
    entries += [(p,'CatPaw-Linux/companion/'+p.relative_to(ROOT/'companion').as_posix()) for p in sorted((ROOT/'companion').rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
    with DEST.open('wb') as out, gzip.GzipFile(filename='',mode='wb',fileobj=out,mtime=0) as compressed, tarfile.open(fileobj=compressed,mode='w') as archive:
        for source,name in sorted(entries,key=lambda e:e[1]):
            info=archive.gettarinfo(str(source),arcname=name)
            info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
            info.mode=0o755 if info.isdir() or source.name=='Install.sh' else (0o777 if info.issym() else 0o644)
            if info.isfile():
                with source.open('rb') as handle: archive.addfile(info,handle)
            else:archive.addfile(info)
    digest=hashlib.sha256(DEST.read_bytes()).hexdigest()
    DEST.with_suffix(DEST.suffix+'.sha256').write_text(f'{digest}  {DEST.name}\n')
    print(f'{DEST.name}: {DEST.stat().st_size:,} bytes; SHA256 {digest}')

if __name__=='__main__': package()
