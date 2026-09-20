"""Build native multi-size Xcursor themes from the existing IceGem SVG renderer."""
from pathlib import Path
import argparse
import importlib.util
import json
import struct
from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
COLORS = ('IceBlue', 'Violet', 'RosePink', 'Mint', 'Amber')
SIZES = (24, 32, 48, 64, 96)
# 支持原生动画的角色；实际帧数和时长从配色生成器读取。
ANIMATED = ('normal','working','busy','link','help','location','person','text','vertical-text','move','resize-ew','resize-ns','resize-nwse','resize-nesw')


def hotspot(renderer, name, size):
    # The added 24px pen tip lands between rows; round inward, not below the tip.
    return (5, 19) if name == 'handwriting' and size == 24 else renderer.hotspot(name, size)


ALIASES = {
    'normal': ('left_ptr', 'default', 'arrow', 'top_left_arrow'),
    'working': ('left_ptr_watch', 'progress', '08e8e1c95fe2fc01f976f1e063a24ccd'),
    'busy': ('watch', 'wait'),
    'help': ('question_arrow', 'help', 'left_ptr_help', 'whats_this'),
    'link': ('hand2', 'pointer', 'hand1', 'hand', 'e29285e634086352946a0e7090d73106'),
    'unavailable': ('crossed_circle', 'not-allowed', 'forbidden', 'no-drop'),
    'text': ('xterm', 'text', 'ibeam'),
    'vertical-text': ('vertical-text',),
    'precision': ('crosshair', 'cross', 'tcross', 'plus'),
    'resize-nwse': ('size_fdiag', 'nwse-resize', 'nw-resize', 'se-resize', 'top_left_corner', 'bottom_right_corner', 'bd_double_arrow'),
    'resize-nesw': ('size_bdiag', 'nesw-resize', 'ne-resize', 'sw-resize', 'top_right_corner', 'bottom_left_corner', 'fd_double_arrow'),
    'resize-ew': ('sb_h_double_arrow', 'ew-resize', 'e-resize', 'w-resize', 'col-resize', 'h_double_arrow', 'size_hor', 'split_h', 'left_side', 'right_side'),
    'resize-ns': ('sb_v_double_arrow', 'ns-resize', 'n-resize', 's-resize', 'row-resize', 'v_double_arrow', 'size_ver', 'split_v', 'top_side', 'bottom_side'),
    'move': ('fleur', 'move', 'all-scroll', 'size_all'),
    'alternate': ('up_arrow', 'center_ptr'),
    'handwriting': ('pencil',),
    'location': ('icegem-location',),
    'person': ('icegem-person',),
}


def encode(images):
    """Little-endian Xcursor v1 with premultiplied ARGB image chunks."""
    offset = 16 + 12 * len(images)
    toc, chunks = [], []
    for size, hotspot, delay, image in images:
        r, g, b, alpha = image.convert('RGBA').split()
        premul = Image.merge('RGBA', tuple(ImageChops.multiply(c, alpha) for c in (r, g, b)) + (alpha,))
        pixels = premul.tobytes('raw', 'BGRA')
        chunk = struct.pack('<9I', 36, 0xfffd0002, size, 1, size, size, *hotspot, delay) + pixels
        toc.append(struct.pack('<3I', 0xfffd0002, size, offset))
        chunks.append(chunk)
        offset += len(chunk)
    return struct.pack('<4I', 0x72756358, 16, 0x10000, len(images)) + b''.join(toc + chunks)


def build(variants, output):
    """复用五色渲染器与时序，生成动态、静态 Xcursor 主题及别名。"""
    output.mkdir(parents=True, exist_ok=True)
    metadata = {'version': '4.4-linux.1', 'animation': {}, 'sizes': SIZES, 'themes': [], 'aliases': ALIASES}
    for color in COLORS:
        spec = importlib.util.spec_from_file_location('icegem_' + color, variants / color / 'tools/build.py')
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        rendered = {}
        for name, _, _ in renderer.NAMES:
            # 与 Windows 共用 jiffy 时间表，累计取整保证 Linux 周期总长相同。
            rates = renderer.ANIMATIONS.get(name, (0,))
            frames = len(rates)
            metadata['animation'][name] = {'frames': frames, 'periodMs': round(sum(rates)*1000/60)}
            rendered[name] = [(n, hotspot(renderer, name, n),
                              round(sum(rates[:f+1])*1000/60) - round(sum(rates[:f])*1000/60) if frames > 1 else 0,
                              renderer.render(renderer.geometry(name, f), n))
                             for n in SIZES for f in range(frames)]
        for mode in ('Animated', 'Static'):
            theme = f'IceGem-{color}-{mode}'
            root = output / theme
            cursors = root / 'cursors'
            cursors.mkdir(parents=True, exist_ok=True)
            (root / 'index.theme').write_text(f'[Icon Theme]\nName=IceGem {color} {mode}\nComment=Faceted crystal cursor theme\nInherits=Adwaita\n', encoding='utf-8')
            (root / '.icegem-linux').write_text('IceGem-Linux-v1\n')
            for name, aliases in ALIASES.items():
                images = rendered[name]
                if mode == 'Static' and name in ANIMATED:
                    images = [(n, h, 0, im) for n, h, _, im in images[::len(renderer.ANIMATIONS[name])]]
                canonical = cursors / aliases[0]
                canonical.write_bytes(encode(images))
                for alias in aliases[1:]:
                    link = cursors / alias
                    if link.is_symlink():
                        link.unlink()
                    elif link.exists():
                        raise FileExistsError(f'Refusing to replace non-symlink: {link}')
                    link.symlink_to(canonical.name)
            metadata['themes'].append(theme)
        print(f'{color}: animated + static complete', flush=True)
    (output.parent / 'manifest.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    default = HERE / 'source/variants' if (HERE / 'source/variants').exists() else HERE.parent / 'variants'
    parser.add_argument('--variants', type=Path, default=default)
    parser.add_argument('--output', type=Path, default=HERE / 'themes')
    args = parser.parse_args()
    build(args.variants, args.output)
