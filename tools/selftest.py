"""Self-test against the real game data.

Checks that all formats can be read and (where supported) written back byte for byte. Run it
before and after every change to zaxtools.

    python tools/selftest.py --data "C:/Spiele/Zax/Data.dat"
    python tools/selftest.py --data Data --quick      # samples only
"""
import argparse
import csv
import hashlib
import math
import os
import re
import struct
import time
from pathlib import Path
from collections import Counter

import numpy as np

from _common import data_arg, open_data
from zaxtools import font, frm, links, mdl, minimap, newlevel, plasma, rds, render, seq, textformat as tf, transition, way
from zaxtools import waymap
from zaxtools.datasource import DataSource
from zaxtools.level import Level
from zaxtools.exeschema import Schema, find_exe
from zaxtools.modelhead import DecodeError, ModelHead

ROOT = Path(__file__).resolve().parent.parent
# zax-decomp (docs/fields.csv): ZAX_DECOMP, else the folder zax-decomp next to this repository
DECOMP = Path(os.environ.get('ZAX_DECOMP') or ROOT.parent / 'zax-decomp')

TEXT_SUFFIXES = ('.zax', '.txt', '.zgt', '.can', '.sty', '.dificulty', '.quips', '.foo')


def _nodes(node):
    for c in node.children:
        if isinstance(c, tf.Node):
            yield c
            yield from _nodes(c)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    data_arg(p)
    p.add_argument('--quick', action='store_true')
    a = p.parse_args()
    quick = a.quick
    ds = open_data(a)
    sample = (lambda xs: xs[::max(1, len(xs) // 15)]) if a.quick else (lambda xs: xs)
    failures = 0

    def report(title, ok, total, extra=''):
        nonlocal failures
        failures += total - ok
        mark = 'OK ' if ok == total else 'FAIL'
        print(f'[{mark}] {title}: {ok}/{total} {extra}')

    t0 = time.time()
    # 1. Text files lossless
    texts = sample([f for f in ds.list(suffix='') if f.lower().endswith(TEXT_SUFFIXES)])
    ok, bad = 0, []
    for f in texts:
        b = ds.read(f)
        try:
            if tf.dump_bytes(tf.load_bytes(b)) == b:
                ok += 1
            else:
                bad.append(f)
        except ValueError as e:
            bad.append(f'{f}: {e}')
    report('Text files written back byte for byte', ok, len(texts), bad[:3] or '')

    # 2. Way points: read, write back, consistency, comparison with .zax
    ways = sample(ds.list('Levels/', '.way'))
    ok, notes = 0, Counter()
    for f in ways:
        b = ds.read(f)
        w = way.loads(b)
        good = way.dumps(w) == b
        probs = way.check(w)
        notes['consistency problems'] += len(probs)
        zax = f[:-4] + '.zax'
        if ds.exists(zax):
            pd = tf.root(tf.load_bytes(ds.read(zax))).block('Path Data')
            if pd is not None and (int(pd.get('MinDistBetweenWayPoints', -1)), int(pd.get('MaxDistToConnect', -1))) != (w.min_dist, w.max_connect):
                notes['header differs from .zax'] += 1
        ok += good and not probs
    report('.way read, written byte for byte, consistent', ok, len(ways), dict(notes) or '')

    # 2b. The way point map as the game builds it (zaxtools/waymap.py): equal to the shipped .way byte for byte
    _check_waymap(ds, report, sample)

    # 3. Levels as objects
    zaxs = sample(ds.list('Levels/', '.zax'))
    ok, missing = 0, Counter()
    for f in zaxs:
        lv = Level.from_bytes(ds.read(f))
        e = lv.elevations
        assert e.ndim == 2 and len(lv.ground_textures) > 0
        for n in lv.ground_textures:
            if not ds.exists(f'Cache/Textures/{n}.frm16'):
                missing['texture'] += 1
        for prt in lv.parts:
            if prt.model and not ds.exists(f'Cache/Models/{prt.model}.mdl16'):
                missing[prt.model] += 1
        ok += 1
    report('Levels loaded (objects, Plasma Ground)', ok, len(zaxs),
           f'missing files: {dict(missing.most_common(5))}' if missing else '')
    ok = 0
    for f in zaxs:
        raw = ds.read(f)
        lv = Level.from_bytes(raw)
        lv.ground_textures = list(lv.ground_textures)
        ok += lv.to_bytes() == raw
    report('Unchanged texture list written back byte for byte', ok, len(zaxs))
    keyseq = lambda l: tuple((c.key, isinstance(c, tf.Node)) for c in l.root.children if not isinstance(c, tf.Raw))
    seqs = Counter(keyseq(Level.from_bytes(ds.read(f))) for f in zaxs)
    nl = newlevel.new_level('Test/New', 3000, 2500, ['11 Dirt', '13 Rock'], ground=1)
    ok = (keyseq(nl) == seqs.most_common(1)[0][0], nl.elevations.shape == (40, 47),
          Level.from_bytes(nl.to_bytes()).to_bytes() == nl.to_bytes(), minimap.can_render(nl))
    report('New level: structure like the originals, grid, round trip, mini map', sum(ok), len(ok))
    ok = n = 0
    for f in zaxs:
        lv = Level.from_bytes(ds.read(f))
        m = minimap.mapping(lv)
        if m['stored'] or not ds.exists(minimap.minimap_path(lv)):
            continue
        n += 1
        orig = frm.rgb_to_rgb565(frm.decode(ds.read(minimap.minimap_path(lv)))[0][..., :3]) != 0x00C5
        py, px = np.mgrid[0:121, 0:176]
        wx, wy = (px + 0.5 - m['X Offset']) / m['X Scale'], (py + 0.5 - m['Y Offset']) / m['Y Scale']
        x0, y0, x1, y1 = m['box']
        inside = (wx >= x0) & (wy >= y0) & (wx < x1) & (wy < y1)
        bbox = lambda b: (lambda ys, xs: (xs.min(), ys.min(), xs.max(), ys.max()))(*np.nonzero(b))
        ok += bbox(inside) == bbox(orig)
    report('Mini map mapping with Scale 0 as in the game (position of the original mini maps)', ok, n)
    # Let the game draw the mini map: placeholders of the wrong size next to the level's files
    ph = minimap.placeholder_files(nl)
    pal = frm.load_palette(ds.read('Palettes/GamePalette.pal'))
    ok = (sorted(ph) == sorted(minimap.game_files(nl)[:2]),
          all(frm.decode(v, palette=pal)[0].shape[:2] != minimap.SIZE[::-1] for v in ph.values()),
          minimap.game_files(nl)[2] == 'Levels/Test/-New.tga')
    report('Mini map placeholders for the game (wrong size, paths)', sum(ok), len(ok))
    at = Counter()
    for f in zaxs:
        lv = Level.from_bytes(ds.read(f))
        n, e = len(lv.ground_textures), lv.elevations.astype(int)
        band = np.minimum(e * n // 256, n - 1)
        at['band start'] += int((e == np.vectorize(lambda i: render.band_start(i, n))(band)).sum())
        at['band middle'] += int((e == np.minimum(255, ((band + 0.5) * 256 / n).astype(int))).sum())
        at['points'] += e.size
    # all levels: band start 7.3 times as often as band middle; the --quick sample is lower
    ok = (at['band start'] > (1 if a.quick else 5) * at['band middle'],
          not render.blend_weight(nl.elevations, len(nl.ground_textures), render.blending(nl))[1].any())
    report('Ground: originals paint at the band start, a new level shows the pure texture', sum(ok), len(ok), dict(at))
    # checksum of tiles that were compared byte for byte with the original code (emulator)
    keys = [(0, 128, 0, 128, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0), (255, 0, 0, 255, 3, 200, 17),
            (64, 64, 64, 64, 0, 0, 0), (1, 0, 0, 2, 0, 0, 0), (192, 128, 128, 192, 0, 0, 0)]
    digest = hashlib.sha1(plasma.tiles(np.array(keys)).tobytes()).hexdigest()
    report('Ground: plasma fractal like Zax.exe (checksum)', int(digest == 'c745b2ed2c8bed9910e8453d72107918c038df1c'), 1)
    _check_ground_pieces(ds, zaxs, report)
    scripts, stats, total, ok = links.DialogScripts(ds), Counter(), 0, 0
    for f in zaxs:
        lv = Level.from_bytes(ds.read(f))
        for lk in links.LinkIndex(lv).links:
            stats['exact' if lk.targets and lk.exact else 'spelling' if lk.targets else 'not in level'] += 1
        for p in lv.parts:
            for s, line in links.dialog_refs(p):
                total += 1
                ok += scripts.lines(s, line) is not None
    report('Dialogue lines of the scripts found in the .RDS', ok, total, f'links: {dict(stats)}')
    _check_rds(ds, zaxs, report, 'game data')
    loaded = {f: Level.from_bytes(ds.read(f)) for f in zaxs}
    spawns = {lv.partial_file_name.lower(): {p.name.lower() for p in transition.spawn_points(lv)} for lv in loaded.values()}
    shape = [e.key for e in transition.relocate_action('a', 'b').children]
    ok, total, found = 0, 0, Counter()
    for lv in loaded.values():
        for p in lv.parts:
            for e in transition.exits(p):
                found['target level present' if e.map_name.lower() in spawns else 'target level missing'] += 1
                if e.map_name.lower() in spawns:
                    found['start point found'] += e.location.strip().lower() in spawns[e.map_name.lower()]
                if e.action == transition.ACTION:
                    node = next(n for n in _nodes(p.node) if n.value == e.action and n.get('New Map Name') == e.map_name)
                    total += 1
                    ok += [c.key for c in node.children if isinstance(c, tf.Entry)] == shape
    report('Transitions: new CRelocateAction built like the originals', ok, total, dict(found))
    # COtherMapAction/CExpireMapAction: target level exists; the names are in that level
    by_map = {transition._fold(lv.partial_file_name): lv for lv in loaded.values()}
    by_map.update({transition._fold(f[len('Levels/'):]): lv for f, lv in loaded.items()})
    idx = {id(lv): links.LinkIndex(lv) for lv in loaded.values()}
    ok, total, found = 0, 0, Counter()
    for lv in loaded.values():
        for p in lv.parts:
            for r in transition.remote_actions(p):
                total += 1
                other = by_map.get(transition._fold(r.map_name))
                ok += other is not None
                found[r.action] += 1
                for _, n in r.names:
                    found['name there' if other is not None and idx[id(other)].resolve(n)[0] else 'name missing there'] += 1
    if a.quick:  # the target levels are usually missing from the sample
        print(f'[---] Actions in other levels: only checked without --quick {dict(found)}')
    else:
        report('Actions in other levels: target level present', ok, total, dict(found))
    # Renaming: afterwards the same references point exactly to the object (except the reported
    # ranges and duplicate names), undo byte for byte. Every 3rd object (run time)
    ok, total, found = 0, 0, Counter()
    for f in zaxs:
        raw = ds.read(f)
        lv = Level.from_bytes(raw)
        index = links.LinkIndex(lv)
        for p in [p for p in lv.parts if p.name and index.links_to(p)][::30 if a.quick else 3]:
            mine = lambda n: any(t.node is p.node for t in index.resolve(n)[0])     # noqa: E731
            want = Counter((id(lk.source.node), lk.key) for lk in index.links_to(p))
            plan = links.rename_plan(lv, p, 'Renamed Test', index)
            for r in {id(r.entry): r for r in plan.in_range + plan.shared}.values():
                want -= Counter({(id(r.part.node), r.entry.key): sum(map(mine, links.names_in(r.entry.value)))})
            edits = [(p.node.item('Name'), 'Renamed Test')] + [(r.entry, r.new) for r in plan.edits]
            olds = [e.value for e, _ in edits]
            for e, v in edits:
                e.value = v
            got = links.LinkIndex(lv).links_to(p)
            total += 1
            ok += Counter((id(lk.source.node), lk.key) for lk in got) == want and all(lk.exact for lk in got)
            found['references changed'] += plan.count
            found['range, kept'] += len(plan.in_range)
            found['duplicate name, kept'] += len(plan.shared)
            for (e, _), v in zip(edits, olds):
                e.value = v
        total += 1
        ok += lv.to_bytes() == raw
    report('Renaming: references follow, undo byte for byte', ok, total, dict(found))

    # 4. Images
    pal = frm.load_palette(ds.read('Palettes/GamePalette.pal'))
    for suffix, palette in (('.frm16', None), ('.frm', pal)):
        files = sample(ds.list('Cache/', suffix))
        ok, bad = 0, []
        for f in files:
            try:
                frm.decode(ds.read(f), 0, palette)
                ok += 1
            except Exception as e:  # noqa: BLE001
                bad.append(f'{f}: {e}')
        report(f'Images {suffix} decoded', ok, len(files), bad[:2] or '')
    # 8-bit frames: every block drawn at the 256-colour mode's opacity step (frm.OPACITY8, docs/FORMATS.md 5)
    ok = total = 0
    for f in sample(ds.list('Cache/', '.frm')):
        d = ds.read(f)
        hd, bl, _ = frm.blocks(d, 0)
        if not hd.rle:
            continue
        total += 1
        rgba = frm.decode(d, 0, pal)[0]
        order = [bl[0], bl[4], bl[3], bl[2], bl[1]]
        masks = [b[1] if b is not None else np.zeros((hd.height, hd.width), bool) for b in order]
        alone = np.sum(masks, axis=0) == 1
        good = (rgba[..., 3][np.sum(masks, axis=0) == 0] == 0).all()
        for b, m, op in zip(order, masks, frm.OPACITY8):
            if b is not None:
                one = m & alone
                good &= bool((rgba[..., 3][one] == op).all() and (rgba[..., :3][one] == pal[b[0][one]]).all())
        ok += bool(good)
    alpha = np.array([255, 229, 178, 127, 76, 25])[:, None].repeat(10, 1).astype(np.uint8)  # each band's top, then dropped
    dec = frm.decode(frm.encode8(np.full((6, 10), 77, np.uint8), alpha), 0, pal)[0]
    ok += bool((dec[:, 0, 3] == np.array(frm.OPACITY8 + (0,))).all())
    report('Images .frm: the five 8-bit blocks at the opacity steps 1, 0.8, 0.6, 0.4, 0.2', ok, total + 1)
    # Image sequences (without fonts): every byte read, frames complete, same count for 8 and 16 bit
    files = [f for f in sample(ds.list('Cache/', '.seq16')) if ds.read(f)[:8] == seq.TAG]
    ok, bad, frames = 0, [], 0
    for f in files:
        try:
            a, b = seq.load(ds.read(f)), seq.load(ds.read(f[:-2]), pal)
            if len(a.frames) == len(b.frames) == a.total:
                ok += 1
                frames += len(a.frames)
            else:
                bad.append(f)
        except Exception as e:  # noqa: BLE001
            bad.append(f'{f}: {e}')
    report('Image sequences .seq/.seq16 decoded', ok, len(files), bad[:2] or f'{{\'Frames\': {frames}}}')
    # Fonts: every byte read, same characters and sizes for 8 and 16 bit; dialogue font readable
    files = ds.list('Cache/Fonts/', '.seq16')
    ok, bad, chars = 0, [], 0
    for f in files:
        try:
            a, b = font.load(ds.read(f)), font.load(ds.read(f[:-2]), pal)
            if a.glyphs.keys() == b.glyphs.keys() and all(a.glyphs[k].rgba.shape == b.glyphs[k].rgba.shape
                                                          for k in a.glyphs):
                ok += 1
                chars += len(a.glyphs)
            else:
                bad.append(f)
        except Exception as e:  # noqa: BLE001
            bad.append(f'{f}: {e}')
    if 'Cache/Fonts/Gold Editor.seq16' in files:
        g = font.load(ds.read('Cache/Fonts/Gold Editor.seq16'))
        if (g.first, g.last, g.box, g.render('Select Map').shape) != (24, 255, (0, -2, 12, 14), (14, 63, 4)):
            bad.append('Gold Editor: header or text width differs')
            ok -= 1
    report('Fonts .seq/.seq16 decoded', ok, len(files), bad[:2] or f'{{\'characters\': {chars}}}')
    # Mini maps (raw, 16 bit) re-encoded byte for byte
    files = [f for f in sample(ds.list('Cache/Levels/', '.frm16')) if frm.read_header(ds.read(f)).flags == 0x40]
    ok = sum(frm.encode_raw16(frm.decode(d := ds.read(f))[0][..., :3], int.from_bytes(d[10:12], 'little')) == d
             for f in files)
    report('Mini maps .frm16 encoded byte for byte', ok, len(files))
    files, ok = sample(ds.list('Cache/Levels/', '.frm')), 0
    for f in files:
        d = ds.read(f)
        hd = frm.read_header(d)
        tab = struct.unpack_from('<%dI' % hd.height, d, frm.HEADER + hd.size)
        idx, op = frm.decode_rle(d[frm.HEADER:frm.HEADER + hd.size], tab, hd.width, hd.height, 1)
        ok += bool((frm.decode(frm.encode_rle8(idx, opaque=op), 0, pal)[0] == frm.decode(d, 0, pal)[0]).all())
    report('Mini maps .frm (8 bit) re-encoded, same image', ok, len(files))
    _check_encoder(ds, report, sample, pal)

    # 5. Models
    mdls = sample(ds.list('Cache/Models/', '.mdl16'))
    ok, stats = 0, Counter()
    for f in mdls:
        m = mdl.load(ds.read(f), f)
        for s in m.sequences:
            stats['sequences'] += 1
            stats['frames'] += len(s.stored)
            stats['empty frames'] += s.total - len(s.stored)
            if s.exact and len(s.frames) == s.total and s.rotations * s.frames_per_rotation == s.total:
                stats['sequences complete'] += 1
        ok += bool(m.sequences) and all(s.exact for s in m.sequences)
    report('Models .mdl16: sequences, every frame in its place', ok, len(mdls), dict(stats))
    # Empty frames (byte 00): Zax's Run Shadow has 12 empty frames at the end, Sparkle starts empty
    s = mdl.load(ds.read(f := 'Cache/Models/Characters/Crater/SmallGun.mdl16'), f).sequence('Run Shadow')
    t = mdl.load(ds.read(f := 'Cache/Models/Items/Money/Sparkle.mdl16'), f).sequence('Idle')
    report('Empty frames in their place', int(s.frames[-12:] == [None] * 12 and None not in s.frames[:132]
                                             and t.frames[0] is None and t.still() is t.frames[1]), 1)
    # Rotations (exe 0x55fdd0): Rotational Offset/Range read, angle -> rotation
    r = mdl.load(ds.read(f := 'Cache/Models/Characters/Jungle Creature.mdl16'), f)
    offs = Counter(round(s.rot_offset, 4) for s in r.sequences)
    v = mdl.load(ds.read(f := 'Cache/Models/Characters/Villager Korbo.mdl16'), f).sequence('Idle')
    got = [v.rotation(a) for a in (0, 1.5708, 3.14159, 4.71239, 0.785398, -0.1, 6.27)]
    report('Rotation from facing angle as in the exe',
           int(got == [0, 3, 6, 9, 1, 0, 0] and -0.7854 in offs
               and all(abs(s.rot_range - 2 * np.pi) < 1e-4 for s in r.sequences)), 1, {'Villager': got})
    # Shadows: alpha per RLE entry, the inside (run of 17 pixels in row 21) is opaque
    f = 'Cache/Models/Environments/General/JungleGoodieBox.mdl16'
    sh = mdl.load(ds.read(f), f).sequence('Idle Shadow').frames[0].rgba
    report('Shadows filled (alpha per RLE entry)',
           int((sh[21, 6:23, 3] == 0x99).all() and (sh[..., 3] > 0).sum() == 663), 1)
    # Render modes (FORMATS.md 6): Black Bias images carry alpha (blending like the game),
    # Amplify Light images are opaque and brighten the background with d + d*s
    f = 'Cache/Models/Explosions/Explode 1.mdl16'
    bb = mdl.load(ds.read(f), f).sequence('Idle').still(0).rgba[..., 3]
    f = 'Cache/Models/Environments/Cave/Light Beams Pieces/Light Beam 1.mdl16'
    al = mdl.load(ds.read(f), f).sequence('Floor Light').still(0).rgba[..., 3]
    # Switches per sequence: "Always Visible" is always drawn, "Editor Only" (handles) never
    lb = [s.name for _, s in mdl.load(ds.read(f), f).layers('Idle')]
    f = 'Cache/Models/Environments/Volcanic Pits/Details/Steam.mdl16'
    st = [s.name for _, s in mdl.load(ds.read(f), f).layers('Idle')]
    report('Sequence switches (Always Visible, Editor Only)', int(lb == ['Floor Light', 'Idle'] and st == ['Idle Shadow', 'Idle']),
           1, {'Light Beam 1': lb, 'Steam': st})
    amp = render.amplify(np.float32([0, 100, 200]), np.float32([255, 128, 255]))
    report('Blend modes as in the exe', int(((bb > 0) & (bb < 255)).sum() > 0.9 * (bb > 0).sum()
                                            and set(np.unique(al)) == {0, 255}
                                            and amp.round().tolist() == [0, 150, 255]), 1)
    # Exact 16-bit arithmetic (FORMATS.md 6): scalar blend 31/32 of the difference, the MMX blend
    # the full source at 255, the blue borrow, Amplify Light's tables without the low green bit
    d, sv, wv = np.array([0, 0, 0x0841, 0x8410]), np.array([0xffff, 0xffff, 0x0000, 0xffff]), np.array([255, 128, 255, 0])
    exact = (render.blend565(d, sv, wv).tolist(), render.blend565_mmx(d, sv, wv).tolist(),
             render.amplify565(np.array([0x8410, 0x0000, 0x4208]), np.array([0xffff, 0xffff, 0x4208])).tolist())
    report('Blend modes: 16-bit integer arithmetic', int(exact == (
        [0xf7de, 0x7bef, 0x0000, 0x8410], [0xffff, 0x8410, 0x0000, 0x8410], [0xffdf, 0x0000, 0x528a])), 1, exact)
    # Edge spans of a frame: one entry per RLE run/literal of the edge block (the MMX groups)
    f = 'Cache/Models/Environments/General/JungleGoodieBox.mdl16'
    lay = mdl.load(ds.read(f), f).sequence('Idle Shadow').frames[0].layers16()
    report('Frame edge spans', int(lay is not None and lay.edge_mask.sum() == 663 and lay.span_len[21, 6] == 17
                                   and (lay.span_start[lay.edge_mask] >= 0).all()), 1)
    # Sorting per layer: "Sorting Y Offset" and "Cutting Lines" (vertical strips, Zax.exe 0x4886a0)
    strips = {}
    for m in ('Cave/Walls/Cave Stone Wall 3', 'North Wasteland/Glacier Wall 4'):
        f = f'Cache/Models/Environments/{m}.mdl16'
        strips[m.split('/')[-1]] = mdl.load(ds.read(f), f).sequence('Idle').strips()
    inf = float('inf')
    report('Sorting strips (Cutting Lines)', int(strips == {
        'Cave Stone Wall 3': [(86, -inf, 13), (24, 13, 50), (0, 50, inf)],
        'Glacier Wall 4': [(0, -inf, 34), (-38, 34, inf)]}), 1, strips)
    # Polygons: key bottom edge + YSort (Zax.exe 0x55dc30), all polygons have YSort
    surf = [p for lv in loaded.values() for p in lv.parts if p.cls == 'CRenderablePolygon' and p.polygon]
    water = next((p for p in surf if p.get('YSort') == '-800'), None)
    key = render.surface_key(water) if water else None
    report('Polygon sorting (YSort)', int(all(p.get('YSort') is not None for p in surf)
                                              and key == (max(math.ceil(y) for _, y in water.polygon) - 800,
                                                          min(x for x, _ in water.polygon))), 1,
           {'polygons': len(surf), 'water with YSort -800': key})

    # Language pack (GERMAN.RED next to the game data): replaces dialogue, keeps levels and models
    root = Path(ds.root).resolve()
    pack = next((f for d in (root.parent, root.parent.parent) if d.is_dir()
                 for f in sorted(d.iterdir()) if f.suffix.lower() == '.red'), None)
    if pack is None:
        print('[--] Language pack: no .RED next to the game data')
    else:
        dp = DataSource(ds.root, pack)
        line = links.DialogScripts(dp).lines('ACT 1/M1M2/Mission01n2', '01 Zax Are you ok') or ['']
        checks = [dp.read('Levels/ACT 1/M1M2/Mission01n2.RDS') != ds.read('Levels/ACT 1/M1M2/Mission01n2.RDS'),
                  dp.exists('Local.txt') and not ds.exists('Local.txt'),
                  set(ds.list()) <= set(dp.list()),
                  all(not dp.in_pack(f) for f in ds.list('Levels/', '.zax') + ds.list('Cache/Models/', '.mdl16'))]
        report(f'Language pack {pack.name}', sum(checks), len(checks),
               {'files': len(dp.list()) - len(ds.list()), 'line': line[0][:40]})
        _check_rds(dp, zaxs, report, pack.name)

    # 6. Model headers (CModel + default object) - needs Zax.exe next to the game data
    exe = find_exe(ds)
    if exe is None:
        print('[--] Model headers: Zax.exe not found (put it next to Data/ or Data.dat)')
    else:
        import tempfile
        mh = ModelHead(Schema.open(exe, ds, Path(tempfile.gettempdir()) / 'zax-selftest'))
        ok, bad, stats = 0, [], Counter()
        for f in mdls:
            name = f[len('Cache/Models/'):-len('.mdl16')]
            try:
                m = mh.decode(ds.read(f))
            except DecodeError as e:
                bad.append(f'{name}: {e}'[:120])
                continue
            node = mh.default_part(m, name)
            if node is not None:
                text = tf.dumps(tf.Node(None, '<document>', [node]))
                if tf.dumps(tf.loads(text)) != text:
                    bad.append(f'{name}: default object not lossless')
                    continue
                stats['with default object'] += 1
            ok += 1
        report('Model headers (CModel) read', ok, len(mdls), bad[:3] or dict(stats))

        # Field help texts (FieldDesc_SetHelp 0x419020) and the class of every field: the field lists
        # must equal zax-decomp/docs/fields.csv (zax-decomp/tools/exe_classes.py), the texts stay out of the repository
        sch = mh.s
        ref: dict[str, list[str]] = {}
        fields_csv = DECOMP / 'docs' / 'fields.csv'
        if fields_csv.is_file():
            with open(fields_csv, newline='', encoding='utf-8') as fh:
                for r in csv.DictReader(fh):
                    ref.setdefault(r['class'], []).append(r['name'])
        else:
            print(f'(no {fields_csv}: the field lists are compared with nothing)')
        same = sum([f['name'] for f in c['fields']] == ref.get(n, []) for n, c in sch.classes.items())
        allf = [f for c in sch.classes.values() for f in c['fields']]
        helped = [f for f in allf if f.get('help')]
        sub = next((n for n, c in sch.classes.items() if c['parent'] == 'CRotationSequence'), None)
        checks = [len(helped) >= 250, bool(sch.help('CRotationSequence', 'Auto-Animate')),
                  sub is None or sch.help(sub, 'Auto-Animate') == sch.help('CRotationSequence', 'Auto-Animate'),
                  sch.help('CRotationSequence', 'No Such Field') is None]
        if ref:
            report('Fields per class as in zax-decomp/docs/fields.csv', same, len(sch.classes))
        report('Field help texts from Zax.exe', sum(checks), len(checks),
               {'fields': len(allf), 'with help text': len(helped)})

        # Our own help texts from the reimplementation (zaxtools/fieldhelp.py): every key a field of its
        # registering class, written once per table; corrections only for fields with an exe text; known evidence levels and correction kinds
        import ast
        from zaxtools import fieldhelp
        own = {(n, f['name']): f for n, c in sch.classes.items() for f in c['fields']}
        dicts = [d for d in ast.walk(ast.parse((ROOT / 'zaxtools' / 'fieldhelp.py').read_text(encoding='utf-8')))
                 if isinstance(d, ast.Dict) and d.keys and all(isinstance(k, ast.Tuple) for k in d.keys)]
        keys = [ast.literal_eval(k) for d in dicts for k in d.keys]
        dup = sum(len(d.keys) - len({ast.literal_eval(k) for k in d.keys}) for d in dicts)
        bad = [k for k in fieldhelp.HELP if k not in own]
        bad += [k for k in fieldhelp.CORRECTIONS if k not in own or not own[k].get('help')]
        bad += [k for k, v in fieldhelp.HELP.items() if v[0] not in fieldhelp.EVIDENCE or not v[2]]
        bad += [k for k, v in fieldhelp.CORRECTIONS.items()
                if v[0] not in fieldhelp.CHECK or v[1] not in fieldhelp.EVIDENCE or not v[3]]
        tip = fieldhelp.help_text('CLayerPart', 'Active') or ''
        report('Own field help texts: real fields, no duplicates', len(keys) - len(bad) - dup, len(keys),
               bad[:3] or {'help texts': len(fieldhelp.HELP), 'corrections': len(fieldhelp.CORRECTIONS),
                           'fields without any help': sum(1 for k, f in own.items()
                                                         if not f.get('help') and k not in fieldhelp.HELP)})
        report('Own field help text marked as derived from the game code', int(tip.startswith('From the game code')), 1)

        # Value kinds, limits and defaults from the constructors' arguments, name lists (AddEnum,
        # AddEnumFloat, enum tables of the typed resources) and the flags' lists from the game data;
        # known values from zax-decomp/docs/DECOMPILATION.md section 6 ("Definition classes", "Field kinds", stats)
        from zaxtools import exeschema as es
        kinds = Counter(f.get('kind') for f in allf)
        fv = sch.field
        hue, quip = fv('CHueRemapHolder', 'Source Hue 1'), fv('CQuipCategory', 'Delay Before Saying')
        inv = fv('CItemTypeData', 'Cur Inventory Index')
        cat, used = fv('CLayerPart', 'Category'), fv('CLayerPart', 'Used In')
        cats, games = es.flag_names(ds, cat['list']), es.flag_names(ds, used['list'])
        checks = [
            kinds['enum'] >= 200, kinds['float'] >= 300, kinds['int'] >= 60, kinds['flags'] == 11,
            kinds['choice'] >= 50, sum(bool(f.get('enum')) for f in allf) >= 20,
            (hue['default'], hue['min'], hue['max'], hue['step']) == (268.0, 0.0, 360.0, 0.5),
            (quip['default'], quip['min'], quip['max'], quip.get('units')) == (1.5, 0.0, 1e9, 'Seconds'),
            fv('CHueRemapHolder', 'Error 2')['default'] == 4.0 and fv('CHueRemapHolder', 'Error 2')['max'] == 100.0,
            fv('CNormalAttackAI', 'Minimum Attack Distance')['default'] == 100.0,
            ['Do not move while attacking'] == sch.names('CNormalAttackAI', 'Minimum Attack Distance'),
            (inv['default'], inv['min'], inv['max']) == (0xffffffff, 0, 999999),
            es.value_text(inv, inv['default']) == 'None Selected',
            fv('CDamageTypeDefinition', 'Unavoidable damage')['default'] == 0,
            fv('CQuestGameType', 'Scroll Rate')['units'] == 'Pixels/Tick',
            es.value_text(fv('CQuestGameType', 'Scroll Rate'), fv('CQuestGameType', 'Scroll Rate')['default']) == '0.01',
            cat.get('default') == '' and used.get('default', '').lower() == '$all',
            cats == ['Enemy', 'Enemy Shot', 'NonInteractiveSequence Actor', 'Player', 'Player Friend',
                     'Player Shot', 'Top Hide'],
            games == ['MultiPlayer/Capture The Flag', 'MultiPlayer/Death Match', 'MultiPlayer/Salvage King',
                      'QuestMode'],
            es.default_text(used, games) == ','.join(games),
            fv('CRenderablePolygon', 'Render Type')['choices'][:2] == ['Black', 'Shadow'],
            es.choice_find(fv('CSkeletonAI', 'State'), 'unknown') == 5,      # an alternative name
            es.game_read(hue, '400') == 360.0 and es.game_read(hue, '-3') == 0.0,
            es.out_of_limits(fv('CNormalAttackAI', 'Minimum Attack Distance'), '0.25') == '1',
            es.flags_parse('Enemy,,Player', cats) == ({'Enemy', 'Player'}, ['']),
        ]
        report('Field kinds, limits and defaults from Zax.exe', sum(checks), len(checks), dict(kinds))

        # every value of the kinds with names in the game data is one the game accepts, written the way
        # the editor writes it (flags: names in list order without blanks; choices: the table's spelling)
        flists = {a: es.flag_names(ds, a) for a in es.FLAG_LISTS}
        seen, bad = Counter(), []

        def walk_values(n, cls):
            for c in n.children:
                if isinstance(c, tf.Entry) and cls:
                    f = sch.field(cls, c.key)
                    k = f and f.get('kind')
                    if k == 'flags' and flists.get(f.get('list')) is not None:
                        have, wrong = es.flags_parse(c.value, flists[f['list']])
                        seen['flags'] += 1
                        if wrong or es.flags_text(flists[f['list']], have) != c.value:
                            bad.append(f'{cls}.{c.key}={c.value}')
                    elif k == 'choice':
                        seen['choice'] += 1
                        i = es.choice_find(f, c.value)
                        if i is None or f['choices'][i] != c.value:
                            bad.append(f'{cls}.{c.key}={c.value}')
                    elif k in ('int', 'enum', 'float', 'double'):
                        seen['number'] += 1
                        if es.out_of_limits(f, c.value) is not None:
                            bad.append(f'{cls}.{c.key}={c.value} -> {es.out_of_limits(f, c.value)}')
                elif isinstance(c, tf.Node):
                    walk_values(c, c.value if sch.known(c.value) else None)

        for f in zaxs:
            walk_values(tf.load_bytes(ds.read(f)), None)
        report('Names, flags and limits of the level values as the game reads them',
               sum(seen.values()) - len(bad), sum(seen.values()), bad[:3] or dict(seen))

    # 7. AI overlays (zaxtools.overlays): shapes of AIs in 01 Main against values computed by hand from
    # the reimplemented drawing (zax-decomp/reimpl/src/ai_draw_c5.cpp, view_draw.cpp, ai_patrol.cpp)
    _check_overlays(ds, report, ModelHead(Schema.open(exe, ds, Path(tempfile.gettempdir()) / 'zax-selftest'))
                    if exe is not None else None)

    # 7. Level check (zaxtools/levelcheck.py): the original levels give no crash finding (the game loads
    # them all), and every crash check fires on its broken test level (written into a temporary folder)
    import tempfile
    import check_levels
    from zaxtools import levelcheck
    lc_schema = Schema.open(exe, ds, Path(tempfile.gettempdir()) / 'zax-selftest') if exe else None
    ctx = levelcheck.Context(ds, lc_schema, exe)
    levels = sample(ds.list('Levels/', '.zax'))
    ok, bad, per = 0, [], Counter()
    for f in levels:
        found = levelcheck.check(Level.from_bytes(ds.read(f)), ctx, f[len('Levels/'):])
        per.update(x.severity for x in found)
        errs = [x for x in found if x.severity == 'error'
                and (f, x.check) not in check_levels.KNOWN_ORIGINAL_ERRORS]
        if errs:
            bad.append(f'{f}: {errs[0].check} {errs[0].value!r}')
        else:
            ok += 1
    report('Level check: no crash finding in the original levels', ok, len(levels), bad[:3] or dict(per))
    with tempfile.TemporaryDirectory() as tmp:
        good = check_levels.broken_cases(ds, lc_schema, exe, Path(tmp))
    report('Level check: every crash check fires on its broken level', int(good), 1)

    # 8. Rules.txt, Team Info and the level header (zaxtools/rules.py, header.py)
    _check_rules_header(ds, report, sample(ds.list('Levels/', '.zax')))

    # 8b. The mini map as the game draws it (minimap.render_game_minimap) against the shipped ones
    _check_game_minimap(ds, report, quick)

    # 8c. Animations as in the game (zaxtools.anim) over all levels, renderer polygon outlines
    _check_animation(ds, report, sample, quick)

    # 8c2. Child objects (upper bodies, attached effects, carried items) as the game draws them
    _check_children(ds, report, sample, quick)

    # 8c3. Editing child objects (zaxtools/children.py): add/remove only rewrite their lines, undo states, new
    # upper bodies and attached objects, the level check's child checks, nested children, copy/paste of child objects
    _check_child_edit(ds, report, sample, exe)

    # 8d. The model viewer's previews (zaxtools/preview.py): layers, drawing order, frame triggers and their
    # sounds, the sequence writer, 8-bit bands
    _check_preview(ds, report, sample, exe)

    # 8e. The model writer (zaxtools/mdlfile.py) and the image import (zaxtools/imageimport.py)
    _check_import(ds, report, sample, exe, quick)

    # 8f. The game's use of the assets (zaxtools/usage.py) and the transitions to missing levels
    _check_usage(ds, report, exe, quick)

    # 9. UI translations: the editor's, since the split of 2026-11-07 in zax-editor/tools/selftest_ui.py

    print(f'\nDone in {time.time() - t0:.0f} s, {failures} failures.')
    raise SystemExit(1 if failures else 0)


def _check_import(ds, report, sample, exe, quick):
    """8e. Every model file comes back byte for byte from mdlfile.parse + dumps (.mdl16 and .mdl), every simple
    header from dumps_head; the 8-bit colour lookup equals the shipped inverse colour table; an imported model, image
    and sequence read back with the images' pixels."""
    import tempfile
    from zaxtools import imageimport, mdlfile
    if exe is None:
        print('[--] Model writer: Zax.exe not found')
        return
    sch = Schema.open(exe, ds, Path(tempfile.gettempdir()) / 'zax-selftest')
    mh = ModelHead(sch)
    files = sample([f for f in ds.list('Cache/Models/', '') if f.lower().endswith(('.mdl16', '.mdl'))])
    ok, bad, heads, hok = 0, [], 0, 0
    for f in files:
        d = ds.read(f)
        try:
            m = mdlfile.parse(d, mh)
            good = mdlfile.dumps(m) == d
        except (ValueError, DecodeError, struct.error) as e:
            bad.append(f'{f}: {e}')
            continue
        ok += good
        if not good:
            bad.append(f)
        if f.endswith('.mdl16'):
            o = mh.decode(d)
            v = o.values
            if not (o.dynamic or v['Activity'] or v['Default Entity'] is not None or v['Fidget Settings'] is not None):
                heads += 1
                hok += mdlfile.dumps_head(v, sch) == m.head
    report('Model writer: every model file written back byte for byte', ok, len(files), bad[:3] or '')
    report('Model writer: every simple CModel header (no default object) written back byte for byte', hok, heads,
           '' if quick else f'(all: {heads}, the originals: 626)')
    if not quick:
        report('Model writer: 626 simple headers in the German edition', int(heads == 626), 1, heads)
    # 8-bit colours: InvColorTable15.pal is the nearest GamePalette entry 1..254 (weights 30/59/11) of (r, g, b) * 8
    inv = np.frombuffer(ds.read(frm.INV_COLOR_TABLE15), np.uint8)
    pal = frm.load_palette(ds.read('Palettes/GamePalette.pal')).astype(np.int64)
    idx = np.arange(0, 32768, 64 if quick else 1)
    rgb = np.stack([(idx >> 10) & 31, (idx >> 5) & 31, idx & 31], -1) * 8
    near = np.empty(len(idx), np.int64)
    for i in range(0, len(idx), 2048):
        dd = (((rgb[i:i + 2048, None, :] - pal[None, 1:255]) ** 2) * np.array([30, 59, 11])).sum(-1)
        near[i:i + 2048] = dd.argmin(-1) + 1
    report('Import: the 5-5-5 inverse colour table is the nearest palette colour', int((near == inv[idx]).sum()),
           len(idx))
    full = np.rint(rgb / 8 * 255 / 31).astype(np.uint8)        # the 8-bit colour of each 5-5-5 value
    ok8 = int((frm.nearest_index8(full, inv) == inv[idx]).all())
    report('Import: nearest_index8 of an 8-bit colour is the table entry of its 5-5-5 value', ok8, 1)
    # an import: a soft-edged series as a model, a sequence and an image
    h, w = 40, 30
    yy, xx = np.mgrid[0:h, 0:w]
    ims = []
    for k in range(3):
        a = np.clip((1 - np.hypot(xx - 15, yy - 20) / 14) * 4, 0, 1) * 255
        ims.append(np.dstack([np.full((h, w), 40 + 60 * k), (xx * 8) % 256, (yy * 6) % 256, a]).astype(np.uint8))
    spec = imageimport.ImportSpec('model', 'Selftest Gem', 'Own', ims, hot=(15, 39), fps=12)
    out = imageimport.build(spec, inv.tobytes(), sch)
    m16 = mdl.load(out['Cache/Models/Own/Selftest Gem.mdl16'], 'x')
    m8 = mdl.load(out['Cache/Models/Own/Selftest Gem.mdl'], 'x', frm.load_palette(ds.read('Palettes/GamePalette.pal')))
    s16, s8 = m16.sequences[0], m8.sequences[0]
    exp = frm.rgb565_to_rgb(frm.rgb_to_rgb565(ims[1][..., :3]))
    f16 = s16.frame(0, 1)
    vis = ims[1][..., 3] > 250
    checks = [s16.name == 'Idle', s16.total == 3, s16.rotations == 1, abs(s16.fps - 12) < 1e-6, s16.auto_animate,
              (f16.hot_x, f16.hot_y) == (15, 39), bool((f16.rgba[..., :3][vis] == exp[vis]).all()),
              s8.total == 3, mh.decode(out['Cache/Models/Own/Selftest Gem.mdl16']).values['Default Sequence'] == 'Idle',
              all(mdlfile.dumps(mdlfile.parse(d, mh)) == d for d in out.values())]
    vals8 = frm.values(out['Cache/Models/Own/Selftest Gem.mdl'], m8.sequences[0].frame(0, 1).offset)
    checks.append(bool((vals8.values[vis] == frm.nearest_index8(ims[1][..., :3], inv)[vis]).all()))
    sq = imageimport.build(imageimport.ImportSpec('sequence', 'Selftest Glow', 'Sequences', ims, fps=8), inv.tobytes())
    sf = seq.load(sq['Cache/Sequences/Selftest Glow.seq16'])
    checks += [sf.total == 3, abs(sf.fps - 8) < 1e-6, sf.box == (0, 0, w, h)]
    im = imageimport.build(imageimport.ImportSpec('image', 'Selftest Icon', 'Interface', ims[:1], hot=(2, 3)),
                           inv.tobytes())
    hd = frm.read_header(im['Cache/Interface/Selftest Icon.frm16'])
    checks += [(hd.hot_x, hd.hot_y, hd.width, hd.height) == (2, 3, w, h),
               frm.read_header(im['Cache/Interface/Selftest Icon.frm']).bpp == 8]
    rep = imageimport.replace_frames(ds.read('Cache/Models/Environments/CrashDebris/RockyPieces1.mdl16'), mh, 'Idle',
                                     ims[:1], (15, 39))
    checks.append(mdl.load(rep, 'x').sequences[0].frame(0, 0).rgba.shape[:2] == (h, w))
    report('Import: model, sequence, image and a replaced sequence read back as written', sum(checks), len(checks))
    # textures: an animated texture and a ground texture are raw and opaque, like the shipped ones
    tex = [np.dstack([(xx2 := np.mgrid[0:128, 0:128])[1] * 2, xx2[0] * 2, np.full((128, 128), 9 * k),
                      np.full((128, 128), 255)]).astype(np.uint8) for k in range(2)]
    pal8 = frm.load_palette(ds.read('Palettes/GamePalette.pal'))
    ts = imageimport.ImportSpec('sequence', 'Selftest Water', 'Animated Textures/Own', tex, fps=12)
    out = imageimport.build(ts, inv.tobytes())
    s16 = seq.load(out['Cache/Animated Textures/Own/Selftest Water.seq16'])
    s8 = seq.load(out['Cache/Animated Textures/Own/Selftest Water.seq'], pal8)
    d8 = out['Cache/Animated Textures/Own/Selftest Water.seq']
    h8 = frm.read_header(d8, s8.frames[0].offset)
    ref = ds.read('Cache/Animated Textures/Water Green Dark.seq')
    rs = seq.load(ref, pal8)
    rh = frm.read_header(ref, rs.frames[0].offset)
    checks = [ts.texture, not imageimport.ImportSpec('sequence', 'x', 'Sequences', tex).texture,
              imageimport.ImportSpec('image', 'x', 'Textures/Own', tex[:1]).texture, s16.total == 2,
              (h8.rle, h8.flags, h8.hot_x, h8.hot_y) == (rh.rle, rh.flags, rh.hot_x, rh.hot_y),
              s8.load_flags == rs.load_flags == imageimport.TEXTURE_LOAD_FLAGS, s8.box == rs.box,
              bool((s8.frames[1].rgba[..., :3] == pal8[frm.nearest_index8(tex[1][..., :3], inv)]).all()),
              bool((s16.frames[0].rgba[..., 3] == 255).all()), not imageimport.notes(ts)]
    gt = imageimport.build(imageimport.ImportSpec('image', 'Selftest Floor', 'Textures/Own', [tex[0][:64]]),
                           inv.tobytes())
    gh = frm.read_header(gt['Cache/Textures/Own/Selftest Floor.frm16'])
    soft = tex[0].copy()
    soft[0, 0, 3] = 100
    checks += [(gh.rle, gh.hot_x, gh.hot_y, gh.height) == (False, 0, 0, 64),
               len(imageimport.notes(imageimport.ImportSpec('image', 'x', 'Textures', [soft[:64]]))) == 2]
    report('Import: textures written raw and opaque like the shipped ones', sum(checks), len(checks))


def _check_usage(ds, report, exe, quick):
    """8f. The game's use of the assets (zaxtools.usage): the counts of the analysis of 2026-10-29 on the full
    data; in quick mode only the inventory and a few resolutions. The transitions to missing levels."""
    import tempfile
    from zaxtools import levelcheck, usage
    if exe is None:
        print('[--] Asset use: Zax.exe not found')
        return
    cache = Path(tempfile.gettempdir()) / 'zax-selftest'
    if quick:
        a = usage._Analysis(ds, None, b'')
        a.inventory()
        a.build_index()
        hits = {v: [t for t, _ in a.resolve(v)] for v in ('Particles/Smoke Puff', 'Sounds/Error.wav', 'Main Zax Font',
                                                           'Act 1/M1M2/01 Main')}
        checks = [len(a.assets) == 2987, 'models:particles/smoke puff' in hits['Particles/Smoke Puff'],
                  'sounds:error.wav' in hits['Sounds/Error.wav'], 'fonts:main zax font' in hits['Main Zax Font'],
                  'levels:act 1/m1m2/01 main' in hits['Act 1/M1M2/01 Main']]
        report('Asset use (quick): the inventory (2,987 assets) and sample names resolve', sum(checks), len(checks))
    else:
        u = usage.analyze(ds, exe, cache_dir=cache)
        c, mv = u.counts(), u.models_vs_level_use()
        got = (c['total'], c['unused'], c['possibly'], c['missing'], mv['not_placed'], mv['not_placed_used'],
               mv['not_placed_possibly'], mv['not_placed_unused'])
        want = (2987, 358, 31, 10, 235, 101, 9, 125)
        report('Asset use: 2,987 assets, 358 never used, 31 possibly, 10 missing; of the 235 models placed in no '
               'level 101 used, 9 possibly, 125 never', int(got == want), 1, got)
        names = {m.name for m in u.missing}
        report('Asset use: the missing levels Demo Mission2 and Hasbro Start',
               int({'Levels/Demo Mission2.zax', 'Levels/Hasbro Start.zax'} <= names), 1)
    ctx = levelcheck.Context(ds)
    if quick:
        files = ['Levels/ACT 3/M19/19 Volcanic Run Pit.zax', 'Levels/ACT 1/M1M2/01 Main.zax']
    else:
        files = ds.list('Levels/', '.zax')
    per: dict[str, set] = {}
    for f in files:
        for x in levelcheck.check(Level.from_bytes(ds.read(f)), ctx, f[len('Levels/'):]):
            if x.check == 'missing-target-level':
                per.setdefault(x.value, set()).add(f)
    got = {k: len(v) for k, v in per.items()}
    want = {'Demo Mission2': 1, 'Hasbro Start': 1} if quick else {'Demo Mission2': 5, 'Hasbro Start': 2}
    report('Level check: transitions to missing levels (the originals: Demo Mission2 in 5 levels, Hasbro Start in 2)',
           int(got == want), 1, got)


def _check_encoder(ds, report, sample, pal):
    """4b. The game's frame encoder (frm.encode, seq.dumps): decoding a frame and encoding its values
    gives the file byte for byte, for every .frm/.frm16 and every image sequence (docs/FORMATS.md 5)."""
    for suffix in ('.frm', '.frm16'):
        files, ok, bad = sample(ds.list('', suffix)), 0, []
        for f in files:
            d = ds.read(f)
            try:
                good = frm.encode(frm.values(d)) == d
            except ValueError as e:
                good, f = False, f'{f}: {e}'
            ok += good
            if not good:
                bad.append(f)
        report(f'Images {suffix} encoded byte for byte', ok, len(files), bad[:3] or '')
    files = [f for f in sample(ds.list('', '.seq') + ds.list('', '.seq16')) if ds.read(f)[:8] == seq.TAG]
    ok, bad = 0, []
    for f in files:
        d = ds.read(f)
        s = seq.load(d, pal)
        try:
            frames = [None if x is None else frm.encode(frm.values(d, x.offset)) for x in s.frames]
            good = seq.dumps(frames, s.fps_raw, s.mode, s.load_flags, s.offset) == d
        except ValueError as e:
            good, f = False, f'{f}: {e}'
        ok += good
        if not good:
            bad.append(f)
    report('Image sequences .seq/.seq16 encoded byte for byte', ok, len(files), bad[:3] or '')
    # An own RGBA image: soft edge (6-250) and dropped pixels (0-5) as the game splits them
    rgba = np.zeros((4, 12, 4), np.uint8)
    rgba[..., :3] = (200, 100, 50)
    rgba[..., 3] = np.array([255, 251, 250, 128, 6, 5, 0, 255, 255, 255, 255, 255], np.uint8)
    back, hd, _ = frm.decode(frm.encode_rgba16(rgba, hot=(3, -2)))
    ok = ((back[..., 3] == np.where(rgba[..., 3] > 5, np.where(rgba[..., 3] > 250, 255, rgba[..., 3]), 0)).all(),
          (back[..., :3][rgba[..., 3] > 5] == frm.rgb565_to_rgb(frm.rgb_to_rgb565(rgba[..., :3]))[rgba[..., 3] > 5]).all(),
          (hd.hot_x, hd.hot_y, hd.flags) == (3, -2, 0x2044))
    report('Own RGBA image encoded (alpha bands, hot spot, flags)', sum(ok), len(ok))


def _check_waymap(ds, report, sample):
    """waymap.build on every level against the shipped .way (needs Zax.exe for the models' AIs), the
    analysis helpers and the level check's way point findings on a small level of our own."""
    import tempfile
    exe = find_exe(ds)
    if exe is None:
        print('[--] Way point map: Zax.exe not found (the models\' AIs decide what blocks a way point)')
        return
    md = waymap.model_data_source(ds, ModelHead(Schema.open(exe, ds, Path(tempfile.gettempdir()) / 'zax-selftest')))
    ok, bad, times = 0, [], []
    for f in sample(ds.list('Levels/', '.zax')):
        t = time.time()
        r = waymap.build(Level.from_bytes(ds.read(f)), md)
        times.append(time.time() - t)
        if way.dumps(r.way) == ds.read(f[:-4] + '.way') and r.exact:
            ok += 1
        else:
            bad.append(f)
    report('Way point map as the game builds it, equal to the shipped .way', ok, len(times),
           bad[:3] or f'{sum(times):.0f} s, at most {max(times):.1f} s per level')
    # the table atan2 and the polygon text as the game reads them
    p = waymap.poly_from_text(', '.join(f'{i}, {i * 2}' for i in range(30)) + ', 5, 5, 5, 5')
    q = waymap.poly_from_text('1, 1, 1, 1, 7.5, 2')
    checks = (waymap.table_atan2(0.0, 0.0) == waymap.PI, waymap.table_atan2(0.0, 5.0) == 0.0,
              abs(waymap.table_atan2(1.0, 1.0) - math.pi / 4) < 1e-3, p.count == 25, q.points() == [(1, 1), (7.5, 2)])
    report('Way point map helpers (table atan2, polygon text with its 25-point limit)', sum(checks), len(checks))
    # level check findings on a level of our own: an island, an unreachable walking character, 26 points
    from zaxtools import levelcheck
    lv = newlevel.new_level('Test/WayCheck', 2000, 1500, ['11 Dirt'])
    def add(text):
        lv.insert_part(next(n for n in tf.loads(text.replace("\n", tf.NL)).children if isinstance(n, tf.Node)))
    add('Level Part=CWayPointsPolygon\n{\n\tPolygon=200, 200, 800, 200, 800, 600, 200, 600, 200, 200\n}')
    add('Level Part=CWayPointsPolygon\n{\n\tPolygon=1400, 900, 1700, 900, 1700, 1200, 1400, 1200, 1400, 900\n}')
    add('Level Part=CWayPointsPolygon\n{\n\tPolygon=' + ', '.join(f'{100 + i * 10}, 1400' for i in range(26)) + '\n}')
    add('Level Part=CEntityWalking\n{\n\tName=Far\n\tPosition X=1000\n\tPosition Y=1100\n}')
    ctx = levelcheck.Context(ds, None, None)
    found = {x.check for x in levelcheck.check(lv, ctx, 'Test/WayCheck.zax')}
    want = {'way-island', 'way-unreachable', 'polygon-points'}
    report('Level check: way point island, object far from the network, polygon over 25 points',
           len(want & found), len(want), sorted(want - found) or '')


def _check_game_minimap(ds, report, quick):
    """minimap.render_game_minimap against the shipped mini maps: every shipped image lies in the image
    rectangle of 0x4ec280, and the drawing of some levels equals most pixels (all 112: 98.0 % equal,
    docs/FORMATS.md mini maps; the rest is the renderer's)."""
    levels = [f for f in ds.list('Levels/', '.zax')]
    ok = n = 0
    for f in levels:
        lv = Level.from_bytes(ds.read(f))
        mp = minimap.minimap_path(lv)
        if not ds.exists(mp):
            continue
        n += 1
        px = frm.rgb_to_rgb565(frm.decode(ds.read(mp))[0][..., :3])
        ys, xs = np.nonzero(px != minimap.BACKGROUND565)
        x0, y0, x1, y1 = minimap.image_rect(lv)
        ok += len(xs) > 0 and xs.min() >= x0 and ys.min() >= y0 and xs.max() < x1 and ys.max() < y1
    report('Shipped mini maps inside the image rectangle the game computes (0x4ec280)', ok, n)
    picks = ['Levels/ACT 1/M1M2/02 Cave2.zax', 'Levels/ACT 2/M9/09 Assimilate Cave1.zax'] + \
        ([] if quick else ['Levels/ACT 1/M3/03 Intelligence Main.zax', 'Levels/ACT 1/M1M2/01 TargDens.zax'])
    assets = render.Assets(ds)
    exe = find_exe(ds)
    if exe is not None:
        import tempfile
        from zaxtools.catalog import Catalog
        assets.sort_y = Catalog.open(ds, Path(tempfile.gettempdir()) / 'zax-selftest', exe=exe).sorting_y()
    shares = []
    for f in picks:
        lv = Level.from_bytes(ds.read(f))
        ship = frm.rgb_to_rgb565(frm.decode(ds.read(minimap.minimap_path(lv)))[0][..., :3])
        shares.append(float((minimap.render_game_minimap(lv, assets) == ship).mean()))
    good = sum(s >= 0.9 for s in shares)
    report('Mini map drawn as the game draws it: at least 90 % of the pixels equal the shipped one', good, len(shares),
           ', '.join(f'{s * 100:.1f} %' for s in shares))


# German UI text outside translate(): umlauts, German quotes or frequent German words (case-sensitive,
# chosen so that English UI texts, class and field names do not hit them)
def _changed_lines(a: bytes, b: bytes) -> list[str]:
    import difflib
    return [d for d in difflib.unified_diff(a.decode('latin-1').split('\r\n'), b.decode('latin-1').split('\r\n'),
                                            lineterm='', n=0) if d[:1] in '+-' and d[:3] not in ('+++', '---')]


def _check_rules_header(ds, report, zaxs):
    """Rules.txt and the Team Info of every level written back byte for byte, a change only in its own
    line; every header field of the levels has its group in the settings view; the songs of the levels and
    Rules.txt are names of the music folder list."""
    import tempfile
    from zaxtools import header, rules
    raw = ds.read('Rules.txt')
    rf = rules.from_data(ds)
    same = rf.to_bytes() == raw
    rules.set_start(rf, rf.first_map, rf.first_spawn)
    same_set = rf.to_bytes() == raw
    rules.set_start(rf, 'Test/Rules', 'Start 2')
    diff = _changed_lines(raw, rf.to_bytes())
    with tempfile.TemporaryDirectory() as tmp:
        out = rules.save(rf, Path(tmp))
        again = rules.load(ds, Path(tmp))
        saved = out.read_bytes() == rf.to_bytes() and again.source == 'output' and again.first_spawn == 'Start 2'
    music = header.music_names(ds)
    ok = (same, same_set, diff == ['-\tFirst Map Name=Act 1/M1M2/01 Main', '-\tFirst Map Spawn Point=Game Start ',
                                   '+\tFirst Map Name=Test/Rules', '+\tFirst Map Spawn Point=Start 2'],
          saved, rules.from_data(ds).first_spawn == 'Game Start ',
          header.is_music_name(music, tf.root(tf.load_bytes(raw)).get('Startup Song')),
          rules.find_level(rules.level_files(ds, None), 'act 1\\m1m2\\01 main') == 'ACT 1/M1M2/01 Main')
    report('Rules.txt: byte for byte, start level/point change only their lines, saved and read back', sum(ok),
           len(ok))
    ok, bad, teams = 0, [], 0
    for f in zaxs:
        b = ds.read(f)
        lv = Level.from_bytes(b)
        infos = header.team_infos(lv)
        teams += len(infos)
        good = infos or tf.root(tf.load_bytes(b)).block('Team Info').get('Item Count') == '0'   # 01 TargDens
        for t in infos:
            for k in ('Spawn Point Name', 'Re-Spawn Point Name', 'Model Type'):
                if t.get(k) is not None:
                    t.set(k, t.get(k))
        good = good and lv.to_bytes() == b
        if infos:
            old = infos[0].get('Spawn Point Name')
            infos[0].set('Spawn Point Name', 'Elsewhere')
            good = good and _changed_lines(b, lv.to_bytes()) == [f'-\t\t\tSpawn Point Name={old}',
                                                                 '+\t\t\tSpawn Point Name=Elsewhere']
        groups = header.layout(lv.root)
        shown = [c for _, _, items in groups for c in items]
        rest = [c.key for c in lv.root.children if not isinstance(c, tf.Raw) and c.key not in header.HIDDEN]
        good = good and len(shown) == len(rest) and not [g for g, _, _ in groups if g == header.OTHER[0]]
        mix = lv.root.block('Music Mix')
        if mix is not None:
            good = good and all(header.is_music_name(music, mix.get(k, '')) for k in header.SONG_KEYS)
        if good:
            ok += 1
        else:
            bad.append(f)
    nm = header.music_node(tuple(newlevel.MUSIC[0][1:]))
    nl = newlevel.new_level('Test/New', 3000, 2500, ['11 Dirt'], music=tuple(newlevel.MUSIC[0][1:]))
    ok += tf.dumps(nm) == tf.dumps(nl.root.block('Music Mix'))
    report(f'Team Info ({teams} entries) and header layout of the levels, music block as a new level writes it',
           ok, len(zaxs) + 1, bad[:3] or '')


def _check_ground_pieces(ds, zaxs, report):
    """render.Ground (pieces, tables, small integer types) against the former whole-box computation (plasma values
    -> blend_weight -> mix16 over np.mgrid), which this keeps as the reference: boxes across piece and plasma tile
    borders, at odd offsets, step 1 and 2, on every level. (All 112 levels whole, step 1 and 2, were compared byte
    for byte when Ground replaced it, 2026-11-08.)"""
    def reference(lv, assets, box, step):
        x0, y0, x1, y1 = box
        T = np.stack([render._tile128(assets.texture(n)) for n in lv.ground_textures])
        N = len(lv.ground_textures)
        ys, xs = np.mgrid[y0:y1:step, x0:x1:step].astype(np.float32)
        v = render.ground_values(lv, xs.astype(int), ys.astype(int))
        i, f = render.blend_weight(v, N, render.blending(lv))
        tx, ty = xs.astype(int) % 128, ys.astype(int) % 128
        return render.mix16(T[i, ty, tx], T[np.minimum(i + 1, N - 1), ty, tx], f)
    assets = render.Assets(ds)
    ok = n = 0
    for k, f in enumerate(zaxs):
        lv = Level.from_bytes(ds.read(f))
        W, H = lv.size
        g = render.Ground(lv, assets)
        for step, (x, y, w, h) in ((1, (480 + 37 * k % 61, 450, 100, 140)), (2, (W - 731, H - 517, 731, 517)),
                                   (1, (-5, -3, 70, 66)), (2, (1, 1, 1100, 9))):
            box = (x, y, x + w, y + h)
            n += 1
            ok += np.array_equal(render.render_ground(lv, assets, box, step, surfaces=False, ground=g),
                                 reference(lv, assets, box, step))
    report('Ground: render.Ground (pieces, tables) equals the whole-box computation', ok, n)


def _check_next_changes(ds, assets, sample, got) -> list:
    """anim.timed_next / entity_next / layer_next (the editor redraws an object only when its frame changes):
    for the animated objects of the levels at several times, the frame stays the same at every millisecond (and
    just before the moment) until the time they give, and changes there. Returns the failures."""
    from zaxtools import anim
    bad, tried = [], 0
    rng = np.random.default_rng(7)
    for f in sample(ds.list('Levels/', '.zax'))[::4]:
        for p in Level.from_bytes(ds.read(f)).parts:
            m = assets.model(p.model) if p.position is not None and p.model else None
            if m is None:
                continue
            a = anim.part_animation(p, m)
            a.phase = anim.phase_of(p)
            layers = [s for _, s in m.layers(a.sequence)]
            cur = next((s for o, s in m.layers(a.sequence) if o == 2), None)
            for t in rng.uniform(0, 3000, 2).tolist() + [0.0]:
                for s in layers:
                    nxt = anim.layer_next(s, a, t)
                    if nxt == math.inf:
                        continue
                    tried += 1
                    off = 0 if s.sync_auto else a.phase
                    now = anim.timed_frame(t, s.fps, off)
                    ms = np.arange(math.floor(t * 1000) + 1, math.floor(nxt * 1000))
                    same = all(anim.timed_frame(x / 1000 + 0.0002, s.fps, off) == now for x in ms[:400])
                    if not same or anim.timed_frame(nxt, s.fps, off) == now and len(ms) < 2000 / abs(s.fps) + 2:
                        bad.append(f'{p.model} {s.name} t={t}')
                nxt = anim.entity_next(a, cur, t)
                if nxt < math.inf:
                    tried += 1
                    now = anim.frame_index(a, cur, t)
                    if anim.frame_index(a, cur, nxt - 2e-6) != now or anim.frame_index(a, cur, nxt) == now:
                        bad.append(f'{p.model} entity t={t}')
    got['next-change cases'] = tried
    return bad[:3]


def _check_animation(ds, report, sample, quick):
    """zaxtools.anim against values from the code (0x55fee0, 0x48feb0, 0x55e4b0, 0x4cb590) and the counts
    of the original levels; the renderer's polygon outlines and overlays."""
    from zaxtools import anim, mdl
    from zaxtools.render import Assets, POLYGON_COLORS, render_level
    checks, got = [], {}
    # hand-computed cases
    seq = mdl.Sequence('X', 9, 15.0, 'Transparent Mask', 1, 9, 0, 0, flags=bytes([0, 0, 1, 0, 0, 0]),
                       frames=[None] * 9)
    still = mdl.Sequence('Y', 9, 15.0, 'Transparent Mask', 1, 9, 0, 0, frames=[None] * 9)
    base = anim.PartAnim(False, 'Idle', phase=5067)
    checks += [anim.layer_frame(seq, base, 0, None) == 5067 % 9,             # Auto-Animate at game time 0
               anim.layer_frame(seq, base, 0, 1.0) == (15 + 5067) % 9,       # 15 frames later
               anim.layer_frame(still, base, 0, 5.0) == 0,                   # CEntityBase: frame 0 for good
               anim.layer_frame(still, base, 9, None) is None,               # index past the frames: nothing
               anim.wrap_frame(5.6, 15) == 5.6, anim.wrap_frame(-1.0, 15) == 14.0, anim.wrap_frame(31.0, 15) == 1.0,
               abs(anim.wrap_frame(2.25, 1) - 0.25) < 1e-9, anim.fistp(2.5) == 2, anim.fistp(3.5) == 4]
    loop = anim.PartAnim(True, 'Idle', 3.0, anim.Loop('', ping_pong=True))
    checks += [anim.entity_frame(loop, 10, 12.0, 1.0) == 5.0,                  # 3 + 12 = 15 -> 20 - 15
               anim.entity_frame(loop, 10, 12.0, None) == 3.0]
    # all levels: every object gets an animation; the looped AIs found where the originals have them
    assets = Assets(ds)
    counts = Counter()
    bad = []
    for f in sample(ds.list('Levels/', '.zax')):
        for p in Level.from_bytes(ds.read(f)).parts:
            if p.position is None or not p.model:
                continue
            m = assets.model(p.model)
            a = anim.part_animation(p, m)
            counts['objects'] += 1
            counts['looped'] += a.loop is not None
            counts['idle'] += a.idle
            if m is None:
                continue
            cur = next((s for o, s in m.layers(a.sequence) if o == 2), None)
            if cur is not None and not 0 <= a.frame < max(1, cur.frames_per_rotation):
                bad.append(f'{f}: {p.model} frame {a.frame}')
            fi = anim.frame_index(a, cur, None)
            for _, s in m.layers(a.sequence):
                k = anim.layer_frame(s, a, fi, None)
                if k is not None and not 0 <= k < s.frames_per_rotation:
                    bad.append(f'{f}: {p.model} {s.name} frame {k}')
    got.update(counts)
    checks += [not _check_next_changes(ds, assets, sample, got)]
    if not quick:                                           # full run: the counts of the originals
        checks += [counts['looped'] == 817, counts['idle'] == 2770]
    checks += [not bad]
    # renderer: polygon outlines in the editor's colours on top
    lv = Level.from_bytes(ds.read('Levels/ACT 1/M1M2/01 Main.zax'))
    wp = next(q for q in lv.parts if q.cls == 'CWayPointsPolygon')
    (x0, y0), (x1, y1) = wp.polygon[0], wp.polygon[1]
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    box = (int(mx) - 20, int(my) - 20, int(mx) + 20, int(my) + 20)
    img = np.asarray(render_level(lv, assets, box=box, step=1, polygons={'CWayPointsPolygon'}))
    checks += [bool((img.reshape(-1, 3) == POLYGON_COLORS['CWayPointsPolygon']).all(1).any())]
    img = np.asarray(render_level(lv, assets, box=box, step=1))
    checks += [not (img.reshape(-1, 3) == POLYGON_COLORS['CWayPointsPolygon']).all(1).any()]
    report('Animations as in the game (zaxtools.anim), renderer outlines', sum(map(bool, checks)), len(checks),
           bad[:3] or got)


def _check_children(ds, report, sample, quick):
    """LevelPart.children and anim.child_animation/child_facing over the levels: the counts of the original
    levels (1,354 children in 76 levels, 1,339 upper bodies), every upper body showing its parent's sequence,
    and the renderer drawing them (more pixels with children than without in 01 Main)."""
    from zaxtools import anim
    from zaxtools.render import Assets, render_level
    assets = Assets(ds)
    counts, bad = Counter(), []
    files = ds.list('Levels/', '.zax')
    for f in sample(files):
        n = 0
        for p in Level.from_bytes(ds.read(f)).parts:
            if p.position is None or not p.model:
                continue
            m = assets.model(p.model)
            a = anim.part_animation(p, m)
            for c in p.children:
                n += 1
                counts[c.cls] += 1
                cm = assets.model(c.model) if c.model else None
                ca = anim.child_animation(c, cm, a) if cm is not None else None
                if c.cls == 'CEntityAnimatedUpperBody':
                    want = cm.sequence(a.sequence or '') if cm is not None else None
                    if (ca is None) != (want is None) or (ca is not None and ca.sequence != want.name):
                        bad.append((f, p.name, c.model, a.sequence))
                    if ca is not None and anim.child_facing(c, p) != p.draw_angle:
                        bad.append((f, p.name, 'facing'))
        counts['levels'] += bool(n)
    full = len(sample(files)) == len(files)
    ok = not bad and (not full or (counts['levels'], sum(v for k, v in counts.items() if k != 'levels'),
                                   counts['CEntityAnimatedUpperBody']) == (76, 1354, 1339))
    report('Child objects: counts of the originals, upper bodies with the parent\'s sequence and turn',
           int(ok), 1, bad[:3] or ('' if full else 'sample'))
    lv = Level.from_bytes(ds.read('Levels/ACT 1/M1M2/01 Main.zax'))
    box = (2050, 1250, 2370, 1530)
    a = np.asarray(render_level(lv, assets, box, children=False))
    b = np.asarray(render_level(lv, assets, box, children=True))
    changed = int((a != b).any(axis=2).sum())
    report('Renderer draws the upper bodies (01 Main, three Rogcoils)', int(changed > 1000), 1, f'{changed} pixels')


def _check_child_edit(ds, report, sample, exe):
    """zaxtools.children over the levels: removing a child and adding it back at its place gives the file back
    byte for byte, so does save_state/restore_state after adding to a part without children; the first child turns
    "Child List=" into the block at its place (only those lines change); find_parent/root_of; with Zax.exe and the
    catalogue: a new Rogcoil upper body equals the one of its Default Entity, a model swap keeps the sequence when
    the model has it, a minimal upper body on a walker without one, an attached item; the level check's child
    checks fire on broken cases and give no finding in the originals."""
    import tempfile
    from zaxtools import children as chl, levelcheck
    from zaxtools.level import LevelPart
    files = ds.list('Levels/', '.zax')
    ok = total = 0
    bad = []
    for f in sample(files):
        raw = ds.read(f)
        lv = Level.from_bytes(raw)
        parts = lv.parts
        withc = [p for p in parts if p.children]
        empty = next((p for p in parts if isinstance(p.node.item('Child List'), tf.Entry)), None)
        if not withc and empty is None:
            continue
        total += 1
        good = True
        for p in withc[:20]:
            kids = p.children
            c = kids[-1]
            if chl.root_of(parts, c.node) is not p or chl.find_parent(parts, c.node) is not p:
                good = False
            i = chl.remove_child(p, c)
            chl.add_child(p, c.node, i)
        good &= lv.to_bytes() == raw
        if empty is not None:
            st = chl.save_state(empty)
            chl.add_child(empty, chl.minimal_child('CEntityBase', 'Items/Money/Crystal 01', 'Idle', 3, -4))
            old, cur = raw.decode('latin-1').split('\r\n'), lv.to_bytes().decode('latin-1').split('\r\n')
            i = next(k for k, (x, y) in enumerate(zip(old, cur)) if x != y)
            tail = len(old) - i - 1
            good &= old[i].strip() == 'Child List=' and cur[:i] == old[:i] and cur[len(cur) - tail:] == old[i + 1:] \
                and cur[i].strip() == 'Child List=CChildList' and LevelPart(empty.node).children[0].position == (3, -4)
            reread = Level.from_bytes(lv.to_bytes())
            good &= any(len(q.children) == 1 and q.children[0].model == 'Items/Money/Crystal 01' for q in reread.parts)
            chl.restore_state(st)
            good &= lv.to_bytes() == raw
        ok += good
        if not good:
            bad.append(f)
    report('Child objects: remove/add and the undo states give the file back, a first child rewrites only its line',
           ok, total, bad[:3] or '')
    if exe is None:
        print('[--] Child objects: new upper bodies and the level check need Zax.exe')
        return
    from zaxtools.catalog import Catalog
    sch = Schema.open(exe, ds, Path(tempfile.gettempdir()) / 'zax-selftest')
    cat = Catalog.open(ds, Path(tempfile.gettempdir()) / 'zax-selftest', exe=exe)
    rog = LevelPart(cat.make_node('Characters/Rogcoil/Rogcoil'))
    ub = rog.children[0]
    new = chl.upper_body_node(cat, rog, None, sch)
    checks = [tf.dumps(tf.Node(None, '<d>', [new])) == tf.dumps(tf.Node(None, '<d>', [ub.node])),
              chl.torso_candidates(cat, rog.model)[0] == 'Characters/Rogcoil/Rogcoil Torso']
    swap = chl.upper_body_node(cat, rog, 'Characters/Talon/Talon Torso', sch)
    checks.append(LevelPart(swap).model == 'Characters/Talon/Talon Torso' and LevelPart(swap).sequence == 'Idle')
    edits = chl.model_edits(cat, ub, 'Characters/Talon/Talon Torso')
    checks.append([v for _, v in edits] == ['Characters/Talon/Talon Torso'])
    targ = LevelPart(cat.make_node('Characters/Targ'))
    mini = LevelPart(chl.upper_body_node(cat, targ, 'Characters/Rogcoil/Rogcoil Torso', sch))
    ai = chl.same_as_parent_ai(mini, sch)
    checks.append(mini.cls == chl.UPPER_BODY and ai is not None and ai.value == 'CWalkingUpperBodyAI')
    staff = LevelPart(tf.Node('Level Part', 'CEntityAnimated', [tf.Entry('Model', 'Environments/Cave/Light Beams '
                                                                         'Pieces/Light Beam Start Staff')]))
    checks.append(chl.same_as_parent_ai(LevelPart(chl.upper_body_node(cat, staff, 'Characters/Rogcoil/Rogcoil Torso',
                                                                      sch)), sch).value == 'CSameAsParentAI')
    item = LevelPart(chl.attached_node(cat, 'Items/Money/Crystal 01', 14, -17))
    checks.append((item.cls, item.position, item.sequence) == ('CEntityBase', (14.0, -17.0), 'Idle'))
    report('Child objects: new upper bodies (Default Entity, swapped, minimal) and attached objects', sum(checks),
           len(checks))
    # the level check's child checks on a level with broken children
    ctx = levelcheck.Context(ds, sch, exe)
    lv = Level.from_bytes(ds.read('Levels/ACT 1/M1M2/01 Main.zax'))
    walker = next(p for p in lv.parts if p.cls == 'CEntityWalking' and p.children)
    base = next(p for p in lv.parts if p.cls == 'CEntityBase' and p.position is not None and not p.children)
    anim_p = next(p for p in lv.parts if p.cls == 'CEntityAnimated' and p.position is not None and not p.children)
    chl.add_child(base, chl.as_child(walker.children[0].node))     # upper body on a CEntityBase (+ its walking AI)
    chl.add_child(anim_p, chl.as_child(walker.children[0].node))               # CWalkingUpperBodyAI, root no walker
    odd = chl.minimal_child('CEntityBase', 'Items/Money/Crystal 01', 'Idle')
    odd.children.insert(1, tf.Node('Activity', 'Array', [tf.Entry('Item Count', '1'),
                                                         tf.Node('Activity', 'CSameAsParentAI', [])]))
    chl.add_child(walker, odd)                                                 # CSameAsParentAI on a CEntityBase
    chl.add_child(walker, chl.minimal_child('CEntityBase', '', ''))            # no model
    chl.add_child(walker, chl.minimal_child('CEntityBase', 'Items/Money/Crystal 01', 'No Such'))   # sequence
    hid = chl.as_child(walker.children[0].node)
    LevelPart(hid).model = 'Special Effects/staff particles 2'
    hid.set('Cur Sequence', 'Loop')
    chl.add_child(walker, hid)                                                 # upper body hidden (no Idle)
    found = Counter(x.check for x in levelcheck.check(lv, ctx, 'Test/Children.zax') if x.check.startswith('child-')
                    or (x.check == 'missing-sequence' and 'Child List' in x.field))
    want = {'child-upper-body-parent': 1, 'child-walking-ai-root': 2, 'child-same-as-parent-class': 1,
            'child-no-model': 1, 'missing-sequence': 1, 'child-hidden': 1}
    report('Level check: every child check fires on its broken child', int(dict(found) == want), 1, dict(found))
    # nested children (a child's own Child List; the originals have none): found, drawn from the child's position
    # and height, checked against the root; copy/paste of child objects (zaxtools.children "Copy, paste")
    raw = ds.read('Levels/ACT 1/M1M2/01 Main.zax')
    lv = Level.from_bytes(raw)
    walker = next(p for p in lv.parts if p.cls == 'CEntityWalking' and p.children and p.position is not None
                  and p.drawn_in_game and p.children[0].drawn_in_game)
    ub = walker.children[0]
    ub_pos = ub.position or (0.0, 0.0)
    ub_state = chl.save_state(ub)
    grand = chl.add_child(ub, chl.attached_node(cat, 'Items/Money/Crystal 01', 14, -17))
    checks = [chl.find_parent(lv.parts, grand.node).node is ub.node,
              chl.root_of(lv.parts, grand.node).node is walker.node,
              Level.from_bytes(lv.to_bytes()).parts[lv.part_index(walker)].children[0].children[0].model ==
              'Items/Money/Crystal 01']
    assets = render.Assets(ds)
    x, y = walker.position
    box = (int(x) - 80, int(y) - 120, int(x) + 80, int(y) + 60)
    nested = np.asarray(render.render_level(lv, assets, box, use_facing=True))
    chl.restore_state(ub_state)
    plain = np.asarray(render.render_level(lv, assets, box, use_facing=True))
    w_state = chl.save_state(walker)
    chl.add_child(walker, chl.attached_node(cat, 'Items/Money/Crystal 01', ub_pos[0] + 14, ub_pos[1] - 17))
    flat = np.asarray(render.render_level(lv, assets, box, use_facing=True))
    chl.restore_state(w_state)
    checks += [bool((nested != plain).any()), bool((nested == flat).all()), lv.to_bytes() == raw]
    base = next(p for p in lv.parts if p.cls == 'CEntityBase' and p.position is not None and not p.children)
    holder = chl.add_child(base, chl.attached_node(cat, 'Items/Money/Crystal 01'))
    chl.add_child(holder, chl.as_child(ub.node))          # a walking upper body two levels below a CEntityBase
    nf = Counter(x.check for x in levelcheck.check(lv, ctx, 'Test/Nested.zax') if x.check.startswith('child-'))
    checks.append(nf.get('child-walking-ai-root') == 1)
    report('Child objects: nested children found, drawn from their parent child, checked against the root',
           sum(checks), len(checks), dict(nf))
    lv = Level.from_bytes(raw)
    walker = next(p for p in lv.parts if p.cls == 'CEntityWalking' and p.children and p.position is not None)
    ub = walker.children[0]
    staff_p = LevelPart(tf.Node('Level Part', 'CEntityAnimated', [tf.Entry('Model', 'x')]))
    base = next(p for p in lv.parts if p.cls == 'CEntityBase' and p.position is not None and not p.children)
    crystal = chl.attached_node(cat, 'Items/Money/Crystal 01', 3, 4)
    checks = [chl.paste_problem([ub.node], base, schema=sch) == chl.PASTE_UPPER_BODY_PARENT,
              chl.paste_problem([ub.node], staff_p, schema=sch) == chl.PASTE_WALKING_AI_ROOT,
              chl.paste_problem([ub.node], targ, schema=sch) is None,
              chl.paste_problem([crystal], base, schema=sch) is None]
    st = chl.save_state(walker)
    new = chl.paste_children(walker, [ub.node])           # duplicate onto the same parent
    checks += [len(walker.children) == 2, tf.dumps(tf.Node(None, '<d>', [new[0]])) == tf.dumps(tf.Node(None, '<d>',
               [ub.node])), new[0] is not ub.node]
    chl.restore_state(st)
    st = chl.save_state(base)
    got = chl.paste_children(base, [crystal, crystal])    # onto another parent, twice
    checks += [[c.position for c in base.children] == [(3.0, 4.0), (3.0, 4.0)], got[0] is not got[1]]
    chl.restore_state(st)
    checks.append(lv.to_bytes() == raw)
    report('Child objects: pasted and duplicated as child objects, upper bodies refused where the game fails',
           sum(checks), len(checks))
    n = 0
    for f in sample(files):
        n += sum(x.check.startswith('child-') for x in levelcheck.check(Level.from_bytes(ds.read(f)), ctx, f[7:]))
    report('Level check: no child finding in the original levels', int(n == 0), 1, n)


def _check_preview(ds, report, sample, exe):
    """zaxtools.preview: every item loads and draws (8 bit: every eighth); the layers the game draws are
    Model.layers in its order; ground layers come first; the frame triggers of every sequence read (with
    Zax.exe) and their sounds and the model headers' sounds are found; a sequence file written back equals the
    shipped one; an 8-bit frame's image covers all five blocks."""
    import tempfile
    from zaxtools import preview
    pal = preview.palette(ds)
    items = preview.list_items(ds)
    kinds = Counter(i.kind for i in items)
    checks = [kinds['model'] == len(ds.list('Cache/Models/', '.mdl16')),
              kinds['font'] == len(ds.list('Cache/Fonts/', '.seq16'))]
    report('Viewer: the item list has every model and font', sum(checks), len(checks), dict(kinds))
    head = ModelHead(Schema.open(exe, ds, Path(tempfile.gettempdir()) / 'zax-selftest')) if exe else None
    bad, n_files, n_seq, n_ok, n_seqfile, seq_bad = [], 0, 0, 0, 0, []
    trig, missing = Counter(), set()
    for k, it in enumerate(sample(items)):
        for bpp in it.depths:
            if bpp == 8 and k % 8:
                continue
            n_files += 1
            data = ds.read(it.rel(bpp))
            try:
                v = preview.load(data, it.kind, it.name, pal)
            except (ValueError, IndexError, KeyError) as e:
                bad.append(f'{it.rel(bpp)}: {e}')
                continue
            m = v.model
            # one frame draws: the first non-empty frame of the base sequence, at its time (Auto-Animate)
            layers = preview.layer_list(m, None)
            b = preview.base_layer(layers)
            if b is not None and b.seq.stored:
                i = preview.still_index(b.seq)
                t = i / b.seq.fps if b.seq.fps > 0 else 0.0
                _, drawn = preview.compose(layers, 0.0, i, t, False, preview.content_box(layers, [0.0]))
                if not drawn and b.seq.frame(0, i) is not None:
                    bad.append(f'{it.rel(bpp)}: nothing drawn')
            if it.kind == 'sequence':
                n_seqfile += 1
                if preview.sequence_file(v, m.sequences[0]) != data:
                    seq_bad.append(it.rel(bpp))
            if it.kind != 'model' or bpp != 16:
                continue
            # the layers the game draws for every sequence as the active one; the frame triggers and sounds
            for s in m.sequences:
                n_seq += 1
                lay = preview.layer_list(m, s.name)
                game = [(x.order, x.seq) for x in sorted((x for x in lay if x.number < len(m.layers(s.name))),
                                                         key=lambda x: x.number)]
                n_ok += game == m.layers(s.name) and all(x.on != x.editor_only or x.order == 2 for x in lay)
                if head is not None:
                    tr = preview.triggers(data, s, head)
                    trig['read' if tr is not None else 'not read'] += 1
                    for x in tr or []:
                        for snd in x.sounds:
                            trig['sounds'] += 1
                            if preview.sound_file(ds, snd) is None:
                                missing.add(snd)
            if head is not None:
                for _, snd in preview.model_sounds(head.decode(data)):
                    trig['header sounds'] += 1
                    if preview.sound_file(ds, snd) is None:
                        missing.add(snd)
    report('Viewer: models, sequences, fonts and images load and draw', n_files - len(bad), n_files, bad[:3] or '')
    # drawing order: Light Beam 1's "Floor Light" (Always Visible, Render On Ground) before "Idle"; Crater's
    # shadow before its body
    order_bad = []
    for name, want in (('Environments/Cave/Light Beams Pieces/Light Beam 1', ['Floor Light', 'Idle']),
                       ('Characters/Crater/Crater', ['Idle Shadow', 'Idle'])):
        m = mdl.load(ds.read(f'Cache/Models/{name}.mdl16'), name)
        layers = preview.layer_list(m, 'Idle')
        box = preview.content_box(layers, [0.0])
        d = preview.draw(preview.background('black', box), box, layers, 0.0, 0, 0.0, False)
        n_seq += 1
        n_ok += [x.layer.seq.name for x in d] == want
        order_bad += [] if [x.layer.seq.name for x in d] == want else [name]
    report('Viewer: the layers the game draws (Model.layers, order), handles switched off, drawing order', n_ok,
           n_seq, order_bad[:2] or '')
    if head is not None:
        report('Viewer: frame triggers of every sequence read, every sound found in Sounds/',
               trig['read'] + (not missing), trig['read'] + trig['not read'] + 1, sorted(missing)[:3] or dict(trig))
    report('Viewer: an image sequence exported through the encoder equals the file', n_seqfile - len(seq_bad),
           n_seqfile, seq_bad[:3] or '')
    ok = total = 0
    for it in [i for i in items if i.kind == 'frame' and 8 in i.depths][::7]:
        d = ds.read(it.rel(8))
        f = preview.load(d, 'frame', it.name, pal).model.sequences[0].frames[0]
        hd, blocks, _ = frm.blocks(d, 0)
        if not hd.rle:
            continue                                        # raw: no blocks
        total += 1
        cover = np.zeros((hd.height, hd.width), bool)
        for blk in blocks:
            if isinstance(blk, tuple):
                cover |= blk[1]
        ok += bool(((f.rgba[..., 3] > 0) == cover).all())
    report('Viewer: an 8-bit frame shows the pixels of all five blocks', ok, total)


def _check_rds(ds, zaxs, report, what):
    """zaxtools/rds.py: every .RDS byte for byte, the game's items, every dialogue action's label found,
    edits that keep the rest of the file, voices and portraits found for (almost) every line."""
    files = [f for f in ds.list('Levels/', '') if f.lower().endswith('.rds')]
    ok, scripts = 0, {}
    for f in files:
        b = ds.read(f)
        s = rds.loads(b)
        scripts[f[len('Levels/'):-4].lower()] = s
        ok += s.dumps() == b and [n for n, _ in s.game_items()] == ['!None'] + s.labels()
    report(f'.RDS ({what}) written back byte for byte', ok, len(files))
    total = found = 0
    for f in zaxs:
        for p in Level.from_bytes(ds.read(f)).parts:
            for script, line in links.dialog_refs(p):
                total += 1
                sc = scripts.get(script.replace('\\', '/').lower())
                found += sc is not None and sc.find(line.strip()) is not None
    report(f'.RDS ({what}): every dialogue action finds its label (rds.Script.find)', found, total)
    ok = total = 0
    for f in files:
        b = ds.read(f)
        s = rds.loads(b)
        before = s.game_items()
        for it in list(s.items):
            s.set_text(it.name, it.text())          # the same text: the game sees the same items
        s.add('Selftest label', 'Zax: one\ntwo')
        first = s.items[0].name
        s.rename(first, first + ' X')
        again = rds.loads(s.dumps())
        items = again.game_items()
        total += 1
        ok += (items[2:-1] == before[2:] and items[1] == (first + ' X', before[1][1])
               and items[-1] == ('Selftest label', 'Zax: one\ntwo')
               and rds.loads(s.dumps()).dumps() == s.dumps())
    report(f'.RDS ({what}): edit, add, rename keep the other items', ok, total)
    res = rds.Resources(ds)
    lines = [it for f in files if 'mission' in f.lower() for it in rds.loads(ds.read(f)).items]
    voices = sum(res.voice(it.name) is not None for it in lines)
    portraits = sum(res.portrait(rds.split_line(it.text())[0]) is not None for it in lines)
    speaker_ok = rds.split_line('Zelon: hi  there') == ('Zelon', 'hi  there') and \
        rds.split_line('A very long speaker name: x') == ('', 'A very long speaker name: x') and \
        rds.shown_speaker('  ') == '???'
    # the shipped mission scripts: all but a handful of lines have a voice and a portrait (counts as found)
    report(f'.RDS ({what}): voices/portraits of the mission lines, speaker split',
           int(voices >= len(lines) - 5 and portraits >= len(lines) - 4 and speaker_ok), 1,
           {'lines': len(lines), 'voice': voices, 'portrait': portraits})


def _check_overlays(ds, report, mh):
    from zaxtools import overlays as ov

    def bounds(model):
        if mh is None:
            return None
        try:
            return mh.decode(ds.read(f'Cache/Models/{model}.mdl16')).values.get('Bounds Poly') or []
        except (DecodeError, KeyError, OSError):
            return None

    def near(p, q, eps=1e-3):
        return abs(p[0] - q[0]) < eps and abs(p[1] - q[1]) < eps

    lv = Level.from_bytes(ds.read('Levels/ACT 1/M1M2/01 Main.zax'))
    geo = ov.Geometry(lv, bounds)
    by = {}
    for p in lv.parts:
        for s in ov.part_shapes(geo, p):
            by.setdefault((s.source.split(':')[0], p.name, p.position), []).append(s)
    got, checks = {}, []
    # oval trigger "X Radius" 45, "YX Ratio" 0.712766 at (1071, 2092): 45 // 4 = 11 segments
    o = by.get(('CTouchingOvalTriggerAI', '', (1071.0, 2092.0)), [None])[0]
    checks.append(o is not None and len(o.points) == 12 and near(o.points[0], (1116, 2092))
                  and near(o.points[3], (1064.596, 2123.748)) and near(o.points[-1], o.points[0]))
    # spawn point "Den1 Spawn" (1120, 2162), Facing Angle 50: shaft tip and the first barb's end
    a = by.get(('CSpawnPointAI', 'Den1 Spawn', (1120.0, 2162.0)), [])
    checks.append(len(a) == 3 and near(a[0].points[1], (1139.284, 2178.380))
                  and near(a[1].points[1], (1129.625, 2176.535)))
    # ambient sound (3565, 1544), radii 400 / 1000 / 2000, Rolloff 5: circles of 400 and 1400 (25
    # segments), the scale at y 144, the fall-off 1400 / (1400 + 5 k) down to k = 1999, 12 % at the end (x + 3400)
    s = by.get(('CAmbientSoundAI', 'Generator under the ground', (3565.0, 1544.0)), [])
    line = next((x for x in s if len(x.points) > 30), None)
    text = next((x for x in s if x.text), None)
    checks.append(len(s) == 4 and near(s[0].points[0], (3965, 1544)) and near(s[1].points[0], (4965, 1544))
                  and line is not None and len(line.points) == 2004 and near(line.points[1], (4965, 144))
                  and near(line.points[-3], (6964, 1371.994)) and near(line.points[-1], (3565, 1544))
                  and text is not None and text.text == '12' and near(text.points[0], (6965, 1554)))
    # patrol area of the Targ (home 223, 1130), Radius 100: 25 segments from (323, 1130)
    pa = [x for x in by.get(('CPatrolAreaAI', '', (223.0, 1130.0)), [])]
    checks.append(len(pa) == 1 and len(pa[0].points) == 26 and near(pa[0].points[0], (323, 1130)))
    # follow path "bird path" (Go To End: one point less) and the square at Target Point 0, on the path part
    fp = by.get(('CFollowPathAI', 'bird 1', (612.0, 679.0)), [])
    path = lv.find('bird path')
    checks.append(len(fp) == 2 and fp[0].points == [(630, 636), (2936, 2611), (2821, 2600)]
                  and fp[1].points == [(629, 635), (631, 635), (631, 637), (629, 637), (629, 635)]
                  and fp[0].anchor.node is path.node)
    # polygon trigger "talking poly": its own polygon, closed
    pt = by.get(('CTouchingPolygonTriggerAI', 'talking poly', None), [])
    checks.append(len(pt) == 1 and pt[0].points == lv.find('talking poly').polygon)
    got['shapes'] = sum(len(v) for v in by.values())
    if mh is not None:
        # objects: polygon = the model's Bounds Poly at the position, centre = position + its mean
        sw = lv.find('stone switch guarding secret area')
        b = bounds(sw.model)
        ct = by.get(('CollideTriggerAI', sw.name, sw.position), [])
        checks.append(bool(b) and len(ct) == 1 and near(ct[0].points[0], (b[0][0] + 2189.75, b[0][1] + 2512.75)))
        targ = next(p for p in lv.parts if p.model == 'Characters/Targ' and p.position == (223.0, 1130.0))
        tb = bounds(targ.model)
        c = (223 + sum(x for x, _ in tb[:-1]) / (len(tb) - 1), 1130 + sum(y for _, y in tb[:-1]) / (len(tb) - 1))
        sk = by.get(('CSkeletonAI', '', (223.0, 1130.0)), [])
        checks.append(len(sk) == 4 and near(sk[0].points[0], c) and sk[3].text == 'Patrol')
    got['failed'] = [i for i, c in enumerate(checks) if not c] or None
    report('AI overlays (shapes as the debug drawing of Zax.exe)', sum(checks), len(checks), got)


if __name__ == '__main__':
    main()
