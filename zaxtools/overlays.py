"""AI overlays: the shapes the AIs' debug drawing of Zax.exe puts on the map, computed from a level.

Every AI has a debug drawing slot (slot 41, see zax-decomp/docs/EXE_FINDINGS.md "Debug drawing of the AIs and
parts"). The release never calls it, but the code is complete and reimplemented in
``zax-decomp/reimpl/src/ai_draw*.cpp``, ``view_draw.cpp``, ``ai_patrol.cpp`` and ``normal_attack_ai.cpp``. This
module computes the same lines from the fields of the AIs and their objects, without Qt, so the
editor can draw them and the self-test can check them.

What it draws [confirmed: the reimplemented code; formulas as there]:

- the oval ``DrawView_Oval`` 0x4fccc0: centre + (cos t * r, sin t * r * ratio) for t from 0 to 2 pi in
  n steps, n = trunc(max(r, r * ratio)) / 4 clamped to [10, 25] (``oval``);
- the arrow ``DrawView_Arrow`` 0x4fceb0: a shaft of 30 pixels along the angle (y times 0.7128) and two
  barbs of 10 pixels at angle +- 145 degrees (``arrow``);
- the polygon outline 0x546d40: count - skip - 1 lines from point i to i + 1 at the part's offset,
  a single point as a 10 x 10 rectangle (``outline``);
- the rectangle 0x4b33f0: the outline from (x1, y1) to (x2 - 1, y2 - 1) (``rect``).

The part's centre (``LayerPart_Position`` 0x4fb0a0) is the mean of its polygon (slot 48: the own
``Polygon`` of a polygon part, the model's ``Bounds Poly`` of an object; the closing point not
counted) plus the offset (slot 50: 0 for polygon parts, the position for objects), otherwise the
position. The "home" (slot 40) of a character is ``Home Pos X/Y``, of the other parts the position.

The AIs reached: the object's ``Activity`` and, as in the exe, the sub-AIs the composite AIs pass the
drawing on to (CSkeletonAI: the AI of its state, always "Patrol" after Begin (0x576200);
CSimultaneousAIsAI, CSeriesAI (the current one), CWhileAI, CForceUpdatingAI, CTemporaryTaskAI,
CChaseInvestigateAI, CScanInvestigateAI). Not drawn: what only exists while the game runs (paths of
the move behaviours, targets, timer colours, current radii) and the particle systems' shapes. In the
exe the chain itself starts only at the model's ``Activity`` (CEntityBase slot 29 0x488560), which in
the original models never holds one of these AIs; the editor shows the object's AIs, which is what an
editor overlay needs.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from . import textformat as tf
from .i18n import translate
from .level import Level, LevelPart

Y_RATIO = 0.7127659320831299        # float 0x3f3677d4: the view's tilt (67/94)
DEG = 0.01745329238474369           # float of pi / 180 (0x5edb3c)
BARB = 2.5307273864746094           # the barbs' angle, 145 degrees (0x5f9538)
TWO_PI = 6.2831854820251465         # float 0x40c90fdb

YELLOW = (200, 205, 25)             # triggers, spawn facing, patrol areas and paths, turret range
RED = (255, 50, 50)
DARK_BLUE = (25, 25, 125)           # approach/companion/attack distances
GREEN_ATTACK = (25, 125, 25)        # attack buffer zone
TURRET_EXTRA = (10, 205, 25)
LANDSCAPE = (60, 205, 60)
DAMAGE_START = (100, 205, 25)
TIMEOUT = (255, 100, 100)
SOUND_SCALE = (180, 255, 24)
SOUND_INNER = (0, 255, 0)
SOUND_OUTER = (255, 0, 0)
SCAN_START = (0, 255, 255)
SCAN_END = (255, 255, 0)
SCAN_FACING = (255, 128, 0)
SCAN_FACING_WAITING = (0, 0, 255)

# Overlay groups (the editor's menu items), in menu order
GROUPS = ('trigger', 'spawn', 'sound', 'patrol', 'enemy', 'scan', 'area')

# parents of the entity classes (zax-decomp/docs/classes.csv)
_ENTITY_PARENT = {
    'CEntityAnimated': 'CEntityDestructable', 'CEntityAnimatedLine': 'CEntityBase',
    'CEntityAnimatedUpperBody': 'CEntityAnimated', 'CEntityBase': 'CLayerPart',
    'CEntityCharacter': 'CEntityMovable', 'CEntityDestructable': 'CEntityBase',
    'CEntityFlying': 'CEntityCharacter', 'CEntityMovable': 'CEntityAnimated', 'CEntityOm': 'CEntityWalking',
    'CEntityOverlayWalking': 'CEntityWalking', 'CEntityProjectile': 'CEntityMovable',
    'CEntityStationaryCharacter': 'CEntityCharacter', 'CEntityWalking': 'CEntityCharacter',
}


def is_kind(cls: str, base: str) -> bool:
    while cls:
        if cls == base:
            return True
        cls = _ENTITY_PARENT.get(cls, '')
    return False


@dataclass
class Shape:
    """A polyline (or, with ``text``, a text whose top left corner is ``points[0]``) in world pixels.
    ``anchor`` is the part whose moving moves the shape along."""
    group: str
    points: list[tuple[float, float]]
    color: tuple[int, int, int]
    anchor: LevelPart
    source: str = ''                    # the AI and its fields, for the tooltip
    text: str = ''
    font: str = ''                      # the game font of the text ('' = not known)


# --- The view helpers --------------------------------------------------------------------------------

def oval(c, r: float, ratio: float) -> list[tuple[float, float]]:
    """DrawView_Oval 0x4fccc0 (the arc 0x4fcd10 from 0 to 2 pi, open)."""
    m = max(r, r * ratio)
    n = int(math.trunc(m))
    n = int(n / 4)                      # C division, towards zero
    n = min(max(n, 10), 25)
    step = TWO_PI / n
    return [(c[0] + math.cos(k * step) * r, c[1] + math.sin(k * step) * r * ratio) for k in range(n + 1)]


def arrow(p, angle: float, ratio: float = Y_RATIO) -> list[list[tuple[float, float]]]:
    """DrawView_Arrow 0x4fceb0: shaft and the two barbs as three lines."""
    tip = (p[0] + 30 * math.cos(angle), p[1] + 30 * math.sin(angle) * ratio)
    out = [[tuple(p), tip]]
    for a in (angle + BARB, angle - BARB):
        out.append([tip, (tip[0] + 10 * math.cos(a), tip[1] + 10 * math.sin(a) * ratio)])
    return out


def outline(pts, dx: float, dy: float, skip: int = 0) -> list[tuple[float, float]]:
    """The polygon outline 0x546d40: count - skip - 1 lines from point i to i + 1 (one point: a 10 x 10
    rectangle around it, rounded)."""
    n = len(pts)
    if n == 0:
        return []
    if n == 1:
        x, y = pts[0][0] + dx, pts[0][1] + dy
        return rect(round(x - 5), round(y - 5), round(x + 5), round(y + 5))
    lines = n - skip - 1
    if lines <= 0:
        return []
    return [(x + dx, y + dy) for x, y in pts[:lines + 1]]


def rect(x1: int, y1: int, x2: int, y2: int) -> list[tuple[float, float]]:
    """Frame_DrawRectXY 0x4b33f0: the outline from (x1, y1) to (x2 - 1, y2 - 1)."""
    return [(x1, y1), (x2 - 1, y1), (x2 - 1, y2 - 1), (x1, y2 - 1), (x1, y1)]


# --- Fields ----------------------------------------------------------------------------------------

def _f(node: tf.Node, key: str, default: float = 0.0) -> float:
    v = node.get(key)
    try:
        return float(v) if v not in (None, '') else default
    except ValueError:
        return default


def _i(node: tf.Node, key: str, default: int = 0) -> int:
    try:
        return int(float(node.get(key) or default))
    except ValueError:
        return default


def _b(node: tf.Node, key: str) -> bool:
    return (node.get(key) or '0').strip() not in ('0', '')


def _sub(node: tf.Node, key: str) -> tf.Node | None:
    """A pointer or embedded field holding an AI (None when empty)."""
    b = node.block(key)
    return b if b is not None and b.value != 'Array' else None


def _elements(node: tf.Node, key: str) -> list[tf.Node]:
    arr = node.block(key)
    if arr is None:
        return []
    return [c for c in arr.children if isinstance(c, tf.Node)]


class Geometry:
    """The parts' points the drawing needs. ``bounds(model)`` gives the model's "Bounds Poly"
    (None or [] when unknown or empty; without it objects count as having no polygon)."""

    def __init__(self, level: Level, bounds=None):
        self.level = level
        self.bounds = bounds or (lambda _model: None)
        self._by_name: dict[str, LevelPart] | None = None

    def polygon(self, part: LevelPart):
        """(points, offset) of slot 48/50, or None without a polygon."""
        if part.position is None:
            pts = part.polygon
            return (pts, (0.0, 0.0)) if pts is not None else None
        if not part.model:
            return None
        pts = self.bounds(part.model)
        if pts is None:
            return None
        return list(pts), part.position

    def center(self, part: LevelPart) -> tuple[float, float] | None:
        """LayerPart_Position 0x4fb0a0."""
        pg = self.polygon(part)
        if pg is None:
            return part.position if part.position is not None else _first(part.polygon)
        pts, (ox, oy) = pg
        m = len(pts) - 1 if len(pts) > 1 else len(pts)
        cx = sum(x for x, _ in pts[:m]) / m if m else 0.0
        cy = sum(y for _, y in pts[:m]) / m if m else 0.0
        return ox + cx, oy + cy

    def position(self, part: LevelPart) -> tuple[float, float] | None:
        """Slot 43: the position, for polygon parts the first point."""
        return part.position if part.position is not None else _first(part.polygon)

    def home(self, part: LevelPart) -> tuple[float, float] | None:
        """Slot 40: a character's "Home Pos", otherwise slot 43."""
        if is_kind(part.cls, 'CEntityCharacter') and part.get('Home Pos X') is not None:
            return _f(part.node, 'Home Pos X'), _f(part.node, 'Home Pos Y')
        return self.position(part)

    def facing(self, part: LevelPart) -> float:
        """Slot 46: the movement angle of an animated object (``LevelPart.draw_angle``), 0 for the others."""
        if not is_kind(part.cls, 'CEntityAnimated'):
            return 0.0
        return part.draw_angle

    def find(self, name: str) -> LevelPart | None:
        if self._by_name is None:
            self._by_name = {}
            for p in self.level.parts:
                if p.name:
                    self._by_name.setdefault(p.name.lower(), p)
        return self._by_name.get((name or '').lower())


def _first(pts):
    return pts[0] if pts else None


def _fmt(v: float) -> str:
    return f'{v:g}'


# --- The AIs ---------------------------------------------------------------------------------------

class _Ctx:
    def __init__(self, geo: Geometry, part: LevelPart, groups):
        self.geo, self.part, self.groups = geo, part, groups
        self.out: list[Shape] = []
        self.depth = 0

    def add(self, group: str, pts, color, source: str, anchor: LevelPart | None = None) -> None:
        if pts and (self.groups is None or group in self.groups):
            self.out.append(Shape(group, list(pts), color, anchor or self.part, source))

    def text(self, group: str, at, text: str, color, source: str, font: str = '') -> None:
        if at is not None and (self.groups is None or group in self.groups):
            self.out.append(Shape(group, [at], color, self.part, source, text, font))


def _trigger_done(ai: tf.Node) -> bool:
    return _b(ai, 'Trigger Only Once') and _b(ai, 'Was Triggered')


def _polygon_trigger(ctx: _Ctx, ai: tf.Node) -> None:
    """0x41cfb0 CollideTriggerAI and 0x421b80 CTouchingPolygonTriggerAI: the part's polygon at its
    offset in (200, 205, 25) (the run-time colours of a recent hit or a path left out)."""
    if _trigger_done(ai):
        return
    pg = ctx.geo.polygon(ctx.part)
    if pg is None:
        return
    pts, (ox, oy) = pg
    ctx.add('trigger', outline(pts, ox, oy), YELLOW, f'{ai.value}: Polygon')


def _oval_trigger(ctx: _Ctx, ai: tf.Node) -> None:
    """0x421430 CTouchingOvalTriggerAI: the oval "X Radius", "YX Ratio" at the centre."""
    if _trigger_done(ai):
        return
    c = ctx.geo.center(ctx.part)
    if c is None:
        return
    r, q = _f(ai, 'X Radius'), _f(ai, 'YX Ratio')
    ctx.add('trigger', oval(c, r, q), YELLOW, f'{ai.value}: X Radius={_fmt(r)}, YX Ratio={_fmt(q)}')


def _spawn(ctx: _Ctx, ai: tf.Node) -> None:
    """0x420d00 CSpawnPointAI: with "Set Facing Angle" the arrow of "Facing Angle" (degrees)."""
    if not _b(ai, 'Set Facing Angle'):
        return
    c = ctx.geo.center(ctx.part)
    if c is None:
        return
    a = _f(ai, 'Facing Angle')
    for line in arrow(c, a * DEG):
        ctx.add('spawn', line, YELLOW, f'{ai.value}: Facing Angle={_fmt(a)}')


def sound_lines(c, r0: float, r1: float, r2: float, rolloff: float):
    """CAmbientSoundAI 0x42dd30 without the ovals: the scale above the part, the fall-off curve over
    the silent radius (``rolloff`` = the level's "Rolloff", the listener value 0x713698 that its setter
    0x4e6c50 sets) and the base line. Returns (polyline, (text position, value))."""
    x, y = c
    s = r0 + r1
    top = y - s
    total = r0 + r1 + r2
    pts = [(x, top), (x + s, top)]
    scale = 1.0
    if rolloff == 0:
        pts.append((x + total, top))
    elif r2 > 0:
        t = s
        u = s / rolloff
        while t < total:
            q = s / (u * rolloff)
            scale = q if q <= 1 else 1.0
            pts.append((t + x, y - s * scale))
            t += 1
            u += 1
    end = (x + total, y)
    pts += [end, (x, y)]
    return pts, ((math.trunc(end[0]), math.trunc(end[1]) + 10), math.trunc(scale * 100))


def _sound(ctx: _Ctx, ai: tf.Node) -> None:
    """0x42dd30 CAmbientSoundAI: "Ambient Inner Radius" (green), inner + "Ambient Outer Radius"
    (red) as circles, the scale and fall-off in (180, 255, 24), the fall-off in percent at its end."""
    c = ctx.geo.center(ctx.part)
    if c is None:
        return
    r0, r1, r2 = _f(ai, 'Ambient Inner Radius'), _f(ai, 'Ambient Outer Radius'), _f(ai, 'Max Distance')
    rolloff = _f(ctx.geo.level.root, 'Rolloff', 5.0)
    src = f'{ai.value}: Inner={_fmt(r0)}, Outer={_fmt(r1)}, Max Distance={_fmt(r2)}, Rolloff={_fmt(rolloff)}'
    if r0 > 0:
        ctx.add('sound', oval(c, r0, 1.0), SOUND_INNER, src)
    if r1 > 0:
        ctx.add('sound', oval(c, r0 + r1, 1.0), SOUND_OUTER, src)
    pts, (at, value) = sound_lines(c, r0, r1, r2, rolloff)
    ctx.add('sound', pts, SOUND_SCALE, src)
    ctx.text('sound', at, str(value), SOUND_SCALE, src)


def _approach(ctx: _Ctx, ai: tf.Node) -> None:
    """0x42e730 CApproachTargetAI: a walking entity's "Stop Distance" oval (25, 25, 125)."""
    if not is_kind(ctx.part.cls, 'CEntityWalking'):
        return
    c = ctx.geo.center(ctx.part)
    r = _f(ai, 'Stop Distance')
    if c is not None and r != 0:
        ctx.add('enemy', oval(c, r, Y_RATIO), DARK_BLUE, f'{ai.value}: Stop Distance={_fmt(r)}')


def _companion(ctx: _Ctx, ai: tf.Node) -> None:
    """0x46e990 CCompanionAI: a flying entity's "Minimum Distance" and "Maximum Distance" circles."""
    if not is_kind(ctx.part.cls, 'CEntityFlying'):
        return
    c = ctx.geo.center(ctx.part)
    for key in ('Minimum Distance', 'Maximum Distance'):
        r = _f(ai, key)
        if c is not None and r != 0:
            ctx.add('enemy', oval(c, r, 1.0), DARK_BLUE, f'{ai.value}: {key}={_fmt(r)}')


def _attack(ctx: _Ctx, ai: tf.Node) -> None:
    """0x523730 CNormalAttackAI (with a "MoveBehavior"): "Minimum Attack Distance" (25, 25, 125) and
    plus "Move Buffer Zone" (25, 125, 25)."""
    if _sub(ai, 'MoveBehavior') is None:
        return
    c = ctx.geo.center(ctx.part)
    if c is None:
        return
    r, z = _f(ai, 'Minimum Attack Distance'), _f(ai, 'Move Buffer Zone')
    src = f'{ai.value}: Minimum Attack Distance={_fmt(r)}, Move Buffer Zone={_fmt(z)}'
    if r != 0:
        ctx.add('enemy', oval(c, r, Y_RATIO), DARK_BLUE, src)
    if z != 0:
        ctx.add('enemy', oval(c, z + r, Y_RATIO), GREEN_ATTACK, src)


def _turret(ctx: _Ctx, ai: tf.Node) -> None:
    """0x58e390 CTurretAI (also CSentinonAI, CAutoGunAI): "Start Attack" (200, 205, 25) and plus
    "Stop Attack Extra" (10, 205, 25) (the angles as text left out)."""
    c = ctx.geo.center(ctx.part)
    if c is None:
        return
    a, e = _i(ai, 'Start Attack'), _i(ai, 'Stop Attack Extra')
    src = f'{ai.value}: Start Attack={a}, Stop Attack Extra={e}'
    ctx.add('enemy', oval(c, float(a), Y_RATIO), YELLOW, src)
    ctx.add('enemy', oval(c, float((a + e) & 0xffffffff), Y_RATIO), TURRET_EXTRA, src)


def _damage(ctx: _Ctx, ai: tf.Node) -> None:
    """0x476d00 CDamageExpandingRadiusAI: "Start Radius" (100, 205, 25) and "End Radius"
    (200, 205, 25) with "YX Ratio" (the current radius only exists in the game)."""
    c = ctx.geo.center(ctx.part)
    if c is None:
        return
    q = _f(ai, 'YX Ratio')
    for key, col in (('Start Radius', DAMAGE_START), ('End Radius', YELLOW)):
        r = _f(ai, key)
        ctx.add('area', oval(c, r, q), col, f'{ai.value}: {key}={_fmt(r)}, YX Ratio={_fmt(q)}')


def _landscape(ctx: _Ctx, ai: tf.Node) -> None:
    """0x4e4280 CLandscapeAI (while "Change Rate" > 0): "Width" x "Height" as an oval or a rectangle
    ("Shape") at the position in (60, 205, 60)."""
    if _f(ai, 'Change Rate') <= 0:
        return
    p = ctx.geo.position(ctx.part)
    if p is None:
        return
    w, h = _i(ai, 'Width'), _i(ai, 'Height')
    shape = (ai.get('Shape') or 'Oval').strip()
    src = f'{ai.value}: Width={w}, Height={h}, Shape={shape}'
    if shape.lower() == 'oval':
        if w:
            ctx.add('area', oval(p, w * 0.5, h / w), LANDSCAPE, src)
    elif shape.lower() == 'rectangle':
        x, y = math.trunc(p[0]), math.trunc(p[1])
        hw, hh = (w & 0xffffffff) >> 1, (h & 0xffffffff) >> 1
        ctx.add('area', rect(x - hw, y - hh, hw + x, hh + y), LANDSCAPE, src)


def _scan(ctx: _Ctx, ai: tf.Node) -> None:
    """0x565f40 CScanAreaAI: the arrows of "Starting Angle" (0, 255, 255) and "Ending Angle"
    (255, 255, 0) (degrees, plus "Starting Facing Angle") and of the facing (blue while "Waiting",
    else (255, 128, 0))."""
    c = ctx.geo.center(ctx.part)
    if c is None:
        return
    base = _f(ai, 'Starting Facing Angle')
    a0, a1 = _f(ai, 'Starting Angle'), _f(ai, 'Ending Angle')
    src = f'{ai.value}: Starting Angle={_fmt(a0)}, Ending Angle={_fmt(a1)}, Starting Facing Angle={_fmt(base)}'
    for a, col in ((a0, SCAN_START), (a1, SCAN_END)):
        for line in arrow(c, a * DEG + base):
            ctx.add('scan', line, col, src)
    col = SCAN_FACING_WAITING if _b(ai, 'Waiting') else SCAN_FACING
    for line in arrow(c, ctx.geo.facing(ctx.part)):
        ctx.add('scan', line, col, src)


def _timeout_oval(ctx: _Ctx, ai: tf.Node) -> None:
    """0x4cad40 CDrawTimeoutOvalAI: the oval "Radius", "Aspect Ratio" at the position in (255, 100, 100)."""
    p = ctx.geo.position(ctx.part)
    if p is not None:
        r, q = _f(ai, 'Radius'), _f(ai, 'Aspect Ratio')
        ctx.add('area', oval(p, r, q), TIMEOUT, f'{ai.value}: Radius={_fmt(r)}, Aspect Ratio={_fmt(q)}')


def _old_patrol(ctx: _Ctx, ai: tf.Node) -> None:
    """0x53b300 COldBadPatrolAI: with "Return Home Dist" > 0 its oval around the home."""
    r = _f(ai, 'Return Home Dist')
    h = ctx.geo.home(ctx.part)
    if r > 0 and h is not None:
        ctx.add('patrol', oval(h, r, Y_RATIO), YELLOW, f'{ai.value}: Return Home Dist={_fmt(r)}')


def _patrol_area(ctx: _Ctx, ai: tf.Node) -> None:
    """0x53bbd0/0x53bc10 CPatrolAreaAI: the oval "Radius" around the home."""
    h = ctx.geo.home(ctx.part)
    if h is not None:
        r = _f(ai, 'Radius')
        ctx.add('patrol', oval(h, r, Y_RATIO), YELLOW, f'{ai.value}: Radius={_fmt(r)}')


_TURNING_ORDERS = ('back and forth', 'forth and back', 'go to end')     # enum 0, 1, 4


def _patrol_path(ctx: _Ctx, ai: tf.Node) -> None:
    """0x53cae0 CPatrolPathAI, CFollowPathAI: the outline of the "Path Poly" part (polygon of at least
    two points; one point less for the orders that turn or stop, one more with "Ignore last point")
    and a 3 x 3 square at "Target Point". The shapes move with the path part."""
    name = ai.get('Path Poly') or ''
    path = ctx.geo.find(name)
    pg = ctx.geo.polygon(path) if path is not None else None
    if pg is None or len(pg[0]) < 2:
        return
    pts, (ox, oy) = pg
    order = (ai.get('Order') or 'Back and forth').strip().lower()
    skip = (1 if order in _TURNING_ORDERS else 0) + (1 if _b(ai, 'Ignore last point') else 0)
    src = f'{ai.value}: Path Poly={name}, Order={ai.get("Order") or ""}'
    ctx.add('patrol', outline(pts, ox, oy, skip), YELLOW, src, anchor=path)
    i = _i(ai, 'Target Point', -1)
    if 0 <= i < len(pts):
        x, y = math.trunc(pts[i][0] + ox), math.trunc(oy + pts[i][1])
        ctx.add('patrol', rect(x - 1, y - 1, x + 2, y + 2), YELLOW, src + f', Target Point={i}', anchor=path)


_SKELETON_STATE_AI = {'patrol': 'Patrol AI', 'pursue': 'Pursue AI', 'attack': 'Attack AI',
                      'investigate': 'Investigate AI'}


def _skeleton(ctx: _Ctx, ai: tf.Node) -> None:
    """0x577030 CSkeletonAI: the facing arrow (200, 205, 25), the AI of the state and the state's name
    in "Small Blue". Begin (0x576200) always sets "Patrol", so that state is shown (the stored "State"
    is the last one of the internal editor's run, mostly "Any")."""
    c = ctx.geo.center(ctx.part)
    if c is None:
        return
    for line in arrow(c, ctx.geo.facing(ctx.part)):
        ctx.add('enemy', line, YELLOW, translate('overlays', '{ai}: facing direction').format(ai=ai.value))
    sub = _sub(ai, _SKELETON_STATE_AI['patrol'])
    if sub is not None:
        _draw(ctx, sub)
    ctx.text('enemy', (math.trunc(c[0]), math.trunc(c[1])), 'Patrol', (90, 120, 255), f'{ai.value}: State',
             'Small Blue')


def _series(ctx: _Ctx, ai: tf.Node) -> None:
    """0x56cd20 CSeriesAI: the current AI ("Current AI" of "AIs")."""
    els = _elements(ai, 'AIs')
    i = _i(ai, 'Current AI', -1)
    if 0 <= i < len(els):
        _draw(ctx, els[i])


def _simultaneous(ctx: _Ctx, ai: tf.Node) -> None:
    """0x4cbaa0 CSimultaneousAIsAI: every AI of "AIs"."""
    for el in _elements(ai, 'AIs'):
        _draw(ctx, el)


def _one(key: str):
    def draw(ctx: _Ctx, ai: tf.Node) -> None:
        sub = _sub(ai, key)
        if sub is not None:
            _draw(ctx, sub)
    return draw


DRAWERS = {
    'CTouchingOvalTriggerAI': _oval_trigger,
    'CTouchingPolygonTriggerAI': _polygon_trigger,
    'CollideTriggerAI': _polygon_trigger,
    'CSpawnPointAI': _spawn,
    'CAmbientSoundAI': _sound,
    'CApproachTargetAI': _approach,
    'CCompanionAI': _companion,
    'CNormalAttackAI': _attack,
    'CTurretAI': _turret, 'CSentinonAI': _turret, 'CAutoGunAI': _turret,
    'CDamageExpandingRadiusAI': _damage,
    'CLandscapeAI': _landscape,
    'CScanAreaAI': _scan,
    'CDrawTimeoutOvalAI': _timeout_oval,
    'COldBadPatrolAI': _old_patrol, 'CPatrolAI': _old_patrol,
    'CPatrolAreaAI': _patrol_area,
    'CPatrolPathAI': _patrol_path, 'CFollowPathAI': _patrol_path,
    'CSkeletonAI': _skeleton,
    'CSeriesAI': _series,
    'CSimultaneousAIsAI': _simultaneous,
    'CWhileAI': _one('What to do while waiting'),          # 0x4cbf10
    'CForceUpdatingAI': _one('AI To Force'),                # 0x4ccc30
    'CTemporaryTaskAI': _one('Temporary AI'),               # 0x58b430
    'CChaseInvestigateAI': _one('Investigate AI'),          # 0x46c4b0 (its state text left out)
    'CScanInvestigateAI': _one('AI'),                       # 0x5663d0
}


def _draw(ctx: _Ctx, ai: tf.Node) -> None:
    f = DRAWERS.get(ai.value)
    if f is None or ctx.depth > 16:
        return
    ctx.depth += 1
    try:
        f(ctx, ai)
    finally:
        ctx.depth -= 1


def activity(part: LevelPart) -> list[tf.Node]:
    """The AIs of the object's "Activity"."""
    return _elements(part.node, 'Activity')


def part_shapes(geo: Geometry, part: LevelPart, groups=None) -> list[Shape]:
    """The overlay shapes of one part (``groups``: a set of GROUPS, None = all)."""
    ctx = _Ctx(geo, part, groups)
    for ai in activity(part):
        _draw(ctx, ai)
    return ctx.out


def has_overlay(part: LevelPart) -> bool:
    """Does the part have an AI the overlays know (without looking at the fields)?"""
    return any(ai.value in DRAWERS for ai in activity(part))
