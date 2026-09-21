# IceGem 4.5 · 玫瑰粉

仓库源码目录需要先执行 `python tools/build.py` 生成 cursors；也可直接下载主题 dist 中的完整安装包。生成后双击本目录 Install.cmd 安装并应用 玫瑰粉 动态方案。Windows 方案名为 IceGem RosePink Gentle (multi)；Static 为静态版。各颜色方案独立命名，安装过的配色可在鼠标属性中切换。

18 种状态，32/48/64px 与 multi，15 种状态提供独立时序 ANI；正常为 96 个动作帧加停留帧，后台为 160 帧 / 6.4 秒，不可用为 125 帧 / 5 秒，等待为 36 帧。文本与竖排文本使用 75 帧 / 3 秒的水晶展台：紧凑切面底座、固定支撑柱、上端晶体自转浮动与倾摆，热点固定在柱身中心。Static 使用首帧；禁用符号保持红色，其他材质按主题配色。

Install.cmd -Mode Static：静态版。
Install.cmd -Action Restore：恢复首次安装前设置。
Install.cmd -Action Uninstall：恢复首次设置并卸载共同管理的全部 IceGem 配色。
Check-Link.cmd：只读检查当前 Link 是否匹配本色。

每次安装产生新资源路径，保留首次备份。资源存于 LocalApplicationData 下的 IceGem-Managed，备份为 IceGem-Backups。无需管理员权限。不得仅覆盖解压文件而不重新安装。

源文件在 src，生成器在 tools/build.py。安装 requirements.txt 后运行 python tools/build.py 重建；本套色相参数已写入源码，固定输入得到固定输出。
32/48/64 为资源分辨率，不是显示大小选项。竖排文本为应用专用资源，无独立全局槽位。系统方案无法覆盖应用自行绘制的所有光标。

已检查 CUR/ANI 结构、透明度、热点和动画帧。Windows 安装、播放与跨 DPI 尚未实机验收。
