#!/usr/bin/env python3
"""End-to-end checks against the actual archive, without modifying the desktop."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import hashlib
import importlib.util
import json
import os
import tarfile
import tempfile

HERE=Path(__file__).resolve().parent
archive=HERE.parent/'dist/CatPaw-0.4.0-Linux.tar.gz'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==archive.with_suffix('.gz.sha256').read_text().split()[0]
with tempfile.TemporaryDirectory(prefix='catpaw-package-') as tmp:
    root=Path(tmp)
    with tarfile.open(archive) as package:
        names=[m.name for m in package.getmembers()]
        assert all(n.startswith('CatPaw-Linux/') for n in names)
        package.extractall(root,filter='data')
    unpacked=root/'CatPaw-Linux'
    spec=importlib.util.spec_from_file_location('package_installer',unpacked/'install.py')
    installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
    home=root/'user';home.mkdir()
    args=SimpleNamespace(action='install',no_apply=True,color='Pink',mode='animated',size=32,all=True)
    with patch.dict(os.environ,{'XDG_DATA_HOME':str(home/'.local/share'),'XDG_STATE_HOME':str(home/'.local/state')}), patch.object(installer,'settings',side_effect=AssertionError('Desktop access forbidden in package test')):
        installer.perform(args,home)
        for name in installer.NAMES:
            installed=home/'.local/share/icons'/name
            source=unpacked/'themes'/name
            assert (home/'.icons'/name).resolve()==installed.resolve()
            for f in (source/'cursors').iterdir():
                target=installed/'cursors'/f.name
                assert target.read_bytes()==f.read_bytes()
                if f.is_symlink():assert target.is_symlink() and target.resolve().parent==installed/'cursors'
        args.action='uninstall';installer.perform(args,home)
        assert not list((home/'.local/share/icons').glob('CatPaw-*'))
        assert len(list((home/'.local/state/CatPaw-Linux/removed').glob('*/CatPaw-*')))==4
report={'result':'PASS','checks':['SHA-256','safe archive extraction','four real themes installed into temporary home','all native files and aliases preserved','no gsettings access','all four themes archived on uninstall'],'desktopModified':False}
(HERE/'package-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
