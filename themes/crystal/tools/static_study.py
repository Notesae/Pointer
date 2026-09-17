"""Crystal 静态校准稿：按设计参考调整倾角、台面和冠部边缘，暂不替换动画原型。"""
from pathlib import Path
import io
import math
import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'preview'
# 所有角色共用完整凸菱形和中央台面，禁止逐帧变形或改变尖端。
OUTER = [(3, 5), (20.3, 10.2), (30, 25.3), (10.4, 17.6)]
INNER = [(9.8, 9.4), (20, 12.3), (23.5, 20.5), (12.8, 17.1)]
PERIODS = [96, 48, 48, 36]
LABELS = ['常态 · 台面掠光', '链接 · 冠面提亮', '后台 · 顺序折射', '忙碌 · 双面交替']


def points(vertices):
    return ' '.join(f'{x},{y}' for x, y in vertices)


def document(role, frame):
    """按时序生成固定几何 SVG：动画仅调整各冠面亮度和台面内部光带。"""
    phase = frame / PERIODS[role]
    if role == 0:
        travel = frame / 24
        power = math.sin(math.pi * travel) ** 2 if frame < 24 else 0
        levels = [power * .3, power * .45, power * .3, power * .15]
    elif role == 1:
        power = math.sin(math.pi * phase) ** 2
        travel = phase
        levels = [power * .75, power * .55, power * .1, power * .12]
    elif role == 2:
        travel = phase
        power = 1
        levels = [max(0, math.cos(2 * math.pi * (phase - i / 4))) ** 4 * .72 for i in range(4)]
    else:
        travel = phase
        power = .45
        levels = [.68 * max(0, math.sin(2 * math.pi * phase)),
                  .72 * max(0, -math.sin(2 * math.pi * phase)),
                  .45 * max(0, -math.sin(2 * math.pi * phase)),
                  .55 * max(0, math.sin(2 * math.pi * phase))]
    gradients = [('table', '#a9d9f2', '#b9e4f4'), ('top', '#fbfeff', '#82b7e1'),
                 ('right', '#22568c', '#aec8f2'), ('bottom', '#c0c0ec', '#5485bf'),
                 ('left', '#265786', '#aeeaff')]
    defs = ''.join(f'<linearGradient id="{name}" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>' for name, a, b in gradients)
    # 光带使用固定坐标系，裁剪到中央台面，避免外部光晕或越界像素。
    pos = -12 + 52 * travel
    defs += f'<clipPath id="tableClip"><polygon points="{points(INNER)}"/></clipPath><linearGradient id="beam" gradientUnits="userSpaceOnUse" x1="{pos-5}" y1="0" x2="{pos+5}" y2="0"><stop stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#f7ffff" stop-opacity="{power*.85}"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32"><defs>{defs}</defs>']
    for i, name in enumerate(['top', 'right', 'bottom', 'left']):
        face = [OUTER[i], OUTER[(i+1)%4], INNER[(i+1)%4], INNER[i]]
        parts.append(f'<polygon points="{points(face)}" fill="url(#{name})"/>')
        parts.append(f'<polygon points="{points(face)}" fill="#f4fcff" opacity="{levels[i]}"/>')
        # 一条固定的冠部斜切面提供厚度，不增添密集碎切面。
        mid = ((OUTER[i][0]+OUTER[(i+1)%4][0])/2, (OUTER[i][1]+OUTER[(i+1)%4][1])/2)
        parts.append(f'<polygon points="{points([mid,INNER[(i+1)%4],INNER[i]])}" fill="#e2f7ff" opacity=".65"/>')
    # 每个冠面补充暗侧、亮侧及连接棱线，形成抛光切面而非平面色块。
    for i in range(4):
        j = (i+1)%4
        mid = ((OUTER[i][0]+OUTER[j][0])/2, (OUTER[i][1]+OUTER[j][1])/2)
        tone = ['#76b7e8','#24477e','#726fc1','#3f80b5'][i]
        parts.append(f'<polygon points="{points([OUTER[j],mid,INNER[j]])}" fill="{tone}" opacity=".55"/>')
        parts.append(f'<polyline points="{points([OUTER[i],INNER[i],mid,INNER[j]])}" fill="none" stroke="#def6ff" stroke-width=".12" opacity=".5"/>')
    # 冠部两端汇聚、侧缘分段折射；这些固定小面均位于平整台面之外。
    for facet_index, (vertices, tone) in enumerate([
        ([(3,5),(12,7.7),(9.8,9.4)], '#f5fcff'),
        ([(12,7.7),(17.7,9.5),(20,12.3)], '#6296c7'),
        ([(20.3,10.2),(22,13),(20,12.3)], '#e5f6ff'),
        ([(22,13),(26,19),(23.5,20.5)], '#365d9a'),
        ([(26,19),(30,25.3),(23.5,20.5)], '#6765aa'),
        ([(10.4,17.6),(16,19.8),(12.8,17.1)], '#36659b'),
        ([(16,19.8),(21.5,22),(23.5,20.5)], '#e1efff'),
        ([(3,5),(7,12),(9.8,9.4)], '#76bee3'),
        ([(7,12),(10.4,17.6),(12.8,17.1)], '#316693')]):
        # 切面内采用连续折射渐变，保留明暗硬交界，避免大片实色造成纸片感。
        bright = '#edfaff' if facet_index % 3 else '#b6e6ff'
        parts.append(f'<defs><linearGradient id="facet{facet_index}" x1="0%" y1="0%" x2="100%" y2="100%"><stop stop-color="{tone}"/><stop offset=".55" stop-color="{bright}"/><stop offset="1" stop-color="{tone}"/></linearGradient></defs>')
        parts.append(f'<polygon points="{points(vertices)}" fill="url(#facet{facet_index})"/>')
    parts.append('<defs><linearGradient id="tablePolish" x1="0%" y1="0%" x2="100%" y2="100%"><stop stop-color="#79b2d8"/><stop offset=".48" stop-color="#c3e9f8"/><stop offset="1" stop-color="#8fc5e7"/></linearGradient></defs>')
    parts.append(f'<polygon points="{points(INNER)}" fill="url(#tablePolish)"/>')
    # 中央台面为单一平整抛光面，只允许连续反光，不添加三角分面或内部棱线。
    parts.append('<g clip-path="url(#tableClip)"><rect width="32" height="32" fill="url(#beam)"/></g>')
    parts.append(f'<polygon points="{points(INNER)}" fill="#f4ffff" opacity="{.10+levels[0]*.2}" stroke="#e6faff" stroke-width=".5"/>')
    # 外缘采用窄腰棱和内侧倒角，交替反光沿四边连接，避免粗描边压扁宝石。
    rim = [(x+(16.0-x)*t, y+(15-y)*t) for (x,y),t in zip(OUTER,(.018,.075,.025,.07))]
    for i in range(4):
        j = (i+1)%4
        edge = [OUTER[i], OUTER[j], rim[j], rim[i]]
        mid = ((OUTER[i][0]+OUTER[j][0])/2, (OUTER[i][1]+OUTER[j][1])/2)
        tone = ['#b7e3ff','#294f8a','#787bb5','#659cca'][i]
        parts.append(f'<polygon points="{points(edge)}" fill="{tone}"/>')
        parts.append(f'<polygon points="{points([OUTER[i],mid,rim[i]])}" fill="#ecfbff" opacity=".85"/>')
        parts.append(f'<polyline points="{points([rim[i],rim[j]])}" fill="none" stroke="#ebfaff" stroke-width=".14"/>')
    # 台面边界保持清晰完整，冠部连线延续到倒角而不越过外轮廓。
    parts.append(f'<polygon points="{points(INNER)}" fill="none" stroke="#e9faff" stroke-width=".28"/>')
    parts.append(f'<polygon points="{points(OUTER)}" fill="none" stroke="#34598a" stroke-width=".20" stroke-linejoin="miter"/>')
    return ''.join(parts) + '</svg>'



def build_study():
    """同页并列原设计局部、上一版和校准稿，附真实尺寸与深色背景检查。"""
    import importlib.util
    spec = importlib.util.spec_from_file_location('previous', ROOT / 'tools/preview_motion.py')
    previous = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(previous)
    sheet = Image.new('RGB', (1200, 660), '#f1f6fb')
    draw = ImageDraw.Draw(sheet)
    title = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 23)
    label = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 17)
    draw.text((24,18), 'Crystal · 静态造型校准 / 本轮不改动画', font=title, fill='#233d64')
    # 参考图只裁出已确认的静置宝石，保留原图比例，不重绘参考内容。
    reference = Image.open(ROOT / 'docs/shape-approved.png').convert('RGB').crop((681,158,945,353))
    reference.thumbnail((330,280), Image.Resampling.LANCZOS)
    sheet.paste(reference,(30,125))
    draw.text((30,72), '设计稿 · 静置局部',font=label,fill='#233d64')
    draw.text((410,72), '上一版 · 约 47°',font=label,fill='#233d64')
    draw.text((800,72), '校准稿 · 约 37°',font=label,fill='#233d64')
    for column, module in [(1,previous),(2,None)]:
        svg = previous.document(0,0) if module else document(0,0)
        crystal = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),output_width=768,output_height=768))).convert('RGBA')
        large = crystal.resize((300,300),Image.Resampling.LANCZOS)
        sheet.paste(large,(column*390+20,90),large)
        draw.rectangle((column*390+12,409,column*390+365,632), fill='#172638')
        medium=crystal.resize((168,168),Image.Resampling.LANCZOS)
        sheet.paste(medium,(column*390+22,430),medium)
        for n,offset in [(32,202),(48,250),(64,305)]:
            small=crystal.resize((n,n),Image.Resampling.LANCZOS)
            sheet.paste(small,(column*390+offset,472),small)
            draw.text((column*390+offset,548),str(n),font=label,fill='#d6e8ff')
    draw.text((24,420),'校准重点',font=title,fill='#233d64')
    for i,text in enumerate(['更平缓的长轴与完整台面','非等宽冠部，尖端切面汇聚','减细描边，用明暗形成棱角','右侧保留窄暗面与折射亮边']):
        draw.text((24,463+i*32),text,font=label,fill='#233d64')
    OUT.mkdir(exist_ok=True)
    sheet.save(OUT / 'static-study-02.png')
    (OUT / 'static-study-02.svg').write_text(document(0,0),encoding='utf-8')
    print('Static comparison ready.')


if __name__ == '__main__':
    build_study()
