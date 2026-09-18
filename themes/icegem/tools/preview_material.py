"""对照初版 4.4 和统一材质，在浅、中、深背景按原始像素尺寸检查可读性。"""
from pathlib import Path
import importlib.util
import subprocess
import types
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
# 琥珀为当前使用配色，冰蓝用于确认原有冷色宝石材质没有失真。
renderers={}
for color in ('Amber','IceBlue'):
    path=ROOT/f'variants/{color}/tools/build.py'
    spec=importlib.util.spec_from_file_location(color,path)
    current=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(current)
    baseline=types.ModuleType('release_44_'+color)
    baseline.__file__=str(path)
    source=subprocess.check_output(['git','show',f'2c18de8:themes/icegem/variants/{color}/tools/build.py'],cwd=ROOT)
    exec(compile(source,str(path),'exec'),baseline.__dict__)
    renderers[color]=(baseline,current)

def comparison(frame):
    """左右分别展示原版和新版，不放大光标；每行使用相同原生尺寸。"""
    sheet=Image.new('RGB',(768,396),'#edf2f6')
    for color_index,(color,versions) in enumerate(renderers.items()):
        for background,bg in enumerate(('#ffffff','#b9c5ce','#172638')):
            column=color_index*3+background
            for row,size in enumerate((32,48,64)):
                tile=Image.new('RGB',(128,132),bg)
                ink='#dcefff' if background==2 else '#294261'
                draw=ImageDraw.Draw(tile)
                draw.text((5,4),f'{color} / {size}px',fill=ink)
                draw.text((5,23),'OLD      NEW',fill=ink)
                for index,renderer in enumerate(versions):
                    cursor=renderer.render(renderer.geometry('normal',frame),size)
                    tile.paste(cursor,(index*64+(64-size)//2,48),cursor)
                sheet.paste(tile,(column*128,row*132))
    return sheet

if __name__=='__main__':
    comparison(36).save(ROOT/'preview/material-comparison-4.4.png')
    # 保留正常光标的真实 ANI 帧时长及停顿，让材质对比反映日常运动节奏。
    frames=[comparison(frame) for frame in range(97)]
    durations=[round((i+1)*1000/60)-round(i*1000/60) for i in range(96)]+[1600]
    frames[0].save(ROOT/'preview/material-comparison-4.4.webp',save_all=True,
                   append_images=frames[1:],duration=durations,loop=0,lossless=True)
    print('Unified material comparison exported',flush=True)
