> **0.5.0 更新：安装脚本已集成 X11 猫爪跟随、点击回弹和开机启动。使用与限制见 [Companion](companion/README.md)。**

# Cat Paw / 猫爪动态光标

**Phase 2 · Linux 原生主题已交付，版本 0.5.0。** Pink / Coffee 两色各有动态／静态版，提供六档尺寸、安装／恢复／卸载工具。[下载 Linux 安装包](dist/CatPaw-0.5.0-Linux.tar.gz?raw=true) · [Zorin 安装说明](linux/) · [Linux 实际角色预览](preview/Cat%20Paw%20Linux%20Roles.png)。

已通过原生 Xcursor 加载和隔离安装测试；Zorin 桌面、多屏和 HiDPI 实机验收尚未完成。Windows 尚未实现；X11 Companion 已提供。

一个带小爪印与蝴蝶结铃铛装饰的传统箭头，身后跟着一只独立的暖白猫爪。箭头负责准确定位；猫爪负责姿态与反馈。与 IceGem 完全独立。

![造型与细节审核](preview/Cat%20Paw%20Detail%20Review.png)

![Cat Paw Cursor Theme Preview](preview/Cat%20Paw%20Cursor%20Theme%20Preview.png)

[原尺寸 PNG](preview/Cat%20Paw%20Cursor%20Theme%20Preview.png) · [矢量预览](preview/Cat%20Paw%20Cursor%20Theme%20Preview.svg) · [资源与热点清单](assets/manifest.json)

## Linux 动画预览

下图从发布安装包的真实 Xcursor 帧导出。**Animated 只让 Busy / Working 爪印环旋转；Normal、Link 和点击没有动态反馈。** 独立猫爪跟随与拍击由安装包中的 X11 Companion 提供。PNG 状态表是静态预览。

![Linux 实际忙碌动画](preview/Cat%20Paw%20Linux%20Animation.gif)

## 第一阶段交付

- Pink Paw / Coffee Paw 两个配色。猫爪均为四个小肉垫与一个大肉垫。
- 保留 14 种视觉场景：13 种光标角色参考，以及单独归类的 Click Companion 反馈。
- 两个配色 × 六种尺寸 × 13 种光标资源，共 156 个 SVG 与同尺寸透明 PNG；不含 Click 系统光标。资源角色不等同于 Windows 安装槽位，平台映射在后续打包阶段确定。
- Click 独立提供按下、回弹、恢复三张猫爪关键帧：两色六尺寸共 36 个 SVG 与 PNG，无系统热点或安装槽位。
- 独立的箭头与猫爪 SVG，以及 28 张双层关系参考图。双层参考图用于审核，不直接作为系统光标打包。
- 预览显示放大状态与浅／深背景实际尺寸样例；在查看器按 100% 查看才是原始像素。

## 设计取舍

第三版根据用户参考稿重新制作母稿，强调短绒毛的走向、非对称的软掌形、肉垫明暗和蝴蝶结铃铛。使用内置 ImageGen 制作参考驱动的手绘质感母稿，经 VTracer 转成真实的 SVG 路径，再校正背景边缘、热点与缺失细节；SVG 不嵌入位图。母稿来源与提示词见 [制作记录](assets/masters/ARTWORK.md)。

**只提供 Pink / Coffee 两个配色**，没有独立灰色主题。咖啡色箭头内的小爪印已补齐四个小趾垫与一个大肉垫。Disabled 按原始功能需求对当前配色去饱和，仅是状态，不是第三个主题。

24/32px 使用精简毛发母版；48/64px 使用中等细节；96/128px 及放大审核图保留更完整的毛发、肉垫明暗。小尺寸箭头额外保留爪印的轮廓，不让颜色简化吞掉小趾垫。源文件分为 small / medium / detail 三档，而非仅缩放同一张图。

目标色系为暖白、柔咖轮廓、粉色／咖啡色肉垫。手绘母稿内包含多档明暗色，不是仅由三个纯色构成。主题 JSON 的 palette 仍控制程序绘制的功能符号；artwork 字段指定每个配色的手绘母版。

箭头尖端固定为热点。I-Beam 维持细窄中轴、上端小猫耳；Crosshair 中心准确且不放大猫爪；Resize 和 Move 保留双箭头／四箭头结构。Help 使用矢量问号，无字体依赖。Disabled 为灰白猫爪与传统禁用符号。

Busy 的 8 个爪印交替采用粉色和咖啡色，并有透明度梯度。当前 SVG 为一个静态关键帧，旋转帧将在平台打包阶段实现。

第一阶段素材中的 Normal / Link / Drag 箭头相同；Linux 实现已为 Link / Grab / Grabbing 增加固定的小猫爪姿态以区分角色，见 Linux 实际角色预览。Click 只属于 Companion 输入反馈，拍下期间系统仍显示所在位置的 Arrow / Link / Text 等角色，不切换到 Click 光标。这些原生状态不要求运行 Companion，但不具备独立延迟跟随。参考图的间距是布局示意；运行时 16px 距离需由 Companion 根据实际光标大小和位置计算，不能把整张参考图当作跟随效果。

## 资源目录

```text
cat-paw/
  theme.json                      配色、尺寸、参数与动效目标
  assets/
    masters/<detail-level>/       可编辑手绘质感 SVG 母稿
    pointer/<color>/<size>/        独立传统箭头
    paw-pink/<size>/               独立猫爪及灰化版本
    paw-coffee/<size>/
    states/<color>/<size>/         13 种光标资源，不含 Click
    companion/<color>/<size>/      Click 猫爪三姿态关键帧，无热点
    source-svg/                   64px 母版与双层审核图
    manifest.json                 状态清单、尺寸、热点
  preview/
    Cat Paw Cursor Theme Preview.png
    Cat Paw Cursor Theme Preview.svg
    raster/<color>/<size>/         光标角色透明 PNG
    companion/<color>/<size>/      Companion 关键帧透明 PNG
  tools/                          确定性构建与校验
  linux/                          Phase 2 构建、安装、校验与打包工具
  dist/                           Linux 安装包与 SHA-256
  windows/                        Phase 3 预留说明
  companion/                      X11 运行程序、参数和行为约定
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

## Link 与 Click 的边界

| 项目 | 类型 | 交付位置 | Windows 安装映射 |
|---|---|---|---|
| Link | 光标角色，表示链接选择 | `assets/states/.../link.svg` | `IDC_HAND` / 链接选择 |
| Click | 鼠标按下／松开的输入反馈 | `assets/companion/` | 无独立槽位，不能由 INF 安装为 Click |

点击可发生在 Arrow、Link 或 Text 等角色上，不能把点击事件合并为 Link。单独安装 `.cur` / `.ani` 主题不会获得按点击触发的猫爪拍击。X11 Companion 已监听输入事件驱动独立猫爪动画。

主预览保留 Click 的视觉审核格，使用不同底色并标注 Companion。原尺寸系统层检查图不再包含 Click。清单中 `cursors` 仅列光标资源，`companionAnimations` 单独列关键帧、输入事件和路径。

依据：[Microsoft — About Cursors](https://learn.microsoft.com/en-us/windows/win32/menurc/about-cursors)、[WM_LBUTTONDOWN](https://learn.microsoft.com/en-us/windows/win32/inputdev/wm-lbuttondown)。

## 后续阶段

当前进度：

1. Phase 2：已提供标准 Xcursor、状态别名、Busy / Progress 动画、`index.theme` 与安装／卸载流程。原生文件及安装测试通过；GNOME / Zorin 的 X11 / Wayland 桌面验收待进行。
2. Phase 3：Windows `.cur` / `.ani` 与 `install.inf`，按清单保留准确热点。
3. Phase 4：X11 Companion 已实现；Windows 和 Wayland Companion 待开发。

原生 Cursor Theme 不能提供真正独立的延迟猫爪。X11 事件和透明输入层已在隔离桌面验证；Wayland 尚不支持，真实桌面多屏/HiDPI 与 GPU、电量指标尚待验证。
