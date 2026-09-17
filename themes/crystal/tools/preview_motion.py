"""Crystal 独立主题的造型/本体动画原型；只生成预览，不更改 CUR、ANI 或安装包。"""
from pathlib import Path
import io
import math
import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'preview'
# 所有角色共用完整凸菱形和中央台面，禁止逐帧变形或改变尖端。
OUTER = [(4, 3), (22, 11), (28, 29), (10, 21)]
INNER = [(8, 8), (19.5, 13), (24, 24), (12.5, 19)]
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
    gradients = [('table', '#c5eaff', '#89bce0'), ('top', '#f2fcff', '#73b4e8'),
                 ('right', '#244b8b', '#a3c4f2'), ('bottom', '#d0c9f5', '#5084be'),
                 ('left', '#4581b6', '#c1f0ff')]
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
        parts.append(f'<polygon points="{points([mid,INNER[(i+1)%4],INNER[i]])}" fill="#e2f7ff" opacity=".40"/>')
    # 每个冠面补充暗侧、亮侧及连接棱线，形成抛光切面而非平面色块。
    for i in range(4):
        j = (i+1)%4
        mid = ((OUTER[i][0]+OUTER[j][0])/2, (OUTER[i][1]+OUTER[j][1])/2)
        tone = ['#76b7e8','#24477e','#726fc1','#3f80b5'][i]
        parts.append(f'<polygon points="{points([OUTER[j],mid,INNER[j]])}" fill="{tone}" opacity=".55"/>')
        parts.append(f'<polyline points="{points([OUTER[i],INNER[i],mid,INNER[j]])}" fill="none" stroke="#def6ff" stroke-width=".25" opacity=".85"/>')
    parts.append(f'<polygon points="{points(INNER)}" fill="url(#table)"/>')
    # 中央台面为单一平整抛光面，只允许连续反光，不添加三角分面或内部棱线。
    parts.append('<g clip-path="url(#tableClip)"><rect width="32" height="32" fill="url(#beam)"/></g>')
    parts.append(f'<polygon points="{points(INNER)}" fill="#f4ffff" opacity="{.10+levels[0]*.2}" stroke="#e6faff" stroke-width=".5"/>')
    # 外缘采用窄腰棱和内侧倒角，交替反光沿四边连接，避免粗描边压扁宝石。
    rim = [(x+(16-x)*.075, y+(16-y)*.075) for x,y in OUTER]
    for i in range(4):
        j = (i+1)%4
        edge = [OUTER[i], OUTER[j], rim[j], rim[i]]
        mid = ((OUTER[i][0]+OUTER[j][0])/2, (OUTER[i][1]+OUTER[j][1])/2)
        tone = ['#b7e3ff','#294f8a','#787bb5','#659cca'][i]
        parts.append(f'<polygon points="{points(edge)}" fill="{tone}"/>')
        parts.append(f'<polygon points="{points([OUTER[i],mid,rim[i]])}" fill="#ecfbff" opacity=".85"/>')
        parts.append(f'<polyline points="{points([rim[i],rim[j]])}" fill="none" stroke="#ebfaff" stroke-width=".27"/>')
    # 台面边界保持清晰完整，冠部连线延续到倒角而不越过外轮廓。
    parts.append(f'<polygon points="{points(INNER)}" fill="none" stroke="#e9faff" stroke-width=".42"/>')
    parts.append(f'<polygon points="{points(OUTER)}" fill="none" stroke="#34598a" stroke-width=".32" stroke-linejoin="miter"/>')
    return ''.join(parts) + '</svg>'


def build():
    """生成四角色的真实逐帧预览，深浅背景共用同一缓存与时序。"""
    OUT.mkdir(exist_ok=True)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 17)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 13)
    cache = []
    for role, count in enumerate(PERIODS):
        frames = []
        for frame in range(count):
            im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=document(role, frame).encode(), output_width=256, output_height=256))).convert('RGBA')
            frames.append({n: im.resize((n, n), Image.Resampling.LANCZOS) for n in (32,48,64,144)})
        cache.append(frames)
        print(f'Role {role+1} rendered', flush=True)
    for dark in (False, True):
        bg, fg = ('#172638', '#dfedff') if dark else ('#f0f5fa', '#263f65')
        frames = []
        for frame in range(288):
            sheet = Image.new('RGB', (960, 350), bg)
            draw = ImageDraw.Draw(sheet)
            draw.text((20, 12), 'Crystal · 切面晶石动画原型 / 轮廓与热点固定', font=font, fill=fg)
            for role in range(4):
                x = role * 240
                draw.text((x+18, 53), LABELS[role], font=font, fill=fg)
                draw.text((x+18, 79), ['3.2s · 含停留','1.6s · 缓亮回落','1.6s · 连续折射','1.2s · 交替明暗'][role], font=small, fill=fg)
                rendered = cache[role][frame % PERIODS[role]]
                sheet.paste(rendered[144], (x+45, 102), rendered[144])
                for n, offset in [(32,22),(48,78),(64,150)]:
                    sheet.paste(rendered[n], (x+offset, 260), rendered[n])
                    draw.text((x+offset, 326), f'{n}px', font=small, fill=fg)
            frames.append(sheet)
        name = 'crystal-motion-prototype' + ('-dark' if dark else '')
        frames[16].save(OUT / (name+'.png'))
        frames[0].save(OUT / (name+'.gif'), save_all=True, append_images=frames[1:], duration=[30,30,40]*96, loop=0)
        print(name+' saved', flush=True)


if __name__ == '__main__':
    build()
