using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Runtime.InteropServices;
using System.Threading;
using System.Windows.Forms;
using Microsoft.Win32;

namespace IceGem {
    // Windows 托盘宿主：输入到来才唤醒动画，动作结束后停止刷新。
    internal sealed class Companion : Form {
        private readonly Motion motion = new Motion();
        private readonly Stopwatch clock = Stopwatch.StartNew();
        private readonly System.Windows.Forms.Timer frames = new System.Windows.Forms.Timer {Interval=16};
        private readonly System.Windows.Forms.Timer idle = new System.Windows.Forms.Timer {Interval=1600};
        private readonly Dictionary<IntPtr,Role> roles = new Dictionary<IntPtr,Role>();
        private readonly NotifyIcon tray;
        private readonly Native.WinEvent cursorCallback;
        private readonly string configPath=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"IceGem-Companion","settings.txt");
        private IntPtr cursorHook, previousCursor;
        private string color="IceBlue";
        // 手动暂停和会话锁定分别记录，解锁不能覆盖用户的暂停选择。
        private bool reduced, paused, locked, closing;
        private int frameCount;
        private readonly string smokeOutput;
        private const int CanvasSize=384;

        // 创建输入穿透且不激活的宿主，注册鼠标原始事件和光标角色变化事件。
        internal Companion(string smoke) {
            smokeOutput=smoke;
            FormBorderStyle=FormBorderStyle.None; ShowInTaskbar=false; TopMost=true;
            Size=new Size(CanvasSize,CanvasSize); StartPosition=FormStartPosition.Manual;
            LoadPreferences();
            var menu=new ContextMenuStrip();
            menu.Items.Add("暂停 / 继续",null,delegate { paused=!paused; Wake(); });
            menu.Items.Add("轻柔 / 生动",null,delegate { motion.Strength=motion.Strength>.7f ? .6f : 1; SavePreferences(); Wake(); });
            menu.Items.Add("跟随：开 / 关",null,delegate { motion.Follow=!motion.Follow; SavePreferences(); Wake(); });
            menu.Items.Add("点击：开 / 关",null,delegate { motion.Click=!motion.Click; SavePreferences(); Wake(); });
            foreach(string value in Artwork.Colors) {
                string selected=value;
                menu.Items.Add(selected,null,delegate { color=selected; SavePreferences(); Wake(); });
            }
            menu.Items.Add("退出",null,delegate { Close(); });
            tray=new NotifyIcon {Icon=SystemIcons.Application,Text="IceGem 晶光随行",ContextMenuStrip=menu,Visible=smoke==null};
            frames.Tick+=delegate { TickMotion(); };
            idle.Tick+=delegate { idle.Stop(); motion.Idle(clock.Elapsed.TotalSeconds); Wake(); };
            cursorCallback=delegate(IntPtr h,uint ev,IntPtr w,int obj,int child,uint thread,uint time) {
                if(obj==-9 && (ev==0x8002 || ev==0x8003 || ev==0x800C) && !closing) Wake();
            };
            // Handle 的创建必须早于 Raw Input 注册；不修改光标方案与自启动设置。
            IntPtr window=Handle;
            RefreshRoles();
            var devices=new[]{new Native.RawDevice {Page=1,Usage=2,Flags=0x100,Target=window}};
            if(!Native.RegisterRawInputDevices(devices,1,(uint)Marshal.SizeOf(typeof(Native.RawDevice))))
                throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error());
            cursorHook=Native.SetWinEventHook(0x8002,0x800C,IntPtr.Zero,cursorCallback,0,0,0);
            if(cursorHook==IntPtr.Zero) throw new InvalidOperationException("Cannot observe cursor role changes.");
            SystemEvents.SessionSwitch+=SessionChanged;
        }

        protected override bool ShowWithoutActivation { get { return true; } }
        protected override CreateParams CreateParams {
            get { var p=base.CreateParams; p.ExStyle|=0x80000|0x20|0x80|0x08000000; return p; }
        }

        // 用户会话锁定后停止绘制，并在解锁时重新检查光标可见性。
        private void SessionChanged(object sender,SessionSwitchEventArgs e) {
            // SystemEvents 可能从工作线程通知，所有窗口和定时器操作回到 UI 线程。
            if(!IsHandleCreated || closing) return;
            BeginInvoke((Action)delegate {
                if(e.Reason==SessionSwitchReason.SessionLock) {
                    locked=true; motion.Button(false,clock.Elapsed.TotalSeconds); motion.ReleaseAt=-10; Wake();
                } else if(e.Reason==SessionSwitchReason.SessionUnlock) { locked=false; Wake(); }
            });
        }

        // 只保存用户通过托盘改变的偏好；启动时不会写入系统鼠标设置。
        private void SavePreferences() {
            Directory.CreateDirectory(Path.GetDirectoryName(configPath));
            File.WriteAllLines(configPath,new[]{"color="+color,"follow="+motion.Follow,"click="+motion.Click,"gentle="+(motion.Strength<.7f)});
        }

        // 配置只接受预定义键和值，损坏文件退回默认状态。
        private void LoadPreferences() {
            try {
                using(var key=Registry.CurrentUser.OpenSubKey(@"Control Panel\Cursors")) {
                    string scheme=key==null ? "" : Convert.ToString(key.GetValue(""));
                    foreach(string name in Artwork.Colors) if(scheme.Contains(name)) color=name;
                }
                if(!File.Exists(configPath)) return;
                foreach(string line in File.ReadAllLines(configPath)) {
                    string[] pair=line.Split('='); if(pair.Length!=2) continue;
                    bool value;
                    if(pair[0]=="color" && Array.IndexOf(Artwork.Colors,pair[1])>=0) color=pair[1];
                    else if(bool.TryParse(pair[1],out value)) {
                        if(pair[0]=="follow") motion.Follow=value;
                        if(pair[0]=="click") motion.Click=value;
                        if(pair[0]=="gentle") motion.Strength=value ? .6f : 1;
                    }
                }
            } catch(IOException) { } catch(UnauthorizedAccessException) { }
        }

        // 重新读取当前标准角色句柄；自绘或未知光标保守隐藏装饰，避免遮住精确操作。
        private void RefreshRoles() {
            roles.Clear();
            foreach(int id in new[]{32512,32649,32513,32514,32515,32642,32643,32644,32645,32646,32648,32650,32651,32671,32672}) {
                IntPtr handle=Native.LoadCursor(IntPtr.Zero,new IntPtr(id));
                if(handle!=IntPtr.Zero) roles[handle]=id==32512 ? Role.Normal : id==32649 ? Role.Link : id==32513 ? Role.Text : Role.Hidden;
            }
            int enabled;
            reduced=Native.SystemParametersInfo(0x1042,0,out enabled,0) && enabled==0;
            previousCursor=IntPtr.Zero;
        }

        // 在输入或角色通知时检查真实屏幕位置、角色、DPI 和按键；没有持续轮询。
        private void Wake() {
            if(closing) return;
            idle.Stop();
            var info=new Native.CursorInfo {Size=Marshal.SizeOf(typeof(Native.CursorInfo))};
            if(!Native.GetCursorInfo(ref info)) { Hide(); frames.Stop(); return; }
            Role role;
            motion.SetRole(roles.TryGetValue(info.Cursor,out role) ? role : Role.Hidden,clock.Elapsed.TotalSeconds);
            motion.Enabled=!paused && !locked && !reduced && (info.Flags&1)!=0;
            // GetIconInfo 分配的 GDI 位图需要释放，只在角色句柄变化时获取。
            if(previousCursor!=info.Cursor) {
                Native.IconInfo icon;
                if(Native.GetIconInfo(info.Cursor,out icon)) {
                    try {
                        if(icon.Color!=IntPtr.Zero) using(var bitmap=Image.FromHbitmap(icon.Color)) motion.Size=Math.Max(24,Math.Min(128,bitmap.Width));
                    } finally {
                        if(icon.Color!=IntPtr.Zero) Native.DeleteObject(icon.Color);
                        if(icon.Mask!=IntPtr.Zero) Native.DeleteObject(icon.Mask);
                    }
                }
                previousCursor=info.Cursor;
            }
            Rectangle bounds=Screen.FromPoint(new Point(info.Position.X,info.Position.Y)).Bounds;
            motion.OffsetX=info.Position.X+motion.Size*1.5f>bounds.Right ? -1 : 1;
            motion.OffsetY=info.Position.Y+motion.Size*1.5f>bounds.Bottom ? -1 : 1;
            motion.Move(info.Position.X,info.Position.Y,clock.Elapsed.TotalSeconds);
            if(!motion.Visible) { Hide(); frames.Stop(); return; }
            if(!Visible) Show();
            frames.Start();
        }

        // 每帧只推进模型和合成局部位图；收敛后只保留一次性的待机定时器。
        private void TickMotion() {
            double now=clock.Elapsed.TotalSeconds;
            // 合成前重新读取热点，避免排队的输入位置令装饰与硬件光标产生额外一帧错位。
            Native.Point latest;
            if(Native.GetCursorPos(out latest)) motion.Move(latest.X,latest.Y,now);
            bool active=motion.Step(now);
            using(var bitmap=new Bitmap(CanvasSize,CanvasSize,PixelFormat.Format32bppPArgb)) {
                PointF origin=new PointF(motion.Pointer.X-CanvasSize/2,motion.Pointer.Y-CanvasSize/2);
                using(var g=Graphics.FromImage(bitmap)) Artwork.Draw(g,motion,now,color,origin);
                Native.Present(Handle,bitmap,(int)origin.X,(int)origin.Y);
            }
            frameCount++;
            if(!active) {
                frames.Stop();
                if(!motion.IdleUsed && !motion.Down && motion.Visible) {
                    idle.Interval=Math.Max(1,(int)Math.Ceiling((motion.LastInput+1.6-now)*1000)); idle.Start();
                }
            }
        }

        // 在本进程读取 WM_INPUT 数据，始终交给默认窗口过程完成系统清理。
        protected override void WndProc(ref Message message) {
            if(message.Msg==0x84) { message.Result=new IntPtr(-1); return; }
            if(message.Msg==0x21) { message.Result=new IntPtr(3); return; }
            if(message.Msg==0x1A || message.Msg==0x7E || message.Msg==0x02E0) { RefreshRoles(); Wake(); }
            if(message.Msg==0x00FF && !closing) {
                uint size=0, header=(uint)Marshal.SizeOf(typeof(Native.RawHeader));
                Native.GetRawInputData(message.LParam,0x10000003,IntPtr.Zero,ref size,header);
                if(size>=header+24 && size<65536) {
                    IntPtr data=Marshal.AllocHGlobal((int)size);
                    try {
                        if(Native.GetRawInputData(message.LParam,0x10000003,data,ref size,header)==size && Marshal.ReadInt32(data)==0) {
                            Wake();
                            ushort flags=(ushort)Marshal.ReadInt16(data,(int)header+4);
                            // 尊重交换左右键的系统设置，只有主按钮驱动点击和拖动反馈。
                            int downFlag=SystemInformation.MouseButtonsSwapped ? 4 : 1;
                            int upFlag=SystemInformation.MouseButtonsSwapped ? 8 : 2;
                            if((flags&downFlag)!=0) motion.Button(true,clock.Elapsed.TotalSeconds);
                            if((flags&upFlag)!=0) motion.Button(false,clock.Elapsed.TotalSeconds);
                            if(motion.Visible) frames.Start();
                        }
                    } finally { Marshal.FreeHGlobal(data); }
                }
            }
            base.WndProc(ref message);
        }

        // 冒烟测试仅检查本窗口，不发送模拟输入，也不修改系统主题。
        protected override void OnShown(EventArgs e) {
            base.OnShown(e);
            if(smokeOutput!=null) BeginInvoke((Action)delegate {
                long style=Native.GetWindowLongPtr(Handle,-20).ToInt64();
                if((style&0x80800A0)!=0x80800A0) throw new InvalidOperationException("Overlay styles missing.");
                using(var bitmap=new Bitmap(CanvasSize,CanvasSize,PixelFormat.Format32bppPArgb)) Native.Present(Handle,bitmap,0,0);
                File.WriteAllText(smokeOutput,"PASS: Raw Input registration, cursor event hook, no-activate/click-through/layered styles, per-pixel composition. No desktop input injected.\n");
                Close();
            });
            else Wake();
        }

        // 所有句柄和定时器由宿主释放；退出不需要恢复系统指针，因为从未替换它。
        protected override void OnFormClosed(FormClosedEventArgs e) {
            closing=true; frames.Stop(); idle.Stop(); frames.Dispose(); idle.Dispose();
            SystemEvents.SessionSwitch-=SessionChanged;
            if(cursorHook!=IntPtr.Zero) Native.UnhookWinEvent(cursorHook);
            Native.RegisterRawInputDevices(new[]{new Native.RawDevice {Page=1,Usage=2,Flags=1,Target=IntPtr.Zero}},1,(uint)Marshal.SizeOf(typeof(Native.RawDevice)));
            tray.Visible=false; tray.Dispose();
            base.OnFormClosed(e);
        }
    }

    // 命令行仅提供自测、离线预览与启动；普通运行使用单实例托盘窗口。
    internal static class Program {
        [STAThread]
        private static int Main(string[] args) {
            try {
                if(args.Length>0 && args[0]=="--self-test") { SelfTest(); return 0; }
                if(args.Length==2 && args[0]=="--render-preview") { RenderPreview(args[1],false); return 0; }
                if(args.Length==2 && args[0]=="--render-preview-dark") { RenderPreview(args[1],true); return 0; }
                try { Native.SetProcessDpiAwarenessContext(new IntPtr(-4)); } catch(EntryPointNotFoundException) { Native.SetProcessDPIAware(); }
                bool created;
                using(var mutex=new Mutex(true,@"Local\IceGem-Companion-4",out created)) {
                    if(!created && !(args.Length==2 && args[0]=="--smoke-test")) return 0;
                    Application.EnableVisualStyles();
                    Application.SetCompatibleTextRenderingDefault(false);
                    Application.Run(new Companion(args.Length==2 && args[0]=="--smoke-test" ? args[1] : null));
                }
                return 0;
            } catch(Exception e) { Console.Error.WriteLine(e); return 1; }
        }

        // 回归覆盖跟随收敛、固定点击原点、拖动取消闪光和精确状态隐藏。
        private static void SelfTest() {
            var m=new Motion(); m.Move(100,100,0); m.Step(.016); m.Move(150,100,.02);
            if(m.Shards.X>=180) throw new Exception("Follow must lag decoration only.");
            for(int i=2;i<90;i++) m.Step(i*.016);
            if(m.Step(1.5)) throw new Exception("Settled animation must stop.");
            m.Button(true,1.6); m.Button(false,1.7); m.Move(200,100,1.71);
            if(m.FlashOrigin.X!=150) throw new Exception("Click flash must stay at release origin.");
            m.Button(true,1.8); m.Move(230,100,1.9);
            if(!m.Dragging) throw new Exception("Drag threshold missing.");
            m.Button(false,2);
            if(m.ReleaseAt>0) throw new Exception("Dragging must not produce click flash.");
            m.SetRole(Role.Text,2.1); if(m.Visible) throw new Exception("Text must hide companions.");
            m.SetRole(Role.Normal,2.2); m.Move(240,100,2.3); m.Idle(4);
            if(!m.IdleUsed) throw new Exception("Idle effect missing.");
            for(int i=0;i<120;i++) m.Step(4+i*.016);
            if(m.Step(6)) throw new Exception("Idle must stop refreshing.");
            m.Enabled=false; if(m.Visible) throw new Exception("Reduced motion not honored.");
            // 用真实渲染结果检查小尺寸不透明核心，防止细线低透明度导致晶片发虚。
            foreach(int size in new[]{32,48,64}) {
                var compact=new Motion {Size=size}; compact.Move(24,20,0); compact.Step(0);
                float scale=size/32f;
                if(Math.Abs(compact.Shards.X-compact.Pointer.X-20*scale)>.01 || Math.Abs(compact.Shards.Y-compact.Pointer.Y-20*scale)>.01)
                    throw new Exception("Shard docking must use crystal-tail geometry.");
                using(var bitmap=new Bitmap(160,160,PixelFormat.Format32bppPArgb)) {
                    using(var g=Graphics.FromImage(bitmap)) Artwork.Draw(g,compact,0,"IceBlue",PointF.Empty);
                    int solid=0;
                    for(int y=0;y<bitmap.Height;y++) for(int x=0;x<bitmap.Width;x++) if(bitmap.GetPixel(x,y).A>=240) solid++;
                    if(solid<40*scale*scale) throw new Exception("Shard facets need a readable opaque core.");
                }
                compact.Move(54,20,.016); compact.Step(.032);
                var dock=new PointF(compact.Pointer.X+20*scale,compact.Pointer.Y+20*scale);
                if(Motion.Distance(compact.Shards,dock)>size*.1f+.01) throw new Exception("Follow lag detached the shards.");
                compact.Button(true,.04); compact.Move(70,20,.05); compact.Step(.06);
                if(compact.DragBlend<=0 || compact.DragBlend>=1) throw new Exception("Drag layout must transition smoothly.");
            }
            // 中心对称确保不是箭头形；全过渡路径保持两晶片分离，且拖动后沿右下方排列。
            var vertices=Artwork.ShardVertices(0,0,1);
            if(Math.Abs(vertices[0].X+vertices[2].X)>.001 || Math.Abs(vertices[1].X+vertices[3].X)>.001)
                throw new Exception("Shards must retain opposing diamond tips.");
            foreach(int size in new[]{32,48,64}) {
                var layout=new Motion {Size=size}; layout.Move(50,50,0);
                for(int step=0;step<=100;step++) {
                    layout.DragBlend=step/100f;
                    var centers=Artwork.ShardCenters(layout,PointF.Empty);
                    if(Motion.Distance(centers[0],centers[1])<8*size/32f)
                        throw new Exception("Drag transition crosses the shards.");
                    if(step==100) {
                        var main=new PointF(layout.Pointer.X+6.175f*size/32,layout.Pointer.Y+13.65f*size/32);
                        // 按拖动轴投影扣除主体与晶片轮廓，检查可见空隙而非中心距离。
                        float firstGap=Motion.Distance(main,centers[0])-(10.43f+5.02f)*size/32;
                        float secondGap=Motion.Distance(centers[0],centers[1])-(5.02f+3.923f)*size/32;
                        if(firstGap<=0 || secondGap<=0 || Math.Abs(firstGap-secondGap)>.15f*size/32)
                            throw new Exception("Dragging gems must have matching visible gaps.");
                    }
                    if(step==100 && (centers[1].X<=centers[0].X || centers[1].Y<=centers[0].Y))
                        throw new Exception("Drag trail must extend down and right.");
                }
            }
            // 释放特效在 200ms 时仍刷新，240ms 后停止，防止宿主提前截断增强后的闪光。
            var flash=new Motion(); flash.Move(50,50,0); flash.Step(0); flash.Button(true,1); flash.Button(false,1.01);
            if(!flash.Step(1.21) || flash.Step(1.26)) throw new Exception("Release animation lifetime mismatch.");
            Console.WriteLine("PASS: visible gaps, 240ms release lifetime, follow, settle, click anchoring, drag, text suppression, one-shot idle, reduced motion, compact docking, bounded lag, opaque facets");
        }

        // 离线效果帧直接使用运行时绘制器，避免另做一套与真实程序不符的演示。
        private static void RenderPreview(string folder,bool dark) {
            Directory.CreateDirectory(folder);
            string pointerPath=Path.Combine(AppDomain.CurrentDomain.BaseDirectory,"..","variants","IceBlue","preview","icegem-normal-64.png");
            if(!File.Exists(pointerPath)) pointerPath=Path.Combine(AppDomain.CurrentDomain.BaseDirectory,"..","IceBlue","preview","icegem-normal-64.png");
            using(var pointer=Image.FromFile(pointerPath))
            for(int frame=0;frame<60;frame++) {
                using(var bitmap=new Bitmap(960,300,PixelFormat.Format32bppPArgb))
                using(var g=Graphics.FromImage(bitmap))
                using(var font=new Font("Segoe UI",12)) {
                    g.Clear(dark ? Color.FromArgb(23,38,56) : Color.FromArgb(239,245,249));
                    string[] labels={"Follow","Hover","Press / release","Drag"};
                    for(int col=0;col<4;col++) {
                        float px=col*240+70, py=140;
                        var m=new Motion {Size=56};
                        m.Move(px,py,0);
                        double now=frame/30.0;
                        if(col==0) {
                            for(int i=0;i<=frame;i++) { m.Move(px+(float)Math.Sin(i/30.0*Math.PI)*30,py,i/30.0); m.Step(i/30.0); }
                        } else if(col==1) { m.SetRole(Role.Link,0); for(int i=0;i<=frame;i++) m.Step(i/30.0); }
                        else if(col==2) { if(now>=.35) m.Button(true,.35); if(now>=.65) m.Button(false,.65); m.Step(now); }
                        else { m.Button(true,0); m.Move(px+12,py,.1); for(int i=0;i<=frame;i++) m.Step(i/30.0); }
                        using(var text=new SolidBrush(dark ? Color.FromArgb(209,226,245) : Color.FromArgb(41,66,97))) g.DrawString(labels[col],font,text,col*240+18,22);
                        // 保持与原生 PNG 相同的尖端热点，展示主光标和伴随晶片的实际间距。
                        g.DrawImage(pointer,m.Pointer.X-6*m.Size/32,m.Pointer.Y-3*m.Size/32,m.Size,m.Size);
                        Artwork.Draw(g,m,now,"IceBlue",PointF.Empty);
                    }
                    bitmap.Save(Path.Combine(folder,string.Format("frame-{0:D2}.png",frame)),ImageFormat.Png);
                }
            }
        }
    }
}
