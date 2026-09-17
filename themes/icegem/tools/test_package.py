"""跨平台复核发行包：版本、资源一致性、Xcursor 结构、别名与校验值。"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import struct
import tarfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]

class PackageTests(unittest.TestCase):
    """直接验证用户下载的安装包，不仅验证本地构建目录。"""
    def test_windows_package(self):
        """安装包中的源文件、二进制及五色所有 CUR/ANI 与本次构建保持一致。"""
        with zipfile.ZipFile(ROOT/'dist/IceGem-4.2-Color-Collection.zip') as archive:
            self.assertIsNone(archive.testzip())
            for color in ('IceBlue','Violet','RosePink','Mint','Amber'):
                folder=ROOT/'variants'/color
                self.assertEqual(json.loads(archive.read(f'IceGem-Colors/{color}/theme.json'))['version'],'4.2')
                for path in (folder/'cursors').rglob('*'):
                    if path.is_file():self.assertEqual(archive.read('IceGem-Colors/'+color+'/'+path.relative_to(folder).as_posix()),path.read_bytes())
            for path in (ROOT/'companion').iterdir():
                if path.is_file() and not path.name.startswith('.'):
                    self.assertEqual(archive.read('IceGem-Colors/companion/'+path.name),path.read_bytes())

    def test_linux_package(self):
        """校验五尺寸、每角色时间表、预乘 Alpha、可见热点以及所有符号链接目标。"""
        path=ROOT/'dist/IceGem-4.2-Linux.tar.gz'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),path.with_name(path.name+'.sha256').read_text().split()[0])
        with tarfile.open(path) as archive:
            metadata=json.load(archive.extractfile('IceGem-Linux/manifest.json'))
            self.assertEqual(metadata['version'],'4.2-linux.1')
            self.assertEqual(len(metadata['themes']),10)
            files={entry.name:entry for entry in archive.getmembers()}
            for line in archive.extractfile('IceGem-Linux/SHA256SUMS').read().decode().splitlines():
                digest,name=line.split('  ',1)
                self.assertEqual(hashlib.sha256(archive.extractfile('IceGem-Linux/'+name).read()).hexdigest(),digest)
            cursor_count=0
            for name,entry in files.items():
                if entry.issym():
                    target=str(PurePosixPath(name).parent/entry.linkname)
                    self.assertIn(target,files)
                    self.assertTrue(files[target].isfile())
                if '/cursors/' not in name or not entry.isfile():continue
                role=next(role for role,aliases in metadata['aliases'].items() if aliases[0]==PurePosixPath(name).name)
                timing=metadata['animation'][role]
                frames=timing['frames'] if '-Animated/' in name else 1
                data=archive.extractfile(entry).read()
                self.assertEqual(struct.unpack_from('<4I',data),(0x72756358,16,0x10000,frames*5))
                end=16+12*frames*5
                periods={size:0 for size in metadata['sizes']}
                for index in range(frames*5):
                    kind,size,offset=struct.unpack_from('<3I',data,16+index*12)
                    self.assertEqual(offset,end)
                    h,t,n,v,w,height,hx,hy,delay=struct.unpack_from('<9I',data,offset)
                    self.assertEqual((h,t,n,v,w,height),(36,0xfffd0002,size,1,size,size))
                    self.assertTrue(0<=hx<size and 0<=hy<size)
                    pixels=data[offset+36:offset+36+size*size*4]
                    self.assertEqual(len(pixels),size*size*4)
                    self.assertGreater(pixels[(hy*size+hx)*4+3],0)
                    self.assertTrue(all(max(b,g,r)<=a for b,g,r,a in struct.iter_unpack('4B',pixels)))
                    periods[size]+=delay
                    end=offset+36+len(pixels)
                self.assertEqual(end,len(data))
                self.assertEqual(set(periods.values()),{timing['periodMs'] if frames>1 else 0})
                cursor_count+=1
            self.assertEqual(cursor_count,180)

if __name__=='__main__':
    unittest.main()
