"""Own graphics: PNG images (with alpha) as game images, image sequences and simple new models, through the game's
encoder (zaxtools.frm, seq, mdlfile).

What is written, always as the pair the game needs for its two colour depths (16 bit and 256 colours):

    image      Cache/<folder>/<name>.frm16 + .frm                     (one PNG)
    sequence   Cache/<folder>/<name>.seq16 + .seq                     (a numbered PNG series, or one PNG)
    model      Cache/Models/<folder>/<name>.mdl16 + .mdl              (one sequence of the PNGs, one rotation)

The files go into the editor's output folder at their ``Cache/...`` path (copied below ``Data/`` they win over
``Data.dat`` in the game), never into the game data or a language pack (``write`` refuses a target inside them).

A new model is a decoration model like the 626 shipped ones without a default object (``mdlfile.new_head``):
class ``CEntityBase`` when placed (the editor's minimal object), no collision polygon, no sounds, no hit points;
one sequence (``Idle`` by default) with one rotation. A ``CEntityBase`` always shows frame 0 (FORMATS.md 6, "Frame
shown"), so a sequence of several frames is written with ``Auto-Animate`` on (it then plays by the game time at its
fps, like 231 shipped sequences). All of this is the user's to confirm (docs: CLAUDE.md step 35).

Textures are written uncompressed: an image sequence below ``Cache/Animated Textures`` (the ``Animated Texture`` of a
surface) and an image below ``Cache/Textures`` (ground and surface textures) get raw frames (``frm.encode_raw``), as the
84 frames per depth of the 4 shipped animated textures and all shipped textures are, with the hot spot in the centre
(animated textures) or at 0/0 (textures) and, for a sequence, the shipped animated textures' load switches (Center Hot
Spot 1, Blended With Black 1, Crop Clor 0 1, Use 8 Bit Alpha 0, Dither 0) [verified: the shipped files]. The surface
draws its texture frame's pixels directly: an RLE sequence there shows as garbage in the game [verified 2026-10-30, VM
job 20261030-064034-7177, 8 bit, ``/Original``]. Alpha is dropped (every pixel opaque); the shipped textures are all
128 x 128 but one (``notes``).

The 16-bit frames are what ``frm.encode_rgba16`` writes (the game's encoder; the loader's TGA filters before it -
alpha threshold, crop, un-premultiply - are not applied: the PNG is taken as straight alpha and as it is); the 8-bit
frames take each pixel's palette index from the game's 5-5-5 inverse colour table (``frm.nearest_index8``).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

from . import frm, mdlfile, seq

KINDS = ('image', 'sequence', 'model')
BLIT_TYPES = ('Transparent Mask', 'Blend Black Bias', 'Blend Amplify Light')    # the modes of the shipped data
EXTENSIONS = {'image': ('.frm16', '.frm'), 'sequence': ('.seq16', '.seq'), 'model': ('.mdl16', '.mdl')}
MODEL_DIR = 'Cache/Models'
TEXTURE_FOLDERS = {'sequence': 'animated textures', 'image': 'textures'}   # below Cache/, compared in lower case
TEXTURE_SIZE = (128, 128)                   # every shipped texture and animated texture [verified]
TEXTURE_LOAD_FLAGS = (1, 1, 1, 0, 0)        # Center Hot Spot and the four switches of all 4 shipped animated textures (8 files)
_NUM_RE = re.compile(r'(\d+)')


def natural_key(p: str | Path) -> list:
    """Sort key that orders "frame2" before "frame10"."""
    return [int(t) if t.isdigit() else t.lower() for t in _NUM_RE.split(Path(p).name)]


def series(paths) -> list[Path]:
    """The PNGs of a series in their numbered order."""
    return sorted((Path(p) for p in paths), key=natural_key)


def load_png(path: str | Path) -> np.ndarray:
    """An image as RGBA (h, w, 4) uint8 (images without alpha become opaque)."""
    with Image.open(path) as im:
        return np.asarray(im.convert('RGBA')).copy()


def hot_spot(kind: str, w: int, h: int, where: str) -> tuple[int, int]:
    """A hot spot (anchor pixel from the top left; the game draws the image at position - hot spot):
    'top-left' (0, 0), 'centre', 'bottom-centre' (the foot of a figure or object)."""
    return {'top-left': (0, 0), 'centre': (w // 2, h // 2), 'bottom-centre': (w // 2, h - 1)}[where]


@dataclass
class ImportSpec:
    kind: str                           # image | sequence | model
    name: str                           # file name without extension, e.g. "My Rock"
    folder: str                         # below Cache/ (image, sequence) or below Cache/Models/ (model)
    images: list[np.ndarray]            # RGBA
    hot: tuple[int, int] = (0, 0)
    fps: float = 30.0
    mode: str = 'Transparent Mask'
    sequence: str = 'Idle'              # model: name of its sequence
    on_ground: bool = False             # model: "Render On Ground" (drawn in the ground queue, below all objects)
    auto_animate: bool | None = None    # model: None = on when there is more than one frame
    sorting_y: int = 0                  # model: "Sorting Y"
    warnings: list[str] = field(default_factory=list)

    @property
    def model_path(self) -> str:
        """The model's name as the levels write it (``Model=``): "<folder>/<name>"."""
        f = self.folder.strip('/')
        return f'{f}/{self.name}' if f else self.name

    @property
    def texture(self) -> bool:
        """An image sequence below Cache/Animated Textures or an image below Cache/Textures: written raw."""
        top = self.folder.strip('/').split('/')[0].lower()
        return TEXTURE_FOLDERS.get(self.kind) == top

    def rel(self, ext: str) -> str:
        f = self.folder.strip('/')
        base = MODEL_DIR if self.kind == 'model' else 'Cache'
        return f'{base}/{f}/{self.name}{ext}' if f else f'{base}/{self.name}{ext}'


def check(spec: ImportSpec) -> list[str]:
    """Problems that stop the import (English; the editor shows them)."""
    out = []
    if spec.kind not in KINDS:
        out.append(f'unknown kind {spec.kind!r}')
    if not spec.name.strip() or any(c in spec.name for c in '/\\:*?"<>|~'):
        out.append('the name is empty or contains one of / \\ : * ? " < > | ~')
    if '~' in spec.folder or '..' in spec.folder.split('/') or '\\' in spec.folder:
        out.append('the folder contains "~", ".." or a backslash')
    if not spec.images:
        out.append('no image')
    elif spec.kind == 'image' and len(spec.images) > 1:
        out.append('an image takes one PNG; choose "image sequence" or "model" for a series')
    for im in spec.images:
        h, w = im.shape[:2]
        if not (0 < w <= 2048 and 0 < h <= 2048):
            out.append(f'image size {w}x{h} outside 1..2048')
            break
    if spec.kind == 'model' and not spec.sequence.strip():
        out.append('the model needs a sequence name')
    if spec.mode not in BLIT_TYPES:
        out.append(f'unknown blit type {spec.mode!r}')
    return out


def notes(spec: ImportSpec) -> list[str]:
    """Hints that do not stop the import (English; the editor shows them)."""
    out = []
    if spec.texture and spec.images:
        if any(im.shape[:2] != TEXTURE_SIZE[::-1] for im in spec.images):
            out.append('every shipped texture is 128x128; the ground takes only that size (other sizes in a surface '
                       'are not tested)')
        if any((im[..., 3] < 255).any() for im in spec.images):
            out.append('a texture is written without transparency: every pixel becomes opaque')
    return out


def build(spec: ImportSpec, inv15: bytes, schema=None) -> dict[str, bytes]:
    """The files of the import: data path -> bytes (16 and 8 bit). ``inv15``: ``Palettes/InvColorTable15.pal`` of the
    game data; ``schema``: the exe's field schema (needed for a model's header)."""
    problems = check(spec)
    if problems:
        raise ValueError('; '.join(problems))
    e16, e8 = EXTENSIONS[spec.kind]
    if spec.texture:
        f16, f8 = [], []
        for im in spec.images:
            h, w = im.shape[:2]
            hot = (w // 2, h // 2) if spec.kind == 'sequence' else (0, 0)     # as the shipped ones
            f16.append(frm.encode_raw(frm.rgb_to_pixel16(im[..., :3]), hot))
            f8.append(frm.encode_raw(frm.nearest_index8(im[..., :3], inv15), hot))
        if spec.kind == 'image':
            return {spec.rel(e16): f16[0], spec.rel(e8): f8[0]}
        return {spec.rel(e16): seq.dumps(f16, spec.fps, spec.mode, TEXTURE_LOAD_FLAGS),
                spec.rel(e8): seq.dumps(f8, spec.fps, spec.mode, TEXTURE_LOAD_FLAGS)}
    f16 = [frm.encode_rgba16(im, spec.hot) for im in spec.images]
    f8 = [frm.encode_rgba8(im, inv15, spec.hot) for im in spec.images]
    if spec.kind == 'image':
        return {spec.rel(e16): f16[0], spec.rel(e8): f8[0]}
    if spec.kind == 'sequence':
        return {spec.rel(e16): seq.dumps(f16, spec.fps, spec.mode), spec.rel(e8): seq.dumps(f8, spec.fps, spec.mode)}
    if schema is None:
        raise ValueError('a model needs Zax.exe (the field schema of its header)')
    animate = (len(spec.images) > 1) if spec.auto_animate is None else spec.auto_animate
    head = mdlfile.new_head(spec.name, spec.sequence, schema, spec.sorting_y)
    out = {}
    for ext, frames in ((e16, f16), (e8, f8)):
        rec = mdlfile.SeqRecord(spec.sequence, frames, fps=spec.fps, mode=spec.mode,
                                switches=(int(spec.on_ground), 0, int(animate), 0, 0, 0))
        out[spec.rel(ext)] = mdlfile.dumps(mdlfile.ModelFile(head, mdlfile.model_path(spec.model_path), [rec]))
    return out


def replace_frames(data: bytes, head, sequence: str, images: list[np.ndarray], hot: tuple[int, int],
                   inv15: bytes | None = None, rotation: int | None = None) -> bytes:
    """A copy of a model file (``data``, .mdl16 or .mdl by its frames' depth) with the frames of one sequence
    replaced by the images (``rotation`` None: the images are every frame of the sequence, their number may differ
    but must divide by its rotations; a rotation index: only that rotation's frames, the number must match).
    Everything else stays byte for byte; the frame box is computed anew, the frame deltas become zeros."""
    m = mdlfile.parse(data, head)
    s = next((x for x in m.sequences if x.present and x.name.lower() == sequence.lower()), None)
    if s is None:
        raise ValueError(f'the model has no sequence {sequence!r}')
    depth = next((d[1] for d in s.frames if d is not None), 16)
    if depth == 8 and inv15 is None:
        raise ValueError('an 8-bit model needs the inverse colour table')
    enc = [frm.encode_rgba16(im, hot) if depth == 16 else frm.encode_rgba8(im, inv15, hot) for im in images]
    if rotation is None:
        if len(enc) % max(1, s.rotations):
            raise ValueError(f'{len(enc)} images do not divide by the {s.rotations} rotations')
        s.frames = enc
    else:
        per = s.per_rotation
        if len(enc) != per or not 0 <= rotation < s.rotations:
            raise ValueError(f'rotation {rotation}: {per} images needed')
        s.frames = s.frames[:rotation * per] + enc + s.frames[(rotation + 1) * per:]
    s.box = None
    s.deltas = None                         # the frame triggers belong to frame numbers and stay as they are
    return mdlfile.dumps(m)


def inside(path: Path, roots) -> bool:
    p = Path(path).resolve()
    for r in roots:
        if r is None:
            continue
        r = Path(r).resolve()
        if p == r or r in p.parents:
            return True
    return False


def write(files: dict[str, bytes], out_dir: Path, forbidden=()) -> list[Path]:
    """Write the files below the output folder; ``forbidden`` the game data folder/file and the language pack
    (a target inside them is refused). Returns the written paths."""
    out_dir = Path(out_dir)
    if inside(out_dir, [f if Path(f).is_dir() else Path(f).parent for f in forbidden if f]):
        raise ValueError('the output folder lies inside the game data')
    written = []
    for rel, data in files.items():
        target = out_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        written.append(target)
    return written
