"""Which assets of the game data the game really uses: placed in a level, used in other ways (particles, shots,
child objects, spawned effects, item definitions, the exe's own names), possibly used, or never used.

The model browser's old mark "occurs in no level" (``Catalog`` ``uses == 0``, 235 models) was misleading: 101 of
those models are used by the game through other paths. This module follows every path the game data and Zax.exe
give a name through and closes over them (ported from the analysis of 2026-10-29, which gave: 2,987 assets, 358
never used, 31 possibly used, 10 names missing).

Assets: every entry of the game data, grouped the way the game's resource lists see them: an ``.mdl16``/``.mdl``,
``.seq16``/``.seq`` or ``.frm16``/``.frm`` pair is one asset; a ground texture is ``Cache/Textures/<n>`` plus
``Textures/<n>.TXT``; a level is ``<n>.zax`` + ``<n>.way`` + its mini map ``Cache/Levels/<Partial File Name>``.
Each asset has its list (models, sequences, fonts, cursors, inventory icons, sounds, voices, music, dialogue
scripts, the definition lists ...) and its name in that list (path below the list folder, without extension,
a leading "-" cut).

References: every key=value of every level, of ``Rules.txt`` and of every definition text (item definitions and
types, death behaviours, categories, damage/surface types, water warp effects, canned objects, difficulties,
quips, frame overlay options, game types, ``Textures/*.TXT``); every model header decoded with the exe's field
schema (``zaxtools.modelhead``) plus the length-prefixed strings of the model's sequence part (frame triggers:
sounds, particles); the speakers of every ``.RDS`` line -> "<speaker> Portrait"; a quip category -> all sounds of
its folder ``Resources/Quips/<category>/`` (CQuipCategory::ReadSounds); all printable strings of Zax.exe. Object
names, texts and link fields (``Name``, ``Description``, ``Relay Name`` ...) are no references.

Resolution as ZNamedList::Find 0x591bd0: the exact name (case-insensitive), else the first entry of the list whose
file name matches (FindFileName 0x591ac0); sounds keep their extension and try .wav/.ogg (CSoundList::Find
0x57e690); a dialogue ``Line=`` is looked up as "<label>.wav" in the voice list. Every key is typed by the lists
its values hit exactly (sequence-name keys and free tags are no references). Values are split at commas only
when the whole value does not resolve.

Roots (used): Zax.exe's strings, ``Rules.txt``, the levels reached from ``First Map Name`` through ``New Map
Name``/``Other Map Name``, the ``Levels/Multiplayer`` maps, the level the exe names, and the lists the game uses
as a whole (categories, damage types, game types, difficulties). Weak roots (possibly used): fonts and surface
types (loaded whole at start), item definitions/types (the materials generator lists the whole catalogue),
levels no transition reaches. The closure follows references transitively; an asset reached only from possibly
used assets is "possibly", one only referenced by unused assets is "unused".

Evidence: "confirmed" = every reference path above was searched over all data and the exe; "assumption" = a name
built at run time or a whole-list iteration could still reach it. Limits: names assembled at run time beyond the
format strings reviewed by hand ("%s Portrait", "%s.wav", "Interface/%s.bmp", "Movies/%s.bik", the quip folders),
objects a level only creates through scripts that never run, and the multiplayer map selection are not simulated.
The language pack is not included (it only replaces files of the same name).

No Qt. The result is cached as JSON like the model catalogue (``Usage.open``). Needs Zax.exe (its strings and the
field schema for the model headers); without the exe only the level use of the catalogue is known.
"""
from __future__ import annotations

import json
import re
import struct
from collections import Counter, defaultdict, deque
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import mdl, rds, textformat as tf
from .datasource import DataSource
from .links import REF_KEYS

VERSION = 1                     # increase when the analysis changes (invalidates the cache)

# status of an asset
USED, POSSIBLY, UNUSED = 'used', 'possibly', 'unused'

# --- Inventory ------------------------------------------------------------------------------------------------
CACHE_LISTS = [   # (prefix, extensions, list, kind)
    ('Cache/Models/', {'mdl16', 'mdl'}, 'models', 'model'),
    ('Cache/Sequences/', {'seq16', 'seq'}, 'sequences', 'sequence'),
    ('Cache/Animated Textures/', {'seq16', 'seq'}, 'anim_tex', 'texture'),
    ('Cache/Fonts/', {'seq16', 'seq'}, 'fonts', 'sequence'),
    ('Cache/Interface/Cursors/', {'seq16', 'seq'}, 'cursors', 'sequence'),
    ('Cache/Interface/Textures/', {'frm16', 'frm'}, 'ui_tex', 'texture'),
    ('Cache/Interface/', {'frm16', 'frm'}, 'interface', 'frame'),
    ('Cache/Resources/', {'seq16', 'seq'}, 'res_seq', 'sequence'),
    ('Cache/Resources/', {'frm16', 'frm'}, 'res_frm', 'frame'),
    ('Cache/Inventory/Icon Frames/', {'frm16', 'frm'}, 'inv_icons', 'frame'),
    ('Cache/Inventory/Frames/', {'frm16', 'frm'}, 'inv_frames', 'frame'),
    ('Cache/Inventory/Detail Sequences/', {'seq16', 'seq'}, 'inv_detail', 'sequence'),
    ('Cache/Inventory/HUD Sequences/', {'seq16', 'seq'}, 'inv_hud', 'sequence'),
    ('Cache/Inventory/', {'frm16', 'frm'}, 'inventory_misc', 'frame'),
    ('Cache/Textures/', {'frm16', 'frm'}, 'ground_tex', 'texture'),
]
TEXT_LISTS = [   # (folder, extension, list)
    ('Inventory/Item Definitions/', 'txt', 'item_defs'),
    ('Inventory/Item Types/', 'txt', 'item_types'),
    ('Death Behaviors/', 'txt', 'death'),
    ('Categories/', 'txt', 'categories'),
    ('Damage Types/', 'txt', 'damage'),
    ('Surface Types/', 'sty', 'surface'),
    ('Water Warp Effects/', 'txt', 'water_warp'),
    ('Resources/Frame Overlay Options/', 'foo', 'foo'),
    ('Resources/Game Types/', 'zgt', 'game_types'),
    ('Resources/', 'can', 'canned'),
    ('Resources/', 'dificulty', 'difficulty'),
    ('Resources/', 'quips', 'quips'),
]
DEFINITION_LISTS = {'item_defs', 'item_types', 'death', 'categories', 'damage', 'surface', 'water_warp', 'foo',
                    'game_types', 'canned', 'difficulty', 'quips'}
KIND_ORDER = ['model', 'sequence', 'frame', 'texture', 'sound', 'music', 'level', 'other']

# --- Reference extraction -------------------------------------------------------------------------------------
SKIP_KEYS = {'Name', 'New Name', 'Printable Name', 'Description', 'Map Description', 'Text String', 'Legacy Name',
             'Text', 'Item Count', 'Array Count', 'Polygon', 'Text Overlays'} | (set(REF_KEYS) - {'Position'})
SEQ_TAG = struct.pack('<ff', 27.0, 758.0)
_STR_RE = re.compile(rb'([\x02-\xff])\x00\x00\x00')
_EXE_STR_RE = re.compile(rb'[\x20-\x7e]{2,}')
RENDER_MODES = {'transparent mask', 'blend black bias', 'blend amplify light'}

# --- Resolution -----------------------------------------------------------------------------------------------
KNOWN_EXT = {'wav', 'ogg', 'tga', 'zax', 'way', 'mdl16', 'mdl', 'frm16', 'frm', 'seq16', 'seq', 'txt', 'rds', 'bmp',
             'bik', 'pal', 'can', 'quips', 'zgt', 'dificulty', 'sty', 'foo', 'property'}
SOUND_LISTS = {'sounds', 'voices'}
NONE_VALUES = {'!none', 'none', '!none.wav', '!unknown model', ''}
SEQUENCE_KEYS = {'Cur Sequence', 'Default Sequence', 'Sequence', 'Turn Sequence Name', 'End Sequence Name', 'Animation',
                 'Done Sequence', 'Blocking Priority', 'Start Sequence', 'Sequence Name', 'Idle Sequence'}
# keys whose list is fixed by the code that reads them (the others are typed from the data)
MANUAL = {'Portrait': {'inv_frames'}, 'Line': {'voices'}, 'ReadSounds': {'quip_snd'},
          'Icon Image': {'inv_icons'}, 'Generator Icon Image': {'inv_icons'}, 'Detail Image': {'inv_detail'},
          'HUD Image': {'inv_hud'}, 'Inventory Type': {'item_types'}}
for _k in ('Definition Index', 'Inventory Item Definition', 'Ingredient 1 Type', 'Ingredient 2 Type', 'Ingredient 3 Type',
           'Required Item', 'Normal Item', 'Alternate Item Def', 'Ammunition', 'Discovered Item', 'Weapon/Ammunition'):
    MANUAL[_k] = {'item_defs'}
UNTYPED = {'string'}            # raw strings (exe, model sequence parts): may name anything

# exe strings that only match an asset by a coincidental word (checked by hand: the xrefs of the string)
EXE_COINCIDENCE = {
    'cursors:delete': 'the exe string "Delete" is a message/button text (xrefs 0x41c238 CActionQueueItem::OnMessage, '
                      '0x422688, 0x429fb2), not one of the 19 cursor names App/World::LoadGameData loads from '
                      'Interface/Cursors',
    'voices:act 2/m12/vos/new line.ogg': 'the exe string "New Line" is the default name of a CDialogLine '
                                         '(CDialogLine::RegisterFields 0x41df10), not a voice lookup',
    'inv_detail:characters/zax': 'the exe strings "Zax"/"zax" are the game name (World::Ctor via CZaxApp_Ctor 0x59a670, '
                                 'GameSpy browser 0x518e00, server dialog 0x4d3080), not a detail-sequence lookup',
}
# assets the exe shows only in demo mode (byte 0x62485c, set when the model "Om" is missing)
DEMO_ONLY = {'res_frm:demo screens/sell screen 01', 'res_frm:demo screens/sell screen 02',
             'res_frm:demo screens/sell screen 03', 'res_frm:demo screens/demo complete',
             'foo:demo screens/sell screen 01', 'foo:demo screens/sell screen 02', 'foo:demo screens/sell screen 03',
             'foo:demo screens/demo complete'}
DEMO_REASON = ('shown only in demo mode: MainMenu_Notify 0x5bf4a0 shows the sell screens (list 0x6273fc) on Exit and '
               'App_Frame 0x59d140 "Demo Complete" at the end only when the demo byte 0x62485c is set, which '
               'App_LoadGameData 0x5a01c0 sets only when the model "Om" is missing; Cache/Models/Characters/Om.mdl16 is '
               'in the game data')
EDITOR_CURSOR_NOTE = ('a tool cursor of the internal level editor; the retail exe loads only its 19 named cursors from '
                      'Interface/Cursors (World::LoadGameData 0x4f13a0, cursor table 0x62e5e4) and the editor is not in '
                      'the retail build')
# names the game asks for that no file answers (beyond the transitions to missing levels, which are computed);
# each entry only counts when its file is really missing
KNOWN_MISSING = [
    ('Cache/Inventory/Frames/Dialog Display/Portraits/Periscope Portrait', 'frame',
     ['Levels/ACT 3/M18/Mission18.RDS (speaker "Periscope")'],
     'the dialogue window falls back to "!Unknown Portrait" (DialogDisplay_Portrait 0x47ccc0)', 'confirmed',
     ('Cache/Inventory/Frames/Dialog Display/Portraits/Periscope Portrait.frm16',)),
    ('Cache/Inventory/Frames/Dialog Display/Portraits/Talon Portrait', 'frame',
     ['Levels/ACT 3/M18/Mission18.RDS (speaker "Talon")'], 'falls back to "!Unknown Portrait"', 'confirmed',
     ('Cache/Inventory/Frames/Dialog Display/Portraits/Talon Portrait.frm16',)),
    ('Cache/Interface/Mute.frm16', 'frame',
     ['Zax.exe: the sound dialog\'s mute check boxes load the image "Interface"/"Mute" (ui_settings.cpp new_check -> '
      'Button::LoadImage 0x40ff50)'],
     'only the 8-bit Cache/Interface/Mute.frm exists; the Chinese language pack 0Chinese.RED adds Mute.frm16. What the '
     '16-bit game shows without it was not tested', 'confirmed (data); effect: assumption', ('Cache/Interface/Mute.frm16',)),
    ('Interface/Splash Screen 2.bmp', 'other', ['Zax.exe: App_LoadGameData 0x5a01c0 (string 0x624e1c)'],
     'the first splash screen of the loading sequence; Splash Screen 3.bmp exists (docs/FORMATS.md 5.2)', 'confirmed',
     ('Interface/Splash Screen 2.bmp',)),
    ('Sounds/Startup.wav', 'sound', ['Zax.exe: string 0x618194, used at 0x4f0793 (World::Ctor 0x4f0780)'],
     'no file of that name below Sounds', 'confirmed (string); how it is used: assumption',
     ('Sounds/Startup.wav', 'Sounds/Startup.ogg')),
    ('Palettes/InvColorTable.pal', 'other', ['Zax.exe: string 0x60c58c at 0x433168 (InitBlendTables 0x433000)'],
     'only InvColorTable15/16.pal exist; the exe creates missing blend tables at start (docs/FORMATS.md 5)', 'assumption',
     ('Palettes/InvColorTable.pal',)),
    ('Local.txt', 'other', ['Zax.exe: ZLocalTable::Load 0x500ac0 at start'],
     'not in the game data by design: it comes with the language packs (GERMAN.RED etc.)', 'confirmed', ('Local.txt',)),
]


# --- Helpers ----------------------------------------------------------------------------------------------------
def _noext(p: str) -> str:
    return p.rsplit('.', 1)[0] if '.' in p.rsplit('/', 1)[-1] else p


def _ext(p: str) -> str:
    return p.rsplit('.', 1)[-1].lower() if '.' in p.rsplit('/', 1)[-1] else ''


def _dir(p: str) -> str:
    return p.rsplit('/', 1)[0] if '/' in p else ''


def _base(p: str) -> str:
    return p.rsplit('/', 1)[-1]


def _cut_dash(rel: str) -> str:
    d, _, b = rel.rpartition('/')
    if b.startswith('-'):
        b = b[1:]
    return f'{d}/{b}' if d else b


def _strip_ext(p: str) -> str:
    b = _base(p)
    if '.' in b and b.rsplit('.', 1)[1].lower() in KNOWN_EXT:
        return p[:len(p) - len(b)] + b.rsplit('.', 1)[0]
    return p


def exe_strings(exe_bytes: bytes) -> list[str]:
    """Every printable ASCII run of at least 2 characters in the exe (sorted, without duplicates)."""
    return sorted({m.group().decode('latin-1') for m in _EXE_STR_RE.finditer(exe_bytes)})


def _walk(node: tf.Node, ctx=()):
    for c in node.children:
        if isinstance(c, tf.Node):
            yield ctx, c.key, c.value, True
            yield from _walk(c, ctx + (c.value,))
        elif isinstance(c, tf.Entry):
            yield ctx, c.key, c.value, False


def text_refs(text: str) -> list[tuple[str, str, str]]:
    """(class of the enclosing object, key, value) of every value of a text file that may name an asset."""
    try:
        doc = tf.loads(text)
    except Exception:          # noqa: BLE001 - an unreadable text names nothing
        return []
    out = []
    for ctx, k, v, isnode in _walk(doc):
        if isnode or k in SKIP_KEYS or not v.strip():
            continue
        out.append((ctx[-1] if ctx else '', k, v))
    return out


def raw_strings(d: bytes, start: int = 0) -> list[str]:
    """The length-prefixed strings of a binary file from ``start`` (u32 length 2..255 + printable text)."""
    out = []
    for m in _STR_RE.finditer(d, start):
        p = m.start()
        n = d[p]
        s = d[p + 4:p + 4 + n]
        if len(s) == n and all(32 <= c < 127 or c >= 160 for c in s) and re.search(rb'[A-Za-z]{2}', s):
            out.append(s.decode('latin-1'))
    return out


# --- Result -----------------------------------------------------------------------------------------------------
@dataclass
class Asset:
    id: str                         # "<list>:<name in lower case>"
    kind: str                       # model, sequence, frame, texture, sound, music, level, other
    list: str
    name: str                       # name in its list (original spelling)
    files: list[str] = field(default_factory=list)
    bytes: int = 0
    status: str = USED              # used | possibly | unused
    reason: str = ''                # why it is possibly used / unused ('' for used)
    referenced_by: list[str] = field(default_factory=list)   # the references that make it used (or the evidence)
    evidence: str = ''              # confirmed | assumption ('' for used)

    @property
    def path(self) -> str:
        """The main file (the .zax, .mdl16, .seq16, .frm16, .wav or .ogg of the asset)."""
        for e in ('.zax', '.mdl16', '.seq16', '.frm16', '.wav', '.ogg'):
            for f in self.files:
                if f.lower().endswith(e):
                    return f
        return self.files[0]


@dataclass
class Missing:
    name: str
    kind: str
    referenced_by: list[str]
    note: str
    evidence: str


class Usage:
    """The analysis result: ``assets`` (id -> Asset), ``missing`` (names the game asks for without a file),
    ``placed`` (model ids placed in a level as ``Model``)."""

    def __init__(self, assets: dict[str, Asset], missing: list[Missing], placed: set[str], signature: str = ''):
        self.assets, self.missing, self.placed, self.signature = assets, missing, placed, signature
        self._models = {a.name.lower(): a for a in assets.values() if a.list == 'models'}

    # --- queries ---------------------------------------------------------------------------------------------
    def counts(self) -> dict[str, int]:
        """Number of assets per status, plus 'missing'."""
        c = Counter(a.status for a in self.assets.values())
        return {USED: c[USED], POSSIBLY: c[POSSIBLY], UNUSED: c[UNUSED], 'missing': len(self.missing),
                'total': len(self.assets)}

    def model(self, path: str) -> Asset | None:
        """The asset of a model path as in the levels (``Characters/Crater/Crater``)."""
        return self._models.get(path.lower())

    def model_use(self, path: str) -> str | None:
        """'placed' (placed in a level as Model), 'used' (not placed, but used by the game in another way),
        'possibly', 'unused'; None for a model the analysis does not know (e.g. an own model)."""
        a = self.model(path)
        if a is None:
            return None
        if a.id in self.placed:
            return 'placed'
        return a.status

    def models_vs_level_use(self) -> dict[str, int]:
        models = [a for a in self.assets.values() if a.list == 'models']
        no_level = [a for a in models if a.id not in self.placed]
        return {'models': len(models), 'placed': len(self.placed), 'not_placed': len(no_level),
                'not_placed_used': sum(a.status == USED for a in no_level),
                'not_placed_possibly': sum(a.status == POSSIBLY for a in no_level),
                'not_placed_unused': sum(a.status == UNUSED for a in no_level)}

    # --- cache -----------------------------------------------------------------------------------------------
    def save(self, file: Path) -> None:
        file.parent.mkdir(parents=True, exist_ok=True)
        data = {'version': VERSION, 'signature': self.signature,
                'assets': [asdict(a) for a in self.assets.values()],
                'missing': [asdict(m) for m in self.missing], 'placed': sorted(self.placed)}
        tmp = file.with_suffix('.tmp')
        tmp.write_text(json.dumps(data), encoding='utf-8')
        tmp.replace(file)

    @classmethod
    def load(cls, file: Path, sig: str | None = None) -> 'Usage | None':
        try:
            data = json.loads(Path(file).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None
        if data.get('version') != VERSION or (sig is not None and data.get('signature') != sig):
            return None
        return cls({a['id']: Asset(**a) for a in data['assets']}, [Missing(**m) for m in data['missing']],
                   set(data['placed']), data['signature'])

    @classmethod
    def open(cls, ds: DataSource, exe: str | Path, cache_dir: Path, schema=None) -> 'Usage':
        """From the cache or analysed anew (about 20 s) and saved. The cache key is the catalogue's signature
        (levels, models, the data file and the exe)."""
        from .catalog import signature
        sig = signature(ds, exe)
        file = Path(cache_dir) / f'usage-{sig[:16]}.json'
        u = cls.load(file, sig)
        if u is None:
            u = analyze(ds, exe, schema=schema, cache_dir=cache_dir)
            u.signature = sig
            u.save(file)
            for old in Path(cache_dir).glob('usage-*.json'):
                if old != file:
                    old.unlink(missing_ok=True)
        return u


# --- The analysis -----------------------------------------------------------------------------------------------
def analyze(ds: DataSource, exe: str | Path, schema=None, cache_dir: Path | None = None) -> Usage:
    """Analyse the game data ``ds`` (its language pack is left out) with Zax.exe ``exe``. ``schema``: the exe's
    field schema (built from ``exe`` when None, cached in ``cache_dir``)."""
    if ds.language_pack is not None:
        ds = DataSource(ds.root)
    from .exeschema import Schema
    from .modelhead import ModelHead
    if schema is None:
        schema = Schema.open(exe, ds, cache_dir) if cache_dir else Schema.build(exe, ds)
    a = _Analysis(ds, ModelHead(schema), Path(exe).read_bytes())
    return a.run()


class _Analysis:
    def __init__(self, ds: DataSource, head, exe_bytes: bytes):
        self.ds, self.head, self.exe_bytes = ds, head, exe_bytes
        self.assets: dict[str, dict] = {}
        self.refs: dict[str, list] = defaultdict(list)          # source id -> [(cls, key, value)]
        self.rds_labels: dict[str, list[str]] = {}

    # --- inventory ----------------------------------------------------------------------------------------------
    def _add(self, aid, kind, lst, rel, f, size):
        a = self.assets.setdefault(aid, dict(id=aid, kind=kind, list=lst, rel=rel, files=[], bytes=0))
        a['files'].append(f)
        a['bytes'] += size

    def inventory(self) -> None:
        ds = self.ds
        files = ds.list()
        size = {f: ds.size(f) for f in files}
        for f in files:
            e = _ext(f)
            done = False
            for pre, exts, lst, kind in CACHE_LISTS:
                if f.startswith(pre) and e in exts:
                    if pre in ('Cache/Interface/', 'Cache/Inventory/') and '/' in f[len(pre):]:
                        continue
                    rel = _cut_dash(_noext(f[len(pre):]))
                    self._add(f'{lst}:{rel.lower()}', kind, lst, rel, f, size[f])
                    done = True
                    break
            if done or f.startswith('Cache/Levels/'):
                continue                           # mini maps: attached to their levels below
            if f.startswith('Textures/') and e == 'txt':
                rel = _noext(f[len('Textures/'):])
                self._add(f'ground_tex:{rel.lower()}', 'texture', 'ground_tex', rel, f, size[f])
                continue
            for pre, ex, lst in TEXT_LISTS:
                if f.startswith(pre) and e == ex:
                    rel = _cut_dash(_noext(f[len(pre):]))
                    self._add(f'{lst}:{rel.lower()}', 'other', lst, rel, f, size[f])
                    done = True
                    break
            if done:
                continue
            if f.startswith('Sounds/') and e in ('wav', 'ogg'):
                rel = f[len('Sounds/'):]
                self._add(f'sounds:{rel.lower()}', 'sound', 'sounds', rel, f, size[f])
            elif f.startswith('Resources/Quips/') and e in ('wav', 'ogg'):
                rel = f[len('Resources/'):]
                self._add(f'quip_snd:{rel.lower()}', 'sound', 'quip_snd', rel, f, size[f])
            elif f.startswith('Levels/') and e in ('wav', 'ogg'):
                rel = f[len('Levels/'):]
                self._add(f'voices:{rel.lower()}', 'sound', 'voices', rel, f, size[f])
            elif f.startswith('Music/') and e == 'ogg':
                rel = _noext(f[len('Music/'):])
                self._add(f'music:{rel.lower()}', 'music', 'music', rel, f, size[f])
            elif f.startswith('Levels/') and e in ('zax', 'way'):
                rel = _noext(f[len('Levels/'):])
                self._add(f'levels:{rel.lower()}', 'level', 'levels', rel, f, size[f])
            elif f.startswith('Levels/') and e == 'rds':
                rel = _noext(f[len('Levels/'):])
                self._add(f'rds:{rel.lower()}', 'other', 'rds', rel, f, size[f])
            else:
                self._add(f'file:{f.lower()}', 'other', 'file', f, f, size[f])
        # mini maps: Cache/Levels/<Partial File Name> belongs to the level with that Partial File Name
        self.level_text = {}
        pfn = {}
        for aid, a in self.assets.items():
            if a['list'] == 'levels':
                z = [x for x in a['files'] if x.lower().endswith('.zax')]
                if z:
                    self.level_text[aid] = ds.read(z[0]).decode('latin-1')
                    m = re.search(r'\n\s*Partial File Name=([^\r\n]*)', self.level_text[aid])
                    pfn[aid] = m.group(1).strip() if m else ''
        by_pfn = {v.lower(): k for k, v in pfn.items()}
        for f in files:
            if f.startswith('Cache/Levels/'):
                rel = _noext(f[len('Cache/Levels/'):]).lower()
                target = by_pfn.get(rel) or (f'levels:{rel}' if f'levels:{rel}' in self.assets else None)
                if target:
                    self.assets[target]['files'].append(f)
                    self.assets[target]['bytes'] += size[f]
                else:
                    self._add(f'minimap:{rel}', 'frame', 'minimap', _noext(f[len('Cache/Levels/'):]), f, size[f])

    # --- references ---------------------------------------------------------------------------------------------
    def references(self) -> None:
        ds, refs = self.ds, self.refs
        for aid, t in self.level_text.items():
            refs[aid] += text_refs(t)
        for aid, a in self.assets.items():
            if a['list'] in DEFINITION_LISTS or a['list'] == 'ground_tex':
                for f in a['files']:
                    if f.lower().endswith(('.txt', '.sty', '.foo', '.zgt', '.can', '.dificulty', '.quips')):
                        refs[aid] += text_refs(ds.read(f).decode('latin-1'))
        if ds.exists('Rules.txt'):
            refs['file:rules.txt'] += text_refs(ds.read('Rules.txt').decode('latin-1'))
        for aid, a in self.assets.items():          # dialogue: speakers -> portraits
            if a['list'] == 'rds':
                s = rds.loads(ds.read(a['files'][0]))
                self.rds_labels[aid] = [n for n, _ in s.game_items()]
                for _, text in s.game_items():
                    sp, _ = rds.split_line(text)
                    sp = sp.strip() if sp else ''
                    if sp:
                        refs[aid].append(('speaker', 'Portrait', f'{sp} Portrait'))
        for aid, a in self.assets.items():          # quips: the sounds of their folder
            if a['list'] == 'quips':
                folder = 'quips/' + a['rel'].split('/', 1)[1].lower() + '/'
                for bid, b in self.assets.items():
                    if b['list'] == 'quip_snd' and b['rel'].lower().startswith(folder):
                        refs[aid].append(('folder scan', 'ReadSounds', '@id:' + bid))
        for aid, a in self.assets.items():          # models: the header as text, the sequence part as raw strings
            if a['list'] != 'models':
                continue
            f16 = [x for x in a['files'] if x.endswith('.mdl16')]
            d = ds.read(f16[0] if f16 else a['files'][0])
            try:
                seqnames = {s.name.lower() for s in mdl.read_sequences(d)}
            except Exception:                   # noqa: BLE001
                seqnames = set()
            end = d.find(SEQ_TAG)
            try:
                node = self.head.node(self.head.decode(d), 'CModel')
                refs[aid] += text_refs(tf.dumps(tf.Node(None, '<document>', [node])))
                start = end if end > 0 else 0
            except Exception:                   # noqa: BLE001 - an unreadable header: all its strings
                start = 0
            for s in raw_strings(d, start):
                if s.lower() in seqnames or s.lower() in RENDER_MODES or (s.startswith('C') and re.fullmatch(r'C[A-Z]\w+', s)):
                    continue
                refs[aid].append(('raw', 'string', s))
        refs['EXE'] = [('exe', 'string', s) for s in exe_strings(self.exe_bytes) if re.search(r'[A-Za-z]', s)]

    # --- resolution ---------------------------------------------------------------------------------------------
    def build_index(self) -> None:
        self.exact = defaultdict(dict)          # list -> name -> id
        self.by_base = defaultdict(dict)        # list -> file name -> id (first in name order, as FindFileName)
        for aid, a in sorted(self.assets.items(), key=lambda kv: kv[1]['rel'].lower()):
            if a['list'] == 'file':
                continue
            k = a['rel'].lower()
            self.exact[a['list']].setdefault(k, aid)
            self.by_base[a['list']].setdefault(_base(k), aid)
        self.files_other = {aid: a for aid, a in self.assets.items() if a['list'] == 'file'}
        self._cache: dict[str, list] = {}

    def _resolve(self, value: str) -> list[tuple[str, str]]:
        v = value.strip().replace('\\', '/').lstrip('/')
        if not v:
            return []
        if v.startswith('@id:'):
            return [(v[4:], 'folder scan')]
        lv = v.lower()
        out = []
        ne = _strip_ext(lv)
        has_ext = ne != lv
        for lst in self.exact:
            exact = self.exact[lst]
            if lst in SOUND_LISTS:
                cands = [lv] if has_ext and lv.endswith(('.wav', '.ogg')) else [ne + '.wav']
                alt = [c[:-4] + ('.ogg' if c.endswith('.wav') else '.wav') for c in cands]
                hit = None
                for c in cands + alt:
                    if c in exact:
                        hit = (exact[c], 'exact')
                        break
                if hit is None:
                    for c in cands + alt:          # a folder prefix such as "Sounds/"
                        parts = c.split('/')
                        for i in range(1, len(parts)):
                            s = '/'.join(parts[i:])
                            if s in exact:
                                hit = (exact[s], 'exact')
                                break
                        if hit:
                            break
                if hit is None:
                    for c in cands + alt:
                        if _base(c) in self.by_base[lst]:
                            hit = (self.by_base[lst][_base(c)], 'file name')
                            break
                if hit:
                    out.append(hit)
                continue
            if ne in exact:
                out.append((exact[ne], 'exact'))
                continue
            parts = ne.split('/')
            hit = None
            for i in range(1, len(parts)):
                s = '/'.join(parts[i:])
                if s in exact:
                    hit = (exact[s], 'exact')
                    break
            if hit is None and _base(ne) in self.by_base[lst]:
                hit = (self.by_base[lst][_base(ne)], 'file name')
            if hit:
                out.append(hit)
        # other files: full path, file name with extension, or without extension for .bik/.pal/Interface .bmp
        for aid, a in self.files_other.items():
            p = a['rel'].lower()
            b = _base(p)
            if lv == p or lv == b:
                out.append((aid, 'exact'))
            elif '.' in b and lv == b.rsplit('.', 1)[0] and (b.endswith(('.bik', '.pal')) or p.startswith('interface/')):
                out.append((aid, 'name without extension'))
        return out

    def resolve(self, v: str) -> list[tuple[str, str]]:
        r = self._cache.get(v)
        if r is None:
            r = self._cache[v] = self._resolve(v)
        return r

    def type_keys(self) -> None:
        """A key names entries of the lists its values hit exactly (in at least half as many cases as the best)."""
        key_lists: dict[str, Counter] = defaultdict(Counter)
        for lst in self.refs.values():
            for _, key, value in lst:
                if key in UNTYPED or key in MANUAL:
                    continue
                vs = [value] + ([p for p in value.split(',') if p.strip()] if ',' in value else [])
                for v in vs:
                    if v.strip().lower() in NONE_VALUES:
                        continue
                    for tid, how in self.resolve(v):
                        if how in ('exact', 'name without extension'):
                            key_lists[key][self.assets[tid]['list']] += 1
        allowed = {}
        for key, c in key_lists.items():
            top = max(c.values())
            allowed[key] = {lst for lst, n in c.items() if n >= max(1, 0.5 * top)}
        allowed.update(MANUAL)
        for k in SEQUENCE_KEYS | {'Environment Type', 'Position', 'Y HUD Screen Justify', 'Human Readable Name',
                                  'ID Tag', 'Objective Id Tag', 'Message To Handle'}:
            allowed[k] = set()
        allowed['Overlay HUD Sequence'] = {'inv_hud'}
        allowed['Warp Effect'] = {'sequences', 'water_warp'}
        self.allowed = allowed

    def _hits(self, src: str, key: str, v: str) -> list[tuple[str, str]]:
        ok = None if key in UNTYPED else self.allowed.get(key, set())
        low = v.strip().lower()
        out = []
        for tid, how in self.resolve(v):
            if ok is not None and self.assets[tid]['list'] not in ok:
                continue
            if key in UNTYPED:
                if low in NONE_VALUES:
                    continue
                if src != 'EXE' and how == 'file name' and '/' not in low and _strip_ext(low) == low:
                    continue
            out.append((tid, how))
        return out

    def build_edges(self) -> None:
        self.edges: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
        self.unresolved: dict[str, list] = defaultdict(list)       # key -> [(source, cls, value)]
        for src, lst in self.refs.items():
            for cls, key, value in lst:
                h = [(value, x) for x in self._hits(src, key, value)]
                if not h and ',' in value:
                    for p in value.split(','):
                        if p.strip():
                            h += [(p, x) for x in self._hits(src, key, p)]
                for v, (tid, how) in h:
                    if tid != src:
                        self.edges[src][tid].append((cls, key, v.strip(), how))
                if not h and src != 'EXE' and key not in UNTYPED and self.allowed.get(key):
                    self.unresolved[key].append((src, cls, value))

    # --- closure ------------------------------------------------------------------------------------------------
    def _blocked(self, s: str, t: str) -> bool:
        return s == 'EXE' and (t in EXE_COINCIDENCE or t in DEMO_ONLY)

    def _bfs(self, roots):
        seen = set(roots)
        q = deque(roots)
        while q:
            s = q.popleft()
            for t in self.edges.get(s, {}):
                if t not in seen and not self._blocked(s, t):
                    seen.add(t)
                    q.append(t)
        return seen

    def _label(self, a: str) -> str:
        if a == 'EXE':
            return 'Zax.exe'
        fs = self.assets[a]['files']
        for e in ('.zax', '.mdl16', '.seq16', '.frm16'):
            for f in fs:
                if f.lower().endswith(e):
                    return f
        return fs[0]

    def _ev(self, s: str, t: str) -> str:
        e = self.edges[s][t][0]
        return f'{self._label(s)} ({e[0]}: {e[1]}={e[2]}; {e[3]})'

    def closure(self) -> None:
        A, edges = self.assets, self.edges
        lv = {a for a, x in A.items() if x['list'] == 'levels'}

        def reach(start):
            seen, q = set(start), deque(start)
            while q:
                s = q.popleft()
                for t, evs in edges.get(s, {}).items():
                    if t in lv and t not in seen and any(e[1] in ('New Map Name', 'Other Map Name') for e in evs):
                        seen.add(t)
                        q.append(t)
            return seen
        story = reach([t for t in edges['file:rules.txt'] if t in lv])
        mp_levels = {a for a in lv if A[a]['rel'].lower().startswith('multiplayer/')}
        exe_levels = {t for t in edges['EXE'] if t in lv}
        reached = reach(list(story | mp_levels | exe_levels))
        orphan = lv - reached
        weak = {}
        for a, x in A.items():
            if x['list'] == 'fonts':
                weak[a] = ('loaded at start with the whole folder (Fonts list, World::LoadGameData 0x4f13a0 loads every '
                           'entry), but no name refers to it')
            elif x['list'] == 'surface':
                weak[a] = 'loaded at start with the whole folder (Surface Types, every entry loaded), but no name refers to it'
            elif x['list'] == 'item_defs':
                weak[a] = ('no name refers to it; the materials generator lists the whole item catalogue (ui_materials.cpp), '
                           'so it may appear there if its category/discovery settings allow')
            elif x['list'] == 'item_types':
                weak[a] = 'no name refers to it; item types are a definition list the inventory may iterate'
        for a in orphan:
            weak[a] = ('no transition (New Map Name/Other Map Name) from the start level leads to it, it is not in '
                       'Levels/Multiplayer and the exe does not name it; only loadable through the map selection')
        strong = ['EXE', 'file:rules.txt'] + sorted(reached) + \
            [a for a, x in A.items() if x['list'] in ('categories', 'damage', 'game_types', 'difficulty')]
        used = self._bfs(strong)
        poss = self._bfs(list(used) + [a for a in weak if a not in used]) - used
        demo_seen = self._bfs(list(DEMO_ONLY))
        inc = defaultdict(set)
        for s, ts in edges.items():
            for t in ts:
                if not self._blocked(s, t):
                    inc[t].add(s)
        status, reason, evidence, refby = {}, {}, {}, {}
        for a in A:
            if a in used:
                status[a] = USED
                srcs = sorted(s for s in inc[a] if s in used)
                refby[a] = [self._ev(s, a) for s in srcs[:8]]
                continue
            if a in poss:
                status[a] = POSSIBLY
                if a in weak:
                    reason[a] = weak[a]
                else:
                    srcs = sorted(s for s in inc[a] if s in poss or s in weak)
                    reason[a] = 'only referenced by assets that are themselves only possibly used'
                    refby[a] = [self._ev(s, a) for s in srcs[:8]]
                if a in EXE_COINCIDENCE:
                    reason[a] += '; ' + EXE_COINCIDENCE[a]
                evidence[a] = 'assumption'
                continue
            status[a] = UNUSED
            evidence[a] = 'confirmed'
            if a in DEMO_ONLY or (a in demo_seen and inc[a] <= (demo_seen | {'EXE'})):
                reason[a] = 'only used in demo mode'
                refby[a] = [DEMO_REASON]
                continue
            srcs = sorted(inc[a])
            if a in EXE_COINCIDENCE:
                reason[a] = 'no reference found (exe word coincidence only)'
                refby[a] = [EXE_COINCIDENCE[a]]
            elif srcs:
                reason[a] = 'only referenced by unused assets'
                refby[a] = [self._ev(s, a) for s in srcs[:8]]
            else:
                reason[a] = 'no reference found'
        self._refine(status, reason, refby)
        self.status, self.reason, self.evidence, self.refby = status, reason, evidence, refby
        self.placed = set()
        for s in reached | orphan:
            for t, evs in edges.get(s, {}).items():
                if A[t]['list'] == 'models' and any(e[1] == 'Model' for e in evs):
                    self.placed.add(t)

    def _refine(self, status, reason, refby) -> None:
        """More precise reasons for unused voices, mini maps, editor cursors and a few single files."""
        A = self.assets
        labels = defaultdict(list)
        for r, ls in self.rds_labels.items():
            for lab in ls:
                labels[lab.strip().lower()].append(A[r]['files'][0])
        voice_by_base = defaultdict(list)
        for a, x in sorted(A.items(), key=lambda kv: kv[1]['rel'].lower()):
            if x['list'] == 'voices':
                voice_by_base[_base(x['rel']).lower().rsplit('.', 1)[0]].append(a)
        for a, x in A.items():
            if status[a] == USED:
                continue
            lst, rel = x['list'], x['rel']
            if lst == 'voices':
                b = _base(rel).lower().rsplit('.', 1)[0]
                winner = next((o for o in voice_by_base[b] if status[o] == USED), None)
                if winner and winner != a:
                    reason[a] = 'shadowed by a file of the same name'
                    refby[a] = ['the voice lookup (CSoundList::Find 0x57e690 / ZNamedList::FindFileName 0x591ac0) takes '
                                'the exact name "<label>.wav" first, then the other extension, then the first file of that '
                                f'name below Levels in path order: {self._label(winner)} wins']
                elif b in labels:
                    reason[a] = 'dialogue line exists but no CZaxDialogAction plays it'
                    refby[a] = [f'label ":{b}" (case-insensitive) in ' + ', '.join(sorted(set(labels[b]))) +
                                '; no Line= in any level, model or definition names it']
                elif reason[a] == 'no reference found':
                    reason[a] = 'no reference found (no dialogue line of this name)'
            elif lst == 'minimap':
                reason[a] = 'stale mini map: no level with this Partial File Name in the game data'
                refby[a] = ['Cache/Levels/<Partial File Name> is only loaded for a level being loaded (Map_LoadMiniMap '
                            '0x4ece20); the Demo/ and E3 Demo/ levels were removed from the release']
            elif lst == 'cursors' and status[a] == UNUSED:
                reason[a] = 'only in the internal editor (tool cursor)'
                refby[a] = [EDITOR_CURSOR_NOTE] + refby.get(a, [])
            elif rel.lower().startswith('editor/') and lst in ('models', 'res_frm') and status[a] == UNUSED:
                reason[a] = "only in the editor's Editor/ folder: " + reason[a]
            elif lst == 'file' and rel.lower().endswith('.pk'):
                reason[a] = 'no reference found (audio-editor peak file)'
                refby[a] = ['the exe has no ".pk" string (docs/FORMATS.md 1); a waveform overview of the .ogg of the '
                            'same name']
            elif lst == 'file' and rel.lower() == 'palettes/gamepalette.bmp':
                refby[a] = ['the palette is loaded as "Palettes" + "GamePalette" + ".pal" (App_LoadPalettesAndSounds '
                            '0x4cdf70 -> 0x433000); no ".bmp" load of it']
            elif lst == 'file' and rel.lower() == 'interface/companylogo.bmp':
                refby[a] = ['no string "CompanyLogo" in the exe; Interface/%s.bmp is only the fallback of App_PlayMovie '
                            '0x4cd5a0 for the movie names JoWooD, Reflexive, Intro']

    def missing(self) -> list[Missing]:
        out = []
        for name in sorted({v.strip() for _, _, v in self.unresolved.get('New Map Name', [])}, key=str.lower):
            srcs = sorted({self._label(s) for s, _, v in self.unresolved['New Map Name'] if v.strip() == name})
            out.append(Missing(f'Levels/{name}.zax', 'level', srcs,
                               'New Map Name of a transition; no level of that name or Partial File Name exists',
                               'confirmed'))
        for name, kind, by, note, ev, files in KNOWN_MISSING:
            if not any(self.ds.exists(f) for f in files):
                out.append(Missing(name, kind, by, note, ev))
        stale = [a for a, x in self.assets.items() if x['list'] == 'minimap']
        if stale and not any(f.lower().endswith('.frm') for a in stale for f in self.assets[a]['files']):
            out.append(Missing('Cache/Levels/Demo/*.frm, Cache/Levels/E3 Demo/*.frm', 'frame', [],
                               f'the {len(stale)} stale mini maps exist only as .frm16 (no 8-bit pair); they belong to no '
                               'level anyway', 'confirmed'))
        return out

    def run(self) -> Usage:
        self.inventory()
        self.references()
        self.build_index()
        self.type_keys()
        self.build_edges()
        self.closure()
        assets = {}
        for aid, x in self.assets.items():
            st = self.status[aid]
            assets[aid] = Asset(aid, x['kind'], x['list'], x['rel'], sorted(x['files']), x['bytes'], st,
                                self.reason.get(aid, ''), self.refby.get(aid, []),
                                '' if st == USED else self.evidence.get(aid, 'assumption'))
        return Usage(assets, self.missing(), self.placed)
