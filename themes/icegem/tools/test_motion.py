"""验证 IceGem 动效时序、周期闭合、热点及静态角色稳定性。"""
from pathlib import Path
import importlib.util
import unittest
from PIL import ImageChops, ImageStat

ROOT=Path(__file__).resolve().parents[1]

class MotionTests(unittest.TestCase):
    """用实际五色渲染器验证用户可感知的动效约束。"""
    def test_motion_contract(self):
        """旋转帧率、停留节奏、周期、热点及可见边界必须在五色间保持一致。"""
        for color in ('IceBlue','Violet','RosePink','Mint','Amber'):
            spec=importlib.util.spec_from_file_location(color,ROOT/'variants'/color/'tools/build.py')
            renderer=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(renderer)
            self.assertEqual(renderer.ANIMATIONS['working'],(2,)*48)
            self.assertEqual(renderer.ANIMATIONS['busy'],(2,)*36)
            self.assertEqual(sum(renderer.ANIMATIONS['normal']),192)
            for name,rates in renderer.ANIMATIONS.items():
                with self.subTest(color=color,state=name):
                    self.assertEqual(renderer.svg(renderer.geometry(name,0)),renderer.svg(renderer.geometry(name,len(rates))))
                    images=[renderer.render(renderer.geometry(name,f),32) for f in range(len(rates))]
                    self.assertGreater(len({im.tobytes() for im in images}),10)
                    self.assertTrue(all(im.getpixel(renderer.hotspot(name,32))[3]>0 for im in images))
                    if name in ('working','busy'):
                        self.assertEqual(len({im.tobytes() for im in images}),len(rates))
                        deltas=[sum(ImageStat.Stat(ImageChops.difference(images[f],images[(f+1)%len(images)])).mean) for f in range(len(images))]
                        self.assertLessEqual(deltas[-1],max(deltas[:-1])*1.4)
                        for size in (24,32,48,64,96):
                            im=renderer.render(renderer.geometry(name,len(rates)//2),size)
                            self.assertGreater(im.getpixel(renderer.hotspot(name,size))[3],0)
                            alpha=im.getchannel('A')
                            for box in ((0,0,size,1),(0,size-1,size,size),(0,0,1,size),(size-1,0,size,size)):
                                self.assertLess(alpha.crop(box).getextrema()[1],16)
            for name in ('text','vertical-text','precision','unavailable','alternate','handwriting'):
                self.assertEqual(renderer.svg(renderer.geometry(name,0)),renderer.svg(renderer.geometry(name,12)))

if __name__=='__main__':
    unittest.main()
