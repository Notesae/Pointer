# Pointer

Windows 自定义光标主题集合。**每套光标独立目录，主题内再区分配色**，方便持续加入不同造型和风格。

## 光标主题

| 主题 | 风格 | 配色 | 入口 |
|---|---|---|---|
| IceGem | 修长切面、冰透宝石、轻盈微光 | 冰蓝 / 紫罗兰 / 玫瑰粉 / 薄荷绿 / 琥珀 | [预览与安装](themes/icegem/) |

![IceGem 五色预览](themes/icegem/preview/colorways.png)

[下载 IceGem 4.0 五色安装包](themes/icegem/dist/IceGem-4.0-Color-Collection.zip?raw=true)

## 目录约定

| 路径 | 用途 |
|---|---|
| `themes/<主题名>/README.md` | 主题说明、预览、安装与构建方法 |
| `themes/<主题名>/theme.json` | 主题版本、配色和规格 |
| `themes/<主题名>/variants/<配色名>/` | 各配色的源码、构建器和安装脚本 |
| `themes/<主题名>/preview/` | 预览图片 |
| `themes/<主题名>/dist/` | 完整可安装分发包 |
| `themes/<主题名>/tools/` | 主题级构建工具 |

新增主题时创建与 `icegem` 同级的目录，独立管理资源与版本，再在上方主题表登记。不同主题不混放文件。主题安装器应使用独立方案名、安装目录与备份归属，避免主题之间互相覆盖。

IceGem 的 CUR/ANI 文件校验已通过；Windows 实机兼容性验证范围见主题说明。
