#!/usr/bin/env python3
"""Event-driven, input-transparent Cat Paw overlay for Linux X11."""
import argparse
import fcntl
import json
import math
import os
from pathlib import Path
import signal
import sys
import time

HERE=Path(__file__).resolve().parent
from motion import Motion, config

class Companion:
    def __init__(self,args):
        self.args=args;self.frame_source=0;self.idle_source=0;self.drain_source=0;self.locked=False
        self.frames=0;self.draws=0;self.input_events=0;self.role_events=0;self.original_theme=None;self.applied_theme=None
        self.settings=None;self.settings_signal=0;self.screen_proxy=None;self.screen_signal=0
        self.config_path=Path(args.config);self.state_dir=Path(args.state_dir)
        self.state_dir.mkdir(parents=True,exist_ok=True)
        self.lock=(self.state_dir/'run.lock').open('a+')
        try:fcntl.flock(self.lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise RuntimeError('Cat Paw Companion is already running')
        self.lock.seek(0);self.lock.truncate();self.lock.write(json.dumps({'pid':os.getpid(),'app':str(HERE/'app.py')}));self.lock.flush()
        self.cfg=config(json.loads(self.config_path.read_text()))
        self.source=Source()
        self.window=Gtk.Window(type=Gtk.WindowType.POPUP)
        self.window.set_title('Cat Paw Companion');self.window.set_wmclass('catpaw-companion','CatPawCompanion')
        self.window.set_decorated(False);self.window.set_app_paintable(True);self.window.set_accept_focus(False)
        self.window.set_focus_on_map(False);self.window.set_skip_taskbar_hint(True);self.window.set_skip_pager_hint(True)
        self.window.set_keep_above(True);self.window.stick();self.window.set_type_hint(Gdk.WindowTypeHint.NOTIFICATION)
        screen=self.window.get_screen();visual=screen.get_rgba_visual()
        if visual is None:raise RuntimeError('An RGBA-capable X11 visual is required')
        self.window.set_visual(visual)
        if not args.allow_uncomposited and not screen.is_composited():raise RuntimeError('A compositing desktop is required for a transparent paw')
        self.side=256 # Fixed transparent bounding window; actual artwork follows cursor-size.
        self.window.set_default_size(self.side,self.side);self.window.resize(self.side,self.side)
        self.window.connect('realize',self.realize);self.window.connect('draw',self.draw)
        self.pixbufs={color:GdkPixbuf.Pixbuf.new_from_file(str(HERE/'assets'/f'paw-{color}.png')) for color in ('pink','coffee')}
        self.window.realize()
        self.scale_factor=max(1,self.window.get_scale_factor())
        now=time.monotonic();position=self.source.position() or (0,0,0)
        self.model=Motion(self.cfg,position[0]/self.scale_factor,position[1]/self.scale_factor,now)
        self.name=self.source.cursor_name();self.model.set_role(self.name)
        self.io_source=GLib.io_add_watch(self.source.fd,GLib.IO_IN|GLib.IO_HUP|GLib.IO_ERR,self.input_ready)
        # Monitor configuration changes, never poll the file.
        self.config_path.parent.mkdir(parents=True,exist_ok=True)
        self.monitor=Gio.File.new_for_path(str(self.config_path.parent)).monitor_directory(Gio.FileMonitorFlags.NONE,None)
        self.monitor_signal=self.monitor.connect('changed',self.config_changed)
        if not args.no_theme_switch:
            schema=Gio.SettingsSchemaSource.get_default().lookup('org.gnome.desktop.interface',True)
            if schema:
                self.settings=Gio.Settings.new_full(schema,None,None)
                self.settings_signal=self.settings.connect('changed',self.desktop_changed)
                self.desktop_changed(self.settings,'cursor-size')
                current=self.settings.get_string('cursor-theme');color=self.cfg['pawColor'].title()
                companion=f'CatPaw-{color}-Companion'+('-Static' if current.endswith('Static') else '')
                icons=Path(os.environ.get('XDG_DATA_HOME',Path.home()/'.local/share'))/'icons'
                if current in (f'CatPaw-{color}-Animated',f'CatPaw-{color}-Static',companion) and (icons/companion/'index.theme').is_file():
                    self.original_theme=(f'CatPaw-{color}-'+('Static' if current.endswith('Static') else 'Animated'));self.applied_theme=companion;self.settings.set_string('cursor-theme',companion)
        try:
            self.screen_proxy=Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,Gio.DBusProxyFlags.DO_NOT_AUTO_START,None,'org.gnome.ScreenSaver','/org/gnome/ScreenSaver','org.gnome.ScreenSaver',None)
            self.screen_signal=self.screen_proxy.connect('g-signal',self.screen_signal_received)
        except GLib.Error:pass
        self.window.show_all();self.update_visibility();self.wake();self.status()

    def realize(self,window):
        native=window.get_window()
        native.set_pass_through(True)
        window.input_shape_combine_region(cairo.Region())
        native.input_shape_combine_region(cairo.Region(),0,0)

    def desktop_changed(self,settings,key):
        if key=='cursor-size':self.cfg['cursorSize']=max(24,min(128,settings.get_int(key)))
        if key in ('cursor-size','enable-animations'):
            self.model.cfg=config(self.cfg)
            if not settings.get_boolean('enable-animations'):self.model.cfg['animationStrength']=0
            self.wake()

    def screen_signal_received(self,proxy,sender,name,parameters):
        if name=='ActiveChanged':
            self.locked=bool(parameters.unpack()[0]);self.update_visibility()
            if not self.locked:self.wake()

    def config_changed(self,monitor,file,other,event):
        if file.get_basename()!=self.config_path.name:return
        try:self.cfg=config(json.loads(self.config_path.read_text()));self.model.cfg=self.cfg.copy();self.desktop_changed(self.settings,'enable-animations') if self.settings else self.wake()
        except (OSError,ValueError) as error:print('Configuration ignored:',error,flush=True)

    def input_ready(self,fd,condition):
        if condition & (GLib.IO_HUP|GLib.IO_ERR):Gtk.main_quit();return False
        self.drain();return True

    def drain(self):
        self.drain_source=0;events=self.source.drain()
        if not events:return False
        now=time.monotonic();position=self.source.position()
        if position:
            self.scale_factor=max(1,self.window.get_scale_factor())
            self.model.pointer(position[0]/self.scale_factor,position[1]/self.scale_factor,now)
        for kind,value in events:
            if kind=='button':self.model.button(value,now);self.input_events+=1
            elif kind=='motion':self.input_events+=1
            elif value!=self.name:
                self.name=value;self.model.set_role(value);self.role_events+=1;self.update_visibility()
        self.wake()
        if self.source.x.XPending(self.source.display) and not self.drain_source:self.drain_source=GLib.idle_add(self.drain)
        return False

    def update_visibility(self):
        visible=not self.locked and self.model.role!='hidden'
        if visible:self.window.show()
        else:
            self.window.hide();self.cancel('frame_source');self.cancel('idle_source')

    def cancel(self,name):
        value=getattr(self,name,0)
        if value:GLib.source_remove(value);setattr(self,name,0)

    def wake(self):
        self.cancel('idle_source')
        if self.locked or self.model.role=='hidden':self.status();return
        if not self.frame_source:
            self.model.last=time.monotonic()-.016
            self.frame_source=GLib.timeout_add(16,self.tick)

    def tick(self):
        now=time.monotonic();active=self.model.step(now);self.frames+=1
        if self.model.down and now-self.model.press_time<.15:active=True
        monitor=self.window.get_display().get_monitor_at_point(round(self.model.px),round(self.model.py))
        geometry=monitor.get_geometry() if monitor else self.window.get_screen().get_monitor_geometry(0)
        radius=self.cfg['cursorSize']*.4*self.cfg['pawScale']*1.1+4
        x=max(geometry.x+radius,min(geometry.x+geometry.width-radius,self.model.x))
        y=max(geometry.y+radius,min(geometry.y+geometry.height-radius,self.model.y))
        self.window.move(round(x-self.side/2),round(y+self.model.lift-self.side/2));self.window.queue_draw()
        if not active:
            self.frame_source=0
            if self.model.role!='text' and not self.model.idle_used and self.model.cfg['idleAnimation'] and not self.model.down and self.model.cfg['animationStrength']>0:
                delay=max(1,math.ceil((self.model.last_input+self.model.cfg['idleDelay']/1000-now)*1000))
                self.idle_source=GLib.timeout_add(delay,self.idle)
            self.status();return False
        return True

    def idle(self):
        self.idle_source=0;self.model.start_idle(time.monotonic());self.wake();return False

    def draw(self,window,cr):
        self.draws+=1
        cr.set_operator(cairo.OPERATOR_SOURCE);cr.set_source_rgba(0,0,0,0);cr.paint();cr.set_operator(cairo.OPERATOR_OVER)
        if not hasattr(self,'model'):return False
        pix=self.pixbufs[self.cfg['pawColor']]
        size=self.cfg['cursorSize']*.8*self.cfg['pawScale']*self.model.scale*(.65 if self.model.role=='text' else 1)
        cr.save();cr.translate(self.side/2,self.side/2);cr.rotate(math.radians(self.model.angle));cr.scale(size*self.model.squash/pix.get_width(),size/self.model.squash/pix.get_height())
        cr.translate(-pix.get_width()/2,-pix.get_height()/2);Gdk.cairo_set_source_pixbuf(cr,pix,0,0);cr.paint();cr.restore()
        if self.model.down and time.monotonic()-self.model.press_time<.14 and self.cfg['clickAnimation'] and self.model.cfg['animationStrength']>0:
            cr.set_source_rgba(.85,.55,.50,.85);cr.set_line_width(1.4)
            for a in (-130,-90,-50):
                angle=math.radians(a);r=size*.58
                cr.move_to(self.side/2+math.cos(angle)*r,self.side/2+math.sin(angle)*r)
                cr.line_to(self.side/2+math.cos(angle)*(r+3),self.side/2+math.sin(angle)*(r+3))
            cr.stroke()
        return False

    def status(self):
        if not self.args.diagnostics:return
        data={'pid':os.getpid(),'frames':self.frames,'draws':self.draws,'inputEvents':self.input_events,'cursorEvents':self.role_events,
              'cursorName':getattr(self,'name',''),'role':self.model.role,'pressed':self.model.down,'dragging':self.model.drag,
              'frameTimer':bool(self.frame_source),'idleTimer':bool(self.idle_source),'x':self.model.x,'y':self.model.y,
              'scale':self.model.scale,'angle':self.model.angle,'visible':self.window.get_visible(),'xid':self.window.get_window().get_xid()}
        path=Path(self.args.diagnostics);temporary=path.with_suffix('.tmp');temporary.write_text(json.dumps(data));temporary.replace(path)

    def close(self):
        for name in ('frame_source','idle_source','drain_source','io_source'):self.cancel(name)
        if hasattr(self,'monitor'):self.monitor.disconnect(self.monitor_signal);self.monitor.cancel()
        if self.screen_proxy and self.screen_signal:self.screen_proxy.disconnect(self.screen_signal)
        if self.settings:
            if self.settings_signal:self.settings.disconnect(self.settings_signal)
            if self.original_theme and self.settings.get_string('cursor-theme')==self.applied_theme:self.settings.set_string('cursor-theme',self.original_theme);Gio.Settings.sync()
        if hasattr(self,'window'):self.window.destroy()
        if hasattr(self,'source'):self.source.close()
        if hasattr(self,'lock'):self.lock.close()


def main():
    parser=argparse.ArgumentParser(description='Cat Paw X11 Companion')
    parser.add_argument('--config',required=True);parser.add_argument('--state-dir',required=True)
    parser.add_argument('--diagnostics');parser.add_argument('--no-theme-switch',action='store_true',help=argparse.SUPPRESS)
    parser.add_argument('--allow-uncomposited',action='store_true',help=argparse.SUPPRESS)
    args=parser.parse_args()
    if os.environ.get('XDG_SESSION_TYPE','').lower()=='wayland':parser.exit(2,'Wayland 尚不支持本版全局跟随；请在登录界面选择 Xorg 会话。\n')
    os.environ['GDK_BACKEND']='x11'
    global Gtk,Gdk,GLib,Gio,GdkPixbuf,cairo,Source
    import gi
    gi.require_version('Gtk','3.0');gi.require_version('Gdk','3.0');gi.require_version('GdkX11','3.0');gi.require_foreign('cairo')
    from gi.repository import Gtk,Gdk,GdkX11,GLib,Gio,GdkPixbuf
    import cairo
    from x11 import Source
    initialized,_=Gtk.init_check(None)
    if not initialized:parser.exit(2,'无法连接 X11 图形桌面。\n')
    app=None
    try:
        app=Companion(args)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT,signal.SIGTERM,lambda:Gtk.main_quit() or False)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT,signal.SIGINT,lambda:Gtk.main_quit() or False)
        print('Cat Paw Companion ready: XInput2 events, transparent overlay.',flush=True)
        Gtk.main()
    finally:
        if app:app.close()

if __name__=='__main__':
    try:main()
    except Exception as error:print(f'Cat Paw: {error}',file=sys.stderr);sys.exit(1)
