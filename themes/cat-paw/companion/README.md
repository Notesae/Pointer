# Cat Paw Companion · Linux X11

0.5.0 提供真正的全局猫爪跟随、悬停抬爪、按下/回弹、拖动和一次轻微待机晃动。暖白猫毛，粉色/咖啡色肉垫；箭头尖端和点击精度不变。

## 安装和控制

下载并解压 `CatPaw-0.5.0-Linux.tar.gz`，在解压目录运行：

```sh
bash Install.sh --color pink --size 32
# 咖啡色：
bash Install.sh --color coffee --size 48
# 管理：
bash Install.sh --action status
bash Install.sh --action stop
bash Install.sh --action start
bash Install.sh --action restore
bash Install.sh --action uninstall
```

默认安装、立即启动并设置用户登录时启动。`--no-autostart` 仅启动本次；`--theme-only` 只安装系统主题；`--no-apply` 仅复制文件，不启动或新建自启动。如果已有 Companion 正在运行，复制模式会要求先停止，避免热覆盖运行文件。不要 sudo 运行安装器。

Zorin/Ubuntu 缺少依赖时，安装器给出明确提示：

```sh
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

参数位于 `~/.config/catpaw-companion/config.json`（遵循 XDG_CONFIG_HOME），保存后自动读取：`pawColor`、`pawDistance`、`pawScale`、`followDelay`、`animationStrength`、`clickAnimation`、`idleAnimation`、`followAnimation`。默认距离16、延迟65ms；关闭某种动画设为 false。系统光标大小由 GNOME 设置同步，系统关闭动画时也会关闭动作幅度。

运行文件：`~/.local/share/CatPaw-Companion`；日志：`~/.local/state/CatPaw-Companion/companion.log`；自启动：`~/.config/autostart/catpaw-companion.desktop`。卸载将运行文件归档并移除自启动，保留个人参数。

## 支持范围

本版 Companion 需要 **Linux X11 + GTK3 + 合成桌面**，面向 Zorin/GNOME。Wayland 会明确拒绝启动 Companion；系统光标主题仍可使用。尚无 Windows Companion。没有管理员权限要求，不读取键盘，不占用鼠标输入。

悬停状态由 XFixes 提供的光标名称识别；没有设置标准名称的应用仍可跟随、点击，但可能无法识别 Link。文本、精确定位、缩放、Busy 等状态隐藏伴随猫爪，保留系统主题。Link 是光标角色，Click 是鼠标事件。

为避免双爪，运行时切换到 Companion 专用主题；正常停止后恢复原 CatPaw 主题。强制杀死/断电无法执行恢复，可再次启动后停止或重跑安装器。

XInput2 鼠标事件驱动，不轮询位置；动画约60fps，动作结束后取消刷新定时器；待机只执行一次轻晃。隔离 Xvfb 测试覆盖跟随、按下/回弹、拖动、悬停、文本隐藏、穿透输入区域，并确认静止时不增加动画帧及采样区间内 CPU tick。真实桌面的混合 DPI、全屏应用和合成效果仍需体验验证。

测试：`python3 companion/test_runtime.py`（需要 Xvfb 和 libXtst）；可通过 CATPAW_XVFB 指定虚拟服务器路径。测试只对自己的虚拟显示发送输入。
