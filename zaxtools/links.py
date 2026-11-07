"""Links between objects (via ``Name``) and dialogue lines from the ``.RDS``.

Scripts live in the objects themselves (``Activity``: triggers, relays, actions). An action names
its target with the name of another object, e.g. ``COpenDoorAction`` with ``Door Name=ship door``.
Which fields contain such names was determined from the levels: ``REF_KEYS`` only occur in
actions/AIs and mostly hit existing names [verified on all 112 levels]. Other fields whose value
happens to equal a name (``Visible=1`` with an object named "1") are not references.

Notations in the value:
- several names separated by commas: ``crutch2, crutch1``
- range ``#a-b#``: ``figure 8 #1-50#`` = ``figure 8 1`` ... ``figure 8 50`` (these names exist in
  the level [verified])
- placeholders ``$Trigger``, ``$Instigator``, ``$Touching`` ... are only resolved in the game.

The exact spelling is found first, otherwise without surrounding spaces or ignoring case
(``exact`` = False). Whether the game resolves such deviations is unverified.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import textformat as tf
from .i18n import QT_TRANSLATE_NOOP
from .level import Level, LevelPart

# field -> kind of link
REF_KEYS = {
    'Triggered By Name': 'trigger',          # the trigger only reacts to this object
    'Relay Name': 'relay',
    'Door Name': 'door', 'Switch Name': 'door',
    'Destination': 'place', 'Path Poly': 'place', 'New Home Position': 'place',
    'New Location': 'place', 'Location Entity': 'place', 'Position': 'place',
    'New Camera Target': 'place', 'New Compass Target': 'place',
    'Target Name': 'target', 'Target': 'target', 'Source Name': 'target',
    'Entity To Change': 'target', 'Name To Check For': 'target', 'Target to attack': 'target',
    'Attacker': 'target', 'Who To Switch': 'target', 'Who To Warp': 'target',
    'Entity Name': 'target', 'Leader Name': 'target', 'Actor': 'target',
}
# With ``New Map Name``, ``New Location`` is a place in the other level, not an object of this
# level (CRelocateAction without New Map Name relocates within the level)
MAP_ACTIONS = {'CRelocateAction', 'CSwitchMapAction', 'CTeleportAction'}
# Act in another level (``Other Map Name``): names in them refer to objects of that level
# [verified: of 214 names 161 only exist there, 35 in both, 1 only here, 17 in neither]
OTHER_MAP_ACTIONS = {'COtherMapAction', 'CExpireMapAction'}

# shown translated: translate('links', KIND_TEXT[kind])
KIND_TEXT = {'trigger': QT_TRANSLATE_NOOP('links', 'Trigger'), 'relay': QT_TRANSLATE_NOOP('links', 'Relay'),
             'door': QT_TRANSLATE_NOOP('links', 'Door/switch'), 'place': QT_TRANSLATE_NOOP('links', 'Place/path'),
             'target': QT_TRANSLATE_NOOP('links', 'Target')}

_RANGE = re.compile(r'#(\d+)-(\d+)#')


def names_in(value: str) -> list[str]:
    """All names of a reference field (comma list, ranges expanded, placeholders ``$...`` and empty
    entries left out)."""
    out = []
    for v in value.split(','):
        v = v.strip()
        if not v or v.startswith('$'):
            continue
        m = _RANGE.search(v)
        if m and int(m[2]) - int(m[1]) < 1000:
            out += [f'{v[:m.start()]}{i}{v[m.end():]}'.strip() for i in range(int(m[1]), int(m[2]) + 1)]
        else:
            out.append(v)
    return out


def _fold(name: str) -> str:
    return name.strip().casefold()


@dataclass
class Link:
    source: LevelPart               # object in whose script the reference is
    action: str                     # class of the action/AI, e.g. COpenDoorAction
    key: str                        # field, e.g. Door Name
    name: str                       # the name given
    targets: list[LevelPart] = field(default_factory=list)   # empty = not in the level
    exact: bool = True

    @property
    def kind(self) -> str:
        return REF_KEYS[self.key]


def _refs(node: tf.Node, cls: str):
    """(action class, entry) of all reference fields below ``node``."""
    other_map = cls in MAP_ACTIONS and bool(node.get('New Map Name'))
    for c in node.children:
        if isinstance(c, tf.Entry):
            if c.key in REF_KEYS and not (c.key == 'New Location' and other_map):
                yield cls, c
        elif isinstance(c, tf.Node) and c.value not in OTHER_MAP_ACTIONS:
            yield from _refs(c, c.value or cls)


class LinkIndex:
    """All links of a level. Create anew after changes (cheap)."""

    def __init__(self, level: Level):
        self.level = level
        self.by_name: dict[str, list[LevelPart]] = {}
        self.by_fold: dict[str, list[LevelPart]] = {}
        for p in level.parts:
            if p.name:
                self.by_name.setdefault(p.name, []).append(p)
                self.by_fold.setdefault(_fold(p.name), []).append(p)
        self.links: list[Link] = []
        for p in level.parts:
            self.links += self._scan(p)

    def resolve(self, name: str) -> tuple[list[LevelPart], bool]:
        if name in self.by_name:
            return self.by_name[name], True
        return self.by_fold.get(_fold(name), []), False

    def _scan(self, part: LevelPart) -> list[Link]:
        out = []
        for cls, e in _refs(part.node, part.cls):
            for n in names_in(e.value):
                targets, exact = self.resolve(n)
                others = [t for t in targets if t.node is not part.node]
                if targets and not others:
                    continue                    # names itself
                out.append(Link(part, cls, e.key, n, others, exact or not others))
        return out

    def links_from(self, part: LevelPart) -> list[Link]:
        return [lk for lk in self.links if lk.source.node is part.node]

    def links_to(self, part: LevelPart) -> list[Link]:
        return [lk for lk in self.links if any(t.node is part.node for t in lk.targets)]



# --- Renaming ------------------------------------------------------------------------------

@dataclass
class RefEdit:
    part: LevelPart                 # object in whose script the reference is
    entry: tf.Entry                 # reference field
    action: str
    new: str                        # new value of the whole field


@dataclass
class RenamePlan:
    """What is changed along with the references when renaming an object."""
    edits: list[RefEdit] = field(default_factory=list)
    in_range: list[RefEdit] = field(default_factory=list)    # name is inside ``#a-b#``: kept
    shared: list[RefEdit] = field(default_factory=list)      # name also belongs to others: kept

    @property
    def count(self) -> int:
        return len(self.edits)


def rename_plan(level: Level, part: LevelPart, new_name: str, index: LinkIndex | None = None) -> RenamePlan:
    """Rewrite the references to ``part`` for the new name (also in its own script).

    An entry of a comma list is replaced if it means exactly this object (exactly or in another
    spelling, like ``LinkIndex.resolve``); spaces around the entry are kept. Not changed are
    ranges ``#a-b#`` (the originals never mix ranges with lists, splitting would be guesswork)
    and names that other objects carry as well (the reference still hits the others). Both are
    reported; ``edits[*].new`` or the old value.
    """
    index = index or LinkIndex(level)
    plan = RenamePlan()
    mine = lambda ts: any(t.node is part.node for t in ts)         # noqa: E731
    for p in level.parts:
        for cls, e in _refs(p.node, p.cls):
            items = e.value.split(',')
            changed = False
            for i, raw in enumerate(items):
                v = raw.strip()
                if not v or v.startswith('$'):
                    continue
                if _RANGE.search(v):
                    if any(mine(index.resolve(n)[0]) for n in names_in(v)):
                        plan.in_range.append(RefEdit(p, e, cls, e.value))
                    continue
                targets = index.resolve(v)[0]
                if not mine(targets):
                    continue
                if len(targets) > 1:
                    plan.shared.append(RefEdit(p, e, cls, e.value))
                    continue
                lead = raw[:len(raw) - len(raw.lstrip())]
                trail = raw[len(raw.rstrip()):]
                items[i] = lead + new_name + trail
                changed = True
            if changed:
                plan.edits.append(RefEdit(p, e, cls, ','.join(items)))
    return plan


# --- Dialogue ------------------------------------------------------------------------------

def dialog_refs(part: LevelPart) -> list[tuple[str, str]]:
    """(Script, Line) of all dialogue actions in the object's script, in text order."""
    out = []

    def walk(node: tf.Node):
        for c in node.children:
            if isinstance(c, tf.Node):
                s, l = c.get('Script'), c.get('Line')
                if s is not None and l is not None:
                    out.append((s, l))
                walk(c)
    walk(part.node)
    return out


def parse_rds(data: bytes) -> dict[str, list[str]]:
    """Label -> speaker lines. Blocks: ``:label`` and lines up to the blank line."""
    out: dict[str, list[str]] = {}
    cur = None
    for line in data.decode('latin-1').splitlines():
        if line.startswith(':'):
            cur = line[1:]
            out[cur] = []
        elif not line.strip():
            cur = None
        elif cur is not None:
            out[cur].append(line)
    return out


class DialogScripts:
    """Dialogue texts from ``Levels/<Script>.RDS`` (cached per file). ``extra_roots``: folders laid out like
    ``Data`` whose scripts win (the editor's output folder, as files below ``Data/`` win in the game)."""

    def __init__(self, ds, extra_roots=()):
        self.ds = ds
        self.extra_roots = list(extra_roots)
        self._cache: dict[str, dict[str, list[str]] | None] = {}

    def script(self, script: str) -> dict[str, list[str]] | None:
        if script not in self._cache:
            from .rds import read_script
            found = read_script(self.ds, script, self.extra_roots)
            self._cache[script] = parse_rds(found[0]) if found else None
        return self._cache[script]

    def invalidate(self, script: str | None = None) -> None:
        """Forget a script (all with None) after it was saved."""
        if script is None:
            self._cache.clear()
        else:
            self._cache.pop(script, None)

    def lines(self, script: str, line: str) -> list[str] | None:
        """Speaker lines for the label or None (file or label missing)."""
        s = self.script(script)
        return None if s is None else s.get(line)
