#!/usr/bin/env python3
"""End-to-end checks against the actual archive, without modifying the desktop."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import hashlib
import importlib.util
import json
import os
import sys
import tarfile
import tempfile

HERE=Path(__file__).resolve().parent
archive=HERE.parent/'dist/CatPaw-0.5.1-Linux.tar.gz'
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
    with patch.dict(os.environ,{'XDG_DATA_HOME':str(home/'.local/share'),'XDG_STATE_HOME':str(home/'.local/state'),'XDG_CONFIG_HOME':str(home/'.config')}), patch.object(installer,'settings',side_effect=AssertionError('Desktop access forbidden in package test')):
        installer.perform(args,home)
        for name in installer.NAMES:
            installed=home/'.local/share/icons'/name
            source=unpacked/'themes'/name
            assert (home/'.icons'/name).resolve()==installed.resolve()
            for f in (source/'cursors').iterdir():
                target=installed/'cursors'/f.name
                assert target.read_bytes()==f.read_bytes()
                if f.is_symlink():assert target.is_symlink() and target.resolve().parent==installed/'cursors'
        sys.path.insert(0,str(unpacked/'companion'))
        from manage import Manager
        manager=Manager(home)
        manager.install({'pawColor':'coffee'})
        assert (manager.runtime/'app.py').read_bytes()==(unpacked/'companion/app.py').read_bytes()
        assert not manager.desktop.exists() and manager.pid() is None
        manager.autostart(True)
        assert str(manager.runtime/'app.py') in manager.desktop.read_text()
        manager.configure({'followAnimation':False})
        assert json.loads(manager.config.read_text())['followAnimation'] is False
        manager.uninstall()
        assert not manager.runtime.exists() and not manager.desktop.exists()
        args.action='uninstall';installer.perform(args,home)
        assert not list((home/'.local/share/icons').glob('CatPaw-*'))
        assert len(list((home/'.local/state/CatPaw-Linux/removed').glob('*/CatPaw-*')))==8
report={'result':'PASS','checks':['SHA-256','safe archive extraction','eight real themes installed into temporary home','all native files and aliases preserved','packaged Companion install/configure/autostart/uninstall','no gsettings access','all eight themes archived on uninstall'],'desktopModified':False}
(HERE/'package-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
