# IceGem Linux · Zorin OS 18.1 Pro

五色原生 Xcursor 主题：IceBlue（冰蓝）、Violet（紫罗兰）、RosePink（玫瑰粉）、Mint（薄荷绿）、Amber（琥珀）。每色提供 Animated / Static 两套，共 10 套主题。

本版基于 Windows 4.2 的已确认造型：保持缩小后的文本选择、紧凑调整光标、宝石主体与加强点击放射线。没有把 CUR/ANI 改扩展名，而是重新编码为 Linux Xcursor 文件。

[下载 Linux 4.2 完整安装包](../dist/IceGem-4.2-Linux.tar.gz?raw=true) · [SHA-256 校验值](../dist/IceGem-4.2-Linux.tar.gz.sha256)

## 安装：不需要 sudo

解压 `IceGem-4.2-Linux.tar.gz`，进入解压出的 `IceGem-Linux` 文件夹，在空白处右键“在终端打开”，执行：

```bash
bash Install.sh
```

默认安装并应用冰蓝动态版、32px。需要在 Zorin 图形桌面中以当前用户运行，不要 sudo。预构建包安装只需要 Python 3 和 gsettings，不需要安装绘图库或编译器。

```bash
# 紫罗兰动态版
bash Install.sh --color Violet

# 玫瑰粉静态版
bash Install.sh --color RosePink --mode static

# 安装全部颜色，应用薄荷绿、32px
bash Install.sh --all --color Mint --size 32

# 琥珀色，48px
bash Install.sh --color Amber --size 48

# 仅安装文件，不改桌面设置
bash Install.sh --no-apply

# 恢复首次安装前的主题与尺寸
bash Install.sh --action restore

# 恢复原主题，并将所有 IceGem Linux 主题移到可恢复归档
bash Install.sh --action uninstall
```

每次按所选颜色安装动态和静态两套；`--all` 才安装全部十套。首次更改桌面设置前备份主题和尺寸，换色不覆盖该备份。`--size` 可选 24、32、48、64、96；最终显示大小还受 GNOME 缩放和应用行为影响。

## 文件位置与安全行为

- 主题：`~/.local/share/icons/IceGem-<颜色>-<模式>/`，支持主目录内的 `XDG_DATA_HOME`。
- 兼容入口：`~/.icons/` 下同名符号链接，便于使用旧搜索路径的客户端查找。
- 备份、旧版本、卸载归档：`~/.local/state/IceGem-Linux/`，支持主目录内的 `XDG_STATE_HOME`。
- 只修改当前用户的 `org.gnome.desktop.interface` 中 `cursor-theme` / `cursor-size`。
- 不改系统图标目录、登录界面、GTK 配置文件、Shell 启动文件或 Flatpak 权限。
- 拒绝覆盖不带本安装器标记的同名目录；失败时尝试恢复本次操作前的配置与文件。
- 卸载仅归档本安装器所有的主题。备份不执行为 Shell 代码。
- 如果 `~/.icons` 本身是符号链接，自动安装器会停止，避免改动未知位置；可按下方手动方法安装。

## 手动安装

把包内 `themes/IceGem-IceBlue-Animated` 文件夹复制到 `~/.local/share/icons/`（如果存在同名文件夹，先自行备份，不要盲目覆盖），然后在桌面终端执行：

```bash
gsettings set org.gnome.desktop.interface cursor-theme 'IceGem-IceBlue-Animated'
gsettings set org.gnome.desktop.interface cursor-size 32
```

手动方式不会自动备份原值，建议先用 `gsettings get` 记录当前设置。

## 覆盖范围

- 每套有 18 个基础图形及常用 Linux 别名：default/left_ptr、pointer/hand2、text/xterm、vertical-text、help、wait、progress、crosshair、move、各向 resize 等。
- 行列调整映射到现有紧凑的水平/垂直晶体调整图形，非额外绘制的分隔条图案。
- 动态版提供 12 种动效。normal 为 3.2 秒（含静止停留），working 为 48 帧 / 1.6 秒，busy 为 36 帧 / 1.2 秒，旋转均为 30fps。Link 为切面与提示线的循环高光，不是按键触发动画；点击交互层目前仅提供 Windows 版本。
- 位置/人员选择以 `icegem-location`、`icegem-person` 名称保留，没有宣称 GNOME 会自动调用它们。
- 未设计的 grab/grabbing、复制拖放等状态继承 Adwaita；软件自己的图片光标不受主题控制。不承诺所有应用所有状态都被替换。

## 部分窗口仍为旧光标怎么办？

先完全退出并重启该应用；若桌面仍不刷新，注销后重新登录。不要为了刷新光标强行重启 Wayland 桌面进程。

Flatpak、Snap、远程桌面、浏览器自定义 cursor 或软件内置光标可能使用不同的资源路径。此安装器不会自动放宽沙箱权限；若只有特定软件不生效，请记录软件名、安装来源和 X11/Wayland 会话类型后再排查。

## 构建与验证

尺寸为 24/32/48/64/96px。32/48/64 的几何与热点沿用 Windows 版本；24px 手写热点向笔尖内侧取整。Xcursor 像素采用预乘 Alpha，防止半透明边缘出现色边。

从源码构建需要 Python 3、Pillow、CairoSVG 和 Cairo 系统库。仓库用户先进入 `themes/icegem/linux/`，再执行以下命令；构建后才能运行本目录的安装器：

```bash
python3 -m pip install Pillow CairoSVG
python3 build.py
python3 validate.py
python3 test_install.py
```

仓库中的构建器读取相邻 `variants/`；安装包中的构建器读取 `source/variants/`。运行验证需要系统 `libXcursor`。

4.2 的跨平台结构检查见主题 `preview/motion-4.2-validation.json`。当前 Windows 构建机没有执行新版 `libXcursor` 原生加载；可在 Linux 运行 `python validate.py themes` 验证原生加载及别名解析。仓库 `validation.json` 为历史版本记录。安装器测试使用隔离的临时目录及模拟桌面设置。

**尚未在真实 Zorin OS 18.1 Pro 桌面执行安装、动画播放和多屏/DPI 验收。** 本地库加载通过不能代替 Zorin 实机验证。

## 参考

- [Zorin 官方技术规格：18.1 基于 Ubuntu 24.04，Pro 使用 GNOME Shell](https://zorin.com/os/details/)
- [X.Org Xcursor 格式与主题规范](https://www.x.org/archive/X11R7.5/doc/man/man3/Xcursor.3.html)
