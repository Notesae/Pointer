# Companion：Phase 4 行为约定

当前仅为设计目标，尚无运行程序。配置来源为上层 `theme.json`，实现时需要验证输入并限制合理范围。

| 配置 | 默认 | 单位／含义 |
|---|---|---|
| pawColor | pink | colorways 中的键；可选 coffee，允许未来扩展 |
| pawDistance | 16 | 逻辑 px，指针可见轮廓与猫爪之间的目标间距 |
| pawScale | 1.0 | 相对于默认猫爪尺寸的倍率 |
| followDelay | 65 | ms，视觉响应目标，并非高频轮询周期 |
| animationStrength | 1.0 | 姿态变化幅度倍率 |
| clickAnimation | true | 按下靠近、缩至 0.88，松开 1.05 → 1.0 |
| idleAnimation | true | 停止 1600ms 后轻晃一次，不持续刷新 |
| followAnimation | true | 启用 spring/ease-out 跟随；关闭后无滞后 |

Hover：抬起 3px、旋转 −5°。Click：全周期 180ms，最多三条短强调线。Drag：靠近至约 11px、旋转 8°。Busy：8 个粉／咖爪印，目标 1000ms/圈。尺寸为逻辑 px，需适配显示缩放与多屏坐标。

输入事件触发动画；仅运动时请求约 60fps 帧。静止后停止绘制，Idle 使用一次性计时器。`animationStrength=0` 应关闭非必要动作；系统减少动画偏好应优先。性能目标为 idle CPU 接近 0%，需实际测量。

文字、精准选择与缩放时按预览省略完整猫爪，避免遮挡目标。Companion 必须点击穿透，不修改系统热点，不抢输入焦点。关闭或崩溃后仍由完整系统主题服务。

此处不引入平台 hook、守护进程或轮询实现。Wayland 下能否获得全局指针事件、绘制全局层，需要针对 compositor 选择能力允许的方式，不能预先承诺通用支持。
