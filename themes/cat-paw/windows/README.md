# Windows — Phase 3

Linux 主题已交付，Windows 阶段尚未开始。本目录尚无 `.cur`、`.ani` 或安装 INF。

后续从 SVG 与热点清单生成 Pink / Coffee 两套独立方案、Busy 动画和 `install.inf`，验证点击、文本与缩放热点。此阶段不承诺原生系统光标能提供独立猫爪延迟跟随。

## 安装角色约束

- Link 对应 Windows 的“链接选择”（`IDC_HAND`）。
- Windows 光标方案没有独立 Click 项：安装器不得注册 `click.cur` / `click.ani` 或将点击动作作为光标槽位。
- `assets/companion/` 中的 Click 文件仅用于未来 Companion 的鼠标按下／松开反馈，不进入 INF 的系统光标映射。
- 13 种现有光标资源是跨平台设计资源，不代表完整或一一对应的 Windows 标准槽位。例如 Drag 也没有独立的标准方案项；Busy 与“后台运行”等角色需要在平台阶段明确区分、补齐。

参考：[Microsoft 标准光标列表](https://learn.microsoft.com/en-us/windows/win32/menurc/about-cursors)。
