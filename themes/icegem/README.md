# IceGem · 冰晶宝石光标

> IceGem 4.5 使用原生固定 ANI：后台运行新增三晶分离与环绕，小晶体使用独立透光切面和随转向变化的高光。仅更新 Windows；Linux 保留 4.4，不再逐版同步构建。

冰蓝、紫罗兰、玫瑰粉、薄荷绿、琥珀五套配色，沿用修长晶体造型和加强版点击线条。

![五色预览](preview/colorways.png)

## 4.5 更新 · 三晶分离

- 不可用状态采用已确认的“固定尖端、尾部下垂”：熄光后转向垂直，蓄光后恢复倾角，红色禁止符号固定。125 帧 / 5 秒，热点不变，Static 保留首帧。[动态预览](preview/unavailable-tail-drop-motion/unavailable-tail-drop-motion.gif)。

- 三枚晶石依次从主指针分离，右侧就位后环绕两圈，再收回主体；热点保持固定。
- 小晶体采用清晰的大切面、中央透光层、暗侧厚度及连续变化的窄棱反光。
- 五色共用 160 帧 / 6.4 秒循环（25fps），ANI 按累计 jiffy 取整；Static 保留首帧。
- [已确认的材质与动画预览](preview/working-4.5-split-material/working-crystal-ring.gif)。
- 默认仅打包 Windows；Linux 历史包不变，手动构建需显式传入 `--with-linux`。

## 4.4 更新 · 晶体旋律

- 主体比例上长下短（68:32），纵轴自转与摆动同步；迎光、背光和面内反射随角度自然变化。
- 材质统一增强切面明暗、内部亮棱与集中反射，覆盖所有默认尺寸；不需要专用 32px 设置，安装入口不变。
- 主体以 60fps 输出，普通状态转动 1.6 秒后停留 1.6 秒；查看[全彩动态预览](preview/spin-lighting-4.4.webp)。
- Companion 新增随配色变化的冰晶托盘图标、暂停标记及带当前状态的分组菜单。
- 更新 Companion 前先从旧版托盘退出，再运行新包的 Start-Companion.cmd。

主体晶体在左右摆动基础上绕自身纵轴自转：使用带厚度的八面环带投影与固定光源，让切面、棱线和亮度随角度变化。尖端热点保持固定，三晶体等待动画不变。[自转关键帧](preview/longitudinal-spin-4.4.png) · [当前动效预览](preview/native-motion-4.4.gif)。

- 15 种原生动画：常态纵轴自转、后台三晶分离、三晶体等待、不可用失能下垂、链接、帮助、位置、人员、文本与竖排文本水晶展台、移动和四向缩放。
- 后台 160 帧 / 6.4 秒（25fps）、忙碌 36 帧 / 1.2 秒（30fps）；常态一轮 3.2 秒，包含静止停留。
- [Windows Companion](companion/)：可选双晶片跟随、悬停点亮、点击折射和拖动收束。安装原生主题后运行包内 `Start-Companion.cmd`，无需设置自启动。
- 文本选择采用水晶展台：切面底座为初始提案的 72.25%，支撑柱与中心热点固定，上端晶体自转、浮动和轻微倾摆。75 帧 / 3 秒，ANI 使用累计取整的 jiffy 时长；竖排文本整体旋转 90°，Static 保留首帧。精确、手写、替代选择保持静止，不可用状态采用固定热点下垂动画，这些角色也隐藏伴随装饰。
- [已确认的文本展台预览](preview/text-pedestal-compact-v2/crystal-pedestal.webp)；安装包内分色预览由正式渲染器输出。
- Windows 与 Linux 均提供原生动效；当前交互程序仅支持 Windows x64。
- [原生动效实帧预览](preview/native-motion-4.4.gif) · [交互绘制器预览](preview/companion-motion-4.2.gif)。

## 4.1 更新

- 后台运行：旋转单光弧、渐亮尾迹与晶体端点。
- 忙碌等待：双光弧环绕冰晶，强化运行状态辨识度。
- 五色 Windows / Linux 资源同步更新，保持原有热点及静态方案。

## Windows 下载与安装

[下载 4.5 五色完整安装包](dist/IceGem-4.5-Color-Collection.zip?raw=true)。解压完整文件夹后双击对应入口：

| 颜色 | 文件 |
|---|---|
| 冰蓝 | Install-IceBlue.cmd |
| 紫罗兰 | Install-Violet.cmd |
| 玫瑰粉 | Install-RosePink.cmd |
| 薄荷绿 | Install-Mint.cmd |
| 琥珀 | Install-Amber.cmd |

默认动态 multi 方案，无需管理员权限。每色注册独立静态/动态方案，已安装的颜色可在 Windows 鼠标属性 → 指针中切换。安装包内的 IceGem-Colors-Preview.html 支持五色动画预览与悬停测试。

## Linux / Zorin OS

[下载 Linux 4.4 完整安装包](dist/IceGem-4.4-Linux.tar.gz?raw=true) · [安装、换色、恢复与卸载说明](linux/)

五色动态/静态共十套原生 Xcursor 主题，支持 24/32/48/64/96px。解压后进入 `IceGem-Linux`，运行 `bash Install.sh`，默认应用冰蓝动态版、32px，无需 sudo。Linux 构建器与安装脚本位于 `linux/`，复用 `variants/` 中的配色渲染源码。Zorin 桌面显示、动画及多屏/DPI 尚待实机验收。

## 规格与目录

- 每色 18 种状态，32/48/64px 和多分辨率 CUR。
- 15 种角色提供各自帧数与时长的 ANI，所有帧使用固定热点；Static 方案仍全部使用 CUR。
- [查看五色忙碌动画](preview/busy-motion.gif)：每格上方为 64px、下方为 32px，分别展示浅色与深色背景；需要减少动态时安装 Static 方案。
- Link 保留原晶体＋高对比提示线并加入循环高光；文本采用已确认的紧凑水晶展台。
- `variants/<配色>/`：SVG 源文件、构建器、安装脚本、热点映射与校验记录。
- `preview/`：主题总览；`dist/`：可直接使用的完整安装包。
- 仓库不重复存放生成的 CUR/ANI、动画逐帧 SVG 和大体积内嵌预览 HTML；它们均在安装包中，也可从源码重建。

## 从源码构建

需要 Python 3、Pillow、CairoSVG 及 Cairo 系统库；预览生成还使用 DejaVu Sans 字体。推荐 Linux 构建环境。

```bash
python -m pip install -r themes/icegem/requirements.txt
python themes/icegem/tools/build_all.py
python themes/icegem/tools/test_motion.py
# Windows 编译可选交互程序后，默认只生成 Windows 安装包
# powershell -File themes/icegem/companion/Build.ps1
python themes/icegem/tools/package.py
# 仅在需要时显式构建 Linux：python themes/icegem/tools/package.py --with-linux
```

产物写入每种配色目录中的 cursors、src/animation、preview，随后自动检查 CUR/ANI 结构。此时该配色目录下 Install.cmd 可直接使用。仅查看静态源码无需安装依赖。

## 恢复与卸载

在解压包目录执行 `Install-IceBlue.cmd -Action Restore` 恢复首次安装前的指针；`Install-IceBlue.cmd -Action Uninstall` 恢复并卸载共同管理的所有 IceGem 配色。不同配色共用首次备份，支持已有 IceGem 版本更新。`Check-Link.cmd` 检查当前 Link 的文件与注册表映射。

## 验证与边界

不可用下垂动画通过 200 组确认稿逐像素对比（五色 × 八个关键帧 × 五档尺寸），并验证五色 125 帧中的热点可见性、固定红色符号及首尾一致；静态方案保留首帧，不移动热点。

4.5 后台三晶动画通过 200 组确认稿逐像素对比（五色 × 八个关键帧 × 五档尺寸）。五色全部 multi CUR/ANI 通过 480 次 Windows 原生加载；安装包验证覆盖当前源码、版本、资源和安装器哈希。未应用系统指针方案，桌面实际播放及跨 DPI 体验仍需安装后验收。Linux 4.4 历史包仅做完整性回归，不重新构建。

文本展台已通过 125 组已确认预览的逐像素对比，以及五色、双方向、多尺寸的热点、边界和循环衔接检查。Windows 的文本 CUR/ANI 通过 60 次 LoadImage 原生加载与 GetIconInfo 热点读取（五色 × 双方向 × 两种格式 × 三档尺寸）。本次未应用系统方案，桌面连续播放与跨 DPI 切换仍待实机验收。Linux 包执行结构、预乘 Alpha、时序、别名及哈希检查，当前 Windows 构建机未运行 libXcursor 原生加载。32/48/64 表示资源分辨率，不是显示大小选项；竖排文本无独立 Windows 全局槽位，系统方案不覆盖应用自行绘制的全部光标。

## 无动画稳定效果归档

保留 [4.0 Windows 原始包](dist/IceGem-4.0-Color-Collection.zip?raw=true) 的 **Static** 方案作为动效改造前的稳定外观基线。进入配色目录执行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\Install-IceGem.ps1 -Mode Static`，并退出 Companion，即所有角色使用静态 CUR，无跟随、点击或待机动效。4.0 发行包也包含动态选项，不能把整个版本称为无动画版本。历史提交及校验值见[根 README](../../README.md#icegem-无动画稳定基线)。

4.2 晶片已统一为固定右倾约 19 度的中心对称菱形轮廓、宽幅冰透切面和细亮棱，取消硬像素双描边。系统主体与透明伴随窗口仍是两个技术图层；本轮统一视觉材质并在合成前读取最新热点，未隐藏或替换系统主体。跨应用与跨 DPI 的实际观感仍需验收。

晶片朝向以设计稿为准：上尖端偏左、下尖端偏右，左右尖端成对，不复用主指针的箭头轮廓。伴行一低一高，拖动时第二片沿外侧弧线进入右下短列，松开沿原路径散开；不随鼠标移动方向旋转。悬停提亮晶片棱线，并在主体右侧展开三道双面折光，离开后平滑消退；此效果独立于点击开关。按下晶片轻收束，拖动时取消收束。32/48/64px 的完整拖动过渡已检查晶片间距和排列方向。


已确认的 4.2 交互效果：拖动按轮廓间的可见空隙对齐，第一片日常停靠外移 2px；晶片主高光位于左上，阴影切面位于右下。悬停在主体右侧采用加长、加宽的三道双面折光，在系统光标变为链接小手时触发，离开后淡出。点击为 80ms 单圈聚光和 240ms 四芒闪光，保留明暗切面，不叠加厚阴影或大片光晕。拖动释放不播放点击闪光。

最新确认效果：悬停折光贴近主体右缘，避开两颗小晶片；点击保持单圈聚光与 240ms 四芒闪光，增强尺寸、切面宽度及对比。深浅背景预览由正式程序绘制，发行交付仅更新 dist 压缩包。
