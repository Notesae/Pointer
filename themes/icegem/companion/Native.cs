using System;
using System.Drawing;
using System.Runtime.InteropServices;

namespace IceGem {
    // Win32 边界集中于此；只订阅鼠标输入，绝不注入、抓取或阻止用户输入。
    internal static class Native {
        [StructLayout(LayoutKind.Sequential)] internal struct Point { public int X,Y; public Point(int x,int y){X=x;Y=y;} }
        [StructLayout(LayoutKind.Sequential)] internal struct Size { public int Width,Height; public Size(int w,int h){Width=w;Height=h;} }
        [StructLayout(LayoutKind.Sequential)] internal struct CursorInfo { public int Size,Flags; public IntPtr Cursor; public Point Position; }
        [StructLayout(LayoutKind.Sequential)] internal struct RawDevice { public ushort Page,Usage; public uint Flags; public IntPtr Target; }
        [StructLayout(LayoutKind.Sequential)] internal struct RawHeader { public uint Type,Size; public IntPtr Device,WParam; }
        [StructLayout(LayoutKind.Sequential,Pack=1)] internal struct Blend { public byte Operation,Flags,Alpha,Format; }
        [StructLayout(LayoutKind.Sequential)] internal struct IconInfo { public bool IsIcon; public uint HotX,HotY; public IntPtr Mask,Color; }
        // 回调必须由宿主字段持有，防止原生钩子使用已回收委托。
        internal delegate void WinEvent(IntPtr hook,uint ev,IntPtr window,int obj,int child,uint thread,uint time);
        // 读取当前全局光标句柄、位置及可见标记。
        [DllImport("user32.dll")] internal static extern bool GetCursorInfo(ref CursorInfo info);
        // 读取系统热点的真实屏幕坐标。
        [DllImport("user32.dll")] internal static extern bool GetCursorPos(out Point point);
        // 获取系统当前标准角色的共享光标句柄。
        [DllImport("user32.dll")] internal static extern IntPtr LoadCursor(IntPtr instance,IntPtr id);
        // 注册或撤销仅鼠标的后台原始事件订阅。
        [DllImport("user32.dll",SetLastError=true)] internal static extern bool RegisterRawInputDevices(RawDevice[] devices,uint count,uint size);
        // 读取当前 WM_INPUT 携带的数据，不消费其他应用输入。
        [DllImport("user32.dll",SetLastError=true)] internal static extern uint GetRawInputData(IntPtr raw,uint command,IntPtr data,ref uint size,uint headerSize);
        // 订阅光标显示和角色变化事件。
        [DllImport("user32.dll")] internal static extern IntPtr SetWinEventHook(uint min,uint max,IntPtr module,WinEvent callback,uint process,uint thread,uint flags);
        // 释放角色变化订阅句柄。
        [DllImport("user32.dll")] internal static extern bool UnhookWinEvent(IntPtr hook);
        // 启用按显示器 DPI 感知，保持物理坐标一致。
        [DllImport("user32.dll")] internal static extern bool SetProcessDpiAwarenessContext(IntPtr value);
        // 为不支持新 DPI API 的系统提供兼容回退。
        [DllImport("user32.dll")] internal static extern bool SetProcessDPIAware();
        // 读取窗口所在显示器 DPI。
        [DllImport("user32.dll")] internal static extern uint GetDpiForWindow(IntPtr window);
        // 读取系统减少动画等用户偏好。
        [DllImport("user32.dll")] internal static extern bool SystemParametersInfo(uint action,uint param,out int value,uint flags);
        // 获取实际光标尺寸，返回的 GDI 位图由调用者释放。
        [DllImport("user32.dll")] internal static extern bool GetIconInfo(IntPtr icon,out IconInfo info);
        // 取得屏幕合成所需设备上下文。
        [DllImport("user32.dll")] internal static extern IntPtr GetDC(IntPtr window);
        // 归还屏幕设备上下文。
        [DllImport("user32.dll")] internal static extern int ReleaseDC(IntPtr window,IntPtr dc);
        // 创建用于透明位图合成的内存设备上下文。
        [DllImport("gdi32.dll")] internal static extern IntPtr CreateCompatibleDC(IntPtr dc);
        // 绑定位图或恢复内存设备上下文的原对象。
        [DllImport("gdi32.dll")] internal static extern IntPtr SelectObject(IntPtr dc,IntPtr obj);
        // 释放位图等 GDI 资源。
        [DllImport("gdi32.dll")] internal static extern bool DeleteObject(IntPtr obj);
        // 释放内存设备上下文。
        [DllImport("gdi32.dll")] internal static extern bool DeleteDC(IntPtr dc);
        // 以预乘透明像素更新不激活的覆盖窗口。
        [DllImport("user32.dll",SetLastError=true)] internal static extern bool UpdateLayeredWindow(IntPtr window,IntPtr dest,ref Point pos,ref Size size,IntPtr source,ref Point sourcePos,uint key,ref Blend blend,uint flags);
        // 读取原生窗口样式，用于冒烟验证。
        [DllImport("user32.dll")] internal static extern IntPtr GetWindowLongPtr(IntPtr window,int index);
        // 查询本进程注册的原始输入设备。
        [DllImport("user32.dll")] internal static extern uint GetRegisteredRawInputDevices(IntPtr devices,ref uint count,uint size);

        // 逐像素透明合成不使用透明色键，细边缘不会出现洋红色毛边。
        internal static void Present(IntPtr handle, Bitmap bitmap, int x,int y) {
            IntPtr screen=GetDC(IntPtr.Zero), memory=CreateCompatibleDC(screen), dib=IntPtr.Zero, previous=IntPtr.Zero;
            try {
                dib=bitmap.GetHbitmap(Color.FromArgb(0)); previous=SelectObject(memory,dib);
                var pos=new Point(x,y); var from=new Point(0,0); var size=new Size(bitmap.Width,bitmap.Height);
                var blend=new Blend {Operation=0,Flags=0,Alpha=255,Format=1};
                if(!UpdateLayeredWindow(handle,screen,ref pos,ref size,memory,ref from,0,ref blend,2))
                    throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error());
            } finally {
                if(previous!=IntPtr.Zero) SelectObject(memory,previous);
                if(dib!=IntPtr.Zero) DeleteObject(dib);
                DeleteDC(memory); ReleaseDC(IntPtr.Zero,screen);
            }
        }
    }
}
