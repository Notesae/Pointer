from pathlib import Path
import struct,json
from build import ANIMATIONS
ROOT=Path(__file__).resolve().parents[1]
counts={'cur_files':0,'ani_files':0,'images':0,'ani_frames':0}
def check_cur(b):
 r,t,n=struct.unpack_from('<HHH',b);assert (r,t)==(0,2) and n in (1,3)
 end=6+16*n
 for i in range(n):
  w,h,cc,res,hx,hy,length,off=struct.unpack_from('<BBBBHHII',b,6+16*i)
  assert w==h and w in (32,48,64) and hx<w and hy<h and off==end
  header=struct.unpack_from('<IiiHHIIiiII',b,off)
  assert header[:7]==(40,w,h*2,1,32,0,w*h*4+((w+31)//32)*4*h)
  assert length==40+header[6] and off+length<=len(b)
  alphas=b[off+43:off+40+w*h*4:4];assert min(alphas)==0 and max(alphas)>200
  assert alphas[(h-1-hy)*w+hx]>0
  counts['images']+=1;end=off+length
 assert end==len(b)
def chunks(b,start,end):
 p=start
 while p<end:
  tag=b[p:p+4];n=struct.unpack_from('<I',b,p+4)[0];assert p+8+n<=end
  yield tag,b[p+8:p+8+n];p+=8+n+(n%2)
 assert p==end
for path in sorted((ROOT/'cursors').rglob('*.cur')):check_cur(path.read_bytes());counts['cur_files']+=1
for path in sorted((ROOT/'cursors').rglob('*.ani')):
 b=path.read_bytes();assert b[:4]==b'RIFF' and b[8:12]==b'ACON' and struct.unpack_from('<I',b,4)[0]+8==len(b)
 # 校验当前角色的实际帧数和精确时长，避免新动画被固定 24 帧规则误判。
 expected=ANIMATIONS[path.stem.removeprefix('icegem-')]
 count=len(expected)
 cs=dict(chunks(b,12,len(b)));a=struct.unpack('<9I',cs[b'anih']);assert a[0:3]==(36,count,count) and a[8]==1
 rates=struct.unpack(f'<{count}I',cs[b'rate']);assert rates==expected
 frames=list(chunks(cs[b'LIST'],4,len(cs[b'LIST'])));assert cs[b'LIST'][:4]==b'fram' and len(frames)==count
 assert len(set(data for tag,data in frames))>1
 for tag,data in frames:assert tag==b'icon';check_cur(data);counts['ani_frames']+=1
 counts['ani_files']+=1
print(json.dumps(counts,indent=2));(ROOT/'docs/validation.json').write_text(json.dumps({'result':'PASS: binary structure, bounds, alpha, hotspots, animated frame variation','counts':counts,'windows_runtime':'NOT RUN; use tools/Validate-Windows.ps1'},indent=2))
