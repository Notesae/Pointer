# IceGem · 冰晶宝石光标

> 完整宝石方案已独立为 [Crystal 新主题](../crystal/)，不再作为 IceGem 4.3。IceGem 4.2 的交互动画保留为实验历史。

冰蓝、紫罗兰、玫瑰粉、薄荷绿、琥珀五套配色，沿用修长晶体造型和加强版点击线条。

![五色预览](preview/colorways.png)

## 4.2 更新 · 晶光随行

- 12 种原生动画：常态切面流光、后台单弧、忙碌双弧、链接、帮助、位置、人员、移动和四向缩放。
- 后台 48 帧 / 1.6 秒、忙碌 36 帧 / 1.2 秒，旋转均为 30fps；常态一轮 3.2 秒，包含静止停留。
- [Windows Companion](companion/)：可选双晶片跟随、悬停点亮、点击折射和拖动收束。安装原生主题后运行包内 `Start-Companion.cmd`，无需设置自启动。
- 文本、精确、手写、不可用等状态保持静止；这些角色也隐藏伴随装饰。
- Windows 与 Linux 均提供原生动效；当前交互程序仅支持 Windows x64。
- [原生动效实帧预览](preview/native-motion-4.2.gif) · [交互绘制器预览](preview/companion-motion-4.2.gif)。

## 4.1 更新

- 后台运行：旋转单光弧、渐亮尾迹与晶体端点。
- 忙碌等待：双光弧环绕冰晶，强化运行状态辨识度。
- 五色 Windows / Linux 资源同步更新，保持原有热点及静态方案。

## Windows 下载与安装

[下载 4.2 五色完整安装包](dist/IceGem-4.2-Color-Collection.zip?raw=true)。解压完整文件夹后双击对应入口：

| 颜色 | 文件 |
|---|---|
| 冰蓝 | Install-IceBlue.cmd |
| 紫罗兰 | Install-Violet.cmd |
| 玫瑰粉 | Install-RosePink.cmd |
| 薄荷绿 | Install-Mint.cmd |
| 琥珀 | Install-Amber.cmd |

默认动态 multi 方案，无需管理员权限。每色注册独立静态/动态方案，已安装的颜色可在 Windows 鼠标属性 → 指针中切换。安装包内的 IceGem-Colors-Preview.html 支持五色动画预览与悬停测试。

## Linux / Zorin OS

[下载 Linux 4.2 完整安装包](dist/IceGem-4.2-Linux.tar.gz?raw=true) · [安装、换色、恢复与卸载说明](linux/)

五色动态/静态共十套原生 Xcursor 主题，支持 24/32/48/64/96px。解压后进入 `IceGem-Linux`，运行 `bash Install.sh`，默认应用冰蓝动态版、32px，无需 sudo。Linux 构建器与安装脚本位于 `linux/`，复用 `variants/` 中的配色渲染源码。Zorin 桌面显示、动画及多屏/DPI 尚待实机验收。

## 规格与目录

- 每色 18 种状态，32/48/64px 和多分辨率 CUR。
- 12 种角色提供各自帧数与时长的 ANI，所有帧使用固定热点；Static 方案仍全部使用 CUR。
- [查看五色忙碌动画](preview/busy-motion.gif)：每格上方为 64px、下方为 32px，分别展示浅色与深色背景；需要减少动态时安装 Static 方案。
- Link 保留原晶体＋高对比提示线并加入循环高光；文本保持已缩小的尺寸。
- `variants/<配色>/`：SVG 源文件、构建器、安装脚本、热点映射与校验记录。
- `preview/`：主题总览；`dist/`：可直接使用的完整安装包。
- 仓库不重复存放生成的 CUR/ANI、动画逐帧 SVG 和大体积内嵌预览 HTML；它们均在安装包中，也可从源码重建。

## 从源码构建

需要 Python 3、Pillow、CairoSVG 及 Cairo 系统库；预览生成还使用 DejaVu Sans 字体。推荐 Linux 构建环境。

```bash
python -m pip install -r themes/icegem/requirements.txt
python themes/icegem/tools/build_all.py
python themes/icegem/tools/test_motion.py
# Windows 编译可选交互程序后，生成两平台安装包
# powershell -File themes/icegem/companion/Build.ps1
python themes/icegem/tools/package.py
```

产物写入每种配色目录中的 cursors、src/animation、preview，随后自动检查 CUR/ANI 结构。此时该配色目录下 Install.cmd 可直接使用。仅查看静态源码无需安装依赖。

## 恢复与卸载

在解压包目录执行 `Install-IceBlue.cmd -Action Restore` 恢复首次安装前的指针；`Install-IceBlue.cmd -Action Uninstall` 恢复并卸载共同管理的所有 IceGem 配色。不同配色共用首次备份，支持已有 IceGem 版本更新。`Check-Link.cmd` 检查当前 Link 的文件与注册表映射。

## 验证与边界

二进制结构、透明轮廓、热点及动画帧检查已通过。本次五色光标通过 450 次 Windows LoadImage 的 32/48/64px 原生加载检查；后台运行与忙碌另外通过 24/32/48/64/96px 边界、热点、逐帧差异及循环衔接检查。Companion 通过运动模型及透明窗口冒烟测试。Windows 安装、桌面连续播放和跨 DPI 切换仍未实机验收。32/48/64 表示资源分辨率，不是显示大小选项。竖排文本无独立全局槽位，系统方案不覆盖应用自行绘制的全部光标。

## 无动画稳定效果归档

保留 [4.0 Windows 原始包](dist/IceGem-4.0-Color-Collection.zip?raw=true) 的 **Static** 方案作为动效改造前的稳定外观基线。进入配色目录执行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\Install-IceGem.ps1 -Mode Static`，并退出 Companion，即所有角色使用静态 CUR，无跟随、点击或待机动效。4.0 发行包也包含动态选项，不能把整个版本称为无动画版本。历史提交及校验值见[根 README](../../README.md#icegem-无动画稳定基线)。

4.2 晶片已统一为固定右倾约 19 度的中心对称菱形轮廓、宽幅冰透切面和细亮棱，取消硬像素双描边。系统主体与透明伴随窗口仍是两个技术图层；本轮统一视觉材质并在合成前读取最新热点，未隐藏或替换系统主体。跨应用与跨 DPI 的实际观感仍需验收。

晶片朝向以设计稿为准：上尖端偏左、下尖端偏右，左右尖端成对，不复用主指针的箭头轮廓。伴行一低一高，拖动时第二片沿外侧弧线进入右下短列，松开沿原路径散开；不随鼠标移动方向旋转。悬停提亮晶片棱线，并在主体右侧展开三道双面折光，离开后平滑消退；此效果独立于点击开关。按下晶片轻收束，拖动时取消收束。32/48/64px 的完整拖动过渡已检查晶片间距和排列方向。


已确认的 4.2 交互效果：拖动按轮廓间的可见空隙对齐，第一片日常停靠外移 2px；晶片主高光位于左上，阴影切面位于右下。悬停在主体右侧采用加长、加宽的三道双面折光，在系统光标变为链接小手时触发，离开后淡出。点击为 80ms 单圈聚光和 240ms 四芒闪光，保留明暗切面，不叠加厚阴影或大片光晕。拖动释放不播放点击闪光。

最新确认效果：悬停折光贴近主体右缘，避开两颗小晶片；点击保持单圈聚光与 240ms 四芒闪光，增强尺寸、切面宽度及对比。深浅背景预览由正式程序绘制，发行交付仅更新 dist 压缩包。
