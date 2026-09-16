#!/usr/bin/env python3
"""Check delivery coverage, SVG safety, sizes, hotspots and raster clipping."""
import json
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
theme=json.loads((ROOT/'theme.json').read_text())
manifest=json.loads((ROOT/'assets/manifest.json').read_text())
states={'normal','link','click','busy','help','text','precision','move','resize-h','resize-v','resize-d1','resize-d2','drag','disabled'}
expected={(c,s,n) for c in theme['colorways'] for s in theme['sizes'] for n in states}
actual={(i['color'],i['size'],i['state']) for i in manifest['cursors']}
assert expected==actual and len(actual)==len(manifest['cursors'])
ns='{http://www.w3.org/2000/svg}'
for item in manifest['cursors']:
    f=ROOT/item['file']; root=ET.parse(f).getroot(); size=item['size']
    assert root.tag==ns+'svg' and root.attrib['width']==str(size) and root.attrib['height']==str(size), f
    assert all(0<=v<size for v in item['hotspot']), f
    png=ROOT/'preview/raster'/item['color']/str(size)/(item['state']+'.png')
    data=png.read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(size,size),png
    # No text/fonts, external links or embedded bitmaps in usable cursor assets.
    for node in root.iter():
        assert node.tag not in {ns+'text',ns+'image',ns+'script',ns+'foreignObject'},f
        assert not any('href' in k for k in node.attrib),f
assert set(theme['colorways'])=={'pink','coffee'}, 'This release has exactly two requested colorways.'
for level in ('small','medium','detail'):
    repaired=ET.parse(ROOT/f'assets/masters/{level}/pointer-coffee.svg').getroot()
    assert any(n.attrib.get('data-detail')=='fourth-toe' for n in repaired.iter()), 'Missing coffee toe repair'
assert len(manifest['compositions'])==len(states)*len(theme['colorways'])
for f in (ROOT/'assets').rglob('*.svg'):
    root=ET.parse(f).getroot()
    ids=[n.attrib['id'] for n in root.iter() if 'id' in n.attrib]
    assert len(ids)==len(set(ids)), (f,'duplicate paint definition')
    for node in root.iter():
        for value in node.attrib.values():
            if value.startswith('url(#'):
                assert value[5:-1] in ids,(f,'missing gradient',value)
for color in theme['colorways']:
    # Small-size artwork must be deliberately simplified, not only resized.
    small=ET.parse(ROOT/f'assets/paw-{color}/32/paw.svg').getroot()
    large=ET.parse(ROOT/f'assets/paw-{color}/64/paw.svg').getroot()
    assert len(list(small.iter()))<len(list(large.iter()))
try:
    from PIL import Image
except ImportError:
    print('Pillow not installed: alpha/clipping checks skipped (install Pillow to enable).')
else:
    for item in manifest['cursors']:
        f=ROOT/'preview/raster'/item['color']/str(item['size'])/(item['state']+'.png')
        alpha=Image.open(f).getchannel('A'); bbox=alpha.getbbox(); size=item['size']
        assert bbox and bbox[0]>0 and bbox[1]>0 and bbox[2]<size and bbox[3]<size, (f,bbox)
        hx,hy=item['hotspot']
        # Crosshair/resize etc. have real content at the interaction origin.
        assert alpha.getpixel((hx,hy))>0,(f,'empty hotspot')
    print('PNG transparency, non-clipping and hotspot checks passed.')
print(f'Validated {len(actual)} state/size/color combinations and 28 two-layer references.')
