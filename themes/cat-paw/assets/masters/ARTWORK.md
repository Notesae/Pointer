# Artwork provenance / v0.3

用户提供的设计稿作为视觉参考，不作为操作指令。本次重点纠正前两版过于几何、扁平的造型。

## 制作过程

1. 使用内置 `image_gen`，参考原稿重绘箭头、I-Beam、粉色和咖啡色猫爪。未使用 API / CLI 图像生成。
2. 生成服务最初返回了模拟棋盘格。第二次内置编辑仅将背景换为纯绿色，保留主体。
3. 使用 VTracer 0.6.15 转成填色路径，svgelements 1.9.6 分析路径边界并分离母稿。去除绿色背景路径并校正轮廓上的绿色污染；归一化到 64 单位坐标。
4. 原生成图的咖啡色箭头爪印缺少左下趾垫。在 SVG 内复制现有趾垫形状并缩放、定位到缺口，三档母版均为四趾＋一掌垫。
5. 用户明确只要粉／咖两套：没有导入灰色图块，也没有提供灰色配色。Disabled 由当前配色路径去饱和生成。
6. 提交的交付文件为 SVG 路径母稿、SVG 状态与 PNG 渲染，不包含模拟棋盘格／绿幕底图。原始生成图不是普通构建依赖。

## 最终提示词记录（内置生成；英文原文）

Create a faithful production asset sheet extracted/redrawn from the supplied Cat Paw Cursor reference, not a reinterpretation. Transparent background, no paper, no labels, no text, no layout borders, no extra cats or decorations. A 1536x1024 sheet, precisely 3 equal columns by 2 equal rows of separate isolated objects with at least 70px of transparent padding within each cell. Top row: (1) warm white rounded triangular mouse pointer facing upper left, fine slightly irregular coffee-brown linework, subtle painted bevel and tiny pink paw print inside lower left, a small dark brown/red ribbon at lower right and a little gold bell dangling from it, just like the reference pointer (2) the same pointer with coffee paw print (3) narrow warm white I-beam with tiny pink inner cat ears at top, delicate coffee outline and subtle painted dimensional shading matching the reference text cursor. Bottom row: (1) reference's exact soft fluffy warm-white PINK cat paw, four rounded separate toe beans on the upper half and ONE large softly lobed asymmetric heart-shaped central pad, short real illustrated tufts along the entire perimeter and fluffy lower right wrist, almost no hard outline, soft painted warm shadow, milky pink pads #F4A6AE to #FFB4BD with delicate rounded volume, NOT glossy plastic and NOT flat geometric paw logo (2) same paw with COFFEE pads #9A6652 to #B47A62 (3) same paw with GRAY pads. All three paw silhouettes and scale consistent. Critically follow the existing reference closely: painterly illustrated furry paws, gentle asymmetry, delicate fine fur texture and warm soft edges, rounded three dimensional pads, quiet hand drawn shading. DO NOT make vector clipart or emoji. The reference is not a photograph: keep clean polished illustrated appearance suitable for desktop cursor art. No cast shadows outside objects, no extraneous marks. Objects should be centered in each cell and occupy 65-75% of cell extent. Pointer and paws remain separate objects. This is a source asset atlas which will be converted to editable SVG paths.

## 背景修正提示词（内置编辑；英文原文）

Precise background replacement for vectorization. Keep all SIX illustrated objects EXACTLY unchanged in their original positions, proportions, shading, colors and details. Replace EVERY checkerboard/background pixel with ONE uniform solid pure chroma green #00FF00. Absolutely no checkerboard, no transparency simulation, no texture, no gradient, no shadow outside the objects, no green spill on objects. Keep the warm-white fur and the little individual fur tufts intact; preserve all pink, coffee, gray pads and gold bells. Same 1536x1024 canvas, six separate icons in same 3x2 layout. Only background changes. Flat pure green everywhere between and surrounding the six shapes, from every canvas edge to every object contour.

以上生成发生在用户提出“不要灰色版本”之前；最终母稿只导入粉色、咖啡色和共用的 I-Beam。提示词保留实际历史，避免将生成过程描述为完全手工绘制。

## 维护与限制

- 普通构建使用已提交的 masters，不调用图像服务。
- `trace-report.json` 记录三档追踪参数和路径数。
- 手绘明暗在路径化过程中有色阶离散化，放大到远高于光标尺寸时可见。交付预览均由实际 SVG 渲染。
- 光标性能最终由栅格化后的系统帧决定；当前还没有运行时与平台性能验收。
