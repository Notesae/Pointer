"""Isolated X11 integration test. Never injects input into the user's desktop."""
import ctypes as C
import ctypes.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import sys
from motion import Motion,config

HERE=Path(__file__).resolve().parent
m=Motion({});m.pointer(100,100,.01);m.step(.026);assert 46<m.x<146
m.button(True,.03)
for i in range(1,30):m.step(.03+i*.016)
assert abs(m.scale-.88)<.002
m.button(False,.5);peak=0
for i in range(1,30):m.step(.5+i*.016);peak=max(peak,m.scale)
assert peak>1.02 and abs(m.scale-1)<.002
assert config({'followDelay':900})['followDelay']==100

binary=os.environ.get('CATPAW_XVFB','Xvfb')
with tempfile.TemporaryDirectory() as tmp:
    tmp=Path(tmp)
    server=subprocess.Popen([binary,'-displayfd','1','-screen','0','800x600x24','-nolisten','tcp','-ac'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    app=None
    try:
        display=':'+server.stdout.readline().strip();assert display!=':'
        env=os.environ.copy();env.update(DISPLAY=display,XDG_SESSION_TYPE='x11')
        cfg=tmp/'config.json';cfg.write_text(json.dumps({'idleAnimation':True}))
        diag=tmp/'diagnostics.json'
        with (tmp/'log').open('w') as log:
            app=subprocess.Popen(['/usr/bin/python3',str(HERE/'app.py'),'--config',str(cfg),'--state-dir',str(tmp/'state'),'--diagnostics',str(diag),'--no-theme-switch','--allow-uncomposited'],env=env,stdout=log,stderr=log)
        time.sleep(.5)
        assert app.poll() is None,(tmp/'log').read_text()
        x=C.CDLL(ctypes.util.find_library('X11'));xt=C.CDLL(ctypes.util.find_library('Xtst'))
        x.XOpenDisplay.argtypes=[C.c_char_p];x.XOpenDisplay.restype=C.c_void_p
        d=x.XOpenDisplay(display.encode());assert d
        x.XFlush.argtypes=[C.c_void_p];x.XDefaultRootWindow.argtypes=[C.c_void_p];x.XDefaultRootWindow.restype=C.c_ulong
        xt.XTestFakeMotionEvent.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_ulong]
        xt.XTestFakeButtonEvent.argtypes=[C.c_void_p,C.c_uint,C.c_int,C.c_ulong]
        def move(a,b):xt.XTestFakeMotionEvent(d,0,a,b,0);x.XFlush(d);time.sleep(.4)
        def button(v):xt.XTestFakeButtonEvent(d,1,int(v),0);x.XFlush(d);time.sleep(.4)
        def state():return json.loads(diag.read_text())
        move(250,240);assert state()['inputEvents']>0 and abs(state()['x']-(250+32*.42+(32*.4+16)*.7071))<1,state()
        button(True);assert state()['pressed'] and abs(state()['scale']-.88)<.01,state()
        move(290,250);assert state()['dragging'] and state()['angle']==8,state()
        button(False);assert not state()['pressed'] and abs(state()['scale']-1)<.01,state()
        fix=C.CDLL(ctypes.util.find_library('Xfixes'))
        fix.XFixesQueryVersion.argtypes=[C.c_void_p,C.POINTER(C.c_int),C.POINTER(C.c_int)]
        major=C.c_int(5);minor=C.c_int(0);fix.XFixesQueryVersion(d,C.byref(major),C.byref(minor))
        fix.XFixesSetCursorName.argtypes=[C.c_void_p,C.c_ulong,C.c_char_p]
        x.XCreateFontCursor.argtypes=[C.c_void_p,C.c_uint];x.XCreateFontCursor.restype=C.c_ulong
        x.XDefineCursor.argtypes=[C.c_void_p,C.c_ulong,C.c_ulong]
        cursor=x.XCreateFontCursor(d,68);fix.XFixesSetCursorName(d,cursor,b'hand2');x.XDefineCursor(d,x.XDefaultRootWindow(d),cursor);x.XFlush(d);time.sleep(.3)
        assert state()['role']=='hover' and state()['angle']==-5,state()
        shape=C.CDLL(ctypes.util.find_library('Xext'))
        shape.XShapeGetRectangles.argtypes=[C.c_void_p,C.c_ulong,C.c_int,C.POINTER(C.c_int),C.POINTER(C.c_int)];shape.XShapeGetRectangles.restype=C.c_void_p
        count=C.c_int();order=C.c_int();shape.XShapeGetRectangles(d,state()['xid'],2,C.byref(count),C.byref(order));assert count.value==0,'Overlay intercepts input'
        time.sleep(2.5);before=state();ticks=Path(f'/proc/{app.pid}/stat').read_text().split()[13:15];time.sleep(.5)
        assert state()['frames']==before['frames'] and not before['frameTimer'] and not before['idleTimer'],state()
        assert Path(f'/proc/{app.pid}/stat').read_text().split()[13:15]==ticks,'CPU used while settled'
        cursor2=x.XCreateFontCursor(d,152);fix.XFixesSetCursorName(d,cursor2,b'xterm');x.XDefineCursor(d,x.XDefaultRootWindow(d),cursor2);x.XFlush(d);time.sleep(.4)
        assert state()['visible'] and state()['role']=='text' and not state()['idleTimer'],state()
        assert abs(state()['x']-(290+32*.4*.65+16*.3))<.1,state()
        # Another client grabs the pointer, as selection widgets and menus do.
        x.XGrabPointer.argtypes=[C.c_void_p,C.c_ulong,C.c_int,C.c_uint,C.c_int,C.c_int,C.c_ulong,C.c_ulong,C.c_ulong]
        x.XUngrabPointer.argtypes=[C.c_void_p,C.c_ulong]
        assert x.XGrabPointer(d,x.XDefaultRootWindow(d),0,(1<<6)|(1<<2)|(1<<3),1,1,0,cursor2,0)==0
        button(True)
        previous=state()['inputEvents']
        move(420,280)
        assert state()['inputEvents']>previous and state()['pressed'],'Lost raw motion during selection grab: '+str(state())
        assert abs(state()['x']-(420+32*.4*.65+4))<.1,state()
        button(False)
        assert not state()['pressed'],'Lost release during selection grab'
        x.XUngrabPointer(d,0);x.XFlush(d)
        print('PASS: motion, press/rebound, drag, hover, compact text placement, selection grab continuity, empty input shape, settled rendering/CPU, isolated X11 events')
    finally:
        if app and app.poll() is None:app.terminate();app.wait(timeout=3)
        server.terminate();server.wait(timeout=3)
