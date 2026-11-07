"""Image sequences (.seq = 256 colours, .seq16 = 16 bit) from Data/Cache: animated polygon textures
(``Cache/Animated Textures``, field ``Animated Texture`` of CRenderablePolygon), effects,
cursors, inventory.

A file is a single sequence object, built like the sequences in .mdl16 (zaxtools.mdl), but with
signature (27.0, 207.0) and without rotations:

    +0   f32 27.0, f32 207.0     signature
    +8   i32 0
    +12  u32 number of frames
    +16  f32 frames/s
    +20  u8  Center Hot Spot
    +21  u32 length + chars      Blit Type ("Transparent Mask", "Blend Black Bias")
    ...  4 x u8                  Blended With Black, Crop Clor 0, Use 8 Bit Alpha, Dither
    ...  2 x i32                 X Offset, Y Offset
    ...  4 x i32                 frame box x0, y0, x1, y1: the union of the frames' rectangles
Then one byte per frame: 01 + frame like .frm (zaxtools.frm), 00 = empty frame.
Raw frames (not RLE) have a row table (height x u32) after the pixels, like .frm.

The writer (dumps) follows Object_WriteBinary 0x416f50 (27.0, the class version 207.0, the fields of
CObject and CSequence in registration order: an i32 0, the frame count, then the named fields) and
CSequence::WriteBinary 0x56ba90 (the box, per frame 01 + CFrame::WriteFrm or 00 for a frame without
width or height) [confirmed: code; verified: all 352 files byte for byte, docs/FORMATS.md 5.1].

Fonts (Cache/Fonts, signature 654.0) are read by zaxtools.font.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field

import numpy as np

from . import frm
from .mdl import Frame

TAG = struct.pack('<ff', 27.0, 207.0)


EMPTY_BOX = (99999, 999999, -999999, -999999)     # the box's start values (CSequence::AddFrame 0x56bb70)


@dataclass
class SeqFile:
    total: int
    fps: float
    mode: str
    box: tuple[int, int, int, int]          # x0, y0, x1, y1
    frames: list[Frame | None] = field(default_factory=list)
    load_flags: tuple[int, int, int, int, int] = (0, 1, 1, 0, 0)   # Center Hot Spot, Blended With Black,
    #                                          Crop Clor 0, Use 8 Bit Alpha, Dither (field defaults 0x56ad20)
    offset: tuple[int, int] = (0, 0)        # X Offset, Y Offset
    fps_raw: float = 0.0                    # frames per second as stored (float32), for writing back

    def frame_at(self, seconds: float) -> Frame | None:
        """Frame at a point in time (looped playback)."""
        if not self.frames:
            return None
        return self.frames[int(seconds * self.fps) % len(self.frames)]


def load(data: bytes, palette: np.ndarray | None = None) -> SeqFile:
    """Read a file. For .seq (8 bit) pass ``palette`` (frm.load_palette)."""
    if data[:8] != TAG:
        raise ValueError('not an image sequence (signature 27/207)')
    _, total, fps = struct.unpack_from('<iIf', data, 8)
    ln = struct.unpack_from('<I', data, 21)[0]
    mode = data[25:25 + ln].decode('latin-1')
    o = 25 + ln
    flags = (data[20],) + struct.unpack_from('<4B', data, o)
    offset = struct.unpack_from('<2i', data, o + 4)
    o += 12
    box = struct.unpack_from('<4i', data, o)
    o += 16
    out = SeqFile(total, round(fps, 3), mode, box, load_flags=flags, offset=offset, fps_raw=fps)
    for _ in range(total):
        marker = data[o]
        o += 1
        if marker == 0:
            out.frames.append(None)
            continue
        if marker != 1:
            raise ValueError(f'unexpected frame marker {marker} at offset {o - 1}')
        rgba, hd, end = frm.decode(data, o, palette)
        out.frames.append(Frame(rgba, hd.hot_x, hd.hot_y, o))
        o = end if hd.rle or end == len(data) else end + 4 * hd.height
    if o != len(data):
        raise ValueError(f'{len(data) - o} bytes after the last frame')
    return out


def frame_box(frames: list[bytes | None]) -> tuple[int, int, int, int]:
    """The union of the frames' rectangles (origin = -hot spot, plus width/height) as CSequence::AddFrame
    0x56bb70 builds it; EMPTY_BOX without frames."""
    x0, y0, x1, y1 = EMPTY_BOX
    for d in frames:
        if d is None:
            continue
        hd = frm.read_header(d)
        x0, y0 = min(x0, -hd.hot_x), min(y0, -hd.hot_y)
        x1, y1 = max(x1, -hd.hot_x + hd.width), max(y1, -hd.hot_y + hd.height)
    return x0, y0, x1, y1


def dumps(frames: list[bytes | None], fps: float = 30.0, mode: str = 'Transparent Mask',
          load_flags: tuple[int, int, int, int, int] = (0, 1, 1, 0, 0), offset: tuple[int, int] = (0, 0),
          box: tuple[int, int, int, int] | None = None) -> bytes:
    """Write an image sequence: ``frames`` the encoded frames (frm.encode16/encode8/encode_raw) or None
    for an empty one; ``fps``, ``mode`` (Blit Type), ``load_flags`` and ``offset`` the CSequence fields
    (defaults = the exe's field defaults); ``box`` None = computed from the frames (frame_box)."""
    if box is None:
        box = frame_box(frames)
    m = mode.encode('latin-1')
    out = bytearray(TAG + struct.pack('<iIfB', 0, len(frames), fps, load_flags[0]))
    out += struct.pack('<I', len(m)) + m + struct.pack('<4B2i', *load_flags[1:], *offset)
    out += struct.pack('<4i', *box)
    for d in frames:
        hd = frm.read_header(d) if d is not None else None
        if hd is None or not (hd.width and hd.height):
            out.append(0)
        else:
            out.append(1)
            out += d
    return bytes(out)
