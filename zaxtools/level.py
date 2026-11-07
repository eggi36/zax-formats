"""Level (.zax) as an editable object.

The .zax is a text tree (zaxtools.textformat). This class offers convenient access to the parts
that matter for an editor, but always writes back into the tree - unknown fields are therefore
kept unchanged.

Path conventions (relative to Data/):
    Levels/<Partial File Name>.zax / .way      level and way points
    Cache/Levels/<Partial File Name>.frm16     mini map
    Cache/Models/<Model>.mdl16                 models
    Cache/Textures/<Texture>.frm16             ground and polygon textures
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from . import textformat as tf


@dataclass
class LevelPart:
    """An object of the Tree List. Reads/writes directly in the text tree."""
    node: tf.Node

    @property
    def cls(self) -> str:
        return self.node.value

    def get(self, key: str, default: str | None = None) -> str | None:
        return self.node.get(key, default)

    def set(self, key: str, value) -> None:
        self.node.set(key, value)

    name = property(lambda s: s.get('Name', ''), lambda s, v: s.set('Name', v))
    model = property(lambda s: s.get('Model'), lambda s, v: s.set('Model', v))
    sequence = property(lambda s: s.get('Cur Sequence'), lambda s, v: s.set('Cur Sequence', v))

    @property
    def facing_angle(self) -> float:
        """Facing direction in radians (only animated/movable objects, otherwise 0)."""
        return float(self.get('Start FacingAngle', '0') or 0)

    @property
    def draw_angle(self) -> float:
        """The angle the game draws the object with (its rotation): ``CEntityAnimated`` slot 46 0x48fc50,
        the movement angle (+0xc8), turned by pi while "Facing Backwards" is set. Reading "Movement Angle"
        or "Aiming Angle" from the level sets the movement angle (their setter 0x48e8f0); "Start
        FacingAngle" has no setter and is only stored [confirmed: code, zax-decomp/reimpl/src/entities.cpp; VM]; so the
        last of the two in the file wins ("Movement Angle" follows "Aiming Angle"), and without either it
        stays the constructor's 0. In the game the objects of the original levels turn by "Movement
        Angle", not by "Start FacingAngle" [verified 2026-10-29, VM: test level GTChild2, run
        20261029-214817-a56f, seven Rogcoils with the three angles varied]. "Facing Backwards" computed from
        movement and aiming (0x48f260) is left out: only the stored flag counts [assumption]."""
        def num(key):
            v = self.get(key)
            try:
                return None if v is None else float(v)
            except ValueError:
                return None
        m = num('Movement Angle')
        if m is None:
            m = num('Aiming Angle')
        if m is None:
            m = 0.0
        if (self.get('Facing Backwards', '0') or '0').strip() not in ('0', ''):
            m = (m + math.pi) % (2 * math.pi)
        return m

    @property
    def visible(self) -> bool:
        return self.get('Visible', '1') != '0'

    @property
    def rendering_height(self) -> float:
        """Height above the ground in pixels: the game draws all layers without "Render On Ground"
        that much higher, shadows and ground light stay on the ground [verified 2026-10-20:
        Light Beam 1 with 32]."""
        v = self.get('Rendering Height Float') or self.get('Rendering Height') or '0'
        try:
            return float(v)
        except ValueError:
            return 0.0

    @property
    def drawn_in_game(self) -> bool:
        """Does the game draw the object? Not with ``Visible=0`` and not for ``CEntityAnimated`` with
        ``Active=0`` (effects that scripts switch on via CActivateAction; in the game they then
        also have no collision and cannot be shot) [verified 2026-10-20: Test/Licht and
        Test/Aktiv, 11 models each on/off]."""
        if not self.visible:
            return False
        return not (self.cls == 'CEntityAnimated' and self.get('Active', '1') == '0')

    @property
    def position(self) -> tuple[float, float] | None:
        x, y = self.get('Position X'), self.get('Position Y')
        return None if x is None or y is None else (float(x), float(y))

    @position.setter
    def position(self, xy) -> None:
        self.set('Position X', _num(xy[0]))
        self.set('Position Y', _num(xy[1]))

    @property
    def polygon(self) -> list[tuple[float, float]] | None:
        p = self.get('Polygon')
        if p is None:
            return None
        v = [float(t) for t in p.split(',') if t.strip()]
        return list(zip(v[0::2], v[1::2]))

    @polygon.setter
    def polygon(self, pts) -> None:
        self.set('Polygon', ', '.join(f'{_num(x)}, {_num(y)}' for x, y in pts))

    @property
    def children(self) -> list['LevelPart']:
        """The objects of the "Child List" (``CChildList`` +8): upper bodies of characters, effects on
        a staff, items a character carries. In the original levels 1,354 children in 76 levels, none
        with children of its own [verified 2026-10-29]. The game draws them with the parent: their
        position and "Rendering Height" are added to the parent's (``CLayerPart`` slot 23 0x4fa9a0
        draws every child flagged visible with the position ``Entity_Draw`` 0x488d70 moved by the
        parent's slots 52-54) [confirmed: code, zax-decomp/reimpl/src/entity_draw.cpp, layer_parts.cpp; VM]; a
        child's own children likewise from the child [verified 2026-10-30, VM, docs/FORMATS.md
        "Composite characters"]."""
        block = self.node.block('Child List')
        if not isinstance(block, tf.Node):
            return []
        arr = block.block('Child List')
        if not isinstance(arr, tf.Node):
            return []
        return [LevelPart(e) for e in arr.items('Child') if isinstance(e, tf.Node)]

    def shift(self, dx: float, dy: float) -> None:
        """Move by (dx, dy): position or polygon points. Only changed lines are rewritten.
        ``Home Pos`` equals ``Position`` in all 3,245 original cases [verified] and is then moved
        along."""
        pos = self.position
        if pos is not None:
            x, y = pos
            home = (self.get('Home Pos X'), self.get('Home Pos Y'))
            follow = home[0] is not None and home[1] is not None and (float(home[0]), float(home[1])) == (x, y)
            for axis, old, d in (('X', x, dx), ('Y', y, dy)):
                if d:
                    self.set(f'Position {axis}', _num(old + d))
                    if follow:
                        self.set(f'Home Pos {axis}', _num(old + d))
        elif self.polygon is not None and (dx or dy):
            self.polygon = [(x + dx, y + dy) for x, y in self.polygon]


def _num(v) -> str:
    """Write a number as in the original: integers without decimals, otherwise the shortest
    representation (rounded to 6 digits against float noise)."""
    v = round(float(v), 6)
    return str(int(v)) if v.is_integer() else repr(v)


num = _num


class Level:
    def __init__(self, doc: tf.Node):
        self.doc = doc
        self.root = tf.root(doc)

    # --- Load/save -----------------------------------------------------------
    @classmethod
    def from_bytes(cls, data: bytes) -> 'Level':
        return cls(tf.load_bytes(data))

    def to_bytes(self) -> bytes:
        return tf.dump_bytes(self.doc)

    # --- Header data ---------------------------------------------------------
    @property
    def size(self) -> tuple[int, int]:
        return int(self.root.get('Width', '0')), int(self.root.get('Height', '0'))

    @property
    def partial_file_name(self) -> str:
        return self.root.get('Partial File Name', '')

    @property
    def description(self) -> str:
        return self.root.get('Map Description', '')

    # --- Objects -------------------------------------------------------------
    @property
    def tree_list(self) -> tf.Node:
        return self.root.block('Tree List')

    @property
    def parts(self) -> list[LevelPart]:
        return [LevelPart(n) for n in self.tree_list.items('Level Part') if isinstance(n, tf.Node)]

    def find(self, name: str) -> LevelPart | None:
        return next((p for p in self.parts if p.name == name), None)

    def part_index(self, part: LevelPart) -> int:
        """Position of the object in ``tree_list.children``."""
        return next(i for i, c in enumerate(self.tree_list.children) if c is part.node)

    def insert_part(self, node: tf.Node, index: int | None = None) -> LevelPart:
        """Insert an object (``Level Part`` node), without index after the last object. The Tree
        List (``CSortList2D``) has no counter. Whether the order matters to the game is
        unverified [assumption: no]."""
        if node.key != 'Level Part':
            raise ValueError('not a Level Part')
        ch = self.tree_list.children
        if index is None:
            last = [i for i, c in enumerate(ch) if isinstance(c, tf.Node) and c.key == 'Level Part']
            index = last[-1] + 1 if last else len(ch)
        ch.insert(index, node)
        return LevelPart(node)

    def remove_part(self, part: LevelPart) -> int:
        """Remove an object; returns its previous position (for undo)."""
        i = self.part_index(part)
        del self.tree_list.children[i]
        return i

    # --- Ground (Plasma Ground) -----------------------------------------------
    @property
    def plasma(self) -> tf.Node:
        return self.root.block('Plasma Ground')

    @property
    def ground_textures(self) -> list[str]:
        p = self.plasma
        n = int(p.get('Num Textures', '0'))
        return [p.get(f'Texture {i}') for i in range(n)]

    @ground_textures.setter
    def ground_textures(self, names: list[str]) -> None:
        """Replace the texture list: ``Num Textures`` and ``Texture i`` at their place in the block
        (new entries after the last ``Texture``, surplus ones removed). The grid stays unchanged;
        the caller has to convert it."""
        p = self.plasma
        p.set('Num Textures', str(len(names)))
        key = lambda i: f'Texture {i}'
        old = [c for c in p.children if isinstance(c, tf.Entry) and c.key.startswith('Texture ')]
        for c in old:
            if c.key not in {key(i) for i in range(len(names))}:
                p.children.remove(c)
        last = p.children.index(p.item('Num Textures'))
        for i, name in enumerate(names):
            it = p.item(key(i))
            if it is None:
                it = tf.Entry(key(i), name)
                p.children.insert(last + 1, it)
            it.value = name
            last = p.children.index(it)

    def _grid(self, kind: str) -> np.ndarray:
        rows = []
        i = 0
        while (v := self.plasma.get(f'{kind} Row {i}')) is not None:
            rows.append(list(bytes.fromhex(v)))
            i += 1
        return np.array(rows, np.uint8)

    def _set_grid(self, kind: str, g: np.ndarray) -> None:
        for i, row in enumerate(np.asarray(g, np.uint8)):
            self.plasma.set(f'{kind} Row {i}', bytes(row).hex().upper())

    elevations = property(lambda s: s._grid('Elevations'), lambda s, g: s._set_grid('Elevations', g))
    seeds = property(lambda s: s._grid('Seeds'), lambda s, g: s._set_grid('Seeds', g))

    # --- Mini map ----------------------------------------------------------------
    def minimap_transform(self):
        """Function world (x, y) -> mini map pixel (px, py)."""
        g = lambda k: float(self.root.get(k, '0'))
        sx, ox, sy, oy = g('MiniMap X Scale'), g('MiniMap X Offset'), g('MiniMap Y Scale'), g('MiniMap Y Offset')
        return lambda x, y: (x * sx + ox, y * sy + oy)


GRID_CELL = 64   # spacing of the Plasma Ground grid points in world pixels
