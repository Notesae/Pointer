"""仅生成双晶冠文本指针提案预览，不改动正式资源或安装包。"""
from pathlib import Path
import importlib.util
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'preview/text-redesign'
COLORS = ('IceBlue', 'Violet', 'RosePink', 'Mint', 'Amber')


def proposal(renderer, frame, size):
    """投影双尖八面晶冠，以固定端点和中心轴承载可见的切面自转。"""
    phase = frame / 60 * math.tau
    # 中轴为窄六边晶柱，暗侧面与亮中棱保证浅深背景上的定位辨识。
    parts = ['<path d="M16 7 L17.25 10 L16.95 23 L16 25 L15.05 23 L14.75 10 Z" fill="#87c9ed" stroke="#233e79" stroke-width=".65"/>',
             '<path d="M16 8 L16 24 L15.05 23 L14.75 10 Z" fill="#477bb4"/>',
             '<path d="M16 9 L16.55 11 L16.35 22 L16 24 Z" fill="#e3faff"/>']
    for cy, direction in ((7.5, 1), (24.5, -1)):
        # 两端晶冠反向自转，投影不移动晶冠中心；蓝紫切面来自主题色相转换。
        angle = phase * direction + .3
        ring = [(16, cy + 2.25 * math.cos(i * math.tau / 8 + angle),
                 2.25 * math.sin(i * math.tau / 8 + angle)) for i in range(8)]
        faces = []
        for i in range(8):
            for tip in ((10.1, cy, 0), (21.9, cy, 0)):
                vertices = (tip, ring[i], ring[(i + 1) % 8])
                depth = sum(p[2] for p in vertices) / 3
                # 左端迎光、右端背光，保留清晰的深色侧面与轮转时的明暗交替。
                light = .5 + .5 * math.sin(i * math.tau / 8 + angle + .65)
                light = (.12 + .48 * light) if tip[0] > 16 else (.28 + .70 * light)
                base = (48, 101, 169) if i % 3 else (100, 110, 188)
                rgb = tuple(round(c + (245 - c) * light) for c in base)
                fill = '#' + ''.join(f'{value:02x}' for value in rgb)
                points = ' '.join(f'{x:.3f},{y:.3f}' for x, y, _ in vertices)
                faces.append((depth, f'<polygon points="{points}" fill="{fill}" stroke="#bceaff" stroke-width=".16"/>'))
        parts.extend(face for _, face in sorted(faces))
        extent = max(abs(y - cy) for _, y, _ in ring)
        parts.append(f'<path d="M10.1 {cy} L16 {cy-extent} L21.9 {cy} L16 {cy+extent} Z" fill="none" stroke="#233e79" stroke-width=".55"/>')
        parts.append(f'<path d="M10.6 {cy} L16 {cy-extent+.25} L21.25 {cy}" fill="none" stroke="#eafaff" stroke-width=".25"/>')
    document = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">' + ''.join(parts) + '</svg>'
    return renderer.raster(renderer.theme_svg(document), size)


def main():
    """生成旧版对照、原生尺寸及五色动画，供用户先评审设计。"""
    OUT.mkdir(parents=True, exist_ok=True)
    renderers = {}
    for color in COLORS:
        spec = importlib.util.spec_from_file_location(color, ROOT / f'variants/{color}/tools/build.py')
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        renderers[color] = renderer
    font_path = 'C:/Windows/Fonts/msyh.ttc'
    title_font = ImageFont.truetype(font_path, 28)
    text_font = ImageFont.truetype(font_path, 16)
    frames = []
    for frame in range(60):
        sheet = Image.new('RGB', (960, 640), '#eef3f7')
        draw = ImageDraw.Draw(sheet)
        draw.text((30, 20), 'ICEGEM / 双晶冠 · 文本指针提案', font=title_font, fill='#24405a')
        draw.text((30, 65), '立体晶冠反向自转 · 中央定位轴稳定 · 2.4 秒循环 · 仅预览', font=text_font, fill='#536b80')
        for column, (bg, ink) in enumerate((('#f9fbfd', '#294261'), ('#172638', '#dcefff'))):
            x = 24 + column * 468
            draw.rectangle((x, 110, x + 444, 400), fill=bg)
            draw.text((x + 18, 123), '上一版                         新提案 / 放大 5 倍', font=text_font, fill=ink)
            old = renderers['IceBlue'].render(renderers['IceBlue'].geometry('text'), 160)
            new = proposal(renderers['IceBlue'], frame, 160)
            sheet.paste(old, (x + 30, 156), old)
            sheet.paste(new, (x + 242, 156), new)
            draw.text((x + 18, 324), '实际尺寸', font=text_font, fill=ink)
            for index, size in enumerate((32, 48, 64)):
                cursor = proposal(renderers['IceBlue'], frame, size)
                sheet.paste(cursor, (x + 120 + index * 95, 330), cursor)
                draw.text((x + 110 + index * 95, 306), f'{size}px', font=text_font, fill=ink)
        draw.text((30, 422), '五色材质 / 同一套几何与动效', font=text_font, fill='#294261')
        for index, color in enumerate(COLORS):
            x = 28 + index * 186
            cursor = proposal(renderers[color], frame, 112)
            sheet.paste(cursor, (x + 28, 454), cursor)
            draw.text((x + 28, 579), color, font=text_font, fill='#294261')
        frames.append(sheet)
    frames[10].save(OUT / 'double-crown.png')
    frames[0].save(OUT / 'double-crown.gif', save_all=True, append_images=frames[1:], duration=40, loop=0, disposal=2)
    frames[0].save(OUT / 'double-crown.webp', save_all=True, append_images=frames[1:], duration=40, loop=0, lossless=True)
    print(OUT, flush=True)


if __name__ == '__main__':
    main()
