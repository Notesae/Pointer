#!/usr/bin/env python3
"""Build native Xcursor themes. Artwork is rasterized from committed SVG masters."""
import argparse
import importlib.util
import json
import math
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageChops

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
COLORS=('pink','coffee')
SIZES=(24,32,48,64,96,128)
FRAMES=24
PERIOD=1000
ANIMATED={'wait','progress'}
OWNER='CatPaw-Linux-v1'
ALIASES={
    'normal':('left_ptr','default','arrow','top_left_arrow'),
    'link':('hand2','pointer','hand1','hand','e29285e634086352946a0e7090d73106'),
    'progress':('left_ptr_watch','progress','08e8e1c95fe2fc01f976f1e063a24ccd'),
    'wait':('watch','wait'),
    'help':('question_arrow','help','left_ptr_help','whats_this'),
    'text':('xterm','text','ibeam'),
    'vertical-text':('vertical-text',),
    'precision':('crosshair','cross','tcross','plus'),
    'move':('fleur','move','all-scroll','size_all'),
    'resize-h':('sb_h_double_arrow','ew-resize','e-resize','w-resize','col-resize','h_double_arrow','size_hor','split_h','left_side','right_side'),
    'resize-v':('sb_v_double_arrow','ns-resize','n-resize','s-resize','row-resize','v_double_arrow','size_ver','split_v','top_side','bottom_side'),
    'resize-d1':('bd_double_arrow','nwse-resize','nw-resize','se-resize','top_left_corner','bottom_right_corner','size_fdiag'),
    'resize-d2':('fd_double_arrow','nesw-resize','ne-resize','sw-resize','top_right_corner','bottom_left_corner','size_bdiag'),
    'grab':('openhand','grab','9d800788f1b08800ae810202380a0822'),
    'grabbing':('closedhand','grabbing','208530c400c041818281048008011002'),
    'disabled':('crossed_circle','not-allowed','forbidden','no-drop'),
}


def load_art():
    spec=importlib.util.spec_from_file_location('catpaw_art',ROOT/'tools/build_assets.py')
    art=importlib.util.module_from_spec(spec);spec.loader.exec_module(art)
    return art


def geometry(art,state,color,size,frame=0):
    if state in ('link','grab','grabbing'):
        # Bake a small separate paw into this role, with a stable arrow-tip hotspot.
        # This is a static role indicator, not independent trailing motion.
        s=art.group(art.arrow(color,size),'translate(6 5) scale(.80) translate(-6 -5)')
        rotation={'link':-5,'grab':-10,'grabbing':8}[state]
        scale=.40 if state=='grabbing' else .43
        s+=art.group(art.paw(color,size),f'translate(36 29) rotate({rotation} 12 12) scale({scale})')
        return s
    if state=='vertical-text':
        return art.group(art.cursor('text',color,size),'rotate(90 32 32)')
    if state in ANIMATED:
        s=''
        if state=='progress':
            s+=art.group(art.arrow(color,size),'translate(6 5) scale(.70) translate(-6 -5)')
        cx,cy,radius,scale=(40,38,16,.16) if state=='progress' else (32,32,20,.22)
        for i in range(8):
            degrees=i*45+frame*360/FRAMES
            a=math.radians(degrees)
            x,y=cx+radius*math.cos(a),cy+radius*math.sin(a)
            ink=art.THEME['colorways']['pink' if i%2==0 else 'coffee']['pad']
            s+=art.group(art.print_mark(ink),f'translate({x:.4f} {y:.4f}) rotate({degrees+90:.4f}) scale({scale}) translate(-32 -32)',f'opacity="{.32+.085*i:.3f}"')
        return s
    return art.cursor(state,color,size)


def hotspot(state,size):
    x,y=(6,5) if state in ('normal','link','help','progress','grab','grabbing') else (32,32)
    return round(x*size/64),round(y*size/64)


def encode(images):
    offset=16+12*len(images);toc=[];chunks=[]
    for size,hot,delay,image in images:
        r,g,b,a=image.convert('RGBA').split()
        pixels=Image.merge('RGBA',tuple(ImageChops.multiply(c,a) for c in (r,g,b))+(a,)).tobytes('raw','BGRA')
        chunk=struct.pack('<9I',36,0xfffd0002,size,1,size,size,*hot,delay)+pixels
        toc.append(struct.pack('<3I',0xfffd0002,size,offset));chunks.append(chunk);offset+=len(chunk)
    return struct.pack('<4I',0x72756358,16,0x10000,len(images))+b''.join(toc+chunks)


def build(node,output):
    art=load_art();output.mkdir(parents=True,exist_ok=True)
    manifest={'version':'0.5.0-linux.1','sizes':SIZES,'themes':[],'aliases':ALIASES,
              'animation':{'roles':sorted(ANIMATED),'frames':FRAMES,'periodMs':PERIOD},
              'click':'Companion-only; no native role', 'source':'committed Cat Paw SVG masters'}
    with tempfile.TemporaryDirectory(prefix='catpaw-render-') as directory:
        tmp=Path(directory);jobs=[]
        for color in COLORS:
            for state in ALIASES:
                for size in SIZES:
                    count=FRAMES if state in ANIMATED else 1
                    for frame in range(count):
                        stem=f'{color}-{state}-{size}-{frame}'
                        source=tmp/(stem+'.svg');dest=tmp/(stem+'.png')
                        source.write_text(art.svg(geometry(art,state,color,size,frame),size,title=f'Cat Paw Linux {state}'))
                        jobs.append({'source':str(source),'dest':str(dest)})
        index=tmp/'jobs.json';index.write_text(json.dumps(jobs))
        subprocess.run([node,str(HERE/'render.cjs'),str(index)],check=True)
        # Native role review must use exactly the same geometry as the binaries.
        review=art.rect(0,0,1600,700,'#FFF9F5')+art.text(35,45,'CAT PAW / LINUX NATIVE ROLES',24,weight=600)
        for ci,color in enumerate(COLORS):
            for i,state in enumerate(ALIASES):
                x=30+(i%8)*195;y=80+ci*300+(i//8)*145
                review+=art.group(geometry(art,state,color,64),f'translate({x+20} {y+8}) scale(1.15)')
                review+=art.text(x+4,y+112,f'{color} / {state}',14)
        (ROOT/'preview/Cat Paw Linux Roles.svg').write_text(art.svg(review,1600,700,'0 0 1600 700','Native Linux role artwork'))
        subprocess.run([node,str(HERE/'render.cjs'),'--preview'],check=True)
        for color in COLORS:
            rendered={}
            for state in ALIASES:
                count=FRAMES if state in ANIMATED else 1
                rendered[state]=[(size,hotspot(state,size),round((f+1)*PERIOD/count)-round(f*PERIOD/count) if count>1 else 0,
                                 Image.open(tmp/f'{color}-{state}-{size}-{f}.png').convert('RGBA'))
                                for size in SIZES for f in range(count)]
            for mode in ('Animated','Static','Companion','Companion-Static'):
                name=f'CatPaw-{color.title()}-{mode}';theme=output/name;cursor_dir=theme/'cursors'
                if theme.exists() and not (theme/'.catpaw-linux').is_file():
                    raise RuntimeError(f'Refusing to overwrite unowned output {theme}')
                cursor_dir.mkdir(parents=True,exist_ok=True)
                (theme/'index.theme').write_text(f'[Icon Theme]\nName=Cat Paw {color.title()} {mode}\nComment=Warm white cat paw cursor theme\nInherits=Adwaita\n')
                (theme/'.catpaw-linux').write_text(OWNER+'\n')
                expected={name for names in ALIASES.values() for name in names}
                stale={p.name for p in cursor_dir.iterdir()}-expected
                if stale: raise RuntimeError(f'Unexpected files in output: {stale}')
                for state,aliases in ALIASES.items():
                    frames=rendered['normal'] if 'Companion' in mode and state in ('link','grab','grabbing') else rendered[state]
                    if mode.endswith('Static') and state in ANIMATED:
                        frames=[(n,h,0,im) for n,h,_,im in frames[::FRAMES]]
                    canonical=cursor_dir/aliases[0]
                    if canonical.is_symlink(): raise RuntimeError(f'Unexpected canonical symlink {canonical}')
                    canonical.write_bytes(encode(frames))
                    for alias in aliases[1:]:
                        link=cursor_dir/alias
                        if link.is_symlink():link.unlink()
                        elif link.exists():raise RuntimeError(f'Refusing non-alias file {link}')
                        link.symlink_to(canonical.name)
                manifest['themes'].append(name)
                print(f'{name}: {len(ALIASES)} roles / {len(SIZES)} sizes',flush=True)
    (output.parent/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--node',default=shutil.which('node'));p.add_argument('--output',type=Path,default=HERE/'themes');args=p.parse_args()
    if not args.node:p.error('Node.js and sharp are needed to render SVGs')
    build(args.node,args.output)
