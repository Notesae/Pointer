"""生成水晶展台文本指针的独立动效提案，不修改正式光标与发行包。"""
import math
import importlib.util
from PIL import Image, ImageDraw, ImageFont
from preview_text_asymmetric import ROOT, crystal

# 独立输出目录保留此前设计，供用户比较；一轮 3 秒，以 25fps 展示。
OUT = ROOT / 'preview/text-pedestal-compact-v2'
FRAME_COUNT = 75


def proposal(renderer, frame, size):
    """以固定六角晶台和棱柱承托浮动晶石，上端叠加纵轴自转与中心倾摆。"""
    phase = (frame % FRAME_COUNT) / FRAME_COUNT * math.tau
    # 平滑周期运动只作用于上端；中心热点所在支撑柱与底座始终固定。
    lift = -.7 * math.sin(phase)
    tilt = 7 * math.sin(phase + .6)
    # 同一组透色材质用于台面、倒角与棱柱；各切面的明暗随朝向而非宽幅白带变化。
    stand = renderer.theme_svg('''<defs>
      <linearGradient id="ice" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#e7fbff" stop-opacity=".82"/><stop offset=".45" stop-color="#a6d9ef" stop-opacity=".38"/><stop offset="1" stop-color="#6395cd" stop-opacity=".64"/></linearGradient>
      <linearGradient id="lilac" x1="0" y1="1" x2="1" y2="0"><stop stop-color="#6878b6" stop-opacity=".7"/><stop offset=".55" stop-color="#bbc7ed" stop-opacity=".32"/><stop offset="1" stop-color="#e7eaff" stop-opacity=".72"/></linearGradient>
      <linearGradient id="refract" x1="0" y1="0" x2="1" y2=".8"><stop stop-color="#7bb9e1" stop-opacity=".16"/><stop offset=".48" stop-color="#ecffff" stop-opacity=".82"/><stop offset=".53" stop-color="#9cd2e9" stop-opacity=".27"/><stop offset="1" stop-color="#a1a5e0" stop-opacity=".48"/></linearGradient>
      <!-- 固定左上光源：各表面独立明暗，底缘压暗，柱身使用连续色阶表现透光深度。 -->
      <linearGradient id="tableLight" x1="0" y1="0" x2=".8" y2="1"><stop stop-color="#ecffff" stop-opacity=".9"/><stop offset=".58" stop-color="#b6e0f4" stop-opacity=".62"/><stop offset="1" stop-color="#86a7d1" stop-opacity=".65"/></linearGradient>
      <linearGradient id="frontLight" x1="0" y1="0" x2=".25" y2="1"><stop stop-color="#d7f7ff" stop-opacity=".88"/><stop offset=".3" stop-color="#94c4e5" stop-opacity=".66"/><stop offset="1" stop-color="#496d9e" stop-opacity=".78"/></linearGradient>
      <linearGradient id="rightShade" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#84a9d5" stop-opacity=".7"/><stop offset=".65" stop-color="#46689b" stop-opacity=".8"/><stop offset="1" stop-color="#797bb7" stop-opacity=".66"/></linearGradient>
      <linearGradient id="columnLight" x1="0" y1="0" x2=".8" y2="1"><stop stop-color="#d2f5ff" stop-opacity=".84"/><stop offset=".3" stop-color="#8bbbe0" stop-opacity=".5"/><stop offset=".62" stop-color="#e4faff" stop-opacity=".9"/><stop offset="1" stop-color="#88a9d4" stop-opacity=".72"/></linearGradient>
      <linearGradient id="columnShade" x1="0" y1="0" x2=".7" y2="1"><stop stop-color="#5378a8" stop-opacity=".78"/><stop offset=".45" stop-color="#a3b8e0" stop-opacity=".5"/><stop offset="1" stop-color="#4b699c" stop-opacity=".8"/></linearGradient>
      </defs>
      <!-- 仅保留外壳与互不重叠的表面切面，去掉内部骨架和交叉光带产生的杂质重影。 -->
      <!-- 底座在上版基础上再缩小 15%，累计为原尺寸的 72.25%，固定柱脚连接点。 -->
      <g transform="translate(16 25) scale(.7225) translate(-16 -25)">
      <path d="M10 25 L13 23.8 L19 23.8 L22 25 L22 27.1 L19.4 28.5 L12.6 28.5 L10 27.1 Z" fill="#aed9ed" fill-opacity=".25"/>
      <!-- 台面仅通过大块透色切面表现折射，不叠加柱脚或内部零件形状。 -->
      <path d="M10 25 L13 23.8 L15.6 25.6 L13 26.4 Z" fill="url(#tableLight)"/>
      <path d="M13 23.8 L19 23.8 L15.6 25.6 Z" fill="#d8f6ff" fill-opacity=".68"/>
      <path d="M19 23.8 L22 25 L19 26.4 L15.6 25.6 Z" fill="url(#lilac)"/>
      <path d="M13 26.4 L15.6 25.6 L19 26.4 Z" fill="#82b6da" fill-opacity=".6"/>
      <path d="M10 25 L13 26.4 L12.6 28.5 L10 27.1 Z" fill="url(#frontLight)"/>
      <path d="M13 26.4 L19 26.4 L16.8 27.45 L12.6 28.5 Z" fill="url(#frontLight)"/>
      <path d="M19 26.4 L19.4 28.5 L12.6 28.5 L16.8 27.45 Z" fill="url(#rightShade)"/>
      <path d="M19 26.4 L22 25 L22 27.1 L19.4 28.5 Z" fill="url(#rightShade)"/>
      <path d="M10 25 L13 23.8 L19 23.8 L22 25 L22 27.1 L19.4 28.5 L12.6 28.5 L10 27.1 Z" fill="none" stroke="#476d99" stroke-opacity=".72" stroke-width=".25"/>
      <path d="M10.2 25 L13.1 23.95 L18.8 23.95 M10.15 25.1 L13 26.4 L19 26.4 L21.85 25.1 M12.8 28.25 L19.3 28.25" fill="none" stroke="#efffff" stroke-opacity=".87" stroke-width=".2"/>
      <path d="M13 26.4 L12.6 28.3 M19 26.4 L19.4 28.3" fill="none" stroke="#b4d9f6" stroke-width=".16"/>
      <!-- 柱体直接连接台面，连续纵向切面代替内部三角碎片与独立底脚。 -->
      </g>
      <path d="M15.05 14.5 L16 14.1 L16.95 14.5 L17.1 24.4 L16 25 L14.9 24.4 Z" fill="#b0ddef" fill-opacity=".35"/>
      <path d="M15.05 14.5 L15.5 14.75 L15.65 24.65 L14.9 24.4 Z" fill="#648bb9" fill-opacity=".7"/>
      <path d="M15.5 14.75 L16 14.1 L16 25 L15.65 24.65 Z" fill="url(#columnLight)"/>
      <path d="M16 14.1 L16.95 14.5 L16.45 24.7 L16 25 Z" fill="url(#columnShade)"/>
      <path d="M16.95 14.5 L17.1 24.4 L16.45 24.7 Z" fill="#5679ad" fill-opacity=".62"/>
      <path d="M15.05 14.5 L16 14.1 L16.95 14.5 L17.1 24.4 L16 25 L14.9 24.4 Z" fill="none" stroke="#6383ac" stroke-opacity=".68" stroke-width=".19"/>
      <path d="M15.12 14.7 L14.99 24.2 M15.55 14.9 L15.68 24.5" fill="none" stroke="#f0ffff" stroke-opacity=".9" stroke-width=".14"/>
      <!-- 柱顶承托台与底座共享透明斜面，保持材料连续。 -->
      <path d="M13.9 14.2 L16 13.55 L18.1 14.2 L17.6 15.05 L16 15.5 L14.4 15.05 Z" fill="url(#lilac)" stroke="#6383ab" stroke-width=".2"/>
      <path d="M13.9 14.2 L16 13.55 L16.25 14.6 L16 14.9 Z" fill="url(#ice)"/>
      <path d="M16 13.55 L18.1 14.2 L16 14.9 L16.25 14.6 Z" fill="url(#refract)"/>
      <path d="M14.15 14.3 L16 14.9 L17.85 14.3 M14.45 15 L16 15.35" fill="none" stroke="#efffff" stroke-opacity=".8" stroke-width=".16"/>''')
    # 柔和反光仅落在现有表面，以连续透明度变化呼应晶石运动，不添加内部物体或交叉光带。
    reflection = .1 + .1 * (.5 + .5 * math.sin(phase - .4))
    stand += renderer.theme_svg(f'''<defs>
      <linearGradient id="surfaceReflection" x1="0" y1="0" x2=".8" y2="1"><stop stop-color="#f0ffff" stop-opacity=".8"/><stop offset=".55" stop-color="#c8eeff" stop-opacity=".18"/><stop offset="1" stop-color="#b4c4ef" stop-opacity="0"/></linearGradient>
      </defs><g opacity="{reflection:.4f}">
      <path d="M15.5 14.75 L16 14.1 L16 25 L15.65 24.65 Z" fill="url(#surfaceReflection)"/>
      <path d="M15.55 14.9 L15.68 24.5" fill="none" stroke="#efffff" stroke-width=".22"/>
      <!-- 表面反光与底座共用缩放中心，避免高光越出缩小后的轮廓。 -->
      <g transform="translate(16 25) scale(.7225) translate(-16 -25)">
      <path d="M10 25 L13 23.8 L15.6 25.6 L13 26.4 Z" fill="url(#surfaceReflection)"/>
      <path d="M10.2 25.1 L13 26.4 L18.8 26.4" fill="none" stroke="#efffff" stroke-width=".22"/>
      </g>
      </g>''')
    # 自转复用已认可的主晶石材质，浮动与倾摆围绕晶石中点，不牵动展台。
    transform = (f'translate(0 {lift:.4f}) rotate({tilt:.4f} 16 7.4) '
                 'translate(16 2.3) rotate(24.624) scale(.39) translate(-6 -3)')
    top = crystal(renderer, int(frame % FRAME_COUNT * 96 / FRAME_COUNT), transform, 'top')
    document = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">' + stand + top + '</svg>'
    return renderer.raster(document, size)


def main():
    """输出动画、静态图与关键帧，检查五色材质和 32/48/64px 下的完整结构。"""
    OUT.mkdir(parents=True, exist_ok=True)
    renderers = {}
    for color in ('IceBlue', 'Violet', 'RosePink', 'Mint', 'Amber'):
        spec = importlib.util.spec_from_file_location(color, ROOT / f'variants/{color}/tools/build.py')
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        renderers[color] = renderer
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 17)
    heading = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 27)
    frames = []
    for frame in range(FRAME_COUNT):
        sheet = Image.new('RGB', (880, 680), '#eef3f7')
        draw = ImageDraw.Draw(sheet)
        draw.text((28, 20), 'ICEGEM / 水晶展台 · 切面光影', font=heading, fill='#294261')
        draw.text((28, 64), '切面底座 + 支撑柱 / 上端自转、浮动、倾摆 / 仅设计预览', font=font, fill='#536b80')
        for column, (bg, ink) in enumerate((('#f9fbfd', '#294261'), ('#172638', '#dcefff'))):
            x = 20 + column * 430
            draw.rectangle((x, 106, x + 410, 458), fill=bg)
            draw.text((x + 18, 120), '放大结构与动效', font=font, fill=ink)
            cursor = proposal(renderers['IceBlue'], frame, 240)
            sheet.paste(cursor, (x + 84, 144), cursor)
            for index, size in enumerate((32, 48, 64)):
                small = proposal(renderers['IceBlue'], frame, size)
                sheet.paste(small, (x + 64 + index * 110, 383), small)
                draw.text((x + 62 + index * 110, 363), f'{size}px', font=font, fill=ink)
        draw.text((28, 480), '五色材质 / 底座与支撑柱固定，上端晶石独立运动', font=font, fill='#294261')
        for index, (color, renderer) in enumerate(renderers.items()):
            cursor = proposal(renderer, frame, 120)
            x = 30 + index * 170
            sheet.paste(cursor, (x + 14, 510), cursor)
            draw.text((x + 22, 643), color, font=font, fill='#294261')
        frames.append(sheet)
    frames[12].save(OUT / 'crystal-pedestal.png')
    frames[0].save(OUT / 'crystal-pedestal.gif', save_all=True, append_images=frames[1:], duration=40, loop=0, disposal=2)
    frames[0].save(OUT / 'crystal-pedestal.webp', save_all=True, append_images=frames[1:], duration=40, loop=0, lossless=True)
    # 输出四个时间点便于直接审核运动幅度及晶石与柱顶的间隙。
    storyboard = Image.new('RGB', (640, 190), '#172638')
    for index, frame in enumerate((0, 19, 38, 56)):
        cursor = proposal(renderers['IceBlue'], frame, 160)
        storyboard.paste(cursor, (index * 160, 0), cursor)
        ImageDraw.Draw(storyboard).text((index * 160 + 50, 166), f'{frame * .04:.2f}s', font=font, fill='#dcefff')
    storyboard.save(OUT / 'keyframes.png')
    print(OUT, flush=True)


if __name__ == '__main__':
    main()
