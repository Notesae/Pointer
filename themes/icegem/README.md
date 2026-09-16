# IceGem · 冰晶宝石光标

冰蓝、紫罗兰、玫瑰粉、薄荷绿、琥珀五套配色，沿用修长晶体造型和加强版点击线条。

![五色预览](preview/colorways.png)

## 下载与安装

[下载 4.0 五色完整安装包](dist/IceGem-4.0-Color-Collection.zip?raw=true)。解压完整文件夹后双击对应入口：

| 颜色 | 文件 |
|---|---|
| 冰蓝 | Install-IceBlue.cmd |
| 紫罗兰 | Install-Violet.cmd |
| 玫瑰粉 | Install-RosePink.cmd |
| 薄荷绿 | Install-Mint.cmd |
| 琥珀 | Install-Amber.cmd |

默认动态 multi 方案，无需管理员权限。每色注册独立静态/动态方案，已安装的颜色可在 Windows 鼠标属性 → 指针中切换。安装包内的 IceGem-Colors-Preview.html 支持五色动画预览与悬停测试。

## 规格与目录

- 每色 18 种状态，32/48/64px 和多分辨率 CUR。
- 正常、后台忙碌、等待提供 24 帧 ANI。
- Link 使用原晶体＋高对比点击放射线；文本保持已缩小的尺寸。
- `variants/<配色>/`：SVG 源文件、构建器、安装脚本、热点映射与校验记录。
- `preview/`：主题总览；`dist/`：可直接使用的完整安装包。
- 仓库不重复存放生成的 CUR/ANI、动画逐帧 SVG 和大体积内嵌预览 HTML；它们均在安装包中，也可从源码重建。

## 从源码构建

需要 Python 3、Pillow、CairoSVG 及 Cairo 系统库；预览生成还使用 DejaVu Sans 字体。推荐 Linux 构建环境。

```bash
python -m pip install -r themes/icegem/requirements.txt
python themes/icegem/tools/build_all.py
```

产物写入每种配色目录中的 cursors、src/animation、preview，随后自动检查 CUR/ANI 结构。此时该配色目录下 Install.cmd 可直接使用。仅查看静态源码无需安装依赖。

## 恢复与卸载

在解压包目录执行 `Install-IceBlue.cmd -Action Restore` 恢复首次安装前的指针；`Install-IceBlue.cmd -Action Uninstall` 恢复并卸载共同管理的所有 IceGem 配色。不同配色共用首次备份，支持已有 IceGem 版本更新。`Check-Link.cmd` 检查当前 Link 的文件与注册表映射。

## 验证与边界

二进制结构、透明轮廓、热点及动画帧检查已通过。冰蓝资源与 3.5 一致；Windows 安装/播放/跨 DPI 未在构建环境实机验收。32/48/64 表示资源分辨率，不是显示大小选项。竖排文本无独立全局槽位，系统方案不覆盖应用自行绘制的全部光标。
