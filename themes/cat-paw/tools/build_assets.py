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
    detailed = size >= 48
    pad_id = 'gray' if disabled else color
    contour = ('M11 30 C4 27 6 17 13 15 C11 7 19 3 25 7 '
               'C29 1 38 3 40 10 C48 5 56 12 53 21 '
               'C61 24 59 33 55 37 C60 43 57 52 51 55 '
               'Q51 57 47 56 Q46 61 42 58 Q39 62 36 59 '
               'Q32 62 30 59 Q26 61 24 58 Q20 59 19 56 '
               'C13 54 9 49 10 45 Q6 44 8 41 C3 37 6 32 11 30Z')
    simple = ('M11 30 C4 27 6 17 13 15 C11 7 19 3 25 7 '
              'C29 1 38 3 40 10 C48 5 56 12 53 21 '
              'C61 24 59 33 55 37 C63 51 48 60 36 60 '
              'C20 62 7 53 9 42 C4 38 6 32 11 30Z')
    contour = contour if detailed else simple
    out = path(contour,'#CAB5A6','none',extra='transform="translate(.5 1)" opacity=".18"')
    out += path(contour,'url(#fur)','#C3ADA0' if detailed else '#9B8070',.95 if detailed else 1.8)
    if detailed:
        out += path('M13 39 C18 48 27 48 35 47 C44 45 52 40 55 36 C57 46 50 55 40 57 C28 62 15 52 13 39Z','url(#fluff)')
        # Short tapered locks build a soft wrist, without a photographic texture.
        for d in ['M12 37 Q15 39 13 44 Q17 43 18 49',
                  'M17 46 Q21 47 20 53 Q24 50 26 57',
                  'M25 49 Q29 52 28 57 Q33 54 35 59',
                  'M35 49 Q40 50 39 56 Q44 51 45 56',
                  'M45 44 Q50 44 49 51 Q54 46 54 43']:
            out += path(d,'none','#FFFCF8',1.5)
        if size >= 64:
            for i in range(17):
                a=math.radians(22+i*8)
                x=33+18*math.cos(a); y=38+15*math.sin(a)
                dx=2.3*math.cos(a); dy=4.3*math.sin(a)
                out+=path(f'M{x:.2f} {y:.2f} q{dx*.35:.2f} {dy*.6:.2f} {dx:.2f} {dy:.2f}',
                          'none','#FFFFFF',.55,extra='opacity=".72"')
        for d in ['M12 17 Q16 14 19 17','M19 8 Q22 7 24 10','M30 6 Q35 5 37 10','M44 12 Q49 10 51 16']:
            out += path(d,'none','#FFFFFF',1.2)
    for x,y,rx,ry,a in [(14,27,4.5,5.8,-26),(23,16,4.8,6.3,-17),(36,13,4.7,6.3,4),(48,23,4.1,5.4,24)]:
        out += ellipse(x,y+.8,rx+.45,ry+.3,'#D8BEB1','opacity=".23"')
        out += ellipse(x,y,rx,ry,f'url(#{pad_id}-pad)',f'transform="rotate({a} {x} {y})"')
        if detailed:
            out += ellipse(x-1.3,y-2,1.35,1.7,'#FFFFFF','opacity=".42"')
    bean='M22 37 C22 31 28 28 33 30 C39 26 47 30 47 36 C49 43 43 46 37 47 C31 53 23 53 20 47 C18 43 19 39 22 37Z'
    out += path(bean,'#DDB6A8','none',extra='transform="translate(.2 .8)" opacity=".25"')
    out += path(bean,f'url(#{pad_id}-pad)')
    if detailed:
        out += path('M25 37 Q26 34 29 34','none','#FFFFFF',1.5,extra='opacity=".5"')
        out += ellipse(33,33,.8,.7,'#FFFFFF','opacity=".5"')
    return group(out,'translate(2 1) scale(.94) rotate(-12 32 32)',extra='opacity=".76"' if disabled else '')


def arrow(color, size=64):
    # The visible tip / hotspot stays at (6, 5). Round the body, never the origin.
    d='M6 5 Q7 5 10 7 L43 30 Q48 34 43 37 L27 42 L13 52 Q8 56 8 49Z'
    out=path(d,'#B69A86','none',extra='transform="translate(1 1.5)" opacity=".16"')
    out+=path(d,'url(#pointer)', '#866B5B',1.45 if size>=48 else 2.2)
    if size>=48:
        out+=path('M10 12 L12 44 Q12 46 14 45','none','#FFFFFF',1.4)
        out+=path('M17 49 L29 40 L42 35','none','#DAC6B9',1.4)
    out+=group(print_mark(THEME['colorways'][color]['pad']),'translate(11 22) scale(.31) rotate(-12 32 32)')
    # Small ribbon and golden bell from the supplied reference, clear of the tip.
    if size>=32:
        out+=path('M29 41 Q25 37 28 36 Q31 35 33 40 Q34 35 37 38 Q38 41 33 43Z','#B9836B','#88604F',.7)
        out+=path('M32 42 L35 46','none','#796056',1.4)
        out+=ellipse(37,50,7.1,7.2,'#BCA18A','opacity=".15" transform="translate(.8 1)"')
        out+=ellipse(37,50,7.1,7.2,'url(#bell)','stroke="#A57948" stroke-width=".9"')
        out+=path('M33 46 Q35 43 38 45','none','#FFF3C7',1.8)
        out+=ellipse(38.2,52,1.4,1.4,'#9C6A3B')
        out+=path('M38.2 52 L39.3 55','none','#9C6A3B',.8)
    else:
        out+=ellipse(35,48,5,5,'#EDBE79','stroke="#9E7855" stroke-width="1.2"')
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
        d='M24 15 Q20 14 22 10 L22 6 Q24 4 28 9 L36 9 Q40 4 42 6 L42 10 Q44 14 40 15 L35 15 L35 49 L41 49 Q44 49 44 53 Q44 56 40 56 L24 56 Q20 56 20 53 Q20 49 24 49 L29 49 L29 15Z'
        out=path(d,'url(#pointer)',EDGE,1.5 if size>=48 else 2)
        out+=path('M24 8 L24 12 L28 11 M40 8 L40 12 L36 11',THEME['colorways'][color]['pad'])
        if size>=48:
            out+=path('M30 18 L30 46','none','#FFFFFF',1)
            out+=group(print_mark(THEME['colorways'][color]['pad']),'translate(46 42) scale(.19)')
        return out
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
    x,y,scale,angle=59,38,.77,0
    if state=='link': y-=3; angle=-5
    if state=='click': x-=6; y-=3; scale*=.88
    if state=='drag': x-=4; angle=8
    s+=group(paw(color,size,state=='disabled'),f'translate({x} {y}) rotate({angle} 21 21) scale({scale})')
    if state=='click':
        s+=path('M56 36 L53 31 M79 32 L80 27 M95 44 L100 42','none',THEME['colorways'][color]['pad'],2.5)
    return s


def gradients():
    defs='<defs>'
    for name,cx,cy,stops in [
        ('fur','.38','.22',[(0,'#FFFFFF'),(.65,'#FFF9F5'),(1,'#E9D9CD')]),
        ('fluff','.4','.2',[(0,'#FFFDF9'),(.6,'#FFF9F5'),(1,'#E7D7CC')]),
        ('pointer','.32','.22',[(0,'#FFFFFF'),(.7,'#FFF9F5'),(1,'#EFE1D7')]),
        ('bell','.28','.22',[(0,'#FFF0BF'),(.48,'#F7D491'),(1,'#D99C53')]),
        ('gray-pad','.3','.2',[(0,'#D9D2CD'),(.4,'#BDB4AE'),(1,'#9E938B')]),
    ]:
        defs+=f'<radialGradient id="{name}" cx="{cx}" cy="{cy}" r=".85">'
        defs+=''.join(f'<stop offset="{offset}" stop-color="{c}"/>' for offset,c in stops)+'</radialGradient>'
    for color,palette in THEME['colorways'].items():
        defs+=f'<radialGradient id="{color}-pad" cx=".28" cy=".2" r=".9">'
        defs+=f'<stop offset="0" stop-color="{palette["padLight"]}"/><stop offset=".46" stop-color="{palette["pad"]}"/><stop offset="1" stop-color="{palette["padEdge"]}"/></radialGradient>'
    return defs+'</defs>'


def svg(body,width=64,height=None,viewbox='0 0 64 64',title='Cat Paw'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height or width}" viewBox="{viewbox}" role="img"><title>{escape(title)}</title>{gradients()}{body}</svg>\n'


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
    s+=text(1730,1983,'SVG ASSETS  /  v0.2  /  NOT AN INSTALLER',14,extra='text-anchor="end"')
    write('preview/Cat Paw Cursor Theme Preview.svg',svg(s,W,H,f'0 0 {W} {H}','Cat Paw Cursor Theme Preview — Pink and Coffee'))


def detail_preview():
    W,H=1500,1060
    s=rect(0,0,W,H,'#FCF5EF')
    s+=group(print_mark('#F4B1B3'),'translate(58 43) scale(.65) rotate(-15 32 32)')
    s+=text(121,91,'猫爪光标',51,'#946F5E',700)
    s+=text(124,132,'把温柔的猫爪，带进你的每一次点击',20,'#A17D6A')
    s+=text(1430,81,'CAT PAW / 02',18,'#A17D6A',extra='text-anchor="end"')
    s+=text(1430,115,'造型修订 · 视觉待审核',17,'#A17D6A',extra='text-anchor="end"')
    for index,color in enumerate(THEME['colorways']):
        x=50+index*710
        s+=rect(x,173,690,525,'#FFF9F4',28,'#E8D3C5')
        s+=rect(x+22,195,235,48,'#A77E68',16)
        s+=text(x+44,229,'粉色猫爪' if color=='pink' else '咖啡猫爪',24,'#FFF9F5',600)
        s+=group(arrow(color,128),f'translate({x+65} 286) scale(3.15)')
        s+=group(paw(color,128),f'translate({x+345} 359) scale(3.7)')
        s+=text(x+57,608,'暖白箭头 · 小爪印 · 蝴蝶结铃铛',18,'#9B7764')
        s+=text(x+57,648,'指针与猫爪保持分离；装饰不改变尖端热点',17,'#B1917F')
    s+=rect(50,722,1400,248,'#FFF9F4',28,'#E8D3C5')
    s+=text(79,770,'细节与实际尺寸',24,'#946F5E',600)
    s+=group(paw('pink',128),'translate(83 805) scale(1.7)')
    s+=text(220,834,'四个小肉垫 + 一个大肉垫',18,'#946F5E')
    s+=text(220,867,'浅色毛尖 / 柔和阴影 / 轻微高光',17,'#A98977')
    s+=text(220,907,'24 / 32px 单独简化，48px 起保留层次',16,'#A98977')
    for j,size in enumerate([24,32,48,64]):
        x=664+j*184
        s+=group(arrow('pink',size),f'translate({x} 812) scale({size/64})')
        s+=group(paw('pink',size),f'translate({x+size+14} 825) scale({size/64})')
        s+=text(x,925,str(size)+' px',16,'#A98977')
    s+=text(53,1021,'可编辑 SVG 原生绘制  /  第一阶段：视觉资产',16,'#B1917F')
    s+=text(1448,1021,'尚未进入 Linux / Windows / Companion 开发',16,'#B1917F',extra='text-anchor="end"')
    write('preview/Cat Paw Detail Review.svg',svg(s,W,H,f'0 0 {W} {H}','Cat Paw revised shape and material review'))


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
    detail_preview()
    print(f"Built {len(manifest['cursors'])} cursor SVGs, 28 compositions, 6 sizes, {len(THEME['colorways'])} palettes.")

if __name__=='__main__': main()
