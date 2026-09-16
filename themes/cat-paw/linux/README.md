# Cat Paw Linux / Zorin · 0.4.0

Phase 2 的原生 Xcursor 交付：**Pink / Coffee 两个配色，各有 Animated / Static 版本**，共四套独立主题。尺寸为 24 / 32 / 48 / 64 / 96 / 128px。

[下载 Linux 安装包](../dist/CatPaw-0.4.0-Linux.tar.gz?raw=true) · [SHA-256](../dist/CatPaw-0.4.0-Linux.tar.gz.sha256) · [实际 Linux 角色预览](../preview/Cat%20Paw%20Linux%20Roles.png)

## 安装

解压安装包，进入 `CatPaw-Linux` 文件夹，在该文件夹打开终端：

```bash
bash Install.sh
```

默认安装粉色的动态／静态两套，应用粉色动态版、32px。请使用当前桌面用户，**不要 sudo**。预构建包只需要 Python 3（Zorin 18.1 自带）和 GNOME 的 gsettings；不需要 Node.js、绘图库或编译器。

```bash
# 咖啡色，48px
bash Install.sh --color coffee --size 48

# 两个配色都安装，应用粉色动态版
bash Install.sh --all --color pink

# 使用静态版，关闭系统忙碌动画
bash Install.sh --color coffee --mode static

# 仅复制文件，不更改桌面配置
bash Install.sh --all --no-apply

# 恢复首次安装前的主题和尺寸，保留 Cat Paw 文件
bash Install.sh --action restore

# 卸载：归档 Cat Paw 文件；若仍在使用 Cat Paw 则恢复原主题
bash Install.sh --action uninstall

# 对于仅复制文件的安装，也可以只归档文件，不读写桌面配置
bash Install.sh --action uninstall --no-apply
```

`--no-apply` 卸载不会改变当前设置；如果你曾手动选中了 Cat Paw，应先切换到其他主题。正常卸载发现你已改用 IceGem 等其他主题时，会保留你的当前选择。

## 安装位置与恢复

- 主题：`~/.local/share/icons/CatPaw-<Pink|Coffee>-<Animated|Static>/`
- 兼容搜索入口：`~/.icons/` 下同名链接。
- 原主题备份及可恢复归档：`~/.local/state/CatPaw-Linux/`。
- 支持主目录内部的 `XDG_DATA_HOME`、`XDG_STATE_HOME`。
- 首次应用前保存主题与大小，换色不覆盖首次备份。
- 更新与卸载只处理带 Cat Paw 所有权标记的目录；不覆盖 IceGem 或其他主题。
- 应用失败会尝试回滚本次文件与设置；卸载归档失败也会尝试恢复。

安装器不修改系统主题目录、登录界面、Shell 配置或 Flatpak 权限。`~/.icons` 是符号链接时，自动安装器会停止；可使用手动安装。

## 手动安装

将包内相应主题目录复制到 `~/.local/share/icons/`，确认没有覆盖其他内容，再在桌面终端选择：

```bash
gsettings set org.gnome.desktop.interface cursor-theme 'CatPaw-Pink-Animated'
gsettings set org.gnome.desktop.interface cursor-size 32
```

手动安装不自动备份设置，建议先运行 `gsettings get` 记录原值。其他桌面环境请使用其自己的光标主题选择设置。

## 原生角色与动画

每套包含 16 种基础角色及 74 个名称（基础名称与别名合计）：

| 角色 | Linux 常用名称 | 行为 |
|---|---|---|
| 正常 | default / left_ptr | 原稿箭头与铃铛 |
| 链接 | pointer / hand2 | 箭头旁有抬起的小猫爪，静态提示可点击 |
| 后台运行 | progress / left_ptr_watch | 保留箭头，旁边旋转爪印环 |
| 忙碌等待 | wait / watch | 只有粉／咖爪印环，热点位于中心 |
| 帮助 | help / question_arrow | 箭头与问号 |
| 文本 | text / xterm / vertical-text | 猫耳 I-Beam，含垂直排版版本 |
| 精准 | crosshair | 准确十字中心 |
| 移动 | move / fleur / all-scroll | 四向箭头 |
| 缩放 | ew/ns/nwse/nesw-resize | 四种双箭头，含方向与行列别名 |
| 抓取／拖动 | grab / grabbing | 箭头与不同姿态的猫爪 |
| 禁用 | not-allowed / no-drop | 传统禁止符号 |

Animated 的 wait / progress 各为 24 帧，周期准确为 1000ms；Static 使用第一帧。普通移动和链接状态不持续播放动画。动画由系统光标机制显示，没有常驻后台进程。

Link / Grab 中的小猫爪是原生光标内的固定静态构图，箭头尖端热点保持一致。它不提供独立跟随延迟。**Click 没有系统光标项，也没有把 `.ani`/Xcursor 动画当成点击监听。** 真正的猫爪滞后跟随、按下拍击、松开回弹仍由未来 Companion 实现。

未单独绘制的复制、快捷方式拖放、手写等特殊名称继承 Adwaita。应用使用自己提供的图片光标时，不一定采用桌面主题。

## GNOME / Zorin、X11 与 Wayland

主题采用标准 Xcursor 文件和 `index.theme`，通过 GNOME 的用户设置选择。X11 客户端还可经 `~/.icons` 兼容入口找到主题；Wayland 下是否采用主题由合成器、工具包和应用决定，不承诺所有应用都自动替换。

若个别应用仍显示旧光标，先完全退出并重启该应用；必要时注销并重新登录。Flatpak / Snap / 远程桌面可能使用独立资源路径，安装器不会自动修改其权限。

**尚未在真实 Zorin OS 18.1 Pro 桌面完成安装、动画播放、多屏及 HiDPI 验收。** 本次通过的是原生文件加载、别名、安装器隔离测试，不能替代实机验收。

## 从仓库构建

在仓库 `themes/cat-paw/` 中执行：

```bash
npm install
python3 -m pip install -r linux/requirements-build.txt
python3 linux/build.py
python3 linux/validate.py
python3 linux/test_install.py
python3 linux/package.py
```

构建使用已提交的 SVG 母稿，不调用图像生成。Node.js / sharp 负责栅格化，Python / Pillow 编码原生 Xcursor。验证额外需要系统 `libXcursor`；不依赖桌面会话。`linux/themes/` 是可重建的完整主题输出，发布包包含全部文件和别名。

安装包中的 `Preview.png` 是打包时的原生角色预览。仓库的 `manifest.json`、`validation.json` 和 `installer-validation.json` 记录交付范围与验证结果。

## 参考

- [X.Org Xcursor 文件和主题规范](https://www.x.org/archive/X11R7.5/doc/man/man3/Xcursor.3.html)
- [Zorin 官方技术规格](https://zorin.com/os/details/)
