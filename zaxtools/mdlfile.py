"""Write models (.mdl16 / .mdl) as the game writes them: the CModel header, the sequence list and every
CRotationSequence with its frames.

File layout [confirmed: code Object_WriteBinary 0x416f50, CModel::WriteOwn 0x517160 / ReadOwn 0x516ff0,
CRotationSequence::RegisterFields 0x55ed20, CSequence::WriteBinary 0x56ba90, CRotationSequence slot 13 0x55f980;
zax-decomp/reimpl/src/models.cpp, sequence_classes.cpp, sequence_load.cpp; verified: ``parse`` + ``dumps`` give every
.mdl16 and .mdl of the German edition back byte for byte (self-test section 4c)]:

    CModel object        f32 27.0, f32 403.0 (the class signature of all 1,119 models), u32 0 dynamic properties,
                         the fields (zaxtools.modelhead; ``dumps_head`` writes the simple form below)
    u32                  number of sequences
    u32 + text           path "Models/<folder>/-<name>"
    per sequence         u8 1 (present), u32 + name, u8 0 (the name's terminator), then the CRotationSequence:
      f32 27.0, f32 758.0, i32 0 (CObject's field), u32 frames, f32 Frames Per Second, u8 Center Hot Spot,
      u32 + Blit Type, u8 Blended With Black, u8 Crop Clor 0, u8 Use 8 Bit Alpha, u8 Dither, i32 X Offset,
      i32 Y Offset, i32 Num Rotations, i32 Editor Display Offset, u32 frames per rotation (unnamed +0x48),
      6 x u8 Render On Ground, Is Shadow, Auto-Animate, Sync The Auto Animation, Editor Only, Always Visible,
      i32 the unnamed +0x50 (default -1), f32 Rotational Offset, f32 Rotational Range, i32 Sorting Y Offset,
      u32 + n x CVerticalCut (27.0, 36.0, i32 0, i32 Cut Offset, i32 Strip Sorting Y Offset), u32 + n x
      CAnimationTrigger (kept as bytes here), 4 x i32 frame box, per frame u8 1 + frame (zaxtools.frm) or u8 0,
      8 bytes "Frame Delta" per frame.

``dumps_head`` writes only the CModel form of the decoration models: no dynamic properties, an empty
``Activity``, no ``Default Entity``, no ``Fidget Settings`` (626 of the 1,119 headers; ``dumps_head`` gives
each of them back byte for byte). That is all a new model made from own images gets (``new_head``).
"""
from __future__ import annotations

import math
import struct
from dataclasses import dataclass, field

from . import frm, seq

MODEL_SIG = 403.0
SEQ_SIG = 758.0
CUT_SIG = 36.0
TWO_PI_F32 = struct.unpack('<f', struct.pack('<f', 2 * math.pi))[0]


@dataclass
class SeqRecord:
    """One CRotationSequence as stored (all fields; frames as encoded bytes, None = empty frame)."""
    name: str
    frames: list[bytes | None]
    fps: float = 30.0
    center: int = 1
    mode: str = 'Transparent Mask'
    load_flags: tuple[int, int, int, int] = (1, 1, 0, 0)     # Blended With Black, Crop Clor 0, Use 8 Bit Alpha, Dither
    offset: tuple[int, int] = (0, 0)                          # X Offset, Y Offset
    rotations: int = 1
    editor_display_offset: int = -100
    switches: tuple[int, int, int, int, int, int] = (0, 0, 0, 0, 0, 0)
    ref50: int = -1                     # the unnamed field +0x50 (default -1)
    rot_offset: float = 0.0
    rot_range: float = TWO_PI_F32
    sort_offset: int = 0
    cuts: list[tuple[int, int]] = field(default_factory=list)
    triggers: bytes = b'\0\0\0\0'       # u32 count + the CAnimationTrigger objects, as stored
    box: tuple[int, int, int, int] | None = None              # None = computed from the frames (seq.frame_box)
    deltas: bytes | None = None         # 8 bytes per frame; None = zeros
    present: int = 1

    @property
    def per_rotation(self) -> int:
        return len(self.frames) // max(1, self.rotations)


@dataclass
class ModelFile:
    head: bytes                         # the CModel object
    path: str                           # "Models/<folder>/-<name>"
    sequences: list[SeqRecord]


def _str(s: str) -> bytes:
    b = s.encode('latin-1')
    return struct.pack('<I', len(b)) + b


def model_path(model: str) -> str:
    """The path a model stores for itself: "Models/<folder>/-<name>" (as every shipped model)."""
    folder, _, name = model.rpartition('/')
    return f'Models/{folder}/-{name}' if folder else f'Models/-{name}'


def dumps_sequence(s: SeqRecord) -> bytes:
    n = len(s.frames)
    out = bytearray(struct.pack('<B', s.present))
    if not s.present:
        return bytes(out)
    out += _str(s.name) + b'\0'
    out += struct.pack('<ffiIfB', 27.0, SEQ_SIG, 0, n, s.fps, s.center) + _str(s.mode)
    out += struct.pack('<4B2i', *s.load_flags, *s.offset)
    out += struct.pack('<iiI', s.rotations, s.editor_display_offset, s.per_rotation)
    out += struct.pack('<6B', *s.switches)
    out += struct.pack('<iffiI', s.ref50, s.rot_offset, s.rot_range, s.sort_offset, len(s.cuts))
    for c, o in s.cuts:
        out += struct.pack('<ffiii', 27.0, CUT_SIG, 0, c, o)
    out += s.triggers
    out += struct.pack('<4i', *(s.box if s.box is not None else seq.frame_box(s.frames)))
    for d in s.frames:
        hd = frm.read_header(d) if d is not None else None
        if hd is None or not (hd.width and hd.height):
            out.append(0)
        else:
            out.append(1)
            out += d
    out += s.deltas if s.deltas is not None else bytes(8 * n)
    return bytes(out)


def dumps(m: ModelFile) -> bytes:
    out = bytearray(m.head)
    out += struct.pack('<I', len(m.sequences)) + _str(m.path)
    for s in m.sequences:
        out += dumps_sequence(s)
    return bytes(out)


# --- Reading (for the round trip and for replacing frames in a copy) --------------------------------------------
class _R:
    def __init__(self, d: bytes, o: int):
        self.d, self.o = d, o

    def take(self, fmt: str):
        v = struct.unpack_from(fmt, self.d, self.o)
        self.o += struct.calcsize(fmt)
        return v

    def text(self) -> str:
        (n,) = self.take('<I')
        s = self.d[self.o:self.o + n].decode('latin-1')
        self.o += n
        return s


def parse(data: bytes, head) -> ModelFile:
    """Every part of a model file; ``head`` a ``modelhead.ModelHead`` (the exe's schema: it finds the header's end
    and reads the frame triggers). Raises ValueError for a file that does not end where its parts do."""
    _, end = head.decode_end(data)
    r = _R(data, end)
    (count,) = r.take('<I')
    path = r.text()
    seqs = []
    for _ in range(count):
        (present,) = r.take('<B')
        if not present:
            seqs.append(SeqRecord('', [], present=0))
            continue
        name = r.text()
        r.take('<B')
        sig, csig, zero, n, fps, center = r.take('<ffiIfB')
        if (sig, csig, zero) != (27.0, SEQ_SIG, 0):
            raise ValueError(f'sequence {name!r}: signature {sig}/{csig}/{zero}')
        mode = r.text()
        flags = r.take('<4B')
        offset = r.take('<2i')
        rots, edo, _per = r.take('<iiI')
        switches = r.take('<6B')
        ref50, ro, rr, so, ncut = r.take('<iffiI')
        cuts = []
        for _ in range(ncut):
            cs, cg, cz, c, o = r.take('<ffiii')
            cuts.append((c, o))
        t0 = r.o
        (ntrig,) = r.take('<I')
        for _ in range(ntrig):
            _, r.o = head.decode_object(data, r.o, 'CAnimationTrigger')
        triggers = data[t0:r.o]
        box = r.take('<4i')
        frames = []
        for _ in range(n):
            (has,) = r.take('<B')
            if not has:
                frames.append(None)
                continue
            e = frm.frame_end(data, r.o)
            frames.append(data[r.o:e])
            r.o = e
        deltas = data[r.o:r.o + 8 * n]
        r.o += 8 * n
        seqs.append(SeqRecord(name, frames, fps, center, mode, flags, offset, rots, edo, switches, ref50, ro, rr, so,
                              cuts, triggers, box, deltas))
    if r.o != len(data):
        raise ValueError(f'{len(data) - r.o} bytes after the last sequence')
    return ModelFile(data[:end], path, seqs)


# --- The header of a new model --------------------------------------------------------------------------------
# Values of the simple headers (626 of the 1,119 models: decoration without default object): the most frequent
# value of each field there [verified: counted 2026-10-29], which for the numbers is also the exe's field default.
HEAD_DEFAULTS = {
    'Printable Name': '', 'Description': '', 'Hit Points': 0.0, 'Collide Damage': 0.0, 'Collide Damage Type': '!None',
    'Closing Damage': 10.0, 'Explosion Radial Damage': 0.0, 'Sorting Y': 0, 'Default Sequence': 'Idle',
    'Activate Sound': 'Error.wav', 'Close Sound': 'Error.wav', 'Explosion': '!Unknown Model', 'Death Sound': 'Error.wav',
    'Pain Sound': 'Error.wav', 'Surface Type': '!None', 'Max Velocity': 500.0, 'Turn Speed': 180.0,
    'Bounce Factor': 1.0, 'Min Bounce': 0.1, 'Bounce Friction': 0.0, 'Min Bounce Friction': 0.1, 'Bounds Poly': [],
    'Also Render': '!Unknown Model',
}


def dumps_head(values: dict, schema) -> bytes:
    """The CModel object of the simple form (see the module text) from its field values (``modelhead.Obj.values``
    or ``new_head``); ``schema`` the exe's (field order and kinds). ValueError for a value the form cannot hold."""
    out = bytearray(struct.pack('<ffI', 27.0, MODEL_SIG, 0))
    for f in schema.fields('CModel'):
        nm, e = f['name'], f['enc']
        v = values.get(nm)
        if e == 'str':
            out += _str(v or '')
        elif e == 'f4':
            out += struct.pack('<f', float(v or 0.0))
        elif e == 'i4':
            out += struct.pack('<i', int(v or 0))
        elif e == 'arr':
            if v:
                raise ValueError(f'{nm}: only an empty array')
            out += struct.pack('<I', 0)
        elif e == 'ptr':
            if v is not None:
                raise ValueError(f'{nm}: only an empty pointer')
            out += _str('')
        elif e == 'poly':
            pts = v or []
            out += b'POLY2D\0\x07' + struct.pack('<I', len(pts))     # the header's byte 7 (0x5482a0)
            for x, y in pts:
                out += struct.pack('<ff', x, y)
        else:
            raise ValueError(f'{nm}: field kind {e} not supported')
    return bytes(out)


def new_head(name: str, sequence: str, schema, sorting_y: int = 0) -> bytes:
    """The header of a new decoration model: ``HEAD_DEFAULTS`` with ``Legacy Name`` = the model's name,
    ``Default Sequence`` = its sequence and ``Sorting Y``."""
    values = dict(HEAD_DEFAULTS, **{'Legacy Name': name, 'Default Sequence': sequence, 'Sorting Y': sorting_y})
    return dumps_head(values, schema)
