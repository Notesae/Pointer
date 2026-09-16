#!/usr/bin/env python3
"""One-time tracing of the approved-direction ImageGen atlas into editable SVG.

Optional tooling: vtracer==0.6.15, svgelements==1.9.6.
The build consumes committed SVG masters; it does not need the bitmap or AI.
"""
import argparse
import copy
import json
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
import vtracer
from svgelements import Path as SvgPath

ROOT=Path(__file__).resolve().parents[1]
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
# Gray reference tile is intentionally not imported: only two theme colorways.
TILES={(0,0):'pointer-pink',(1,0):'pointer-coffee',(2,0):'text',
       (0,1):'paw-pink',(1,1):'paw-coffee'}
PRESETS={'small':dict(filter_speckle=28,color_precision=6,layer_difference=12,length_threshold=6),
         'medium':dict(filter_speckle=6,color_precision=7,layer_difference=8,length_threshold=4),
         'detail':dict(filter_speckle=4,color_precision=8,layer_difference=4,length_threshold=3)}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('atlas');args=parser.parse_args()
    reports=[]
    with tempfile.TemporaryDirectory() as tmp:
        repair_source=Path(tmp)/'repair-source.svg'
        vtracer.convert_image_to_svg_py(args.atlas,str(repair_source),colormode='color',hierarchical='stacked',mode='spline',corner_threshold=60,max_iterations=10,splice_threshold=45,path_precision=2,**PRESETS['medium'])
        toe=next(n for n in ET.parse(repair_source).getroot() if (lambda b:b and b[0]>650 and b[2]<700 and b[1]>245 and b[3]<295)(SvgPath(n.attrib).bbox()))
        for level,settings in PRESETS.items():
            traced=Path(tmp)/'trace.svg'
            vtracer.convert_image_to_svg_py(args.atlas,str(traced),colormode='color',hierarchical='stacked',mode='spline',corner_threshold=60,max_iterations=10,splice_threshold=45,path_precision=2,**settings)
            buckets={name:[] for name in TILES.values()}
            for node in ET.parse(traced).getroot():
                fill=node.attrib.get('fill','#000000')
                r,g,b=[int(fill[i:i+2],16) for i in (1,3,5)]
                if g>120 and g>r*1.28 and g>b*1.28: continue
                # De-spill residual green in anti-aliased boundary paths, in
                # vector space; retain cream fur, pink pads and golden bell.
                if g > r*.92 and b < r*.90:
                    g=round((r+b)/2)
                    node.set('fill',f'#{r:02x}{g:02x}{b:02x}')
                bounds=SvgPath(node.attrib).bbox()
                if not bounds: continue
                x0,y0,x1,y1=bounds
                tile=(int((x0+x1)/2//512),int((y0+y1)/2//512))
                if tile in TILES: buckets[TILES[tile]].append(node)
            for name,nodes in buckets.items():
                root=ET.Element(f'{{{NS}}}svg',width='64',height='64',viewBox='0 0 64 64')
                ET.SubElement(root,f'{{{NS}}}title').text=f'Cat Paw {name} / {level} / editable traced paths'
                if name.startswith('pointer'):
                    tip=154 if name.endswith('pink') else 644
                    transform=f'translate(6 5) scale(.17) translate({-tip} -98)'
                elif name=='text':
                    transform='translate(32 32) scale(.095 .157) translate(-1270 -248)'
                else:
                    center=270 if name.endswith('pink') else 764
                    transform=f'translate(32 32) scale(.137) translate({-center} -737)'
                wrapper=ET.SubElement(root,f'{{{NS}}}g',transform=transform)
                for node in nodes: wrapper.append(node)
                if name=='pointer-coffee':
                    # The generated coffee mark had three toes. Copy its left toe
                    # to the missing lower-left position: now exactly four + one.
                    repair=ET.SubElement(wrapper,f'{{{NS}}}g',{'data-detail':'fourth-toe','transform':'translate(668 302) scale(.72) translate(-674 -272)'})
                    repair.append(copy.deepcopy(toe))
                dest=ROOT/'assets/masters'/level/(name+'.svg');dest.parent.mkdir(parents=True,exist_ok=True)
                ET.ElementTree(root).write(dest,encoding='unicode',xml_declaration=False)
                reports.append({'file':str(dest.relative_to(ROOT)),'paths':len(list(root.iter(f'{{{NS}}}path'))),'preset':settings})
    # Coarse color clustering erased the tiny pointer prints. Keep their medium
    # shapes at 24/32 px, removing only subpixel glints, never a toe or main pad.
    for color in ('pink','coffee'):
        source=ROOT/f'assets/masters/medium/pointer-{color}.svg'
        root=ET.parse(source).getroot()
        for parent in root.iter():
            for node in list(parent):
                if node.tag.endswith('}path'):
                    b=SvgPath(node.attrib).bbox()
                    if b and (b[2]-b[0])*(b[3]-b[1])<10: parent.remove(node)
        dest=ROOT/f'assets/masters/small/pointer-{color}.svg'
        ET.ElementTree(root).write(dest,encoding='unicode',xml_declaration=False)
        for record in reports:
            if record['file']==str(dest.relative_to(ROOT)):
                record['paths']=len(list(root.iter(f'{{{NS}}}path')))
                record['opticalCorrection']='medium palette preserves four toes; subpixel glints removed'
    (ROOT/'assets/masters/trace-report.json').write_text(json.dumps(reports,indent=2)+'\n')
    print('Imported 5 masters × 3 optical detail levels; no gray colorway.')

if __name__=='__main__': main()
