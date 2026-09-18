"""生成 Crystal 功能光标的静态 SVG 与深浅背景审核图，不写入系统光标。"""
from pathlib import Path
import io
import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
# 所有功能角色使用中心热点；32px 下杆宽约 2px，轮廓负责辨识，切面负责材质。
ROLES = [('text','文本选择'),('precision','精确选择'),('move','移动'),('size-we','水平缩放'),('size-ns','垂直缩放'),('size-nwse','斜向缩放 ↖↘'),('size-nesw','斜向缩放 ↗↙')]


def gem_shape(path, facets):
    """用连续外沿、宽冠面和窄高光构成冰晶厚度，内部切面裁剪于角色轮廓。"""
    return f'''<defs><clipPath id="cut"><path d="{path}"/></clipPath></defs>
    <path d="{path}" fill="url(#body)" stroke="#365e94" stroke-width=".65" stroke-linejoin="round"/>
    <g clip-path="url(#cut)">{facets}
    <path d="{path}" fill="none" stroke="#e3f6ff" stroke-width="1.4" opacity=".55"/>
    <path d="{path}" fill="none" stroke="#4d79ad" stroke-width=".5"/></g>'''


def document(role):
    """按操作语义构建文本杆、十字及双向箭头；旋转围绕同一个中心热点。"""
    defs='''<defs>
    <linearGradient id="body" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#daf5ff"/><stop offset=".35" stop-color="#83bde5"/><stop offset=".64" stop-color="#eafaff"/><stop offset="1" stop-color="#406baa"/></linearGradient>
    <linearGradient id="table" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#94d0f0"/><stop offset=".55" stop-color="#ceeefe"/><stop offset="1" stop-color="#75a8db"/></linearGradient>
    </defs>'''
    if role=='text':
        # 平头六边形晶冠连接平整细柱，避免上一版漏斗状端帽和粗双描边。
        path='M37 12 Q35 12 34 14 L31 18 Q30 20 33 22 L43 26 Q46 27 46 31 L46 69 Q46 73 43 74 L33 78 Q30 80 31 82 L34 86 Q35 88 37 88 L63 88 Q65 88 66 86 L69 82 Q70 80 67 78 L57 74 Q54 73 54 69 L54 31 Q54 27 57 26 L67 22 Q70 20 69 18 L66 14 Q65 12 63 12 Z'
        facets='''<path d="M35 14 L65 14 L61 20 L39 20 Z" fill="url(#table)"/>
        <path d="M31 19 L39 20 L46 27 L33 22 Z" fill="#3a72a6"/>
        <path d="M65 14 L69 19 L61 20 Z" fill="#effaff"/>
        <path d="M39 20 L61 20 L54 27 L46 27 Z" fill="#9cc9e8"/>
        <path d="M46 28 L49 31 L49 69 L46 74 Z" fill="#3b70a6"/>
        <path d="M49 29 L53 28 L53 72 L49 70 Z" fill="url(#table)"/>
        <path d="M46 74 L54 74 L61 80 L39 80 Z" fill="#d9f3ff"/>
        <path d="M39 80 L61 80 L65 86 L35 86 Z" fill="url(#table)"/>
        <path d="M31 81 L39 80 L35 86 Z" fill="#5685b6"/>
        <path d="M61 80 L69 81 L65 86 Z" fill="#3b629a"/>
        <path d="M35 14 L65 14 M49 30 V70 M39 80 H61" fill="none" stroke="#f4fcff" stroke-width=".7"/>'''
    elif role in ('precision','move'):
        # 四臂共用中心区域，避免叠加四枚宝石造成热点遮挡与接缝。
        tip=9 if role=='move' else 15
        shoulder=25 if role=='move' else 31
        wing=11 if role=='move' else 5
        arm=f'M50 {tip} Q49 {tip} 48 {tip+3} L{50-wing} {shoulder} L46 {shoulder} L46 46 L{shoulder} 46 L{shoulder} {50-wing} L{tip+3} 48 Q{tip} 49 {tip} 50 Q{tip} 51 {tip+3} 52 L{shoulder} {50+wing} L{shoulder} 54 L46 54 L46 {100-shoulder} L{50-wing} {100-shoulder} L48 {97-tip} Q50 {103-tip} 52 {97-tip} L{50+wing} {100-shoulder} L54 {100-shoulder} L54 54 L{100-shoulder} 54 L{100-shoulder} {50+wing} L{97-tip} 52 Q{103-tip} 50 {97-tip} 48 L{100-shoulder} {50-wing} L{100-shoulder} 46 L54 46 L54 {shoulder} L{50+wing} {shoulder} L52 {tip+3} Q51 {tip} 50 {tip} Z'
        path=arm
        facets=''.join(f'<g transform="rotate({angle} 50 50)"><path d="M50 {tip} L50 46 L46 46 L46 {shoulder} L{50-wing} {shoulder} Z" fill="#5087bc"/><path d="M50 {tip} L54 {shoulder} L54 46 L50 46 Z" fill="url(#table)"/><path d="M50 {tip+4} V44" stroke="#ecfaff" stroke-width="1.1"/></g>' for angle in (0,90,180,270))
        facets+='<path d="M46 46 L54 46 L54 54 L46 54 Z" fill="url(#table)"/><path d="M46 46 L54 46 L54 54" fill="none" stroke="#e9faff" stroke-width="1"/>'
    else:
        # 双端采用饱满的菱形晶冠，以窄晶桥连接；端部仍向外指示缩放方向。
        path='M8 49 L24 36 Q27 34 30 36 L39 43 Q42 46 46 46 L54 46 Q58 46 61 43 L70 36 Q73 34 76 36 L92 49 Q94 50 92 52 L76 64 Q73 66 70 64 L61 57 Q58 54 54 54 L46 54 Q42 54 39 57 L30 64 Q27 66 24 64 L8 52 Q6 50 8 49 Z'
        facets='''<path d="M8 50 L26 36 L24 43 L15 50 Z" fill="#eaf9ff"/>
        <path d="M26 36 L40 46 L32 47 L24 43 Z" fill="#9ac9e8"/>
        <path d="M15 50 L24 43 L32 47 L35 53 L25 58 Z" fill="url(#table)"/>
        <path d="M8 50 L25 58 L27 65 Z" fill="#3c6d9f"/>
        <path d="M25 58 L35 53 L40 55 L27 65 Z" fill="#6a91c0"/>
        <path d="M32 47 L68 47 L65 52 L35 52 Z" fill="url(#table)"/>
        <path d="M35 52 L65 52 L60 55 L40 55 Z" fill="#4d79ac"/>
        <path d="M60 46 L73 35 L76 43 L68 47 Z" fill="#e8f9ff"/>
        <path d="M73 35 L93 50 L85 50 L76 43 Z" fill="#a6cfea"/>
        <path d="M68 47 L76 43 L85 50 L75 58 L65 53 Z" fill="url(#table)"/>
        <path d="M85 50 L93 50 L73 65 L75 58 Z" fill="#416a9f"/>
        <path d="M65 53 L75 58 L73 65 L60 55 Z" fill="#83acda"/>
        <path d="M15 50 L24 43 L32 47 L68 47 L76 43 L85 50" fill="none" stroke="#effbff" stroke-width=".65"/>'''
    angle={'size-ns':90,'size-nwse':45,'size-nesw':-45}.get(role,0)
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">{defs}<g transform="rotate({angle} 50 50)">{gem_shape(path,facets)}</g></svg>'


def build():
    """保存独立矢量资源及同尺度明暗预览，附真实32/48/64像素尺寸检查。"""
    out=ROOT/'preview'/'roles-02'
    out.mkdir(parents=True,exist_ok=True)
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
    small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
    sheet=Image.new('RGB',(1085,1020),'#eef4fa')
    draw=ImageDraw.Draw(sheet)
    draw.text((30,20),'Crystal · 功能光标 02 / 主体沿用第14轮',font=font,fill='#243c60')
    draw.text((30,57),'重做文本晶柱与双端晶冠 · 深浅背景和实际尺寸 · 待校对',font=small,fill='#546d8c')
    roles=[('normal','已确认主体')]+[item for item in ROLES if item[0] not in ('precision','move')]
    for index,(role,title) in enumerate(roles):
        x=20+(index%3)*355
        y=100+(index//3)*450
        svg=(ROOT/'preview'/'static-study-14.svg').read_text(encoding='utf-8') if role=='normal' else document(role)
        (out/f'{role}.svg').write_text(svg,encoding='utf-8')
        draw.rounded_rectangle((x,y,x+340,y+432),radius=12,fill='#ffffff',outline='#cedcea')
        draw.text((x+16,y+12),title,font=font,fill='#263f64')
        for offset,bg in [(50,'#f3f7fc'),(228,'#172638')]:
            draw.rectangle((x+10,y+offset,x+330,y+offset+166),fill=bg)
            im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),output_width=142,output_height=142))).convert('RGBA')
            sheet.paste(im,(x+18,y+offset+12),im)
            for size,px,py in [(32,188,12),(48,246,12),(64,217,72)]:
                im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),output_width=size,output_height=size))).convert('RGBA')
                sheet.paste(im,(x+px,y+offset+py),im)
            draw.text((x+177,y+offset+143),'32 / 48 / 64 px',font=small,fill='#8296b0')
        draw.text((x+15,y+404),'中心热点 · 静态待校对' if role!='normal' else '第14轮主体 · 已确认',font=small,fill='#647d9b')
    draw.text((30,1000),'仅生成预览与 SVG，尚未制作安装包。',font=small,fill='#546d8c')
    sheet.save(out/'contact-sheet.png')
    print(out/'contact-sheet.png')


if __name__=='__main__':
    build()
