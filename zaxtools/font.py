"""Bitmap fonts (Cache/Fonts, .seq = 256 colours, .seq16 = 16 bit), class ``CFont``.

Built like an image sequence (zaxtools.seq), but with signature (27.0, 654.0) and one frame per
character. Fields according to Zax.exe: CSequence (Frames Per Second, Center Hot Spot, Blit Type,
4 x u8, X/Y Offset), then CFont (First ASCII, Last ASCII, Fixed Width):

    +0   f32 27.0, f32 654.0     signature
    +8   i32 0
    +12  u32 number of chars     = Last ASCII - First ASCII + 1
    +16  f32 frames/s            always 30
    +20  u8  Center Hot Spot     always 0
    +21  u32 length + chars      Blit Type ("Transparent Mask")
    ...  4 x u8, 2 x i32         Blended With Black, Crop Color 0, Use 8 Bit Alpha, Dither, X/Y Offset
    ...  i32                     unknown (5..25; often = glyph height, for "Small *" 8 at height 13)
    ...  i32, i32                First ASCII, Last ASCII
    ...  u8                      Fixed Width (only the Courier fonts)
    ...  4 x i32                 frame box x0, y0, x1, y1: largest width and height, y0 = -hot spot Y
Then one byte per character: 01 + frame (zaxtools.frm, RLE) or 00 (empty). The width of a frame is
the advance width of the character; all frames of a font have the same height.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field

import numpy as np

from . import frm
from .mdl import Frame

TAG = struct.pack('<ff', 27.0, 654.0)


@dataclass
class Font:
    first: int
    last: int
    fixed_width: bool
    box: tuple[int, int, int, int]          # x0, y0, x1, y1
    unknown: int                            # i32 before First ASCII, meaning unknown
    flags: bytes                            # Blended With Black, Crop Color 0, Use 8 Bit Alpha, Dither
    offset: tuple[int, int]                 # X/Y Offset
    glyphs: dict[int, Frame] = field(default_factory=dict)   # character code (Latin-1) -> frame

    @property
    def height(self) -> int:
        return self.box[3]

    def glyph(self, ch: str) -> Frame | None:
        return self.glyphs.get(ord(ch))

    def width(self, text: str) -> int:
        return sum(g.width for c in text if (g := self.glyph(c)) is not None)

    def render(self, text: str) -> np.ndarray:
        """One line of text as an RGBA image (height = font height). Missing characters are skipped."""
        out = np.zeros((self.height, max(self.width(text), 1), 4), np.uint8)
        x = 0
        for c in text:
            g = self.glyph(c)
            if g is None:
                continue
            h = min(g.height, self.height)
            src = g.rgba[:h]
            dst = out[:h, x:x + g.width]
            a = src[..., 3:4].astype(np.uint16)
            dst[..., :3] = (src[..., :3] * a + dst[..., :3] * (255 - a)) // 255
            dst[..., 3] = np.maximum(dst[..., 3], src[..., 3])
            x += g.width
        return out


def load(data: bytes, palette: np.ndarray | None = None) -> Font:
    """Read a font. For .seq (8 bit) pass ``palette`` (frm.load_palette)."""
    if data[:8] != TAG:
        raise ValueError('not a font (signature 27/654)')
    total = struct.unpack_from('<I', data, 12)[0]
    ln = struct.unpack_from('<I', data, 21)[0]
    o = 25 + ln
    flags = data[o:o + 4]
    offset = struct.unpack_from('<ii', data, o + 4)
    unknown, first, last = struct.unpack_from('<iii', data, o + 12)
    fixed = data[o + 24]
    box = struct.unpack_from('<4i', data, o + 25)
    o += 41
    if last - first + 1 != total:
        raise ValueError(f'character range {first}..{last} does not match {total} frames')
    out = Font(first, last, bool(fixed), box, unknown, flags, offset)
    for i in range(total):
        marker = data[o]
        o += 1
        if marker == 0:
            continue
        if marker != 1:
            raise ValueError(f'unexpected frame marker {marker} at offset {o - 1}')
        rgba, hd, end = frm.decode(data, o, palette)
        out.glyphs[first + i] = Frame(rgba, hd.hot_x, hd.hot_y, o)
        o = end if hd.rle or end == len(data) else end + 4 * hd.height
    if o != len(data):
        raise ValueError(f'{len(data) - o} bytes after the last character')
    return out
