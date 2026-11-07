"""Build the way point map (``.way``) of a level the way Zax.exe does when it loads a level without one.

Port of ``CWayPointMap::Calculate`` (``0x5383f0``, called by ``CLayer::LoadOrCalculateWay`` ``0x4eca80``) and
everything it calls, from the reimplementation (``zax-decomp/reimpl/src/waypoint_map.cpp``, ``polygon.cpp``,
``math_tables.cpp``, ``sort_list.cpp``, ``layer_parts.cpp``, ``entities.cpp``) [confirmed: code; the result is
compared with all 112 shipped ``.way`` files by ``tools/selftest.py``, docs/FORMATS.md 4]:

- The level's ``CWayPointsPolygon`` parts (the grid query by class ``0x57aae0``: flags 0x200000 set, 0x9d0000
  clear; in the order the grid walks its 64-pixel cells, column by column, each cell in the order the parts
  were read) in two passes by ``Insertion Priority`` (Primary, then Secondary): every outline unshifted, then
  shifted out and in by 20, 25, 30 and 35 pixels (the world's slots 62-66: 20, 20 * 1.99, 2 * that, 20 * 0.25).
- Along every outline edge points at steps of at most 0.9 * MaxDistToConnect; a point becomes a way point when
  no collidable part holds a circle of 0.74 * MinDistBetweenWayPoints around it (``0x537d40``) and no way
  point is within MinDistBetweenWayPoints (``0x539350``). A new way point is joined to every way point within
  MaxDistToConnect found by the quadtree (``0x538ae0``, with the self loop bug of the original).

The x87 runs with 53-bit precision control (``_setdefaultprecision`` at startup, zax-decomp/docs/DECOMPILATION.md), so a
Python float (IEEE double) gives every intermediate result the original has on the FPU stack; ``f32`` rounds
exactly where the original stores a float (``fstp dword``). ``round`` is ``fistp`` (round half to even),
``int`` is ``__ftol`` (truncation).

The collision test needs the models' "Bounds Poly" (read from the ``.mdl16`` header: its only ``POLY2D``
block) and the AI classes in their "Activity" (only with Zax.exe: ``modelhead``). Without the exe the model
activity is unknown; ``Result.exact`` is then False when a model the test reaches has AIs.
"""
from __future__ import annotations

import math
import re
import struct
from dataclasses import dataclass, field

from . import textformat as tf
from . import way
from .level import Level

_F = struct.Struct('<f')


def f32(v: float) -> float:
    """fstp dword: the value rounded to a float."""
    try:
        return _F.unpack(_F.pack(v))[0]
    except OverflowError:
        return math.inf if v > 0 else -math.inf


def _fbits(bits: int) -> float:
    return _F.unpack(struct.pack('<I', bits))[0]


# Float constants of the exe (address: bits) [confirmed: Zax.exe]
ONE = 1.0
PI = _fbits(0x40490fdb)               # 0x5eecc8
HALF_PI = _fbits(0x3fc90fdb)          # 0x5ee000
MINUS_HALF_PI = _fbits(0xbfc90fdb)    # 0x5f7de0
TWO_PI = _fbits(0x40c90fdb)           # 0x5edffc
EPS2 = _fbits(0x3c23d70a)             # 0x5f1e48, 0.01
MINUS_EPS2 = _fbits(0xbc23d70a)       # 0x5f9fa8
STEP_SHARE = _fbits(0x3f666666)       # 0x5fc7ec, 0.9
RADIUS_SHARE = _fbits(0x3f3d70a4)     # 0x5fc7f0, 0.74
CONNECT_SHARE = _fbits(0x3ffeb852)    # 0x5f917c, 1.99
STEP_FACTOR = 0.25                    # 0x5f05b8
BASE_DIST = 20.0                      # 0x5f9178 (World slot 62, 0x4f39f0)
BIG = _fbits(0x4b18967f)              # 9999999.0, start of the bounding rectangle search

# The world's slots 62-66 (0x4f39f0-0x4f3a30, the base World vtable 0x5f8fc0 and the game's 0x602dc8 alike),
# each returned on the FPU and stored as a float argument by 0x4eca80
MIN_DIST = f32(BASE_DIST)                            # slot 62
MAX_CONNECT = f32(BASE_DIST * CONNECT_SHARE)         # slot 63: 39.8
STEP = f32(BASE_DIST * STEP_FACTOR)                  # slot 64: 5
MAX_OFFSET = f32(2 * (BASE_DIST * CONNECT_SHARE))    # slot 65: twice slot 63's unrounded value
START_OFFSET = MIN_DIST                              # slot 66: slot 62

# Layer part flags (+0x1c, layer_parts.h)
F_DELETED, F_VISIBLE, F_COLLIDEABLE, F_TRIES, F_HIT_POINTS, F_STATIONARY = 0x10000, 0x20000, 0x40000, 0x80000, 0x100000, 0x200000
F_ACTIVE = 0x800000
CTOR_FLAGS = 0xa60000                 # CLayerPart's constructor 0x4fa770
FLAG_FIELDS = (('Is Marked For Deletion', None, F_DELETED), ('Visible', None, F_VISIBLE),
               ('Collideable', 'Is Collidable', F_COLLIDEABLE), ('Tries To Collide', 'Trys To Collide', F_TRIES),
               ('Has Hit Points', None, F_HIT_POINTS), ('Stationary', None, F_STATIONARY), ('Active', None, F_ACTIVE))
# CWayPointsPolygon: ResetFields 0x5992c0 clears 0x9d0000; RegisterFields 0x598f60 hides these flag fields
# (their names emptied, so the text lines are not read)
WPP_HIDDEN = {'Visible', 'Collideable', 'Is Collidable', 'Active', 'Has Hit Points', 'Stationary',
              'Is Marked For Deletion'}
WPP_CLASS = 'CWayPointsPolygon'
WPP_PRIORITIES = ('Primary', 'Secondary')     # the list 0x713dd8; default "Secondary"
POLY_CLASSES = {'CFreeRangePoly', 'CRenderablePolygon', WPP_CLASS}   # slot 48 0x4b5ce0, slot 43 0x4b6100
# Slot 48 of these returns no polygon (0x4011e0); other classes not listed here are entities (0x48b860)
NO_SHAPE_CLASSES = {'CUnderConstructionLayerPart', 'CSimpleLayerPart'}
# Character classes (CEntityCharacter and below, zax-decomp/docs/classes.csv) for CTurretAI's slot 31
CHARACTER_CLASSES = {'CEntityCharacter', 'CEntityStationaryCharacter', 'CEntityWalking', 'CEntityFlying'}
DOOR_AI = 'CDoorAI'                   # IsPointBlocked skips doors (slot 64 with CDoorAI's class 0x481710)
# AI classes whose slot 31 (part, null, 0) answers 0, so slot 65 (AND of the AIs) says "not touchable":
# CTouchingPolygonTriggerAI 0x4218c0, CPickupAI and CPickupDeployedItemAI 0x53dea0 (no entity),
# CTurnToBounceDirAI 0x5706a0 (null other == null shooter); CTurretAI 0x58e340 only for a character in
# "Idle". All other AI classes answer 1 for a null part (0x53e0d0 and the others in zax-decomp/docs/classes.csv).
NOT_TOUCHABLE_AIS = {'CTouchingPolygonTriggerAI', 'CPickupAI', 'CPickupDeployedItemAI', 'CTurnToBounceDirAI'}
TURRET_AI = 'CTurretAI'
NOT_FOUND = 0x7fffffff


# ---- Polygons (POLY2D, polygon.cpp) ---------------------------------------------------------------------------

def _floor_down(v: float) -> float:
    """0x509340: fistp, minus 1 when that is above the value."""
    r = float(round(v))
    return r if r <= v else r - ONE


def _ceil_up(v: float) -> float:
    """0x5093a0: fistp, plus 1 when that is below the value."""
    r = float(round(v))
    return r + ONE if r < v else r


class Poly:
    """A POLY2D: points (floats), edge normals and lengths, the bounding rectangle."""
    __slots__ = ('xs', 'ys', 'nx', 'ny', 'ln', 'left', 'top', 'right', 'bottom')

    def __init__(self, pts=()):
        self.xs = [p[0] for p in pts]
        self.ys = [p[1] for p in pts]
        self.left = self.top = self.right = self.bottom = 0
        self.update()

    @property
    def count(self) -> int:
        return len(self.xs)

    def points(self) -> list[tuple[float, float]]:
        return list(zip(self.xs, self.ys))

    def update(self) -> None:
        self._bounds()
        self._edges()

    def _bounds(self) -> None:
        """0x5460b0 (the rectangle part)."""
        if not self.xs:
            return
        minx = miny = BIG
        maxx = maxy = -BIG
        for x, y in zip(self.xs, self.ys):
            f = _floor_down(x)
            if not minx < f:
                minx = f32(f)
            f = _floor_down(y)
            if not miny < f:
                miny = f32(f)
            f = _ceil_up(x)
            if maxx <= f:
                maxx = f32(f)
            f = _ceil_up(y)
            if maxy <= f:
                maxy = f32(f)
        self.bottom, self.right, self.top, self.left = round(maxy), round(maxx), round(miny), round(minx)
        if self.left == self.right:
            self.right += 1
        if self.top == self.bottom:
            self.bottom += 1

    def _edges(self) -> None:
        """0x546240 (normals and lengths; the turn flags are not needed here)."""
        xs, ys = self.xs, self.ys
        self.nx, self.ny, self.ln = [], [], []
        for i in range(len(xs) - 1):
            dxu = xs[i + 1] - xs[i]
            dy = f32(ys[i + 1] - ys[i])
            mdx = f32(-dxu)
            dy2 = dy * dy
            n = math.sqrt(mdx * mdx + dy2)
            if n == 0:
                self.nx.append(0.0)
                self.ny.append(1.0)
            else:
                inv = ONE / n
                self.nx.append(f32(dy * inv))
                self.ny.append(f32(mdx * inv))
            self.ln.append(f32(math.sqrt(dxu * dxu + dy2)))

    def insert(self, x: float, y: float) -> None:
        """0x5466c0 with "after the last point": nothing from 25 points on or when the last point is the same."""
        n = len(self.xs)
        if n:
            if n >= 25 or (self.xs[-1] == x and self.ys[-1] == y):
                return
        self.xs.append(x)
        self.ys.append(y)

    def contains(self, x: float, y: float) -> bool:
        """0x546830: inside the rectangle, then the winding counted in quadrant steps."""
        if not (self.left <= x) or self.right < x or not (self.top <= y) or self.bottom < y:
            return False
        xs, ys = self.xs, self.ys
        px, py = xs[0], ys[0]
        pq = _quadrant(px, py, x, y)
        total = 0
        for i in range(1, len(xs)):
            cx, cy = xs[i], ys[i]
            q = _quadrant(cx, cy, x, y)
            step = q - pq
            if step == -3:
                step = 1
            elif step == 3:
                step = -1
            elif step in (2, -2):
                xi = cx - ((px - cx) * (cy - y)) / (py - cy)
                if not xi <= x:
                    step = -step
            px, py, pq = cx, cy, q
            total += step
        return total in (4, -4)

    def hits_circle(self, x: float, y: float, r: float) -> bool:
        """0x5469c0: the rectangle widened by r, then inside, then an edge within r (0x546c70)."""
        if not (self.left - r <= x) or self.right + r < x or not (self.top - r <= y) or self.bottom + r < y:
            return False
        if self.contains(x, y):
            return True
        xs, ys = self.xs, self.ys
        for i in range(len(xs) - 1):
            if _seg_hits_circle(xs[i], ys[i], f32(-self.ny[i]), self.nx[i], self.ln[i], x, y, r):
                return True
        return False


def _quadrant(px: float, py: float, x: float, y: float) -> int:
    xle, yle = px <= x, py <= y
    if not xle:
        return 3 if yle else 0
    return 2 if yle else 1


def _seg_hits_circle(p0, p1, d0, d1, length, c0, c1, r) -> bool:
    """0x545620 (only whether it hits): does the segment p + d * [0, length] come closer than r to c?"""
    dx = f32(c0 - p0)
    dyu = c1 - p1
    dy = f32(dyu)
    t = f32(dyu * d1 + dx * d0)
    if not (-r < t):
        return False
    if length + r <= t:
        return False
    if not (t < 0) and t < length:
        perp = (dy * dy + dx * dx) - t * t
        return not (r * r <= perp)
    r2 = r * r
    if dy * dy + dx * dx < r2:
        return True
    ex = f32(d0 * length + p0)
    ey = f32(f32(d1 * length) + p1)
    dx2, dy2 = c0 - ex, c1 - ey
    return dy2 * dy2 + dx2 * dx2 < r2


def _seg_intersect(x1, y1, x2, y2, x3, y3, x4, y4):
    """0x5093d0 with the range tests off: the intersection of the two lines, None when parallel."""
    a = f32(x2 - x1)
    b = f32(x3 - x4)
    dy12 = f32(y2 - y1)
    dy34 = f32(y3 - y4)
    e1 = f32(x1 - x3)
    e2 = f32(y1 - y3)
    num = f32(e1 * dy34 - e2 * b)
    den = f32(dy12 * b - dy34 * a)
    if not (den <= MINUS_EPS2) and den < EPS2:
        return None
    inv = ONE / den
    return f32(num * a * inv + x1), f32(num * dy12 * inv + y1)


_NUM = r'[ \t\n\v\f\r]*[+-]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[eE][+-]?[0-9]+)?'
_PAIR = re.compile(f'({_NUM}),[ \\t\\n\\v\\f\\r]*({_NUM})')


def poly_from_text(text: str) -> Poly:
    """The polygon field's text slot 0x5480e0: "%f, %f" pairs (every second comma) appended with 0x5466c0
    until one does not scan; one point with an 'e' in the text is emptied again."""
    p = Poly()
    pos = 0
    while pos < len(text):
        m = _PAIR.match(text, pos)
        if not m:
            break
        p.insert(f32(float(m.group(1))), f32(float(m.group(2))))
        c = text.find(',', pos)
        if c < 0:
            break
        c = text.find(',', c + 1)
        if c < 0:
            break
        pos = c + 1
    if p.count == 1 and 'e' in text:
        p = Poly()
    p.update()
    return p


def poly_from_model(data: bytes) -> Poly | None:
    """The model's "Bounds Poly" (CModel +0x78): the only POLY2D block of the .mdl16 header (header
    "POLY2D\\0", the byte 7, the count, the points; 0x545fa0). None when there is none."""
    i = data.find(b'POLY2D\0')
    if i < 0 or data[i + 7] != 7:
        return None
    n = struct.unpack_from('<I', data, i + 8)[0]
    v = struct.unpack_from(f'<{2 * n}f', data, i + 12)
    p = Poly()
    p.xs, p.ys = list(v[0::2]), list(v[1::2])
    p.update()
    return p


# ---- The arc tangent table (math_tables.cpp) ------------------------------------------------------------------

def _atan_table() -> list[float]:
    """0x508cb0: entry 0 is 0, entry k atan2(10.0, 10 / k * 1000) as a float."""
    return [0.0] + [f32(math.atan2(10.0, 10.0 / k * 1000.0)) for k in range(1, 1001)]


ATAN = _atan_table()


def _atan_of(ratio: float) -> float:
    return ATAN[round(f32(ratio * 1000.0))]


def table_atan2(y: float, x: float) -> float:
    """0x509100: the angle of (x, y) in (-pi, pi] through the table (a thousandth of the smaller over the
    larger magnitude); y = 0: 0 for x > 0, else pi; x = 0: +-pi/2."""
    if y == 0:
        return PI if x <= 0 else 0.0
    if x == 0:
        return MINUS_HALF_PI if y <= 0 else HALF_PI
    if not x <= 0:
        if not y <= 0:
            if not x <= y:
                return _atan_of(y / x)
            return HALF_PI - _atan_of(x / y)
        ny = -y
        if not x <= ny:
            return -_atan_of(ny / x)
        return _atan_of(x / ny) - HALF_PI
    nx = -x
    if not y <= 0:
        if not nx <= y:
            return PI - _atan_of(y / nx)
        return _atan_of(nx / y) + HALF_PI
    ny = -y
    if not nx <= ny:
        return _atan_of(ny / nx) - PI
    return MINUS_HALF_PI - _atan_of(nx / ny)


# ---- The level's parts as the builder sees them ---------------------------------------------------------------

@dataclass
class ModelData:
    bounds: Poly | None                  # "Bounds Poly"; None without one (or without the model file)
    activity: list[str] | None = None    # AI classes of "Activity"; None when unknown (no Zax.exe)


@dataclass
class Blocker:
    """A part IsPointBlocked can test: the shape (slot 48), the position it is tested relative to (slot 43)
    and the rectangle of kind 3 (slot 37) the grid query compares."""
    index: int                           # in level.parts
    shape: Poly
    px: float
    py: float
    rect: tuple[int, int, int, int]


@dataclass
class WayPolygon:
    index: int                           # in level.parts
    poly: Poly
    priority: int


def _flag_text(part, key: str, alt: str | None):
    v = part.get(key)
    if v is None and alt:
        v = part.get(alt)
    return v


def part_flags(part) -> int:
    """The flags (+0x1c) after the part was read: the constructor's, CWayPointsPolygon's ResetFields, then
    the flag fields of the text (atoi != 0). The descriptors' defaults are the constructor's bits."""
    flags = CTOR_FLAGS
    hidden = ()
    if part.cls == WPP_CLASS:
        flags &= ~0x9d0000
        hidden = WPP_HIDDEN
    for key, alt, bit in FLAG_FIELDS:
        if key in hidden:
            continue
        v = _flag_text(part, key, alt)
        if v is None:
            continue
        m = re.match(r'[ \t\n\v\f\r]*([+-]?[0-9]+)', v)
        if m and int(m.group(1)) != 0:
            flags |= bit
        else:
            flags &= ~bit
    return flags


def _f32_field(part, key: str) -> float:
    v = part.get(key)
    if v is None:
        return 0.0
    m = re.match(_NUM, v)
    return f32(float(m.group(0))) if m else 0.0


def _activity(part) -> list[str]:
    a = part.node.block('Activity')
    if a is None:
        return []
    return [n.value for n in a if isinstance(n, tf.Node) and n.value]


@dataclass
class Inputs:
    polygons: list[WayPolygon]
    blockers: list[Blocker]
    exact: bool = True                   # False when a model's activity was unknown
    notes: list[str] = field(default_factory=list)


def collect(level: Level, model_data) -> Inputs:
    """The way point polygons in the grid's order and the parts that can block a point.
    ``model_data(model path) -> ModelData | None``."""
    W, H = level.size
    columns = (W >> 6) + (1 if W & 63 else 0)
    rows = (H >> 6) + (1 if H & 63 else 0)
    max_x, max_y = columns * 64 - 1, rows * 64 - 1
    polys, blockers, exact, notes = [], [], True, []
    cache: dict[str, ModelData | None] = {}
    for i, part in enumerate(level.parts):
        flags = part_flags(part)
        cls = part.cls
        if cls == WPP_CLASS:
            if flags & (F_STATIONARY | 0x9d0000) == F_STATIONARY:
                text = part.get('Polygon')
                pr = (part.get('Insertion Priority') or 'Secondary').strip().lower()
                prio = next((k for k, n in enumerate(WPP_PRIORITIES) if n.lower() == pr), 1)
                p = poly_from_text(text) if text is not None else Poly()
                polys.append(WayPolygon(i, p, prio))
            continue
        # IsPointBlocked's grid filter: all of 0x840000, none of 0x190000
        if flags & (F_ACTIVE | F_COLLIDEABLE | F_HIT_POINTS | F_TRIES | F_DELETED) != F_ACTIVE | F_COLLIDEABLE:
            continue
        if cls in NO_SHAPE_CLASSES:
            continue
        ais = _activity(part)
        if cls in POLY_CLASSES:
            text = part.get('Polygon')
            shape = poly_from_text(text) if text is not None else Poly()
            if shape.count == 0:
                px = py = 0.0
            else:
                px, py = shape.xs[0], shape.ys[0]
            rect = (shape.left, shape.top, shape.right, shape.bottom)
        else:
            model = part.get('Model')
            if not model:
                continue
            key = model.lower()
            if key not in cache:
                cache[key] = model_data(model)
            md = cache[key]
            if md is None or md.bounds is None:
                continue
            shape = md.bounds
            if shape.count < 2:
                continue          # never hits (no edge, the winding of one point is 0)
            px, py = _f32_field(part, 'Position X'), _f32_field(part, 'Position Y')
            ox, oy = round(px), round(py)
            rect = (shape.left + ox, shape.top + oy, shape.right + ox, shape.bottom + oy)
            if md.activity is None:
                if exact:
                    notes.append(f'model activity unknown (no Zax.exe): {model}')
                exact = False
            else:
                ais = ais + md.activity
        if DOOR_AI in ais or any(a in NOT_TOUCHABLE_AIS for a in ais):
            continue
        if TURRET_AI in ais and cls in CHARACTER_CLASSES and (part.get('Cur Sequence') or '').lower() == 'idle':
            continue
        if shape.count < 2:
            continue
        blockers.append(Blocker(i, shape, px, py, rect))

    def first_cell(wp: WayPolygon):
        p = wp.poly
        return (_to_cell(max_x, p.left), _to_cell(max_y, p.top), wp.index)

    polys.sort(key=first_cell)
    return Inputs(polys, blockers, exact, notes)


def _to_cell(limit: int, v: int) -> int:
    """The inlined cell index of the grid: 16-bit, at most the limit, at least 0, divided by 64."""
    def s16(n):
        n &= 0xffff
        return n - 0x10000 if n & 0x8000 else n
    c = min(s16(limit), s16(v))
    return max(c, 0) >> 6


# ---- The map -------------------------------------------------------------------------------------------------

class _Quad:
    """The map's quadtree (ZQuadNode): one node per way point; children by the node's position:
    0 x >= and y >=, 1 x < and y >=, 2 x < and y <, 3 x >= and y <."""
    __slots__ = ('x', 'y', 'c', 'root')

    def __init__(self):
        self.x, self.y, self.c = [], [], []
        self.root = -1

    def insert(self, x: int, y: int) -> None:
        n = len(self.x)
        self.x.append(x)
        self.y.append(y)
        self.c.append([-1, -1, -1, -1])
        if self.root < 0:
            self.root = n
            return
        cur = self.root
        xs, ys, cs = self.x, self.y, self.c
        while True:
            if x < xs[cur]:
                k = 2 if y < ys[cur] else 1
            else:
                k = 3 if y < ys[cur] else 0
            nxt = cs[cur][k]
            if nxt < 0:
                cs[cur][k] = n
                return
            cur = nxt

    def query(self, r0: int, r1: int, r2: int, r3: int) -> list[int]:
        """0x539760: the nodes inside {left, top, right, bottom} (right and bottom excluded) in the
        original's visiting order (the node, then the children 0-3 with the rectangle cut at the node)."""
        out = []
        if self.root < 0:
            return out
        xs, ys, cs = self.x, self.y, self.c
        stack = [(self.root, r0, r1, r2, r3)]
        pop, push = stack.pop, stack.append
        while stack:
            n, a, b, c, d = pop()
            x, y = xs[n], ys[n]
            if x >= a and y >= b and x < c and y < d:
                out.append(n)
            ch = cs[n]
            # pushed in reverse so child 0 is visited first
            if ch[3] >= 0 and x <= c and y >= b:
                push3 = (ch[3], x if x > a else a, b, c, y if y < d else d)
            else:
                push3 = None
            if ch[2] >= 0 and x >= a and y >= b:
                push2 = (ch[2], a, b, x if x < c else c, y if y < d else d)
            else:
                push2 = None
            if ch[1] >= 0 and x >= a and y <= d:
                push1 = (ch[1], a, y if y > b else b, x if x < c else c, d)
            else:
                push1 = None
            if push3:
                push(push3)
            if push2:
                push(push2)
            if push1:
                push(push1)
            if ch[0] >= 0 and x <= c and y <= d:
                push((ch[0], x if x > a else a, y if y > b else b, c, d))
        return out


class Builder:
    def __init__(self, inputs: Inputs, min_dist: float = MIN_DIST, max_connect: float = MAX_CONNECT):
        self.inputs = inputs
        self.min_dist = int(min_dist)
        self.max_connect = int(max_connect)
        self.nx: list[int] = []
        self.ny: list[int] = []
        self.nsegs: list[list[int]] = []
        self.sa: list[int] = []
        self.sb: list[int] = []
        self.slen: list[float] = []
        self.sang: list[float] = []
        self.quad = _Quad()
        self.cells: dict[tuple[int, int], list[int]] = {}
        self.origin: list[int] = []      # per way point: the index in inputs.polygons whose outline made it
        self._current = -1
        self.points_tested = 0
        # blockers by 64-pixel cells of their rectangle
        self.bcells: dict[tuple[int, int], list[Blocker]] = {}
        for b in inputs.blockers:
            for cy in range(b.rect[1] >> 6, (b.rect[3] >> 6) + 1):
                for cx in range(b.rect[0] >> 6, (b.rect[2] >> 6) + 1):
                    self.bcells.setdefault((cx, cy), []).append(b)

    # 0x537d40
    def blocked(self, x: float, y: float, radius: float) -> bool:
        r0 = int(x - radius - ONE)
        r1 = int(y - radius - ONE)
        r2 = int(x + radius - ONE)
        r3 = int(y + radius - ONE)
        if r3 - r1 == 0 or r2 - r0 == 0:
            return False        # FindRect gives nothing for a rectangle without width or height
        seen = set()
        for cy in range(r1 >> 6, (r3 >> 6) + 1):
            for cx in range(r0 >> 6, (r2 >> 6) + 1):
                for b in self.bcells.get((cx, cy), ()):
                    if id(b) in seen:
                        continue
                    seen.add(id(b))
                    br = b.rect
                    if not (max(r0, br[0]) < min(r2, br[2]) and max(r1, br[1]) < min(r3, br[3])):
                        continue
                    if b.shape.hits_circle(f32(x - b.px), f32(y - b.py), radius):
                        return True
        return False

    # 0x539350 without a mover: is a way point within the distance (in the half-open square of the query)?
    def near(self, x: int, y: int, d: int) -> bool:
        limit = d * d
        for cy in range((y - d) >> 5, ((y + d - 1) >> 5) + 1):
            for cx in range((x - d) >> 5, ((x + d - 1) >> 5) + 1):
                for n in self.cells.get((cx, cy), ()):
                    ox, oy = self.nx[n], self.ny[n]
                    if x - d <= ox < x + d and y - d <= oy < y + d:
                        ddx, ddy = x - ox, y - oy
                        if ddx * ddx + ddy * ddy <= limit:
                            return True
        return False

    # 0x538df0
    def add_node(self, x: int, y: int) -> int:
        i = len(self.nx)
        self.nx.append(x)
        self.ny.append(y)
        self.nsegs.append([])
        self.origin.append(self._current)
        self.quad.insert(x, y)
        self.cells.setdefault((x >> 5, y >> 5), []).append(i)
        self.connect(i)
        return i

    # 0x538ae0 (with the original's slip: it skips list position `index`, not the way point itself)
    def connect(self, index: int) -> None:
        x, y, mc = self.nx[index], self.ny[index], self.max_connect
        found = self.quad.query(x - mc, y - mc, x + mc, y + mc)
        limit = mc * mc
        for i, other in enumerate(found):
            if i == index:
                continue
            dx, dy = x - self.nx[other], y - self.ny[other]
            if ((dx * dx + dy * dy) & 0xffffffff) > limit:
                continue
            self.add_edge(index, other)

    def _joins(self, s: int, i: int, j: int) -> bool:
        a, b = self.sa[s], self.sb[s]
        return (a == i and b == j) or (b == i and a == j)

    # 0x53a780
    def add_edge(self, me: int, other: int) -> None:
        for s in self.nsegs[me]:
            if self._joins(s, me, other):
                if s != -1:
                    return
                break
        found = -1
        for s in self.nsegs[other]:
            if self._joins(s, me, other):
                found = s
                break
        if found == -1:
            found = self._new_segment(me, other)
        self.nsegs[me].append(found)
        self.nsegs[other].append(found)

    # 0x53a010 + 0x53a0f0 (the ends by position, 0x5392f0: always the way points themselves, positions are unique)
    def _new_segment(self, a: int, b: int) -> int:
        ax, ay, bx, by = float(self.nx[a]), f32(self.ny[a]), float(self.nx[b]), f32(self.ny[b])
        dx_ab = f32(ax - bx)
        dy_ab = f32(ay - by)
        dx = f32(bx - ax)
        dy = f32(by - ay)
        r = table_atan2(dy, dx)
        if r < 0:
            r = r + TWO_PI
        if not r < TWO_PI:
            r = r - TWO_PI
        self.sa.append(a)
        self.sb.append(b)
        self.sang.append(f32(r))
        self.slen.append(f32(math.sqrt(dy_ab * dy_ab + dx_ab * dx_ab)))
        return len(self.sa) - 1

    # 0x537e90: outline vertex j = (i + 1) % (count - 1) moved out by dist
    @staticmethod
    def offset_vertex(s: Poly, i: int, dist: float) -> tuple[float, float]:
        n = s.count - 1
        j = (i + 1) % n
        k = (j + 1) % n
        xs, ys, nxs, nys = s.xs, s.ys, s.nx, s.ny

        def moved(nx, ny, px, py):
            return f32(px + nx * dist), f32(py + f32(ny * dist))

        q0, q1 = moved(nxs[i], nys[i], xs[i], ys[i])
        q2, q3 = moved(nxs[i], nys[i], xs[j], ys[j])
        q4, q5 = moved(nxs[j], nys[j], xs[j], ys[j])
        q6, q7 = moved(nxs[j], nys[j], xs[k], ys[k])
        r = _seg_intersect(q0, q1, q2, q3, q4, q5, q6, q7)
        if r is None:
            return q2, q3
        ox, oy = r
        ey = oy - q3
        ex = ox - q2
        d2 = ex * ex + ey * ey
        if not (dist * dist < d2):
            return ox, oy
        vx = q2 - q0
        vy = q3 - q1
        vyf = f32(vy)
        ln = math.sqrt(vy * vyf + vx * vx)
        if ln != 0:
            inv = ONE / ln
            vx = vx * inv
            vyf = f32(vyf * inv)
        return f32(vx * dist + q2), f32(vyf * dist + q3)

    # 0x5380d0
    def points_along(self, fx, fy, tx, ty, radius, state) -> None:
        step = float(self.max_connect) * STEP_SHARE
        dx = tx - fx
        dy = f32(ty - fy)
        cx, cy = fx, fy
        ln = math.sqrt(dy * dy + dx * dx)
        ln_f = f32(ln)
        if ln != 0:
            inv = ONE / ln
            dx = dx * inv
            dy = f32(dy * inv)
        n = int(ln_f / step) + 1
        seg = ln_f / n
        seg_f = f32(seg)
        sx = f32(seg * dx)
        sy = f32(dy * seg_f)
        md = self.min_dist
        for _ in range(n):
            self.points_tested += 1
            if not self.blocked(cx, cy, radius):
                px, py = round(cx), round(cy)
                if not self.near(px, py, md):
                    self.add_node(px, py)
                    state[0], state[1], state[2] = cx, cy, True
            cx = f32(cx + sx)
            cy = f32(cy + sy)

    # 0x538230
    def outline(self, s: Poly, dist: float, radius: float) -> None:
        n = s.count - 1
        if n <= 1:
            return
        state = [0.0, 0.0, False]       # the last point added, the added flag
        i = 0
        while i < n:
            ax, ay = self.offset_vertex(s, i, dist)
            i += 1
            bx, by = self.offset_vertex(s, i % n, dist)
            ax, ay, bx, by = f32(0.0 + ax), f32(ay + 0.0), f32(bx + 0.0), f32(by + 0.0)
            if state[2]:
                self.points_along(state[0], state[1], ax, ay, radius, state)
            self.points_along(ax, ay, bx, by, radius, state)

    # 0x5383f0
    def calculate(self, offset: float = START_OFFSET, min_dist: float = MIN_DIST, max_offset: float = MAX_OFFSET,
                  step: float = STEP) -> None:
        radius = f32(min_dist * RADIUS_SHARE)
        limit = f32(max_offset * 0.5)
        for pas in (0, 1):
            group = [(k, wp.poly) for k, wp in enumerate(self.inputs.polygons) if wp.priority == pas]
            for self._current, p in group:
                self.outline(p, 0.0, 0.0)
            off = offset
            if off < limit:
                while True:
                    for self._current, p in group:
                        self.outline(p, off, radius)
                        self.outline(p, f32(-off), radius)
                    off = f32(off + step)
                    if not off < limit:
                        break

    def way_map(self) -> way.WayMap:
        nodes = [way.WayNode(x, y, list(s)) for x, y, s in zip(self.nx, self.ny, self.nsegs)]
        edges = [way.WayEdge(a, b, ln, ang) for a, b, ln, ang in zip(self.sa, self.sb, self.slen, self.sang)]
        return way.WayMap(self.min_dist, self.max_connect, nodes, edges)


@dataclass
class Result:
    way: way.WayMap
    exact: bool                          # False: a model's activity was unknown (no Zax.exe)
    notes: list[str]
    points_tested: int
    inputs: Inputs
    origin: list[int]                    # per way point: the index in inputs.polygons that made it


def build(level: Level, model_data) -> Result:
    """The level's way point map as the game calculates it. ``model_data(model path) -> ModelData|None``."""
    inp = collect(level, model_data)
    b = Builder(inp)
    b.calculate()
    return Result(b.way_map(), inp.exact, inp.notes, b.points_tested, inp, b.origin)


# ---- Analysis for the editor (not code of the game) -----------------------------------------------------------

# FindPath 0x5386b0 takes for a path's end a way point within 4, a temporary one joined to the way points
# within MaxDistToConnect, else one within 4 * MaxDistToConnect; without any the search gives up
PATH_END_REACH = 4


def components(w: way.WayMap) -> list[int]:
    """The connected component of every way point (0 = the largest), by the segments."""
    parent = list(range(len(w.nodes)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for e in w.edges:
        if e.a != e.b and 0 <= e.a < len(parent) and 0 <= e.b < len(parent):
            ra, rb = find(e.a), find(e.b)
            if ra != rb:
                parent[ra] = rb
    roots = [find(i) for i in range(len(parent))]
    sizes: dict[int, int] = {}
    for r in roots:
        sizes[r] = sizes.get(r, 0) + 1
    order = {r: k for k, r in enumerate(sorted(sizes, key=lambda r: (-sizes[r], r)))}
    return [order[r] for r in roots]


class NodeIndex:
    """Way points by 64-pixel cells for distance queries."""

    def __init__(self, w: way.WayMap):
        self.w = w
        self.cells: dict[tuple[int, int], list[int]] = {}
        for i, n in enumerate(w.nodes):
            self.cells.setdefault((n.x >> 6, n.y >> 6), []).append(i)

    def nearest(self, x: float, y: float, d: float, among=None) -> tuple[int, float] | None:
        """The nearest way point within d (optionally only those with ``among(index)``) and its distance."""
        best, bi = None, -1
        r = int(d) + 1
        for cy in range((int(y) - r) >> 6, ((int(y) + r) >> 6) + 1):
            for cx in range((int(x) - r) >> 6, ((int(x) + r) >> 6) + 1):
                for i in self.cells.get((cx, cy), ()):
                    if among is not None and not among(i):
                        continue
                    n = self.w.nodes[i]
                    dd = math.hypot(n.x - x, n.y - y)
                    if dd <= d and (best is None or dd < best):
                        best, bi = dd, i
        return None if best is None else (bi, best)

    def path_end(self, x: float, y: float) -> int | None:
        """The way point FindPath would use for a path's end at (x, y) (rounded like the integer points of
        CWayPointPath), None when it finds none."""
        mc = self.w.max_connect
        for d in (PATH_END_REACH, mc, mc * PATH_END_REACH):
            hit = self.nearest(round(x), round(y), d)
            if hit is not None:
                return hit[0]
        return None


def model_data_source(ds, head=None):
    """``model_data`` for ``build`` reading ``Cache/Models/<model>.mdl16`` from a DataSource; with a
    ``modelhead.ModelHead`` (needs Zax.exe) also the model's activity."""
    def get(model: str) -> ModelData | None:
        rel = f'Cache/Models/{model}.mdl16'
        if not ds.exists(rel):
            return None
        data = ds.read(rel)
        bounds = poly_from_model(data)
        activity = None
        if head is not None:
            try:
                m = head.decode(data)
                activity = [o.cls for o in (m.values.get('Activity') or []) if o is not None]
            except Exception:       # noqa: BLE001 - unreadable header: activity stays unknown
                activity = None
        return ModelData(bounds, activity)
    return get


def dumps(level: Level, model_data) -> bytes:
    """The .way file the game writes for the level (0x4ec520: Object_WriteBinary of the map)."""
    return way.dumps(build(level, model_data).way)
