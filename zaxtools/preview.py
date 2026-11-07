"""Models, image sequences, fonts and single images as the game draws them, for the viewer (zaxeditor.viewer).

Everything is one ``Viewable``: a model's sequences, or one sequence made from a ``.seq``/``.seq16``, a font's
glyphs or a single ``.frm``/``.frm16``. Drawing follows the renderer (zaxtools.render, docs/FORMATS.md 6):

- the layers of the active sequence as the game picks them (``mdl.Model.layers``: the base sequence, its
  ``<active> Shadow/Ground/Glow …`` layers, the ``Always Visible`` ones); ``layer_list`` also returns the
  ``Editor Only`` layers (handles), which the game never draws [confirmed: code 0x517410], switched off;
- two queues, the ``Render On Ground`` layers first, each sorted by the model's ``Sorting Y`` + the strip's
  offset, then the layer number (``0x4886a0``, ``0x4e7c00``); every layer split into its vertical strips
  (``Cutting Lines``, ``mdl.Sequence.strips``); a shadow layer drawn as ``Transparent Mask``;
- the frame a layer shows from the entity's frame index (``anim.layer_frame``: one frame per rotation shows
  frame 0, an index past the layer's frames draws nothing, ``Auto-Animate`` layers follow the game time);
  the viewer plays the active sequence like ``CPlaySequenceLoopedAI`` at its frames per second
  (``anim.entity_frame``);
- 16-bit frames with the exe's integer arithmetic on RGB565 (``render._blit``: copy, the MMX and scalar
  edge blends, Amplify Light tables), drawn as an object that changes every frame (no 64-pixel clip
  columns); 8-bit frames blended in float (the 256-colour mode's tables, which take the nearest palette
  entry of every blend, are not ported). An 8-bit frame's five blocks are drawn as the game's five opacity
  steps 1, 0.8, 0.6, 0.4, 0.2 (``frm.decode``, ``frm.OPACITY8``, docs/FORMATS.md 5).

Plus the sequence's fields as a text node for the property view, the frame triggers (``CAnimationTrigger``,
e.g. the sounds of footsteps), sprite sheets and writing a sequence back through the game's encoder.
"""
from __future__ import annotations

import math
import struct
from dataclasses import dataclass, field
from functools import partial

import numpy as np
from PIL import Image, ImageDraw

from . import anim, frm, mdl, render, seq
from . import font as fontmod
from . import textformat as tf

KINDS = ('model', 'sequence', 'frame', 'font')
EXTENSIONS = {'model': ('.mdl16', '.mdl'), 'sequence': ('.seq16', '.seq'), 'font': ('.seq16', '.seq'),
              'frame': ('.frm16', '.frm')}           # (16 bit, 8 bit)
MODEL_DIR = 'Cache/Models/'
FONT_DIR = 'Cache/Fonts/'
PALETTE = 'Palettes/GamePalette.pal'
SOUND_DIR = 'Sounds/'
AUDIO = ('.wav', '.ogg')
SWITCHES = ('Render On Ground', 'Is Shadow', 'Auto-Animate', 'Sync The Auto Animation', 'Editor Only',
            'Always Visible')                       # mdl.Sequence.flags, order of the field registration
LOAD_FLAGS = ('Blended With Black', 'Crop Clor 0', 'Use 8 Bit Alpha', 'Dither')   # spelling of the exe
SHADOW_MODE = 'Transparent Mask'


# ---- Listing and loading ---------------------------------------------------------------------------------

@dataclass
class Item:
    """One thing to look at: ``key`` the data path without extension (``Cache/Models/Characters/Om``)."""
    kind: str
    key: str
    depths: tuple[int, ...]             # available colour depths, 16 first

    @property
    def name(self) -> str:
        """Model name as in the levels; other files relative to ``Cache/``."""
        if self.kind == 'model':
            return self.key[len(MODEL_DIR):]
        return self.key[len('Cache/'):] if self.key.startswith('Cache/') else self.key

    def rel(self, bpp: int) -> str:
        return self.key + EXTENSIONS[self.kind][0 if bpp == 16 else 1]


def kind_of(rel: str) -> str | None:
    low = rel.lower()
    if low.endswith(('.mdl16', '.mdl')):
        return 'model'
    if low.endswith(('.seq16', '.seq')):
        return 'font' if low.startswith(FONT_DIR.lower()) else 'sequence'
    if low.endswith(('.frm16', '.frm')):
        return 'frame'
    return None


def list_items(ds) -> list[Item]:
    """Every model, image sequence, font and image of the game data, sorted by kind and path."""
    found: dict[tuple[str, str], set[int]] = {}
    for rel in ds.list('Cache/'):
        kind = kind_of(rel)
        if kind is None:
            continue
        stem, ext = rel.rsplit('.', 1)
        found.setdefault((kind, stem), set()).add(16 if ext.endswith('16') else 8)
    return [Item(k, s, tuple(sorted(d, reverse=True)))
            for (k, s), d in sorted(found.items(), key=lambda kv: (KINDS.index(kv[0][0]), kv[0][1].lower()))]


@dataclass
class Viewable:
    kind: str
    name: str
    bpp: int
    data: bytes                         # the file; frames point into it (mdl.Frame.offset)
    model: mdl.Model                    # a sequence, font or image: one sequence
    seqfile: seq.SeqFile | None = None
    font: fontmod.Font | None = None

    def sequence_fields(self, s: mdl.Sequence) -> tuple[int, tuple[int, ...], tuple[int, int]]:
        """CSequence's Center Hot Spot, the four load switches and X/Y Offset of a sequence."""
        if self.kind == 'frame':
            return 0, (0, 1, 1, 0), (0, 0)
        o = s.offset
        sl = struct.unpack_from('<I', self.data, o + 21)[0]
        return (self.data[o + 20], tuple(self.data[o + 25 + sl:o + 29 + sl]),
                struct.unpack_from('<2i', self.data, o + 29 + sl))


def palette(ds) -> np.ndarray:
    return frm.load_palette(ds.read(PALETTE))


def load(data: bytes, kind: str, name: str, pal: np.ndarray | None = None) -> Viewable:
    """Read a file of ``kind``; 8-bit files need the palette (``palette``)."""
    if kind == 'model':
        m = mdl.load(data, name, pal)
        bpp = next((data[f.offset + 1] for s in m.sequences for f in s.stored), 16)
        return Viewable(kind, name, bpp, data, m)
    if kind == 'frame':
        rgba, hd, _ = frm.decode(data, 0, pal)
        f = mdl.Frame(rgba, hd.hot_x, hd.hot_y, 0, data if hd.bpp == 16 else None)
        s = mdl.Sequence(_stem(name), 1, 0.0, 'Transparent Mask', 1, 1, 0, 0, frames=[f])
        return Viewable(kind, name, hd.bpp, data, mdl.Model(name, [s]))
    if kind == 'font':
        fn = fontmod.load(data, pal)
        frames = [fn.glyphs.get(c) for c in range(fn.first, fn.last + 1)]
        fps = struct.unpack_from('<f', data, 16)[0]
        mode = data[25:25 + struct.unpack_from('<I', data, 21)[0]].decode('latin-1')
        s = mdl.Sequence(_stem(name), len(frames), round(fps, 3), mode, 1, len(frames), 0, 0, frames=frames)
        v = Viewable(kind, name, 16, data, mdl.Model(name, [s]), font=fn)
    else:
        sf = seq.load(data, pal)
        s = mdl.Sequence(_stem(name), sf.total, sf.fps, sf.mode, 1, sf.total, 0, 0, frames=sf.frames)
        v = Viewable(kind, name, 16, data, mdl.Model(name, [s]), seqfile=sf)
    stored = [f for f in s.frames if f is not None]
    v.bpp = data[stored[0].offset + 1] if stored else 16
    if v.bpp == 16:
        for f in stored:
            f.data = data                       # for frm.layers16 (the exact 16-bit drawing)
    return v


def _stem(name: str) -> str:
    return name.rsplit('/', 1)[-1]


# ---- Layers and drawing --------------------------------------------------------------------------------

@dataclass
class Layer:
    order: int                          # 0 shadow, 1 ground, 2 the base sequence, 3 on top (mdl.Model.layers)
    seq: mdl.Sequence
    number: int                         # the layer's number in the game's sort key (its index in Model.layers)
    on: bool = True
    editor_only: bool = False           # a handle: the game never draws it


def base_name(model: mdl.Model, current: str | None) -> str:
    """The base sequence ``Model.layers`` resolves ``current`` to (lower case)."""
    names = [s.name.lower() for s in model.sequences]
    base = (current or '').lower()
    if base not in names:
        base = 'idle' if 'idle' in names else (names[0] if names else '')
    return base


def layer_list(model: mdl.Model, current: str | None) -> list[Layer]:
    """The layers of the active sequence: those the game draws (``Model.layers``, in its order, switched on)
    and the ``Editor Only`` ones it would pick by name or ``Always Visible`` (switched off)."""
    game = model.layers(current)
    out = [Layer(order, s, i) for i, (order, s) in enumerate(game)]
    drawn = {id(s) for _, s in game}
    base = base_name(model, current)
    extra = []
    for s in model.sequences:
        n = s.name.lower()
        if id(s) in drawn or not s.editor_only:
            continue
        if n.startswith(base + ' '):
            suf = n[len(base) + 1:]
            order = 0 if 'shadow' in suf else 1 if ('ground' in suf or 'floor' in suf) else 3
        elif s.always_visible:
            order = 0 if s.is_shadow else 1 if s.on_ground else 3
        else:
            continue
        extra.append(Layer(order, s, len(game) + len(extra), False, True))
    out = sorted(out + extra, key=lambda lay: lay.order)
    for lay in out:
        if lay.order == 2 and lay.seq.editor_only:
            lay.editor_only = True              # an editor model: its base sequence is a handle too
    return out


def base_layer(layers: list[Layer]) -> Layer | None:
    return next((lay for lay in layers if lay.order == 2), None)


def entity_anim(playing: bool) -> anim.PartAnim:
    """The viewer's object: a CEntityAnimated whose sequence plays in a loop (``CPlaySequenceLoopedAI``)
    while ``playing``; paused, it rests at the chosen frame."""
    return anim.PartAnim(True, None, loop=anim.Loop('') if playing else None)


def entity_index(base: mdl.Sequence | None, t: float) -> int:
    """The frame index of the playing object ``t`` seconds after the start (anim.frame_index)."""
    return anim.frame_index(entity_anim(True), base, t)


@dataclass
class Drawn:
    layer: Layer
    frame: mdl.Frame
    index: int                          # the frame within the rotation
    rotation: int


def layer_frames(layers: list[Layer], angle: float, index: int, t: float, playing: bool) -> list[Drawn]:
    """The frame every switched-on layer shows (layers drawing nothing left out)."""
    a = entity_anim(playing)
    out = []
    for lay in layers:
        if not lay.on:
            continue
        s = lay.seq
        k = anim.layer_frame(s, a, index, t)
        r = s.rotation(angle)
        if k is not None and (f := s.frame(r, k)) is not None:
            out.append(Drawn(lay, f, k, r))
    return out


def draw(img: np.ndarray, box, layers: list[Layer], angle: float, index: int, t: float, playing: bool,
         origin: tuple[int, int] = (0, 0)) -> list[Drawn]:
    """Draw the object with its position at ``origin`` into ``img`` (float RGB on the RGB565 grid, covering
    ``box`` = x0, y0, x1, y1 in the same coordinates). Returns what was drawn, in drawing order. (The
    model's ``Sorting Y`` is the same for every layer of one object and does not change the order.)"""
    a = entity_anim(playing)
    queues: dict[bool, list] = {True: [], False: []}
    for d in layer_frames(layers, angle, index, t, playing):
        s = d.layer.seq
        mode = SHADOW_MODE if d.layer.order == 0 else s.mode
        group = 0 if anim.layer_resting(s, a) or not s.on_ground else 1
        for off, lo, hi in s.strips():
            queues[s.on_ground].append((group, off, d.layer.number, d, partial(
                render._blit, img, d.frame, origin[0], origin[1], mode, box, 1, (lo, hi), False)))
    out, seen = [], set()
    for ground in (True, False):
        for *_, d, fn in sorted(queues[ground], key=lambda q: q[:3]):
            fn()
            if id(d) not in seen:
                seen.add(id(d))
                out.append(d)
    return out


def content_box(layers: list[Layer], angles, margin: int = 8) -> tuple[int, int, int, int]:
    """The box around every frame of the switched-on layers in the rotations of ``angles`` (stays the same
    while the sequence plays)."""
    x0 = y0 = math.inf
    x1 = y1 = -math.inf
    for lay in layers:
        if not lay.on:
            continue
        s = lay.seq
        for r in {s.rotation(a) for a in angles}:
            for i in range(s.frames_per_rotation):
                f = s.frame(r, i)
                if f is None:
                    continue
                x0, y0 = min(x0, -f.hot_x), min(y0, -f.hot_y)
                x1, y1 = max(x1, f.width - f.hot_x), max(y1, f.height - f.hot_y)
    if x0 == math.inf:
        return -16, -16, 16, 16
    # the hot spot (the object's position) always inside
    return (min(int(x0), 0) - margin, min(int(y0), 0) - margin, max(int(x1), 1) + margin,
            max(int(y1), 1) + margin)


def still_index(s: mdl.Sequence | None, rotation: int = 0) -> int:
    """The first frame of a rotation that is not empty (effects often start empty), for still images."""
    if s is None:
        return 0
    return next((i for i in range(s.frames_per_rotation) if s.frame(rotation, i) is not None), 0)


def rotation_angles(s: mdl.Sequence | None) -> list[float]:
    """One facing angle per rotation of ``s`` (Rotational Offset + r * Range / Num Rotations), which
    ``mdl.rotation_index`` maps back to rotation r."""
    if s is None or s.rotations <= 1:
        return [0.0]
    return [s.rot_offset + r * s.rot_range / s.rotations for r in range(s.rotations)]


# ---- Backgrounds -------------------------------------------------------------------------------------------

BACKGROUNDS = ('checker', 'black', 'grey', 'texture')
CHECKER = ((102, 102, 102), (153, 153, 153))
CHECKER_CELL = 8
GREY = (38, 38, 38)


def background(kind: str, box, texture: np.ndarray | None = None, origin: tuple[int, int] = (0, 0)) -> np.ndarray:
    """A background (float RGB on the RGB565 grid) for ``box``: a checkerboard, black, grey or a ground
    texture tiled from the world origin with the object at ``origin`` (render.Assets.texture)."""
    x0, y0, x1, y1 = box
    h, w = y1 - y0, x1 - x0
    ys, xs = np.mgrid[y0:y1, x0:x1]
    if kind == 'texture' and texture is not None:
        th, tw = texture.shape[:2]
        img = texture[(ys - origin[1]) % th, (xs - origin[0]) % tw].astype(np.float32)
    elif kind == 'black':
        img = np.zeros((h, w, 3), np.float32)
    elif kind == 'grey':
        img = np.broadcast_to(np.array(GREY, np.float32), (h, w, 3)).copy()
    else:
        odd = (((xs - origin[0]) // CHECKER_CELL + (ys - origin[1]) // CHECKER_CELL) & 1).astype(bool)
        img = np.where(odd[..., None], np.array(CHECKER[1], np.float32), np.array(CHECKER[0], np.float32))
    return render.from565(render.to565(img))


def compose(layers: list[Layer], angle: float, index: int, t: float, playing: bool, box, bg: str = 'checker',
            texture: np.ndarray | None = None) -> tuple[np.ndarray, list[Drawn]]:
    """The object on a background as an RGB uint8 image covering ``box``."""
    img = background(bg, box, texture)
    drawn = draw(img, box, layers, angle, index, t, playing)
    return np.clip(img, 0, 255).astype(np.uint8), drawn


def compose_sheet(layers: list[Layer], angles: list[float], frames: int, fps: float, bg: str = 'checker',
                  texture: np.ndarray | None = None, gap: int = 2) -> Image.Image:
    """One row per facing angle, one column per frame of the base sequence, every cell composed as in the
    view (the entity's frame index = the column, the game time of that frame for ``Auto-Animate``)."""
    box = content_box(layers, angles, margin=2)
    cw, ch = box[2] - box[0], box[3] - box[1]
    sheet = Image.new('RGB', (frames * (cw + gap) + gap, len(angles) * (ch + gap) + gap), (20, 20, 20))
    for r, ang in enumerate(angles):
        for i in range(frames):
            img, _ = compose(layers, ang, i, i / fps if fps > 0 else 0.0, True, box, bg, texture)
            sheet.paste(Image.fromarray(img), (gap + i * (cw + gap), gap + r * (ch + gap)))
    return sheet


def sprite_sheet(rows: list[tuple[str, list[mdl.Frame]]], label: int = 16) -> Image.Image:
    """The frames as an RGBA sheet: one row per (title, frames), every frame with its hot spot on a common
    anchor (``tools/export_model.py``)."""
    if not rows:
        raise ValueError('no frames')
    L = max(f.hot_x for _, fs in rows for f in fs)
    T = max(f.hot_y for _, fs in rows for f in fs)
    R = max(f.width - f.hot_x for _, fs in rows for f in fs)
    B = max(f.height - f.hot_y for _, fs in rows for f in fs)
    cw, ch = L + R + 4, T + B + 4
    ncol = max(len(fs) for _, fs in rows)
    sheet = Image.new('RGBA', (ncol * cw, len(rows) * (ch + label)), (60, 60, 60, 255))
    d = ImageDraw.Draw(sheet)
    for ri, (title, fs) in enumerate(rows):
        y = ri * (ch + label)
        if label:
            d.text((2, y + 2), title, fill=(255, 255, 255, 255))
        for ci, f in enumerate(fs):
            sheet.alpha_composite(Image.fromarray(f.rgba), (ci * cw + 2 + L - f.hot_x, y + label + 2 + T - f.hot_y))
    return sheet


def model_rows(m: mdl.Model, max_frames: int = 24) -> list[tuple[str, list[mdl.Frame]]]:
    """Sprite sheet rows of a model: every sequence, one row per rotation (empty frames left out)."""
    rows = []
    for s in m.sequences:
        rows += sequence_rows(s, max_frames)
    return rows


def sequence_rows(s: mdl.Sequence, max_frames: int | None = None) -> list[tuple[str, list[mdl.Frame]]]:
    rows = []
    n = s.frames_per_rotation if max_frames is None else min(s.frames_per_rotation, max_frames)
    for r in range(s.rotations):
        frames = [f for i in range(n) if (f := s.frame(r, i)) is not None]
        if frames:
            rows.append((f'{s.name} / rotation {r}', frames))
    return rows


# ---- Writing through the game's encoder ------------------------------------------------------------------

def frame_bytes(v: Viewable, f: mdl.Frame) -> bytes:
    """The frame as the game's encoder writes it (frm.encode of its values: the stored frame byte for byte)."""
    return frm.encode(frm.values(v.data, f.offset))


def sequence_file(v: Viewable, s: mdl.Sequence, rotation: int = 0) -> bytes:
    """One rotation of ``s`` as an image sequence file (``.seq16``/``.seq`` by the frames' depth) with the
    sequence's CSequence fields (seq.dumps)."""
    frames = [s.frame(rotation, i) for i in range(s.frames_per_rotation)]
    center, flags, offset = v.sequence_fields(s)
    if v.seqfile is not None:
        return seq.dumps([frame_bytes(v, f) if f is not None else None for f in frames], v.seqfile.fps_raw,
                         v.seqfile.mode, v.seqfile.load_flags, v.seqfile.offset)
    fps = struct.unpack_from('<f', v.data, s.offset + 16)[0] if v.kind != 'frame' else 30.0
    return seq.dumps([frame_bytes(v, f) if f is not None else None for f in frames], fps, s.mode,
                     (center, *flags), offset)


# ---- Properties, frame triggers and sounds ------------------------------------------------------------------

def _num(v: float) -> str:
    s = f'{v:g}'
    return '0' if s == '-0' else s


def sequence_node(v: Viewable, s: mdl.Sequence, trig: list | None = None, head=None) -> tf.Node:
    """The sequence's fields as a text node of its class (CRotationSequence, CSequence or CFont) for the
    property view; ``trig`` the frame triggers (``triggers``), shown with ``head`` (modelhead.ModelHead)."""
    center, flags, offset = v.sequence_fields(s)
    cls = 'CRotationSequence' if v.kind == 'model' else 'CFont' if v.kind == 'font' else 'CSequence'
    n = tf.Node(s.name, cls)
    E = tf.Entry
    n.children += [E('Frames Per Second', _num(s.fps)), E('Center Hot Spot', str(center)), E('Blit Type', s.mode)]
    n.children += [E(k, str(b)) for k, b in zip(LOAD_FLAGS, flags)]
    n.children += [E('X Offset', str(offset[0])), E('Y Offset', str(offset[1]))]
    if v.font is not None:
        n.children += [E('First ASCII', str(v.font.first)), E('Last ASCII', str(v.font.last)),
                       E('Fixed Width', '1' if v.font.fixed_width else '0')]
    if cls != 'CRotationSequence':
        return n
    n.children += [E('Num Rotations', str(s.rotations)), E('Editor Display Offset', str(s.sort_y))]
    n.children += [E(k, str(b)) for k, b in zip(SWITCHES, s.flags)]
    n.children += [E('Rotational Offset', _num(s.rot_offset)), E('Rotational Range', _num(s.rot_range)),
                   E('Sorting Y Offset', str(s.sort_offset))]
    cuts = tf.Node('Cutting Lines', 'Array', [E('Array Count', str(len(s.cuts)))])
    for i, (c, o) in enumerate(s.cuts):
        cuts.children.append(tf.Node(f'Cut {i + 1}', 'CVerticalCut', [E('Cut Offset', str(c)),
                                                                      E('Strip Sorting Y Offset', str(o))]))
    n.children.append(cuts)
    if trig is not None:
        tn = tf.Node('Trigger', 'Array', [E('Array Count', str(len(trig)))])
        for t in trig:
            if t.action is None:
                continue
            node = tf.Node(f'Frame {t.frame}', 'CAnimationTrigger')
            node.children.append(head.node(t.action, 'Action') if head is not None else E('Action', t.action.cls))
            node.children += [E('Trigger Forward', '1' if t.forward else '0'),
                              E('Trigger Reverse', '1' if t.reverse else '0')]
            tn.children.append(node)
        n.children.append(tn)
    return n


@dataclass
class Trigger:
    """A frame trigger of a sequence (CAnimationTrigger, one per frame of a rotation): the action fired when
    the playing sequence reaches the frame forwards (``Trigger Forward``) or backwards [confirmed: code
    0x560300, zax-decomp/reimpl/src/sequence_player.cpp]."""
    frame: int
    forward: bool
    reverse: bool
    action: object | None               # modelhead.Obj
    sounds: list[str] = field(default_factory=list)


def trigger_offset(data: bytes, s: mdl.Sequence) -> int | None:
    """Where the sequence's ``Trigger`` array starts: after the cuts (``mdl.read_sequences``); None if the
    cuts could not be read."""
    o = s.offset
    sl = struct.unpack_from('<I', data, o + 21)[0]
    p = o + 25 + sl + 46
    if struct.unpack_from('<I', data, p)[0] != len(s.cuts):
        return None
    return p + 4 + 20 * len(s.cuts)


def triggers(data: bytes, s: mdl.Sequence, head) -> list[Trigger] | None:
    """The frame triggers of a model sequence, read with the exe's field schema (``head`` a
    modelhead.ModelHead): ``u32`` count + one embedded CAnimationTrigger per frame (Action pointer, the two
    switches). None if they cannot be read (none of the 2,660 sequences of the game data, docs/FORMATS.md 6)."""
    from .modelhead import DecodeError
    p = trigger_offset(data, s)
    if p is None:
        return None
    n = struct.unpack_from('<I', data, p)[0]
    if n > 10000:
        return None
    p += 4
    out = []
    try:
        for i in range(n):
            obj, p = head.decode_object(data, p, 'CAnimationTrigger')
            act = obj.values.get('Action')
            out.append(Trigger(i, bool(obj.values.get('Trigger Forward')), bool(obj.values.get('Trigger Reverse')),
                               act, sounds_in(act)))
    except (DecodeError, struct.error):
        return None
    return out


def sounds_in(obj) -> list[str]:
    """Every text value of an object tree that names a sound file (ends in .wav/.ogg), in field order."""
    out: list[str] = []

    def walk(v, depth=0):
        if depth > 20 or v is None:
            return
        if isinstance(v, str):
            if v.lower().endswith(AUDIO) and v not in out:
                out.append(v)
        elif isinstance(v, (list, tuple)):
            for x in v:
                walk(x, depth + 1)
        elif hasattr(v, 'values') and hasattr(v, 'cls'):
            for _, o in v.dynamic:
                walk(o, depth + 1)
            for x in v.values.values():
                walk(x, depth + 1)
    walk(obj)
    return out


MODEL_SOUNDS = ('Activate Sound', 'Close Sound', 'Death Sound', 'Pain Sound')


def model_sounds(model_obj) -> list[tuple[str, str]]:
    """(field, sound) of the model header's sound fields that are set."""
    if model_obj is None:
        return []
    return [(k, model_obj.values.get(k)) for k in MODEL_SOUNDS if model_obj.values.get(k)]


def sound_file(ds, name: str) -> str | None:
    """The file of a sound reference: ``Sounds/<name>``, a missing ``.wav`` looked up as ``.ogg`` and back
    (``CSoundList::Find`` 0x57e690, docs/FORMATS.md 1) [assumption: the sound list the actions search is
    the one of ``Sounds/``; every reference of the models is found there, tools/selftest.py]."""
    if not name:
        return None
    rel = SOUND_DIR + name.replace('\\', '/')
    if ds.exists(rel):
        return rel
    low = rel.lower()
    for a, b in (('.wav', '.ogg'), ('.ogg', '.wav')):
        if low.endswith(a) and ds.exists(rel[:-4] + b):
            return rel[:-4] + b
    return None


# ---- Frame details -------------------------------------------------------------------------------------------

def frame_info(v: Viewable, f: mdl.Frame) -> dict:
    """Header values of a frame (docs/FORMATS.md 5)."""
    hd = frm.read_header(v.data, f.offset)
    return {'bpp': hd.bpp, 'width': hd.width, 'height': hd.height, 'hot_x': hd.hot_x, 'hot_y': hd.hot_y,
            'rle': hd.rle, 'flags': hd.flags, 'pixel': hd.size, 'extra20': hd.extra20_size,
            'extra24': hd.extra24_size, 'alpha': hd.alpha_size, 'edge': hd.edge_size,
            'semi': int(((f.rgba[..., 3] > 0) & (f.rgba[..., 3] < 255)).sum()),
            'opaque': int((f.rgba[..., 3] == 255).sum())}


def palette_indices(v: Viewable, f: mdl.Frame) -> list[int]:
    """The palette indices an 8-bit frame uses (every block); [] for 16-bit frames."""
    if v.data[f.offset + 1] != 8:
        return []
    fv = frm.values(v.data, f.offset)
    used = fv.values if fv.alpha is None else fv.values[fv.alpha > 0]
    return sorted(int(i) for i in np.unique(used))
