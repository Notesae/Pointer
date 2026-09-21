"""验证 IceGem 动效时序、周期闭合、热点及静态角色稳定性。"""
from pathlib import Path
import importlib.util
import unittest
from PIL import ImageChops, ImageStat

ROOT=Path(__file__).resolve().parents[1]

class MotionTests(unittest.TestCase):
    """用实际五色渲染器验证用户可感知的动效约束。"""
    def test_approved_unavailable_preview(self):
        """检查失能下垂五色多尺寸与确认稿相同，热点、标识和首尾保持稳定。"""
        import preview_unavailable_tail_drop as approved
        for color in ('IceBlue','Violet','RosePink','Mint','Amber'):
            spec=importlib.util.spec_from_file_location(color,ROOT/'variants'/color/'tools/build.py')
            renderer=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(renderer)
            self.assertEqual((len(renderer.ANIMATIONS['unavailable']),sum(renderer.ANIMATIONS['unavailable'])),(125,300))
            for size in (24,32,48,64,96):
                first=renderer.render(renderer.geometry('unavailable',0),size)
                self.assertEqual(first.tobytes(),renderer.render(renderer.geometry('unavailable',124),size).tobytes())
                for frame in (0,20,40,55,75,95,115,124):
                    with self.subTest(color=color,size=size,frame=frame):
                        actual=renderer.render(renderer.geometry('unavailable',frame),size)
                        self.assertEqual(actual.tobytes(),approved.proposal(renderer,size,frame).tobytes())
                        self.assertEqual(renderer.hotspot('unavailable',size),(round(6*size/32),round(3*size/32)))
                        self.assertGreater(actual.getpixel(renderer.hotspot('unavailable',size))[3],0)
            images=[renderer.render(renderer.geometry('unavailable',frame),32) for frame in range(125)]
            self.assertEqual(len({im.crop((24,7,30,16)).tobytes() for im in images}),1)
            self.assertTrue(all(im.getpixel((6,3))[3]>0 for im in images))

    def test_approved_working_preview(self):
        """覆盖分离、环绕和回收的关键帧，正式五色输出必须与确认稿逐像素相同。"""
        import preview_working_split as approved
        for color in ('IceBlue','Violet','RosePink','Mint','Amber'):
            spec=importlib.util.spec_from_file_location(color,ROOT/'variants'/color/'tools/build.py')
            renderer=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(renderer)
            for frame in (0,12,35,65,100,130,150,159):
                for size in (24,32,48,64,96):
                    with self.subTest(color=color,frame=frame,size=size):
                        self.assertEqual(approved.proposal(renderer,frame,size).tobytes(),
                                         renderer.render(renderer.geometry('working',frame),size).tobytes())

    def test_approved_text_preview(self):
        """以保留的已确认提案为独立基准，阻止正式接入改变五色材质或缩放比例。"""
        import preview_text_pedestal as approved
        for color in ('IceBlue','Violet','RosePink','Mint','Amber'):
            spec=importlib.util.spec_from_file_location(color,ROOT/'variants'/color/'tools/build.py')
            renderer=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(renderer)
            for frame in (0,12,38,56,74):
                for size in (24,32,48,64,96):
                    with self.subTest(color=color,frame=frame,size=size):
                        expected=approved.proposal(renderer,frame,size)
                        actual=renderer.render(renderer.geometry('text',frame),size)
                        self.assertEqual(expected.tobytes(),actual.tobytes())

    def test_motion_contract(self):
        """旋转帧率、停留节奏、周期、热点及可见边界必须在五色间保持一致。"""
        for color in ('IceBlue','Violet','RosePink','Mint','Amber'):
            spec=importlib.util.spec_from_file_location(color,ROOT/'variants'/color/'tools/build.py')
            renderer=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(renderer)
            # 默认多尺寸资源共用材质，各尺寸都保留热点及原动画的静止衔接。
            for size in (24,32,48,64,96):
                first=renderer.render(renderer.geometry('normal',0),size)
                hold=renderer.render(renderer.geometry('normal',96),size)
                self.assertEqual(first.tobytes(),hold.tobytes())
                self.assertGreater(first.getpixel(renderer.hotspot('normal',size))[3],0)
            self.assertEqual((len(renderer.ANIMATIONS['working']),sum(renderer.ANIMATIONS['working'])),(160,384))
            self.assertEqual(renderer.ANIMATIONS['busy'],(2,)*36)
            self.assertGreater(renderer.ROTATION_AMPLITUDES['link'],renderer.ROTATION_AMPLITUDES['normal'])
            self.assertEqual(sum(renderer.ANIMATIONS['normal']),192)
            # 长停留必须与下一轮起点完全一致，起停邻帧差异应小于中段，防止回正跳变。
            for role in ('normal','link'):
                count=len(renderer.ANIMATIONS[role])
                first=renderer.render(renderer.geometry(role,0),32)
                hold=renderer.render(renderer.geometry(role,count-1),32)
                self.assertEqual(first.tobytes(),hold.tobytes())
                near=renderer.render(renderer.geometry(role,1),32)
                before=renderer.render(renderer.geometry(role,count-2),32)
                middle=renderer.render(renderer.geometry(role,count//2),32)
                after=renderer.render(renderer.geometry(role,count//2+1),32)
                mid_delta=sum(ImageStat.Stat(ImageChops.difference(middle,after)).mean)
                self.assertLess(sum(ImageStat.Stat(ImageChops.difference(first,near)).mean),mid_delta)
                self.assertLess(sum(ImageStat.Stat(ImageChops.difference(before,hold)).mean),mid_delta)
            for name,rates in renderer.ANIMATIONS.items():
                with self.subTest(color=color,state=name):
                    self.assertEqual(renderer.svg(renderer.geometry(name,0)),renderer.svg(renderer.geometry(name,len(rates))))
                    images=[renderer.render(renderer.geometry(name,f),32) for f in range(len(rates))]
                    self.assertGreater(len({im.tobytes() for im in images}),10)
                    self.assertTrue(all(im.getpixel(renderer.hotspot(name,32))[3]>0 for im in images))
                    if name in renderer.ROTATION_AMPLITUDES:
                        self.assertIn('transform="rotate(',renderer.svg(renderer.geometry(name,1)))
                    if name in ('working','busy'):
                        if name=='busy':
                            self.assertEqual(len({im.tobytes() for im in images}),len(rates))
                        else:
                            # 两圈环绕允许跨圈重复姿态；相邻帧必须变化，禁止中途卡帧。
                            self.assertTrue(all(a.tobytes()!=b.tobytes()
                                                for a,b in zip(images[40:119],images[41:120])))
                            self.assertGreaterEqual(len({im.tobytes() for im in images}),150)
                        deltas=[sum(ImageStat.Stat(ImageChops.difference(images[f],images[(f+1)%len(images)])).mean) for f in range(len(images))]
                        self.assertLessEqual(deltas[-1],max(deltas[:-1])*1.4)
                        for size in (24,32,48,64,96):
                            im=renderer.render(renderer.geometry(name,len(rates)//2),size)
                            self.assertGreater(im.getpixel(renderer.hotspot(name,size))[3],0)
                            alpha=im.getchannel('A')
                            for box in ((0,0,size,1),(0,size-1,size,size),(0,0,1,size),(size-1,0,size,size)):
                                self.assertLess(alpha.crop(box).getextrema()[1],16)
            # 展台的晶石允许浮动倾摆，热点仍固定在柱身；每轮 75 帧、3 秒并闭合。
            for name in ('text','vertical-text'):
                rates=renderer.ANIMATIONS[name]
                self.assertEqual((len(rates),sum(rates)),(75,180))
                first=renderer.render(renderer.geometry(name,0),64)
                hold=renderer.render(renderer.geometry(name,len(rates)),64)
                middle=renderer.render(renderer.geometry(name,len(rates)//2),64)
                self.assertEqual(first.tobytes(),hold.tobytes())
                self.assertNotEqual(first.tobytes(),middle.tobytes())
                for size in (24,32,48,64,96):
                    for frame in (0,18,38,56,74):
                        im=renderer.render(renderer.geometry(name,frame),size)
                        self.assertEqual(renderer.hotspot(name,size),(round(size/2),round(size/2)))
                        self.assertGreater(im.getpixel(renderer.hotspot(name,size))[3],0)
                        for box in ((0,0,size,1),(0,size-1,size,size),(0,0,1,size),(size-1,0,size,size)):
                            self.assertLess(im.getchannel('A').crop(box).getextrema()[1],16)
                # 循环接缝不能比运动中段产生更大的像素跳变。
                before=renderer.render(renderer.geometry(name,len(rates)-1),32)
                start=renderer.render(renderer.geometry(name,0),32)
                samples=[renderer.render(renderer.geometry(name,f),32) for f in range(len(rates))]
                deltas=[sum(ImageStat.Stat(ImageChops.difference(a,b)).mean) for a,b in zip(samples,samples[1:])]
                self.assertLessEqual(sum(ImageStat.Stat(ImageChops.difference(before,start)).mean),max(deltas)*1.4)
            for name in ('precision','alternate','handwriting'):
                self.assertEqual(renderer.svg(renderer.geometry(name,0)),renderer.svg(renderer.geometry(name,12)))

if __name__=='__main__':
    unittest.main()
