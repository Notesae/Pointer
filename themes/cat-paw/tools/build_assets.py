#!/usr/bin/env python3
"""Build original, editable SVG assets. No generated bitmap is used as source."""
import json
import math
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
THEME = json.loads((ROOT / 'theme.json').read_text())
STATES = [('normal','Normal','正常'),('link','Link','链接'),('click','Click','按下'),('busy','Busy','忙碌'),('help','Help','帮助'),('text','Text','文本'),('precision','Precision','精准'),('move','Move','移动'),('resize-h','Resize H','水平缩放'),('resize-v','Resize V','垂直缩放'),('resize-d1','Resize D1','对角 ↖↘'),('resize-d2','Resize D2','对角 ↗↙'),('drag','Drag','拖动'),('disabled','Disabled','不可用')]
FUR = THEME['palette']['fur']
EDGE = THEME['palette']['outline']


def path(d, fill, stroke='none', sw=1, extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'


def group(body, transform='', extra=''):
    return f'<g transform="{transform}" {extra}>{body}</g>'


def ellipse(x,y,rx,ry,fill,extra=''):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" {extra}/>'


def print_mark(color):
    return ''.join(ellipse(x,y,rx,ry,color,f'transform="rotate({a} {x} {y})"') for x,y,rx,ry,a in [(15,23,6,8,-28),(26,14,6,8,-10),(40,14,6,8,12),(51,24,5.5,7.5,28)]) + path('M20 39 C20 34 26 30 32 30 C39 30 45 35 46 40 C49 49 41 52 35 49 C31 47 28 51 23 49 C17 47 16 42 20 39Z',color)


def paw(color, size=64, disabled=False):
    p = THEME['colorways'][color]
    pad = '#A8A1A0' if disabled else p['pad']
    light = '#CCC6C4' if disabled else p['padLight']
    contour = 'M10 29 C4 24 8 14 16 14 C14 4 24 1 30 8 C34 0 44 4 45 13 C55 9 61 20 55 28 C63 37 59 49 51 53 L49 57 L45 56 C39 63 25 63 19 57 L15 58 L14 54 C4 49 2 38 10 29Z'
    out = path(contour, FUR, '#A38A7E' if size>32 else EDGE, 1.5 if size>32 else 2.4)
    if size >= 48:
        out += path('M11 44 C17 54 24 57 33 57 C44 57 52 52 55 43 C54 53 46 61 32 60 C21 60 12 55 11 44Z','#EEE0D7')
        out += path('M12 31 L16 33 M49 34 L53 31 M18 50 L21 48 M44 50 L47 52','none','#DBCAC0',1.2)
    # Four toe beans and one large, softly lobed metacarpal pad.
    for x,y,rx,ry,a in [(15,26,5,6.4,-28),(26,17,5.3,7,-10),(40,17,5.3,7,12),(51,27,4.7,6.2,28)]:
        out += ellipse(x,y,rx,ry,pad,f'transform="rotate({a} {x} {y})"')
        if size >= 48:
            out += ellipse(x-1,y-2,1.8,2.3,light,'opacity=".85"')
    out += path('M21 39 C22 35 27 32 32 33 C37 29 45 34 46 39 C49 45 44 51 39 50 C34 49 33 52 28 52 C19 53 17 44 21 39Z',pad)
    if size >=48:
        out += path('M25 39 C27 36 31 36 33 37','none',light,2.2)
    return group(out, extra='opacity=".72"' if disabled else '')


def arrow(color, size=64):
    # Geometric hotspot is (6, 5) in the 64-unit source grid.
    sw = 2.6 if size<=32 else 2
    d='M6 5 L6 43 Q6 45 8 43 L17 35 L25 51 Q26 53 28 52 L34 49 Q35 48 34 46 L26 31 L40 31 Q43 31 40 29Z'
    out=path(d,FUR,EDGE,sw)
    if size>=48:
        out+=path('M10 12 L10 34','none','#FFFFFF',1.4)
    out+=group(print_mark(THEME['colorways'][color]['pad']),'translate(9 18) scale(.23)')
    # A small curved tail at the stem, omitted at 24/32 px for legibility.
    if size>=48:
        out+=path('M29 42 C36 40 39 46 35 49','none',EDGE,1.5)
    return out


def line(d,size):
    # Warm white inner stroke preserves visibility on dark surfaces.
    return path(d,'none',EDGE,5.7 if size<=32 else 4.5)+path(d,'none',FUR,2.5 if size<=32 else 2.2)


def cursor(state,color,size=64):
    if state in ('normal','link','click','drag'):
        return arrow(color,size)
    if state=='help':
        q=path('M43 15 C43 7 57 7 57 16 C57 21 50 21 50 27','none',EDGE,3.8)
        q+=ellipse(50,33,2,2,EDGE)
        return arrow(color,size)+q
    if state=='text':
        s=line('M25 14 L39 14 M32 14 L32 51 M25 51 L39 51',size)
        s+=path('M25 14 L24 8 L29 11 M35 11 L40 8 L39 14','none',EDGE,1.8 if size>32 else 2.5)
        if size>=48: s+=path('M38 51 C44 55 43 47 41 48','none',THEME['colorways'][color]['pad'],1.8)
        return s
    if state=='precision':
        s=line('M32 10 L32 25 M32 39 L32 54 M10 32 L25 32 M39 32 L54 32',size)
        s+=ellipse(32,32,1.5,1.5,EDGE)
        if size>=48: s+=path('M28 12 L32 9 L36 12','none',THEME['colorways'][color]['pad'],1.7)
        return s
    if state in ('move','resize-h','resize-v','resize-d1','resize-d2'):
        basic='M10 32 L54 32 M18 24 L10 32 L18 40 M46 24 L54 32 L46 40'
        s=line(basic,size)
        if state=='move': s+=group(line(basic,size),'rotate(90 32 32)')
        angle={'resize-v':90,'resize-d1':45,'resize-d2':-45}.get(state,0)
        s=group(s,f'rotate({angle} 32 32)')
        if size>=48: s+=group(print_mark(THEME['colorways'][color]['pad']),'translate(26 24) scale(.2)')
        else: s+=ellipse(32,32,2,2,THEME['colorways'][color]['pad'])
        return s
    if state=='disabled':
        s=f'<circle cx="32" cy="32" r="21" fill="{FUR}" stroke="#A8A1A0" stroke-width="3.5"/>'
        s+=group(print_mark('#BDB5B1'),'translate(15 14) scale(.5)')
        return s+path('M18 18 L46 46','none','#928884',4)
    if state=='busy':
        s=group(arrow(color,size),'translate(3 3) scale(.63)')
        for i in range(8):
            a=i*math.pi/4
            x,y=36+18*math.cos(a),35+18*math.sin(a)
            c=THEME['colorways']['pink' if i%2==0 else 'coffee']['pad']
            s+=group(print_mark(c),f'translate({x:.3f} {y:.3f}) rotate({i*45+90}) scale(.18) translate(-32 -32)',f'opacity="{.35+i*.08:.2f}"')
        return s
    raise ValueError(state)


def composition(state,color,size=64):
    s=cursor(state,color,size)
    # Technical cursors and busy deliberately do not gain a full paw.
    if state not in ('normal','link','click','help','drag','disabled'): return group(s,'translate(20 10)')
    x,y,scale,angle=62,41,.67,0
    if state=='link': y-=3; angle=-5
    if state=='click': x-=6; y-=3; scale*=.88
    if state=='drag': x-=4; angle=8
    s+=group(paw(color,size,state=='disabled'),f'translate({x} {y}) rotate({angle} 21 21) scale({scale})')
    if state=='click':
        s+=path('M56 36 L53 31 M79 32 L80 27 M95 44 L100 42','none',THEME['colorways'][color]['pad'],2.5)
    return s


def svg(body,width=64,height=None,viewbox='0 0 64 64',title='Cat Paw'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height or width}" viewBox="{viewbox}" role="img"><title>{escape(title)}</title>{body}</svg>\n'


def write(rel,body):
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(body)


def text(x,y,label,size=18,fill=EDGE,weight=400,extra=''):
    return f'<text x="{x}" y="{y}" font-family="Noto Sans CJK SC, DejaVu Sans, sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}" {extra}>{escape(label)}</text>'


def rect(x,y,w,h,fill,rx=0,stroke='none'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>'


def preview():
    W,H=1800,2040
    s=rect(0,0,W,H,'#FCF7F3')
    s+=text(70,63,'POINTER  /  THEME STUDY 02',16,weight=600)
    s+=text(70,137,'Cat Paw',62,weight=700)+text(72,187,'猫爪动态光标',29)
    s+=text(72,235,'准确的指针，软乎乎的陪伴。',23,'#A38476')
    s+=rect(73,264,206,36,'#EFE2DA',18)+text(92,288,'PHASE 01 · 视觉审核',15)
    s+=group(composition('normal','pink'),'translate(656 44) scale(2.85)')
    s+=group(composition('normal','coffee'),'translate(1066 44) scale(2.85)')
    s+=text(1460,120,'01 / POINTER',16,weight=600)+text(1460,155,'传统箭头 · 尖端定位',17)
    s+=text(1460,224,'02 / PAW',16,weight=600)+text(1460,259,'独立猫爪 · 四趾一垫',17)
    s+=path('M70 340 L1730 340','none','#E5D6CC',1)
    for section,(color,y) in enumerate([('pink',372),('coffee',889)]):
        p=THEME['colorways'][color]
        s+=ellipse(85,y+12,10,10,p['pad'])
        s+=text(108,y+21,p['name'],30,weight=600)
        s+=text(1718,y+18,'暖白猫毛  /  '+('樱花粉肉垫' if color=='pink' else '柔咖肉垫'),17,extra='text-anchor="end"')
        for i,(state,en,cn) in enumerate(STATES):
            x=70+(i%7)*239; cy=y+48+(i//7)*211
            s+=rect(x,cy,226,197,'#FFFCFA',18,'#EBDDD4')
            s+=group(composition(state,color),f'translate({x+47} {cy+13}) scale(1.2)')
            s+=text(x+16,cy+151,en,17,weight=600)+text(x+16,cy+177,cn,14,'#A08779')
    s+=path('M70 1393 L1730 1393','none','#E5D6CC',1)
    s+=text(70,1442,'小尺寸检查',28,weight=600)+text(295,1440,'实际像素 · 优先 32 / 48 px · 大小分别优化轮廓与细节',17,'#A08779')
    for k,color in enumerate(THEME['colorways']):
        y=1470+k*124
        s+=rect(70,y,795,109,'#FFFFFF',14,'#EBDDD4')+rect(886,y,844,109,'#332D2A',14)
        for j,size in enumerate(THEME['sizes']):
            x=90+j*129
            # The largest examples exceed the row: use separate size labels and cap shown sizes.
            if size>64: continue
            s+=group(cursor('normal',color,size),f'translate({x} {y+12}) scale({size/64})')
            s+=group(paw(color,size),f'translate({x+size+6} {y+15}) scale({size*.55/64})')
            s+=text(x,y+94,str(size)+'px',13)
            dx=910+j*160
            s+=group(cursor('normal',color,size),f'translate({dx} {y+12}) scale({size/64})')
            s+=group(paw(color,size),f'translate({dx+size+6} {y+15}) scale({size*.55/64})')
            s+=text(dx,y+94,str(size)+'px',13,'#E9D5C9')
        s+=text(657,y+40,'96 / 128 px',17,weight=600)+text(657,y+67,'另附独立 SVG',14,'#A08779')
    s+=text(70,1774,'动效关键姿态',27,weight=600)+text(295,1772,'静态设计目标；Companion 在视觉确认后开发',17,'#A08779')
    for i,(state,label,desc) in enumerate([('normal','FOLLOW','65 ms  /  16 px'),('link','HOVER','抬起 3 px  /  −5°'),('click','PRESS','0.88 → 1.05 → 1.0'),('drag','DRAG','靠近  /  旋转 8°'),('busy','BUSY','8 爪印  /  1000 ms')]):
        x=70+i*336
        s+=group(composition(state,'pink'),f'translate({x+4} 1790) scale(1.12)')
        s+=text(x+135,1836,label,16,weight=600)+text(x+135,1870,desc,14,'#A08779')
    s+=path('M70 1940 L1730 1940','none','#E5D6CC',1)
    s+=text(70,1983,'WARM WHITE  #FFF9F5    ·    PINK  #F4A6AE    ·    COFFEE  #9A6652',15)
    s+=text(1730,1983,'SVG ASSETS  /  v0.1  /  NOT AN INSTALLER',14,extra='text-anchor="end"')
    write('preview/Cat Paw Cursor Theme Preview.svg',svg(s,W,H,f'0 0 {W} {H}','Cat Paw Cursor Theme Preview — Pink and Coffee'))


def audit():
    s=rect(0,0,1400,640,'#FCF7F3')
    s+=text(20,29,'NATIVE PIXELS / 32 & 48 px / SYSTEM LAYER ONLY',18,weight=600)
    for row,(color,size) in enumerate([('pink',32),('pink',48),('coffee',32),('coffee',48)]):
        for col,(state,en,cn) in enumerate(STATES):
            x,y=col*100,row*145+45
            s+=text(x+5,y+18,f'{color} {size}',13)
            s+=group(cursor(state,color,size),f'translate({x+20} {y+30}) scale({size/64})')
            s+=text(x+5,y+112,state,12)
    write('preview/Native Size State Audit.svg',svg(s,1400,640,'0 0 1400 640','Native-size state audit'))


def main():
    manifest={'phase':'visual-review','coordinateSystem':'hotspots use output SVG pixels, rounded to integer; canonical 64x64 geometry','cursors':[],'compositions':[]}
    for color in THEME['colorways']:
        for size in THEME['sizes']:
            write(f'assets/paw-{color}/{size}/paw.svg',svg(paw(color,size),size,title=f'{color} paw {size}px'))
            write(f'assets/paw-{color}/{size}/disabled.svg',svg(paw(color,size,True),size,title=f'Disabled paw {size}px'))
            write(f'assets/pointer/{color}/{size}/arrow.svg',svg(arrow(color,size),size,title=f'{color} arrow {size}px'))
            for state,en,cn in STATES:
                rel=f'assets/states/{color}/{size}/{state}.svg'
                body=cursor(state,color,size)
                write(rel,svg(body,size,title=f'{en} · {color} · {size}px'))
                hx,hy=(6,5) if state in ('normal','link','click','help','drag') else ((6.78,6.15) if state=='busy' else (32,32))
                manifest['cursors'].append({'state':state,'color':color,'size':size,'file':rel,'hotspot':[round(hx*size/64),round(hy*size/64)]})
        for state,en,cn in STATES:
            rel=f'assets/source-svg/{color}/{state}.svg'
            write(rel,svg(composition(state,color),112,96,'0 0 112 96',f'{en} · {color} · two-layer composition reference'))
            manifest['compositions'].append({'state':state,'color':color,'file':rel,'purpose':'review only, not a system cursor'})
        write(f'assets/source-svg/paw-{color}.svg',svg(paw(color),title=f'{color} editable paw master'))
        write(f'assets/source-svg/pointer-{color}.svg',svg(arrow(color),title=f'{color} editable pointer master'))
    write('assets/manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    preview()
    audit()
    print(f"Built {len(manifest['cursors'])} cursor SVGs, 28 compositions, 6 sizes, {len(THEME['colorways'])} palettes.")

if __name__=='__main__': main()
