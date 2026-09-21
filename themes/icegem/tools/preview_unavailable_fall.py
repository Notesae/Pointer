"""晶体失能滑落预览：光先退去，随后下滑；蓄光领先复浮，五秒平滑循环。"""
import importlib.util
import re
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 独立预览输出，不改正式指针、版本或安装包。
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'preview/unavailable-fall-motion'
COLORS = ('IceBlue', 'Violet', 'RosePink', 'Mint', 'Amber')


@lru_cache(maxsize=128)
def proposal(renderer, size, frame=0):
    """分离光照与位姿时间轴，使失能下滑和重新悬浮存在自然滞后，禁止符号固定。"""
    time = frame % 125 / 25
    falling = max(0,min(1,(time-.3)/1.3))
    rising = max(0,min(1,(time-2.4)/1.5))
    falling = falling**3*(10-15*falling+6*falling**2)
    rising = rising**3*(10-15*rising+6*rising**2)
    level = falling*(1-rising)
    # 位移滞后于光线：先失去能量再下滑，先蓄光再复浮；五次曲线两端速度归零。
    descent = max(0,min(1,(time-.65)/1.3))
    ascent = max(0,min(1,(time-2.95)/1.6))
    descent = descent**3*(10-15*descent+6*descent**2)
    ascent = ascent**3*(10-15*ascent+6*ascent**2)
    drop = descent*(1-ascent)
    normal = renderer.geometry('normal',0)
    symbol_ops = renderer.geometry('unavailable',0)[-2:]
    body = re.sub(r'^<svg[^>]*>|</svg>$','',renderer.svg([op for op in normal if op[0]!='ellipse']))
    ambient = re.sub(r'^<svg[^>]*>|</svg>$','',renderer.svg(symbol_ops))

    def dim_color(match):
        """保留每个切面的相对明暗及主题色，降低亮度和饱和度而非覆盖一层灰板。"""
        rgb = [int(match[0][i:i+2],16) for i in (1,3,5)]
        luminance = .2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2]
        return '#' + ''.join(f'{round((.55*c+.45*luminance)*.54+offset):02x}'
                             for c,offset in zip(rgb,(14,18,24)))

    dim = re.sub(r'#[0-9a-fA-F]{6}(?![0-9a-fA-F])',dim_color,body)
    dim = re.sub(r'id="([^"]+)"',lambda m:f'id="dim_{m[1]}"',dim)
    dim = re.sub(r'url\(#([^)]+)\)',lambda m:f'url(#dim_{m[1]})',dim)
    # 渐变前沿沿尖端到尾端推进，12px 过渡带避免扫描线或突然整面闪灭。
    edge = -7+44*level
    mask = f'<defs><linearGradient id="fade" gradientUnits="userSpaceOnUse" x1="0" y1="{edge-6}" x2="0" y2="{edge+6}"><stop stop-color="white" stop-opacity="0"/><stop offset="1" stop-color="white" stop-opacity="1"/></linearGradient><mask id="energy" maskUnits="userSpaceOnUse" x="0" y="0" width="32" height="32"><rect width="32" height="32" fill="url(#fade)"/></mask></defs>'
    # 阴影保持在下方平面，低位时更集中、更深；宝石只滑落与轻微放平，不弹跳。
    shadow = renderer.theme_svg(f'<defs><radialGradient id="ground"><stop stop-color="#405f88" stop-opacity="{.22+.15*drop}"/><stop offset="1" stop-color="#6b91b5" stop-opacity="0"/></radialGradient></defs><ellipse cx="{13.5+1.2*drop}" cy="29.3" rx="{6.7-2*drop}" ry="{2.1-.85*drop}" fill="url(#ground)"/>')
    transform = f'translate({1.2*drop} {2.2*drop}) rotate({-6*drop} 12 15)'
    document = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'+shadow+ambient+f'<g transform="{transform}">'+dim+mask+'<g mask="url(#energy)">'+body+'</g></g></svg>'
    return renderer.raster(document,size)


def main():
    """输出失能光影的深浅背景、实际尺寸和五色对比，并保留静态封面。"""
    OUT.mkdir(parents=True, exist_ok=True)
    renderers = {}
    for color in COLORS:
        spec = importlib.util.spec_from_file_location(color, ROOT / f'variants/{color}/tools/build.py')
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        renderers[color] = renderer
    frames = []
    for frame in range(125):
        sheet = Image.new('RGB', (960, 660), '#eef3f7')
        draw = ImageDraw.Draw(sheet)
        font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 16)
        heading = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 27)
        draw.text((28, 20), 'ICEGEM / 不可用 · 失能 · 滑落 · 复浮', font=heading, fill='#294261')
        draw.text((28, 65), '5 秒循环 / 熄光先于滑落，蓄光先于复浮 / 红色符号固定', font=font, fill='#536b80')
        renderer = renderers['IceBlue']
        for column, (background, ink) in enumerate((('#fafcfe', '#294261'), ('#172638', '#dcefff'))):
            x = 20 + column * 470
            draw.rectangle((x, 106, x+450, 443), fill=background)
            draw.text((x+25, 121), '当前主指针                      滑落复浮 / 5 倍', font=font, fill=ink)
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
        if frame == 55:
            sheet.save(OUT / 'unavailable-fall-motion.png')
        frames.append(sheet.quantize(colors=256))
        if frame % 25 == 0:
            print(f'Rendered {frame+1}/125', flush=True)
    frames[0].save(OUT / 'unavailable-fall-motion.gif', save_all=True,
                   append_images=frames[1:], duration=40, loop=0, disposal=2)
    print(OUT, flush=True)


if __name__ == '__main__':
    main()
