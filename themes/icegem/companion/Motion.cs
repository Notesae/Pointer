using System;
using System.Drawing;
using System.Drawing.Drawing2D;

namespace IceGem {
    // 角色语义决定装饰是否可见；不会替换系统光标或改变热点。
    public enum Role { Normal, Link, Text, Hidden }

    // 与窗口及输入 API 无关的确定性运动模型，供运行时和回归测试共用。
    public sealed class Motion {
        // 位置均为物理屏幕像素，时间为单调递增秒数。
        public PointF Pointer, Shards, PressOrigin, FlashOrigin;
        public Role Role = Role.Normal;
        public bool Down, Dragging, Enabled = true, Follow = true, Click = true;
        public float Size = 32, OffsetX = 1, OffsetY = 1, Strength = 1;
        public double LastInput, PressAt, ReleaseAt = -10, HoverAt = -10, IdleAt = -10;
        public bool IdleUsed;
        // DragBlend 在拖动与伴行排列之间平滑收束，避免晶片瞬间跳位。
        public float Gather, Hover, DragBlend;
        private double last;
        private bool initialized;

        // 原生指针立即跟手；只有独立晶片通过有上限的时间常数追随。
        public void Move(float x, float y, double now) {
            if (Pointer.X == x && Pointer.Y == y && initialized) return;
            Pointer = new PointF(x,y); LastInput = now; IdleUsed = false; IdleAt = -10;
            if (Down && Distance(Pointer, PressOrigin) > Math.Max(3, Size*.12f)) Dragging = true;
            if (!initialized || Distance(Shards,Target()) > Size*4) {
                Shards = Target(); last = now; initialized = true;
            }
        }

        // 按下聚光，松开只在非拖动时产生一次固定于释放位置的折射闪光。
        public void Button(bool pressed, double now) {
            if (Down == pressed) return;
            Down = pressed; LastInput = now; IdleUsed = false; IdleAt = -10;
            if (pressed) { PressAt = now; PressOrigin = Pointer; ReleaseAt = -10; }
            else { ReleaseAt = Dragging ? -10 : now; FlashOrigin = Pointer; Dragging = false; }
        }

        // 文本与未知精确角色不绘制伴随层，切换角色时不遗留点击或待机效果。
        public void SetRole(Role role, double now) {
            if (Role == role) return;
            Role = role; HoverAt = now; IdleAt = -10; IdleUsed = false;
            if (role == Role.Hidden || role == Role.Text) ReleaseAt = -10;
        }

        public bool Visible { get { return Enabled && Strength>0 && Role != Role.Hidden && Role != Role.Text; } }
        public static float Distance(PointF a, PointF b) { return (float)Math.Sqrt((a.X-b.X)*(a.X-b.X)+(a.Y-b.Y)*(a.Y-b.Y)); }

        // 以 32px 母版的主体尾部定位晶片，而不是用整个透明画布宽度作间距。
        private PointF Target() {
            float s=Size/32;
            return new PointF(Pointer.X+20*s*OffsetX,Pointer.Y+20*s*OffsetY);
        }

        // 指数阻尼不产生弹跳；停止运动后返回 false，宿主即可取消逐帧刷新。
        public bool Step(double now) {
            double dt = Math.Max(0,Math.Min(.05,now-last)); last=now;
            PointF target=Target();
            float blend = Follow ? (float)(1-Math.Exp(-dt/.055)) : 1;
            Shards = new PointF(Shards.X+(target.X-Shards.X)*blend, Shards.Y+(target.Y-Shards.Y)*blend);
            // 保留微小追随感，但快速甩动也只偏离停靠点 3.2px（以 32px 光标为基准），避免拖成远处的光点。
            float lag=Distance(Shards,target), limit=Size*.1f;
            if(lag>limit) Shards=new PointF(target.X+(Shards.X-target.X)*limit/lag,target.Y+(Shards.Y-target.Y)*limit/lag);
            // 第一颗晶片不能滑入主体右缘；镜像布局同样保持留白。
            float clearance=Size*.515625f;
            if((Shards.X-Pointer.X)*OffsetX<clearance) Shards.X=Pointer.X+clearance*OffsetX;
            float settle = (float)(1-Math.Exp(-dt/.035));
            float wanted = Down && Click ? 1 : 0;
            Gather += (wanted-Gather)*settle;
            Hover += ((Role==Role.Link ? 1 : 0)-Hover)*settle;
            float dragTarget=Dragging ? 1 : 0;
            DragBlend+=(dragTarget-DragBlend)*(float)(1-Math.Exp(-dt/.04));
            bool active = Distance(Shards,target)>.08 || Math.Abs(Gather-wanted)>.002 || Math.Abs(Hover-(Role==Role.Link ? 1 : 0))>.002 || Math.Abs(DragBlend-dragTarget)>.002;
            if (!active) { Shards=target; Gather=wanted; Hover=Role==Role.Link ? 1 : 0; DragBlend=dragTarget; }
            return active || (Click && now-ReleaseAt<.24) || now-IdleAt<.65 || (Click && Down && now-PressAt<.08);
        }

        // 待机只扫过一次晶片棱线，后续保持静止，直到新的输入重新计时。
        public void Idle(double now) {
            if (!IdleUsed && !Down && Visible && now-LastInput>=1.6) { IdleAt=now; IdleUsed=true; }
        }
    }

    // 渲染同一套晶片和折射图形，运行时透明窗口与离线预览共用。
    public static class Artwork {
        public static readonly string[] Colors = { "IceBlue", "Violet", "RosePink", "Mint", "Amber" };
        private static readonly Color[] Tints = { Color.FromArgb(112,190,238), Color.FromArgb(160,119,230), Color.FromArgb(228,132,183), Color.FromArgb(81,185,142), Color.FromArgb(224,167,77) };
        public static Color Tint(string name) { int i=Array.IndexOf(Colors,name); return Tints[Math.Max(0,i)]; }

        // 晶片是中心对称的细长菱形，不是缩小的箭头；长轴固定向右倾斜约 19 度。
        public static PointF[] ShardVertices(float x,float y,float r) {
            return new[]{new PointF(x-r*.34f,y-r),new PointF(x+r*.62f,y),new PointF(x+r*.34f,y+r),new PointF(x-r*.62f,y)};
        }

        // 伴行时一低一高；拖动时第二片绕外侧进入短列，避免穿过第一片。
        public static PointF[] ShardCenters(Motion m,PointF origin) {
            float s=m.Size/32, t=m.DragBlend;
            float x=m.Shards.X-origin.X, y=m.Shards.Y-origin.Y;
            // 主体四顶点的几何中心相对热点；拖动沿固定右下方向排列，后段中心距按轮廓尺寸缩短，使两段可见空隙接近。
            PointF main=new PointF(m.Pointer.X-origin.X+6.175f*s,m.Pointer.Y-origin.Y+13.65f*s);
            PointF first=new PointF(x*(1-t)+(main.X+15*s*m.OffsetX)*t,
                (y+2*s*m.OffsetY)*(1-t)+(main.Y+13*s*m.OffsetY)*t);
            float arc=(float)Math.Sin(Math.PI*t)*5*s;
            PointF second=new PointF((x+5.5f*s*m.OffsetX)*(1-t)+(first.X+.67f*(first.X-main.X))*t+arc*m.OffsetX,
                (y-5*s*m.OffsetY)*(1-t)+(first.Y+.67f*(first.Y-main.Y))*t);
            return new[]{first,second};
        }

        // 四块宽切面围绕中心交汇，细轮廓保持与主体一致的冰透材质。
        private static void Diamond(Graphics g,float x,float y,float r,Color tint,float highlight) {
            PointF[] p=ShardVertices(x,y,r);
            PointF ridge=new PointF(x,y);
            Color light=Color.FromArgb((tint.R+510)/3,(tint.G+510)/3,(tint.B+510)/3);
            Color dark=Color.FromArgb((int)(tint.R*.48),(int)(tint.G*.53),(int)(tint.B*.65));
            // 各面只保留一次折射渐变，缩小后仍有完整亮面和暗面，不堆叠微细装饰。
            for(int i=0;i<4;i++) {
                int faceIndex=(i+2)%4;
                Color start=faceIndex==1 ? tint : Color.FromArgb((tint.R+220)/2,(tint.G+240)/2,(tint.B+255)/2);
                Color end=faceIndex==1 ? Color.FromArgb(248,254,255) : faceIndex==2 || faceIndex==0 ? light : tint;
                using(var face=new LinearGradientBrush(new PointF(x+r,y+r),new PointF(x-r,y-r),start,end))
                    g.FillPolygon(face,new[]{p[i],p[(i+1)%4],ridge});
            }
            using(var edge=new Pen(dark,Math.Max(.7f,r*.13f))) {edge.LineJoin=LineJoin.Round;g.DrawPolygon(edge,p);}
            using(var edge=new Pen(Color.FromArgb(235+(int)(20*highlight),250,255),Math.Max(.55f,r*.1f)))
                g.DrawLines(edge,new[]{ridge,p[0],p[3]});
            using(var edge=new Pen(light,Math.Max(.5f,r*.09f))) g.DrawLines(edge,new[]{p[3],ridge,p[1]});
        }

        // 所有装饰相对真实热点绘制，主光标始终由操作系统绘制。
        public static void Draw(Graphics g, Motion m, double now, string color, PointF origin) {
            if (!m.Visible) return;
            g.SmoothingMode=SmoothingMode.AntiAlias;
            float s=m.Size/32, strength=m.Strength;
            Color tint=Tint(color);
            float idle=now-m.IdleAt<.65 ? (float)Math.Pow(Math.Sin(Math.PI*Math.Max(0,now-m.IdleAt)/.65),2) : 0;
            float hover=m.Hover;
            // 朝向不随移动方向翻转；仅调整排列，按下轻收束、悬停提亮棱线。
            PointF[] centers=ShardCenters(m,origin);
            float gather=1-.06f*m.Gather*(1-m.DragBlend);
            float shine=Math.Max(idle,hover*.55f);
            Diamond(g,centers[0].X,centers[0].Y,5.5f*s*gather,tint,shine);
            Diamond(g,centers[1].X,centers[1].Y,4.3f*s*gather,tint,shine);
            float px=m.Pointer.X-origin.X, py=m.Pointer.Y-origin.Y;
            // 折光从主体右缘上半段向右展开，与下方两颗伴随晶片保持间隙。
            if(hover>.01f && !m.Down) {
                for(int i=0;i<3;i++) {
                    double angle=(-20+i*20)*Math.PI/180;
                    float inner=(3+hover)*s, outer=(9+4*hover)*s;
                    float sideX=px+9*s, sideY=py+7*s;
                    PointF a=new PointF(sideX+(float)Math.Cos(angle)*inner,sideY+(float)Math.Sin(angle)*inner);
                    PointF b=new PointF(sideX+(float)Math.Cos(angle)*outer,sideY+(float)Math.Sin(angle)*outer);
                    // 细长双面折光：一侧冰白、一侧主题色，不叠加投影或雾状光晕。
                    float nx=-(float)Math.Sin(angle)*1.3f*s, ny=(float)Math.Cos(angle)*1.3f*s;
                    PointF mid=new PointF((a.X+b.X)/2,(a.Y+b.Y)/2);
                    using(var face=new SolidBrush(Color.FromArgb((int)(255*hover*strength),Color.FromArgb((int)(tint.R*.7f),(int)(tint.G*.82f),(int)(tint.B*.94f)))))
                        g.FillPolygon(face,new[]{a,new PointF(mid.X+nx,mid.Y+ny),b});
                    using(var face=new SolidBrush(Color.FromArgb((int)(255*hover*strength),Color.FromArgb(239,253,255))))
                        g.FillPolygon(face,new[]{a,b,new PointF(mid.X-nx,mid.Y-ny)});
                }
            }
            if (!m.Click) return;
            if (m.Down && !m.Dragging) {
                // 放大单圈聚光并提高线条亮度，保持单层轮廓与局部折射亮弧。
                float t=(float)Math.Min(1,Math.Max(0,(now-m.PressAt)/.08));
                float radius=(10-6*t)*s;
                using(var ring=new Pen(Color.FromArgb((int)(250*strength),tint),1.5f*s))
                    g.DrawEllipse(ring,px-radius,py-radius,radius*2,radius*2);
                using(var edge=new Pen(Color.FromArgb((int)(250*strength),Color.FromArgb(231,251,255)),1.1f*s))
                    g.DrawArc(edge,px-radius,py-radius,radius*2,radius*2,25,105);
            }
            double elapsed=now-m.ReleaseAt;
            if (elapsed>=0 && elapsed<.24) {
                // 四芒扩大约四成并延长至 240ms，稍宽的明暗切面保持尖锐轮廓。
                float t=(float)(elapsed/.24), fade=(float)Math.Pow(1-t,.85);
                float radius=(5+12*(1-(float)Math.Pow(1-t,3)))*s;
                px=m.FlashOrigin.X-origin.X; py=m.FlashOrigin.Y-origin.Y;
                for(int i=0;i<4;i++) {
                    double angle=i*Math.PI/2;
                    float dx=(float)Math.Cos(angle),dy=(float)Math.Sin(angle);
                    float length=radius*(i%2==0 ? .8f : 1),width=1.8f*s*(1-.5f*t);
                    PointF tip=new PointF(px+dx*length,py+dy*length),center=new PointF(px,py);
                    using(var face=new SolidBrush(Color.FromArgb((int)(255*fade*strength),Color.FromArgb((int)(tint.R*.7f),(int)(tint.G*.82f),(int)(tint.B*.94f)))))
                        g.FillPolygon(face,new[]{center,new PointF(px-dy*width,py+dx*width),tip});
                    using(var face=new SolidBrush(Color.FromArgb((int)(250*fade*strength),Color.FromArgb(239,252,255))))
                        g.FillPolygon(face,new[]{center,tip,new PointF(px+dy*width,py-dx*width)});
                }
            }
        }
    }
}
