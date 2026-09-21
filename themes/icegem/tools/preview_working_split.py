"""三枚同材质晶石从主指针分离并环绕：只生成设计预览，不修改正式资源。"""
import math
import re
from functools import lru_cache
from pathlib import Path
import preview_working_45 as preview


def crystal(renderer, frame, transform, prefix, tilt):
    """为小尺寸重绘大块透光切面，以固定左上光源计算转动中的亮面和窄棱反射。"""
    # 保持同源晶石轮廓，减少缩小后会互相干扰的细线；中间台面与深侧面表现厚度。
    turn = math.radians(tilt)
    spin = frame / 96 * math.tau
    ridge = 12.3 + 1.1 * math.sin(spin)
    vertices = [(6, 3), (19, 16.8), (17, 27), (6.7, 19.8),
                (ridge, 12.8), (15.2, 18.2), (12.4, 21.6)]
    facets = ((0, 1, 5, 4), (0, 4, 6, 3), (4, 5, 6), (1, 2, 5), (5, 2, 6), (3, 6, 2))
    normals = (-1.2, -2.8, -.7, .1, 1.2, 2.5)
    shapes = []
    for index, indices in enumerate(facets):
        # 法线随整体转向及自转偏移，反光保持连续，避免随机闪烁。
        facing = .5 + .5 * math.cos(turn + normals[index] + .35 * math.sin(spin) + 2.35)
        brightness = .22 + .64 * facing
        base = (45, 88, 151) if index in (3, 4, 5) else (77, 142, 190)
        tint = '#' + ''.join(f'{round(c + (245-c)*brightness):02x}' for c in base)
        points = ' '.join(f'{vertices[i][0]},{vertices[i][1]}' for i in indices)
        shapes.append(f'<polygon points="{points}" fill="{tint}"/>')
    # 透射层沿长轴渐变，只覆盖中央台面，保留深色厚度边而不把整颗晶石漂白。
    sheen = .18 + .38 * max(0, math.cos(turn + .3 * math.sin(spin) + 2.1))**6
    material = f'''<defs><linearGradient id="{prefix}_transmit" x1="0" y1="0" x2=".8" y2="1">
      <stop stop-color="#efffff" stop-opacity=".8"/>
      <stop offset=".48" stop-color="#b5e8ff" stop-opacity=".2"/>
      <stop offset="1" stop-color="#748cce" stop-opacity=".5"/>
      </linearGradient></defs>
      {''.join(shapes)}
      <path d="M6 3 L{ridge} 12.8 L15.2 18.2 L12.4 21.6 Z" fill="url(#{prefix}_transmit)"/>
      <path d="M6 3 L19 16.8 L17 27 L6.7 19.8 Z" fill="none" stroke="#426597" stroke-width=".7" stroke-linejoin="round"/>
      <path d="M6.5 4.4 L{ridge} 12.8 L12.4 21.6 L7.1 19.5 M{ridge} 12.8 L15.2 18.2 L18.5 16.8" fill="none" stroke="#eeffff" stroke-opacity=".72" stroke-width=".6"/>
      <path d="M6.8 4.5 L{ridge} 12.8 L15.2 18.2" fill="none" stroke="#f3ffff" stroke-opacity="{sheen}" stroke-width="1.1"/>
      <path d="M15.2 18.2 L17 26.5" stroke="#a0b6ec" stroke-width=".6"/>
      '''
    return f'<g transform="{transform}">{renderer.theme_svg(material)}</g>'


def ease(value):
    value = max(0, min(1, value))
    return value * value * (3 - 2 * value)


@lru_cache(maxsize=128)
def proposal(renderer, frame, size):
    """将分离、就位、双圈环绕、回收串成 6.4 秒闭环，保持主指针原有动画。"""
    time = frame / 25
    source_frame = round(frame * 2.4) % 96
    ops = renderer.geometry('working', source_frame, working_base=True)
    boundary = next(i for i, op in enumerate(ops)
                    if op[0] == 'ellipse' and op[1] == (25, 11.5, 4.1, 4.1))
    body = re.sub(r'^<svg[^>]*>|</svg>$', '', renderer.svg(ops[:boundary]))
    # 环绕在三枚全部抵达后才启动，两整圈后停在各自起点，方便原路回收。
    orbit = math.tau * 2 * ease((time - 1.6) / 3.2)
    pieces = []
    for index in range(3):
        departure = .12 + index * .24
        arrival = ease((time - departure) / .92)
        returning = ease((time - 4.85 - (2 - index) * .18) / .95)
        travel = arrival * (1 - returning)
        if travel < .001:
            continue
        angle = -math.pi / 2 + index * math.tau / 3 + orbit
        destination = (25 + 3.35 * math.cos(angle), 11.5 + 3.35 * math.sin(angle))
        # 起点位于主体内部；弧形路径依次向右侧三角阵位展开，不使用拖尾和碎屑。
        start = (12.4 + index * .45, 14.3 + index * 1.15)
        control = (19.5, 7.2 + index * 4.2)
        x = (1-travel)**2 * start[0] + 2*(1-travel)*travel*control[0] + travel**2*destination[0]
        y = (1-travel)**2 * start[1] + 2*(1-travel)*travel*control[1] + travel**2*destination[1]
        scale = .165 * ease(travel / .65)
        tilt = 24.624 + math.degrees(angle) * travel
        transform = f'translate({x} {y}) rotate({tilt}) scale({scale}) translate(-11.5 -15)'
        # 小晶石沿用主题配色，以专用的大切面材质保持原尺寸下的清晰度。
        gem = crystal(renderer, (source_frame + index * 21) % 96, transform, f'shard{index}', tilt)
        pieces.append(f'<g opacity="{ease(travel / .3)}">{gem}</g>')
    document = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">' + body + ''.join(pieces) + '</svg>'
    return renderer.raster(document, size)


if __name__ == '__main__':
    # 复用深浅背景、原尺寸及五色的统一预览画板，不触碰发布脚本和平台构建。
    preview.OUT = Path(__file__).resolve().parents[1] / 'preview/working-4.5-split-material'
    preview.FRAME_COUNT = 160
    preview.proposal = proposal
    preview.main()
