"""Per-user installation and lifecycle; no root and no persistent polling."""
import fcntl
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time
from motion import config

OWNER='CatPaw-Companion-v1'
HERE=Path(__file__).resolve().parent

class Manager:
    def __init__(self,home=None):
        home=Path(home or Path.home()).resolve()
        def base(env,default):
            p=Path(os.environ.get(env,str(home/default)))
            if not p.is_absolute() or not p.resolve().is_relative_to(home) or p.resolve()==home:raise RuntimeError('XDG directory must remain inside your home')
            return p
        self.runtime=base('XDG_DATA_HOME','.local/share')/'CatPaw-Companion'
        self.state=base('XDG_STATE_HOME','.local/state')/'CatPaw-Companion'
        cfg=base('XDG_CONFIG_HOME','.config')
        self.config=cfg/'catpaw-companion/config.json';self.desktop=cfg/'autostart/catpaw-companion.desktop'
        for p in (self.runtime,self.state,self.config.parent,self.desktop.parent):
            if not p.resolve().is_relative_to(home):raise RuntimeError('Unsafe installation path')

    def pid(self):
        path=self.state/'run.lock'
        if not path.exists():return None
        with path.open('r') as f:
            try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);return None
            except BlockingIOError:pass
            data=json.load(f);pid=int(data['pid'])
            proc=Path('/proc')/str(pid)
            if proc.stat().st_uid!=os.getuid() or str(self.runtime/'app.py').encode() not in (proc/'cmdline').read_bytes().split(b'\0'):raise RuntimeError('Refusing to signal an unrelated process')
            return pid

    def configure(self,values):
        current=json.loads(self.config.read_text()) if self.config.exists() else {}
        current.update(values);current=config(current)
        self.config.parent.mkdir(parents=True,exist_ok=True)
        tmp=self.config.with_suffix('.tmp');tmp.write_text(json.dumps(current,indent=2)+'\n');tmp.replace(self.config)

    def autostart(self,enabled):
        if self.desktop.exists() and OWNER not in self.desktop.read_text():raise RuntimeError('Existing autostart file is not owned by Cat Paw')
        if not enabled:
            self.desktop.unlink(missing_ok=True);return
        def quote(s):return '"'+str(s).replace('\\','\\\\').replace('"','\\"').replace('`','\\`').replace('$','\\$').replace('%','%%')+'"'
        command=' '.join(quote(x) for x in self.command())
        self.desktop.parent.mkdir(parents=True,exist_ok=True)
        self.desktop.write_text('[Desktop Entry]\nType=Application\nName=Cat Paw Companion\nComment='+OWNER+'\nExec='+command+'\nTerminal=false\nX-GNOME-Autostart-enabled=true\n')

    def command(self):return ['/usr/bin/python3',str(self.runtime/'app.py'),'--config',str(self.config),'--state-dir',str(self.state)]

    def install(self,values):
        if self.runtime.exists() and (self.runtime.is_symlink() or not (self.runtime/'.owner').is_file() or (self.runtime/'.owner').read_text()!=OWNER):raise RuntimeError('Refusing to overwrite an unowned Companion directory')
        
        if self.pid():raise RuntimeError('请先停止正在运行的 Companion，再更新文件。')
        self.runtime.mkdir(parents=True,exist_ok=True)
        for name in ('app.py','motion.py','x11.py'):
            shutil.copy2(HERE/name,self.runtime/name)
        shutil.copytree(HERE/'assets',self.runtime/'assets',dirs_exist_ok=True)
        (self.runtime/'.owner').write_text(OWNER)
        self.configure(values)

    def start(self):
        if self.pid():print('猫爪已经在运行。');return
        if os.environ.get('XDG_SESSION_TYPE','').lower()=='wayland':raise RuntimeError('主题已安装；本版 Companion 需要 X11。请在登录界面选择 Zorin Desktop on Xorg 后运行 --action start。')
        if not os.environ.get('DISPLAY'):raise RuntimeError('请在图形桌面终端启动 Companion。')
        check=subprocess.run(['/usr/bin/python3','-c',"import gi;gi.require_version('Gtk','3.0');gi.require_foreign('cairo');from gi.repository import Gtk;import cairo"],capture_output=True)
        if check.returncode:raise RuntimeError('缺少桌面依赖，请安装：sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0')
        self.state.mkdir(parents=True,exist_ok=True)
        with (self.state/'companion.log').open('w') as log:
            child=subprocess.Popen(self.command(),stdout=log,stderr=log,start_new_session=True)
        for _ in range(40):
            if child.poll() is not None:raise RuntimeError((self.state/'companion.log').read_text())
            if 'Companion ready:' in (self.state/'companion.log').read_text():print('猫爪跟随、点击和回弹已启动。');return
            time.sleep(.05)
        raise RuntimeError('启动尚未确认，请查看 '+str(self.state/'companion.log'))

    def stop(self):
        pid=self.pid()
        if not pid:return
        os.kill(pid,signal.SIGTERM)
        for _ in range(50):
            if not self.pid():return
            time.sleep(.04)
        raise RuntimeError('Companion has not stopped; installation was not changed')

    def uninstall(self):
        self.stop();self.autostart(False)
        if self.runtime.exists():
            if (self.runtime/'.owner').read_text()!=OWNER:raise RuntimeError('Unowned runtime')
            self.state.mkdir(parents=True,exist_ok=True)
            self.runtime.rename(self.state/('removed-'+str(time.time_ns())))
        print('Companion 已移入归档，个人参数保留。')
