"""晶体失能动效提案：完整主体内部熄光再恢复，红色禁止标识保持固定。"""
import importlib.util
import re
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 独立预览输出，不改正式指针、版本或安装包。
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'preview/unavailable-dim-motion'
COLORS = ('IceBlue', 'Violet', 'RosePink', 'Mint', 'Amber')


@lru_cache(maxsize=128)
def proposal(renderer, size, frame=0):
    """以移动的柔和遮罩依次降低晶面亮度；主体轮廓、热点和禁止符号始终不动。"""
    time = frame % 100 / 25
    falling = max(0,min(1,(time-.25)/1.35))
    rising = max(0,min(1,(time-2.35)/1.3))
    falling = falling**3*(10-15*falling+6*falling**2)
    rising = rising**3*(10-15*rising+6*rising**2)
    level = falling*(1-rising)
    normal = renderer.geometry('normal',0)
    symbol_ops = renderer.geometry('unavailable',0)[-2:]
    if level==0:
        return renderer.render(normal+symbol_ops,size)
    body = re.sub(r'^<svg[^>]*>|</svg>$','',renderer.svg([op for op in normal if op[0]!='ellipse']))
    ambient = re.sub(r'^<svg[^>]*>|</svg>$','',renderer.svg([op for op in normal if op[0]=='ellipse']+symbol_ops))

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
    document = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'+ambient+dim+mask+'<g mask="url(#energy)">'+body+'</g></svg>'
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
    for frame in range(100):
        sheet = Image.new('RGB', (960, 660), '#eef3f7')
        draw = ImageDraw.Draw(sheet)
        font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 16)
        heading = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 27)
        draw.text((28, 20), 'ICEGEM / 不可用 · 晶体失能', font=heading, fill='#294261')
        draw.text((28, 65), '完整晶体 / 内部光线退去、停顿、恢复 / 红色禁止符号固定', font=font, fill='#536b80')
        renderer = renderers['IceBlue']
        for column, (background, ink) in enumerate((('#fafcfe', '#294261'), ('#172638', '#dcefff'))):
            x = 20 + column * 470
            draw.rectangle((x, 106, x+450, 443), fill=background)
            draw.text((x+25, 121), '当前主指针                      失能动画 / 5 倍', font=font, fill=ink)
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
            sheet.save(OUT / 'unavailable-dim-motion.png')
        frames.append(sheet.quantize(colors=256))
        if frame % 25 == 0:
            print(f'Rendered {frame+1}/100', flush=True)
    frames[0].save(OUT / 'unavailable-dim-motion.gif', save_all=True,
                   append_images=frames[1:], duration=40, loop=0, disposal=2)
    print(OUT, flush=True)


if __name__ == '__main__':
    main()
