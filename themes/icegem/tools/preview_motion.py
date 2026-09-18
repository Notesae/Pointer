"""将原生时间表及 Companion 导出帧封装为真实渲染预览。"""
from pathlib import Path
import importlib.util,bisect
from PIL import Image,ImageDraw,ImageFont
# 从脚本位置定位主题，允许在任意工作目录生成预览。
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('ice',root/'variants/IceBlue/tools/build.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
roles=('normal','link','working','busy','resize-ew','resize-ns','resize-nwse','resize-nesw','move','help','location','person')
# 以 30fps 采样真实渲染器与其时间表，放大与原尺寸同时检查。
frames=[]
for tick in range(96):
    canvas=Image.new('RGB',(960,450),'#eef4f8');d=ImageDraw.Draw(canvas)
    d.text((22,14),'ICEGEM 4.4  /  FIXED ANI MOTION',fill='#294261',font=ImageFont.load_default(size=20))
    for i,role in enumerate(roles):
        rates=m.ANIMATIONS[role];pos=(tick*2)%sum(rates)
        ends=[];total=0
        for rate in rates:total+=rate;ends.append(total)
        frame=bisect.bisect_right(ends,pos)
        x=16+(i%6)*158;y=55+(i//6)*192
        d.text((x,y),role,fill='#294261',font=ImageFont.load_default(size=14))
        for offset,bg in ((0,'#ffffff'),(72,'#172638')):
            tile=Image.new('RGBA',(70,138),bg)
            tile.alpha_composite(m.render(m.geometry(role,frame),64),(3,3))
            tile.alpha_composite(m.render(m.geometry(role,frame),32),(19,92))
            canvas.paste(tile.convert('RGB'),(x+offset,y+24))
    frames.append(canvas)
frames[0].save(root/'preview/native-motion-4.4.png')
frames[0].save(root/'preview/native-motion-4.4.gif',save_all=True,append_images=frames[1:],duration=[30,30,40]*32,loop=0)
# 交互预览来自 C# 运行时导出的帧，本文件只负责封装 GIF。
images=[Image.open(p).convert('RGB') for p in sorted((root/'companion/preview-frames').glob('frame-*.png'))]
images[20].save(root/'preview/companion-motion-4.2.png')
images[0].save(root/'preview/companion-motion-4.2.gif',save_all=True,append_images=images[1:],duration=[30,30,40]*20,loop=0)
print('Native and companion renderer previews exported')
