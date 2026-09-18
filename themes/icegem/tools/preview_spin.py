"""导出实际帧关键图与毫秒时序 WebP，检查纵轴自转、缓动和高光连续性。"""
from pathlib import Path
import importlib.util
import bisect
from PIL import Image, ImageDraw

# 复用正式生成器，保证预览与 ANI 使用同一几何和时间表。
root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("icegem_spin", root / "variants/IceBlue/tools/build.py")
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
sheet = Image.new("RGB", (768, 224), "#172638")
draw = ImageDraw.Draw(sheet)
for index in range(8):
    frame=round(index*(len(renderer.ANIMATIONS['normal'])-1)/8)
    crystal = renderer.render(renderer.geometry("normal", frame), 96)
    sheet.paste(crystal, (index * 96, 30), crystal)
    draw.text((index * 96 + 12, 145), str(round(renderer.motion_phase('normal',frame)*360)) + " deg", fill="#dcefff")
draw.text((16, 195), "ICEGEM / LONGITUDINAL SPIN + SWAY / ACTUAL ANI FRAMES", fill="#dcefff")
sheet.save(root / "preview/longitudinal-spin-4.4.png")

# WebP 保留约 16.67ms 的帧节奏和全彩渐变，避免 GIF 厘秒时长及调色板影响流畅度。
frames=[]
roles=('normal','working')
ends={}
for role in roles:
    elapsed=0
    ends[role]=[]
    for rate in renderer.ANIMATIONS[role]:
        elapsed+=rate
        ends[role].append(elapsed)
for tick in range(192):
    canvas=Image.new('RGB',(768,280),'#eef4f8')
    draw=ImageDraw.Draw(canvas)
    draw.text((16,12),'ICEGEM / 60 FPS / EASED SPIN + CONTINUOUS LIGHT',fill='#294261')
    for index in range(4):
        role=roles[index//2]
        dark=index%2==1
        frame=bisect.bisect_right(ends[role],tick%ends[role][-1])
        tile=Image.new('RGBA',(184,216),'#172638' if dark else '#ffffff')
        for size,y in ((96,12),(32,145)):
            crystal=renderer.render(renderer.geometry(role,frame),size)
            tile.alpha_composite(crystal,((184-size)//2,y))
        ImageDraw.Draw(tile).text((12,192),role+' / 96px + 32px',fill='#dcefff' if dark else '#294261')
        canvas.paste(tile.convert('RGB'),(index*192+4,44))
    frames.append(canvas)
durations=[round((tick+1)*1000/60)-round(tick*1000/60) for tick in range(192)]
frames[0].save(root/'preview/spin-lighting-4.4.webp',save_all=True,append_images=frames[1:],
               duration=durations,loop=0,lossless=True,method=4)
# 选取旋转中段，检查主切面的实体色彩与自然反射，不再展示外贴星形。
frames[36].save(root/'preview/spin-lighting-4.4.png')
