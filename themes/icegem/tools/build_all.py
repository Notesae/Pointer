"""Rebuild all IceGem variants and validate the generated CUR/ANI files."""
from pathlib import Path
import subprocess
import sys
import hashlib
import json
import re
import argparse

ROOT = Path(__file__).resolve().parents[1]
# 文本专项构建跳过未改动的角色 ANI，仍逐色执行完整二进制验证并刷新哈希。
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--text-only',action='store_true',help='只重建文本状态动画')
args=parser.parse_args()
for name in ("IceBlue", "Violet", "RosePink", "Mint", "Amber"):
    folder = ROOT / "variants" / name
    print(f"Building {name}", flush=True)
    for script in ("build.py", "validate.py"):
        command=[sys.executable,str(folder / "tools" / script)]
        if script=='build.py' and args.text_only:command.append('--text-only')
        subprocess.run(command,check=True)
    # 从本次生成物计算校验值，避免新造型仍被安装器中的旧版固定哈希拒绝。
    hashes={path.relative_to(folder).as_posix():hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted((folder/'cursors').rglob('*')) if path.is_file()}
    (folder/'docs/sha256.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
    expected="$linkExpected=@{\n"+'\n'.join(
        "            '"+size+"'='"+hashes[f'cursors/{size}/icegem-link.cur'].upper()+"'"
        for size in ('32','48','64','multi'))+"\n        }"
    known="$known=@("+','.join(
        "'"+hashes[f'cursors/{size}/icegem-link.{ext}'].upper()+"'"
        for size in ('32','48','64','multi') for ext in ('cur','ani'))+")"
    # 限定只替换一个已知哈希区块，模板变化时停止构建，防止悄悄漏更新。
    for filename,pattern,replacement in (
            ('Install-IceGem.ps1',r'\$linkExpected=@\{.*?\}',expected),
            ('Check-Link.ps1',r'\$known=@\(.*?\)',known)):
        path=folder/filename
        updated,count=re.subn(pattern,lambda match:replacement,path.read_text(encoding='utf-8'),flags=re.S)
        if count!=1:raise RuntimeError(f'{filename}: expected exactly one hash block')
        path.write_text(updated,encoding='utf-8')
