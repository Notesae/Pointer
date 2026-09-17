# Pointer

> **新主题设计阶段**：完整宝石本体动画已独立为 [Crystal（切面晶石）](themes/crystal/)，不再作为 IceGem 4.3；IceGem 4.2 交互动效保留为实验。Crystal 静态资源尚未校对完成，仍需继续优化，见[后续待办](themes/crystal/TODO.md)。

Windows / Linux 自定义光标主题集合。**每套光标独立目录，主题内再区分配色**，方便持续加入不同造型和风格。

## 光标主题

| 主题 | 风格 | 配色 | 入口 |
|---|---|---|---|
| Crystal（切面晶石） | 完整宝石、台面折射、原生本体动画 | 冰蓝原型 | [设计与动画预览](themes/crystal/) |
| Cat Paw | 暖白猫咪、独立猫爪、柔和肉垫 | 粉色 / 咖啡色 | [视觉预览与 Linux 安装](themes/cat-paw/) |
| IceGem | 修长切面、冰透宝石、轻盈微光 | 冰蓝 / 紫罗兰 / 玫瑰粉 / 薄荷绿 / 琥珀 | [预览与安装](themes/icegem/) |

[下载 Cat Paw 0.5.1 Linux 两色安装包](themes/cat-paw/dist/CatPaw-0.5.1-Linux.tar.gz?raw=true) · [Zorin 安装说明](themes/cat-paw/linux/)

![IceGem 五色预览](themes/icegem/preview/colorways.png)

[下载 IceGem 4.2 Windows 五色安装包](themes/icegem/dist/IceGem-4.2-Color-Collection.zip?raw=true)

[下载 IceGem 4.2 Linux 安装包](themes/icegem/dist/IceGem-4.2-Linux.tar.gz?raw=true) · [Linux / Zorin 安装说明](themes/icegem/linux/)

## IceGem 无动画稳定基线

动效改造前保留 **IceGem 4.0 的 Static 全静态方案**作为回退基线（Windows 包提交 `58b6580`，Linux 包提交 `2225503`）。4.0 整个发行包仍含动态方案；只有选择 Static 且退出 Companion 才是完全无动画效果。

- [Windows 4.0 原始归档](themes/icegem/dist/IceGem-4.0-Color-Collection.zip?raw=true)：解压后进入所需配色目录，运行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\Install-IceGem.ps1 -Mode Static`。
- [Linux 4.0 原始归档](themes/icegem/dist/IceGem-4.0-Linux.tar.gz?raw=true)：安装后选择对应颜色的 `IceGem-<Color>-Static` 主题。
- Windows 原始包 SHA256：`3fe514214132b23614136316c937e06039ebddc3451dca6e377a7fa169cdcf9a`。已核验压缩包及静态 CUR 资源；历史包不随 4.2 修改。
- 4.2 为动效迭代版本，尚未完成用户桌面视觉验收，不取代上述稳定外观基线。

## 目录约定

| 路径 | 用途 |
|---|---|
| `themes/<主题名>/README.md` | 主题说明、预览、安装与构建方法 |
| `themes/<主题名>/theme.json` | 主题版本、配色和规格 |
| `themes/<主题名>/variants/<配色名>/` | 各配色的源码、构建器和安装脚本 |
| `themes/<主题名>/linux/` | Linux 安装器、构建工具与说明 |
| `themes/<主题名>/preview/` | 预览图片 |
| `themes/<主题名>/dist/` | 完整可安装分发包 |
| `themes/<主题名>/tools/` | 主题级构建工具 |

发行交付统一打包到 `themes/<主题名>/dist/`，不在仓库根目录保留解压后的运行副本；源码与预览分别留在主题目录中。

新增主题时创建与 `icegem` 同级的目录，独立管理资源与版本，再在上方主题表登记。不同主题不混放文件。主题安装器应使用独立方案名、安装目录与备份归属，避免主题之间互相覆盖。

IceGem 的 CUR/ANI 文件校验已通过；Windows 实机兼容性验证范围见主题说明。

IceGem Linux 提供五色动态/静态共十套原生 Xcursor 主题，支持 24/32/48/64/96px；Zorin 桌面实机验收仍待完成。
