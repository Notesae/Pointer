"""当前主指针破碎、移动与复原的动态提案；保留红色禁止符号，不改正式资源。"""
import importlib.util
import re
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 单独保存设计提案，避免覆盖用户已确认的正式图像。
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'preview/unavailable-fracture-motion'
COLORS = ('IceBlue', 'Violet', 'RosePink', 'Mint', 'Amber')


@lru_cache(maxsize=128)
def proposal(renderer, size, frame=0):
    """直接分割当前 normal 晶体，固定尖端与禁止符号，三块碎片错位旋转后复原。"""
    time = frame % 100 / 25
    # 破碎展开用 0.8 秒，复原用 0.6 秒；两端平滑静止，不使用弹跳或随机抖动。
    progress = max(0, min(1, (time-.45)/.8)) * (1-max(0, min(1, (time-2.45)/.6)))
    progress = progress**3 * (10-15*progress+6*progress**2)
    normal = renderer.geometry('normal', 0)
    symbol_ops = renderer.geometry('unavailable', 0)[-2:]
    if progress == 0:
        return renderer.render(normal + symbol_ops, size)
    symbol = re.sub(r'^<svg[^>]*>|</svg>$', '', renderer.svg(symbol_ops))
    ambient = re.sub(r'^<svg[^>]*>|</svg>$', '', renderer.svg([op for op in normal if op[0] == 'ellipse']))
    ops = normal
    ops = [op for op in ops if op[0] != 'ellipse']
    body = re.sub(r'^<svg[^>]*>|</svg>$', '', renderer.svg(ops))
    # 锯齿断口跨越原有切面，三块断晶仅小幅错位，仍能辨认原主体轮廓。
    pieces = (
        ('tip', '0,0 32,0 32,13.9 14.6,14.5 12.1,12.5 9.2,14.6 0,12.8', '',
         'M6.4 13.7 L9.2 14.6 L12.1 12.5 L14.6 14.5 L16.2 14.1'),
        ('left', '0,13 9.2,14.6 12.1,12.5 12.8,17.7 10.9,21.6 0,24', f'translate({-1.5*progress} {1.15*progress}) rotate({-9*progress} 10 18)',
         'M6.5 13.8 L9.2 14.6 L12.1 12.5 L12.8 17.7'),
        ('right', '12.1,12.5 14.6,14.5 32,13.9 32,22 15.2,20.5 12.8,17.7', f'translate({1.65*progress} {.7*progress}) rotate({10*progress} 16 18)',
         'M12.1 12.5 L14.6 14.5 L16.2 14.1 M12.8 17.7 L15.2 20.5 L18.2 21'),
        ('tail', '0,24 10.9,21.6 12.8,17.7 15.2,20.5 32,22 32,32 0,32', f'translate({.6*progress} {2.2*progress}) rotate({-8*progress} 15 24)',
         'M10.9 21.6 L12.8 17.7 L15.2 20.5 L18.2 21'),
    )
    fragments = []
    for name, points, transform, edge in pieces:
        # 每块独立隔离渐变 ID；新增断面受裁切约束，不在晶体外悬浮装饰线。
        crystal = re.sub(r'id="([^"]+)"', lambda m: f'id="{name}_{m[1]}"', body)
        crystal = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{name}_{m[1]})', crystal)
        fracture = renderer.theme_svg(f'<path d="{edge}" fill="none" stroke="#405c91" stroke-width=".9" stroke-linejoin="miter"/><path d="{edge}" transform="translate(0 .35)" fill="none" stroke="#e7fcff" stroke-width=".32"/>')
        fragments.append(f'<g transform="{transform}"><defs><clipPath id="cut_{name}"><polygon points="{points}"/></clipPath></defs><g clip-path="url(#cut_{name})">{crystal}<g opacity="{progress}">{fracture}</g></g></g>')
    document = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">' + ambient + ''.join(fragments) + symbol + '</svg>'
    return renderer.raster(document, size)


def main():
    """输出原方案与断晶的深浅背景对比、实际尺寸和五色材质。"""
    OUT.mkdir(parents=True, exist_ok=True)
    renderers = {}
    for color in COLORS:
        spec = importlib.util.spec_from_file_location(color, ROOT / f'variants/{color}/tools/build.py')
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        renderers[color] = renderer
    frames = []
    for frame in range(100):
        sheet = Image.new('RGB', (960, 660), '#eef3f7')
        draw = ImageDraw.Draw(sheet)
        font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 16)
        heading = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 27)
        draw.text((28, 20), 'ICEGEM / 不可用 · 破碎晶体', font=heading, fill='#294261')
        draw.text((28, 65), '当前主体材质 / 固定尖端与红色符号 / 碎片移动、旋转与复原', font=font, fill='#536b80')
        renderer = renderers['IceBlue']
        for column, (background, ink) in enumerate((('#fafcfe', '#294261'), ('#172638', '#dcefff'))):
            x = 20 + column * 470
            draw.rectangle((x, 106, x+450, 443), fill=background)
            draw.text((x+25, 121), '当前主指针                      破碎动画 / 5 倍', font=font, fill=ink)
            old = renderer.render(renderer.geometry('normal', 0), 160)
            new = proposal(renderer, 160, frame)
            sheet.paste(old, (x+24, 155), old)
            sheet.paste(new, (x+246, 155), new)
            for index, size in enumerate((32, 48, 64)):
                cursor = proposal(renderer, size, frame)
                sheet.paste(cursor, (x+95+index*110, 365), cursor)
                draw.text((x+93+index*110, 337), f'{size}px', font=font, fill=ink)
            draw.text((x+20, 337), '实际尺寸', font=font, fill=ink)
        draw.text((28, 462), '五色材质 / 红色禁止符号始终保留', font=font, fill='#294261')
        for index, (color, renderer) in enumerate(renderers.items()):
            cursor = proposal(renderer, 120, frame)
            x = 28 + index*188
            sheet.paste(cursor, (x+20, 491), cursor)
            draw.text((x+25, 626), color, font=font, fill='#294261')
        if frame == 40:
            sheet.save(OUT / 'unavailable-fracture-motion.png')
        frames.append(sheet.quantize(colors=256))
        if frame % 25 == 0:
            print(f'Rendered {frame+1}/100', flush=True)
    frames[0].save(OUT / 'unavailable-fracture-motion.gif', save_all=True,
                   append_images=frames[1:], duration=40, loop=0, disposal=2)
    print(OUT, flush=True)


if __name__ == '__main__':
    main()
