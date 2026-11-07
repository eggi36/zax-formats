"""Regenerate the mini map of a level (``Cache/Levels/<Partial File Name>.frm16``).

The mini map is a scaled-down, darkened image of the level with objects, 176 x 121 pixels,
16 bit. World -> mini map: ``px = x * MiniMap X Scale + MiniMap X Offset`` (Y likewise);
outside the level and in the clipped margins (``Left/Top/Right/Bottom Mini-Map Clipping``,
world pixels from the respective edge, "UnClipped" = 0) it is dark blue [verified: position and
margin match the original mini maps of 01 Main, 03 Intelligence Main and 04 Sacrifice Main]. The
mapping is taken over unchanged from the level, because the game also places the player marker
with it. If the level stores Scale 0, the game computes it itself when loading;
``game_mapping`` computes it the same way.

Since 2026-10-29 the editor draws the mini map the way the game does (``render_game_minimap``, port of
Map_SetupMiniMap 0x4ed150, below): 98 % of the pixels of the 112 shipped mini maps equal (median 99.2 % per level, with the
models' "Sorting Y" from the catalogue) (tools/selftest.py). The darkening the older drawing (``render_minimap``) imitated with
``GAIN`` comes from the game's resampler, which works on 5/6/5-bit channels shifted up without filling the
low bits (31 becomes 248 and comes back as 30) in each of its two passes.
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter

from . import frm
from .level import Level
from .render import Assets, render_level

SIZE = (176, 121)                 # width, height [verified on all mini maps]
BORDER = (0, 24, 41)              # margin colour (RGB565 0x00C5) [verified]
BORDER_INDEX = 0x80               # margin colour in the 8-bit mini map [verified]
GAIN = (0.89, 0.92, 0.82)
MAX_ZOOM = 12                     # Rules.txt, HUD Options: Max Zoom Factor [geprueft]


def _num(level: Level, key: str) -> float:
    v = level.root.get(key, '0')
    try:
        return float(v)
    except ValueError:            # "Left UnClipped" etc.
        return 0.0


def game_mapping(box: tuple, zoom: float = MAX_ZOOM, size: tuple = SIZE) -> tuple:
    """(X Scale, X Offset, Y Scale, Y Offset) as the game computes them for Scale 0
    [confirmed: Zax.exe 0x4ec280/0x4ec3c0; verified: all 42 original mini maps with Scale 0 lie
    exactly in the rectangle computed this way]. ``box`` = visible area (x0, y0, x1, y1).
    Area / ``zoom`` (truncated), then shrunk to at most ``size``, never enlarged (small levels
    at most 1:12), centred."""
    x0, y0, x1, y1 = (int(v) for v in box)
    bw, bh = x1 - x0, y1 - y0
    w, h = size
    ws, hs = int(bw / zoom), int(bh / zoom)
    s = 1.0
    if hs > h:
        s = h / hs
    if ws * s > w:
        s = w / ws
    wn, hn = int(ws * s), int(hs * s)
    left, top = (w - wn) // 2, (h - hn) // 2
    sx, sy = wn / bw, hn / bh
    return sx, left - x0 * sx, sy, top - y0 * sy


def mapping(level: Level) -> dict:
    """Mapping and visible world area from the level fields. ``stored`` is False if the level
    stores no mapping (Scale 0, 42 of 112 levels: caves, temples, TargDens, multiplayer); then
    the mapping the game computes itself applies (``game_mapping``). The level itself is not
    changed."""
    W, H = level.size
    m = {k: _num(level, f'MiniMap {k}') for k in ('X Scale', 'X Offset', 'Y Scale', 'Y Offset')}
    m['box'] = (_num(level, 'Left Mini-Map Clipping'), _num(level, 'Top Mini-Map Clipping'),
                W - _num(level, 'Right Mini-Map Clipping'), H - _num(level, 'Bottom Mini-Map Clipping'))
    m['stored'] = m['X Scale'] != 0 and m['Y Scale'] != 0
    x0, y0, x1, y1 = m['box']
    if not m['stored'] and x1 - x0 >= MAX_ZOOM and y1 - y0 >= MAX_ZOOM:
        m['X Scale'], m['X Offset'], m['Y Scale'], m['Y Offset'] = game_mapping(m['box'])
    return m


def can_render(level: Level) -> bool:
    """Whether the game's drawing has an image rectangle and a visible area (otherwise only margin)."""
    x0, y0, x1, y1 = image_rect(level)
    sl, st, sr, sb = visible_area(level)
    return x1 > x0 and y1 > y0 and sr > sl and sb > st


def render_minimap(level: Level, assets: Assets, step: int = 4) -> np.ndarray:
    """The editor's older approximation (box filter, blur, ``GAIN``; before 2026-10-29): RGB (121, 176, 3)
    uint8, placed by the level's stored mapping. ValueError without a mapping."""
    return _render(level, assets, step)[0]


def _render(level: Level, assets: Assets, step: int = 4):
    """(RGB image, mask "inside the visible area")."""
    m = mapping(level)
    if not (m['X Scale'] > 0 and m['Y Scale'] > 0):
        raise ValueError('no mini map mapping (visible area empty)')
    sx, ox, sy, oy = m['X Scale'], m['X Offset'], m['Y Scale'], m['Y Offset']
    w, h = SIZE
    out = np.empty((h, w, 3), np.uint8)
    out[:] = BORDER
    W, H = level.size
    big = render_level(level, assets, box=(0, 0, W, H), step=step)
    small = big.resize((max(1, round(W * sx)), max(1, round(H * sy))), Image.BOX)
    small = np.asarray(small.filter(ImageFilter.GaussianBlur(0.4)), np.float32)
    py, px = np.mgrid[0:h, 0:w]
    wx, wy = (px + 0.5 - ox) / sx, (py + 0.5 - oy) / sy
    x0, y0, x1, y1 = m['box']
    inside = (wx >= x0) & (wy >= y0) & (wx < x1) & (wy < y1)
    ix = np.clip((wx * sx).astype(int), 0, small.shape[1] - 1)
    iy = np.clip((wy * sy).astype(int), 0, small.shape[0] - 1)
    col = np.clip(small[iy, ix] * np.array(GAIN, np.float32), 0, 255).astype(np.uint8)
    out[inside] = col[inside]
    return out, inside


def minimap_files(level: Level, assets: Assets, palette: np.ndarray) -> dict[str, bytes]:
    """Both mini maps, {path relative to Data/: content}, drawn as the game draws them
    (``render_game_minimap``). With 16-bit colour depth the game takes the .frm16, with 256 colours the
    .frm [information from the user; both verified in the game]. 8 bit: nearest palette colour
    (GamePalette) of the 16-bit image, margin = index 0x80 as in all originals [assumption: the game's
    8-bit path renders with the palette and dithers (0x43bad0); not ported]."""
    px = render_game_minimap(level, assets)
    rgb = frm.rgb565_to_rgb(px)
    x0, y0, x1, y1 = image_rect(level)
    inside = np.zeros(px.shape, bool)
    inside[y0:y1, x0:x1] = True
    idx = frm.nearest_index(rgb, palette)
    idx[~inside] = BORDER_INDEX
    base = minimap_path(level)[:-len('.frm16')]
    return {base + '.frm16': frm.encode_raw16(rgb), base + '.frm': frm.encode_rle8(idx)}


def minimap_frm16(level: Level, assets: Assets) -> bytes:
    return frm.encode_raw16(render_minimap(level, assets))


def minimap_path(level: Level) -> str:
    """Path relative to Data/: ``Cache/Levels/<Partial File Name>.frm16``."""
    return f'Cache/Levels/{level.partial_file_name}.frm16'


# --- Let the game draw the mini map --------------------------------------------------------------
#
# Map_LoadMiniMap (0x4ece20) rebuilds the mini map from the level when the cached image is missing
# or not exactly the mini map size and the level's folder exists on the disk; it then writes
# Levels/<folder>/-<name>.tga and the cache image itself (FORMATS.md, mini maps). The game reads
# a file on the disk below DATA/ before the same name in Data.dat (FORMATS.md 1), so an older
# mini map - the shipped one in Data.dat or an unpacked DATA/, or one copied there earlier - would
# still be found if the editor only deleted its own. A placeholder of the wrong size covers it.

PLACEHOLDER_SIZE = (1, 1)          # anything but SIZE makes the game redraw the mini map


def game_files(level: Level) -> list[str]:
    """Files of the level's mini map relative to Data/: the cached images and the .tga the game
    writes when it draws the mini map itself."""
    base = minimap_path(level)[:-len('.frm16')]
    pfn = level.partial_file_name
    folder, _, name = pfn.rpartition('/')
    tga = f'Levels/{folder}/-{name}.tga' if folder else f'Levels/-{name}.tga'
    return [base + '.frm16', base + '.frm', tga]


def placeholder_files(level: Level) -> dict[str, bytes]:
    """{path relative to Data/: content}: a 1 x 1 .frm16 and .frm in the margin colour. The game
    loads them, finds the wrong size and draws the mini map from the level, writing its own
    images over them."""
    w, h = PLACEHOLDER_SIZE
    rgb = np.empty((h, w, 3), np.uint8)
    rgb[:] = BORDER
    base = minimap_path(level)[:-len('.frm16')]
    return {base + '.frm16': frm.encode_raw16(rgb),
            base + '.frm': frm.encode_rle8(np.full((h, w), BORDER_INDEX, np.uint8))}


# --- The mini map the way the game draws it ----------------------------------------------------------
#
# Map_SetupMiniMap (0x4ed150) [confirmed: code, zax-decomp/reimpl/src/world_c5.cpp; compared with the shipped mini
# maps, tools/selftest.py]: the whole level is rendered into a frame of the level's size (World::RenderLayer
# 0x4f4ae0: every visible active part, without the characters and the parts of the category "Top Hide",
# 0x4ed2b0), the mini map frame is cleared to "MiniMap Background Color", and the visible area (the level
# without the four clipping margins) is resampled into the image rectangle (0x4ec280, ``image_rect``) by
# the "Filter" blit mode (CBlendFilter 0x6b9ca0: a Mitchell-Netravali cubic, rows then columns, through
# 5/6/5-bit channels; zax-decomp/reimpl/src/blitters_filter.cpp). The 16-bit frame is the .frm16 the game saves
# (0x4ec600), whatever mapping the level stores (the image rectangle does not use it).

CHARACTER_CLASSES = {'CEntityCharacter', 'CEntityFlying', 'CEntityOm', 'CEntityOverlayWalking',
                     'CEntityStationaryCharacter', 'CEntityWalking'}      # CEntityCharacter 0x49a930 and below
TOP_HIDE = 'top hide'                                                  # the category 0x617f90
BACKGROUND565 = 0x00c5            # "MiniMap Background Color" 0,24,44 in RGB565 [verified: all shipped maps]


def _f32(v: float) -> float:
    return float(np.float32(v))


def image_rect(level: Level, zoom: float = MAX_ZOOM, size: tuple = SIZE) -> tuple[int, int, int, int]:
    """0x4ec280: the rectangle (left, top, right, bottom) of the mini map the visible area is scaled into:
    its size divided by the zoom (truncated), shrunk to fit ``size`` (the width test on the factor the
    height test left, as floats), truncated and centred (halving towards 0)."""
    W, H = level.size
    l, t = int(_num(level, 'Left Mini-Map Clipping')), int(_num(level, 'Top Mini-Map Clipping'))
    r, b = W - int(_num(level, 'Right Mini-Map Clipping')), H - int(_num(level, 'Bottom Mini-Map Clipping'))
    zf = _f32(zoom)
    ih = int((b - t) / zf)
    iw = int((r - l) / zf)
    s = 1.0
    if ih > size[1]:
        s = size[1] / ih
    wf, sxf = _f32(iw), _f32(size[0])
    if not wf * s <= sxf:
        s = sxf / wf
    h2, w2 = int(ih * s), int(iw * s)
    ypad, xpad = int((size[1] - h2) / 2), int((size[0] - w2) / 2)
    return xpad, ypad, w2 + xpad, h2 + ypad


def visible_area(level: Level) -> tuple[int, int, int, int]:
    """The source rectangle of 0x4ed150: the level without the clipping margins."""
    W, H = level.size
    return (int(_num(level, 'Left Mini-Map Clipping')), int(_num(level, 'Top Mini-Map Clipping')),
            W - int(_num(level, 'Right Mini-Map Clipping')), H - int(_num(level, 'Bottom Mini-Map Clipping')))


def shown_on_minimap(part) -> bool:
    """0x4ed2b0 inverted: RenderLayer hides characters and the category "Top Hide"."""
    if part.cls in CHARACTER_CLASSES:
        return False
    cats = [c.strip().lower() for c in (part.get('Category') or '').split(',')]
    return TOP_HIDE not in cats


class _Shown(Level):
    """The level with only the parts RenderLayer draws (the text tree is shared, nothing is changed)."""

    def __init__(self, level: Level):
        self.doc, self.root = level.doc, level.root

    @property
    def parts(self):
        return [p for p in super().parts if shown_on_minimap(p)]


# The cubic and the channel tables of CBlendFilter (float constants of the exe)
_K7, _KM12, _K16_3, _K6 = 7.0, -12.0, _f32(16 / 3), _f32(1 / 6)
_KM7_3, _K12, _KM20, _K32_3 = _f32(-7 / 3), 12.0, -20.0, _f32(32 / 3)
_C31_255, _C63_255 = _f32(31 / 255), _f32(63 / 255)


def _kernel(t: float) -> float:
    t2 = t * t
    if t < 0:
        t = -t
    if t < 1.0:
        t3 = t * t2
        return (t3 * _K7 + t2 * _KM12 + _K16_3) * _K6
    if t < 2.0:
        a = t2 * t * _KM7_3
        s = a + t2 * _K12
        return (s + t * _KM20 + _K32_3) * _K6
    return 0.0


def _taps(n_in: int, n_out: int, scale: float):
    """0x43ae70/0x43b260: per output pixel the source indices (mirrored at the edges) and float weights,
    as an index and a weight matrix padded with weight 0 (adding 0.0 leaves a sum unchanged)."""
    import math
    inv = _f32(1.0 / scale)
    down = scale < 1.0
    radius = _f32(inv + inv) if down else 0.0
    lists = []
    for i in range(n_out):
        c80 = i * inv
        centre = _f32(c80)
        if down:
            lo = int(_f32(math.ceil(c80 - radius)))
            hi = int(math.floor(centre + radius))
        else:
            lo = int(_f32(math.ceil(centre - 2.0)))
            hi = int(math.floor(centre + 2.0))
        taps = []
        for j in range(lo, hi + 1):
            t = centre - j
            if down:
                t = t * scale
            w = _kernel(t)
            if down:
                w = w * scale
            idx = -j if j < 0 else (j if j < n_in else n_in * 2 - j - 1)
            taps.append((idx, _f32(w)))
        lists.append(taps)
    k = max(len(t) for t in lists)
    index = np.zeros((n_out, k), np.int64)
    weight = np.zeros((n_out, k), np.float64)
    for i, taps in enumerate(lists):
        for j, (ix, w) in enumerate(taps):
            index[i, j], weight[i, j] = ix, w
    return index, weight


def _tables():
    v = np.arange(-128, 384, dtype=np.float64)
    b = v * _C31_255 + 0.5
    b = np.where(b < 0, 0.0, np.where(b <= 31.0, b, 31.0)).astype(np.int64)
    g = v * _C63_255 + 0.5
    g = np.where(g < 0, 0.0, np.where(g <= 63.0, g, 63.0)).astype(np.int64)
    return b, g << 5, b << 11


_T_BLUE, _T_GREEN, _T_RED = _tables()


def _unpack(px: np.ndarray):
    p = px.astype(np.int64)
    return ((p << 3) & 0xff).astype(np.float64), (((p >> 5) << 2) & 0xff).astype(np.float64), ((p >> 8) & 0xf8).astype(np.float64)


def _pass(px: np.ndarray, index: np.ndarray, weight: np.ndarray) -> np.ndarray:
    """One pass of 0x43b650 along the last axis: the weighted sums in tap order (x87 with 53 bits: every
    product and sum rounded to a double), then the tables at trunc(sum + 128.5)."""
    b, g, r = _unpack(px)
    sb = np.zeros(px.shape[:-1] + (index.shape[0],))
    sg, sr = sb.copy(), sb.copy()
    for k in range(index.shape[1]):
        ix, w = index[:, k], weight[:, k]
        sr = sr + r[..., ix] * w
        sg = sg + g[..., ix] * w
        sb = sb + b[..., ix] * w
    tb = _T_BLUE[np.clip((sb + 128.5).astype(np.int64), 0, 511)]
    tg = _T_GREEN[np.clip((sg + 128.5).astype(np.int64), 0, 511)]
    tr = _T_RED[np.clip((sr + 128.5).astype(np.int64), 0, 511)]
    return ((tb + tg + tr) & 0xffff).astype(np.uint16)


def filter_resample(src565: np.ndarray, w_out: int, h_out: int) -> np.ndarray:
    """CBlendFilter (0x43bd10 -> 0x43b650): a 16-bit image resampled to w_out x h_out, rows first."""
    h_in, w_in = src565.shape
    sx = _f32(w_out / w_in)
    sy = _f32(h_out / h_in)
    ix, wx = _taps(w_in, w_out, sx)
    mid = _pass(src565, ix, wx)                    # (h_in, w_out)
    iy, wy = _taps(h_in, h_out, sy)
    return _pass(mid.T, iy, wy).T                  # (h_out, w_out)


def render_game_minimap(level: Level, assets: Assets, zoom: float = MAX_ZOOM) -> np.ndarray:
    """The mini map as the game draws it (Map_SetupMiniMap 0x4ed150): RGB565 (121, 176) uint16. The level
    rendering is zaxtools.render's (render.py lists its deviations from the game)."""
    w, h = SIZE
    out = np.full((h, w), BACKGROUND565, np.uint16)
    x0, y0, x1, y1 = image_rect(level, zoom)
    sl, st, sr, sb = visible_area(level)
    if x1 <= x0 or y1 <= y0 or sr <= sl or sb <= st:
        return out
    img = render_level(_Shown(level), assets, box=(sl, st, sr, sb), step=1)
    src = frm.rgb_to_rgb565(np.asarray(img))
    out[y0:y1, x0:x1] = filter_resample(src, x1 - x0, y1 - y0)
    return out
