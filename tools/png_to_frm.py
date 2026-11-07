"""Convert PNG images (with alpha) into the game's image formats as the game's own compiler writes them.

One PNG gives a .frm16 (RLE with soft edges: alpha above 250 opaque, 6-250 edge pixels with their
opacity, 0-5 dropped; docs/FORMATS.md 5 "Encoder"); several PNGs with --seq give an image sequence
.seq16 (5.1). An output ending in .frm or .seq is the 8-bit file: its palette indices come from the game's
5-5-5 inverse colour table (frm.nearest_index8, read from the game data: --data or ZAX_DATA). The editor's
File → Import images writes both depths at once and also makes models (zaxtools/imageimport.py).

Examples:
    python tools/png_to_frm.py icon.png -o "out/Cache/Interface/Health Indicator Icon.frm16"
    python tools/png_to_frm.py icon.png -o "out/Cache/Interface/Health Indicator Icon.frm"     # 8 bit
    python tools/png_to_frm.py icon.png --hot 12,30 -o icon.frm16          # hot spot (anchor in models)
    python tools/png_to_frm.py f1.png f2.png f3.png --seq --fps 12 -o "out/Cache/Sequences/My Effect.seq16"
    python tools/png_to_frm.py w1.png w2.png --seq --raw --fps 12 -o "out/Cache/Animated Textures/My Water.seq16"

--raw writes uncompressed, opaque frames as textures need them (a surface's animated texture, Cache/Textures):
alpha dropped, the hot spot in the centre of a sequence's frames (0/0 for an image) and a sequence with the shipped
animated textures' load switches (zaxtools/imageimport.py).
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image

from _common import data_arg, open_data
from zaxtools import frm, imageimport, seq


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('png', nargs='+', type=Path)
    p.add_argument('-o', '--out', type=Path, required=True)
    p.add_argument('--hot', default='0,0', help='hot spot x,y in pixels from the top left (default 0,0)')
    p.add_argument('--seq', action='store_true', help='write an image sequence of all PNGs (.seq16 / .seq)')
    p.add_argument('--fps', type=float, default=30.0, help='with --seq: frames per second (default 30, the field default)')
    p.add_argument('--mode', default='Transparent Mask', help='with --seq: Blit Type (default "Transparent Mask")')
    p.add_argument('--raw', action='store_true', help='uncompressed and opaque, for textures (see above)')
    data_arg(p)
    a = p.parse_args()
    hot = tuple(int(v) for v in a.hot.split(','))
    if len(a.png) > 1 and not a.seq:
        p.error('several PNGs need --seq')
    eight = a.out.suffix.lower() in ('.frm', '.seq')
    inv = open_data(a).read(frm.INV_COLOR_TABLE15) if eight else None
    frames = []
    for path in a.png:
        rgba = np.asarray(Image.open(path).convert('RGBA'))
        if a.raw:
            h, w = rgba.shape[:2]
            rhot = (w // 2, h // 2) if a.seq else (0, 0)
            frames.append(frm.encode_raw(frm.nearest_index8(rgba[..., :3], inv) if eight
                                         else frm.rgb_to_pixel16(rgba[..., :3]), rhot))
        else:
            frames.append(frm.encode_rgba8(rgba, inv, hot) if eight else frm.encode_rgba16(rgba, hot))
        print(f'{path}: {rgba.shape[1]}x{rgba.shape[0]}, '
              f'{int((rgba[..., 3] > 250).sum())} opaque, {int(((rgba[..., 3] > 5) & (rgba[..., 3] <= 250)).sum())} edge pixels')
    flags = imageimport.TEXTURE_LOAD_FLAGS if a.raw else (0, 1, 1, 0, 0)
    data = seq.dumps(frames, a.fps, a.mode, flags) if a.seq else frames[0]
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_bytes(data)
    print(f'{a.out}: {len(data)} bytes')


if __name__ == '__main__':
    main()
