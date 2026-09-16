# Cat Paw / 猫爪动态光标

**Phase 1 · 视觉审核稿 v0.3.0。** 这次交付为可编辑 SVG、透明 PNG、预览与构建工具。尚未提供 Xcursor、CUR/ANI 安装包，也没有 Companion 程序。

一个带小爪印与蝴蝶结铃铛装饰的传统箭头，身后跟着一只独立的暖白猫爪。箭头负责准确定位；猫爪负责姿态与反馈。与 IceGem 完全独立。

![造型与细节审核](preview/Cat%20Paw%20Detail%20Review.png)

![Cat Paw Cursor Theme Preview](preview/Cat%20Paw%20Cursor%20Theme%20Preview.png)

[原尺寸 PNG](preview/Cat%20Paw%20Cursor%20Theme%20Preview.png) · [矢量预览](preview/Cat%20Paw%20Cursor%20Theme%20Preview.svg) · [资源与热点清单](assets/manifest.json)

## 第一阶段交付

- Pink Paw / Coffee Paw 两个配色。猫爪均为四个小肉垫与一个大肉垫。
- Normal、Link、Click、Busy、Help、Text、Precision、Move、Resize H/V/D1/D2、Drag、Disabled 共 14 状态。
- 每个配色分别提供 24、32、48、64、96、128px 的系统光标 SVG：共 168 个，并附同尺寸透明 PNG。
- 独立的箭头与猫爪 SVG，以及 28 张双层关系参考图。双层参考图用于审核，不直接作为系统光标打包。
- 预览显示放大状态与浅／深背景实际尺寸样例；在查看器按 100% 查看才是原始像素。

## 设计取舍

第三版根据用户参考稿重新制作母稿，强调短绒毛的走向、非对称的软掌形、肉垫明暗和蝴蝶结铃铛。使用内置 ImageGen 制作参考驱动的手绘质感母稿，经 VTracer 转成真实的 SVG 路径，再校正背景边缘、热点与缺失细节；SVG 不嵌入位图。母稿来源与提示词见 [制作记录](assets/masters/ARTWORK.md)。

**只提供 Pink / Coffee 两个配色**，没有独立灰色主题。咖啡色箭头内的小爪印已补齐四个小趾垫与一个大肉垫。Disabled 按原始功能需求对当前配色去饱和，仅是状态，不是第三个主题。

24/32px 使用精简毛发母版；48/64px 使用中等细节；96/128px 及放大审核图保留更完整的毛发、肉垫明暗。小尺寸箭头额外保留爪印的轮廓，不让颜色简化吞掉小趾垫。源文件分为 small / medium / detail 三档，而非仅缩放同一张图。

目标色系为暖白、柔咖轮廓、粉色／咖啡色肉垫。手绘母稿内包含多档明暗色，不是仅由三个纯色构成。主题 JSON 的 palette 仍控制程序绘制的功能符号；artwork 字段指定每个配色的手绘母版。

箭头尖端固定为热点。I-Beam 维持细窄中轴、上端小猫耳；Crosshair 中心准确且不放大猫爪；Resize 和 Move 保留双箭头／四箭头结构。Help 使用矢量问号，无字体依赖。Disabled 为灰白猫爪与传统禁用符号。

Busy 的 8 个爪印交替采用粉色和咖啡色，并有透明度梯度。当前 SVG 为一个静态关键帧，旋转帧将在平台打包阶段实现。

Normal / Link / Click / Drag 的系统箭头目前有意相同：参考图中的抬起、拍下、旋转发生在独立猫爪上。视觉通过后，平台主题需补充适合无 Companion 使用的链接／抓取反馈映射，并审核其可辨识性。参考图的间距是布局示意；运行时 16px 距离需由 Companion 根据实际光标大小和位置计算，不能把整张参考图当作跟随效果。

## 资源目录

```text
cat-paw/
  theme.json                      配色、尺寸、参数与动效目标
  assets/
    masters/<detail-level>/       可编辑手绘质感 SVG 母稿
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

`assets/masters/` 是已提交的可编辑路径母稿，`tools/build_assets.py` 负责组合状态和导出，`theme.json` 保存配色映射与动作参数。修改母稿后重新构建；不要只改生成目录。新增配色时为其提供 pointer / paw artwork 母稿，再在 `colorways` 登记，不需要改动组合逻辑。Busy 按原始要求使用粉／咖交替方案。

常规构建不依赖 ImageGen、原始 PNG 或矢量化库。`tools/import_masters.py` 仅用于一次性重新导入特定 3×2 布局的母稿，参数及坐标与这张输入图对应，不是通用任意图片导入器。重新生成母稿是非确定性的，不能保证与已提交 SVG 完全相同。

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
