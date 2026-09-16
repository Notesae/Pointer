"""XInput2 raw mouse events and XFixes cursor names via the system libraries.
No device grabbing, /dev/input access, keyboard subscription or polling.
"""
import ctypes as C
import ctypes.util
I=C.c_int; U=C.c_ulong; P=C.c_void_p
class Cookie(C.Structure):
    _fields_=[('type',I),('serial',U),('send_event',I),('display',P),('extension',I),('evtype',I),('cookie',C.c_uint),('data',P)]
class Valuators(C.Structure):
    _fields_=[('mask_len',I),('mask',C.POINTER(C.c_ubyte)),('values',C.POINTER(C.c_double))]
class Raw(C.Structure):
    _fields_=[('type',I),('serial',U),('send_event',I),('display',P),('extension',I),('evtype',I),('time',U),('deviceid',I),('sourceid',I),('detail',I),('flags',I),('valuators',Valuators),('raw_values',C.POINTER(C.c_double))]
class CursorNotify(C.Structure):
    _fields_=[('type',I),('serial',U),('send_event',I),('display',P),('window',U),('subtype',I),('cursor_serial',U),('timestamp',U),('cursor_name',U)]
class Event(C.Union):
    _fields_=[('type',I),('cookie',Cookie),('cursor',CursorNotify),('pad',C.c_long*24)]
class Mask(C.Structure):
    _fields_=[('deviceid',I),('mask_len',I),('mask',C.POINTER(C.c_ubyte))]
class CursorImage(C.Structure):
    _fields_=[('x',C.c_short),('y',C.c_short),('width',C.c_ushort),('height',C.c_ushort),('xhot',C.c_ushort),('yhot',C.c_ushort),('serial',U),('pixels',C.POINTER(U)),('atom',U),('name',C.c_char_p)]

def library(name):
    found=ctypes.util.find_library(name)
    if not found:raise RuntimeError('Missing system library: '+name)
    return C.CDLL(found)

def bind(lib,name,args,result):
    fn=getattr(lib,name);fn.argtypes=args;fn.restype=result;return fn

class Source:
    def __init__(self):
        self.x=library('X11');self.xi=library('Xi');self.fix=library('Xfixes');self.display=None
        bind(self.x,'XOpenDisplay',[C.c_char_p],P);bind(self.x,'XCloseDisplay',[P],I)
        bind(self.x,'XDefaultRootWindow',[P],U);bind(self.x,'XConnectionNumber',[P],I)
        bind(self.x,'XQueryExtension',[P,C.c_char_p,C.POINTER(I),C.POINTER(I),C.POINTER(I)],I)
        bind(self.x,'XPending',[P],I);bind(self.x,'XNextEvent',[P,C.POINTER(Event)],I)
        bind(self.x,'XGetEventData',[P,C.POINTER(Cookie)],I);bind(self.x,'XFreeEventData',[P,C.POINTER(Cookie)],None)
        bind(self.x,'XFlush',[P],I);bind(self.x,'XFree',[P],I)
        bind(self.x,'XGetAtomName',[P,U],P)
        bind(self.x,'XQueryPointer',[P,U,C.POINTER(U),C.POINTER(U),C.POINTER(I),C.POINTER(I),C.POINTER(I),C.POINTER(I),C.POINTER(C.c_uint)],I)
        bind(self.xi,'XIQueryVersion',[P,C.POINTER(I),C.POINTER(I)],I)
        bind(self.xi,'XISelectEvents',[P,U,C.POINTER(Mask),I],I)
        bind(self.fix,'XFixesQueryVersion',[P,C.POINTER(I),C.POINTER(I)],I)
        bind(self.fix,'XFixesQueryExtension',[P,C.POINTER(I),C.POINTER(I)],I)
        bind(self.fix,'XFixesSelectCursorInput',[P,U,U],None)
        bind(self.fix,'XFixesGetCursorImage',[P],C.POINTER(CursorImage))
        self.display=self.x.XOpenDisplay(None)
        if not self.display:raise RuntimeError('Cannot open X11 display')
        try:
            self.root=self.x.XDefaultRootWindow(self.display);opcode=I();event=I();error=I()
            if not self.x.XQueryExtension(self.display,b'XInputExtension',C.byref(opcode),C.byref(event),C.byref(error)):raise RuntimeError('XInput2 unavailable')
            self.opcode=opcode.value;major=I(2);minor=I(0)
            if self.xi.XIQueryVersion(self.display,C.byref(major),C.byref(minor))!=0:raise RuntimeError('XInput 2.0 required')
            bits=(C.c_ubyte*3)()
            for number in (15,16,17):bits[number//8]|=1<<(number%8)
            mask=Mask(1,len(bits),bits) # XIAllMasterDevices; raw button press/release + motion only.
            if self.xi.XISelectEvents(self.display,self.root,C.byref(mask),1)!=0:raise RuntimeError('Cannot subscribe to mouse events')
            if not self.fix.XFixesQueryExtension(self.display,C.byref(event),C.byref(error)):raise RuntimeError('XFixes unavailable')
            major=I(5);minor=I(0)
            if not self.fix.XFixesQueryVersion(self.display,C.byref(major),C.byref(minor)):raise RuntimeError('Cannot negotiate XFixes')
            self.cursor_event=event.value+1;self.fix.XFixesSelectCursorInput(self.display,self.root,1)
            self.x.XFlush(self.display);self.fd=self.x.XConnectionNumber(self.display)
        except Exception:self.close();raise

    def position(self):
        root=U();child=U();rx=I();ry=I();wx=I();wy=I();mask=C.c_uint()
        valid=self.x.XQueryPointer(self.display,self.root,C.byref(root),C.byref(child),C.byref(rx),C.byref(ry),C.byref(wx),C.byref(wy),C.byref(mask))
        return (rx.value,ry.value,mask.value) if valid else None

    def cursor_name(self):
        image=self.fix.XFixesGetCursorImage(self.display)
        if not image:return ''
        try:return (image.contents.name or b'').decode('utf-8','replace')
        finally:self.x.XFree(image)

    def drain(self):
        result=[]
        while self.x.XPending(self.display):
            event=Event();self.x.XNextEvent(self.display,C.byref(event))
            if event.type==35 and event.cookie.extension==self.opcode:
                if self.x.XGetEventData(self.display,C.byref(event.cookie)):
                    try:
                        raw=C.cast(event.cookie.data,C.POINTER(Raw)).contents
                        if raw.evtype==17:result.append(('motion',None))
                        elif raw.detail==1 and raw.evtype in (15,16):result.append(('button',raw.evtype==15))
                    finally:self.x.XFreeEventData(self.display,C.byref(event.cookie))
            elif event.type==self.cursor_event:
                atom=event.cursor.cursor_name;pointer=self.x.XGetAtomName(self.display,atom) if atom else None
                try:result.append(('cursor',C.string_at(pointer).decode('utf-8','replace') if pointer else ''))
                finally:
                    if pointer:self.x.XFree(pointer)
        return result

    def close(self):
        if self.display:self.x.XCloseDisplay(self.display);self.display=None
