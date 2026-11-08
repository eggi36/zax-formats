"""Ground values between the grid points, as Zax.exe computes them (``CPlasmaTileMap``).

The game does not interpolate bilinearly; it fills every 64x64 tile with a plasma fractal
(midpoint displacement) [confirmed: Zax.exe, tile from 0x540d90]:

1. Set the four corner values (``Elevations``); image 65x65, otherwise 0 (= "still empty").
2. Top and bottom edge (0x49f9d0), left and right edge (0x49fe10): halve repeatedly,
   midpoint = (a + b) >> 1 plus random ``(r & (2A - 1)) - A``; ``A`` starts at 64 >> 3 = 8 and
   halves at every level. A result < 0 becomes 1, > 255 becomes 255.
3. Inside (0x49fad0, diamond-square): per cell centre = (a + b + c + d + 2) >> 2 without random,
   edge midpoints as above, but only if the pixel is still 0.

Random: 256 R250 generators, generator k with seed (k + 1) * 0xE6CEF (0x53f520), copied fresh for
every edge/area. ``Seeds`` at the grid point selects the generator: top edge ``Seed(a, b) + 0x55``,
left edge ``Seed(a, b)``, right ``Seed(a + 1, b)``, bottom edge ``Seed(a, b + 1) + 0x55``, inside
``Seed(a, b) - 0x56`` (each & 0xFF). Shared edges of neighbouring tiles are therefore equal.
Everything is deterministic: equal values always give the same image in the game.

Verified: generators and tiles match the original code executed in an emulator byte for byte
(256 generators, 44 tiles including special cases).
"""
from __future__ import annotations

import threading

import numpy as np

TILE = 64
_M = 0xffffffff


def _r250(seed: int) -> list[int]:
    s = [0] * 250
    st = seed & _M
    for i in range(249, -1, -1):           # LCG, like 0x55c390 (upper word of the product)
        p = st * 0x41c64e6d
        lo, hi = p & _M, p >> 32 & _M
        new = (lo + 0x3039) & _M
        s[i] = ((((hi << 16) & _M) + 0xffff + ((lo + 0x3039) >> 32)) & 0xffff0000) | (new >> 16)
        st = new
    mask, bit, k = _M, 0x80000000, 3
    while bit:
        s[k] = (s[k] & mask) | bit
        k, mask, bit = k + 7, mask >> 1, bit >> 1
    return s


_RNG = np.array([_r250(k * 0xe6cef) for k in range(1, 257)], np.uint32)   # Index i1=0, i2=103
_NEXT = (np.arange(250) + 1) % 250


class _Rng:
    """R250 for many tiles at once, each with its own state."""

    def __init__(self, gen: np.ndarray):
        self.s = _RNG[gen].copy()
        n = len(gen)
        self.i1 = np.zeros(n, np.intp)
        self.i2 = np.full(n, 0x67, np.intp)
        self.rows = np.arange(n)

    def draw(self, sel=None) -> np.ndarray:
        r = self.rows if sel is None else self.rows[sel]
        i1, i2 = self.i1[r], self.i2[r]
        v = self.s[r, i1] ^ self.s[r, i2]
        self.s[r, i1] = v
        self.i1[r], self.i2[r] = _NEXT[i1], _NEXT[i2]
        return v


def _jitter(rng: _Rng, val: np.ndarray, amp: int, sel=None) -> np.ndarray:
    v = (rng.draw(sel) & (2 * amp - 1)).astype(np.int32) - amp + val
    return np.where(v < 0, 1, np.minimum(v, 255))


def _edge(img: np.ndarray, line, gen: np.ndarray) -> None:
    """One edge: ``line`` selects the 65 pixels from img (tile, ...)."""
    rng = _Rng(gen)
    px = img[line]
    amp, step = TILE >> 3, TILE
    while step > 1:
        half = step >> 1
        for p in range(0, TILE, step):
            mid = (px[:, p] + px[:, p + step]) >> 1
            px[:, p + half] = _jitter(rng, mid, amp) if amp else mid
        amp, step = amp >> 1, half
    img[line] = px


def _fill(img: np.ndarray, gen: np.ndarray) -> None:
    rng = _Rng(gen)
    amp, h = TILE >> 3, TILE
    while h > 1:
        g = h >> 1
        for y in range(0, TILE, h):
            for x in range(0, TILE, h):
                a, b = img[:, y, x], img[:, y, x + h]
                c, d = img[:, y + h, x + h], img[:, y + h, x]
                img[:, y + g, x + g] = (a + b + c + d + 2) >> 2
                for py, px, val in ((y + g, x + h, (b + c) >> 1), (y + g, x, (a + d) >> 1),
                                    (y, x + g, (a + b) >> 1), (y + h, x + g, (c + d) >> 1)):
                    empty = img[:, py, px] == 0
                    if empty.any():
                        img[empty, py, px] = _jitter(rng, val[empty], amp, empty) if amp else val[empty]
        h, amp = g, amp >> 1


def tiles(keys: np.ndarray) -> np.ndarray:
    """Tiles (n, 65, 65) uint8 for ``keys`` (n, 7): corners e00, e10, e01, e11 (x, y) and
    seeds s00, s10, s01."""
    keys = np.asarray(keys, np.int32).reshape(-1, 7)
    n = len(keys)
    img = np.zeros((n, TILE + 1, TILE + 1), np.int32)
    img[:, 0, 0], img[:, 0, TILE], img[:, TILE, 0], img[:, TILE, TILE] = keys[:, :4].T
    s00, s10, s01 = keys[:, 4], keys[:, 5], keys[:, 6]
    _edge(img, (slice(None), 0), (s00 + 0x55) & 255)
    _edge(img, (slice(None), slice(None), 0), s00 & 255)
    _edge(img, (slice(None), slice(None), TILE), s10 & 255)
    _edge(img, (slice(None), TILE), (s01 + 0x55) & 255)
    _fill(img, (s00 - 0x56) & 255)
    return img.astype(np.uint8)


class PlasmaCache:
    """Ground values per pixel; tiles are cached by their 7 values so that painting only rebuilds
    changed tiles. Safe to use from several threads (one at a time)."""

    def __init__(self):
        self._tiles: dict[bytes, np.ndarray] = {}
        self._lock = threading.Lock()

    BATCH = 1024        # tiles computed at once (~20 MB of intermediates)
    LIMIT = 20000       # tiles kept (64 x 64 bytes each)

    def values(self, E: np.ndarray, S: np.ndarray, rows: slice, cols: slice) -> np.ndarray:
        """Values of the tiles ``rows`` x ``cols`` (tile (b, a) = grid points b..b+1, a..a+1)
        as an image ((len rows) * 64, (len cols) * 64)."""
        with self._lock:
            ids, nb, na = self._ensure(E, S, rows, cols)
            out = np.empty((nb * TILE, na * TILE), np.uint8)
            for n, i in enumerate(ids):
                r, c = divmod(n, na)
                out[r * TILE:(r + 1) * TILE, c * TILE:(c + 1) * TILE] = self._tiles[i]
            return out

    def ensure(self, E: np.ndarray, S: np.ndarray, rows: slice, cols: slice) -> None:
        """Compute the missing tiles of ``rows`` x ``cols`` ahead (few large batches are much faster than
        many small ones)."""
        with self._lock:
            self._ensure(E, S, rows, cols)

    def _ensure(self, E, S, rows, cols):
        E = np.asarray(E, np.int32)
        S = np.asarray(S, np.int32)
        if S.shape != E.shape:
            S = np.zeros_like(E)
        b = np.arange(E.shape[0] - 1)[rows]
        a = np.arange(E.shape[1] - 1)[cols]
        B, A = np.meshgrid(b, a, indexing='ij')
        keys = np.stack([E[B, A], E[B, A + 1], E[B + 1, A], E[B + 1, A + 1],
                         S[B, A], S[B, A + 1], S[B + 1, A]], -1).astype(np.uint8)
        flat = keys.reshape(-1, 7)
        ids = [k.tobytes() for k in flat]
        missing = {i: k for i, k in zip(ids, flat) if i not in self._tiles}
        if missing:
            keys = list(missing)
            for n in range(0, len(keys), self.BATCH):
                part = keys[n:n + self.BATCH]
                new = tiles(np.array([missing[i] for i in part]))
                for i, t in zip(part, new):
                    self._tiles[i] = t[:TILE, :TILE].copy()
            if len(self._tiles) > self.LIMIT:
                self._tiles = {i: self._tiles[i] for i in set(ids)}
        return ids, len(b), len(a)

CACHE = PlasmaCache()
