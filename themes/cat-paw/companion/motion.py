"""Deterministic motion model, independent of GTK/X11. No polling or I/O."""
import math

DEFAULTS=dict(pawColor='pink',pawDistance=16,pawScale=1.0,followDelay=65,
              animationStrength=1.0,clickAnimation=True,idleAnimation=True,
              followAnimation=True,cursorSize=32,idleDelay=1600)
LIMITS={'pawDistance':(8,40),'pawScale':(.5,2),'followDelay':(40,100),
        'animationStrength':(0,2),'cursorSize':(24,128),'idleDelay':(1000,5000)}

def config(values):
    result=DEFAULTS.copy()
    for key,value in values.items():
        if key not in result:continue
        if key=='pawColor':
            if value not in ('pink','coffee'):raise ValueError('pawColor must be pink or coffee')
        elif key in LIMITS:
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):raise ValueError(key)
            low,high=LIMITS[key];value=max(low,min(high,value))
        elif not isinstance(value,bool):raise ValueError(key+' must be boolean')
        result[key]=value
    return result

HOVER={'hand','hand1','hand2','pointer','pointing_hand','openhand','grab','e29285e634086352946a0e7090d73106'}
TEXT={'text','xterm','ibeam','vertical-text'}
HIDDEN={'crosshair','cross','tcross','plus','watch','wait','progress','left_ptr_watch',
        'not-allowed','no-drop','crossed_circle','forbidden','move','fleur','all-scroll','size_all',
        'sb_h_double_arrow','sb_v_double_arrow','bd_double_arrow','fd_double_arrow','size_hor','size_ver',
        'size_fdiag','size_bdiag','top_side','bottom_side','left_side','right_side','top_left_corner','top_right_corner',
        'bottom_left_corner','bottom_right_corner','h_double_arrow','v_double_arrow','split_h','split_v'}

def classify(name):
    name=(name or '').lower()
    if name in TEXT:return 'text'
    if name in HIDDEN or 'resize' in name:return 'hidden'
    if name in ('grabbing','closedhand','208530c400c041818281048008011002'):return 'drag'
    return 'hover' if name in HOVER else 'normal'

class Motion:
    def __init__(self,settings,x=0,y=0,now=0):
        self.cfg=config(settings);self.px=x;self.py=y;self.x=x;self.y=y
        self.vx=self.vy=0.;self.role='normal';self.down=False;self.drag=False
        self.press_origin=(x,y);self.last_input=now;self.idle_used=False;self.idle_start=None
        self.release=None;self.scale=1.;self.angle=0.;self.last=now
        self.squash=1.;self.lift=0.;self.press_time=now
        self.x,self.y=self.target()

    def target(self):
        c=self.cfg;distance=c['pawDistance'];strength=c['animationStrength']
        distance-=5*strength if self.down and c['clickAnimation'] else 0
        # Distance is a single diagonal gap, not an extra full gap on BOTH axes.
        radius=c['cursorSize']*.4*c['pawScale']
        if self.role=='text':
            return self.px+radius*.65+max(4,distance*.3), self.py+c['cursorSize']*.30+radius*.65
        return (self.px+c['cursorSize']*.42+(radius+distance)*.7071,
                self.py+c['cursorSize']*.53+(radius+distance)*.7071-(3*strength if self.role=='hover' else 0))

    def pointer(self,x,y,now):
        if (x,y)!=(self.px,self.py):
            self.px,self.py=x,y;self.last_input=now;self.idle_used=False;self.idle_start=None
            if self.down and math.hypot(x-self.press_origin[0],y-self.press_origin[1])>3:self.drag=True

    def button(self,pressed,now):
        self.down=pressed;self.last_input=now;self.idle_used=False;self.idle_start=None
        if pressed:self.press_time=now;self.press_origin=(self.px,self.py);self.release=None
        else:self.release=now if self.cfg['clickAnimation'] else None;self.drag=False

    def set_role(self,name):
        self.role=classify(name)
        if self.role=='hidden':self.idle_start=None

    def idle_due(self,now):
        return (self.cfg['idleAnimation'] and self.cfg['animationStrength']>0 and not self.down
                and self.role not in ('hidden','text') and not self.idle_used
                and now-self.last_input>=self.cfg['idleDelay']/1000)

    def start_idle(self,now):
        if self.idle_due(now):self.idle_start=now;self.idle_used=True

    def step(self,now):
        dt=max(0,min(.05,now-self.last));self.last=now;c=self.cfg
        tx,ty=self.target()
        if c['followAnimation'] and c['animationStrength']>0:
            omega=3/((min(40,c['followDelay']) if self.role=='text' and self.down else c['followDelay'])/1000)
            for pos,vel,target in [('x','vx',tx),('y','vy',ty)]:
                delta=getattr(self,pos)-target;v=getattr(self,vel);decay=math.exp(-omega*dt)
                temp=(v+omega*delta)*dt
                setattr(self,pos,target+(delta+temp)*decay)
                setattr(self,vel,(v-omega*temp)*decay)
        else:self.x,self.y=tx,ty;self.vx=self.vy=0
        wanted=1.;strength=c['animationStrength'];active=False
        if c['clickAnimation'] and strength>0:
            if self.down:wanted=1-.12*strength
            elif self.release is not None:
                t=(now-self.release)/.18
                if t<1:
                    wanted=(.88+(.17)*min(t/.45,1)) if t<.45 else 1.05-.05*((t-.45)/.55)
                    wanted=1+(wanted-1)*strength;active=True
                else:self.release=None
        blend=1-math.exp(-dt/0.022) if dt else 0
        self.scale+=(wanted-self.scale)*blend
        # A soft pad flattens on contact, then stretches briefly on release.
        deformation=.075*strength if self.down and c['clickAnimation'] else 0.
        if self.release is not None and c['clickAnimation']:
            t=max(0,min(1,(now-self.release)/.18))
            deformation=-.05*strength*math.sin(math.pi*t)
        self.squash+=((1+deformation)-self.squash)*blend
        lift=0.
        if self.release is not None and c['clickAnimation']:
            lift=-2.5*strength*math.sin(math.pi*max(0,min(1,(now-self.release)/.18)))
        angle=(2 if self.role=='text' and self.drag else 8 if self.drag or self.role=='drag' else -5 if self.role=='hover' else 0)*strength
        if c['followAnimation'] and strength>0 and not self.down and self.role!='text':
            angle+=max(-7,min(7,self.vx*.009))*strength
        if self.idle_start is not None:
            t=(now-self.idle_start)/.65
            if t<1:
                envelope=math.sin(math.pi*t)**2
                angle+=5*strength*math.sin(t*math.tau)*envelope
                lift-=2*strength*envelope;active=True
            else:self.idle_start=None
        self.lift+=(lift-self.lift)*blend
        self.angle+=(angle-self.angle)*blend
        settled=math.hypot(self.x-tx,self.y-ty)<.1 and math.hypot(self.vx,self.vy)<1 and abs(self.scale-wanted)<.002 and abs(self.angle-angle)<.05 and abs(self.squash-(1+deformation))<.002 and abs(self.lift-lift)<.02
        if settled:self.x,self.y=tx,ty;self.vx=self.vy=0;self.scale=wanted;self.angle=angle;self.squash=1+deformation;self.lift=lift
        return not settled or active
