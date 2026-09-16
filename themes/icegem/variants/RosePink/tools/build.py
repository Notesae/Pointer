from pathlib import Path
import math, struct, json, io, base64
from PIL import Image, ImageDraw, ImageFont
import cairosvg

ROOT=Path(__file__).resolve().parents[1]
SIZES=(32,48,64)
FRAMES=24
THEME_SHIFT=115
THEME_NAME='玫瑰粉'
NAMES=[('normal','正常选择','Arrow'),('working','后台忙碌','AppStarting'),('busy','忙碌 / 等待','Wait'),('help','帮助选择','Help'),('link','链接选择','Hand'),('unavailable','不可用','No'),('text','文本选择','IBeam'),('vertical-text','竖排文本选择',''),('precision','精准选择','Crosshair'),('resize-nwse','对角调整 ↖↘','SizeNWSE'),('resize-nesw','对角调整 ↗↙','SizeNESW'),('resize-ew','水平调整','SizeWE'),('resize-ns','垂直调整','SizeNS'),('move','移动','SizeAll'),('alternate','替代选择','UpArrow'),('handwriting','手写','NWPen'),('location','位置选择','Pin'),('person','人员选择','Person')]
OUTLINE='#334f7b'; BLUE='#9bdcff'; LIGHT='#edfaff'; MID='#70bce7'; LILAC='#d3d1fa'
def geometry(name,frame=0):
    ops=[]
    def poly(p,c,stroke=OUTLINE,w=.7):ops.append(('poly',p,c,stroke,w))
    def line(p,c=OUTLINE,w=.85):ops.append(('line',p,None,c,w))
    def mix(a,b,t):return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
    def curve(d,c=OUTLINE,w=1):ops.append(('path',d,None,c,w))
    def gem(p,large=False,animated=False,purple=False):
        a,b,c,d=p
        q=mix(a,c,.61 if large else .57)
        ridge=mix(a,q,.48)
        # Four principal planes, with a slender reflected wedge and bevels.
        poly(p,'url(#body)',None)
        poly([a,b,q],'url(#crown)',None)
        poly([b,c,q],'url(#right)',None)
        poly([c,d,q],'url(#violet)' if purple else 'url(#foot)',None)
        poly([d,a,q],'url(#left)',None)
        # Deterministic crown: outer girdle, inset table and eight side facets.
        center=mix(a,c,.58)
        inner=[mix(v,center,t) for v,t in zip(p,(.17,.24,.19,.24))]
        ia,ib,ic,id=inner
        for vertices,fill in [
            ([a,b,ib,ia],'url(#edgeIce)'),
            ([b,c,ic,ib],'url(#edgeIndigo)'),
            ([c,d,id,ic],'url(#edgeLilac)'),
            ([d,a,ia,id],'url(#edgeBlue)'),
            ([ia,ib,q],'url(#tableLight)'),
            ([ia,q,id],'url(#tableBlue)'),
            ([id,q,ic],'url(#tableIce)'),
            ([ib,ic,q],'url(#tableLilac)')]:
            poly(vertices,fill,None)
        if large:
            r=mix(ia,q,.57); t=mix(ib,q,.51); u=mix(ic,q,.45)
            poly([ia,r,mix(ia,ib,.56)],'#ffffffb0',None)
            poly([r,t,q],'url(#reflectedBlue)',None)
            poly([id,r,q],'#72d9ff91',None)
            poly([q,t,u],'#e6faffd9',None)
            poly([ic,u,mix(ic,id,.5)],'#fcf4ffba',None)
            poly([mix(a,d,.33),mix(a,d,.82),id,ia],'url(#edgeBlue)',None)
            line([ia,q,ic],'#f5ffff',.34)
            line([id,q,ib],'#f5ffff',.30)
            line([ia,ib],'#ffffffb0',.23)
            line([ib,ic],'#849cdfb0',.24)
        else:
            line([ia,q,ic],'#efffff',.28)
            line([id,q,ib],'#e3fbff',.24)
        if animated:
            phase=frame/FRAMES
            level=math.sin(math.pi*phase)**2
            # A clipped, soft highlight follows the long crystal axis.
            ops.append(('sweep',p,(a,c,phase,level),None,0))
            poly([a,b,q],'#ffffff'+f'{round(55*level):02x}',None)
            line([q,b],'#ffffff'+f'{round(100+150*level):02x}',.48)
        line(p+[p[0]],'#233e79',.72 if large else .65)
        # The inset bright edge supplies the glass bevel without widening the silhouette.
        center=mix(a,c,.55)
        inset=[mix(v,center,.065 if large else .11) for v in p]
        line([inset[3],inset[0],inset[1]],'#e7fbff',.38 if large else .26)
        line([inset[1],inset[2]],'#c8c8ff',.33 if large else .23)
    def main():
        p=[(6,3),(19,16.8),(17,27),(6.7,19.8)]
        # Radial-gradient shadows keep every export deterministic; no unsupported SVG blur.
        ops.append(('ellipse',(13.5,28.3,6.7,2.2),'url(#shadow)',None,0))
        ops.append(('ellipse',(14.5,22,7,8),'url(#halo)',None,0))
        gem(p,large=True,animated=name in ('normal','working'),purple=name=='alternate')
    def arm(angle,inner=1.25,outer=10,width=2.6):
        def tr(x,y):return (16+x*math.cos(angle)-y*math.sin(angle),16+x*math.sin(angle)+y*math.cos(angle))
        gem([tr(outer,0),tr(inner+2.7,width),tr(inner,0),tr(inner+2.7,-width)])
    if name in ['normal','working','help','unavailable','alternate','location','person']:
        main()
        if name=='working':
            strength=(1-math.cos(2*math.pi*frame/FRAMES))/2
            ops.append(('ellipse',(25,12,4.3,4.3),None,'#528cdd',1.05))
            ops.append(('ellipse',(25,12,3.75,3.75),None,'#baf4ff',.38))
            curve('M 22.1 8.9 A 4.3 4.3 0 0 1 28.2 9.1','#ffffff'+f'{round(40+210*strength):02x}',.8)
        if name=='help':
            curve('M 22 10 C 22 6.3 28.8 6.3 28.8 10 C 28.8 12.1 25.4 12.5 25.4 14.7',w=1.12)
            ops.append(('ellipse',(25.4,17.3,.68,.68),OUTLINE,None,0))
        if name=='unavailable':
            ops.append(('ellipse',(25.5,12,4.4,4.4),None,'#ec647f',1.05))
            line([(22.5,15),(28.5,9)],'#ec647f',1.05)
        if name=='location':
            poly([(25,9),(28,12),(25,19),(22,12)],LIGHT);poly([(25,11),(26,12),(25,13),(24,12)],MID,None)
        if name=='person':
            gem([(25,8),(27,10),(25,12),(23,10)]);line([(21,18),(22,15),(25,14),(28,15),(29,18)],w=1)
    elif name=='link':
        main()
        # Three detached click rays surround the original gem tip; fixed hotspot.
        for ray in [[(1.5,1.5),(3.2,2.2)],[(11,2),(16.5,2)],[(1.6,11),(3.3,6.6)]]:
            line(ray,'#ffffff',2.8)
            line(ray,'#244780',1.85)
            line(ray,'#91e3ff',.72)
    elif name=='busy':
        ops.append(('ellipse',(16,28.5,6.4,1.8),'url(#shadow)',None,0))
        ops.append(('ellipse',(16,20,8,10),'url(#halo)',None,0))
        gem([(16,4),(22,18),(16,27),(10,18)],large=True,animated=True)
    elif name in ('text','vertical-text'):
        def tr(p):return [(32-y,x) for x,y in p] if name=='vertical-text' else p
        poly(tr([(15.4,8.3),(16.6,8.3),(16.6,23.7),(15.4,23.7)]),'url(#text)',w=.6)
        for y in (8.3,23.7):poly(tr([(12.8,y),(16,y-.7),(19.2,y),(16,y+.7)]),'url(#crown)',w=.6)
    elif name in ('precision','move','resize-ew','resize-ns','resize-nwse','resize-nesw'):
        angles={'precision':[0,90,180,270],'move':[0,90,180,270],'resize-ew':[0,180],'resize-ns':[90,270],'resize-nwse':[45,225],'resize-nesw':[135,315]}[name]
        for deg in angles:
            a=math.radians(deg);line([(16,16),(16+4*math.cos(a),16+4*math.sin(a))],OUTLINE,.8)
            arm(a,1.2,9 if name=='precision' else 11,1.8 if name=='precision' else 2.7)
        poly([(15.5,15.5),(16.5,15.5),(16.5,16.5),(15.5,16.5)],LIGHT,w=.55)
    elif name=='handwriting':gem([(7,26),(13,9),(18,6),(17,13)]);line([(7,26),(9,23)],OUTLINE,1)
    return ops
def rgba(c):
    c=c.lstrip('#');return tuple(int(c[i:i+2],16) for i in (0,2,4))+(int(c[6:8],16) if len(c)==8 else 255,)
def render(ops,size):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg(ops).encode(),output_width=size*4,output_height=size*4))).convert('RGBA').resize((size,size),Image.Resampling.LANCZOS)
def svg(ops):
    defs = """<defs>
    <linearGradient id="body" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#e9f8ff"/><stop offset=".55" stop-color="#a1d8fa"/><stop offset="1" stop-color="#d8dcff"/></linearGradient>
    <linearGradient id="crown" x1="0" y1="0" x2=".8" y2="1"><stop stop-color="#b9d7ff"/><stop offset=".40" stop-color="#f9ffff"/><stop offset=".70" stop-color="#eafaff"/><stop offset="1" stop-color="#7dcef2"/></linearGradient>
    <linearGradient id="left" x1="0" y1="0" x2="1" y2=".5"><stop stop-color="#3265a6"/><stop offset=".32" stop-color="#4ea8dc"/><stop offset=".78" stop-color="#bbf3ff"/><stop offset="1" stop-color="#e9ffff"/></linearGradient>
    <linearGradient id="right" x1="0" y1="0" x2=".7" y2="1"><stop stop-color="#72b6f0"/><stop offset=".36" stop-color="#5486cb"/><stop offset=".7" stop-color="#d4e9ff"/><stop offset="1" stop-color="#f5edff"/></linearGradient>
    <linearGradient id="foot" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#b1f3ff"/><stop offset=".48" stop-color="#51a8d9"/><stop offset=".52" stop-color="#d8f9ff"/><stop offset="1" stop-color="#b4b5ee"/></linearGradient>
    <linearGradient id="violet" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#cbf3ff"/><stop offset=".5" stop-color="#8e91e4"/><stop offset="1" stop-color="#d8d0ff"/></linearGradient>
    <linearGradient id="inner" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#345ca6" stop-opacity=".7"/><stop offset=".5" stop-color="#e0faff" stop-opacity=".25"/><stop offset="1" stop-color="#fbffff" stop-opacity=".8"/></linearGradient>
    <linearGradient id="refract" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#f3ffff"/><stop offset=".46" stop-color="#c2e9ff" stop-opacity=".7"/><stop offset="1" stop-color="#bdbaf4" stop-opacity=".4"/></linearGradient>
    <linearGradient id="text" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#76b6e7"/><stop offset=".48" stop-color="#f4ffff"/><stop offset="1" stop-color="#a6bcff"/></linearGradient>
    <radialGradient id="shadow"><stop stop-color="#578cdb" stop-opacity=".25"/><stop offset=".55" stop-color="#6ca4e2" stop-opacity=".10"/><stop offset="1" stop-color="#8db5ed" stop-opacity="0"/></radialGradient>
    <radialGradient id="halo"><stop stop-color="#bec7ff" stop-opacity=".10"/><stop offset=".6" stop-color="#a7dfff" stop-opacity=".07"/><stop offset="1" stop-color="#d4edff" stop-opacity="0"/></radialGradient>
<linearGradient id="edgeIce" x1="0" y1="0" x2="1" y2="1"><stop offset="0.0" stop-color="#edfaff"/><stop offset="0.5" stop-color="#4e90e2"/><stop offset="1.0" stop-color="#e9ffff"/></linearGradient>
<linearGradient id="edgeIndigo" x1="0" y1="0" x2="1" y2="1"><stop offset="0.0" stop-color="#174b9b"/><stop offset="0.5" stop-color="#83bfff"/><stop offset="1.0" stop-color="#6668c6"/></linearGradient>
<linearGradient id="edgeLilac" x1="0" y1="0" x2="1" y2="1"><stop offset="0.0" stop-color="#929fe6"/><stop offset="0.5" stop-color="#faf5ff"/><stop offset="1.0" stop-color="#477cca"/></linearGradient>
<linearGradient id="edgeBlue" x1="0" y1="0" x2="1" y2="1"><stop offset="0.0" stop-color="#2d5494"/><stop offset="0.5" stop-color="#94ecff"/><stop offset="1.0" stop-color="#318eca"/></linearGradient>
<linearGradient id="tableLight" x1="0" y1="0" x2="1" y2="1"><stop offset="0.0" stop-color="#d0eaff"/><stop offset="0.5" stop-color="#ffffff"/><stop offset="1.0" stop-color="#acd7f7"/></linearGradient>
<linearGradient id="tableBlue" x1="0" y1="0" x2="1" y2="1"><stop offset="0.0" stop-color="#529bd5"/><stop offset="0.5" stop-color="#defaff"/><stop offset="1.0" stop-color="#83c7ed"/></linearGradient>
<linearGradient id="tableIce" x1="0" y1="0" x2="1" y2="1"><stop offset="0.0" stop-color="#d8faff"/><stop offset="0.5" stop-color="#55c3ea"/><stop offset="1.0" stop-color="#f1faff"/></linearGradient>
<linearGradient id="tableLilac" x1="0" y1="0" x2="1" y2="1"><stop offset="0.0" stop-color="#718bd9"/><stop offset="0.5" stop-color="#d8ddff"/><stop offset="1.0" stop-color="#fcf7ff"/></linearGradient>
<linearGradient id="reflectedBlue" x1="0" y1="0" x2="1" y2="1"><stop offset="0.0" stop-color="#e8ffff"/><stop offset="0.5" stop-color="#409dcc"/><stop offset="1.0" stop-color="#bbf3ff"/></linearGradient>
    </defs>"""
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">',defs]
    def paint(c,prop):
        if c and c.startswith('#') and len(c)==9:return f'{prop}="{c[:7]}" {prop}-opacity="{int(c[7:9],16)/255:.4f}"'
        return f'{prop}="{c or "none"}"'
    for idx,(typ,p,f,s,w) in enumerate(ops):
        points=lambda: ' '.join(f'{x:.4f},{y:.4f}' for x,y in p)
        if typ=='sweep':
            a,c,phase,level=f
            # A long-axis gradient preserves faceted highlights rather than drawing a flat stripe.
            start=(a[0]+(c[0]-a[0])*(phase-.25),a[1]+(c[1]-a[1])*(phase-.25))
            end=(a[0]+(c[0]-a[0])*(phase+.25),a[1]+(c[1]-a[1])*(phase+.25))
            parts.append(f'<defs><linearGradient id="sweep{idx}" gradientUnits="userSpaceOnUse" x1="{start[0]}" y1="{start[1]}" x2="{end[0]}" y2="{end[1]}"><stop stop-color="#fff" stop-opacity="0"/><stop offset=".3" stop-color="#def9ff" stop-opacity="{.2*level}"/><stop offset=".5" stop-color="#fff" stop-opacity="{.8*level}"/><stop offset=".7" stop-color="#e7f5ff" stop-opacity="{.2*level}"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs><polygon points="{points()}" fill="url(#sweep{idx})"/>')
            continue
        style=f'{paint(f,"fill")} {paint(s,"stroke")} stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'
        if typ=='ellipse':
            x,y,rx,ry=p;parts.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" {style}/>')
        elif typ=='path':parts.append(f'<path d="{p}" {style}/>')
        else:parts.append(f'<{"polygon" if typ=="poly" else "polyline"} points="{points()}" {style}/>')
    return theme_svg(''.join(parts)+'</svg>')

def theme_svg(document):
    # Only the ice-blue / violet material family changes hue. Neutral whites,
    # alpha and the semantic red prohibition symbol remain unchanged.
    import re, colorsys
    def recolor(match):
        value=match.group(0)
        rgb=tuple(int(value[i:i+2],16)/255 for i in (1,3,5))
        h,l,s=colorsys.rgb_to_hls(*rgb)
        if THEME_SHIFT==0 or s<.03 or not 170<=h*360<=285:return value
        h=(h+THEME_SHIFT/360)%1
        converted=colorsys.hls_to_rgb(h,l,s)
        return '#'+''.join(f'{round(c*255):02x}' for c in converted)
    return re.sub(r'#[0-9a-fA-F]{6}(?![0-9a-fA-F])',recolor,document)

def svg_image(ops):
    # Isolate gradient IDs for every frame and state in the HTML preview.
    return '<img alt="cursor" src="data:image/svg+xml;base64,'+base64.b64encode(svg(ops).encode()).decode()+'">'
def hotspot(name,size):
    if name=='link':return round(6*size/32),round(3*size/32)
    x,y=(6,3) if name in ('normal','working','help','link','unavailable','alternate','location','person') else ((7,26) if name=='handwriting' else (16,16))
    return round(x*size/32),round(y*size/32)
def cur(name,frame=0,sizes=SIZES):
    entries=[];data=[];offset=6+16*len(sizes)
    for n in sizes:
        im=render(geometry(name,frame),n); raw=im.tobytes('raw','BGRA',0,-1)
        stride=((n+31)//32)*4;mask=bytearray(stride*n)
        for yy in range(n):
            for xx in range(n):
                if im.getpixel((xx,n-1-yy))[3]==0:mask[yy*stride+xx//8]|=128>>(xx%8)
        dib=struct.pack('<IiiHHIIiiII',40,n,n*2,1,32,0,len(raw)+len(mask),0,0,0,0)+raw+mask
        hx,hy=hotspot(name,n);entries.append(struct.pack('<BBBBHHII',n,n,0,0,hx,hy,len(dib),offset));data.append(dib);offset+=len(dib)
    return struct.pack('<HHH',0,2,len(sizes))+b''.join(entries+data)
def chunk(tag,data):return tag+struct.pack('<I',len(data))+data+(b'\0' if len(data)%2 else b'')
def ani(name,sizes=SIZES):
    rate=4 if name!='normal' else 5
    body=b'ACON'+chunk(b'anih',struct.pack('<9I',36,FRAMES,FRAMES,0,0,32,1,rate,1))+chunk(b'rate',struct.pack(f'<{FRAMES}I',*([rate]*FRAMES)))+chunk(b'LIST',b'fram'+b''.join(chunk(b'icon',cur(name,i,sizes)) for i in range(FRAMES)))
    return b'RIFF'+struct.pack('<I',len(body))+body
def build():
    for d in ['src/svg','src/animation','cursors/multi','preview','docs']+[f'cursors/{s}' for s in SIZES]: (ROOT/d).mkdir(parents=True,exist_ok=True)
    manifest=[]
    for name,cn,slot in NAMES:
        (ROOT/f'src/svg/icegem-{name}.svg').write_text(svg(geometry(name)))
        (ROOT/f'cursors/multi/icegem-{name}.cur').write_bytes(cur(name))
        for n in SIZES:
            (ROOT/f'cursors/{n}/icegem-{name}.cur').write_bytes(cur(name,sizes=(n,)))
            render(geometry(name),n).save(ROOT/f'preview/icegem-{name}-{n}.png')
        manifest.append(dict(name=name,label=cn,slot=slot or None,hotspots={str(n):hotspot(name,n) for n in SIZES}))
    for name in ('normal','working','busy'):
        (ROOT/f'cursors/multi/icegem-{name}.ani').write_bytes(ani(name))
        for n in SIZES:(ROOT/f'cursors/{n}/icegem-{name}.ani').write_bytes(ani(name,(n,)))
        for i in range(FRAMES):(ROOT/f'src/animation/{name}-{i:02}.svg').write_text(svg(geometry(name,i)))
    (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    sheet=Image.new('RGB',(1200,700),'#f5f8fc');d=ImageDraw.Draw(sheet);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
    d.text((32,22),'ICEGEM 4.0 / ROSEPINK',fill='#334f7b',font=font)
    for i,(name,_,_) in enumerate(NAMES):
        x=30+(i%6)*195;y=80+(i//6)*200
        d.rounded_rectangle((x,y,x+180,y+185),12,fill='white')
        sheet.paste(render(geometry(name),96),(x+42,y+10),render(geometry(name),96))
        d.text((x+10,y+115),name,fill='#334f7b',font=font)
        for j,bg in enumerate(['#ffffff','#152238','#b9c5ce']):
            tile=Image.new('RGBA',(40,40),bg);tile.alpha_composite(render(geometry(name),32),(4,4));sheet.paste(tile.convert('RGB'),(x+10+j*54,y+139))
    sheet.save(ROOT/'preview/IceGem-Overview.png')
    cards=[]
    for name,cn,slot in NAMES:
        frames=''.join(f'<span style="animation-delay:-{(FRAMES-i)*(5/60 if name=="normal" else 4/60):.6f}s">{svg_image(geometry(name,i))}</span>' for i in range(FRAMES)) if name in ('normal','working','busy') else svg_image(geometry(name))
        cards.append(f'<article><div class="large {"anim" if name in ("normal","working","busy") else ""}" style="--duration:{2 if name=="normal" else 1.6}s">{frames}</div><h3>{cn}</h3><small>{name} · {slot or "应用专用"}</small><div class="samples">'+''.join(f'<div style="background:{b}">{svg_image(geometry(name))}</div>' for b in ['white','#172638','#afb9c8'])+'</div></article>')
    html='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>IceGem 光标预览</title><style>body{margin:40px auto;max-width:1100px;padding:20px;background:#f3f6fa;color:#294261;font:16px system-ui}h1{font-weight:450}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px}article{padding:22px;background:white;border-radius:16px}h3{font-weight:500;margin:8px 0}small{color:#6a7c95}.large{height:96px;position:relative}.large img{width:80px;height:80px}.samples{display:flex;gap:8px;margin-top:18px}.samples img{width:32px;height:32px}.samples div{width:44px;height:44px;display:grid;place-items:center;border:1px solid #dce2eb}.anim span{position:absolute;opacity:0;animation:frame var(--duration) steps(1) infinite}@keyframes frame{0%{opacity:1}4.1666667%{opacity:0}100%{opacity:0}}@media(prefers-reduced-motion:reduce){.anim span{animation:none}.anim span:first-child{opacity:1}}</style><h1>IceGem · 玫瑰粉光标</h1><p>18 种状态 / 玫瑰粉切面 / 紧凑中心连接</p><p>上方放大展示，下方为 32px 实际尺寸。正常、后台忙碌、等待展示 24 帧流光动画。浏览器预览不代表 Windows 系统加载验证。</p><main>'+''.join(cards)+'</main></html>'
    (ROOT/'preview/IceGem-Preview.html').write_text(html)
if __name__=='__main__':build()
