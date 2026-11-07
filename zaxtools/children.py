"""Editing the child objects of a part ("Child List"): add, remove, the nodes of a new upper body or
attached object, a model swap, and the states the editor's undo restores.

How the game stores and draws children: ``LevelPart.children``, docs/FORMATS.md ("Composite
characters"). A part without children writes ``Child List=`` (an empty entry; 80,786 parts of the
original levels), a part with children ``Child List=CChildList { Child List=Array { Item Count=n
Child=... } }`` (1,351 parts; one of them with ``Item Count=0``) [verified 2026-10-29]. The class
``CChildList`` registers only this one field (``CChildList::RegisterFields`` 0x4f9aa0) [confirmed: code,
zax-decomp/reimpl/src/broadcast.cpp].

Only the changed lines are touched: adding the first child turns the empty entry into the block at
the same place, removing the last one leaves the block with ``Item Count=0`` (the form one original
part has). Every other field of the part and of its children stays as it is.

New children (never values copied from unrelated objects):
    upper body       the ``CEntityAnimatedUpperBody`` of the parent model's own "Default Entity"
                     (``catalog.make_node``; 9 of the 24 walking models have one) with the chosen model;
                     without one a minimal ``CEntityAnimatedUpperBody`` (name, model, position 0/0,
                     sequence) with an empty ``CWalkingUpperBodyAI`` (a walking parent) or
                     ``CSameAsParentAI`` (another animated parent); the game sets the missing fields to
                     the class defaults, as with minimal objects of the Tree List [verified 2026-10-29,
                     VM: a Targ with a minimal Periscope Torso and a light beam staff with a minimal
                     Rogcoil Torso load and draw, CLAUDE.md step 37]. A CWalkingUpperBodyAI under a root
                     that does not walk ends the game (levelcheck ``child-walking-ai-root``).
    attached object  the model's "Default Entity" when its class is ``CEntityBase`` or
                     ``CEntityAnimated``, otherwise a minimal object of the class the catalogue gives
                     the model (``CEntityBase`` unless the header says ``CEntityAnimated``), at a
                     position relative to the parent.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass

from . import textformat as tf
from .level import LevelPart, num

UPPER_BODY = 'CEntityAnimatedUpperBody'
ATTACH_CLASSES = ('CEntityBase', 'CEntityAnimated')
SAME_AS_PARENT = 'CSameAsParentAI'
WALKING_UPPER_BODY_AI = 'CWalkingUpperBodyAI'
# Classes derived from CSameAsParentAI / CEntityWalking / CEntityAnimated (zax-decomp/docs/classes.csv), used
# when no exe schema is at hand
SAME_AS_PARENT_AIS = frozenset({'CSameAsParentAI', 'CWalkingUpperBodyAI', 'CPlayerWalkingItemAI',
                                'CPlayerWalkingWeaponAI'})
WALKING = frozenset({'CEntityWalking', 'CEntityOm', 'CEntityOverlayWalking'})
ANIMATED = frozenset({'CEntityAnimated', 'CEntityAnimatedUpperBody', 'CEntityCharacter', 'CEntityFlying',
                      'CEntityMovable', 'CEntityOm', 'CEntityOverlayWalking', 'CEntityProjectile',
                      'CEntityStationaryCharacter', 'CEntityWalking'})
_STATIC = {'CSameAsParentAI': SAME_AS_PARENT_AIS, 'CWalkingUpperBodyAI': frozenset({'CWalkingUpperBodyAI'}),
           'CEntityWalking': WALKING, 'CEntityAnimated': ANIMATED,
           'CEntityAnimatedUpperBody': frozenset({UPPER_BODY})}


def derives(cls: str, base: str, schema=None) -> bool:
    """Does ``cls`` derive from ``base`` (or equal it)? With the exe schema (``exeschema.Schema``) by
    its class chain, otherwise by the class lists above."""
    if schema is not None and schema.known(cls):
        return base in schema.chain(cls)
    return cls in _STATIC.get(base, frozenset({base}))


# --- The Child List ------------------------------------------------------------------------------
def child_array(part: LevelPart, create: bool = False) -> tf.Node | None:
    """The array of the part's "Child List" (``CChildList`` +8). ``create``: make it when missing -
    the empty entry ``Child List=`` becomes the block at its place; without the entry the block goes
    behind "Name" (where the game writes it), else at the front."""
    item = part.node.item('Child List')
    if isinstance(item, tf.Node):
        arr = item.block('Child List')
        if isinstance(arr, tf.Node) or not create:
            return arr if isinstance(arr, tf.Node) else None
        arr = tf.Node('Child List', 'Array', [tf.Entry('Item Count', '0')])
        old = item.item('Child List')
        if old is not None:
            item.children[item.children.index(old)] = arr
        else:
            item.children.append(arr)
        return arr
    if not create:
        return None
    arr = tf.Node('Child List', 'Array', [tf.Entry('Item Count', '0')])
    block = tf.Node('Child List', 'CChildList', [arr])
    ch = part.node.children
    if item is not None:
        ch[ch.index(item)] = block
    else:
        name = part.node.item('Name')
        ch.insert(ch.index(name) + 1 if name is not None else 0, block)
    return arr


def add_child(part: LevelPart, node: tf.Node, index: int | None = None) -> LevelPart:
    """Add ``node`` (key ``Child``) to the part's Child List, without ``index`` at its end; the
    count follows (``update_array_count``)."""
    if node.key != 'Child':
        raise ValueError('not a Child node')
    arr = child_array(part, create=True)
    elems = [c for c in arr.children if isinstance(c, tf.Node) and c.key == 'Child']
    if index is None or index >= len(elems):
        at = (arr.children.index(elems[-1]) + 1) if elems else len(arr.children)
    else:
        at = arr.children.index(elems[index])
    arr.children.insert(at, node)
    arr.update_array_count()
    return LevelPart(node)


def remove_child(part: LevelPart, child: LevelPart) -> int:
    """Remove a child; returns its former index among the children."""
    arr = child_array(part)
    if arr is None:
        raise ValueError('the part has no children')
    elems = [c for c in arr.children if isinstance(c, tf.Node) and c.key == 'Child']
    i = next(k for k, c in enumerate(elems) if c is child.node)
    arr.children.remove(child.node)
    arr.update_array_count()
    return i


def find_parent(parts, node: tf.Node) -> LevelPart | None:
    """The part (of ``parts``, searched with their children's children) whose Child List holds
    ``node``."""
    todo = list(parts)
    while todo:
        p = todo.pop()
        kids = p.children
        if any(c.node is node for c in kids):
            return p
        todo.extend(kids)
    return None


def root_of(parts, node: tf.Node) -> LevelPart | None:
    """The part of the Tree List a child belongs to (its parent's parent ...); None if ``node`` is no
    child of ``parts``."""
    top = {id(p.node): p for p in parts}
    cur = find_parent(parts, node)
    while cur is not None and id(cur.node) not in top:
        cur = find_parent(parts, cur.node)
    return cur


@dataclass
class State:
    """What a change of the Child List touches, for undo: the part's lines and those of its Child List
    block and array (the nodes themselves are kept, only the lists of their lines are restored)."""
    part: tf.Node
    lines: list
    block: tf.Node | None
    block_lines: list | None
    array: tf.Node | None
    array_lines: list | None
    count: str | None


def save_state(part: LevelPart) -> State:
    block = part.node.block('Child List')
    arr = block.block('Child List') if block is not None else None
    cnt = arr.item('Item Count') if arr is not None else None
    return State(part.node, list(part.node.children), block, list(block.children) if block is not None else None,
                 arr, list(arr.children) if arr is not None else None, cnt.value if cnt is not None else None)


def restore_state(s: State) -> None:
    s.part.children[:] = s.lines
    if s.block is not None:
        s.block.children[:] = s.block_lines
    if s.array is not None:
        s.array.children[:] = s.array_lines
        cnt = s.array.item('Item Count')
        if cnt is not None and s.count is not None:
            cnt.value = s.count


# --- New children ---------------------------------------------------------------------------------------
def as_child(node: tf.Node) -> tf.Node:
    """A copy of an object node (``Level Part`` or ``Child``) with the key ``Child``."""
    n = copy.deepcopy(node)
    n.key = 'Child'
    return n


def default_upper_body(catalog, parent_model: str | None) -> tf.Node | None:
    """The upper body in the "Default Entity" of the parent's model (first ``CEntityAnimatedUpperBody``
    of its Child List), None without one."""
    if not parent_model or catalog is None or parent_model not in catalog.models:
        return None
    info = catalog[parent_model]
    if info.head != 'default' or not info.default:
        return None
    d = LevelPart(catalog.make_node(parent_model))
    return next((c.node for c in d.children if c.cls == UPPER_BODY), None)


def torso_candidates(catalog, parent_model: str | None) -> list[str]:
    """Models offered for an upper body: those named "... Torso" (the ones the originals use), the one
    of the parent's Default Entity first."""
    out = sorted(p for p in catalog.models if p.rsplit('/', 1)[-1].lower().endswith(' torso')) if catalog else []
    d = default_upper_body(catalog, parent_model)
    first = LevelPart(d).model if d is not None else None
    if first:
        out = [first] + [p for p in out if p != first]
    return out


def _sequence_for(catalog, model: str, wanted: str | None) -> str:
    """``wanted`` if the model has that sequence (case as in the model), otherwise its start sequence."""
    info = catalog.models.get(model) if catalog is not None else None
    if info is None:
        return wanted or ''
    if wanted:
        hit = next((s for s in info.sequences if s.lower() == wanted.lower()), None)
        if hit:
            return hit
    return info.default_sequence


def minimal_child(cls: str, model: str, sequence: str, x: float = 0, y: float = 0) -> tf.Node:
    """A child with the fields of a minimal object (``catalog.make_node`` without a default object)."""
    node = tf.Node('Child', cls)
    for k, v in (('Name', ''), ('Model', model), ('Position X', num(x)), ('Position Y', num(y)),
                 ('Cur Sequence', sequence)):
        node.children.append(tf.Entry(k, v))
    return node


def upper_body_node(catalog, parent: LevelPart, model: str | None = None, schema=None) -> tf.Node:
    """A new upper body for ``parent`` with ``model`` (default: the one of the parent model's Default
    Entity, else the first "... Torso" candidate)."""
    template = default_upper_body(catalog, parent.model)
    if model is None:
        cands = torso_candidates(catalog, parent.model)
        if not cands:
            raise ValueError('no upper body model')
        model = cands[0]
    if template is not None:
        n = as_child(template)
        lp = LevelPart(n)
        if lp.model != model:
            lp.model = model
            n.set('Cur Sequence', _sequence_for(catalog, model, lp.sequence))
        return n
    n = minimal_child(UPPER_BODY, model, _sequence_for(catalog, model, parent.sequence))
    ai = WALKING_UPPER_BODY_AI if derives(parent.cls, 'CEntityWalking', schema) else SAME_AS_PARENT
    act = tf.Node('Activity', 'Array', [tf.Entry('Item Count', '1'), tf.Node('Activity', ai, [])])
    n.children.insert(1, act)                 # behind "Name" (the game writes it a few fields later)
    return n


def attached_node(catalog, model: str, x: float = 0, y: float = 0) -> tf.Node:
    """A new attached object with ``model`` at (x, y) relative to the parent."""
    info = catalog.models.get(model) if catalog is not None else None
    if info is not None and info.head == 'default' and info.default:
        d = catalog.make_node(model)
        if d.value in ATTACH_CLASSES:
            n = as_child(d)
            n.set('Position X', num(x))
            n.set('Position Y', num(y))
            return n
    cls = info.cls if info is not None and info.cls in ATTACH_CLASSES and info.head != 'default' else 'CEntityBase'
    seq = info.default_sequence if info is not None else ''
    return minimal_child(cls, model, seq, x, y)


def model_edits(catalog, child: LevelPart, model: str) -> list[tuple[tf.Entry, str]]:
    """The entries to change when a child gets another model: "Model", and "Cur Sequence" when the new
    model lacks the current one (its start sequence then; the game exits on a missing sequence,
    levelcheck ``missing-sequence``). An absent entry is not added: (None, value) asks the caller to
    add it."""
    out = []
    out.append((child.node.item('Model'), model))
    cur = child.sequence
    new = _sequence_for(catalog, model, cur)
    if new and (cur or '') != new:
        out.append((child.node.item('Cur Sequence'), new))
    return out


# --- Copy, paste, duplicate ------------------------------------------------------------------------------
# A copied part keeps its Child List (the whole node is copied). A copied child object is pasted as a child again,
# onto the chosen parent, with its own fields as they are (its name too, as parts keep theirs) and its position,
# which is relative to the parent. A child is never pasted as a part of the Tree List (its position means nothing
# there) and a part never as a child.
PASTE_UPPER_BODY_PARENT = 'upper-body-parent'      # an upper body onto a parent that is no CEntityAnimated
PASTE_WALKING_AI_ROOT = 'walking-ai-root'          # a CWalkingUpperBodyAI under a root that does not walk


def paste_problem(nodes, parent: LevelPart, root: LevelPart | None = None, schema=None) -> str | None:
    """Why child nodes must not go onto ``parent`` (``root``: the part of the Tree List it belongs to, default the
    parent): an upper body only works on an animated parent (``add_upper_body`` refuses the same; levelcheck
    ``child-upper-body-parent``), and a ``CWalkingUpperBodyAI`` under a root that is no ``CEntityWalking`` ends the
    game (levelcheck ``child-walking-ai-root``, verified). None when they may."""
    root = root or parent
    for n in nodes:
        if n.value == UPPER_BODY and not derives(parent.cls, 'CEntityAnimated', schema):
            return PASTE_UPPER_BODY_PARENT
        act = n.block('Activity')
        ais = [e for e in act.array_elements() if isinstance(e, tf.Node)] if act is not None else []
        if any(derives(e.value, WALKING_UPPER_BODY_AI, schema) for e in ais) and \
                not derives(root.cls, 'CEntityWalking', schema):
            return PASTE_WALKING_AI_ROOT
    return None


def paste_children(parent: LevelPart, nodes) -> list[tf.Node]:
    """Append copies of the nodes (``Child`` or ``Level Part`` nodes) to the parent's Child List, in their order;
    returns the new nodes."""
    out = []
    for n in nodes:
        c = as_child(n)
        add_child(parent, c)
        out.append(c)
    return out


# --- What a child means to the game (for the level check and the editor's hints) -----------------
def same_as_parent_ai(child: LevelPart, schema=None) -> tf.Node | None:
    """The child's first AI derived from ``CSameAsParentAI`` (shows the parent's sequence and frame)."""
    act = child.node.block('Activity')
    if act is None:
        return None
    return next((e for e in act.array_elements() if isinstance(e, tf.Node) and
                 derives(e.value, SAME_AS_PARENT, schema)), None)
