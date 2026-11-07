"""Single images (.frm = 256 colours, .frm16 = 16-bit RGB565).

Header (36 bytes, little-endian):
    +0  u8  0x31          type signature
    +1  u8  bits/pixel    8 or 16 (also frm24/frm32 according to Zax.exe, never seen)
    +2  i16 hot spot x    (0 in .frm files; the anchor point in model frames)
    +4  i16 hot spot y
    +6  u16 width
    +8  u16 height
    +10 u16 not written by the exe (stack bytes; 18 in most files)
    +12 u16 flags         0x20/0x40 raw (8/16 bit), 0x2022/0x2044 RLE (bit 0x2000)
    +14 u16 the flags' high word (always 0)
    +16 u32 size of the pixel block
    +20 u32 size of the extra block  (8 bit: the pixels with alpha 25-76)
    +24 u32 size of the block +24    (8 bit: alpha 76-127)
    +28 u32 size of the alpha block  (8 bit: alpha 127-178; 16 bit: one alpha byte per edge entry)
    +32 u32 size of the edge block   (8 bit: alpha 178-229; 16 bit: alpha 6-250)
Then the pixel block; with RLE a row table follows (height x u32, offsets into the block). With
RLE the block itself starts with its size (u32).

RLE per row, control byte c:
    c < 0x40         repeat: (c & 0x3f) pixels with the following value
    0x40 <= c < 0x80 literals: (c & 0x3f) single values follow
    c >= 0x80        (c & 0x7f) transparent pixels, no data
A value is 1 byte (palette index) or 2 bytes (RGB565).

The palette of the 8-bit files is Data/Palettes/GamePalette.pal (256 x B,G,R).

Encoder (encode16, encode8, encode_raw): the game's own TGA -> frame compiler; decoding a file and
encoding its values gives the file byte for byte (all frames of the game data, docs/FORMATS.md 5).
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

import numpy as np

HEADER = 36


@dataclass
class FrameHeader:
    bpp: int
    hot_x: int
    hot_y: int
    width: int
    height: int
    flags: int
    size: int
    extra20_size: int      # 8-bit frames with alpha: the pixels with alpha 25-76
    extra24_size: int      # 8-bit frames with alpha: the pixels with alpha 76-127
    alpha_size: int
    edge_size: int

    @property
    def rle(self) -> bool:
        return bool(self.flags & 0x2000)


def read_header(d: bytes, off: int = 0) -> FrameHeader:
    t, bpp, hx, hy, w, h, _, flags, _ = struct.unpack_from('<BBhhHHHHH', d, off)
    if t != 0x31:
        raise ValueError('Kein Frame-Kopf an Offset %d' % off)
    size, e20, e24, asz, esz = struct.unpack_from('<5I', d, off + 16)
    return FrameHeader(bpp, hx, hy, w, h, flags, size, e20, e24, asz, esz)


def rgb565_to_rgb(a: np.ndarray) -> np.ndarray:
    a = a.astype(np.uint32)
    return np.dstack([(a >> 11 & 31) * 255 // 31,
                      (a >> 5 & 63) * 255 // 63,
                      (a & 31) * 255 // 31]).astype(np.uint8)


def decode_rle(blk: bytes, table, w: int, h: int, bytes_per_value: int):
    """Decode an RLE block -> (values (h,w), opaque mask (h,w))."""
    dtype = np.uint8 if bytes_per_value == 1 else np.dtype('<u2')
    vals = np.zeros((h, w), dtype)
    opaque = np.zeros((h, w), bool)
    ends = list(table[1:]) + [len(blk)]
    for y in range(h):
        p, e, x = table[y], ends[y], 0
        while p < e and x < w:
            c = blk[p]
            p += 1
            n = c & 0x3f
            if c < 0x40:
                v = blk[p] if bytes_per_value == 1 else struct.unpack_from('<H', blk, p)[0]
                vals[y, x:x + n] = v
                opaque[y, x:x + n] = True
                p += bytes_per_value
            elif c < 0x80:
                vals[y, x:x + n] = np.frombuffer(blk[p:p + n * bytes_per_value], dtype)
                opaque[y, x:x + n] = True
                p += n * bytes_per_value
            else:
                n = c & 0x7f
            x += n
        if x != w:
            raise ValueError(f'RLE-Zeile {y}: {x} statt {w} Pixel')
    return vals, opaque


def decode(d: bytes, off: int = 0, palette: np.ndarray | None = None):
    """Decode the frame at ``off``.

    Returns: (RGBA image (h,w,4) uint8, FrameHeader, end offset).
    8-bit frames need ``palette`` (256x3 RGB).
    Alpha/edge layers (16 bit) are applied as well; an 8-bit RLE frame's five blocks as the 256-colour
    mode's opacity steps (``_decode_rle8``).
    """
    hd = read_header(d, off)
    w, h, bpv = hd.width, hd.height, hd.bpp // 8
    if hd.rle and bpv == 1:
        return _decode_rle8(d, off, palette)
    start = off + HEADER
    blk = d[start:start + hd.size]
    if hd.rle:
        table = struct.unpack_from('<%dI' % h, d, start + hd.size)
        vals, opaque = decode_rle(blk, table, w, h, bpv)
        end = start + hd.size + 4 * h
    else:
        dtype = np.uint8 if bpv == 1 else np.dtype('<u2')
        vals = np.frombuffer(blk[:w * h * bpv], dtype).reshape(h, w)
        opaque = np.ones((h, w), bool)
        end = start + hd.size
        if len(d) - end == 4 * h:      # .frm files have a row table here too
            end += 4 * h
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., :3] = _to_rgb(vals, bpv, palette)
    rgba[..., 3] = opaque * 255
    for extra in (hd.extra20_size, hd.extra24_size):
        if extra:                      # skip block + row table
            end += extra + 4 * h
    if hd.alpha_size and hd.edge_size:
        ablk = d[end:end + hd.alpha_size]
        atab = struct.unpack_from('<%dI' % h, d, end + hd.alpha_size)
        end += hd.alpha_size + 4 * h
        eblk = d[end:end + hd.edge_size]
        etab = struct.unpack_from('<%dI' % h, d, end + hd.edge_size)
        end += hd.edge_size + 4 * h
        evals, eop = decode_rle(eblk, etab, w, h, bpv)
        ecol = _to_rgb(evals, bpv, palette)
        alpha = _edge_alpha(eblk, etab, ablk, atab, w, h, bpv)
        rgba[eop, :3] = ecol[eop]
        rgba[eop, 3] = alpha[eop]
    else:                              # only one of the blocks (8-bit frames in .seq): skip
        for extra in (hd.alpha_size, hd.edge_size):
            if extra:
                end += extra + 4 * h
    return rgba, hd, end


# The opacity (0..255) the 256-colour mode draws each block of an 8-bit RLE frame with, in the drawing order
# pixel, edge (+32), alpha (+28), +24, +20 [confirmed: code Rle8_DrawFull_Copy 0x43e380 / _DrawClipped_Copy
# 0x43dbe0 at level 0 (a draw at full opacity): the pixel block with the copy spans T0/T1, the edge block with
# T2/T3 (Alpha20_80 [dst * 256 + src]), the alpha block T4/T5 (Alpha40_60 [dst * 256 + src]), the +24 block
# T6/T7 (Alpha40_60 [src * 256 + dst]) and the +20 block through the row 0x43ea00 with T8/T9 (Alpha20_80
# [src * 256 + dst]); a table row r of factor k is nearest(r * k + c * (1 - k)) (FillGammaTable 0x527420),
# InitBlendTables 0x433000 builds Alpha20_80 with 0.2 and Alpha40_60 with 0.4; zax-decomp/reimpl/src/rle8.cpp,
# spans8.h, palette_rest4b.cpp, image_lo4.cpp]. So the source weighs 1, 0.8, 0.6, 0.4, 0.2; the game takes the
# nearest palette entry of each blend, a preview blends in RGB. A draw with opacity below 1 shifts the blocks
# down these steps (docs/FORMATS.md 5), which a preview of the frame itself does not need.
OPACITY8 = (255, 204, 153, 102, 51)


def _decode_rle8(d: bytes, off: int, palette: np.ndarray | None):
    """decode for an 8-bit RLE frame: all five blocks drawn over each other in the game's order, each with its
    OPACITY8 step (a pixel in one block only gets that opacity and its palette colour exactly)."""
    hd, bl, end = blocks(d, off)
    h, w = hd.height, hd.width
    if palette is None:
        raise ValueError('8-bit frame needs a palette')
    rgb = np.zeros((h, w, 3), np.float64)          # premultiplied
    a = np.zeros((h, w), np.float64)
    for b, op in zip((bl[0], bl[4], bl[3], bl[2], bl[1]), OPACITY8):
        if b is None:
            continue
        vals, m = b
        k = op / 255.0
        rgb[m] = palette[vals[m]] * k + rgb[m] * (1 - k)
        a[m] = k + a[m] * (1 - k)
    rgba = np.zeros((h, w, 4), np.uint8)
    nz = a > 0
    rgba[nz, :3] = np.clip(np.rint(rgb[nz] / a[nz, None]), 0, 255).astype(np.uint8)
    rgba[..., 3] = np.rint(a * 255).astype(np.uint8)
    return rgba, hd, end


@dataclass
class Layers16:
    """The blocks of a 16-bit frame as Zax.exe draws them (FORMATS.md 6, exact arithmetic):
    ``pix``/``pix_mask`` the pixel block (RGB565, copied), ``edge``/``edge_mask``/``alpha`` the
    edge block with its weights, ``span_start``/``span_len`` per edge pixel the column range of
    its RLE entry (the span the game blends in one call; -1/0 elsewhere)."""
    pix: np.ndarray
    pix_mask: np.ndarray
    edge: np.ndarray
    edge_mask: np.ndarray
    alpha: np.ndarray
    span_start: np.ndarray
    span_len: np.ndarray


def layers16(d: bytes, off: int = 0) -> Layers16 | None:
    """The blocks of the 16-bit frame at ``off`` (None for other frames)."""
    hd = read_header(d, off)
    w, h = hd.width, hd.height
    if hd.bpp != 16:
        return None
    start = off + HEADER
    blk = d[start:start + hd.size]
    if hd.rle:
        table = struct.unpack_from('<%dI' % h, d, start + hd.size)
        pix, pmask = decode_rle(blk, table, w, h, 2)
        end = start + hd.size + 4 * h
    else:
        pix = np.frombuffer(blk[:w * h * 2], '<u2').reshape(h, w).copy()
        pmask = np.ones((h, w), bool)
        end = start + hd.size
    for extra in (hd.extra20_size, hd.extra24_size):
        if extra:
            end += extra + 4 * h
    edge = np.zeros((h, w), np.uint16)
    emask = np.zeros((h, w), bool)
    alpha = np.zeros((h, w), np.uint8)
    s0 = np.full((h, w), -1, np.int16)
    sn = np.zeros((h, w), np.int16)
    if hd.rle and hd.alpha_size and hd.edge_size:
        ablk = d[end:end + hd.alpha_size]
        atab = struct.unpack_from('<%dI' % h, d, end + hd.alpha_size)
        end += hd.alpha_size + 4 * h
        eblk = d[end:end + hd.edge_size]
        etab = struct.unpack_from('<%dI' % h, d, end + hd.edge_size)
        edge, emask = decode_rle(eblk, etab, w, h, 2)
        alpha = _edge_alpha(eblk, etab, ablk, atab, w, h, 2)
        ends = list(etab[1:]) + [len(eblk)]
        for y in range(h):
            p, e, x = etab[y], ends[y], 0
            while p < e and x < w:
                c = eblk[p]
                p += 1
                if c >= 0x80:
                    x += c & 0x7f
                    continue
                n = c & 0x3f
                p += 2 if c < 0x40 else 2 * n
                s0[y, x:x + n] = x
                sn[y, x:x + n] = n
                x += n
    return Layers16(pix, pmask, edge, emask, alpha, s0, sn)


def _edge_alpha(eblk: bytes, etab, ablk: bytes, atab, w: int, h: int, bpv: int) -> np.ndarray:
    """Opacity of the edge pixels. Model frames: one byte per RLE entry of the edge block, i.e. one
    per single value and one for a whole run of equal pixels (shadows: the inside is one run)
    [verified: the number of bytes per row matches in all 49,142 model frames]. If the count does
    not match (some images/image sequences outside the models), the alpha block is an RLE image
    of its own with 1-byte values [verified on the 4 affected files]."""
    alpha = np.zeros((h, w), np.uint8)
    eends = list(etab[1:]) + [len(eblk)]
    aends = list(atab[1:]) + [len(ablk)]
    for y in range(h):
        p, e, x, q = etab[y], eends[y], 0, atab[y]
        while p < e and x < w:
            c = eblk[p]
            p += 1
            if c < 0x40:
                if q < aends[y]:
                    alpha[y, x:x + (c & 0x3f)] = ablk[q]
                q += 1
                p += bpv
                x += c & 0x3f
            elif c < 0x80:
                n = c & 0x3f
                av = np.frombuffer(ablk[q:min(q + n, aends[y])], np.uint8)
                alpha[y, x:x + len(av)] = av
                q += n
                p += n * bpv
                x += n
            else:
                x += c & 0x7f
        if q != aends[y]:
            return decode_rle(ablk, atab, w, h, 1)[0]
    return alpha


def _to_rgb(vals, bpv, palette):
    if bpv == 2:
        return rgb565_to_rgb(vals)
    if palette is None:
        raise ValueError('8-bit frame needs a palette')
    return palette[vals]


def rgb_to_rgb565(rgb: np.ndarray) -> np.ndarray:
    """Inverse of rgb565_to_rgb (lossless for its outputs)."""
    c = rgb.astype(np.float64)
    r = np.clip(np.rint(c[..., 0] * 31 / 255), 0, 31).astype(np.uint16)
    g = np.clip(np.rint(c[..., 1] * 63 / 255), 0, 63).astype(np.uint16)
    b = np.clip(np.rint(c[..., 2] * 31 / 255), 0, 31).astype(np.uint16)
    return (r << 11) | (g << 5) | b


def encode_raw16(rgb: np.ndarray, field10: int = 18) -> bytes:
    """Uncompressed 16-bit image (.frm16, flags 0x40) from RGB like the mini maps (encode_raw)
    [verified on all 112 mini maps]. ``field10``: header +10 (stack bytes the exe never writes; 18 for
    textures and RLE mini maps)."""
    return encode_raw(rgb_to_rgb565(rgb), field10=field10)


def encode_rle8(idx: np.ndarray, field10: int = 18, opaque: np.ndarray | None = None) -> bytes:
    """8-bit image (palette indices) RLE-encoded as the game does (encode8; flags 0x2022), e.g. the
    8-bit mini maps. ``opaque`` (optional): False = transparent (cave mini maps use that for empty
    areas); every other pixel stays opaque, index 0 too."""
    idx = np.asarray(idx, np.uint8)
    alpha = np.full(idx.shape, 255, np.uint8) if opaque is None else np.where(opaque, 255, 0).astype(np.uint8)
    return encode8(idx, alpha, field10=field10)


def nearest_index(rgb: np.ndarray, palette: np.ndarray) -> np.ndarray:
    """Per pixel the index of the nearest palette colour (Euclidean in RGB)."""
    flat = rgb.reshape(-1, 3).astype(np.int32)
    pal = palette.astype(np.int32)
    out = np.empty(len(flat), np.uint8)
    for i in range(0, len(flat), 4096):
        d = ((flat[i:i + 4096, None, :] - pal[None, :, :]) ** 2).sum(-1)
        out[i:i + 4096] = d.argmin(-1)
    return out.reshape(rgb.shape[:2])


def load_palette(data: bytes) -> np.ndarray:
    """GamePalette.pal: 256 entries of 3 bytes each in the order B, G, R."""
    return np.frombuffer(data[:768], np.uint8).reshape(256, 3)[:, ::-1].copy()


# ---- Encoder: the game's TGA -> frame compiler -------------------------------------------------------------
# Ported from Zax.exe [confirmed: code, zax-decomp/reimpl/src/frame_load_rle.cpp, frame_load_convert.cpp,
# frame_rest4a.cpp]: the RLE filter FrameFilterRle::Apply 0x4afd40 (32-bit sources: RleEncode_Frame8 0x4aef00
# or RleEncode_Frame16 0x4af690; 8/16-bit sources: RleEncode_Bytes 0x4b16d0 / RleEncode_Words 0x4b18b0),
# then the depth conversion (FrameConvert_To8 0x4ad1e0 / _To16 0x4ad920), written by CFrame::WriteFrm
# 0x4a9740. Since the encoder compares pixels only through equivalence keys (the nearest palette index, the
# 5-6-5 pixel, alpha >> 3) and stores a run's first pixel, encoding the decoded values of a file gives the
# file again (docs/FORMATS.md 5, "Encoder").

ALPHA_BANDS8 = ((229, 255), (178, 229), (127, 178), (76, 127), (25, 76))   # (lo, hi]: pixel, edge, alpha, +24, +20
ALPHA_BANDS16 = ((250, 255), (5, 250))                                      # (lo, hi]: pixel, edge (+ alpha)


def _encode_row(vals: list, clear, run) -> tuple[bytes, list]:
    """One row as RleEncode's row encoder (reimpl encode_row): up to 0x7f clear pixels as a skip code; the
    non-clear stretch after it as runs (more than 8 equal pixels, at most 63) and literals (a literal ends
    at 63 pixels or before 8 equal ones). ``vals`` the stored bytes per pixel, ``clear`` per pixel,
    ``run[i]`` the number of equal pixels from i on (the probe; 0 everywhere = only literals).
    Returns the row's bytes and the stored pixel index of every entry (for the alpha block)."""
    out, entries, w, x = bytearray(), [], len(vals), 0
    while x < w:
        c = 0
        while x + c < w and clear[x + c]:
            c += 1
            if c >= 0x7f:
                break
        if c:
            out.append(0x80 | c)
            x += c
        end = x
        while end < w and not clear[end]:
            end += 1
        while x < end:
            rem = end - x
            count = min(run[x], rem, 0x3f)
            if count > 8:
                out.append(count)
                out += vals[x]
                entries.append(x)
                x += count
                continue
            q, k, left = x, 0, rem
            while q < end:
                if q - x >= 0x3f or k >= 8:
                    break
                left -= 1
                q += 1
                k = min(run[q], left, 8) if left > 0 else 0
            out.append(0x40 | (q - x))
            for i in range(x, q):
                out += vals[i]
                entries.append(i)
            x = q
    return bytes(out), entries


def _runs(key: np.ndarray) -> np.ndarray:
    """Per pixel the number of equal keys from it on within the row (the encoder's probe)."""
    h, w = key.shape
    run = np.ones((h, w), np.int32)
    same = key[:, 1:] == key[:, :-1]
    for x in range(w - 2, -1, -1):
        run[:, x] += np.where(same[:, x], run[:, x + 1], 0)
    return run


def _rle_block(vals: np.ndarray, clear: np.ndarray, key: np.ndarray | None,
               alpha: np.ndarray | None = None) -> tuple[bytes, bytes | None]:
    """An RLE block with its row table (u32 size + rows, then height x u32 offsets); with ``alpha`` also
    the alpha block made from it (FrameConvert_RleAlphaFrom32 0x4aeba0: the codes dropped, one alpha byte
    per stored pixel). ``key`` None = the probe RleEncode_RunLengthNone (only literals)."""
    h, w = clear.shape
    bpv = vals.dtype.itemsize
    raw = np.ascontiguousarray(vals.astype('<u2' if bpv == 2 else np.uint8)).tobytes()
    run = _runs(key) if key is not None else np.zeros((h, w), np.int32)
    rows, arows = [], []
    for y in range(h):
        rv = [raw[(y * w + x) * bpv:(y * w + x + 1) * bpv] for x in range(w)]
        r, entries = _encode_row(rv, clear[y].tolist(), run[y].tolist())
        rows.append(r)
        if alpha is not None:
            arows.append(bytes(alpha[y, entries].astype(np.uint8)))

    def pack(rs):
        offs, p = [], 4
        for r in rs:
            offs.append(p)
            p += len(r)
        return struct.pack('<I', p) + b''.join(rs) + struct.pack('<%dI' % h, *offs)
    return pack(rows), (pack(arows) if alpha is not None else None)


def _frame(bpp: int, w: int, h: int, flags: int, hot: tuple[int, int], field10: int, blocks) -> bytes:
    """Header + blocks as CFrame::WriteFrm 0x4a9740: ``blocks`` = (pixel, +20, +24, alpha, edge), each the
    block with its row table or None; a block's size is its first dword (raw frames: the pixel bytes)."""
    sizes = []
    for k, b in enumerate(blocks):
        if b is None:
            sizes.append(0)
        elif flags & 0x2000:
            sizes.append(struct.unpack_from('<I', b)[0])
        else:
            sizes.append(len(b) - 4 * h)
    head = struct.pack('<BBhhHHHI', 0x31, bpp, hot[0], hot[1], w, h, field10, flags)
    return head + struct.pack('<5I', *sizes) + b''.join(b for b in blocks if b is not None)


def encode_raw(pixels: np.ndarray, hot: tuple[int, int] = (0, 0), field10: int = 18) -> bytes:
    """Uncompressed frame (flags 0x20 for uint8 palette indices, 0x40 for uint16 RGB565): the pixels and a
    row table with pixel offsets y * width (CFrame::WriteFrm writes the table of every block; the reader
    fills it with i * width first) [verified: all raw .frm/.frm16]."""
    h, w = pixels.shape
    bpv = pixels.dtype.itemsize
    px = np.ascontiguousarray(pixels.astype('<u2' if bpv == 2 else np.uint8)).tobytes()
    table = struct.pack('<%dI' % h, *[y * w for y in range(h)])
    return _frame(8 * bpv, w, h, 0x20 * bpv, hot, field10, (px + table, None, None, None, None))


def encode16(pixels: np.ndarray, alpha: np.ndarray | None = None, hot: tuple[int, int] = (0, 0),
             field10: int = 18) -> bytes:
    """RLE .frm16 (flags 0x2044) as the game compiles it.

    ``pixels`` (h, w) uint16 RGB565. ``alpha`` (h, w) uint8, or None for a 16-bit source without alpha
    (RleEncode_Words: the pixel 0 is transparent). With alpha (a 32-bit source, RleEncode_Frame16): alpha
    above 250 the pixel block (runs of equal 5-6-5 pixels), 6-250 the edge block (runs of equal 5-6-5
    pixels whose alpha agrees but in the low three bits) and the alpha block with one byte per entry of
    it (a run's first pixel's alpha), alpha 0-5 dropped. ``hot`` the header's hot spot (the negated
    origin), ``field10`` header +10, which the exe never writes (stack bytes; 18 in most files)."""
    pixels = np.asarray(pixels, np.uint16)
    h, w = pixels.shape
    if alpha is None:
        pix, _ = _rle_block(pixels, pixels == 0, pixels)
        return _frame(16, w, h, 0x2044, hot, field10, (pix, None, None, None, None))
    alpha = np.asarray(alpha, np.uint8)
    (plo, phi), (elo, ehi) = ALPHA_BANDS16
    pmask = (alpha > plo) & (alpha <= phi)
    emask = (alpha > elo) & (alpha <= ehi)
    pix, _ = _rle_block(pixels, ~pmask, pixels)
    edge = abl = None
    if emask.any():
        key = pixels.astype(np.int32) << 5 | alpha >> 3
        edge, abl = _rle_block(pixels, ~emask, key, alpha)
    return _frame(16, w, h, 0x2044, hot, field10, (pix, None, None, abl, edge))


def encode8(indices: np.ndarray, alpha: np.ndarray | None = None, hot: tuple[int, int] = (0, 0),
            field10: int = 18) -> bytes:
    """RLE .frm (flags 0x2022) as the game compiles it.

    ``indices`` (h, w) uint8 palette indices. ``alpha`` (h, w) uint8, or None for an 8-bit source without
    alpha (RleEncode_Bytes: index 0 is transparent). With alpha (a 32-bit source, RleEncode_Frame8): five
    blocks by the alpha bands ALPHA_BANDS8 (pixel block above 229, edge 178-229, alpha 127-178, +24
    76-127, +20 25-76, below 25 dropped), each an image of its own with runs of equal indices; an empty
    band other than the pixel block is left out."""
    indices = np.asarray(indices, np.uint8)
    h, w = indices.shape
    if alpha is None:
        pix, _ = _rle_block(indices, indices == 0, indices)
        return _frame(8, w, h, 0x2022, hot, field10, (pix, None, None, None, None))
    alpha = np.asarray(alpha, np.uint8)
    out = []
    for k, (lo, hi) in enumerate(ALPHA_BANDS8):
        m = (alpha > lo) & (alpha <= hi)
        out.append(_rle_block(indices, ~m, indices)[0] if k == 0 or m.any() else None)
    pix, edge, abl, b24, b20 = out
    return _frame(8, w, h, 0x2022, hot, field10, (pix, b20, b24, abl, edge))


def band_alpha8(blocks: list[np.ndarray]) -> np.ndarray:
    """An alpha image for encode8 from the masks of the five 8-bit blocks (pixel, edge, alpha, +24, +20):
    each band's upper bound (255, 229, 178, 127, 76)."""
    alpha = np.zeros(blocks[0].shape, np.uint8)
    for m, (lo, hi) in zip(blocks, ALPHA_BANDS8):
        alpha[m] = hi
    return alpha


def blocks(d: bytes, off: int = 0) -> tuple[FrameHeader, list, int]:
    """The five blocks of a frame decoded each as an image of its own (a raw frame: its pixels): (header, [(values, mask) or
    None for pixel, +20, +24, alpha, edge], end offset). For 16-bit frames the alpha block is not an image
    (one byte per edge entry, see layers16) and comes back as its raw bytes."""
    hd = read_header(d, off)
    w, h, bpv = hd.width, hd.height, hd.bpp // 8
    p = off + HEADER
    out = []
    for k, size in enumerate((hd.size, hd.extra20_size, hd.extra24_size, hd.alpha_size, hd.edge_size)):
        if not size:
            out.append(None)
            continue
        blk = d[p:p + size]
        table = struct.unpack_from('<%dI' % h, d, p + size)
        p += size + 4 * h
        if not hd.rle:
            vals = np.frombuffer(blk[:w * h * bpv], np.uint8 if bpv == 1 else '<u2').reshape(h, w)
            out.append((vals, np.ones((h, w), bool)))
        else:
            out.append(blk if (k == 3 and bpv == 2) else decode_rle(blk, table, w, h, bpv))
    return hd, out, p


def rgb_to_pixel16(rgb: np.ndarray) -> np.ndarray:
    """RGB -> RGB565 as the game's depth conversion does (Pixel16_FromRGB 0x433a10 with the tables of
    InitBlendTables 0x433000: round(c * 31 / 255), round(g * 63 / 255)) [confirmed: code]; the same as
    rgb_to_rgb565."""
    return rgb_to_rgb565(rgb)


def encode_rgba16(rgba: np.ndarray, hot: tuple[int, int] = (0, 0), field10: int = 18) -> bytes:
    """An RGBA image (straight alpha, as after the loader's filters) as the game's .frm16."""
    return encode16(rgb_to_pixel16(rgba[..., :3]), rgba[..., 3], hot, field10)


INV_COLOR_TABLE15 = 'Palettes/InvColorTable15.pal'


def nearest_index8(rgb: np.ndarray, inv15: bytes | np.ndarray) -> np.ndarray:
    """Per pixel the palette index the game's frame compiler gives an RGB colour for 8 bit: the 5-5-5 inverse colour
    table (``Palettes/InvColorTable15.pal``, 32,768 bytes, loaded into the palette object 0x633388 as kind 5 by
    InitBlendTables 0x433000) at the 5-5-5 pixel of the colour, each channel trunc(c * 31 / 255 + 0.5) (the tables
    0x633b94/0x6753b8/0x630378) [confirmed: code Palette_Nearest 0x526e40 kind 5, FrameConvert_To8 0x4ad1e0,
    zax-decomp/reimpl/src/palette_rest4b.cpp, image_lo4.cpp, frame_load_convert.cpp; verified: the table is the nearest
    GamePalette entry 1..254 of (r, g, b) * 8 with the weights 30/59/11 for all 32,768 colours]. The frame compiler's
    depth filter passes this palette object to the conversion [confirmed: code FrameFilterConvert_Apply 0x4ae740,
    zax-decomp/reimpl/src/frame_load_convert.cpp]; own 8-bit frames show in the game in the palette colours of these indices
    [verified 2026-10-30, VM, docs/FORMATS.md 5]. The shipped .frm agree with it in 88 % of the opaque pixels compared
    with their .frm16 (the 16-bit image lost bits of the source, and some shipped images were dithered)."""
    inv = np.frombuffer(inv15, np.uint8) if isinstance(inv15, (bytes, bytearray)) else np.asarray(inv15, np.uint8)
    c = np.floor(np.asarray(rgb, np.float64) * 31 / 255 + 0.5).astype(np.int64).clip(0, 31)
    return inv[(c[..., 0] << 10) | (c[..., 1] << 5) | c[..., 2]]


def encode_rgba8(rgba: np.ndarray, inv15: bytes | np.ndarray, hot: tuple[int, int] = (0, 0),
                 field10: int = 18) -> bytes:
    """An RGBA image (straight alpha) as the game's 8-bit .frm: the indices of ``nearest_index8`` in the five alpha
    bands of encode8 (alpha at or below 25 dropped)."""
    return encode8(nearest_index8(rgba[..., :3], inv15), rgba[..., 3], hot, field10)


@dataclass
class FrameValues:
    """What a frame was encoded from, as encode takes it: ``values`` (h, w) palette indices (uint8) or
    RGB565 (uint16), ``alpha`` (h, w) uint8 (None for a raw frame), the hot spot and header +10."""
    bpp: int
    rle: bool
    values: np.ndarray
    alpha: np.ndarray | None
    hot: tuple[int, int]
    field10: int


def values(d: bytes, off: int = 0) -> FrameValues:
    """The values of the frame at ``off`` for encode: every pixel's value from its block and an alpha
    that puts it into the same block again (16 bit: 255 or the edge alpha; 8 bit: band_alpha8). Raises
    ValueError if a pixel lies in two blocks (no encoder writes that)."""
    hd, bl, _ = blocks(d, off)
    w, h = hd.width, hd.height
    field10 = struct.unpack_from('<H', d, off + 10)[0]
    hot = (hd.hot_x, hd.hot_y)
    if not hd.rle:
        return FrameValues(hd.bpp, False, bl[0][0], None, hot, field10)
    if hd.bpp == 16:
        L = layers16(d, off)
        if (L.pix_mask & L.edge_mask).any():
            raise ValueError('a pixel in the pixel and the edge block')
        vals = np.where(L.pix_mask, L.pix, L.edge).astype(np.uint16)
        alpha = np.where(L.pix_mask, 255, np.where(L.edge_mask, L.alpha, 0)).astype(np.uint8)
        return FrameValues(16, True, vals, alpha, hot, field10)
    order = [bl[0], bl[4], bl[3], bl[2], bl[1]]          # pixel, edge, alpha, +24, +20 (ALPHA_BANDS8)
    masks = [b[1] if b is not None else np.zeros((h, w), bool) for b in order]
    if (np.sum(masks, axis=0) > 1).any():
        raise ValueError('a pixel in two blocks')
    vals = np.zeros((h, w), np.uint8)
    for b in order:
        if b is not None:
            vals[b[1]] = b[0][b[1]]
    return FrameValues(8, True, vals, band_alpha8(masks), hot, field10)


def encode(v: FrameValues) -> bytes:
    """Encode FrameValues (from values, or built for an own image) as the game writes the frame."""
    if not v.rle:
        return encode_raw(v.values, v.hot, v.field10)
    if v.bpp == 16:
        return encode16(v.values, v.alpha, v.hot, v.field10)
    return encode8(v.values, v.alpha, v.hot, v.field10)


def frame_end(d: bytes, off: int = 0) -> int:
    """The offset after the frame at ``off`` (header, every block and its row table)."""
    hd = read_header(d, off)
    return off + HEADER + sum(s + 4 * hd.height for s in (hd.size, hd.extra20_size, hd.extra24_size,
                                                           hd.alpha_size, hd.edge_size) if s)
