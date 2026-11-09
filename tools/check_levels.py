"""Run the level check (zaxtools/levelcheck.py) over all levels of the game data, or build small broken
test levels and confirm that every crash check fires.

    python tools/check_levels.py                       # all levels: counts per check, all errors listed
    python tools/check_levels.py --verbose             # also every warning and hint
    python tools/check_levels.py --broken OUT          # broken cases into OUT (never into the game data)

Needs Zax.exe next to the game data (or --exe) for the checks that use the class schema.
"""
from __future__ import annotations

import argparse
import struct
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

from _common import data_arg, open_data
from zaxtools import levelcheck as lc, mdl, textformat as tf
from zaxtools.datasource import DataSource
from zaxtools.exeschema import Schema, find_exe
from zaxtools.level import Level

# Error findings the original levels give although the game handles them (each explained in
# zax-decomp/docs/ORIGINAL_BUGS.md / the check's source). Empty: the original levels give no crash finding.
KNOWN_ORIGINAL_ERRORS = set()


def run_all(ds: DataSource, ctx: lc.Context, verbose: bool = False) -> tuple[Counter, list]:
    per_check, errors = Counter(), []
    for f in ds.list('Levels/', '.zax'):
        level = Level.from_bytes(ds.read(f))
        for x in lc.check(level, ctx, f[len('Levels/'):]):
            per_check[x.check] += 1
            if x.severity == 'error':
                errors.append((f, x))
            elif verbose:
                print(f'  {lc.SEVERITY_TEXT[x.severity]:8} {f}: {x.object_text()} [{x.field}] {x.value!r}: {x.title}')
    return per_check, errors


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    data_arg(p)
    p.add_argument('--exe', help='Zax.exe (default: next to the game data)')
    p.add_argument('--broken', metavar='OUT', help='write broken test levels into OUT and check them')
    p.add_argument('--verbose', action='store_true')
    a = p.parse_args()
    ds = open_data(a)
    exe = Path(a.exe) if a.exe else find_exe(ds)
    cache = Path(tempfile.gettempdir()) / 'zax-levelcheck'
    schema = Schema.open(exe, ds, cache) if exe else None
    ctx = lc.Context(ds, schema, exe)
    if ctx.skipped:
        print('Without Zax.exe; left out:', ', '.join(ctx.skipped))
    if a.broken:
        sys.exit(0 if broken_cases(ds, schema, exe, Path(a.broken)) else 1)
    t0 = time.time()
    per_check, errors = run_all(ds, ctx, a.verbose)
    print(f'{len(ds.list("Levels/", ".zax"))} levels in {time.time() - t0:.0f} s')
    for key, (sev, title) in lc.CHECKS.items():
        print(f'  {per_check[key]:6}  {lc.SEVERITY_TEXT[sev]:8} {key:26} {title}')
    for f, x in errors:
        print(f'ERROR {f}: {x.object_text()} [{x.field}] {x.value!r}: {x.message}')
    unexpected = [e for e in errors if (e[0], e[1].check) not in KNOWN_ORIGINAL_ERRORS]
    print(f'{len(errors)} error findings, {len(unexpected)} unexpected')
    sys.exit(1 if unexpected else 0)


# --- Broken test levels -------------------------------------------------------------------------------

BASE = 'Levels/Test/Check/{}.zax'


BASE_LEVEL = 'Levels/ACT 1/M1M2/01 Main.zax'


def _base_level(ds: DataSource) -> Level:
    """The first level of the game as the base (characters, sounds, dialogue, inventories)."""
    return Level.from_bytes(ds.read(BASE_LEVEL))


def _first(level: Level, pred):
    return next(p for p in level.parts if pred(p))


def _entry_in(node: tf.Node, key: str) -> tf.Entry | None:
    for c in node.children:
        if isinstance(c, tf.Entry) and c.key == key:
            return c
        if isinstance(c, tf.Node):
            r = _entry_in(c, key)
            if r is not None:
                return r
    return None


def _patch_model(ds: DataSource, schema, src: str, out_data: Path, name: str, how: str) -> str:
    """Copy model ``src`` into ``out_data/Cache/Models/Test/<name>.mdl16`` with a broken value."""
    d = bytearray(ds.read(f'Cache/Models/{src}.mdl16'))
    if how == 'rotations':
        # the rotation count no longer divides the frames; the frames themselves stay valid (a changed frame total
        # would make the frame reader run past the sequence, with the original game too)
        s = next(s for s in mdl.read_sequences(bytes(d)) if s.rotations > 2 and s.total % (s.rotations - 1))
        o = s.offset + 25 + struct.unpack_from('<I', d, s.offset + 21)[0] + 12
        struct.pack_into('<I', d, o, s.rotations - 1)
    else:
        from zaxtools.modelhead import ModelHead
        mh = ModelHead(schema)
        mh.trace = []
        mh.decode(bytes(d))
        off = next(o for o, path, _ in mh.trace if path == 'CModel.Bounce Factor')
        struct.pack_into('<f', d, off, 1.5)
    target = out_data / 'Cache' / 'Models' / 'Test' / f'{name}.mdl16'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(bytes(d))
    return f'Test/{name}'


def broken_cases(ds: DataSource, schema, exe, out: Path) -> bool:
    out_data = out / 'Data'
    if ds.root.resolve() in (out_data.resolve(), *out_data.resolve().parents):
        sys.exit('OUT must not be the game data')
    cases = []          # (name, expected check, level)

    def case(name, check, edit):
        lv = _base_level(ds)
        edit(lv)
        cases.append((name, check, lv))

    walking = lambda lv: _first(lv, lambda p: p.cls == 'CEntityWalking')

    def missing_seq(lv):
        walking(lv).set('Cur Sequence', 'No Such Sequence')

    def missing_model(lv):
        walking(lv).set('Model', 'Characters/No Such Model')

    def unknown_class(lv):
        walking(lv).node.value = 'CNoSuchEntity'

    def brace(lv):
        # a "{" line right after a block (after its "}"), as a hand edit leaves it
        ch = walking(lv).node.children
        i = next(i for i, c in enumerate(ch) if isinstance(c, tf.Node))
        ch.insert(i + 1, tf.Raw('{'))

    def long_line(lv):
        p = _first(lv, lambda p: p.polygon)
        pts = p.polygon
        while len(p.get('Polygon')) < lc.LINE_LIMIT + 10:
            pts = pts + pts[:1]
            p.polygon = pts

    def count(lv):
        arr = next(n for n in _nodes(lv.root) if n.value == 'Array' and n.get('Item Count') and n.array_elements())
        arr.set('Item Count', str(len(arr.array_elements()) + 1))

    def flag_empty(lv):
        walking(lv).set('Used In', 'QuestMode,,MultiPlayer/Death Match')

    def flag_unknown(lv):
        walking(lv).set('Category', 'Enemy, Player')

    def sound(lv):
        e = next(_entry_in(p.node, 'Sound') for p in lv.parts if _entry_in(p.node, 'Sound'))
        e.value = 'No Such Sound.wav'

    def item(lv):
        e = next(_entry_in(p.node, 'Definition Index') for p in lv.parts if _entry_in(p.node, 'Definition Index'))
        e.value = 'No Such Item'

    def frame(lv):
        walking(lv).set('Current Frame', '1e30')

    def rotations(lv):
        walking(lv).set('Model', _patch_model(ds, schema, walking(lv).model, out_data, 'Rotations', 'rotations'))

    def bounce(lv):
        near_start(lv, walking(lv))
        walking(lv).set('Model', _patch_model(ds, schema, walking(lv).model, out_data, 'Bounce', 'bounce'))

    def dialog(lv):
        # a real dialogue action of the level (there: "Enter Action" of a CTouchingPolygonTriggerAI), its line renamed
        next(n for n in _nodes(lv.root) if n.value == 'CZaxDialogAction').set('Line', 'No such line')

    def add_activity(part, node):
        act = part.node.block('Activity')
        if act is None:
            act = tf.Node('Activity', 'Array', [tf.Entry('Item Count', '0')])
            part.node.children.append(act)
        act.children.append(node)
        act.update_array_count()

    def near_start(lv, part):
        s = _first(lv, lambda p: p.name == 'Game Start').position
        part.position = (s[0] + 60, s[1])
        part.set('Stationary', '0')        # a stationary part gets no updates, its AIs would never run
        part.set('Active', '1')

    def shield(lv):
        add_activity(_first(lv, lambda p: p.cls == 'CEntityBase'), tf.Node('Activity', 'CShieldAI', []))

    def patrol(lv):
        # the element's key is the array's element name ("Activity"; "Array Item" is only for arrays declared with
        # that alternate name). As "slave to hut" in the original level 04: the path AI alone in the Activity.
        w = walking(lv)
        near_start(lv, w)
        x, y = w.position
        lv.insert_part(tf.Node('Level Part', 'CFreeRangePoly', [tf.Entry('Name', 'Check Patrol Path'),
                                                                 tf.Entry('Polygon', f'{x:g}, {y:g}, {x + 200:g}, {y:g}')]))
        act = w.node.block('Activity')
        if act is not None:
            w.node.children.remove(act)
        add_activity(w, tf.Node('Activity', 'CPatrolPathAI', [
            tf.Entry('Path Poly', 'Check Patrol Path'), tf.Entry('Order', 'Random'), tf.Entry('Ignore last point', '0')]))

    def sethome(lv):
        # as in the original levels: "Action" inside the "Action" array of a CMultipleActionsAction, under a timer
        target = _first(lv, lambda p: p.cls == 'CEntityBase' and p.name)
        near_start(lv, walking(lv))
        action = tf.Node('Action', 'CMultipleActionsAction', [tf.Node('Action', 'Array', [
            tf.Entry('Item Count', '1'),
            tf.Node('Action', 'CSetHomeAction', [tf.Entry('Actor', target.name), tf.Entry('New Home Position', target.name)])])])
        add_activity(walking(lv), tf.Node('Activity', 'CRepeatTimerTriggerAI', [tf.Entry('Delay Between Actions', '1'), action]))

    def walking_ai_root(lv):
        from zaxtools import children as chl
        body = next(c for p in lv.parts for c in p.children if c.cls == chl.UPPER_BODY
                    and chl.same_as_parent_ai(c) is not None and chl.same_as_parent_ai(c).value == 'CWalkingUpperBodyAI')
        chl.add_child(_first(lv, lambda p: p.cls == 'CEntityBase' and p.position is not None), chl.as_child(body.node))

    for name, check, edit in [
            ('WalkingAIRoot', 'child-walking-ai-root', walking_ai_root),
            ('Patrol', 'patrol-random-hang', patrol), ('SetHome', 'sethome-non-character', sethome),
            ('MissingSequence', 'missing-sequence', missing_seq), ('MissingModel', 'missing-model', missing_model),
            ('UnknownClass', 'unknown-class', unknown_class), ('Brace', 'unexpected-brace', brace),
            ('LongLine', 'line-too-long', long_line), ('Count', 'array-count', count),
            ('FlagEmpty', 'flag-empty-name', flag_empty), ('FlagUnknown', 'flag-unknown-name', flag_unknown),
            ('Sound', 'resource-unknown', sound), ('Item', 'resource-unknown', item),
            ('Frame', 'current-frame', frame), ('Rotations', 'rotation-frames', rotations),
            ('Bounce', 'bounce-factor', bounce), ('Dialog', 'dialog-missing', dialog),
            ('Shield', 'shield-non-character', shield)]:
        if check in lc.Context(ds, schema).skipped:
            print(f'[SKIP] {name}: needs Zax.exe')
            continue
        try:
            case(name, check, edit)
        except StopIteration:
            print(f'[SKIP] {name}: the base level has nothing to break')
    # the broken models live in OUT/Data: check against the game data plus OUT/Data
    ctx = lc.Context(_Overlay(ds, out_data), schema, exe)
    ok = True
    for name, check, lv in cases:
        rel = BASE.format(name)
        t = out_data / rel
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_bytes(lv.to_bytes())
        found = [x for x in lc.check(Level.from_bytes(t.read_bytes()), ctx, rel[len('Levels/'):]) if x.check == check]
        good = bool(found)
        ok &= good
        print(f'[{"OK " if good else "FAIL"}] {name}: {check} {"fires" if good else "does NOT fire"} ({rel})')
    return ok


def _nodes(node):
    for c in node.children:
        if isinstance(c, tf.Node):
            yield c
            yield from _nodes(c)


class _Overlay:
    """Game data plus a scratch Data folder (the scratch folder wins), read only."""

    def __init__(self, ds: DataSource, extra: Path):
        self.ds, self.extra = ds, DataSource(extra)
        self.root = ds.root

    def exists(self, rel):
        return self.extra.exists(rel) or self.ds.exists(rel)

    def read(self, rel):
        return self.extra.read(rel) if self.extra.exists(rel) else self.ds.read(rel)

    def list(self, prefix='', suffix=''):
        return sorted(set(self.ds.list(prefix, suffix)) | set(self.extra.list(prefix, suffix)))


if __name__ == '__main__':
    main()
