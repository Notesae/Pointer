"""使用正式 ANI 时间表导出全部 18 个角色的冰蓝动图，不修改光标或安装包。"""
import bisect
import importlib.util
from functools import lru_cache
from itertools import accumulate
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 总览覆盖后台三晶完整 6.4 秒周期，30fps 采样各角色独立的原生时钟。
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'preview/all-components-4.5-tail-drop'
FRAME_COUNT = 192


def main():
    """绘制深浅背景的放大与原尺寸总览，保留静态角色并输出 GIF 和静态封面。"""
    spec = importlib.util.spec_from_file_location('icegem_all', ROOT / 'variants/IceBlue/tools/build.py')
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    OUT.mkdir(parents=True, exist_ok=True)
    heading = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 27)
    label = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 15)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 12)
    ends = {role: list(accumulate(rates)) for role, rates in renderer.ANIMATIONS.items()}

    @lru_cache(maxsize=4096)
    def cursor(role, frame, size):
        """缓存独立角色帧，重复背景和短周期复用同一正式渲染结果。"""
        return renderer.render(renderer.geometry(role, frame), size)

    frames = []
    for tick in range(FRAME_COUNT):
        sheet = Image.new('RGB', (1260, 800), '#edf2f6')
        draw = ImageDraw.Draw(sheet)
        draw.text((26, 18), 'ICEGEM 4.5 / 全组件动态总览', font=heading, fill='#294261')
        # 从正式角色表读取数量，避免新增动画后总览标签仍显示旧数据。
        draw.text((28, 62), f'冰蓝 · {len(renderer.NAMES)} 种状态 / {len(renderer.ANIMATIONS)} 种原生动画 · 深浅背景 · 上方 80px / 下方 32px', font=label, fill='#536b80')
        for index, (role, title, slot) in enumerate(renderer.NAMES):
            x = 22 + index % 6 * 206
            y = 108 + index // 6 * 220
            draw.text((x + 4, y), title, font=label, fill='#294261')
            timing = ends.get(role)
            frame = bisect.bisect_right(timing, tick * 2 % timing[-1]) if timing else 0
            for offset, background in ((0, '#fafcfe'), (97, '#172638')):
                tile = Image.new('RGBA', (94, 154), background)
                tile.alpha_composite(cursor(role, frame, 80), (7, 4))
                tile.alpha_composite(cursor(role, frame, 32), (31, 108))
                sheet.paste(tile.convert('RGB'), (x + offset, y + 29))
            draw.text((x + 4, y + 190), role + (' · 静态' if not timing else ''), font=small, fill='#536b80')
        draw.text((28, 777), '正式渲染器与 ANI 时序采样 / 原生指针全状态，不含需鼠标触发的 Companion 交互', font=small, fill='#536b80')
        if tick == 65:
            sheet.save(OUT / 'icegem-all-components.png')
        # GIF 按帧量化以控制内存；累计厘秒取整使总时长精确保持 6.4 秒。
        frames.append(sheet.quantize(colors=256, method=Image.Quantize.MEDIANCUT))
        if tick % 32 == 0:
            print(f'Rendered {tick + 1}/{FRAME_COUNT}', flush=True)
    durations = [round((i+1)*100/30)*10 - round(i*100/30)*10 for i in range(FRAME_COUNT)]
    frames[0].save(OUT / 'icegem-all-components.gif', save_all=True,
                   append_images=frames[1:], duration=durations, loop=0, disposal=2)
    print(OUT, flush=True)


if __name__ == '__main__':
    main()
