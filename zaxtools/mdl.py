"""Models (.mdl = 256 colours, .mdl16 = 16 bit) from Data/Cache/Models.

A .mdl16 is a binary serialised object tree. Objects start with the signature ``float 27.0`` +
``float type number``; strings are u32 length + characters. Known parts (see docs/FORMATS.md):

1. Template object: model name and default entity (e.g. CEntityFlying with CSkeletonAI ...)
   that the editor creates when placing. Binary, not fully decoded yet.
2. Sequences, signature (27.0, 758.0):
       name (u32 length + chars), 1 byte, signature, i32 0, u32 total frames,
       f32 frames/s, 1 byte, string render mode, 12 bytes,
       i32 Num Rotations, i32 Editor Display Offset (always -100), u32 frames per rotation,
       6 x u8 (Render On Ground, Is Shadow, ...), i32, f32 Rotational Offset,
       f32 Rotational Range, i32 Sorting Y Offset, u32 number of Cutting Lines +
       per cut a CVerticalCut (signature 27.0/36.0, i32 0, i32 Cut Offset,
       i32 Strip Sorting Y Offset), ...
   Frames are ordered by rotation (rotation 0: frame 0..n-1, rotation 1, ...).
   One byte per frame: 01 + frame, 00 = empty frame (like .seq, zaxtools.seq).
   Then 8 bytes "Frame Delta" per frame, a byte 01 before the next sequence.
   Between header and frames there can be objects (actions per frame: sound, message ...) that
   are not read here; the frame area is therefore determined from the end (Frame Delta).
   138 sequences in 99 models have empty frames.
3. Frames: format like .frm16 (zaxtools.frm), with hot spot and alpha/edge layer.

Layers: an object shows its active sequence (``Cur Sequence`` in the .zax) and all sequences
"<active> <suffix>": "... Shadow" (first), "... Ground/Floor" (ground), "... Ship"/"... Glow"/
"... Ramp" etc. (on top). Plus sequences with the switch "Always Visible" (always); the game does
not draw sequences with "Editor Only" (handles "handle"/"Tool"). The 6 switches per sequence:
Render On Ground, Is Shadow, Auto-Animate, Sync The Auto Animation, Editor Only, Always Visible
(order of the field registration in Zax.exe).
"""
from __future__ import annotations

import math
import re
import struct
from dataclasses import dataclass, field

import numpy as np

from . import frm

SEQ_TAG = struct.pack('<ff', 27.0, 758.0)
TWO_PI = struct.unpack('<f', struct.pack('<f', 2 * math.pi))[0]    # constant of the exe (float)
_FRAME_RE = re.compile(rb'\x31(\x10|\x08)')


@dataclass
class Frame:
    rgba: np.ndarray
    hot_x: int
    hot_y: int
    offset: int
    data: bytes | None = field(default=None, repr=False, compare=False)   # model file (16 bit), for layers16
    _layers: object = field(default=None, repr=False, compare=False)

    def layers16(self) -> frm.Layers16 | None:
        """Pixel and edge block as the game draws them (frm.layers16), decoded on first use; None
        for 8-bit frames."""
        if self._layers is None and self.data is not None:
            self._layers = frm.layers16(self.data, self.offset)
        return self._layers

    @property
    def width(self) -> int:
        return self.rgba.shape[1]

    @property
    def height(self) -> int:
        return self.rgba.shape[0]


@dataclass
class Sequence:
    name: str
    total: int
    fps: float
    mode: str               # "Transparent Mask", "Blend Black Bias", "Blend Amplify Light"
    rotations: int
    frames_per_rotation: int
    sort_y: int             # Editor Display Offset (always -100), not the model's "Sorting Y"
    offset: int
    rot_offset: float = 0.0             # Rotational Offset (radians)
    rot_range: float = 2 * math.pi      # Rotational Range
    flags: bytes = bytes(6)     # Render On Ground, Is Shadow, Auto-Animate, Sync, Editor Only, Always Visible
    sort_offset: int = 0        # "Sorting Y Offset": sorting offset of the layer (strip 0)
    cuts: list[tuple[int, int]] = field(default_factory=list)   # (Cut Offset, Strip Sorting Y Offset)
    frames: list[Frame | None] = field(default_factory=list)   # one slot per frame, None = empty
    exact: bool = True      # False: slots cannot be determined, only the first frame as a still image

    @property
    def stored(self) -> list[Frame]:
        """Only the stored (non-empty) frames."""
        return [f for f in self.frames if f is not None]

    def frame(self, rotation: int = 0, index: int = 0) -> Frame | None:
        """Frame for rotation and animation index (None if empty)."""
        k = rotation * self.frames_per_rotation + index
        return self.frames[k] if 0 <= k < len(self.frames) else None

    @property
    def on_ground(self) -> bool:
        return bool(self.flags[0])

    @property
    def is_shadow(self) -> bool:
        return bool(self.flags[1])

    @property
    def auto_animate(self) -> bool:
        """"Auto-Animate" (bit 0x80): the frame comes from the game time (zaxtools.anim)."""
        return bool(self.flags[2])

    @property
    def sync_auto(self) -> bool:
        """"Sync The Auto Animation" (bit 0x100): without the object's offset (zaxtools.anim)."""
        return bool(self.flags[3])

    @property
    def editor_only(self) -> bool:
        """Only visible in the editor (handles "Handle"/"Tool", editor models) [confirmed: all 29]."""
        return bool(self.flags[4])

    @property
    def always_visible(self) -> bool:
        """Drawn regardless of the active sequence (ground light of the light beams, pedestals)
        [verified 2026-10-20 in the game: Light Beam 1 "Floor Light"]."""
        return bool(self.flags[5])

    def strips(self) -> list[tuple[int, float, float]]:
        """Vertical strips of the layer: (sorting offset, x from, x to), x relative to the object
        position. Like Zax.exe (0x560270, 0x55fc50): strip 0 lies left of the first cut and has
        the sequence's "Sorting Y Offset", strip k lies between cut k-1 and k and has the
        "Strip Sorting Y Offset" of cut k-1 (replaced, not added). Without cuts one strip
        across the whole image."""
        xs = [-math.inf] + [c for c, _ in self.cuts] + [math.inf]
        offs = [self.sort_offset] + [s for _, s in self.cuts]
        return [(offs[k], xs[k], xs[k + 1]) for k in range(len(offs))]

    def rotation(self, angle: float) -> int:
        """Rotation index for a facing angle, see ``rotation_index``."""
        return rotation_index(angle, self.rotations, self.rot_offset, self.rot_range)

    def still(self, rotation: int = 0) -> Frame | None:
        """Still image of a rotation: first non-empty frame (effects often start empty), otherwise
        that of rotation 0; None if the sequence is completely empty. For thumbnails; the frame the
        game shows in a level comes from zaxtools.anim."""
        for r in (rotation, 0):
            for i in range(self.frames_per_rotation):
                if (f := self.frame(r, i)) is not None:
                    return f
        return None


@dataclass
class Model:
    name: str
    sequences: list[Sequence]

    def sequence(self, name: str) -> Sequence | None:
        low = name.lower()
        return next((s for s in self.sequences if s.name.lower() == low), None)

    def layers(self, current: str | None):
        """Sequences drawn for the active sequence, with their order: 0 shadow, 1 ground/light on
        the ground, 2 base sequence, 3 attachments. Plus all sequences with "Always Visible"
        (order by "Is Shadow"/"Render On Ground"); the game does not draw "Editor Only" layers
        (handles)."""
        names = [s.name.lower() for s in self.sequences]
        base = (current or '').lower()
        if base not in names:
            base = 'idle' if 'idle' in names else (names[0] if names else '')
        out = []
        for s in self.sequences:
            n = s.name.lower()
            if n == base:
                order = 2
            elif s.editor_only:
                continue
            elif n.startswith(base + ' '):
                suf = n[len(base) + 1:]
                order = 0 if 'shadow' in suf else 1 if ('ground' in suf or 'floor' in suf) else 3
            elif s.always_visible:
                order = 0 if s.is_shadow else 1 if s.on_ground else 3
            else:
                continue
            out.append((order, s))
        out.sort(key=lambda t: t[0])
        return out


def rotation_index(angle: float, rotations: int, offset: float = 0.0, rng: float = 2 * math.pi) -> int:
    """Rotation index for an angle in radians (``Start FacingAngle`` in the .zax).

    Like Zax.exe 0x55fdd0 (CRotationSequence): bring the angle into [offset, offset+rng]
    (0x5096a0), subtract offset, bring it to [0, 2*pi), then round(angle * rotations / rng); a
    result >= rotations becomes 0 for a full circle, otherwise the last rotation. Rounding as
    the FPU does (to even).
    """
    if rotations <= 1:
        return 0
    lo, hi = _f32(offset), _f32(offset + rng)
    a = _f32(angle)                     # the exe stores angles as float
    if a < lo:
        a += TWO_PI
        if a < lo or a >= hi:
            a = lo
    if a > hi:
        a -= TWO_PI
        if a < lo or a >= hi:
            a = hi
    a -= offset
    if a < 0:
        a += TWO_PI
    if a >= TWO_PI:
        a -= TWO_PI
    i = round(a * rotations / rng)
    if i >= rotations:
        return i - rotations if abs(rng - TWO_PI) < 0.01 else rotations - 1
    return i


def _f32(x: float) -> float:
    return struct.unpack('<f', struct.pack('<f', x))[0]


def _seq_name(d: bytes, o: int) -> str:
    for ln in range(1, 80):
        s = o - 1 - ln
        if s >= 4 and struct.unpack_from('<I', d, s - 4)[0] == ln and all(32 <= c < 127 for c in d[s:o - 1]):
            return d[s:o - 1].decode('latin-1')
    return ''


def read_sequences(d: bytes) -> list[Sequence]:
    out = []
    for m in re.finditer(re.escape(SEQ_TAG), d):
        o = m.start()
        _, total = struct.unpack_from('<iI', d, o + 8)
        fps = struct.unpack_from('<f', d, o + 16)[0]
        sl = struct.unpack_from('<I', d, o + 21)[0]
        mode = d[o + 25:o + 25 + sl].decode('latin-1')
        rot, sort_y, per = struct.unpack_from('<IiI', d, o + 25 + sl + 12)
        flags = d[o + 25 + sl + 24:o + 25 + sl + 30]
        r_off, r_rng, sort_off, n = struct.unpack_from('<ffiI', d, o + 25 + sl + 34)
        cuts, p = [], o + 25 + sl + 50
        for _ in range(n if n < 64 else 0):
            if struct.unpack_from('<ffi', d, p) != (27.0, 36.0, 0):   # CVerticalCut
                cuts = []
                break
            cuts.append(struct.unpack_from('<ii', d, p + 12))
            p += 20
        out.append(Sequence(_seq_name(d, o), total, round(fps, 3), mode, rot, per, sort_y, o, r_off, r_rng,
                            flags=flags, sort_offset=sort_off, cuts=cuts))
    return out


def _try_frame(d: bytes, o: int, palette):
    try:
        hd = frm.read_header(d, o)
    except (ValueError, struct.error):
        return None
    if hd.bpp not in (8, 16) or not (0 < hd.width <= 2048 and 0 < hd.height <= 2048):
        return None
    if hd.flags not in (0x20, 0x40, 0x2022, 0x2044):
        return None
    if hd.bpp == 8 and palette is None:
        return None
    try:
        rgba, hd, end = frm.decode(d, o, palette)
    except (ValueError, struct.error, IndexError):
        return None
    return Frame(rgba, hd.hot_x, hd.hot_y, o, d if hd.bpp == 16 else None), end


def load(data: bytes, name: str = '', palette: np.ndarray | None = None) -> Model:
    """Load a model. For .mdl (8 bit) pass ``palette`` (frm.load_palette)."""
    seqs = read_sequences(data)
    frames, ends = [], {}
    pos = 0
    for m in _FRAME_RE.finditer(data):
        if m.start() < pos:
            continue
        r = _try_frame(data, m.start(), palette)
        if r:
            frames.append(r[0])
            pos = ends[r[0].offset] = r[1]
    bounds = [s.offset for s in seqs] + [len(data)]
    for k, s in enumerate(seqs):
        found = [f for f in frames if bounds[k] < f.offset < bounds[k + 1]]
        if k + 1 < len(seqs):       # name of the next sequence and the byte 01 before it
            n = seqs[k + 1]
            stop = n.offset - 1 - len(n.name.encode('latin-1')) - 4 - 1
        else:
            stop = len(data)
        s.frames, s.exact = _slots(data, s.total, found, [ends[f.offset] for f in found], stop - 8 * s.total)
    return Model(name, seqs)


def _slots(d: bytes, total: int, found: list[Frame], ends: list[int], end: int) -> tuple[list[Frame | None], bool]:
    """Distribute the frames found onto their slots: every byte 00 in the frame area (before,
    between, after the frames; ``end`` = end of the area) is an empty frame. If that does not
    fit (never in the originals), only the first frame as a still image."""
    if not found:
        return [None] * total, True
    out: list[Frame | None] = []
    gaps = [d[a:f.offset - 1] for a, f in zip(ends, found[1:])] + [d[ends[-1]:end]]
    lead = total - len(found) - sum(len(g) for g in gaps)
    if lead < 0 or any(g.strip(b'\0') for g in gaps) or d[found[0].offset - 1 - lead:found[0].offset - 1].strip(b'\0'):
        return [found[0]] + [None] * (total - 1), False
    out += [None] * lead
    for f, g in zip(found, gaps):
        out += [f] + [None] * len(g)
    return out, True
