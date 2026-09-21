"""不规则断裂预览：非均匀多边形碎块、散开间隙、原主体材质和固定红色标识。"""
import math
import re
from functools import lru_cache
import preview_unavailable_fracture_motion as preview

# 不均匀断裂中心形成大小悬殊的自然多边形，避免三角网格和环形排列。
SEEDS = ((6.8,5.2),(8.5,10.1),(7.5,13.7),(12.8,12.9),(10.6,15),
         (16.4,16.1),(7.8,18.6),(11.9,18.3),(15,20.7),(10.1,21.9),
         (17.1,23.5),(15.9,25.8))
OUTLINE = ((6,3),(19,16.8),(17,27),(6.7,19.8))


@lru_cache(maxsize=1)
def fracture_cells():
    """通过半平面裁切原轮廓生成共享断口，无空洞、无重复覆盖的 Voronoi 分区。"""
    cells = []
    for sx,sy in SEEDS:
        polygon = list(OUTLINE)
        for tx,ty in SEEDS:
            if (sx,sy)==(tx,ty):
                continue
            nx,ny = tx-sx,ty-sy
            bound = (tx*tx+ty*ty-sx*sx-sy*sy)/2
            clipped = []
            for a,b in zip(polygon,polygon[1:]+polygon[:1]):
                da,db = a[0]*nx+a[1]*ny-bound,b[0]*nx+b[1]*ny-bound
                if da<=0:
                    clipped.append(a)
                if (da<=0)!=(db<=0):
                    ratio = da/(da-db)
                    clipped.append((a[0]+(b[0]-a[0])*ratio,a[1]+(b[1]-a[1])*ratio))
            polygon = clipped
        cells.append(tuple(polygon))
    return tuple(cells)


def pose(index, spread):
    """以断裂中心决定外移方向，尖端固定；不叠加会造成交叠的旋转与随机抖动。"""
    sx,sy = SEEDS[index]
    return (0,0) if index==0 else (.68*(sx-12)*spread,.19*(sy-5)*spread)


def validate_spacing():
    """用凸多边形分离轴检查整个展开路径，拒绝碎块交叠或越过画布边界。"""
    cells = fracture_cells()
    for step in range(1,101):
        spread = step/100
        polygons = []
        for index,cell in enumerate(cells):
            dx,dy = pose(index,spread)
            polygon = [(x+dx,y+dy) for x,y in cell]
            assert all(0<x<31.5 and 0<y<31.5 for x,y in polygon), (step,index,'bounds')
            polygons.append(polygon)
        for i,a in enumerate(polygons):
            for j,b in enumerate(polygons[:i]):
                separate = False
                for polygon in (a,b):
                    for p,q in zip(polygon,polygon[1:]+polygon[:1]):
                        nx,ny = p[1]-q[1],q[0]-p[0]
                        pa,pb = [x*nx+y*ny for x,y in a],[x*nx+y*ny for x,y in b]
                        if max(pa)<=min(pb)+1e-7 or max(pb)<=min(pa)+1e-7:
                            separate = True
                            break
                    if separate:
                        break
                assert separate, (step,i,j,'overlap')
    print('PASS: 100 expansion positions, no overlapping fragments',flush=True)


@lru_cache(maxsize=128)
def proposal(renderer,size,frame=0):
    """从当前 normal 晶体裁切多边形残片，连续散开并原路复原，保留固定禁止符号。"""
    time = frame%100/25
    opening = max(0,min(1,(time-.4)/.85))
    closing = max(0,min(1,(time-2.5)/.7))
    progress = opening*(1-closing)
    spread = progress**3*(10-15*progress+6*progress**2)
    normal = renderer.geometry('normal',0)
    symbol = renderer.geometry('unavailable',0)[-2:]
    if spread==0:
        return renderer.render(normal+symbol,size)
    body = re.sub(r'^<svg[^>]*>|</svg>$','',renderer.svg([op for op in normal if op[0]!='ellipse']))
    ambient = re.sub(r'^<svg[^>]*>|</svg>$','',renderer.svg([op for op in normal if op[0]=='ellipse']))
    sign = re.sub(r'^<svg[^>]*>|</svg>$','',renderer.svg(symbol))
    pieces = []
    for index,cell in enumerate(fracture_cells()):
        dx,dy = pose(index,spread)
        points = ' '.join(f'{x},{y}' for x,y in cell)
        fragment = re.sub(r'id="([^"]+)"',lambda m:f'id="piece{index}_{m[1]}"',body)
        fragment = re.sub(r'url\(#([^)]+)\)',lambda m:f'url(#piece{index}_{m[1]})',fragment)
        # 细暗断面与局部亮边只出现在断开后，不把所有碎片描成厚边小宝石。
        edge = renderer.theme_svg(f'<polygon points="{points}" fill="none" stroke="#52749a" stroke-width=".24"/><polyline points="{points}" fill="none" stroke="#e2f7ff" stroke-width=".09"/>')
        pieces.append(f'<g transform="translate({dx} {dy})"><defs><clipPath id="cut{index}"><polygon points="{points}"/></clipPath></defs><g clip-path="url(#cut{index})">{fragment}<g opacity="{spread}">{edge}</g></g></g>')
    document = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'+ambient+''.join(pieces)+sign+'</svg>'
    return renderer.raster(document,size)


if __name__=='__main__':
    validate_spacing()
    preview.OUT = preview.ROOT/'preview/unavailable-irregular-motion'
    preview.proposal = proposal
    preview.main()
