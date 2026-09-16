"""Validate Xcursor bytes, aliases and actual libXcursor loading without a display."""
from pathlib import Path
import argparse
import ctypes as C
import ctypes.util
import json
import os
import struct
from build import ALIASES, SIZES, ANIMATED, FRAMES, PERIOD, hotspot


class CursorImage(C.Structure):
    _fields_ = [(key, C.c_uint32) for key in ('version', 'size', 'width', 'height', 'xhot', 'yhot', 'delay')] + [('pixels', C.POINTER(C.c_uint32))]


class CursorImages(C.Structure):
    _fields_ = [('nimage', C.c_int), ('images', C.POINTER(C.POINTER(CursorImage))), ('name', C.c_char_p)]


def validate(folder):
    library = ctypes.util.find_library('Xcursor')
    if not library:
        raise RuntimeError('libXcursor is required for native loading validation')
    lib = C.CDLL(library)
    ptr = C.POINTER(CursorImages)
    lib.XcursorFilenameLoadImages.argtypes = [C.c_char_p, C.c_int]
    lib.XcursorFilenameLoadImages.restype = ptr
    lib.XcursorLibraryLoadImages.argtypes = [C.c_char_p, C.c_char_p, C.c_int]
    lib.XcursorLibraryLoadImages.restype = ptr
    lib.XcursorImagesDestroy.argtypes = [ptr]
    os.environ['XCURSOR_PATH'] = str(folder.resolve()) + ':/usr/share/icons'
    counts = {'themes': 0, 'canonical_files': 0, 'native_file_loads': 0, 'native_alias_loads': 0}
    for theme in sorted(folder.glob('CatPaw-*')):
        counts['themes'] += 1
        for state, aliases in ALIASES.items():
            path = theme / 'cursors' / aliases[0]
            frames = FRAMES if theme.name.endswith('Animated') and state in ANIMATED else 1
            b = path.read_bytes()
            magic, header, version, ntoc = struct.unpack_from('<4I', b)
            assert (magic, header, version, ntoc) == (0x72756358, 16, 0x10000, frames * len(SIZES))
            assert not (theme/'cursors/click').exists()
            digests = {size:set() for size in SIZES}
            end = 16 + 12 * ntoc
            periods = {size: 0 for size in SIZES}
            for k in range(ntoc):
                kind, nominal, offset = struct.unpack_from('<3I', b, 16 + k * 12)
                assert kind == 0xfffd0002 and nominal in SIZES and offset == end
                h, t, n, v, width, height, hx, hy, delay = struct.unpack_from('<9I', b, offset)
                assert (h, t, n, v, width, height) == (36, kind, nominal, 1, nominal, nominal)
                assert 0 <= hx < width and 0 <= hy < height
                pixels = b[offset + 36:offset + 36 + width * height * 4]
                assert len(pixels) == width * height * 4
                assert (hx,hy)==hotspot(state,nominal), (path,nominal,hx,hy)
                if state != 'wait':
                    assert pixels[(hy * width + hx) * 4 + 3] > 0, (path, nominal, hx, hy)
                for blue, green, red, alpha in struct.iter_unpack('4B', pixels):
                    assert max(blue, green, red) <= alpha
                digests[nominal].add(hash(pixels))
                periods[nominal] += delay
                end = offset + 36 + len(pixels)
            assert end == len(b)
            if frames > 1:
                assert set(periods.values()) == {PERIOD}
                assert all(len(digests[n]) == frames for n in SIZES), 'Animation frames must differ'
            else:
                assert set(periods.values()) == {0}
            for size in SIZES:
                loaded = lib.XcursorFilenameLoadImages(os.fsencode(path), size)
                assert loaded and loaded.contents.nimage == frames, path
                try:
                    for i in range(frames):
                        image = loaded.contents.images[i].contents
                        assert (image.size, image.width, image.height) == (size, size, size)
                        assert image.xhot < size and image.yhot < size
                finally:
                    lib.XcursorImagesDestroy(loaded)
                counts['native_file_loads'] += 1
            for alias in aliases:
                alias_path = theme / 'cursors' / alias
                assert alias_path.resolve() == path.resolve()
                loaded = lib.XcursorLibraryLoadImages(alias.encode(), theme.name.encode(), 32)
                assert loaded and loaded.contents.nimage == frames, alias_path
                lib.XcursorImagesDestroy(loaded)
                counts['native_alias_loads'] += 1
            counts['canonical_files'] += 1
    assert counts['themes'] == 4
    result = {'result': 'PASS', 'checks': ['Xcursor structure', 'premultiplied alpha', 'hotspots', 'frame delays', 'libXcursor loading', 'theme alias resolution'], 'counts': counts, 'zorin_desktop': 'NOT RUN: desktop/session/HiDPI must be tested on Zorin'}
    (folder.parent / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('folder', nargs='?', type=Path, default=Path(__file__).resolve().parent / 'themes')
    validate(p.parse_args().folder)
