"""IceGem 4.5 后台运行连续晶体弧环提案：仅导出视觉预览，不更新正式资源或 Linux 包。"""
import math
import importlib.util
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'preview/working-4.5-crystal-arc'
# 主体 1.6 秒与晶片环 2.4 秒在 4.8 秒闭合，预览按 25fps 采样。
FRAME_COUNT = 120
COLORS = ('IceBlue', 'Violet', 'RosePink', 'Mint', 'Amber')


def proposal(renderer, frame, size):
    """保持主晶体不变，以有缺口、厚度和连续切面的晶体弧环表示后台运行。"""
    ops = renderer.geometry('working', round(frame * 2.4) % 96, working_base=True)
    boundary = next(i for i, op in enumerate(ops) if op[0] == 'ellipse' and op[1] == (25, 11.5, 4.1, 4.1))
    ops = ops[:boundary]
    phase = frame % 60 / 60 * math.tau
    # 276 度连续环体、84 度开口；三道同心棱线构成宽面、倒角与内缘。
    angles = [phase - math.pi / 2 + math.radians(i * 27.6) for i in range(11)]
    outer = [(25 + 4.05 * math.cos(a), 11.5 + 4.05 * math.sin(a)) for a in angles]
    ridge = [(25 + 3.6 * math.cos(a), 11.5 + 3.6 * math.sin(a)) for a in angles]
    inner = [(25 + 2.5 * math.cos(a), 11.5 + 2.5 * math.sin(a)) for a in angles]
    outline = outer + inner[::-1]
    # 后侧厚度只从实体轮廓下沿露出，不添加完整底圈或悬浮碎片。
    back = [(x + .12, y + .38) for x, y in outline]
    ops.append(('poly', back, '#5b75ae', '#344f7b', .28))
    ops.append(('poly', outline, 'url(#clearIce)', None, 0))
    for index in range(10):
        mid = (angles[index] + angles[index + 1]) / 2
        # 固定左上光源下，转动的晶面连续变亮变暗；淡紫侧面保留 IceGem 折射色。
        light = .5 + .5 * math.cos(mid + 2.35)
        base = (63, 109, 172) if index % 3 else (100, 110, 179)
        rgb = [round(c + (241 - c) * (.16 + .72 * light)) for c in base]
        face = '#' + ''.join(f'{value:02x}' for value in rgb)
        ops.append(('poly', [outer[index], outer[index+1], ridge[index+1], ridge[index]], 'url(#clearIce)', None, 0))
        ops.append(('poly', [ridge[index], ridge[index+1], inner[index+1], inner[index]], face, None, 0))
        # 每段仅一个低强度折射三角面，保持连续环的整体感。
        ops.append(('poly', [ridge[index], inner[index+1], inner[index]], '#e5faff' + f'{round(15+45*light):02x}', None, 0))
        ops.append(('line', [ridge[index], ridge[index+1]], None, '#efffff' + f'{round(75+150*light):02x}', .18))
    ops.append(('line', outer, None, '#375785', .28))
    ops.append(('line', inner, None, '#42629a', .24))
    # 开口两端有明确截面，避免看起来像断开的进度条笔画。
    for index in (0, -1):
        ops.append(('line', [outer[index], inner[index]], None, '#375785', .3))
        ops.append(('line', [ridge[index], inner[index]], None, '#e8faff', .15))
    return renderer.render(ops, size)


def main():
    """输出新旧对比、深浅背景、原尺寸与五色动画，供设计确认后再实施。"""
    OUT.mkdir(parents=True, exist_ok=True)
    renderers = {}
    for color in COLORS:
        spec = importlib.util.spec_from_file_location(color, ROOT / f'variants/{color}/tools/build.py')
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        renderers[color] = renderer
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 16)
    heading = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 27)
    frames = []
    for frame in range(FRAME_COUNT):
        sheet = Image.new('RGB', (960, 680), '#eef3f7')
        draw = ImageDraw.Draw(sheet)
        draw.text((28, 20), 'ICEGEM 4.5 / 后台运行 · 三晶分离', font=heading, fill='#294261')
        stage = '分离 → 就位' if frame < 40 else ('就位 → 环绕旋转' if frame < 121 else '回收 → 融入主体')
        draw.text((28, 65), f'{stage} / 同源晶体切面 / Windows 视觉提案', font=font, fill='#536b80')
        for column, (bg, ink) in enumerate((('#f9fbfd', '#294261'), ('#172638', '#dcefff'))):
            x = 20 + column * 470
            draw.rectangle((x, 106, x + 450, 458), fill=bg)
            draw.text((x + 30, 120), '原标识                            三晶分离 / 放大 5 倍', font=font, fill=ink)
            old = renderers['IceBlue'].render(renderers['IceBlue'].geometry('working', round(frame * 2.4) % 96, working_base=True), 160)
            new = proposal(renderers['IceBlue'], frame, 160)
            sheet.paste(old, (x + 24, 158), old)
            sheet.paste(new, (x + 246, 158), new)
            draw.text((x + 20, 337), '实际尺寸', font=font, fill=ink)
            for index, size in enumerate((32, 48, 64)):
                small = proposal(renderers['IceBlue'], frame, size)
                sheet.paste(small, (x + 95 + index * 110, 371), small)
                draw.text((x + 93 + index * 110, 343), f'{size}px', font=font, fill=ink)
        draw.text((28, 478), '五色材质 / loading 高度约为主晶体的三分之一', font=font, fill='#294261')
        for index, (color, renderer) in enumerate(renderers.items()):
            cursor = proposal(renderer, frame, 120)
            x = 28 + index * 188
            sheet.paste(cursor, (x + 20, 510), cursor)
            draw.text((x + 25, 645), color, font=font, fill='#294261')
        frames.append(sheet)
    frames[65].save(OUT / 'working-crystal-ring.png')
    frames[0].save(OUT / 'working-crystal-ring.gif', save_all=True, append_images=frames[1:], duration=40, loop=0, disposal=2)
    frames[0].save(OUT / 'working-crystal-ring.webp', save_all=True, append_images=frames[1:], duration=40, loop=0, lossless=True)
    print(OUT, flush=True)


if __name__ == '__main__':
    main()
