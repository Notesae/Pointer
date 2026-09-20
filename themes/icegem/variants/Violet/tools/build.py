from pathlib import Path
import math, struct, json, io, base64
from PIL import Image, ImageDraw, ImageFont
import cairosvg
from functools import lru_cache

ROOT=Path(__file__).resolve().parents[1]
SIZES=(32,48,64)
# 每个角色分别定义 ANI 的 1/60 秒帧时长；静止停留帧避免反复扫光。
ANIMATIONS={
    'normal': (1,)*96+(96,),
    'working': (1,)*96,
    'busy': (2,)*36,
    'link': (1,)*96+(24,),
    'help': (1,)*144,
    'location': (1,)*144,
    'person': (1,)*144,
    # 展台文本动画为 75 帧 / 3 秒；累计取整到 ANI jiffy，帧误差不累积。
    **{name:tuple(round((i+1)*180/75)-round(i*180/75) for i in range(75))
       for name in ('text','vertical-text')},
    **{name:(3,)*36 for name in ('move','resize-ew','resize-ns','resize-nwse','resize-nesw')},
}
ROTATION_AMPLITUDES={
    'normal':6, 'working':8, 'link':14, 'help':9, 'location':10, 'person':10,
    'move':8, 'resize-ew':4, 'resize-ns':4, 'resize-nwse':4, 'resize-nesw':4,
}
THEME_SHIFT=55
THEME_NAME='紫罗兰'
NAMES=[('normal','正常选择','Arrow'),('working','后台忙碌','AppStarting'),('busy','忙碌 / 等待','Wait'),('help','帮助选择','Help'),('link','链接选择','Hand'),('unavailable','不可用','No'),('text','文本选择','IBeam'),('vertical-text','竖排文本选择',''),('precision','精准选择','Crosshair'),('resize-nwse','对角调整 ↖↘','SizeNWSE'),('resize-nesw','对角调整 ↗↙','SizeNESW'),('resize-ew','水平调整','SizeWE'),('resize-ns','垂直调整','SizeNS'),('move','移动','SizeAll'),('alternate','替代选择','UpArrow'),('handwriting','手写','NWPen'),('location','位置选择','Pin'),('person','人员选择','Person')]
OUTLINE='#334f7b'; BLUE='#9bdcff'; LIGHT='#edfaff'; MID='#70bce7'; LILAC='#d3d1fa'
def motion_phase(name,frame):
    """统一摆动与自转时钟；带停留动作使用两端速度、加速度归零的五次缓动。"""
    rates=ANIMATIONS.get(name,(1,))
    index=frame%len(rates)
    if name in ('normal','link'):
        if index==len(rates)-1:return 0.
        progress=index/(len(rates)-1)
        return progress**3*(10-15*progress+6*progress**2)
    return index/len(rates)

def text_pedestal_svg(frame, vertical=False):
    """以固定六角晶台和棱柱承托浮动晶石，上端叠加纵轴自转与中心倾摆。"""
    # 每轮 75 帧、3 秒；归一化索引保证跨周期首帧完全一致。
    frame %= len(ANIMATIONS['text'])
    phase = frame / len(ANIMATIONS['text']) * math.tau
    # 平滑周期运动只作用于上端；中心热点所在支撑柱与底座始终固定。
    lift = -.7 * math.sin(phase)
    tilt = 7 * math.sin(phase + .6)
    # 同一组透色材质用于台面、倒角与棱柱；各切面的明暗随朝向而非宽幅白带变化。
    stand = theme_svg('''<defs>
      <linearGradient id="ice" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#e7fbff" stop-opacity=".82"/><stop offset=".45" stop-color="#a6d9ef" stop-opacity=".38"/><stop offset="1" stop-color="#6395cd" stop-opacity=".64"/></linearGradient>
      <linearGradient id="lilac" x1="0" y1="1" x2="1" y2="0"><stop stop-color="#6878b6" stop-opacity=".7"/><stop offset=".55" stop-color="#bbc7ed" stop-opacity=".32"/><stop offset="1" stop-color="#e7eaff" stop-opacity=".72"/></linearGradient>
      <linearGradient id="refract" x1="0" y1="0" x2="1" y2=".8"><stop stop-color="#7bb9e1" stop-opacity=".16"/><stop offset=".48" stop-color="#ecffff" stop-opacity=".82"/><stop offset=".53" stop-color="#9cd2e9" stop-opacity=".27"/><stop offset="1" stop-color="#a1a5e0" stop-opacity=".48"/></linearGradient>
      <!-- 固定左上光源：各表面独立明暗，底缘压暗，柱身使用连续色阶表现透光深度。 -->
      <linearGradient id="tableLight" x1="0" y1="0" x2=".8" y2="1"><stop stop-color="#ecffff" stop-opacity=".9"/><stop offset=".58" stop-color="#b6e0f4" stop-opacity=".62"/><stop offset="1" stop-color="#86a7d1" stop-opacity=".65"/></linearGradient>
      <linearGradient id="frontLight" x1="0" y1="0" x2=".25" y2="1"><stop stop-color="#d7f7ff" stop-opacity=".88"/><stop offset=".3" stop-color="#94c4e5" stop-opacity=".66"/><stop offset="1" stop-color="#496d9e" stop-opacity=".78"/></linearGradient>
      <linearGradient id="rightShade" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#84a9d5" stop-opacity=".7"/><stop offset=".65" stop-color="#46689b" stop-opacity=".8"/><stop offset="1" stop-color="#797bb7" stop-opacity=".66"/></linearGradient>
      <linearGradient id="columnLight" x1="0" y1="0" x2=".8" y2="1"><stop stop-color="#d2f5ff" stop-opacity=".84"/><stop offset=".3" stop-color="#8bbbe0" stop-opacity=".5"/><stop offset=".62" stop-color="#e4faff" stop-opacity=".9"/><stop offset="1" stop-color="#88a9d4" stop-opacity=".72"/></linearGradient>
      <linearGradient id="columnShade" x1="0" y1="0" x2=".7" y2="1"><stop stop-color="#5378a8" stop-opacity=".78"/><stop offset=".45" stop-color="#a3b8e0" stop-opacity=".5"/><stop offset="1" stop-color="#4b699c" stop-opacity=".8"/></linearGradient>
      </defs>
      <!-- 仅保留外壳与互不重叠的表面切面，去掉内部骨架和交叉光带产生的杂质重影。 -->
      <!-- 底座在上版基础上再缩小 15%，累计为原尺寸的 72.25%，固定柱脚连接点。 -->
      <g transform="translate(16 25) scale(.7225) translate(-16 -25)">
      <path d="M10 25 L13 23.8 L19 23.8 L22 25 L22 27.1 L19.4 28.5 L12.6 28.5 L10 27.1 Z" fill="#aed9ed" fill-opacity=".25"/>
      <!-- 台面仅通过大块透色切面表现折射，不叠加柱脚或内部零件形状。 -->
      <path d="M10 25 L13 23.8 L15.6 25.6 L13 26.4 Z" fill="url(#tableLight)"/>
      <path d="M13 23.8 L19 23.8 L15.6 25.6 Z" fill="#d8f6ff" fill-opacity=".68"/>
      <path d="M19 23.8 L22 25 L19 26.4 L15.6 25.6 Z" fill="url(#lilac)"/>
      <path d="M13 26.4 L15.6 25.6 L19 26.4 Z" fill="#82b6da" fill-opacity=".6"/>
      <path d="M10 25 L13 26.4 L12.6 28.5 L10 27.1 Z" fill="url(#frontLight)"/>
      <path d="M13 26.4 L19 26.4 L16.8 27.45 L12.6 28.5 Z" fill="url(#frontLight)"/>
      <path d="M19 26.4 L19.4 28.5 L12.6 28.5 L16.8 27.45 Z" fill="url(#rightShade)"/>
      <path d="M19 26.4 L22 25 L22 27.1 L19.4 28.5 Z" fill="url(#rightShade)"/>
      <path d="M10 25 L13 23.8 L19 23.8 L22 25 L22 27.1 L19.4 28.5 L12.6 28.5 L10 27.1 Z" fill="none" stroke="#476d99" stroke-opacity=".72" stroke-width=".25"/>
      <path d="M10.2 25 L13.1 23.95 L18.8 23.95 M10.15 25.1 L13 26.4 L19 26.4 L21.85 25.1 M12.8 28.25 L19.3 28.25" fill="none" stroke="#efffff" stroke-opacity=".87" stroke-width=".2"/>
      <path d="M13 26.4 L12.6 28.3 M19 26.4 L19.4 28.3" fill="none" stroke="#b4d9f6" stroke-width=".16"/>
      <!-- 柱体直接连接台面，连续纵向切面代替内部三角碎片与独立底脚。 -->
      </g>
      <path d="M15.05 14.5 L16 14.1 L16.95 14.5 L17.1 24.4 L16 25 L14.9 24.4 Z" fill="#b0ddef" fill-opacity=".35"/>
      <path d="M15.05 14.5 L15.5 14.75 L15.65 24.65 L14.9 24.4 Z" fill="#648bb9" fill-opacity=".7"/>
      <path d="M15.5 14.75 L16 14.1 L16 25 L15.65 24.65 Z" fill="url(#columnLight)"/>
      <path d="M16 14.1 L16.95 14.5 L16.45 24.7 L16 25 Z" fill="url(#columnShade)"/>
      <path d="M16.95 14.5 L17.1 24.4 L16.45 24.7 Z" fill="#5679ad" fill-opacity=".62"/>
      <path d="M15.05 14.5 L16 14.1 L16.95 14.5 L17.1 24.4 L16 25 L14.9 24.4 Z" fill="none" stroke="#6383ac" stroke-opacity=".68" stroke-width=".19"/>
      <path d="M15.12 14.7 L14.99 24.2 M15.55 14.9 L15.68 24.5" fill="none" stroke="#f0ffff" stroke-opacity=".9" stroke-width=".14"/>
      <!-- 柱顶承托台与底座共享透明斜面，保持材料连续。 -->
      <path d="M13.9 14.2 L16 13.55 L18.1 14.2 L17.6 15.05 L16 15.5 L14.4 15.05 Z" fill="url(#lilac)" stroke="#6383ab" stroke-width=".2"/>
      <path d="M13.9 14.2 L16 13.55 L16.25 14.6 L16 14.9 Z" fill="url(#ice)"/>
      <path d="M16 13.55 L18.1 14.2 L16 14.9 L16.25 14.6 Z" fill="url(#refract)"/>
      <path d="M14.15 14.3 L16 14.9 L17.85 14.3 M14.45 15 L16 15.35" fill="none" stroke="#efffff" stroke-opacity=".8" stroke-width=".16"/>''')
    # 柔和反光仅落在现有表面，以连续透明度变化呼应晶石运动，不添加内部物体或交叉光带。
    reflection = .1 + .1 * (.5 + .5 * math.sin(phase - .4))
    stand += theme_svg(f'''<defs>
      <linearGradient id="surfaceReflection" x1="0" y1="0" x2=".8" y2="1"><stop stop-color="#f0ffff" stop-opacity=".8"/><stop offset=".55" stop-color="#c8eeff" stop-opacity=".18"/><stop offset="1" stop-color="#b4c4ef" stop-opacity="0"/></linearGradient>
      </defs><g opacity="{reflection:.4f}">
      <path d="M15.5 14.75 L16 14.1 L16 25 L15.65 24.65 Z" fill="url(#surfaceReflection)"/>
      <path d="M15.55 14.9 L15.68 24.5" fill="none" stroke="#efffff" stroke-width=".22"/>
      <!-- 表面反光与底座共用缩放中心，避免高光越出缩小后的轮廓。 -->
      <g transform="translate(16 25) scale(.7225) translate(-16 -25)">
      <path d="M10 25 L13 23.8 L15.6 25.6 L13 26.4 Z" fill="url(#surfaceReflection)"/>
      <path d="M10.2 25.1 L13 26.4 L18.8 26.4" fill="none" stroke="#efffff" stroke-width=".22"/>
      </g>
      </g>''')
    # 自转复用已认可的主晶石材质，浮动与倾摆围绕晶石中点，不牵动展台。
    transform = (f'translate(0 {lift:.4f}) rotate({tilt:.4f} 16 7.4) '
                 'translate(16 2.3) rotate(24.624) scale(.39) translate(-6 -3)')
    # 复用主晶石切面，移除主指针外晕及整体摆动，并隔离渐变标识。
    import re
    ops = [op for op in geometry('normal', int(frame * 96 / len(ANIMATIONS['text'])))
           if op[0] not in ('ellipse', 'group-start', 'group-end')]
    body = re.sub(r'^<svg[^>]*>|</svg>$', '', svg(ops))
    body = re.sub(r'id="([^"]+)"', lambda match: f'id="text_{match[1]}"', body)
    body = re.sub(r'url\(#([^)]+)\)', lambda match: f'url(#text_{match[1]})', body)
    top = f'<g transform="{transform}">{body}</g>'
    # 竖排文本围绕固定热点旋转完整展台，材质只换色一次。
    body = f'<g transform="rotate(90 16 16)">{stand}{top}</g>' if vertical else stand + top
    return '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">' + body + '</svg>'

def geometry(name,frame=0):
    """生成固定热点的角色几何，叠加主体纵轴自转、角色摆动及三晶体等待动画。"""
    # 展台复用现有 CUR/ANI、Xcursor 和预览导出路径。
    if name in ('text','vertical-text'):
        return [('document',text_pedestal_svg(frame,name=='vertical-text'),None,None,0)]
    # 帧数跟随角色，所有几何运动均周期化；第零帧也是静态方案的基准。
    rates=ANIMATIONS.get(name,(1,))
    phase=motion_phase(name,frame)
    shimmer=phase
    level=math.sin(math.pi*shimmer)**2
    rotation=ROTATION_AMPLITUDES.get(name,0)*math.sin(phase*math.tau)
    ops=[]
    def poly(p,c,stroke=OUTLINE,w=.7):ops.append(('poly',p,c,stroke,w))
    def line(p,c=OUTLINE,w=.85):ops.append(('line',p,None,c,w))
    def mix(a,b,t):return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
    def curve(d,c=OUTLINE,w=1):ops.append(('path',d,None,c,w))
    def rotated(cx,cy,angle):
        """创建只包裹晶体本体的旋转分组，使阴影、状态符号与热点保持稳定。"""
        class RotationGroup:
            """在上下文范围内向绘制列表写入成对的 SVG 旋转分组标记。"""
            def __enter__(self):
                if abs(angle)>1e-8:ops.append(('group-start',(cx,cy,angle),None,None,0))
            def __exit__(self,*_):
                if abs(angle)>1e-8:ops.append(('group-end',None,None,None,0))
        return RotationGroup()
    def gem(p,large=False,animated=False,purple=False,spin=False):
        """绘制原有切面；主体自转时投影真实三维环带，并按深度绘制受光面。"""
        if spin:
            # 长轴穿过两端尖点，旋转只改变横截面，尖端位置和点击热点保持固定。
            a,b,c,d=p
            length=math.dist(a,c)
            axis=((c[0]-a[0])/length,(c[1]-a[1])/length)
            side=(axis[1],-axis[0])
            radius=max(abs((v[0]-a[0])*side[0]+(v[1]-a[1])*side[1]) for v in (b,d))
            # 带停留的角色在运动段完成一整圈，停留帧精确回到初始切面。
            angle=math.tau*phase
            # 椭圆八面环保留可见厚度；纵轴转动时侧面依次进入正面，而非压扁贴图。
            ring=[]
            for index in range(8):
                theta=math.tau*index/8
                x=radius*math.cos(theta)
                z=radius*.68*math.sin(theta)
                # 最宽环带下移：上段68%、下段32%，两端尖点与热点不动。
                ring.append((x*math.cos(angle)+z*math.sin(angle),length*.68,
                             -x*math.sin(angle)+z*math.cos(angle)))
            faces=[]
            for index in range(8):
                for tip in ((0,0,0),(0,length,0)):
                    vertices=[tip,ring[index],ring[(index+1)%8]]
                    # 根据面法线与固定左上前光源计算漫反射，背面先画、正面后画。
                    u=tuple(vertices[1][j]-tip[j] for j in range(3))
                    v=tuple(vertices[2][j]-tip[j] for j in range(3))
                    normal=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
                    if tip[1]!=0: normal=tuple(-n for n in normal)
                    norm=math.sqrt(sum(n*n for n in normal))
                    # 剔除背向切面，避免近乎重合的前后面交换绘制顺序造成闪烁。
                    if normal[2]<=0:continue
                    # 光源固定在屏幕左上前方，将局部法线连同摆动一起变换后再求光照。
                    swing=math.radians(rotation)
                    nx=side[0]*normal[0]+axis[0]*normal[1]
                    ny=side[1]*normal[0]+axis[1]*normal[1]
                    world_x=(nx*math.cos(swing)-ny*math.sin(swing))/norm
                    world_y=(nx*math.sin(swing)+ny*math.cos(swing))/norm
                    facing=normal[2]/norm
                    light=.18+.82*max(0,-.35*world_x-.45*world_y+.82*facing)
                    points=[(a[0]+axis[0]*y+side[0]*x,a[1]+axis[1]*y+side[1]*x) for x,y,z in vertices]
                    # 材质绑定物体表面而非屏幕位置，转动时冰蓝和淡紫反射随切面进入视野。
                    material=('tableLight','tableBlue','tableIce','tableLilac')[index%4]
                    bevel=('edgeIce','edgeBlue','edgeLilac','edgeIndigo')[index%4]
                    glint=max(0,-.25*world_x-.2*world_y+.947*facing)**8
                    faces.append((sum(vertex[2] for vertex in vertices)/3,points,material,bevel,light,glint,facing))
            for depth,points,material,bevel,light,glint,facing in sorted(faces,key=lambda face:face[0]):
                # 饱满冰晶底色保留宽切面，以局部浅色透光区表达纵深，避免玻璃纸质感。
                inset=[mix(point,tuple(sum(v[j] for v in points)/3 for j in range(2)),.055) for point in points]
                poly(points,'url(#clearIce)' if material in ('tableLight','tableIce') else 'url(#clearLilac)',None)
                # 以法线受光量控制整面色调：背光为蓝紫色，迎光保留冰白亮面，形成稳定体积。
                shade=(1-light)**1.4
                ops.append(('facet-shade',points,shade,None,0))
                poly(inset,'#efffff'+f'{round(32*light**3):02x}',None)
                # 面内仅保留一层宽幅折射，反向缓移表现内部深度，不堆叠碎三角。
                refraction=.46+.1*math.sin(angle+depth/max(radius,.01))
                inner=[mix(inset[0],inset[1],.3),mix(inset[0],inset[1],.65),
                       mix(inset[1],inset[2],.8),mix(inset[0],inset[2],.42)]
                ops.append(('sheen',inner,(refraction,.1+.25*light*(1-facing*.4)),None,0))
                # 反射随迎光角度提亮，稳定的宝石底色与移动高光共同表现实体厚度。
                ops.append(('sheen',inset,(.5+.22*math.sin(angle+depth/max(radius,.01)),.08+.5*glint),None,0))
                if glint>.35:
                    sliver=[mix(inset[0],inset[1],.15),mix(inset[0],inset[1],.20),
                            mix(inset[1],inset[2],.72),mix(inset[1],inset[2],.77)]
                    poly(sliver,'#ffffff'+f'{round(145*(glint-.35)/.65):02x}',None)
                ops.append(('facet-edge',[points[0],points[1]],light,None,0))
                # 棱线反射是沿实际边移动的短亮段，以冰蓝柔光衬托白芯，无独立星形。
                travel=.3+.38*(.5+.5*math.sin(angle+depth/max(radius,.01)))
                edge_start=mix(inset[0],inset[1],max(.08,travel-.12))
                edge_end=mix(inset[0],inset[1],min(.94,travel+.12))
                edge_energy=glint**2*math.sin(math.pi*phase)**2
                line([edge_start,edge_end],'#9bdfff'+f'{round(95*edge_energy):02x}',.8)
                line([edge_start,edge_end],'#ffffff'+f'{round(220*edge_energy):02x}',.29)
            # 用投影环带的左右极值封闭外轮廓，保持小尺寸下清晰的宝石边缘。
            left=min(ring,key=lambda vertex:vertex[0])
            right=max(ring,key=lambda vertex:vertex[0])
            outline=[a,(a[0]+axis[0]*right[1]+side[0]*right[0],a[1]+axis[1]*right[1]+side[1]*right[0]),
                     c,(a[0]+axis[0]*left[1]+side[0]*left[0],a[1]+axis[1]*left[1]+side[1]*left[0])]
            line(outline+[a],'#233e79',.72)
            # 外沿亮棱向内收，保持原版玻璃倒角且不增加光标轮廓尺寸。
            center=mix(a,c,.55)
            inset=[mix(point,center,.06) for point in outline]
            line([inset[3],inset[0],inset[1]],'#e7fbff',.38)
            line([inset[1],inset[2]],'#c8c8ff',.33)
            # 只让最迎光的切面产生集中反射，亮区始终由真实面内坐标限定，不再外贴星形。
            if faces:
                depth,points,material,bevel,light,glint,facing=max(faces,key=lambda face:face[5])
                brilliance=glint**4*math.sin(math.pi*phase)**2
                # 两个切面同样迎光时将窄亮芯淡出，避免最亮面切换瞬间反射位置跳跃。
                runner_up=sorted(face[5] for face in faces)[-2] if len(faces)>1 else 0
                separation=min(1,max(0,(glint-runner_up)/.12))
                brilliance*=separation*separation*(3-2*separation)
                center=tuple(sum(point[j] for point in points)/3 for j in range(2))
                inner=[mix(point,center,.1) for point in points]
                # 白亮窄芯与冰蓝肩部沿同一棱线展开，旋转离开迎光角度后平滑回落。
                ribbon=[mix(inner[0],inner[1],.1),mix(inner[0],inner[1],.22),
                        mix(inner[1],inner[2],.72),mix(inner[1],inner[2],.86)]
                poly(ribbon,'#dcfaff'+f'{round(120*brilliance):02x}',None)
                core=[mix(inner[0],inner[1],.14),mix(inner[0],inner[1],.18),
                      mix(inner[1],inner[2],.76),mix(inner[1],inner[2],.82)]
                poly(core,'#ffffff'+f'{round(235*brilliance):02x}',None)
                line([mix(inner[0],inner[1],.16),mix(inner[1],inner[2],.79)],
                     '#ffffff'+f'{round(185*brilliance):02x}',.24)
            return
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
            # A clipped, soft highlight follows the long crystal axis.
            ops.append(('sweep',p,(a,c,shimmer,level),None,0))
            poly([a,b,q],'#ffffff'+f'{round(55*level):02x}',None)
            line([q,b],'#ffffff'+f'{round(100+150*level):02x}',.48)
        line(p+[p[0]],'#233e79',.72 if large else .65)
        # The inset bright edge supplies the glass bevel without widening the silhouette.
        center=mix(a,c,.55)
        inset=[mix(v,center,.065 if large else .11) for v in p]
        line([inset[3],inset[0],inset[1]],'#e7fbff',.38 if large else .26)
        line([inset[1],inset[2]],'#c8c8ff',.33 if large else .23)
    def orbit(cx,cy,radius,double=False):
        """用匀速旋转的渐亮弧和晶体端点指示忙碌，保持中心与热点不动。"""
        # 按该角色的完整帧数匀速转一周，保持最后一帧到第一帧的角速度。
        angle=2*math.pi*phase-math.pi/2
        ops.append(('ellipse',(cx,cy,radius,radius),None,'#528cdd70',.55))
        for offset in ((0,math.pi) if double else (0,)):
            # 相接的短弧形成由暗到亮的尾迹，避免整圈闪烁。
            for step in range(8):
                start=angle+offset-math.radians(112-step*14)
                end=start+math.radians(15)
                arc=(f'M {cx+radius*math.cos(start):.4f} {cy+radius*math.sin(start):.4f} '
                     f'A {radius} {radius} 0 0 1 {cx+radius*math.cos(end):.4f} {cy+radius*math.sin(end):.4f}')
                curve(arc,'#233e79'+f'{100+step*20:02x}',1.55)
                curve(arc,'#9bdcff'+f'{95+step*22:02x}',1.05)
                curve(arc,'#edfaff'+f'{45+step*28:02x}',.4)
            # 菱形亮点强调旋转方向，并延续冰晶切面语言。
            x=cx+radius*math.cos(angle+offset)
            y=cy+radius*math.sin(angle+offset)
            tip=1.05 if double else .85
            poly([(x,y-tip),(x+tip,y),(x,y+tip),(x-tip,y)],LIGHT,OUTLINE,.45)
    def main():
        p=[(6,3),(19,16.8),(17,27),(6.7,19.8)]
        # Radial-gradient shadows keep every export deterministic; no unsupported SVG blur.
        ops.append(('ellipse',(13.5,28.3,6.7,2.2),'url(#shadow)',None,0))
        ops.append(('ellipse',(14.5,22,7,8),'url(#halo)',None,0))
        with rotated(6,3,rotation):
            gem(p,large=True,animated=name in ('normal','working') or (name in ANIMATIONS and level>1e-8),purple=name=='alternate',spin=name in ROTATION_AMPLITUDES)
    def arm(angle,inner=1.25,outer=10,width=2.6):
        def tr(x,y):return (16+x*math.cos(angle)-y*math.sin(angle),16+x*math.sin(angle)+y*math.cos(angle))
        with rotated(16,16,rotation):
            gem([tr(outer,0),tr(inner+2.7,width),tr(inner,0),tr(inner+2.7,-width)],animated=name in ANIMATIONS and level>1e-8)
    if name in ['normal','working','help','unavailable','alternate','location','person']:
        main()
        if name=='working':
            # 小型单弧与主指针分离，后台工作时仍能辨认点击位置。
            orbit(25,11.5,4.1)
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
            # 保留原始射线轮廓；仅提高内部高光，保证静态帧和点击定位不变。
            line(ray,'#91e3ff',.72)
            if level>1e-8:line(ray,'#ffffff'+f'{round(210*level):02x}',.5)
    elif name=='busy':
        # 三颗横向晶体按相位依次放大、上浮并亮起，循环首尾保持连续。
        for index,cx in enumerate((8,16,24)):
            # 在每个帧区间的中点采样，避免三次接力交界都生成完全相同的静止帧。
            progress=((((frame%len(rates))+.5)/len(rates))*3-index)%3
            if progress<.42:
                pulse=math.sin(math.pi*.5*progress/.42)**2
            elif progress<1:
                pulse=math.cos(math.pi*.5*(progress-.42)/.58)**2
            else:
                pulse=0
            scale=.78+.34*pulse
            cy=16-1.1*pulse
            alpha=round(18+58*pulse)
            ops.append(('ellipse',(cx,cy,3.8*scale,5.8*scale),f'#9bdcff{alpha:02x}',None,0))
            gem([(cx,cy-5.2*scale),(cx+2.8*scale,cy),(cx,cy+5.2*scale),(cx-2.8*scale,cy)])
            poly([(cx,cy-4.1*scale),(cx+1.7*scale,cy),(cx,cy+scale),(cx-1.7*scale,cy)],f'#ffffff{round(22+150*pulse):02x}',None)
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
    return raster(svg(ops),size)

@lru_cache(maxsize=512)
def raster(document,size):
    """缓存相同 SVG 的超采样结果，供单尺寸及多尺寸光标共用；调用者不得修改图像。"""
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=document.encode(),output_width=size*4,output_height=size*4))).convert('RGBA').resize((size,size),Image.Resampling.LANCZOS)
def svg(ops):
    """以统一材质绘制所有尺寸，依靠宽切面明暗和集中反射表达宝石体积。"""
    # 展台文档已完成配色，直接返回避免重复偏移色相。
    if ops and ops[0][0]=='document':return ops[0][1]
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
    <linearGradient id="depthGlass" x1="0" y1="0" x2=".85" y2="1"><stop stop-color="#385cae" stop-opacity=".24"/><stop offset=".4" stop-color="#80c9ef" stop-opacity=".08"/><stop offset=".72" stop-color="#7183d6" stop-opacity=".27"/><stop offset="1" stop-color="#e0d8ff" stop-opacity=".13"/></linearGradient>
    <linearGradient id="iceRefraction" x1="0" y1="0" x2="1" y2=".7"><stop stop-color="#58a9df" stop-opacity=".06"/><stop offset=".35" stop-color="#94e8ff" stop-opacity=".36"/><stop offset=".53" stop-color="#f3ffff" stop-opacity=".72"/><stop offset=".65" stop-color="#65c4eb" stop-opacity=".22"/><stop offset="1" stop-color="#b9eaff" stop-opacity="0"/></linearGradient>
    <linearGradient id="violetRefraction" x1="0" y1="1" x2="1" y2="0"><stop stop-color="#628dd5" stop-opacity="0"/><stop offset=".35" stop-color="#aaa6ef" stop-opacity=".31"/><stop offset=".52" stop-color="#f2eaff" stop-opacity=".59"/><stop offset=".7" stop-color="#8fdaf6" stop-opacity=".18"/><stop offset="1" stop-color="#b5dfff" stop-opacity="0"/></linearGradient>
    <linearGradient id="clearIce" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#efffff" stop-opacity=".98"/><stop offset=".28" stop-color="#b2e5fa" stop-opacity=".94"/><stop offset=".55" stop-color="#e7fbff" stop-opacity=".88"/><stop offset=".78" stop-color="#78bfe5" stop-opacity=".96"/><stop offset="1" stop-color="#d1f2ff" stop-opacity=".98"/></linearGradient>
    <linearGradient id="clearLilac" x1="0" y1="0" x2="1" y2=".85"><stop stop-color="#88bde6" stop-opacity=".98"/><stop offset=".32" stop-color="#c5e9fa" stop-opacity=".94"/><stop offset=".58" stop-color="#e8f5ff" stop-opacity=".90"/><stop offset=".82" stop-color="#a9bce9" stop-opacity=".96"/><stop offset="1" stop-color="#e3e9ff" stop-opacity=".98"/></linearGradient>
    </defs>"""
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">',defs]
    def paint(c,prop):
        if c and c.startswith('#') and len(c)==9:return f'{prop}="{c[:7]}" {prop}-opacity="{int(c[7:9],16)/255:.4f}"'
        return f'{prop}="{c or "none"}"'
    for idx,(typ,p,f,s,w) in enumerate(ops):
        if typ=='group-start':
            cx,cy,angle=p
            parts.append(f'<g transform="rotate({angle:.4f} {cx} {cy})">')
            continue
        if typ=='group-end':
            parts.append('</g>')
            continue
        points=lambda: ' '.join(f'{x:.4f},{y:.4f}' for x,y in p)
        if typ=='facet-shade':
            # 拉开整面的受光层次，避免低对比的碎折射在实际指针大小下混成一片。
            typ,f='poly','#284f91'+f'{min(255,round(78*f+210*f**.5)):02x}'
        elif typ=='facet-edge':
            # 保留亚像素抗锯齿，以略宽的亮棱分开相邻切面而不加粗外轮廓。
            typ,s,w,f='line','#f4ffff'+f'{round(25+125*f):02x}',.42,None
        if typ=='sheen':
            # 使用面内坐标定义移动反射带，透明边缘避免高光接缝，面多边形本身负责裁切。
            position,strength=f
            # 压低铺满表面的白雾，保留独立窄亮芯和暗面之间的反差。
            strength*=.6
            left=(p[0][0]*.35+p[1][0]*.65,p[0][1]*.35+p[1][1]*.65)
            right=(p[0][0]*.35+p[2][0]*.65,p[0][1]*.35+p[2][1]*.65)
            start=(left[0]+(right[0]-left[0])*(position-.5),left[1]+(right[1]-left[1])*(position-.5))
            end=(left[0]+(right[0]-left[0])*(position+.5),left[1]+(right[1]-left[1])*(position+.5))
            parts.append(f'<defs><linearGradient id="sheen{idx}" gradientUnits="userSpaceOnUse" x1="{start[0]}" y1="{start[1]}" x2="{end[0]}" y2="{end[1]}"><stop stop-color="#e4faff" stop-opacity="0"/><stop offset=".3" stop-color="#d6f5ff" stop-opacity="{strength*.3}"/><stop offset=".5" stop-color="#ffffff" stop-opacity="{strength}"/><stop offset=".7" stop-color="#dfdcff" stop-opacity="{strength*.25}"/><stop offset="1" stop-color="#dfdcff" stop-opacity="0"/></linearGradient></defs><polygon points="{points()}" fill="url(#sheen{idx})"/>')
            continue
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
    """按角色的实际帧数及变长停留时间编码 ANI，原生文件与预览共享时间表。"""
    rates=ANIMATIONS[name]
    count=len(rates)
    body=b'ACON'+chunk(b'anih',struct.pack('<9I',36,count,count,0,0,32,1,rates[0],1))+chunk(b'rate',struct.pack(f'<{count}I',*rates))+chunk(b'LIST',b'fram'+b''.join(chunk(b'icon',cur(name,i,sizes)) for i in range(count)))
    return b'RIFF'+struct.pack('<I',len(body))+body

def build(text_only=False):
    """导出资源和同源预览；文本专用构建只重编码两个文本 ANI，保留其他角色动画。"""
    for d in ['src/svg','src/animation','cursors/multi','preview','docs']+[f'cursors/{s}' for s in SIZES]: (ROOT/d).mkdir(parents=True,exist_ok=True)
    manifest=[]
    for name,cn,slot in NAMES:
        (ROOT/f'src/svg/icegem-{name}.svg').write_text(svg(geometry(name)))
        (ROOT/f'cursors/multi/icegem-{name}.cur').write_bytes(cur(name))
        for n in SIZES:
            (ROOT/f'cursors/{n}/icegem-{name}.cur').write_bytes(cur(name,sizes=(n,)))
            render(geometry(name),n).save(ROOT/f'preview/icegem-{name}-{n}.png')
        manifest.append(dict(name=name,label=cn,slot=slot or None,hotspots={str(n):hotspot(name,n) for n in SIZES}))
    for name in ANIMATIONS:
        if text_only and name not in ('text','vertical-text'):continue
        (ROOT/f'cursors/multi/icegem-{name}.ani').write_bytes(ani(name))
        for n in SIZES:(ROOT/f'cursors/{n}/icegem-{name}.ani').write_bytes(ani(name,(n,)))
        for i in range(len(ANIMATIONS[name])):(ROOT/f'src/animation/{name}-{i:02}.svg').write_text(svg(geometry(name,i)))
    (ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    sheet=Image.new('RGB',(1200,700),'#f5f8fc');d=ImageDraw.Draw(sheet)
    # Linux 优先使用原预览字体；Windows 等环境缺失时使用 Pillow 内置字体。
    try:
        font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
    except OSError:
        font=ImageFont.load_default(size=17)
    d.text((32,22),'ICEGEM 4.4 / VIOLET',fill='#334f7b',font=font)
    for i,(name,_,_) in enumerate(NAMES):
        x=30+(i%6)*195;y=80+(i//6)*200
        d.rounded_rectangle((x,y,x+180,y+185),12,fill='white')
        sheet.paste(render(geometry(name),96),(x+42,y+10),render(geometry(name),96))
        d.text((x+10,y+115),name,fill='#334f7b',font=font)
        for j,bg in enumerate(['#ffffff','#152238','#b9c5ce']):
            tile=Image.new('RGBA',(40,40),bg);tile.alpha_composite(render(geometry(name),32),(4,4));sheet.paste(tile.convert('RGB'),(x+10+j*54,y+139))
    sheet.save(ROOT/'preview/IceGem-Overview.png')
    # 通过逐帧关键帧时间点表达不同帧率和停留时间，静态模式只显示第一帧。
    cards=[]
    styles=[]
    for name,cn,slot in NAMES:
        rates=ANIMATIONS.get(name,(1,))
        elapsed=0
        frames=[]
        for i,rate in enumerate(rates):
            start=elapsed/sum(rates)*100
            end=(elapsed+rate)/sum(rates)*100
            key=f'{name}-{i}'
            styles.append(f'@keyframes {key}{{0%,100%{{opacity:0}}{start:.8f}%{{opacity:1}}{end:.8f}%{{opacity:0}}}}')
            frames.append(f'<span style="animation:{key} {sum(rates)/60}s steps(1) infinite">{svg_image(geometry(name,i))}</span>')
            elapsed+=rate
        cards.append(f'<article><div class="large anim">'+''.join(frames)+f'</div><h3>{cn}</h3><small>{name} · {slot or "应用专用"}</small><div class="samples">'+''.join(f'<div style="background:{bg}">{svg_image(geometry(name))}</div>' for bg in ['white','#172638','#afb9c8'])+'</div></article>')
    html='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>IceGem 4.2 光标预览</title><style>body{margin:40px auto;max-width:1100px;padding:20px;background:#f3f6fa;color:#294261;font:16px system-ui}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px}article{padding:22px;background:white;border-radius:16px}h3{font-weight:500}small{color:#6a7c95}.large{height:96px;position:relative}.large img{width:80px;height:80px}.samples{display:flex;gap:8px}.samples img{width:32px;height:32px}.samples div{width:44px;height:44px;display:grid;place-items:center}.anim span{position:absolute;opacity:0}'+''.join(styles)+'@media(prefers-reduced-motion:reduce){.anim span{animation:none!important}.anim span:first-child{opacity:1}}</style><h1>IceGem 4.2 · '+THEME_NAME+'</h1><p>晶光随行 / 14 种原生动效 / 文本光标内部折射扫光</p><p>主体自转为 60fps，三晶体等待为 30fps。此处为原生帧预览；点击与跟随需要单独启动 Companion。</p><main>'+''.join(cards)+'</main></html>'
    html=html.replace('IceGem 4.2','IceGem 4.4')
    html=html.replace('文本光标内部折射扫光','文本水晶展台：自转、浮动与倾摆')
    (ROOT/'preview/IceGem-Preview.html').write_text(html)
if __name__=='__main__':
    # 专用入口只缩小动画重建范围，静态造型、概览和 HTML 仍由同一渲染器刷新。
    import argparse
    parser=argparse.ArgumentParser(description='IceGem 原生光标构建')
    parser.add_argument('--text-only',action='store_true',help='仅重建文本状态 ANI；其余动画保留现有资源')
    build(parser.parse_args().text_only)
