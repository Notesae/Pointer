"""独立预览主晶石、通透棱线与斜切尾晶，不生成正式光标或安装包。"""
import re
import importlib.util
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'preview/text-refined'


def crystal(renderer, frame, transform, prefix):
    """复用主指针的三维切面和折射，去除外晕并隔离渐变标识。"""
    ops = [op for op in renderer.geometry('normal', frame)
           if op[0] not in ('ellipse', 'group-start', 'group-end')]
    body = re.sub(r'^<svg[^>]*>|</svg>$', '', renderer.svg(ops))
    body = re.sub(r'id="([^"]+)"', lambda m: f'id="{prefix}_{m[1]}"', body)
    body = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{prefix}_{m[1]})', body)
    return f'<g transform="{transform}">{body}</g>'


def proposal(renderer, frame, size):
    """保留上端自转晶石，以细透棱线连接单枚斜切尾晶，热点处几何固定。"""
    # 中轴总宽约一像素，以浅色折射面和窄侧棱保持可见性，减少深色直杆的厚重感。
    stem = renderer.theme_svg('''<defs><linearGradient id="spine" x1="0" y1="0" x2="1" y2="0">
      <stop stop-color="#83b7d9" stop-opacity=".85"/><stop offset=".42" stop-color="#efffff"/>
      <stop offset=".7" stop-color="#d2eef9" stop-opacity=".8"/><stop offset="1" stop-color="#a2bde5" stop-opacity=".9"/>
      </linearGradient></defs>
      <path d="M15.6 11.7 L16 12.1 L16.4 11.7 L16.33 24.65 L16 25 L15.67 24.65 Z" fill="url(#spine)" stroke="#648dae" stroke-opacity=".75" stroke-width=".22"/>
      <path d="M15.97 12.5 L15.97 24.5" fill="none" stroke="#f0ffff" stroke-width=".24"/>''')
    # 正立主晶石沿用已选造型与动效；小尾晶以斜向切面收尾，形成明确的上下主次。
    top = crystal(renderer, int(frame * 96 / 60), 'translate(16 3) rotate(24.624) scale(.38) translate(-6 -3)', 'top')
    tail = crystal(renderer, 16, 'translate(17.77 23.23) rotate(69.624) scale(.19) translate(-6 -3)', 'tail')
    document = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">' + stem + top + tail + '</svg>'
    return renderer.raster(document, size)


def main():
    """输出深浅背景、原生尺寸及五色预览，保留旧方案供比较。"""
    OUT.mkdir(parents=True, exist_ok=True)
    renderers = {}
    for color in ('IceBlue', 'Violet', 'RosePink', 'Mint', 'Amber'):
        spec = importlib.util.spec_from_file_location(color, ROOT / f'variants/{color}/tools/build.py')
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        renderers[color] = renderer
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 17)
    heading = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 27)
    frames = []
    for frame in range(60):
        sheet = Image.new('RGB', (880, 600), '#eef3f7')
        draw = ImageDraw.Draw(sheet)
        draw.text((28, 20), 'ICEGEM / 主晶石 × 斜切尾晶', font=heading, fill='#294261')
        draw.text((28, 64), '保留上端切面自转 · 细透冰晶棱线 · 单枚小尾晶 · 仅设计预览', font=font, fill='#536b80')
        for column, (bg, ink) in enumerate((('#f9fbfd', '#294261'), ('#172638', '#dcefff'))):
            x = 20 + column * 430
            draw.rectangle((x, 106, x + 410, 378), fill=bg)
            draw.text((x + 18, 118), '主指针材质参考       新文本指针 / 5 倍', font=font, fill=ink)
            renderer = renderers['IceBlue']
            reference = renderer.render(renderer.geometry('normal', int(frame * 96 / 60)), 128)
            cursor = proposal(renderer, frame, 160)
            sheet.paste(reference, (x + 35, 150), reference)
            sheet.paste(cursor, (x + 224, 143), cursor)
            draw.text((x + 18, 323), '实际尺寸', font=font, fill=ink)
            for index, size in enumerate((32, 48, 64)):
                small = proposal(renderer, frame, size)
                sheet.paste(small, (x + 118 + index * 88, 306), small)
        draw.text((28, 399), '五色材质 / 上端与下端采用不同结构', font=font, fill='#294261')
        for index, (color, renderer) in enumerate(renderers.items()):
            cursor = proposal(renderer, frame, 120)
            x = 30 + index * 170
            sheet.paste(cursor, (x + 14, 427), cursor)
            draw.text((x + 22, 560), color, font=font, fill='#294261')
        frames.append(sheet)
    frames[12].save(OUT / 'crystal-tail.png')
    frames[0].save(OUT / 'crystal-tail.gif', save_all=True, append_images=frames[1:], duration=40, loop=0, disposal=2)
    frames[0].save(OUT / 'crystal-tail.webp', save_all=True, append_images=frames[1:], duration=40, loop=0, lossless=True)
    print(OUT, flush=True)


if __name__ == '__main__':
    main()
