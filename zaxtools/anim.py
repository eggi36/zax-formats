"""Animation of the objects as Zax.exe plays it: which frame a layer shows, how it advances, and
whether the object rests (is drawn into the cached background).

Ported from the reimplementation (zax-decomp/reimpl/src/entities.cpp, sequence_player.cpp, entity_draw.cpp,
ai_behaviors.cpp, ai_slots.cpp) [confirmed: code]:

- **The frame of a layer** (``CRotationSequence_FrameIndex`` 0x55fee0, called by
  ``DrawRotationSequenceLayers`` 0x4886a0 with the entity's frame index, slot 85): a layer with one
  frame per rotation always shows frame 0; a frame index at or past the layer's frames draws nothing;
  a layer with "Auto-Animate" (switch bit 0x80) takes its frame from the game time instead:
  ``fistp(float(ticks * fps * 0.001 + (offset & 0x7fff))) % frames`` with ``ticks`` the tick count
  in ms (``GetTickCount & 0xffffff``, 0x4d2650) and ``offset`` chosen by ``Layer_DrawDirect``
  0x4e9d80: drawing "directly" the rounded position X + Y ``Entity_Draw`` 0x488d70 passes (slots
  52/53), otherwise the address of the root entity; 0 with "Sync The Auto Animation"
  (bit 0x100). In the game the offsets are the addresses [verified 2026-10-29, ``Test/Anim``, started
  through the launcher and through the main menu: three Hydro Lights 137 pixels apart show frames
  whose differences no function of the position explains, constant within a run, different between
  runs], so the phases between objects cannot be reproduced; this module uses the position sum (what
  drawing directly would use) as a fixed stand-in. Every layer uses the rotation of the facing angle.
- **The entity's frame index**: ``CEntityBase`` has none (slot 85 is ``0x4011e0``, always 0), so its
  layers without "Auto-Animate" stand still at frame 0 for good (an empty frame 0 draws nothing).
  ``CEntityAnimated`` and the classes derived from it keep "Current Frame" (+0xbc, the index +0xc0 its
  floor), brought into the current sequence's frames when read (``SetFrame`` 0x48feb0); it only moves
  while a behaviour plays the sequence:
  - ``CPlaySequenceLoopedAI`` (``Begin`` 0x4cb590 when the part is activated, ``Update`` 0x4cb5c0;
    the embedded ``CEntityBehaviorPlaySequenceLooped``: ``Begin`` 0x499d10 plays its "Sequence" (when
    not empty) from frame 0 and sets "Playing", ``Update`` 0x499d50 moves the frame by the sequence's
    frames per second, backwards with "Playing Backwards", turning at the ends with "Ping Pong", or
    the frame of the game time with "Synchronize" (0x55e4b0, no offset)). Neither runs for a part
    with ``Active=0`` (``CEntityAnimated::Update`` 0x48f300).
  - ``CEntityBehaviorIdle`` (0x498fa0/0x4990e0): characters idling play "Idle" at fps x "Play Ratio"
    x a random 0.9-1.1 from a random start frame. Which characters idle at level start depends on
    their AIs; this module counts every character class with an "Activity" as idling [assumption:
    their AIs begin with the idle behaviour, e.g. the move behaviour's end 0x430f20, the patrol's
    0x498f10]; the random start frame and ratio are not reproducible (still image: "Current Frame",
    ratio 1).
- **Resting** (draw item byte +0x24 = 0, ``DrawRotationSequenceLayers``): an entry rests when its
  entity carries "Stationary" (flag 0x200000), the layer has no "Auto-Animate", the fade (slot 92) is
  at least 1 and the ghost flag 0x400000 is missing. All objects of the original levels are saved
  with "Stationary=1"; the playing behaviours clear it on every update (``PlayLooped_Update``,
  ``Idle_Start`` - a walking character's idle restarts every update, so a standing character never
  rests; the player's control 0x543b60 runs its own idle behaviour), ``CEntityBase`` sets it again
  after every drawing (0x488f18). Resting ground entries are drawn into the tile cache with the
  ground (``CPlasmaTileMap`` 0x540b80 -> 0x4e8ce0/0x4e8b60), the others every frame in the changed
  tiles above it (``World_DrawDirtyTiles`` 0x4e8080: the non-resting ground entries, then all
  object entries). So a moving shadow lies above every resting ground part (water with any
  "YSort") - docs/OPEN_ISSUES.md 16.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from . import textformat as tf
from .level import LevelPart
from .mdl import Model, Sequence

# Classes derived from CEntityAnimated / CEntityCharacter (zax-decomp/docs/classes.csv, the parent chain)
ANIMATED = frozenset({'CEntityAnimated', 'CEntityAnimatedUpperBody', 'CEntityCharacter', 'CEntityFlying',
                      'CEntityMovable', 'CEntityOm', 'CEntityOverlayWalking', 'CEntityProjectile',
                      'CEntityStationaryCharacter', 'CEntityWalking'})
CHARACTERS = frozenset({'CEntityCharacter', 'CEntityFlying', 'CEntityOm', 'CEntityOverlayWalking',
                        'CEntityStationaryCharacter', 'CEntityWalking'})

TICK_MASK = 0xffffff         # 0x4d2650: the tick count's low 24 bits
OFFSET_MASK = 0x7fff         # timed_frame: the offset's low 15 bits


@dataclass
class Loop:
    """The behaviour of a ``CPlaySequenceLoopedAI``."""
    sequence: str               # '' = the current sequence
    backwards: bool = False
    ping_pong: bool = False
    synchronize: bool = False


@dataclass
class PartAnim:
    """How an object animates in the game."""
    animated: bool              # a CEntityAnimated (own frame index); False: CEntityBase, frame 0
    sequence: str | None        # the sequence the game shows (a looped AI's replaces "Cur Sequence")
    frame: float = 0.0          # the frame at level start (fraction kept, index = floor)
    loop: Loop | None = None
    idle: bool = False          # a character idling [assumption, see the module text]
    phase: int = 0              # offset of the "Auto-Animate" layers: X + Y as a stand-in (module text)

    @property
    def moving(self) -> bool:
        """The behaviours clear "Stationary" on every update: the object never rests."""
        return self.loop is not None or self.idle


def fistp(v: float) -> int:
    """x87 ``fistp`` in the default rounding mode: to nearest, ties to even."""
    return int(np.rint(v))


def phase_of(part: LevelPart) -> int:
    """Position X + Y rounded as the exe keeps them (+0x54/+0x58, fistp of the floats)."""
    pos = part.position
    if pos is None:
        return 0
    return fistp(np.float32(pos[0])) + fistp(np.float32(pos[1]))


def timed_frame(seconds: float, fps: float, offset: int) -> int:
    """0x55e4b0/0x55e500 without the modulo: the frame of a synchronised sequence at the game time."""
    ticks = int(math.floor(seconds * 1000)) & TICK_MASK
    return fistp(np.float32(ticks * float(np.float32(fps)) * 0.001 + (offset & OFFSET_MASK)))


def wrap_frame(f: float, n: int) -> float:
    """``SetFrame`` 0x48feb0: the frame brought into the sequence's frames (the fraction for fewer than
    two)."""
    if not math.isfinite(f):
        return 0.0          # the game hangs or ends here (zax-decomp/docs/ORIGINAL_BUGS.md, the level check)
    if n < 2:
        return f - math.floor(f)
    while f < 0:
        f += n
    while f >= n:
        f -= n
    return f


def _bit(node: tf.Node, key: str, default: str = '0') -> bool:
    return (node.get(key, default) or default).strip() not in ('0', '')


def _looped_ais(part: LevelPart) -> list[tf.Node]:
    """The ``CPlaySequenceLoopedAI`` of the object's "Activity" (also inside a CSimultaneousAIsAI)."""
    out = []

    def walk(arr: tf.Node | None, depth: int) -> None:
        if arr is None or depth > 8:
            return
        for e in arr.array_elements():
            if not isinstance(e, tf.Node):
                continue
            if e.value == 'CPlaySequenceLoopedAI':
                out.append(e)
            elif e.value == 'CSimultaneousAIsAI':
                walk(e.block('AIs'), depth + 1)
    walk(part.node.block('Activity'), 0)
    return out


def part_animation(part: LevelPart, model: Model | None) -> PartAnim:
    """The animation of an object at level start."""
    seq_name = part.sequence
    if part.cls not in ANIMATED:
        return PartAnim(False, seq_name, phase=phase_of(part))
    cur = model.sequence(seq_name or '') if model is not None else None
    n = cur.frames_per_rotation if cur is not None else 1
    try:
        f = float(part.get('Current Frame') or 0)
    except ValueError:
        f = 0.0
    a = PartAnim(True, seq_name, wrap_frame(f, n), phase=phase_of(part))
    active = part.get('Active', '1') != '0'
    if not active:
        return a
    for ai in _looped_ais(part):
        b = ai.block('Behavior')
        if b is None:
            continue
        name = (b.get('Sequence') or '').strip()
        playing = _bit(b, 'Playing', '1')
        if name:
            # PlaySequence 0x48f700: a sequence the model lacks leaves the current one; the frame is 0
            # either way, and Begin sets "Playing"
            if model is not None and model.sequence(name) is not None:
                a.sequence = model.sequence(name).name
            a.frame = 0.0
            playing = True
        if playing:
            a.loop = Loop(name, _bit(b, 'Playing Backwards'), _bit(b, 'Ping Pong'), _bit(b, 'Synchronize'))
        break
    if a.loop is None and part.cls in CHARACTERS and part.node.block('Activity') is not None \
            and any(isinstance(e, tf.Node) for e in part.node.block('Activity').array_elements()):
        a.idle = True
    return a


def entity_frame(a: PartAnim, n: int, fps: float, t: float | None) -> float:
    """The entity's frame ("Current Frame") at ``t`` seconds after level start (None: at the start)
    in a sequence of ``n`` frames per rotation."""
    if not a.animated:
        return 0.0
    f = a.frame
    if t is None or n < 2 or fps <= 0 or not a.moving:
        return f
    if a.loop is not None and a.loop.synchronize:
        return float(timed_frame(t, fps, 0) % n)
    if a.loop is not None:
        p = f - fps * t if a.loop.backwards else f + fps * t
        if a.loop.ping_pong:
            m = p % (2 * n)
            return m if m < n else 2 * n - m
        return p % n
    return (f + fps * t) % n          # idle, ratio 1 [assumption]


def frame_index(a: PartAnim, current: Sequence | None, t: float | None) -> int:
    """The entity's frame index (slot 85): floor of the frame, 0 for a CEntityBase."""
    if not a.animated or current is None:
        return 0
    return int(math.floor(entity_frame(a, current.frames_per_rotation, current.fps, t)))


def layer_frame(s: Sequence, a: PartAnim, index: int, t: float | None) -> int | None:
    """0x55fee0: the frame (within the rotation) a layer shows for the entity's frame index; None draws
    nothing. ``t`` None: the game time 0 for the "Auto-Animate" layers (the tick count at level start
    is not known)."""
    n = s.frames_per_rotation
    if n == 1:
        return 0
    if index >= n or index < 0:
        return None
    if s.auto_animate:
        return timed_frame(t or 0.0, s.fps, 0 if s.sync_auto else a.phase) % n
    return index


def timed_next(seconds: float, fps: float, offset: int) -> float:
    """The first time after ``seconds`` at which ``timed_frame(t, fps, offset)`` gives another frame (it moves
    on whole milliseconds only); inf if it never changes. Exact: the candidate milliseconds are evaluated with
    the same arithmetic as ``timed_frame`` (if no change turns up within two frame periods - float32 rounding
    of a large sum can hold a frame a little longer - the end of that range is returned, to look again)."""
    f32 = float(np.float32(fps))
    if not f32 or not math.isfinite(f32):
        return math.inf
    ticks = int(math.floor(seconds * 1000))
    off = offset & OFFSET_MASK
    now = np.rint(np.float32((ticks & TICK_MASK) * f32 * 0.001 + off))
    span = int(math.ceil(2000 / abs(f32))) + 4
    cand = np.arange(ticks + 1, ticks + 1 + span, dtype=np.int64)
    x = np.rint(((cand & TICK_MASK) * f32 * 0.001 + off).astype(np.float32))
    hit = np.flatnonzero(x != now)
    tick = int(cand[hit[0]]) if len(hit) else int(cand[-1])
    return (tick + 0.5) / 1000          # inside that millisecond: floor(t * 1000) == tick


def entity_next(a: PartAnim, current: Sequence | None, t: float | None) -> float:
    """The first time after ``t`` at which ``frame_index(a, current, ·)`` can change; inf if it stands still
    (a tiny bit after the exact moment, so the frame has turned by then)."""
    if not a.animated or current is None or t is None:
        return math.inf
    n, fps = current.frames_per_rotation, current.fps
    if n < 2 or fps <= 0 or not a.moving:
        return math.inf
    if a.loop is not None and a.loop.synchronize:
        return timed_next(t, fps, 0)
    # f + fps * t (backwards: f - fps * t) - with ping-pong as well - turns its floor at whole numbers only
    if a.loop is not None and a.loop.backwards:
        p = a.frame - fps * t
        k = math.ceil(p) - 1
        nxt = (a.frame - k) / fps
    else:
        p = a.frame + fps * t
        k = math.floor(p) + 1
        nxt = (k - a.frame) / fps
    return max(nxt, t) + 1e-6


def layer_next(s: Sequence, a: PartAnim, t: float | None) -> float:
    """The first time after ``t`` at which the "Auto-Animate" frame of layer ``s`` (``layer_frame``) can
    change; inf for the other layers (they follow the entity's frame index, ``entity_next``)."""
    if t is None or s.frames_per_rotation == 1 or not s.auto_animate:
        return math.inf
    return timed_next(t, s.fps, 0 if s.sync_auto else a.phase)


def layer_resting(s: Sequence, a: PartAnim) -> bool:
    """Draw item byte +0x24 = 0: "Stationary" kept and no "Auto-Animate" (fade 1, no ghost flag)."""
    return not a.moving and not s.auto_animate


def layer_animated(s: Sequence, a: PartAnim) -> bool:
    """Does the layer change its frame while the game runs?"""
    if s.frames_per_rotation < 2:
        return False
    return s.auto_animate or (a.animated and a.moving)


# The AIs that make an upper body show its parent's sequence and frame (CSameAsParentAI and the class
# derived from it, zax-decomp/docs/classes.csv)
SAME_AS_PARENT = frozenset({'CSameAsParentAI', 'CWalkingUpperBodyAI'})


def _same_as_parent_ai(part: LevelPart) -> tf.Node | None:
    act = part.node.block('Activity')
    if act is None:
        return None
    return next((e for e in act.array_elements() if isinstance(e, tf.Node) and e.value in SAME_AS_PARENT), None)


def child_animation(child: LevelPart, model: Model | None, parent: PartAnim) -> PartAnim | None:
    """The animation of a child object (``LevelPart.children``). A child with a ``CSameAsParentAI``
    (the upper bodies' ``CWalkingUpperBodyAI``) shows its parent's sequence by name and its frame
    (``CSameAsParentAI::Update`` 0x562010; "Only Show First Sequence" plays sequence 0) [confirmed:
    code, zax-decomp/reimpl/src/ai_rest_d.cpp; VM]; a sequence the child's model lacks hides it (None). "Force
    Invisable" (0 in every original level) is not taken into account. Other children animate on their
    own like any object."""
    ai = _same_as_parent_ai(child)
    if ai is None:
        return part_animation(child, model)
    if model is None:
        return None
    if _bit(ai, 'Only Show First Sequence'):
        seqs = model.sequences
        name = seqs[0].name if seqs else None
    else:
        s = model.sequence(parent.sequence or '')
        name = s.name if s is not None else None
    if name is None:
        return None
    return PartAnim(True, name, parent.frame, parent.loop, parent.idle, phase=parent.phase)


def child_facing(child: LevelPart, parent: LevelPart) -> float:
    """The rotation angle of a child (``parent``: its root, the part of the Tree List; for a direct child the
    same): an upper body turns with its root. The code
    (``CEntityAnimatedUpperBody`` slot 46 0x4943b0) takes the root's facing angle while it synchronises
    aiming and moving and the upper body updates, otherwise the root's aiming angle [confirmed: code,
    zax-decomp/reimpl/src/entity_classes.cpp; VM]; in the game at level start the upper bodies showed the root's
    drawn angle ("Movement Angle") whatever "Aiming Angle" and "Synch Aiming And Moving" said [verified
    2026-10-29, VM: run 20261029-214817-a56f], so that is used. Other children use their own angle."""
    if child.cls != 'CEntityAnimatedUpperBody':
        return child.draw_angle
    return parent.draw_angle
