"""按已确认静置参考的局部坐标校准宝石；只生成静态审核图，不修改动画。"""
from pathlib import Path
import io
import cairosvg
import math
from PIL import ImageFilter
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
# 坐标来自设计稿静置局部的四倍观察图，保持台面偏心与冠部不等宽结构。
A, B, C, D = (16,16), (624,197), (966,713), (259,457)
TA, TB, TC, TD = (260,170), (604,252), (733,518), (347,391)
# 下侧圆角扩大到可辨识的抛光转折，外缘、厚度带和亮棱共享轮廓。
# 每个角分别指定入边/出边过渡长度；左下肩宽缓转向，右下尖端沿下边渐收。
CORNER_TRIMS = ((54,58), (64,72), (88,122), (104,126))


def polished_outline(inset=0, table=False):
    """以相切二次圆角连接轻微弯曲的长边；内侧亮棱复用同一几何，避免拐角断开。"""
    # 尖端处内缩量降为肩部的 18%，厚边沿长边渐收，避免形成厚重包头。
    vertices=[]
    for i,(x,y) in enumerate((TA,TB,TC,TD) if table else (A,B,C,D)):
        local_inset=inset*(.18 if not table and i in (0,2) else 1)
        vertices.append((x+(490-x)*local_inset/500,y+(365-y)*local_inset/500))
    # 台面独立控制圆角与轻微边线弧度，填充和高光必须共用同一路径。
    trims=((20,20),(15,15),(24,24),(17,17)) if table else CORNER_TRIMS
    entry,exit_points=[],[]
    for i,(x,y) in enumerate(vertices):
        for side,(neighbor,target) in enumerate([(vertices[(i-1)%4],entry),(vertices[(i+1)%4],exit_points)]):
            length=math.hypot(neighbor[0]-x,neighbor[1]-y)
            amount=trims[i][side]/length
            target.append((x+(neighbor[0]-x)*amount,y+(neighbor[1]-y)*amount))
    # 先计算长边控制点，再用同一切线连接圆角，消除弧段接缝的小折点。
    edge_controls=[]
    for i in range(4):
        sx,sy=exit_points[i]
        ex,ey=entry[(i+1)%4]
        dx,dy=ex-sx,ey-sy
        length=math.hypot(dx,dy)
        bow=((1,1.5,2,1.5) if table else (6,12,19,14))[i]
        nx,ny=dy/length*bow,-dx/length*bow
        edge_controls.append(((sx+dx/3+nx,sy+dy/3+ny),(sx+dx*2/3+nx,sy+dy*2/3+ny)))
    path=[f'M {entry[0][0]} {entry[0][1]}']
    for i in range(4):
        x,y=vertices[i]
        sx,sy=exit_points[i]
        ex,ey=entry[(i+1)%4]
        if table:
            path.append(f'Q {x} {y} {sx} {sy}')
        else:
            # 两端控制柄沿相邻长边的切线，圆角弧度和边缘反射连续转向。
            px,py=entry[i]
            incoming=edge_controls[(i-1)%4][1]
            outgoing=edge_controls[i][0]
            ux,uy=px-incoming[0],py-incoming[1]
            vx,vy=outgoing[0]-sx,outgoing[1]-sy
            ilen,olen=math.hypot(ux,uy),math.hypot(vx,vy)
            h1,h2=trims[i][0]*.62,trims[i][1]*.62
            path.append(f'C {px+ux/ilen*h1} {py+uy/ilen*h1} {sx-vx/olen*h2} {sy-vy/olen*h2} {sx} {sy}')
        c1,c2=edge_controls[i]
        path.append(f'C {c1[0]} {c1[1]} {c2[0]} {c2[1]} {ex} {ey}')
    return ' '.join(path)+' Z'


OUTLINE = polished_outline()
# 台面仍为一个连续平面，四角和边缘高光统一跟随抛光圆弧。
TABLE = polished_outline(table=True)


def points(vertices):
    return ' '.join(f'{x},{y}' for x,y in vertices)



def reference_gradient(vertices, name, exposure=0):
    """拟合参考切面的连续色阶，并按冠面朝向适度调整曝光；台面默认不调整。"""
    source = Image.open(ROOT/'docs/shape-approved.png').convert('RGB').crop((690,166,936,350)).resize((984,736),Image.Resampling.BICUBIC)
    mask = Image.new('L',source.size)
    ImageDraw.Draw(mask).polygon(vertices,fill=255)
    mask = mask.filter(ImageFilter.MinFilter(9))
    # 固定网格采样切面内部，使用三元最小二乘拟合 RGB，保持工具仅依赖 Pillow/CairoSVG。
    samples=[(x,y,source.getpixel((x,y))) for y in range(0,736,5) for x in range(0,984,5) if mask.getpixel((x,y))]
    # 极窄切面无法稳定拟合二维梯度时，用面中心参考色保持连续实面。
    if len(samples)<8 or len({v[0] for v in samples})<3 or len({v[1] for v in samples})<3:
        center=tuple(round(sum(v[axis] for v in vertices)/len(vertices)) for axis in (0,1))
        color=source.getpixel(center)
        # 亮面向冰白靠近，暗面按比例压低，保留参考色相。
        color=tuple(round(c+(255-c)*exposure if exposure>=0 else c*(1+exposure)) for c in color)
        return f'<linearGradient id="{name}"><stop stop-color="rgb{color}"/><stop offset="1" stop-color="rgb{color}"/></linearGradient>'
    cx=sum(v[0] for v in samples)/len(samples)
    cy=sum(v[1] for v in samples)/len(samples)
    rows=[([x-cx,y-cy,1],rgb) for x,y,rgb in samples]
    coefficients=[]
    for channel in range(3):
        matrix=[[sum(row[i]*row[j] for row,rgb in rows) for j in range(3)]+[sum(row[i]*rgb[channel] for row,rgb in rows)] for i in range(3)]
        for pivot in range(3):
            largest=max(range(pivot,3),key=lambda r:abs(matrix[r][pivot]))
            matrix[pivot],matrix[largest]=matrix[largest],matrix[pivot]
            # 窄面的样本可能共线，微小正则项避免奇异矩阵放大数值误差。
            scale=matrix[pivot][pivot]
            if abs(scale)<1e-8:
                scale=1e-8
                matrix[pivot][pivot]=scale
            matrix[pivot]=[v/scale for v in matrix[pivot]]
            for r in range(3):
                if r!=pivot:
                    factor=matrix[r][pivot]
                    matrix[r]=[v-factor*w for v,w in zip(matrix[r],matrix[pivot])]
        coefficients.append([matrix[i][3] for i in range(3)])
    xx=sum(c[0]**2 for c in coefficients)
    yy=sum(c[1]**2 for c in coefficients)
    cross=sum(c[0]*c[1] for c in coefficients)
    angle=.5*math.atan2(2*cross,xx-yy)
    dx,dy=math.cos(angle),math.sin(angle)
    extent=[(x-cx)*dx+(y-cy)*dy for x,y in vertices]
    start=(cx+dx*min(extent),cy+dy*min(extent))
    end=(cx+dx*max(extent),cy+dy*max(extent))
    stops=[]
    for offset in (0,.5,1):
        x=start[0]+(end[0]-start[0])*offset
        y=start[1]+(end[1]-start[1])*offset
        color=[max(0,min(255,round(c[0]*(x-cx)+c[1]*(y-cy)+c[2]))) for c in coefficients]
        # 分面曝光只改变面内亮度，边界由几何形成，不增加描边。
        color=[round(c+(255-c)*exposure if exposure>=0 else c*(1+exposure)) for c in color]
        stops.append(f'<stop offset="{offset}" stop-color="rgb({color[0]},{color[1]},{color[2]})"/>')
    return f'<linearGradient id="{name}" gradientUnits="userSpaceOnUse" x1="{start[0]}" y1="{start[1]}" x2="{end[0]}" y2="{end[1]}">{"".join(stops)}</linearGradient>'



def document():
    """用固定平整台面和按参考逐块定位的外围反射面重建静态宝石。"""
    # 每项是独立冠部平面及其端点色；亮暗交界用面本身形成，不叠一圈白线。
    faces = [
        ([A,B,TB,TA], '#afd5ee','#eaf8ff'),
        ([A,(410,147),TA], '#84b5d7','#b8d9ed'),
        ([A,TA,(307,288)], '#ffffff','#effbff'),
        ([(410,147),(452,134),TB,TA], '#f5fcff','#c3e5f5'),
        ([(452,134),B,(552,214)], '#3d82b4','#90bddc'),
        ([(552,214),B,TB], '#6d9fc3','#d3eafb'),
        ([B,C,TC,TB], '#367fb6','#94c4ea'),
        ([B,(786,437),TB], '#164f85','#528bb8'),
        ([TB,(658,342),(786,437)], '#3b7ba9','#9ed0e8'),
        ([(658,342),TC,(786,437)], '#eafaff','#f9feff'),
        ([(786,437),(824,575),TC], '#a6d5ed','#e2f4fc'),
        ([(786,437),C,(824,575)], '#2e6caa','#83b4e1'),
        ([TC,(824,575),C,(778,654)], '#536cab','#183e81'),
        ([D,TD,TC,C], '#397eaf','#b4c9e8'),
        # 左下暗冠面拆为两块共边切面，避免整块黑三角贴着圆肩。
        ([D,TD,(342,438)], '#103f76','#22649c'),
        ([D,(342,438),(339,471)], '#285f91','#568aba'),
        ([TD,(501,461),(339,471)], '#377eac','#1e649a'),
        # 下冠部共用一个折射节点，三面汇聚，不新增跨过台面的棱线。
        ([(339,471),(501,461),(510,520)], '#4c92bd','#91bbdb'),
        ([(501,461),(628,602),(510,520)], '#5a9fc8','#bcdef1'),
        ([(628,602),(339,471),(510,520)], '#548ab8','#a4cce6'),
        ([(501,461),TC,(628,602)], '#93c1df','#edf9ff'),
        ([(628,602),TC,(778,654)], '#fcffff','#cad7f6'),
        # 右下暗面分成宽主面和窄回光面，尖端不堆叠细碎三角。
        ([(778,654),TC,(862,677)], '#4e61a5','#7186c4'),
        ([TC,C,(862,677)], '#375b9a','#8da9dc'),
        ([D,(339,471),(628,602),(648,628)], '#5a96be','#80b7dc'),
        ([A,TA,TD,D], '#286c9e','#8fcae7'),
        ([A,(113,175),(227,221)], '#144b81','#6db5db'),
        ([A,(227,221),TA], '#548fbe','#9dc9e7'),
        ([(113,175),(182,309),(227,221)], '#3b86b7','#8dc6e4'),
        ([(227,221),TD,(231,309)], '#3e83b2','#77b5d7'),
        ([(182,309),(231,309),D], '#effaff','#c4e9f7'),
        ([(231,309),TD,D], '#76b8da','#b1ddee'),
    ]
    # 指定外围主面的内部折射节点；只细分这些面，避免均匀三角网格侵入台面。
    facet_indices = {4,7,8,9,10,11,16,17,18,19,20,21,22,23,26,27,28,29,31}
    # 每组依原顶点顺序定义亮/灰/暗反射：下冠部和右侧反差较强，顶部较克制。
    facet_exposure = {
        4:(.08,-.08,.03), 7:(-.16,.08,-.04), 8:(.12,-.10,.04),
        9:(.03,-.07,.16), 10:(.16,-.12,.05), 11:(-.18,.13,-.06),
        16:(-.13,.12,-.04), 17:(.10,-.14,.03), 18:(-.08,.15,-.04),
        19:(-.12,.09,-.02), 20:(.17,-.14,.05), 21:(.06,-.13,.19),
        22:(-.16,.14,-.05), 23:(-.12,.11,-.03), 26:(-.12,.07,-.02),
        27:(.05,-.06,.02), 28:(.09,-.12,.02), 29:(-.09,.13,-.03),
        31:(.13,-.10,.04),
    }
    refined=[]
    for index,(vertices,start,end) in enumerate(faces):
        if index not in facet_indices:
            refined.append((vertices,start,end,0))
            continue
        # 共用中心与原边界构成扇形分面，不改变邻面接缝或冠部总面积。
        node=tuple(sum(v[axis] for v in vertices)/len(vertices) for axis in (0,1))
        for edge,vertex in enumerate(vertices):
            refined.append(([vertex,vertices[(edge+1)%len(vertices)],node],start,end,facet_exposure[index][edge]))
    faces=refined
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="984" height="736" viewBox="0 0 984 736">']
    parts.append(f'<defs><clipPath id="bodyClip"><path d="{OUTLINE}"/></clipPath></defs><g clip-path="url(#bodyClip)">')
    parts.append(f'<path d="{OUTLINE}" fill="#6d9fc6"/>')
    for i,(vertices,start,end,exposure) in enumerate(faces):
        parts.append(f'<defs>{reference_gradient(vertices, "f"+str(i), exposure)}</defs><polygon points="{points(vertices)}" fill="url(#f{i})"/>')
    # 顶部亮冠面的宽度和取色以参考为准，不再覆盖为纯白三角形。
    top=[A,TA,(307,288)]
    parts.append(f'<defs>{reference_gradient(top,"topPolish")}</defs><polygon points="{points(top)}" fill="url(#topPolish)"/>')
    # 中央台面单独覆盖，禁止任何冠部面或切线穿过；轻柔渐变仍属于同一平面。
    parts.append(f'<defs>{reference_gradient([TA,TB,TC,TD],"table")}</defs>')
    # 倒角底层覆盖旧台面顶点，避免圆角收回后暴露出暗色三角尖刺。
    parts.append(f'<polygon points="{points([TA,TB,TC,TD])}" fill="#dceffc"/>')
    parts.append(f'<path d="{TABLE}" fill="url(#table)" stroke="#d9f4ff" stroke-width="3"/>')
    # 台面只添加连续的宽反光，没有新切线；亮斑裁剪在同一抛光平面内。
    parts.append(f'<defs><clipPath id="flatTable"><path d="{TABLE}"/></clipPath><radialGradient id="tableSheen" cx="58%" cy="62%" r="65%"><stop stop-color="#e4f7ff" stop-opacity=".10"/><stop offset=".65" stop-color="#d2eeff" stop-opacity=".09"/><stop offset="1" stop-color="#d2eeff" stop-opacity="0"/></radialGradient></defs><path d="{TABLE}" fill="url(#tableSheen)"/>')
    # 右侧窄面上的弯曲反光保持边缘纵深，光带不跨越台面。
    parts.append('<defs><linearGradient id="sideReflection" x1="0%" y1="0%" x2="100%" y2="100%"><stop stop-color="#c2e8fc" stop-opacity=".08"/><stop offset=".6" stop-color="#e3f6ff" stop-opacity=".25"/><stop offset="1" stop-color="#799fdd" stop-opacity=".1"/></linearGradient></defs><path d="M 644 240 C 707 335 777 438 846 551 L 827 536 C 750 418 694 332 635 239 Z" fill="url(#sideReflection)"/>')
    # 明亮台面下沿、上沿和外部窄腰棱分开处理，保留有方向的抛光反射。
    # 移除直线叠加的尖锐端头，用连续渐变边沿贴合台面圆角。
    parts.append('<defs><linearGradient id="tableRim" x1="0%" y1="0%" x2="100%" y2="100%"><stop stop-color="#effaff"/><stop offset=".38" stop-color="#bddff3"/><stop offset=".8" stop-color="#f5fdff"/><stop offset="1" stop-color="#d7eefe"/></linearGradient></defs>')
    parts.append(f'<path d="{TABLE}" fill="none" stroke="url(#tableRim)" stroke-width="4"/>')
    # 宽而淡的抛光带跨越外围切面，向内逐层消退，保留清楚的切面交界。
    parts.append('<defs><linearGradient id="crownPolish" gradientUnits="userSpaceOnUse" x1="200" y1="80" x2="800" y2="720"><stop stop-color="#f0fbff"/><stop offset=".32" stop-color="#c5eaff"/><stop offset=".55" stop-color="#f0fbff"/><stop offset=".78" stop-color="#84b2de"/><stop offset="1" stop-color="#d9eaff"/></linearGradient></defs>')
    for width,opacity in [(58,.035),(44,.045),(30,.055),(18,.065)]:
        parts.append(f'<path d="{OUTLINE}" fill="none" stroke="url(#crownPolish)" stroke-width="{width}" opacity="{opacity}"/>')
    # 实体腰棱由外轮廓与内缩轮廓围成窄带，填充面宽产生厚度，而非放大描边。
    side_inner=polished_outline(26)
    bevel_inner=polished_outline(17)
    parts.append('<defs><linearGradient id="girdleSide" gradientUnits="userSpaceOnUse" x1="120" y1="80" x2="780" y2="690"><stop stop-color="#8fbadc"/><stop offset=".30" stop-color="#547faa"/><stop offset=".56" stop-color="#294f83"/><stop offset=".82" stop-color="#3a588c"/><stop offset="1" stop-color="#253e75"/></linearGradient><linearGradient id="girdleBevel" gradientUnits="userSpaceOnUse" x1="90" y1="40" x2="810" y2="690"><stop stop-color="#e8f8ff"/><stop offset=".38" stop-color="#a6cbe9"/><stop offset=".6" stop-color="#d5ebfc"/><stop offset="1" stop-color="#779dcf"/></linearGradient></defs>')
    parts.append(f'<path d="{OUTLINE} {side_inner}" fill="url(#girdleSide)" fill-rule="evenodd"/>')
    # 内层倒角覆盖腰棱的上沿，形成亮、灰、暗三个层次并沿圆角连续转折。
    parts.append(f'<path d="{bevel_inner} {side_inner}" fill="url(#girdleBevel)" fill-rule="evenodd"/>')
    parts.append(f'<path d="{OUTLINE}" fill="none" stroke="#426795" stroke-width="1.6" opacity=".8"/>')
    # 亮棱在两端柔和消退，避免多条亮线挤成突兀的小环，侧面中段维持原强度。
    parts.append('<defs><linearGradient id="tipRim" gradientUnits="userSpaceOnUse" x1="16" y1="16" x2="966" y2="713"><stop stop-color="#d9efff" stop-opacity=".12"/><stop offset=".14" stop-color="#d9efff"/><stop offset=".86" stop-color="#d9efff"/><stop offset="1" stop-color="#d9efff" stop-opacity=".12"/></linearGradient></defs>')
    parts.append(f'<path d="{side_inner}" fill="none" stroke="url(#tipRim)" stroke-width="2.6" opacity=".85"/>')
    parts.append(f'<path d="{polished_outline(6)}" fill="none" stroke="url(#tipRim)" stroke-width="1.4" opacity=".38"/>')
    parts.append('</g></svg>')
    return ''.join(parts)


def build():
    """生成同尺寸原稿对照与输出像素检查，并保存可编辑 SVG。"""
    out=ROOT/'preview'
    svg=document()
    (out/'static-study-14.svg').write_text(svg,encoding='utf-8')
    original=Image.open(ROOT/'docs/shape-approved.png').convert('RGB').crop((690,166,936,350))
    render=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),output_width=984,output_height=736))).convert('RGBA')
    sheet=Image.new('RGB',(1120,650),'#f1f6fb')
    d=ImageDraw.Draw(sheet)
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
    small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
    d.text((24,15),'Crystal · 静态校准 14 / 同比例对照',font=font,fill='#263e63')
    for x,title in [(24,'已确认设计稿 · 原图局部'),(580,'本轮校准 · 连续圆弧与抛光外缘')]:
        d.text((x,65),title,font=small,fill='#263e63')
    sheet.paste(original.resize((492,368),Image.Resampling.LANCZOS),(24,102))
    im=render.resize((492,368),Image.Resampling.LANCZOS)
    sheet.paste(im,(580,102),im)
    d.rectangle((580,485,1095,634),fill='#172638')
    for size,x in [(32,620),(48,710),(64,810),(96,925)]:
        # 正方形光标画布保持原比例居中，不拉伸宝石。
        im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),output_width=size,output_height=size))).convert('RGBA')
        sheet.paste(im,(x,504),im)
        d.text((x,609),str(size)+'px',font=small,fill='#e0edff')
    d.text((24,510),'统一圆角切线，外缘反光向内柔和过渡。',font=small,fill='#263e63')
    d.text((24,545),'保留圆润厚边和完整平整台面。',font=small,fill='#263e63')
    d.text((24,580),'静态审核稿，尚未替换动画。',font=small,fill='#263e63')
    sheet.save(out/'static-study-14.png')
    # 局部对照统一坐标与倍率，便于比较肩角、下冠面和尖端的轮廓变化。
    detail=Image.new('RGB',(1120,820),'#f1f6fb')
    labels=ImageDraw.Draw(detail)
    previous=Image.open(io.BytesIO(cairosvg.svg2png(url=str(out/'static-study-13.svg'),output_width=984,output_height=736))).convert('RGBA')
    sources=[('设计参考',original.resize((984,736),Image.Resampling.BICUBIC)),('第13轮',previous),('第14轮',render)]
    regions=[('左下肩角',(190,330,460,550)),('下侧切面',(390,430,780,670)),('右下尖端',(710,480,984,736))]
    for column,(title,box) in enumerate(regions):
        x=110+column*335
        labels.text((x,15),title,font=font,fill='#263e63')
        for row,(label,source) in enumerate(sources):
            y=60+row*250
            if column==0:
                labels.text((12,y+90),label,font=small,fill='#263e63')
            crop=source.crop(box)
            crop.thumbnail((315,230),Image.Resampling.LANCZOS)
            detail.paste(crop,(x,y),crop if crop.mode=='RGBA' else None)
    detail.save(out/'lower-facets-study-14.png')
    print('Static trace comparison ready.')


if __name__ == '__main__':
    build()
