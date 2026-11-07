"""Transitions between levels (exit -> start point in another level).

Built as in the original levels [verified: 182 of 286 ``CRelocateAction``]: an invisible object
``Editor/Trigger Icon, Proximity`` with ``CTouchingOvalTriggerAI``; its ``Enter Action`` is a
``CRelocateAction``:

    New Map Name=ACT 1/M1m2/01 TargDens     target level (Partial File Name)
    New Location=Den2 Spawn                 name of a start point in the target level
    Who To Switch=$Instigator               whoever triggers it (264 of 286)
    Return to map=definitely soon           most frequent value (136 of 286); cache, see below
    Relative Position=0                     most frequent value (227 of 286)

``Return to map`` tells the game what happens to the level left behind in the cache [confirmed:
Zax.exe, map switch 0x59b400, list 0x625388]: ``definitely soon`` stays loaded, ``probably soon``
stays loaded and moves to the end of the list (most recently used), ``unlikely soon`` like
``CFlushMapAction`` (out of the list of loaded levels), ``never`` like ``CExpireMapAction`` (the
level expires). The game reports ``Invalid setting!`` (value 0) as an error.

The target is almost always an ``Editor/Spawn Point`` with ``CSpawnPointAI`` (322 of 336 resolved
targets). Trigger and start point themselves come as default objects from the model header
(``catalog.make_node``); only the action is inserted here.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import textformat as tf
from .level import Level, LevelPart
from .links import OTHER_MAP_ACTIONS, REF_KEYS, _refs, names_in

TRIGGER_MODEL = 'Editor/Trigger Icon, Proximity'
SPAWN_MODEL = 'Editor/Spawn Point'
ACTION = 'CRelocateAction'
MAP_ACTIONS = ('CRelocateAction', 'CSwitchMapAction', 'CTeleportAction')
# values in the levels (without "Invalid setting!"), most frequent first [verified]
RETURN_TO_MAP = ['definitely soon', 'unlikely soon', 'probably soon', 'never']


def relocate_action(map_name: str, location: str, return_to_map: str = RETURN_TO_MAP[0]) -> tf.Node:
    """``Enter Action=CRelocateAction`` with the fields in the order used by the levels."""
    node = tf.Node('Enter Action', ACTION)
    for k, v in (('New Map Name', map_name), ('New Location', location), ('Who To Switch', '$Instigator'),
                 ('Return to map', return_to_map), ('Relative Position', '0')):
        node.children.append(tf.Entry(k, v))
    return node


def _trigger_ai(part_node: tf.Node) -> tf.Node | None:
    act = part_node.block('Activity')
    if act is None:
        return None
    return next((c for c in act.children if isinstance(c, tf.Node) and c.value == 'CTouchingOvalTriggerAI'), None)


def make_exit(trigger: tf.Node, map_name: str, location: str, return_to_map: str = RETURN_TO_MAP[0]) -> None:
    """Replace the (empty) ``Enter Action`` in the trigger's default object with the transition."""
    ai = _trigger_ai(trigger)
    if ai is None:
        raise ValueError('trigger without CTouchingOvalTriggerAI (default object missing - Zax.exe needed)')
    old = ai.item('Enter Action')
    if old is None:
        raise ValueError('CTouchingOvalTriggerAI without Enter Action')
    ai.children[ai.children.index(old)] = relocate_action(map_name, location, return_to_map)


def spawn_points(level: Level) -> list[LevelPart]:
    """Named start points (model ``Editor/Spawn Point`` or with ``CSpawnPointAI``)."""
    out = []
    for p in level.parts:
        if not p.name:
            continue
        act = p.node.block('Activity')
        has_ai = act is not None and any(isinstance(c, tf.Node) and c.value == 'CSpawnPointAI' for c in act.children)
        if p.model == SPAWN_MODEL or has_ai:
            out.append(p)
    return out


@dataclass
class Exit:
    part: LevelPart          # object with the script
    action: str              # CRelocateAction / CSwitchMapAction / CTeleportAction
    map_name: str
    location: str


def exits(part: LevelPart) -> list[Exit]:
    """Transitions to other levels in the object's script."""
    out = []

    def walk(node: tf.Node):
        for c in node.children:
            if isinstance(c, tf.Node):
                if c.value in MAP_ACTIONS and c.get('New Map Name'):
                    out.append(Exit(part, c.value, c.get('New Map Name'), c.get('New Location', '')))
                if c.value not in OTHER_MAP_ACTIONS:      # acts in the other level
                    walk(c)
    walk(part.node)
    return out


def _fold(s: str) -> str:
    s = s.strip().replace('\\', '/').casefold()
    # 8 of 224 ``Other Map Name`` include the extension [verified]
    return s[:-4] if s.endswith('.zax') else s


def same_map(a: str, b: str) -> bool:
    """Two level references (Partial File Name, path below Levels/) mean the same level."""
    return _fold(a) == _fold(b)


@dataclass
class RemoteAction:
    """Action that acts in another level without switching to it.

    ``COtherMapAction``: runs ``Action`` in the level ``Other Map Name`` (usually trigger a relay,
    (de)activate an object, open a door); ``names`` are objects of that level.
    ``CExpireMapAction``: only ``Other Map Name``; the game lets the level expire, like
    ``Return to map=never`` (the same function 0x589570 in Zax.exe). Whether the saved state is
    lost in the process is unverified in the game.
    """
    part: LevelPart          # object with the script
    action: str              # COtherMapAction / CExpireMapAction
    map_name: str
    inner: str = ''          # class of the action in the other level (COtherMapAction only)
    names: list[tuple[str, str]] = field(default_factory=list)   # (field, name) in the other level


def remote_actions(part: LevelPart) -> list[RemoteAction]:
    """``COtherMapAction``/``CExpireMapAction`` in the object's script."""
    out = []

    def walk(node: tf.Node):
        for c in node.children:
            if not isinstance(c, tf.Node):
                continue
            if c.value in OTHER_MAP_ACTIONS:
                inner = c.item('Action')
                names = [(e.key, n) for _, e in _refs(inner, inner.value) for n in names_in(e.value)
                         if e.key in REF_KEYS] if isinstance(inner, tf.Node) else []
                out.append(RemoteAction(part, c.value, c.get('Other Map Name', ''),
                                        inner.value if isinstance(inner, tf.Node) else '', names))
            else:
                walk(c)
    walk(part.node)
    return out


def incoming_remote(levels: dict, map_name: str, name: str) -> list[tuple[str, RemoteAction]]:
    """Actions of other levels (``COtherMapAction``) that name the object ``name`` in the level
    ``map_name``. ``levels`` and pre-filter as in ``incoming_exits``."""
    target, key = _fold(map_name), name.strip().casefold()
    base = target.rsplit('/', 1)[-1]          # folders are spelled differently
    out = []
    for lname, read in levels.items():
        try:
            data = read()
        except OSError:
            continue
        text = data.decode('latin-1').casefold()
        if 'cothermapaction' not in text or key not in text or base not in text:
            continue
        try:
            level = Level.from_bytes(data)
        except Exception:  # noqa: BLE001 - broken file: skip
            continue
        for p in level.parts:
            for r in remote_actions(p):
                if _fold(r.map_name) == target and any(n.strip().casefold() == key for _, n in r.names):
                    out.append((lname, r))
    return out


def incoming_exits(levels: dict, map_name: str, location: str) -> list[tuple[str, Exit]]:
    """Exits of other levels that lead to start point ``location`` in level ``map_name``.

    ``levels``: name -> function that returns the bytes of the ``.zax``. The text is searched for
    the start point name first, only hits are parsed (reading all 112 levels takes several
    seconds otherwise). Case-insensitive comparison as in ``links``.
    """
    target, loc = _fold(map_name), _fold(location)
    out = []
    for name, read in levels.items():
        try:
            data = read()
        except OSError:
            continue
        if loc not in data.decode('latin-1').casefold():
            continue
        try:
            level = Level.from_bytes(data)
        except Exception:  # noqa: BLE001 - broken file: skip
            continue
        for p in level.parts:
            for e in exits(p):
                if _fold(e.map_name) == target and _fold(e.location) == loc:
                    out.append((name, e))
    return out
