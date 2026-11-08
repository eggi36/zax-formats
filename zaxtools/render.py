"""Draw a level as it looks in the game (approximation).

Ground: Plasma Ground value * number of textures / 256 selects the texture band, grid points at a
spacing of 64, in between a plasma fractal as in Zax.exe (``plasma``). Transition as in Zax.exe
(CPlasmaTileMap, table over all 256 values): in the upper ``Blending`` share of every band the
texture is mixed linearly with the next one, below that the texture is pure; the top band does
not mix.
Polygons (CRenderablePolygon) by "Render Type": Textured = "Static Texture", Animated Texture =
first image of "Animated Texture" (Cache/Animated Textures), Black = black; other types like
Textured. Polygons are sorted in like objects, with bottom edge + "YSort" (surface_key);
"On Ground=1" below the shadows and ground layers, "On Ground=0" below the objects.
Objects: active sequence + layers (zaxtools.mdl.Model.layers), rotation 0 (with use_facing by
Start FacingAngle like the exe), the frame the game shows (zaxtools.anim: CEntityBase frame 0,
"Current Frame", looped AIs, "Auto-Animate" by the game time), position - hot spot, layers with
"Render On Ground" first, every layer sorted separately by position Y + the model's "Sorting Y"
(CModel, via the catalogue; 0 without catalogue) + the sequence's "Sorting Y Offset"; layers with
"Cutting Lines" split into vertical strips with their own offset (mdl.Sequence.strips, like
Zax.exe 0x4886a0).
Render modes like Zax.exe at 16 bit with its integer arithmetic on RGB565 (FORMATS.md 6, exact
arithmetic): "Transparent Mask" and "Blend Black Bias" copy the pixel block and blend the edge
block (MMX and scalar spans, clip columns of 64 pixels), "Blend Amplify Light" brightens the
background through the 32 x 32 tables (``min(31, d + d * s // 31)`` per channel). 8-bit frames
are blended in float.

Known deviations: facing direction only with use_facing; the frames that depend on the tick count
or on chance (Auto-Animate, idling characters) cannot match a given screenshot. "Rendering Height"
raises all layers without "Render On Ground".
"""
from __future__ import annotations

import math
from functools import partial

import numpy as np
from PIL import Image, ImageDraw

from . import anim, frm, mdl, plasma, seq
from .datasource import DataSource
from .level import Level

EDITOR_PREFIX = 'Editor/'


class Assets:
    """Loads textures and models on demand and keeps them in memory."""

    def __init__(self, ds: DataSource):
        self.ds = ds
        self._tex: dict[str, np.ndarray | None] = {}
        self._mdl: dict[str, mdl.Model | None] = {}
        self._anim: dict[str, list[np.ndarray] | None] = {}
        self.sort_y: dict[str, int] = {}      # model path (lower case) -> "Sorting Y", from Catalog.sorting_y()
        self.own_roots: list = []             # folders laid out like Data (the editor's output folder) whose
        #                                       models win: own models made by zaxtools.imageimport

    def texture(self, name: str) -> np.ndarray | None:
        if name not in self._tex:
            rel = f'Cache/Textures/{name}.frm16'
            self._tex[name] = (frm.decode(self.ds.read(rel))[0][..., :3].astype(np.float32)
                               if self.ds.exists(rel) else None)
        return self._tex[name]

    def animation(self, name: str) -> tuple[list[np.ndarray], float] | None:
        """Images (RGB, float) and frames/s of an animated polygon texture."""
        if name not in self._anim:
            rel = f'Cache/Animated Textures/{name}.seq16'
            a = None
            if self.ds.exists(rel):
                sq = seq.load(self.ds.read(rel))
                frames = [f.rgba[..., :3].astype(np.float32) for f in sq.frames if f is not None]
                a = (frames, sq.fps) if frames else None
            self._anim[name] = a
        return self._anim[name]

    def model(self, name: str) -> mdl.Model | None:
        if name not in self._mdl:
            rel = f'Cache/Models/{name}.mdl16'
            own = next((r / rel for r in self.own_roots if (r / rel).is_file()), None)
            if own is not None:
                self._mdl[name] = mdl.load(own.read_bytes(), name)
            else:
                self._mdl[name] = mdl.load(self.ds.read(rel), name) if self.ds.exists(rel) else None
        return self._mdl[name]

    def forget(self, name: str) -> None:
        """Read the model anew on next use (after an import replaced it)."""
        self._mdl.pop(name, None)

    def sorting_y(self, name: str | None) -> int:
        """Sorting offset of the model: objects are drawn by position Y + Sorting Y."""
        return self.sort_y.get((name or '').lower(), 0)


def blending(level: Level) -> float:
    """``Blending`` of the Plasma Ground; 0.25 without the field (default in Zax.exe)."""
    try:
        return float(level.plasma.get('Blending') or 0.25)
    except (AttributeError, ValueError):
        return 0.25


def band_start(index: int, count: int) -> int:
    """Smallest grid value of band ``index``: the texture is pure there (with any ``Blending``).
    The original editor paints like that too: 24 % of all grid points of the originals lie
    exactly here, 3.3 % in the middle of the band [verified on all 112 levels]."""
    return -(-index * 256 // count)


def blend_weight(v, count: int, blend: float):
    """(band, share of the next texture) for ground values ``v`` (0..255, also interpolated).
    Like Zax.exe: ``f`` = position in the band, share = (f - (1 - Blending)) / Blending, from 0."""
    b = np.asarray(v, np.float32) * count / 256
    i = np.minimum(b.astype(int), count - 1)
    w = np.clip((b - i - (1 - blend)) / max(blend, 1e-6), 0, 1)
    return i, np.where(i >= count - 1, 0, w).astype(np.float32)


def _tile128(t: np.ndarray | None) -> np.ndarray:
    """Bring a texture to 128x128: smaller ones (``Special/Under Construction`` is 32x32, all
    others 128x128 [verified]) are tiled so all fit into one array. The game itself shows a
    smaller ground texture incorrectly (stripes) [verified]; the editor therefore does not
    offer it."""
    if t is None:
        return np.zeros((128, 128, 3), np.float32)
    h, w = t.shape[:2]
    return t[np.arange(128) % h][:, np.arange(128) % w]


def surface_kind(p) -> str:
    """Display of a polygon: 'black', 'animated' or 'textured'."""
    rt = (p.get('Render Type') or '').lower()
    return 'black' if rt == 'black' else 'animated' if rt == 'animated texture' else 'textured'


def on_ground(p) -> bool:
    """"On Ground" of a polygon; 1 without the field, like the constructor in Zax.exe (0x55d880)."""
    return p.get('On Ground', '1') != '0'


def surface_key(p) -> tuple[int, float]:
    """Sort key of a polygon like Zax.exe (0x55dc30): bottom edge of the polygon + "YSort" (0
    without the field), the left edge on ties. It is compared like position Y + Sorting Y of the
    objects - "On Ground=1" below the shadows and ground layers, otherwise below the objects
    (0x55dd90)."""
    xs, ys = zip(*p.polygon)
    return math.ceil(max(ys)) + int(float(p.get('YSort') or 0)), min(xs)


def surface_texture(p, assets: Assets) -> np.ndarray | None:
    """Texture of a polygon for a still image (RGB float, tiling); black = zeros."""
    kind = surface_kind(p)
    if kind == 'black':
        return np.zeros((128, 128, 3), np.float32)
    if kind == 'animated' and (a := assets.animation(p.get('Animated Texture') or '')):
        return a[0][0]
    name = p.get('Static Texture')
    return assets.texture(name) if name else None


_DEPTH = np.array([31, 63, 31], np.int32)        # RGB565 per channel
_SHIFT = np.array([5, 6, 5], np.int32)           # alpha levels: 32 (R, B) or 64 (G)


def mix16(a: np.ndarray, b: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Mix two ground textures like Zax.exe at 16 bit (0x541541): alpha = int(w * 255), per
    channel in RGB565 ``A + floor((B - A) * (alpha >> 3 or >> 2) / 32 or 64)``. The rounding down
    makes every mixed pixel a little darker (on average half a colour step, R/B ~4, G ~2 of
    255) - visible as blotches in the game where the value lies just below a band boundary
    [verified 2026-10-19 on a game screenshot]. Unmixed pixels (w = 0) stay unchanged."""
    alpha = (np.asarray(w, np.float32) * 255).astype(np.int32)[..., None]
    a5 = np.rint(np.asarray(a, np.float32) * _DEPTH / 255).astype(np.int32)
    b5 = np.rint(np.asarray(b, np.float32) * _DEPTH / 255).astype(np.int32)
    k = alpha >> (8 - _SHIFT)
    c = a5 + np.floor_divide((b5 - a5) * k, 1 << _SHIFT)
    out = (c * 255 // _DEPTH).astype(np.float32)
    return np.where(alpha > 0, out, np.asarray(a, np.float32))


def ground_values(level: Level, xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
    """Ground value (0..255) at the world pixels (xs, ys): plasma fractal as in the game
    (``plasma``); outside the grid the value at the edge."""
    E = level.elevations
    rows, cols = E.shape[0] - 1, E.shape[1] - 1
    if rows < 1 or cols < 1:
        return np.full(xs.shape, E.flat[0] if E.size else 0, np.uint8)
    px = np.clip(xs, 0, cols * plasma.TILE - 1)
    py = np.clip(ys, 0, rows * plasma.TILE - 1)
    a0, a1 = int(px.min()) // plasma.TILE, int(px.max()) // plasma.TILE
    b0, b1 = int(py.min()) // plasma.TILE, int(py.max()) // plasma.TILE
    vals = plasma.CACHE.values(E, level.seeds, slice(b0, b1 + 1), slice(a0, a1 + 1))
    return vals[py - b0 * plasma.TILE, px - a0 * plasma.TILE]


GROUND_CHUNK = 512        # output pixels per side of the pieces Ground computes one after the other


def _mix_tables() -> list[np.ndarray]:
    """``mix16`` for one channel as a table [k, a, b] -> uint8 (k = alpha >> 3 or >> 2, a and b the 8-bit
    texture values): the same integer arithmetic on the same RGB565 levels, for every input at once."""
    values = np.repeat(np.arange(256, dtype=np.float32)[:, None], 3, 1)
    levels = np.rint(values * _DEPTH / 255).astype(np.int32)                     # as mix16: (256, 3)
    out = []
    for ch in range(3):
        q, shift, depth = levels[:, ch], int(_SHIFT[ch]), int(_DEPTH[ch])
        a5, b5 = q[:, None], q[None, :]
        table = np.empty((1 << shift, 256, 256), np.uint8)
        for k in range(1 << shift):         # one k at a time: small intermediates
            c = a5 + np.floor_divide((b5 - a5) * k, 1 << shift)
            table[k] = c * 255 // depth
        out.append(table.ravel())
    return out


_MIX: list[np.ndarray] = []


def _bytes(words: np.ndarray) -> np.ndarray:
    """RGBX words (h, w) uint32 (R in the low byte) as (h, w, 4) uint8."""
    if not np.little_endian:
        words = words.byteswap()
    return words.view(np.uint8).reshape(*words.shape, 4)


class Ground:
    """The ground of a level prepared for drawing, piece by piece and in small integer types (~10 bytes per
    pixel of a piece instead of ~150 for the whole box at once): the textures packed as RGBX words, tables
    over the 256 ground values for the band and the blend alpha ``int(w * 255)`` (``blend_weight``), and
    ``mix16`` as tables per channel. All are built with the very expressions of ``blend_weight`` and
    ``mix16`` applied to every possible input (each step is a function of the ground value or of the two
    texture values and alpha alone; the rest is integer arithmetic), so the pixels are exactly theirs
    [verified: all 112 levels, step 1 and 2, byte for byte against the former whole-box computation].

    ``elevations``/``seeds`` are a snapshot of the grid (``refresh_grid`` after painting); the rest
    changes only with the texture list or ``Blending`` (then build a new one). ``rgbx``/``rgb`` may run
    in another thread than the one that changes the level (the plasma cache is locked)."""

    def __init__(self, level: Level, assets: Assets):
        names = level.ground_textures
        tex = np.stack([_tile128(assets.texture(n)) for n in names])     # raises without textures, as before
        t8 = tex.astype(np.uint8)
        if not np.array_equal(t8, tex):                  # decoded frames are whole numbers 0..255
            raise ValueError('ground texture values are not 8-bit integers')
        self.count = len(names)
        self.texels = (t8[..., 0].astype(np.uint32) | t8[..., 1].astype(np.uint32) << 8
                       | t8[..., 2].astype(np.uint32) << 16 | np.uint32(0xff000000)).ravel()
        band, w = blend_weight(np.arange(256, dtype=np.uint8), self.count, blending(level))
        band = band.astype(np.int32)
        self.band_at = band * 128 * 128                  # offset of the band's texture in texels
        self.next_at = np.minimum(band + 1, self.count - 1) * 128 * 128
        self.alpha = (np.asarray(w, np.float32) * 255).astype(np.int32)              # as mix16
        if not _MIX:
            _MIX[:] = _mix_tables()
        self.refresh_grid(level)

    def refresh_grid(self, level: Level) -> None:
        """Take the level's current ``Elevations`` and ``Seeds``."""
        self.elevations = level.elevations
        self.seeds = level.seeds

    def warm(self, box) -> None:
        """Compute the plasma tiles under the world area box=(x0, y0, x1, y1) in one go (``rgbx`` asks for
        them piece by piece, which is slower for an area that is not cached yet)."""
        E = self.elevations
        rows, cols = E.shape[0] - 1, E.shape[1] - 1
        if rows < 1 or cols < 1:
            return
        x0, y0, x1, y1 = (int(v) for v in box)
        a0, a1 = (min(max(x, 0), cols * plasma.TILE - 1) // plasma.TILE for x in (x0, x1 - 1))
        b0, b1 = (min(max(y, 0), rows * plasma.TILE - 1) // plasma.TILE for y in (y0, y1 - 1))
        plasma.CACHE.ensure(E, self.seeds, slice(b0, b1 + 1), slice(a0, a1 + 1))

    def values(self, xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
        """Ground values (uint8) at the grid ``ys`` x ``xs`` of world pixels (1-D int arrays), as
        ``ground_values`` gives them for the full 2-D grids."""
        E = self.elevations
        rows, cols = E.shape[0] - 1, E.shape[1] - 1
        if rows < 1 or cols < 1:
            return np.full((len(ys), len(xs)), E.flat[0] if E.size else 0, np.uint8)
        px = np.clip(xs, 0, cols * plasma.TILE - 1)
        py = np.clip(ys, 0, rows * plasma.TILE - 1)
        a0, a1 = int(px.min()) // plasma.TILE, int(px.max()) // plasma.TILE
        b0, b1 = int(py.min()) // plasma.TILE, int(py.max()) // plasma.TILE
        vals = plasma.CACHE.values(E, self.seeds, slice(b0, b1 + 1), slice(a0, a1 + 1))
        return vals[np.ix_(py - b0 * plasma.TILE, px - a0 * plasma.TILE)]

    def pieces(self, box, step: int = 1):
        """(row, column, RGBX words (h, w) uint32) of the ground in the world area box=(x0, y0, x1, y1),
        every ``step``-th world coordinate, in pieces of at most GROUND_CHUNK x GROUND_CHUNK; row/column
        index the output image."""
        x0, y0, x1, y1 = box
        # the coordinates exactly as np.mgrid[y0:y1:step, x0:x1:step].astype(np.float32).astype(int)
        xs = np.arange(x0, x1, step).astype(np.float32).astype(int)
        ys = np.arange(y0, y1, step).astype(np.float32).astype(int)
        if len(xs) > GROUND_CHUNK or len(ys) > GROUND_CHUNK:
            self.warm(box)
        for r in range(0, len(ys), GROUND_CHUNK):
            for c in range(0, len(xs), GROUND_CHUNK):
                yield r, c, self._piece(xs[c:c + GROUND_CHUNK], ys[r:r + GROUND_CHUNK])

    def rgbx(self, box, step: int = 1) -> np.ndarray:
        """The ground in the world area box=(x0, y0, x1, y1), every ``step``-th world coordinate, as uint8
        (h, w, 4) R, G, B, 255 - the pixels of ``render_ground`` without surfaces."""
        x0, y0, x1, y1 = box
        h, w = len(np.arange(y0, y1, step)), len(np.arange(x0, x1, step))
        out = np.empty((h, w), np.uint32)
        for r, c, px in self.pieces(box, step):
            out[r:r + px.shape[0], c:c + px.shape[1]] = px
        return _bytes(out)

    def rgb(self, box, step: int = 1) -> np.ndarray:
        """As ``rgbx``, (h, w, 3)."""
        return np.ascontiguousarray(self.rgbx(box, step)[..., :3])

    def _piece(self, xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
        """RGBX words (len ys, len xs) uint32 of the world pixels ``ys`` x ``xs``."""
        v = self.values(xs, ys)
        at = ((ys % 128) * 128).astype(np.int32)[:, None] + (xs % 128).astype(np.int32)[None, :]
        px = self.texels.take(self.band_at[v] + at)               # band texture, RGBX words (h, w)
        alpha = self.alpha[v]
        mixed = np.flatnonzero(alpha)
        if not len(mixed):
            return px
        va, at = v.ravel()[mixed], at.ravel()[mixed]
        a = px.ravel()[mixed]
        b = self.texels.take(self.next_at[va] + at)
        al = alpha.ravel()[mixed]
        word = np.full(len(mixed), 0xff000000, np.uint32)
        for ch in range(3):
            sh = 8 * ch
            k = al >> (8 - int(_SHIFT[ch]))
            i = (k << 16) | ((a >> sh) & 0xff).astype(np.int32) << 8 | ((b >> sh) & 0xff).astype(np.int32)
            word |= _MIX[ch].take(i).astype(np.uint32) << sh
        px.ravel()[mixed] = word
        return px


def render_ground(level: Level, assets: Assets, box, step: int = 1, surfaces: bool = True,
                  ground: Ground | None = None) -> np.ndarray:
    """Ground in the world area box=(x0, y0, x1, y1), every ``step``-th world coordinate, as float32 RGB
    (whole numbers 0..255). ``surfaces``: also draw polygons on the ground (CRenderablePolygon, On
    Ground=1) (the editor shows them as a layer of their own). ``ground``: a prepared ``Ground`` of the
    level to reuse. The pixels are those of the former whole-box computation (plasma values ->
    ``blend_weight`` -> ``mix16``), kept byte for byte (selftest, ``Ground``)."""
    g = ground or Ground(level, assets)
    x0, y0, x1, y1 = box
    img = np.empty((len(np.arange(y0, y1, step)), len(np.arange(x0, x1, step)), 3), np.float32)
    for r, c, px in g.pieces(box, step):
        img[r:r + px.shape[0], c:c + px.shape[1]] = _bytes(px)[..., :3]
    if surfaces:
        _draw_surfaces(img, level, assets, box, step, ground=True)
    return img


def surfaces(level: Level, ground: bool) -> list:
    """Visible polygons (CRenderablePolygon) with On Ground = ``ground``."""
    return [p for p in level.parts if p.cls == 'CRenderablePolygon' and p.polygon and p.visible
            and on_ground(p) == ground]


def _draw_surfaces(img, level: Level, assets: Assets, box, step: int, ground: bool) -> None:
    """Draw polygons with On Ground = ``ground`` into the image in the game's order."""
    for p in sorted(surfaces(level, ground), key=surface_key):
        _draw_surface(img, p, assets, box, step)


def _draw_surface(img, p, assets: Assets, box, step: int) -> None:
    """Draw one polygon (CRenderablePolygon) tiled in world coordinates."""
    tex = surface_texture(p, assets)
    if tex is None:
        return
    x0, y0, _, _ = box
    mask = Image.new('1', (img.shape[1], img.shape[0]), 0)
    ImageDraw.Draw(mask).polygon([((x - x0) / step, (y - y0) / step) for x, y in p.polygon], fill=1)
    r, c = np.nonzero(np.array(mask, bool))
    img[r, c] = tex[(y0 + r * step) % 128 % tex.shape[0], (x0 + c * step) % 128 % tex.shape[1]]


def to565(rgb: np.ndarray) -> np.ndarray:
    """8-bit RGB (float or int, values as ``frm.rgb565_to_rgb`` gives them) -> RGB565 as uint32."""
    return frm.rgb_to_rgb565(np.asarray(rgb)).astype(np.uint32)


def from565(px: np.ndarray) -> np.ndarray:
    """RGB565 -> 8-bit RGB (float32), the same expansion as the image decoder."""
    return frm.rgb565_to_rgb(np.asarray(px, np.uint32)).astype(np.float32).reshape(np.shape(px) + (3,))


def blend565(d: np.ndarray, s: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Alpha blend of the scalar 16-bit spans (``Blend16_AlphaPixel`` 0x44bf70, FORMATS.md 6), in
    32-bit unsigned arithmetic like the exe: 31/32 (green 63/64) of the difference at w = 255,
    rounded down; a negative blue difference borrows from green."""
    d, s, w = (np.asarray(v, np.uint32) for v in (d, s, w))
    a6 = w >> 2
    a5 = a6 >> 1
    g = ((((s >> 5) & 63) - ((d >> 5) & 63)) * a6 >> 1) + (d & np.uint32(0xffffffe0)) & 0x7e0
    r = ((((s >> 11) - (d >> 11)) * a5 << 6) + (d & 0xf83f)) & 0xf800
    b = ((s & 31) - (d & 31)) * a5 >> 5
    return ((d & 31) + b + g + r) & 0xffff


def blend565_mmx(d: np.ndarray, s: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Alpha blend of the MMX spans (groups of four pixels, ``zax-decomp/reimpl/src/spans_mmx.h``): a weighted
    mean with rounding, w = 255 gives the source."""
    d, s, w = (np.asarray(v, np.uint32) for v in (d, s, w))
    a6 = w >> 2
    a5 = a6 >> 1
    G = ((s >> 1) & 0x3f0) * a6 + ((d >> 1) & 0x3f0) * (63 - a6) + 0x200
    B = (s & 31) * a5 + (d & 31) * (31 - a5) + 0x10
    R = (s >> 11) * a5 + (d >> 11) * (31 - a5) + 0x10
    return (((G + (G >> 6)) >> 5) & 0x7e0) | ((B + (B >> 5)) >> 5) | (((R + (R >> 5)) >> 5) << 11)


def _amp_table() -> np.ndarray:
    """The 32 x 32 table of CBlendAmplifyLight_Ctor 0x433df0: ``min(31, d + d * s // 31)``."""
    d, s = np.mgrid[0:32, 0:32].astype(np.uint32)
    return np.minimum(31, d + d * s // 31)


AMP = _amp_table()


def amplify565(d: np.ndarray, s: np.ndarray) -> np.ndarray:
    """"Blend Amplify Light" at 16 bit (0x434280/0x434310): per channel the top five bits,
    ``min(31, D + D * S // 31)``; green without its lowest bit (always 0 in the result)."""
    d, s = np.asarray(d, np.uint32), np.asarray(s, np.uint32)
    r = AMP[d >> 11, s >> 11]
    g = AMP[(d >> 6) & 31, (s >> 6) & 31]
    b = AMP[d & 31, s & 31]
    return (r << 11) | (g << 6) | b


# The game draws the sprites of a level view through clip rectangles whose left and right edges lie
# on multiples of 64 world pixels (the tiles of the tile map), so an edge span is cut there and its
# MMX groups counted from the cut [verified 2026-10-28 on one screenshot of Test/Licht: with these
# cuts 99.9-100 % of the static objects' pixels are identical, without them 99.2-99.7 %; which
# rectangles the dirty tile drawing (World_DrawDirtyTiles 0x4e8080) uses per frame: assumption].
# 0 turns the cuts off.
CLIP_COLUMNS = 64


def _blit(img, f: mdl.Frame, px, py, mode, box, step, xs=None, cut=True):
    """Draw a frame with its hot spot at (px, py). ``xs`` = (from, to): only the columns with
    x - hot spot in [from, to) (strip between two cuts, mdl.Sequence.strips).

    16-bit frames are drawn with the exe's integer arithmetic on RGB565 (FORMATS.md 6, exact
    arithmetic): "Transparent Mask" and "Blend Black Bias" copy the pixel block and blend the
    edge block - per RLE entry (span) the first 4 * (n // 4) pixels with the MMX blend, the rest
    with the scalar one; a span cut by the strip or the image edge counts from the cut. "Blend
    Amplify Light" draws the pixel block through its tables (no edge block). ``img`` stays on the
    RGB565 grid (expanded like the image decoder)."""
    x0, y0, x1, y1 = box
    L = f.layers16()
    ox = int(round((px - f.hot_x - x0) / step))
    oy = int(round((py - f.hot_y - y0) / step))
    H, W = img.shape[:2]
    # visible frame columns [c0, c1): strip and image edge (the game's clip rectangle)
    c0, c1 = 0, f.width
    if xs is not None:
        c0 = int(max(c0, min(f.width, xs[0] + f.hot_x)))
        c1 = int(max(c0, min(f.width, xs[1] + f.hot_x)))
    if step == 1:
        c0, c1 = max(c0, -ox), min(c1, W - ox)
    if c1 <= c0:
        return
    if L is None:                                   # 8-bit frame: float blend as before
        rgba = f.rgba.copy()
        rgba[:, :c0, 3] = 0
        rgba[:, c1:, 3] = 0
        _blit_float(img, rgba[::step, ::step], ox, oy, mode)
        return
    cols = np.arange(f.width)
    inside = (cols >= c0) & (cols < c1)
    rows = slice(None, None, step)
    sel = (slice(None, None, step), slice(None, None, step))
    h, w = (f.height + step - 1) // step, (f.width + step - 1) // step
    sx0, sy0 = max(0, -ox), max(0, -oy)
    sx1, sy1 = min(w, W - ox), min(h, H - oy)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    win = (slice(sy0, sy1), slice(sx0, sx1))
    dst = img[oy + sy0:oy + sy1, ox + sx0:ox + sx1]
    d = to565(dst)
    out = d.copy()
    pm = (L.pix_mask & inside)[sel][win]
    pix = L.pix.astype(np.uint32)[sel][win]
    if mode == 'Blend Amplify Light':
        out[pm] = amplify565(d[pm], pix[pm])
    else:
        out[pm] = pix[pm]
        em = (L.edge_mask & inside)[sel][win]
        if em.any():
            # span as the clipped row passes it: [max(start, c0), min(end, c1))
            st = np.maximum(L.span_start.astype(np.int32), c0)
            en = np.minimum(L.span_start.astype(np.int32) + L.span_len, c1)
            if CLIP_COLUMNS and cut:
                # columns of the game's clip rectangles in world x (see CLIP_COLUMNS)
                wx = int(px - f.hot_x)
                cell0 = (np.floor_divide(wx + cols, CLIP_COLUMNS) * CLIP_COLUMNS - wx)[None, :]
                st = np.maximum(st, cell0)
                en = np.minimum(en, cell0 + CLIP_COLUMNS)
            mmx = (cols[None, :] - st) < ((en - st) & ~3)
            mmx = mmx[sel][win]
            e = L.edge.astype(np.uint32)[sel][win]
            a = L.alpha[sel][win]
            base = out
            k = em & mmx
            out[k] = blend565_mmx(base[k], e[k], a[k])
            k = em & ~mmx
            out[k] = blend565(base[k], e[k], a[k])
    dst[:] = from565(out)


def _blit_float(img, rgba, ox, oy, mode):
    """Float blend for 8-bit frames (the exact arithmetic is only known for 16 bit)."""
    h, w = rgba.shape[:2]
    H, W = img.shape[:2]
    sx0, sy0 = max(0, -ox), max(0, -oy)
    sx1, sy1 = min(w, W - ox), min(h, H - oy)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    src = rgba[sy0:sy1, sx0:sx1].astype(np.float32)
    dst = img[oy + sy0:oy + sy1, ox + sx0:ox + sx1]
    a = src[..., 3:4] / 255
    if mode == 'Blend Amplify Light':
        dst[:] = np.where(a > 0, amplify(dst, src[..., :3]), dst)
    else:
        dst[:] = dst * (1 - a) + src[..., :3] * a


def amplify(d, s):
    """"Blend Amplify Light" in float on 8-bit channels (``d + d * s``); the exact 16-bit form is
    ``amplify565``. Used for 8-bit frames and by the editor's preview (scene.Sprite)."""
    return np.minimum(255, d + d * s / 255)


def render_level(level: Level, assets: Assets, box=None, step: int = 1,
                 show_editor: bool = False, use_facing: bool = False, t: float | None = None,
                 polygons=(), overlays=None, bounds=None, children: bool = True) -> Image.Image:
    """Whole level (or an area) as a PIL image.

    ``use_facing``: use the angle the game draws with (``LevelPart.draw_angle``: "Movement Angle"; mapping angle ->
    rotation as in the exe, mdl.rotation_index). ``t``: seconds after level start for the
    animations (zaxtools.anim; None = the frame at level start, "Auto-Animate" layers at game time
    0). ``polygons``: classes whose outlines are drawn on top (``POLYGON_COLORS``); ``overlays``: AI
    overlay groups (zaxtools.overlays.GROUPS) drawn on top, ``bounds(model)`` gives the models'
    "Bounds Poly" for them. ``children``: draw the objects of the parts' "Child List" (upper bodies,
    effects, carried items) at the parent's position plus their own (``LevelPart.children``,
    ``anim.child_animation``)."""
    if box is None:
        box = (0, 0, *level.size)
    img = render_ground(level, assets, box, step, surfaces=False)
    objs = []

    def add(p, m, a, pos, height, facing):
        layers = m.layers(a.sequence)
        cur = next((s for order, s in layers if order == 2), None)
        objs.append((pos[1] + assets.sorting_y(p.model), pos[1], pos[0], layers,
                     facing if use_facing else 0.0, height, a, anim.frame_index(a, cur, t)))

    def add_children(p, a, pos, height, root):
        # every child the game draws at its parent's position and height plus its own; its own children the
        # same way from there (Entity_Draw 0x488d70 hands the moved position to CLayerPart slot 23 0x4fa9a0,
        # which calls each visible child's slot 23 = its Entity_Draw) [confirmed: code]
        for c in p.children:
            cpos = c.position
            if cpos is None or not c.model or not c.drawn_in_game:
                continue
            cm = assets.model(c.model)
            ca = anim.child_animation(c, cm, a) if cm is not None else None
            if ca is None:
                continue
            at, h = (pos[0] + cpos[0], pos[1] + cpos[1]), height + c.rendering_height
            add(c, cm, ca, at, h, anim.child_facing(c, root))
            add_children(c, ca, at, h, root)

    for p in level.parts:
        pos = p.position
        if pos is None or not p.model or not p.drawn_in_game:
            continue
        if p.model.startswith(EDITOR_PREFIX) and not show_editor:
            continue
        m = assets.model(p.model)
        if m is None:
            continue
        a = anim.part_animation(p, m)
        add(p, m, a, pos, p.rendering_height, p.draw_angle)
        if children:
            add_children(p, a, pos, p.rendering_height, p)
    objs.sort(key=lambda o: (o[0], o[2]))

    def lift(s, h):                                 # Rendering Height, not for ground layers
        return 0 if s.on_ground else h

    # Two queues like Zax.exe (0x4e7c00): first layers with "Render On Ground" (shadows, ground layers)
    # and polygons with On Ground=1, then the remaining layers and polygons. Each sorted by
    # (position Y + Sorting Y + offset of the strip) * 8 + layer, by x on ties (comparison
    # 0x49c9a0); every layer split into vertical strips (0x4886a0). The resting entries of the
    # ground queue lie in the cached background, the others are drawn above it every frame
    # (World_DrawDirtyTiles 0x4e8080, zaxtools.anim): first group 0, then 1.
    queues = {True: [], False: []}
    for sy, y, x, layers, ang, h, a, index in objs:
        # an object that changes is redrawn every frame through the dirty tiles: no 64-pixel cuts
        cut = all(anim.layer_resting(s, a) for _, s in layers)
        for li, (order, s) in enumerate(layers):
            k = anim.layer_frame(s, a, index, t)
            if k is None or (fr := s.frame(s.rotation(ang), k)) is None:
                continue
            mode = 'Transparent Mask' if order == 0 else s.mode
            group = 0 if anim.layer_resting(s, a) or not s.on_ground else 1
            for off, x_lo, x_hi in s.strips():
                queues[s.on_ground].append((group, sy + off, li, x, partial(
                    _blit, img, fr, x, y - lift(s, h), mode, box, step, (x_lo, x_hi), cut)))
    for ground in (True, False):
        for p in surfaces(level, ground):
            k, x = surface_key(p)
            # surfaces rest by "Stationary" alone (0x55e007), which nothing clears for them
            queues[ground].append((0, k, 0, x, partial(_draw_surface, img, p, assets, box, step)))
    for ground in (True, False):
        for *_, draw in sorted(queues[ground], key=lambda q: q[:4]):
            draw()
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    if polygons:
        draw_polygons(out, level, box, step, polygons)
    if overlays:
        draw_overlays(out, level, box, step, overlays, bounds)
    return out


# Outline colours of the polygon classes, as the editor (zaxeditor.scene.POLY_COLORS)
POLYGON_COLORS = {
    'CFreeRangePoly': (0, 230, 255),
    'CWayPointsPolygon': (80, 255, 80),
    'CRenderablePolygon': (255, 170, 0),
}


def _to_image(box, step):
    x0, y0 = box[0], box[1]
    return lambda pts: [((px - x0) / step, (py - y0) / step) for px, py in pts]


def draw_polygons(image: Image.Image, level: Level, box, step: int, classes) -> None:
    """Outlines of the polygon parts of ``classes`` (closed, 1 pixel, the editor's colours)."""
    conv = _to_image(box, step)
    d = ImageDraw.Draw(image)
    for p in level.parts:
        if p.cls not in classes or p.position is not None:
            continue
        pts = p.polygon
        if not pts or len(pts) < 2:
            continue
        xy = conv(pts)
        if xy[0] != xy[-1]:
            xy.append(xy[0])
        d.line(xy, fill=POLYGON_COLORS.get(p.cls, (255, 255, 255)), width=1)


def draw_overlays(image: Image.Image, level: Level, box, step: int, groups, bounds=None) -> None:
    """The AI overlays (zaxtools.overlays) of all objects drawn in the game, for ``groups``; texts in
    PIL's default font (the editor uses the game's)."""
    from . import overlays as ov
    conv = _to_image(box, step)
    d = ImageDraw.Draw(image)
    geo = ov.Geometry(level, bounds)
    for p in level.parts:
        if not ov.has_overlay(p):
            continue
        for s in ov.part_shapes(geo, p, set(groups)):
            xy = conv(s.points)
            if s.text:
                d.text(xy[0], s.text, fill=s.color)
            elif len(xy) >= 2:
                d.line(xy, fill=s.color, width=1)


def content_box(level: Level, margin: int = 300):
    """Area that contains all objects (to cut off empty margins)."""
    pts = [p.position for p in level.parts if p.position]
    if not pts:
        return (0, 0, *level.size)
    W, H = level.size
    xs, ys = zip(*pts)
    return (max(0, int(min(xs)) - margin), max(0, int(min(ys)) - margin),
            min(W, int(max(xs)) + margin), min(H, int(max(ys)) + margin))
