"""从已构建的五色资源生成 4.4 包；Linux 直接写 tar 链接，支持 Windows 构建机。"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import io
import json
import tarfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]
VERSION='4.4'
COLORS=('IceBlue','Violet','RosePink','Mint','Amber')


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def package(windows_only=False):
    """打包当前构建资源与安装器，保持历史发行包不变并生成新校验清单。"""
    dist=ROOT/'dist'
    dist.mkdir(exist_ok=True)
    windows=dist/f'IceGem-{VERSION}-Color-Collection.zip'
    staged=windows.with_suffix('.tmp.zip')
    with zipfile.ZipFile(staged,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for color in COLORS:
            folder=ROOT/'variants'/color
            for path in sorted(folder.rglob('*')):
                if not path.is_file() or '__pycache__' in path.parts or 'animation' in path.parts:
                    continue
                archive.write(path,'IceGem-Colors/'+color+'/'+path.relative_to(folder).as_posix())
            launcher=f'@echo off\r\npushd "%~dp0{color}"\r\ncall Install.cmd %*\r\npopd\r\n'
            archive.writestr(f'IceGem-Colors/Install-{color}.cmd',launcher)
        for path in sorted((ROOT/'companion').iterdir()):
            if path.is_file() and not path.name.startswith('.'):
                archive.write(path,'IceGem-Colors/companion/'+path.name)
        archive.writestr('IceGem-Colors/Start-Companion.cmd','@echo off\r\ncall "%~dp0companion\\Start.cmd"\r\n')
        # 分色页面直接预览对应安装资源，减少重复内嵌帧与不一致的动画时间表。
        links=''.join(f'<li><a href="{color}/preview/IceGem-Preview.html">{color}</a></li>' for color in COLORS)
        archive.writestr('IceGem-Colors/IceGem-Colors-Preview.html',f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>IceGem {VERSION}</title><h1>IceGem {VERSION} · 晶体旋律</h1><p>选择颜色查看不同幅度的原生晶体旋转和三晶体等待动画。</p><ul>'+links+'</ul></html>')
        archive.writestr('IceGem-Colors/README.txt',f'IceGem {VERSION}\nInstall: Install-<Color>.cmd\nOptional interaction: Start-Companion.cmd\nCompanion does not change the cursor theme or start automatically at login.\n')
    with zipfile.ZipFile(staged) as archive:
        assert archive.testzip() is None
        assert 'IceGem-Colors/companion/IceGem-Companion.exe' in archive.namelist()
    staged.replace(windows)
    print(f'Windows {VERSION} packaged',flush=True)
    if windows_only:
        return

    linux=load_module('icegem_linux',ROOT/'linux/build.py')
    metadata={'version':f'{VERSION}-linux.1','sizes':linux.SIZES,'themes':[],'aliases':linux.ALIASES,'animation':{}}
    # payload 只存常规文件；别名独立保存为 tar 符号链接，不需要宿主的 symlink 权限。
    payload={name:(ROOT/'linux'/name).read_bytes() for name in ('Install.sh','install.py','README.md','build.py','requirements-build.txt','validate.py')}
    aliases={}
    for color in COLORS:
        path=ROOT/'variants'/color/'tools/build.py'
        renderer=load_module(color,path)
        payload[f'source/variants/{color}/tools/build.py']=path.read_bytes()
        for name,names in linux.ALIASES.items():
            rates=renderer.ANIMATIONS.get(name,(0,))
            count=len(rates)
            metadata['animation'][name]={'frames':count,'periodMs':round(sum(rates)*1000/60)}
            images=[(n,linux.hotspot(renderer,name,n),round(sum(rates[:f+1])*1000/60)-round(sum(rates[:f])*1000/60),renderer.render(renderer.geometry(name,f),n)) for n in linux.SIZES for f in range(count)]
            for mode in ('Animated','Static'):
                theme=f'IceGem-{color}-{mode}'
                prefix=f'themes/{theme}'
                selected=images if mode=='Animated' else [(n,h,0,im) for n,h,_,im in images[::count]]
                payload[f'{prefix}/cursors/{names[0]}']=linux.encode(selected)
                for alias in names[1:]:
                    aliases[f'{prefix}/cursors/{alias}']=names[0]
                if name=='normal':
                    metadata['themes'].append(theme)
                    payload[prefix+'/index.theme']=f'[Icon Theme]\nName=IceGem {color} {mode}\nComment=Crystal motion\nInherits=Adwaita\n'.encode()
                    payload[prefix+'/.icegem-linux']=b'IceGem-Linux-v1\n'
        print(color+' Xcursor encoded',flush=True)
    payload['manifest.json']=(json.dumps(metadata,indent=2)+'\n').encode()
    (ROOT/'linux/manifest.json').write_bytes(payload['manifest.json'])
    payload['SHA256SUMS']=(''.join(hashlib.sha256(data).hexdigest()+'  '+name+'\n' for name,data in sorted(payload.items()))).encode()
    target=dist/f'IceGem-{VERSION}-Linux.tar.gz'
    staged=target.with_suffix('.tmp.gz')
    with tarfile.open(staged,'w:gz') as archive:
        for name,data in sorted(payload.items()):
            entry=tarfile.TarInfo('IceGem-Linux/'+name)
            entry.size=len(data);entry.mode=0o755 if name=='Install.sh' else 0o644
            archive.addfile(entry,io.BytesIO(data))
        for name,destination in sorted(aliases.items()):
            entry=tarfile.TarInfo('IceGem-Linux/'+name)
            entry.type=tarfile.SYMTYPE;entry.linkname=destination;entry.mode=0o777
            archive.addfile(entry)
    staged.replace(target)
    target.with_name(target.name+'.sha256').write_text(hashlib.sha256(target.read_bytes()).hexdigest()+'  '+target.name+'\n',encoding='utf-8')
    print(f'Linux {VERSION} packaged with SHA256',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--windows-only',action='store_true',help='Only repack Windows resources and companion')
    args=parser.parse_args()
    package(args.windows_only)
