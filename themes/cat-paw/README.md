# Cat Paw / 猫爪动态光标

**Phase 1 · 视觉审核稿 v0.1.0。** 这次交付为可编辑 SVG、透明 PNG、预览与构建工具。尚未提供 Xcursor、CUR/ANI 安装包，也没有 Companion 程序。

一个带小爪印与轻微猫尾装饰的传统箭头，身后跟着一只独立的暖白猫爪。箭头负责准确定位；猫爪负责姿态与反馈。与 IceGem 完全独立。

![Cat Paw Cursor Theme Preview](preview/Cat%20Paw%20Cursor%20Theme%20Preview.png)

[原尺寸 PNG](preview/Cat%20Paw%20Cursor%20Theme%20Preview.png) · [矢量预览](preview/Cat%20Paw%20Cursor%20Theme%20Preview.svg) · [资源与热点清单](assets/manifest.json)

## 第一阶段交付

- Pink Paw / Coffee Paw 两个配色。猫爪均为四个小肉垫与一个大肉垫。
- Normal、Link、Click、Busy、Help、Text、Precision、Move、Resize H/V/D1/D2、Drag、Disabled 共 14 状态。
- 每个配色分别提供 24、32、48、64、96、128px 的系统光标 SVG：共 168 个，并附同尺寸透明 PNG。
- 独立的箭头与猫爪 SVG，以及 28 张双层关系参考图。双层参考图用于审核，不直接作为系统光标打包。
- 预览显示放大状态与浅／深背景实际尺寸样例；在查看器按 100% 查看才是原始像素。

## 设计取舍

暖白 `#FFF9F5`、咖啡灰轮廓 `#796056`，搭配粉色 `#F4A6AE` 或咖啡色 `#9A6652`。设计稿只作为视觉参考；资源以新绘制的 SVG 路径表达，没有把参考图裁切、描摹为位图资产。

猫爪通过少量圆润毛边、底部暖阴影与肉垫高光表达柔软。24/32px 版本加粗轮廓并去掉细毛线、高光与箭头猫尾；48px 起恢复细节，而不是直接缩小一张 128px 图。

箭头尖端固定为热点。I-Beam 维持细窄中轴、上端小猫耳；Crosshair 中心准确且不放大猫爪；Resize 和 Move 保留双箭头／四箭头结构。Help 使用矢量问号，无字体依赖。Disabled 为灰白猫爪与传统禁用符号。

Busy 的 8 个爪印交替采用粉色和咖啡色，并有透明度梯度。当前 SVG 为一个静态关键帧，旋转帧将在平台打包阶段实现。

Normal / Link / Click / Drag 的系统箭头目前有意相同：参考图中的抬起、拍下、旋转发生在独立猫爪上。视觉通过后，平台主题需补充适合无 Companion 使用的链接／抓取反馈映射，并审核其可辨识性。参考图的间距是布局示意；运行时 16px 距离需由 Companion 根据实际光标大小和位置计算，不能把整张参考图当作跟随效果。

## 资源目录

```text
cat-paw/
  theme.json                      配色、尺寸、参数与动效目标
  assets/
    pointer/<color>/<size>/        独立传统箭头
    paw-pink/<size>/               独立猫爪及灰化版本
    paw-coffee/<size>/
    states/<color>/<size>/         14 个系统光标状态
    source-svg/                   64px 母版与双层审核图
    manifest.json                 状态清单、尺寸、热点
  preview/
    Cat Paw Cursor Theme Preview.png
    Cat Paw Cursor Theme Preview.svg
    raster/<color>/<size>/         系统状态透明 PNG
  tools/                          确定性构建与校验
  linux/                          Phase 2 预留说明
  windows/                        Phase 3 预留说明
  companion/                      Phase 4 配置与行为约定
```

`tools/build_assets.py` 是几何生成源码，`theme.json` 是颜色与参数来源。修改它们后重新构建；直接编辑导出的 SVG 会在重建时覆盖。添加新配色只需在 `colorways` 新增颜色 token，构建器会枚举生成对应目录。Busy 有意保留粉／咖交替方案。

## 构建与检查

需要 Python 3.10+、Node.js 20+ 和 npm。预览中文使用 Noto Sans CJK SC；可用的字体替代会改变排版，系统光标 SVG 本身全部是路径，不需要字体。

```sh
cd themes/cat-paw
npm install
npm run build
# 可选：安装 Pillow 以启用像素边界与热点落点校验
python3 -m pip install Pillow
npm run validate
```

验证覆盖：全部状态／配色／尺寸组合、SVG 解析、热点范围、PNG 像素尺寸、不含脚本或外部图片，以及小尺寸细节简化。安装 Pillow 时额外检查每个 PNG 非空、边缘未被裁切、热点落在可见像素上。这些是资产检查，不等同于 Linux/Windows 实机兼容性验收。

## 后续阶段

只有用户确认视觉后才继续：

1. Phase 2：优先 Linux / Zorin，构建标准 Xcursor 主题、状态别名、动画帧、`index.theme` 和安装／卸载流程。GNOME / Zorin / X11 / Wayland 下分别验证。
2. Phase 3：Windows `.cur` / `.ani` 与 `install.inf`，按清单保留准确热点。
3. Phase 4：可选 Cat Paw Companion，独立透明层与事件驱动跟随。系统主题单独安装时仍可用。

原生 Cursor Theme 不能提供真正独立的延迟猫爪。Companion 的平台事件获取、覆盖层、Wayland 权限和桌面限制需单独验证；本次没有声称已支持这些能力，也未测量任何运行时 CPU/GPU 指标。
