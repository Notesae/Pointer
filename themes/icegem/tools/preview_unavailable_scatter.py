"""细碎、错时散开的晶体破碎预览；复用已确认主体与固定红色禁止符号。"""
import math
import re
from functools import lru_cache
import preview_unavailable_fracture_motion as preview


@lru_cache(maxsize=128)
def proposal(renderer, size, frame=0):
    """将主体分成不等大的三角碎片，按固定轨迹错时散开并复原，尖端不动。"""
    time = frame % 100 / 25
    normal = renderer.geometry('normal', 0)
    symbol_ops = renderer.geometry('unavailable', 0)[-2:]
    if time <= .4 or time >= 3.4:
        return renderer.render(normal + symbol_ops, size)
    body = re.sub(r'^<svg[^>]*>|</svg>$', '', renderer.svg([op for op in normal if op[0] != 'ellipse']))
    backdrop = re.sub(r'^<svg[^>]*>|</svg>$', '', renderer.svg([op for op in normal if op[0] == 'ellipse'] + symbol_ops))
    # 非均匀节点沿原主体外轮廓铺开，避免规则棋盘式切割；最上端三角形固定热点。
    vertices = ((6,3),(6.25,9),(11.65,9),(9.1,12),(6.48,14.5),(16.83,14.5),
                (12.7,16),(9.2,18),(15.3,20),(19,16.8),(17,27),(6.7,19.8),(12,23.505))
    triangles = ((0,1,2),(1,2,3),(1,3,4),(2,5,3),(3,5,6),
                 (4,3,7),(3,6,7),(5,9,6),(9,8,6),(9,10,8),
                 (6,8,7),(7,8,12),(7,12,11),(4,7,11),(8,10,12))
    # 每块有独立方向和旋角，较小碎片飞得更散；右上区域留给固定禁止符号。
    motions = ((0,0,0),(-1.1,-1.5,-24),(-3.1,.1,-37),(2.3,-1.1,31),
               (.8,-.5,-23),(-2.5,.9,26),(-.5,1.2,-42),(2.4,.2,35),
               (3.3,1.6,-27),(3.4,2.2,19),(.4,2.2,48),
               (-.6,3.1,-31),(-2.8,2.6,29),(-3.8,1.8,-21),(1.1,2.1,-18))
    fragments = []
    for index, (indices, (dx,dy,angle)) in enumerate(zip(triangles,motions)):
        delay = (index * 7 % 5) * .035
        opening = max(0,min(1,(time-.4-delay)/.75))
        closing = max(0,min(1,(time-2.5-delay)/.7))
        opening = opening**3*(10-15*opening+6*opening**2)
        closing = closing**3*(10-15*closing+6*closing**2)
        spread = opening*(1-closing) if index else 0
        points = [vertices[i] for i in indices]
        cx = sum(x for x,y in points)/3
        cy = sum(y for x,y in points)/3
        # 展开后保持轻微连续漂移，回收时随 spread 归零，不逐帧重采随机位置。
        drift = .18*math.sin(time*2.5+index)*spread
        transform = f'translate({dx*spread} {dy*spread+drift if index else 0}) rotate({angle*spread} {cx} {cy})'
        crystal = re.sub(r'id="([^"]+)"', lambda m:f'id="shard{index}_{m[1]}"', body)
        crystal = re.sub(r'url\(#([^)]+)\)', lambda m:f'url(#shard{index}_{m[1]})', crystal)
        polygon = ' '.join(f'{x},{y}' for x,y in points)
        # 薄断面仅在分离后出现，切面仍来自原晶体，不另画独立小宝石。
        edge = renderer.theme_svg(f'<polygon points="{polygon}" fill="none" stroke="#406396" stroke-width=".3"/><polyline points="{polygon}" fill="none" stroke="#e7fbff" stroke-width=".12"/>')
        fragments.append(f'<g transform="{transform}"><defs><clipPath id="cut{index}"><polygon points="{polygon}"/></clipPath></defs><g clip-path="url(#cut{index})">{crystal}<g opacity="{spread}">{edge}</g></g></g>')
    document = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">' + backdrop + ''.join(fragments) + '</svg>'
    return renderer.raster(document,size)


if __name__ == '__main__':
    # 沿用相同对比画板，独立输出细碎版本，不覆盖前一轮预览或正式资源。
    preview.OUT = preview.ROOT / 'preview/unavailable-scatter-motion'
    preview.proposal = proposal
    preview.main()
