"""Level check: what in a level makes the game crash or hang, and what has no effect in the game.

Every finding names its severity, the object (a ``Level Part`` of the Tree List, or the level header),
the field, an explanation for the editor (English, translatable through ``zaxtools.i18n``) and the source of the knowledge (a section of
``zax-decomp/docs/ORIGINAL_BUGS.md``, ``zax-decomp/docs/EXE_FINDINGS.md`` or ``zax-decomp/docs/DECOMPILATION.md`` with the addresses).
Only behaviour the sources describe is checked; where a check also needs an assumption (which list a
field's names come from), the explanation says so.

Severities:
    error    the game ends (message box + exit), hangs, crashes or stops reading the level
    warning  the setting does nothing in the game, or the game reads garbage
    info     the setting has no effect, harmless

What is needed:
    ``DataSource``          always (lists of models, sounds, item definitions, categories, ...)
    ``Schema`` (Zax.exe)    optional: registered classes, the class of a field, point/colour fields,
                            the model header (``Bounce Factor``). Without it the checks that need it
                            are left out (``Context.skipped``).

Nothing here contains data from Zax.exe or the game data: the lists are read at run time.
"""
from __future__ import annotations

import math
import re
import struct
from dataclasses import dataclass
from pathlib import Path

from . import children as ch, mdl, rds, textformat as tf, transition
from .datasource import DataSource
from .i18n import QT_TRANSLATE_NOOP, translate
from .level import Level, LevelPart
from .links import LinkIndex

SEVERITIES = ('error', 'warning', 'info')
# shown translated: translate('levelcheck', SEVERITY_TEXT[s])
SEVERITY_TEXT = {'error': QT_TRANSLATE_NOOP('levelcheck', 'Error'),
                 'warning': QT_TRANSLATE_NOOP('levelcheck', 'Warning'),
                 'info': QT_TRANSLATE_NOOP('levelcheck', 'Note')}

# Stream_ReadLine 0x4a2ad0 reads n - 1 bytes and needs the line end among them; Object_ReadText 0x416b60
# passes a buffer of 0x400 bytes: a line (with its indentation) of 0x3ff characters or more stops the read
LINE_LIMIT = 0x400 - 2

# check id -> (severity, title); the title is shown translated (``Finding.title``)
CHECKS = {
    'unknown-class': ('error', QT_TRANSLATE_NOOP('levelcheck', 'Unknown class')),
    'unexpected-brace': ('error', QT_TRANSLATE_NOOP('levelcheck', 'Unexpected brace “{”')),
    'line-too-long': ('error', QT_TRANSLATE_NOOP('levelcheck', 'Line too long')),
    'array-count': ('error', QT_TRANSLATE_NOOP('levelcheck', 'Count does not match the elements')),
    'missing-model': ('error', QT_TRANSLATE_NOOP('levelcheck', 'Model missing')),
    'missing-sequence': ('error', QT_TRANSLATE_NOOP('levelcheck', 'Sequence missing in the model')),
    'rotation-frames': ('error', QT_TRANSLATE_NOOP('levelcheck', 'Frames not divisible by the rotations')),
    'bounce-factor': ('error', QT_TRANSLATE_NOOP('levelcheck', 'Bounce Factor outside 0 … 1')),
    'flag-empty-name': ('error', QT_TRANSLATE_NOOP('levelcheck', 'Empty name in a name list')),
    'flag-unknown-name': ('error', QT_TRANSLATE_NOOP('levelcheck', 'Unknown name in a name list')),
    'resource-unknown': ('error', QT_TRANSLATE_NOOP('levelcheck', 'Unknown name (the game exits)')),
    'dialog-missing': ('error', QT_TRANSLATE_NOOP('levelcheck', 'Dialogue script or line missing')),
    'dialog-voice': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'Dialogue line without voice file')),
    'dialog-portrait': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'Speaker without portrait')),
    'current-frame': ('error', QT_TRANSLATE_NOOP('levelcheck', 'Current Frame not finite')),
    'patrol-random-hang': ('error', QT_TRANSLATE_NOOP('levelcheck', 'Random path with only one point')),
    'shield-non-character': ('error', QT_TRANSLATE_NOOP('levelcheck', 'CShieldAI on a non-character')),
    'sethome-non-character': ('error', QT_TRANSLATE_NOOP('levelcheck', 'CSetHomeAction on a non-character')),
    'file-name-tilde': ('error', QT_TRANSLATE_NOOP('levelcheck', '“~” in the file name')),
    'point-value': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'Point without two numbers')),
    'color-value': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'Colour without three numbers')),
    'unresolved-reference': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'Name not in the level')),
    'pickup-no-default-item': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'Item without Default Inventory Item')),
    'map-name-backslash': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'Backslash in the level name')),
    'turret-ai': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'Obsolete CTurretAI')),
    'old-bad-patrol-ai': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'Obsolete COldBadPatrolAI')),
    'sound-environment-action': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'CChangeSoundEnvironmentTypeAction '
                                                                            'without effect')),
    'placed-mine': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'Placed Proximity Mine')),
    'placed-drone': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'Placed Companion Drone')),
    'fidget-order': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'Fidget order not implemented')),
    'disable-minimap': ('info', QT_TRANSLATE_NOOP('levelcheck', '“Disable Mini-Map” without effect')),
    'listener-settings': ('info', QT_TRANSLATE_NOOP('levelcheck', '“Listener Settings” without effect')),
    'smooth-turning': ('info', QT_TRANSLATE_NOOP('levelcheck', '“Smooth Turning” off is ignored')),
    'polygon-points': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'Polygon with more than 25 points')),
    'way-none': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'No way point network')),
    'way-island': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'Way point island')),
    'way-unreachable': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'No way point near the object')),
    'way-other-island': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'Object on a way point island')),
    'way-polygon-empty': ('info', QT_TRANSLATE_NOOP('levelcheck', 'Way point polygon without way points')),
    'child-upper-body-parent': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'Upper body on a parent that is not animated')),
    'child-walking-ai-root': ('error', QT_TRANSLATE_NOOP('levelcheck', 'CWalkingUpperBodyAI without a walking root')),
    'child-same-as-parent-class': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'CSameAsParentAI on a child that is no '
                                                                              'upper body')),
    'child-no-model': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'Child object without a model')),
    'child-hidden': ('warning', QT_TRANSLATE_NOOP('levelcheck', 'Upper body without the parent\'s sequence')),
    'missing-target-level': ('info', QT_TRANSLATE_NOOP('levelcheck', 'Transition to a level that does not exist')),
}

# --- Lists of names ---------------------------------------------------------------------------------
# Fields whose text is looked up by name in one of the game's lists (FlagsField 0x414cf0, the resource
# kinds 0x54e220/0x54e560/0x5182d0 in the exe's field registration) and the list they come from. The list
# behind a field is not written in the field; it was matched against the game data: every value of these
# fields in the 112 original levels is in the list named here [verified with tools/check_levels.py].
FLAG_FIELDS = {
    'CLayerPart.Category': 'category', 'CSetCategoryAction.New Category': 'category',
    'CPickupAI.Who Can Pick Up': 'category', 'CSelectiveCollideAI.Collides with': 'category',
    'CSetTargetTypeAction.Valid Targets': 'category', 'CTurretAI.Valid Targets': 'category',
    'CEntityBehaviorStateSetClosestTarget.Valid Targets': 'category',
    'CLayerPart.Used In': 'gametype', 'CLayerSaveData.Allowable Games': 'gametype',
    'CIsGameTypeAction.Type To Check for': 'gametype',
    'CPercentInvulnerableAI.Damage Types': 'damage',
}
RESOURCE_FIELDS = {
    'CEntityBase.Model': 'model', 'CSetModelAction.New Model': 'model',
    'CSetModelAction.New Child Model': 'model', 'CCreateDefaultEntityAction.Model to Create': 'model',
    'CParticleInfo.Model': 'model', 'CSpawnableModel.Model': 'model', 'CSpawnEffectAction.Explosion Model': 'model',
    'CEntityOverlayWalking.Overlay Model': 'model', 'CTeamInfo.Model Type': 'model',
    'CDropAllOreAndCrystalsAction.OreAndCrystalsPileModel': 'model',
    'CAddEffectAction.Warp Sound': 'sound', 'CAmbientSoundAI.Sound': 'sound', 'CGravityParticleAI.Bounce Sound': 'sound',
    'CPainAction.Sound': 'sound', 'CPlaySoundAction.Sound': 'sound', 'SyfaceTypeSoundItem.Sound': 'sound',
    'CPlaySoundBySurfaceTypeAction.Default Sound': 'sound',
    'CCheckForInventoryItemBaseAction.Inventory Item Definition': 'itemdef',
    'CDiscoverInventoryItemAction.Inventory Item Definition': 'itemdef',
    'CGiveDefaultInventoryItemAction.Inventory Item Definition': 'itemdef',
    'CUseChargeFromInventoryItemAction.Inventory Item Definition': 'itemdef',
    'CInventoryItemBase.Definition Index': 'itemdef', 'CPickupAI.Normal Item': 'itemdef',
    'CPickupAI.Alternate Item Def': 'itemdef', 'COverridePickupAI.Alternate Item Def': 'itemdef',
    'CDamageExpandingRadiusAI.Damage Type': 'damage', 'CPainAction.Damage Type': 'damage',
    'CShieldAI.Damage Type': 'damage', 'CShieldInventoryItem.Damage Type': 'damage',
    'CRechargeShieldAction.Damage Type': 'damage',
    'CEntityDestructable.Default Death Type': 'death', 'CLayerSaveData.Default Game Type': 'gametype',
    'CUseCannedAction.Canned Object': 'canned', 'SyfaceTypeSoundItem.Surface Type': 'surface',
    'CRenderablePolygon.Static Texture': 'texture', 'CRenderablePolygon.Animated Texture': 'animtex',
    'CRenderablePolygon.Warp Effect': 'warp',
    'CMusicMixerData.Full Mix Song': 'music', 'CMusicMixerData.Med Mix Song': 'music',
    'CMusicMixerData.Ambiant Song': 'music',
}
# list -> (folder below Data, extensions; the names are the paths below the folder without extension,
# '' = with extension), description (shown translated)
LISTS = {
    'model': ('Cache/Models', ('.mdl16', '.mdl'), QT_TRANSLATE_NOOP('levelcheck', 'models (Cache/Models)')),
    'sound': ('Sounds', ('',), QT_TRANSLATE_NOOP('levelcheck', 'sounds (Sounds)')),
    'itemdef': ('Inventory/Item Definitions', ('.txt',),
                QT_TRANSLATE_NOOP('levelcheck', 'items (Inventory/Item Definitions)')),
    'category': ('Categories', ('.txt',), QT_TRANSLATE_NOOP('levelcheck', 'categories (Categories)')),
    'damage': ('Damage Types', ('.txt',), QT_TRANSLATE_NOOP('levelcheck', 'damage types (Damage Types)')),
    'death': ('Death Behaviors', ('.txt',), QT_TRANSLATE_NOOP('levelcheck', 'kinds of death (Death Behaviors)')),
    'gametype': ('Resources/Game Types', ('.zgt',), QT_TRANSLATE_NOOP('levelcheck', 'game types (Resources/Game Types)')),
    'canned': ('Resources', ('.can',), QT_TRANSLATE_NOOP('levelcheck', 'Canned Objects (Resources)')),
    'surface': ('Surface Types', ('.sty',), QT_TRANSLATE_NOOP('levelcheck', 'surfaces (Surface Types)')),
    'texture': ('Cache/Textures', ('.frm16', '.frm'), QT_TRANSLATE_NOOP('levelcheck', 'textures (Cache/Textures)')),
    'animtex': ('Cache/Animated Textures', ('.seq16', '.seq'),
                QT_TRANSLATE_NOOP('levelcheck', 'animated textures (Cache/Animated Textures)')),
    'warp': ('Water Warp Effects', ('.txt',), QT_TRANSLATE_NOOP('levelcheck', 'water effects (Water Warp Effects)')),
    'music': ('Music', ('',), QT_TRANSLATE_NOOP('levelcheck', 'music (Music)')),
}
SRC_FIND_OR_FAIL = ('zax-decomp/docs/ORIGINAL_BUGS.md 2.7; NamedList_FindOrFail 0x591fc0 '
                    '("Fatal Not Found Error", exit(-1))')

# The class a placed object must derive from for an AI or action that treats it as a character
CHARACTER = 'CEntityCharacter'


@dataclass
class Finding:
    severity: str                   # 'error' | 'warning' | 'info'
    check: str                      # key of CHECKS
    message: str                    # explanation for the editor (translated when the finding is made)
    source: str                     # where the knowledge comes from (document, section, addresses)
    node: tf.Node | None = None     # the Level Part, None = level header / file
    field: str = ''                 # field path below the object, e.g. "Activity › Enter Action › Sound"
    value: str = ''

    @property
    def part(self) -> LevelPart | None:
        return LevelPart(self.node) if self.node is not None else None

    @property
    def title(self) -> str:
        return translate('levelcheck', CHECKS[self.check][1])

    def object_text(self) -> str:
        if self.node is None:
            return translate('levelcheck', 'Level')
        p = LevelPart(self.node)
        return p.name or (p.model or '').rsplit('/', 1)[-1] or p.cls


class Context:
    """What the checks need from the game data, built lazily and kept between runs (one per data
    source). ``schema``: ``exeschema.Schema`` or None. ``exe``: path of Zax.exe for the enum names of the
    fidget order (optional)."""

    def __init__(self, ds: DataSource, schema=None, exe: str | Path | None = None, extra_roots=()):
        """``extra_roots``: folders laid out like ``Data`` whose ``.RDS``, voice and model files win, and whose
        files count in the name lists (the editor's output folder: files below ``Data/`` win in the game)."""
        self.ds, self.schema, self.exe = ds, schema, exe
        self.extra_roots = [Path(r) for r in extra_roots if r]
        self.dialog_resources = rds.Resources(ds, self.extra_roots)
        self._lists: dict[str, set[str]] = {}
        self._files: set[str] | None = None
        self._models: dict[str, object] = {}
        self._heads: dict[str, object] = {}
        self._owner: dict[tuple[str, str], str | None] = {}
        self._defaults: dict[str, str] | None = None
        self._deployable: dict[str, str] | None = None
        self._fidget: list[str] | None = None
        self._scripts: dict[str, rds.Script | None] = {}
        self._head_decoder = None
        self._way: tuple[bytes, object] | None = None
        self._way_models: dict[str, object] = {}
        self._levels: set[str] | None = None

    @property
    def skipped(self) -> list[str]:
        """Checks left out for want of the exe schema."""
        if self.schema is not None:
            return []
        return ['unknown-class', 'bounce-factor', 'point-value', 'color-value', 'shield-non-character',
                'sethome-non-character']

    # --- lists -----------------------------------------------------------------------------------
    def names(self, kind: str) -> set[str]:
        if kind not in self._lists:
            folder, exts, _ = LISTS[kind]
            out = set()
            rels = self.ds.list(folder + '/', '')
            for root in self.extra_roots:        # own files in the output folder (models made by the import)
                base = root / folder
                if base.is_dir():
                    rels += [folder + '/' + f.relative_to(base).as_posix() for f in base.rglob('*') if f.is_file()]
            for rel in rels:
                sub = rel[len(folder) + 1:]
                low = sub.lower()
                for e in exts:
                    if e == '':
                        out.add(low)
                    elif low.endswith(e):
                        out.add(low[:-len(e)])
            self._lists[kind] = out
        return self._lists[kind]

    def has(self, kind: str, name: str) -> bool:
        low = name.lower()
        names = self.names(kind)
        if low in names:
            return True
        # the sound list retries a missing ".wav" as ".ogg" (0x4e2030), not the other way round
        return kind == 'sound' and low.endswith('.wav') and low[:-4] + '.ogg' in names

    def level_exists(self, name: str) -> bool:
        """Is there a level ``Levels/<name>.zax`` (case-insensitive, ``.zax`` optional) in the game data or one
        of the extra roots (the output folder), or a level of that file name in any folder (as ZNamedList's
        FindFileName 0x591ac0; two original transitions name "01 Main" so) [assumption: that the map switch
        resolves the name like the named lists; the two "01 Main" transitions were not run in the game]?"""
        if self._levels is None:
            names = {rel[len('Levels/'):-len('.zax')].lower() for rel in self.ds.list('Levels/', '.zax')}
            for root in self.extra_roots:
                lv = root / 'Levels'
                if lv.is_dir():
                    names |= {f.relative_to(lv).with_suffix('').as_posix().lower() for f in lv.rglob('*')
                              if f.suffix.lower() == '.zax'}
            self._levels = names | {n.rsplit('/', 1)[-1] for n in names}
        key = name.strip().replace('\\', '/').strip('/').lower()
        if key.endswith('.zax'):
            key = key[:-4]
        return key in self._levels

    def _exists(self, rel: str) -> bool:
        return self._own(rel) is not None or self.ds.exists(rel)

    def _own(self, rel: str) -> Path | None:
        """The file below one of the extra roots (the spelling as given; the macOS file system ignores case), else
        None."""
        for root in self.extra_roots:
            f = root / rel
            if f.is_file():
                return f
        return None

    def _read(self, rel: str) -> bytes:
        own = self._own(rel)
        return own.read_bytes() if own is not None else self.ds.read(rel)

    def model(self, path: str):
        """``mdl`` sequences (name, frames, rotations) of a model or None if it is missing."""
        key = path.lower()
        if key not in self._models:
            rel = f'Cache/Models/{path}.mdl16'
            if not self._exists(rel):
                rel = f'Cache/Models/{path}.mdl'
            self._models[key] = mdl.read_sequences(self._read(rel)) if self._exists(rel) else None
        return self._models[key]

    def model_head(self, path: str):
        """Decoded model header (``modelhead.Obj``) or None (no schema, missing, unreadable)."""
        if self.schema is None:
            return None
        key = path.lower()
        if key not in self._heads:
            from .modelhead import DecodeError, ModelHead
            if self._head_decoder is None:
                self._head_decoder = ModelHead(self.schema)
            rel = f'Cache/Models/{path}.mdl16'
            try:
                self._heads[key] = self._head_decoder.decode(self._read(rel)) if self._exists(rel) else None
            except (DecodeError, struct.error, ValueError):
                self._heads[key] = None
        return self._heads[key]

    def way_model(self, path: str):
        """``waymap.ModelData`` of a model: the bounds polygon and, with the schema, the activity."""
        from . import waymap
        key = path.lower()
        if key not in self._way_models:
            rel = f'Cache/Models/{path}.mdl16'
            if not self._exists(rel):
                self._way_models[key] = None
            else:
                head = self.model_head(path)
                act = None if head is None else [o.cls for o in (head.values.get('Activity') or []) if o is not None]
                self._way_models[key] = waymap.ModelData(waymap.poly_from_model(self._read(rel)), act)
        return self._way_models[key]

    def way_map(self, level: Level):
        """``waymap.Result`` of the level as the game builds it (cached for unchanged level text)."""
        from . import waymap
        data = level.to_bytes()
        if self._way is None or self._way[0] != data:
            self._way = (data, waymap.build(level, self.way_model))
        return self._way[1]

    def dialog_script(self, script: str) -> rds.Script | None:
        """The script ``Levels/<script>.RDS`` (an extra root first) or None if it is missing."""
        if script not in self._scripts:
            found = rds.read_script(self.ds, script, self.extra_roots)
            self._scripts[script] = None if found is None else rds.loads(found[0])
        return self._scripts[script]

    def dialog_labels(self, script: str) -> set[str] | None:
        s = self.dialog_script(script)
        return None if s is None else {name.strip().lower() for name in s.labels()}

    def item_defaults(self) -> dict[str, str]:
        """Item definition (lower case) -> class of its "Default Inventory Item" ('' = none)."""
        if self._defaults is None:
            self._defaults, self._deployable = {}, {}
            folder = 'Inventory/Item Definitions/'
            for rel in self.ds.list(folder, '.txt'):
                name = rel[len(folder):-4]
                try:
                    root = tf.root(tf.load_bytes(self.ds.read(rel)))
                except ValueError:
                    continue
                self._defaults[name.lower()] = root.get('Default Inventory Item', '') or ''
                proj = root.get('Projectile') or ''
                # what the game lays or deploys: the mine (laid by "Drop Mine", 0x5ab9a0) and the
                # devices of the category "Companion Drone" (deployed by 0x47a0f0)
                if proj and name.lower() == 'proximity mine':
                    self._deployable[proj.lower()] = 'mine'
                elif proj and (root.get('Inventory Type') or '').lower() == 'companion drone':
                    self._deployable[proj.lower()] = 'drone'
        return self._defaults

    def deployable(self) -> dict[str, str]:
        self.item_defaults()
        return self._deployable

    def fidget_orders(self) -> list[str]:
        """Names of "Fidget Sequence Order" by value (enum table 0x613410 of Zax.exe, read at run time;
        empty without the exe)."""
        if self._fidget is None:
            self._fidget = []
            if self.exe:
                try:
                    self._fidget = _enum_table(Path(self.exe), 0x613410)
                except Exception:          # noqa: BLE001 - another exe, pefile missing
                    self._fidget = []
        return self._fidget

    # --- schema ----------------------------------------------------------------------------------
    def owner(self, cls: str, key: str) -> str | None:
        """Class that registers field ``key`` of ``cls`` (or of a base class)."""
        k = (cls, key)
        if k not in self._owner:
            r = None
            if self.schema is not None and self.schema.known(cls):
                for c in self.schema.chain(cls)[::-1]:
                    if any(f['name'] == key for f in self.schema.classes[c]['fields']):
                        r = c
                        break
            elif self.schema is None:
                r = cls          # without the exe: only fields named with their own class
            self._owner[k] = r
        return self._owner[k]

    def field_enc(self, cls: str, key: str) -> str | None:
        if self.schema is None or not self.schema.known(cls):
            return None
        for c in self.schema.chain(cls)[::-1]:
            for f in self.schema.classes[c]['fields']:
                if f['name'] == key:
                    return f['enc']
        return None

    def derives(self, cls: str, base: str) -> bool | None:
        if self.schema is None or not self.schema.known(cls):
            return None
        return base in self.schema.chain(cls)


def _enum_table(exe: Path, va: int) -> list[str]:
    """(value, name pointer, 0) triples up to the first null name."""
    import pefile
    data = exe.read_bytes()
    pe = pefile.PE(data=data, fast_load=True)
    base = pe.OPTIONAL_HEADER.ImageBase
    off = lambda v: pe.get_offset_from_rva(v - base)
    o, out = off(va), []
    while True:
        value, ptr, _ = struct.unpack_from('<III', data, o)
        if ptr < base or value != len(out):
            return out
        p = off(ptr)
        out.append(data[p:data.find(b'\0', p)].decode('latin-1'))
        o += 12


# --- The check ------------------------------------------------------------------------------------

_NUM = r'\s*[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?\s*'
_POINT = re.compile(f'^{_NUM},{_NUM}')
_COLOR = re.compile(f'^{_NUM},{_NUM},{_NUM}')


def check(level: Level, ctx: Context, path: str | None = None) -> list[Finding]:
    """All findings of a level. ``path``: the level's path below ``Levels/`` (for the file name checks)."""
    out: list[Finding] = []
    add = lambda sev_check, msg, src, node=None, fld='', value='': out.append(
        Finding(CHECKS[sev_check][0], sev_check, msg, src, node, fld, value))
    _walk_header(level, ctx, add)
    for p in level.parts:
        _walk(p.node, p.node.value, p.node, '', 3, ctx, add, level)
        _part_checks(p, level, ctx, add)
        _child_checks(p, ctx, add)
    _raw_braces(level.root, None, add)
    _reference_checks(level, ctx, add)
    _way_checks(level, ctx, add)
    if path and '~' in path:
        add('file-name-tilde', translate('levelcheck', 'The file name contains “~”: the game\'s file search stops with '
                                                       'a message (exit(-1)).'),
            'zax-decomp/docs/ORIGINAL_BUGS.md 2.36; Files_ListNames 0x4a1150', None, translate('levelcheck', 'File'), path)
    return out


def _walk_header(level: Level, ctx: Context, add) -> None:
    root = level.root
    for c in root.children:
        if isinstance(c, tf.Node) and c.key == 'Tree List':
            continue
        if isinstance(c, tf.Node) and c.value == 'Array':
            _array(c, root.value, None, c.key, 2, ctx, add, level)
        elif isinstance(c, tf.Node) and not c.value.startswith('CFrame(') and c.key != 'Dynamic Properties':
            _walk(c, c.value, None, c.key, 2, ctx, add, level)
        elif isinstance(c, tf.Entry):
            _entry(root.value, c, None, '', 1, ctx, add)
    if root.get('Disable Mini-Map', '0') not in ('0', ''):
        add('disable-minimap', translate('levelcheck', '“Disable Mini-Map” has no effect in the game: the game shows '
                                                       'the mini map anyway, no code reads the field.'),
            'zax-decomp/docs/ORIGINAL_BUGS.md 1.6; docs/FORMATS.md 5 (CLayerSaveData +0x168, registered at 0x4e645f)',
            None, 'Disable Mini-Map', root.get('Disable Mini-Map'))
    # Listener Settings: the setters store values the retail game never uses
    lst = [('Environment Type', 'Generic',
            QT_TRANSLATE_NOOP('levelcheck', 'setter 0x4e6c20 passes the type to the empty function 0x4186e0 (ret 4)')),
           ('Rolloff', 5.0,
            QT_TRANSLATE_NOOP('levelcheck', 'setter 0x4e6c50 → 0x57c210 stores 0x713698, which only 0x57c220 reads '
                                            '(only caller 0x42de33 in the never reached debug drawing of '
                                            'CAmbientSoundAI)')),
           ('Environment Size', 7.5,
            QT_TRANSLATE_NOOP('levelcheck', 'setter 0x4e6c80 → 0x57c230 stores 0x7136f0, which no instruction reads'))]
    for key, default, why in lst:
        v = root.get(key)
        if v is None:
            continue
        if isinstance(default, float):
            try:
                same = float(v) == default
            except ValueError:
                same = False
        else:
            same = v.strip().lower() == default.lower()
        if not same:
            add('listener-settings', translate('levelcheck', '“Listener Settings/{key}” has no effect in the game '
                                                             '({why}). The value differs from the default ({default}) '
                                                             'but changes nothing.').format(
                key=key, why=translate('levelcheck', why), default=default),
                'zax-decomp/docs/ORIGINAL_BUGS.md 1.17; zax-decomp/reimpl/src/layer.cpp (registration of the fields)', None, key, v)
    name = root.get('Partial File Name', '') or ''
    if '\\' in name:
        add('map-name-backslash', translate('levelcheck', 'The level name contains “\\”: the game requires slashes '
                                                          '“/” ("Map Name *MAY NOT* contain backslashes").'),
            'zax-decomp/docs/EXE_FINDINGS.md, "Other useful messages" (Map paths)',
            None, 'Partial File Name', name)


def _label(prefix: str, key: str | None) -> str:
    return f'{prefix} › {key}' if prefix else (key or '')


def _walk(node: tf.Node, cls: str, part: tf.Node | None, prefix: str, depth: int, ctx: Context, add, level) -> None:
    """Check a block (object of class ``cls``) and everything below it."""
    if cls and ctx.schema is not None and not cls.startswith('CFrame(') and cls != 'Array' \
            and node.key != 'Dynamic Properties' and not ctx.schema.known(cls):
        add('unknown-class', translate('levelcheck', 'The class “{cls}” is not registered in the game: when loading, '
                                                     'the game shows a message and exits (exit(-1)).').format(cls=cls),
            'zax-decomp/docs/ORIGINAL_BUGS.md 2.5; Create 0x415c00 (classes from the registration in Zax.exe, '
            'zaxtools/exeschema.py)', part, prefix, cls)
    if cls == 'COldBadPatrolAI':
        add('old-bad-patrol-ai', translate('levelcheck', 'COldBadPatrolAI is an obsolete class: its constructor '
                                                         'reseeds the game\'s random generator (2342342), every such '
                                                         'object changes the random sequence.'),
            'zax-decomp/docs/ORIGINAL_BUGS.md 1.14; constructor 0x55c390, generator 0x6d06c0', part, prefix, cls)
    elif cls == 'CTurretAI':
        add('turret-ai', translate('levelcheck', 'CTurretAI is obsolete: on every touch the game reports "Please '
                                                 'change all CTurretAIs to Sentinon AIs". Better use CSentinonAI.'),
            'zax-decomp/docs/EXE_FINDINGS.md, "SourceSafe and other messages"; CTurretAI::MayTouch 0x58e340 (Slot 31); '
            'zax-decomp/docs/ORIGINAL_BUGS.md 4.12', part, prefix, cls)
    elif cls == 'CChangeSoundEnvironmentTypeAction':
        add('sound-environment-action', translate('levelcheck', 'CChangeSoundEnvironmentTypeAction has no effect in '
                                                                'the game: it passes the type to an empty function.'),
            'zax-decomp/docs/ORIGINAL_BUGS.md 1.13; empty function 0x4186e0 (ret 4)',
            part, prefix, cls)
    elif cls == 'CEntityBehaviorMoveToPos' and node.get('Smooth Turning') == '0':
        add('smooth-turning', translate('levelcheck', '“Smooth Turning”=0 is ignored in CEntityBehaviorMoveToPos: the '
                                                      'game tests the field with bit 8 already set, the turning always '
                                                      'goes through the steering.'),
            'zax-decomp/docs/ORIGINAL_BUGS.md 1.8; CEntityBehaviorMoveToPos::Update 0x430f20', part,
            _label(prefix, 'Smooth Turning'), '0')
    elif cls == 'CFidgetSettings':
        _fidget(node, part, prefix, ctx, add)
    elif cls == 'CPatrolPathAI':
        _patrol(node, part, prefix, level, add)
    elif cls in ('CPickupAI', 'CGiveDefaultInventoryItemAction'):
        key = 'Normal Item' if cls == 'CPickupAI' else 'Inventory Item Definition'
        v = node.get(key)
        if v and ctx.item_defaults().get(v.strip().lower(), None) == '':
            msg = (translate('levelcheck', 'The item “{item}” has no “Default Inventory Item”: picking it up then '
                                           'only gives the “Special Item” (nothing without one).')
                   if cls == 'CPickupAI' else
                   translate('levelcheck', 'The item “{item}” has no “Default Inventory Item”: the action only gives '
                                           'items whose definition has a Default Inventory Item.'))
            add('pickup-no-default-item', msg.format(item=v),
                'zax-decomp/docs/DECOMPILATION.md section 8, "CPickupAI" (0x53e4c0, 0x5b7aa0) and "Actions" '
                '(CGiveDefaultInventoryItemAction)', part, _label(prefix, key), v)
    if cls == 'CDialogActionBase' or (node.get('Script') is not None and node.get('Line') is not None
                                      and ctx.owner(cls, 'Script') == 'CDialogActionBase'):
        _dialog(node, part, prefix, ctx, add)
    for c in node.children:
        if isinstance(c, tf.Entry):
            _entry(cls, c, part, prefix, depth, ctx, add)
        elif isinstance(c, tf.Node):
            if c.value == 'Array':
                _array(c, cls, part, _label(prefix, c.key), depth + 1, ctx, add, level)
            elif not c.value.startswith('CFrame(') and c.key != 'Dynamic Properties':
                _walk(c, c.value, part, _label(prefix, c.key), depth + 1, ctx, add, level)


def _array(node: tf.Node, owner_cls: str, part, prefix: str, depth: int, ctx: Context, add, level) -> None:
    cnt = node.get('Item Count') or node.get('Array Count')
    elems = node.array_elements()
    if cnt is not None:
        try:
            n = int(cnt)
        except ValueError:
            n = None
        if n != len(elems):
            add('array-count', translate('levelcheck', 'The count ({count}) does not match the %n element(s): the game '
                                                       'cannot process the state (default objects, crash when deleting '
                                                       'or reading past the data).', None, len(elems)).format(count=cnt),
                'zax-decomp/docs/ORIGINAL_BUGS.md 2.4; 0x419810, 0x418050, 0x416310', part, prefix, cnt)
    for e in elems:
        if isinstance(e, tf.Node):
            if e.value == 'Array':
                _array(e, owner_cls, part, prefix, depth + 1, ctx, add, level)
            elif not e.value.startswith('CFrame('):
                _walk(e, e.value, part, prefix, depth + 1, ctx, add, level)
        elif isinstance(e, tf.Entry):
            _line_length(e, part, prefix, depth, add)


def _line_length(e: tf.Entry, part, prefix: str, depth: int, add) -> None:
    n = len(e.indent if e.indent is not None else '\t' * depth) + len(e.key) + 1 + len(e.value)
    if n > LINE_LIMIT:
        add('line-too-long', translate('levelcheck', 'The line is {length} characters long (at most {limit}): the '
                                                     'game\'s line reader does not find its end in the 0x400 byte '
                                                     'buffer and stops reading there: everything after it is missing '
                                                     'in the game (in the test: ground black, following objects '
                                                     'missing).').format(length=n, limit=LINE_LIMIT),
            'Stream_ReadLine 0x4a2ad0, Object_ReadText 0x416b60 (buffer 0x400); zax-decomp/docs/ORIGINAL_BUGS.md 2.1/2.2; '
            'verified 2026-10-28, /Original, Test/CheckLine',
            part, _label(prefix, e.key), e.value[:40] + '…')


def _entry(cls: str, e: tf.Entry, part, prefix: str, depth: int, ctx: Context, add) -> None:
    _line_length(e, part, prefix, depth, add)
    key, v = e.key, e.value
    owner = ctx.owner(cls, key)
    if owner is None:
        return
    full = f'{owner}.{key}'
    label = _label(prefix, key)
    if full in FLAG_FIELDS:
        _flags(full, v, part, label, ctx, add)
    elif full in RESOURCE_FIELDS:
        kind = RESOURCE_FIELDS[full]
        if not ctx.has(kind, v.strip() if kind != 'sound' else v):
            if kind == 'model':
                add('missing-model', translate('levelcheck', 'The model “{model}” does not exist: the game looks for '
                                                             'it in the model list and exits ("Fatal Not Found '
                                                             'Error").').format(model=v),
                    f'{SRC_FIND_OR_FAIL}; ResourceField_SetByName 0x54e490; zax-decomp/docs/ORIGINAL_BUGS.md 2.13',
                    part, label, v)
            else:
                add('resource-unknown', translate('levelcheck', '“{name}” is not in the list {list}: the game looks '
                                                                'for the name and exits ("Fatal Not Found Error"). '
                                                                '(Which list belongs to the field is derived from the '
                                                                'original data.)').format(
                    name=v, list=translate('levelcheck', LISTS[kind][2])),
                    f'{SRC_FIND_OR_FAIL}; ResourceField_SetByName 0x54e490',
                    part, label, v)
    elif key == 'Current Frame' and owner == 'CEntityAnimated':
        try:
            f = struct.unpack('<f', struct.pack('<f', float(v)))[0]
        except (ValueError, OverflowError):
            f = math.inf
        if not math.isfinite(f) or abs(f) >= 2 ** 24:
            add('current-frame', translate('levelcheck', '“Current Frame”={value}: the game brings the frame into '
                                                         'range by repeatedly adding/subtracting the frame count; with '
                                                         'NaN, infinity or values this large (float32 from 2^24) that '
                                                         'never ends.').format(value=v),
                'zax-decomp/docs/ORIGINAL_BUGS.md 2.16; EntityAnimated_SetFrame 0x48feb0', part, label, v)
    else:
        enc = ctx.field_enc(cls, key)
        if enc in ('pt', 'ipt') and v and not _POINT.match(v):
            add('point-value', translate('levelcheck', 'The point “{value}” needs two numbers “x, y”: the game fills '
                                                       'missing parts with pointer bits (garbage values).').format(
                value=v), 'zax-decomp/docs/ORIGINAL_BUGS.md 2.8; PointField_FromText 0x4a8140, '
                'IntPointField_FromText 0x5455d0', part, label, v)
        elif enc in ('0x46dcc0', '0x46de20') and v and not _COLOR.match(v):
            add('color-value', translate('levelcheck', 'The colour “{value}” needs three numbers “r,g,b”: missing parts '
                                                       'leave stack garbage or pointer bits in the colour.').format(
                value=v), 'zax-decomp/docs/ORIGINAL_BUGS.md 2.8; ColorField_FromText 0x46df60',
                part, label, v)


def _flags(full: str, v: str, part, label: str, ctx: Context, add) -> None:
    """FlagsField_FromText 0x414fa0: each name between the commas through FindOrFail; an empty text gives 0,
    a comma at the end ends the loop, an empty name before a comma is searched (and missing)."""
    if not v:
        return
    kind = FLAG_FIELDS[full]
    parts = v.split(',')
    if parts[-1] == '':
        parts = parts[:-1]
    for name in parts:
        if name == '':
            add('flag-empty-name', translate('levelcheck', '“{value}” contains an empty name between commas: the game '
                                                           'looks for it in the list and exits ("Fatal Not Found '
                                                           'Error").').format(value=v),
                f'{SRC_FIND_OR_FAIL}; FlagsField_FromText 0x414fa0; verified 2026-10-28, /Original, '
                'Test/CheckFlag', part, label, v)
        elif not ctx.has(kind, name):
            add('flag-unknown-name', translate('levelcheck', '“{name}” is not in the list {list}: the game exits '
                                                             '("Fatal Not Found Error"). Write the names without '
                                                             'spaces after the comma. (Which list belongs to the field '
                                                             'is derived from the original data.)').format(
                name=name, list=translate('levelcheck', LISTS[kind][2])),
                f'{SRC_FIND_OR_FAIL}; FlagsField_FromText 0x414fa0', part, label, v)


def _dialog(node: tf.Node, part, prefix: str, ctx: Context, add) -> None:
    script, line = node.get('Script'), node.get('Line')
    if not script:
        return
    labels = ctx.dialog_labels(script)
    src = f'{SRC_FIND_OR_FAIL}; ResourceField_SetByName 0x54e490 (CDialogActionBase.Script/Line)'
    if labels is None:
        add('dialog-missing', translate('levelcheck', 'The dialogue script “Levels/{script}.RDS” does not exist: the '
                                                      'game looks for it and exits.').format(script=script),
            src, part, _label(prefix, 'Script'), script)
    elif line and line.strip().lower() not in labels:
        add('dialog-missing', translate('levelcheck', 'The line “:{line}” is not in the script “{script}”: the game '
                                                      'looks for it and exits.').format(line=line, script=script),
            src, part, _label(prefix, 'Line'), line)
    elif line:
        item = ctx.dialog_script(script).find(line.strip())
        if item is None:
            return
        res = ctx.dialog_resources
        if res.voice(item.name) is None:
            add('dialog-voice', translate('levelcheck', 'No voice file “{name}.wav” or “.ogg” below Levels: the line '
                                                        'is shown without a voice (and scrolls at the fixed '
                                                        'speed).').format(name=item.name),
                'CZaxDialogAction slot 29 0x41d830, SoundList_Find 0x57e690', part, _label(prefix, 'Line'), line)
        speaker, _ = rds.split_line(item.text())
        if res.portrait(speaker) is None:
            add('dialog-portrait', translate('levelcheck', 'No portrait “{speaker} Portrait” in '
                                                           'Cache/Inventory/Frames/Dialog Display/Portraits: the '
                                                           'dialogue window shows “!Unknown Portrait”.').format(
                speaker=rds.shown_speaker(speaker)),
                'DialogDisplay_Portrait 0x47ccc0, CZaxDialogAction::SplitLine 0x5a4bd0', part,
                _label(prefix, 'Line'), line)


def _fidget(node: tf.Node, part, prefix: str, ctx: Context, add) -> None:
    v = node.get('Fidget Sequence Order')
    names = [n.lower() for n in ctx.fidget_orders()]
    if not v or v.strip().lower() not in names:
        return
    i = names.index(v.strip().lower())
    if i in (3, 4):
        msg = translate('levelcheck', 'The fidget order “{value}” is not implemented (the game reports "Not '
                                      'Implemented Yet!!!").')
    elif i == 5:
        msg = translate('levelcheck', 'The fidget order “{value}” never moves on: the game reads the index after the '
                                      'last one taken and only wraps it.')
    else:
        return
    add('fidget-order', msg.format(value=v), 'zax-decomp/docs/ORIGINAL_BUGS.md 1.15; '
        'CFidgetData::PickFidget 0x4a0680', part, _label(prefix, 'Fidget Sequence Order'), v)


def _patrol(node: tf.Node, part, prefix: str, level: Level, add) -> None:
    """CPatrolPathAI: with "Random" and only one point to choose (count - 1, less one with "Ignore last
    point") the loop that wants another point never ends."""
    if (node.get('Order') or '').strip().lower() != 'random':
        return
    name = (node.get('Path Poly') or '').strip()
    poly = next((p for p in level.parts if p.name == name and p.polygon), None)
    if poly is None:
        return
    choose = len(poly.polygon) - 1 - (1 if node.get('Ignore last point') not in (None, '0', '') else 0)
    if choose == 1:
        add('patrol-random-hang', translate('levelcheck', '“Random” on the path “{path}” with only one point to '
                                                          'choose ({points} points): the loop that looks for another '
                                                          'point never ends (the game hangs).').format(
            path=name, points=len(poly.polygon)),
            'zax-decomp/docs/ORIGINAL_BUGS.md 2.31; DECOMPILATION.md section 8, "The patrol, pickup and player control AIs"',
            part, _label(prefix, 'Order'), node.get('Order'))


def _raw_braces(node: tf.Node, part, add) -> None:
    for c in node.children:
        if isinstance(c, tf.Raw) and c.text.strip() == '{':
            add('unexpected-brace', translate('levelcheck', 'A “{” in an unexpected place: the game reports "Found '
                                                            'unexpected \'{\' while parsing class ..." and exits.'),
                'zax-decomp/docs/ORIGINAL_BUGS.md 2.6; Object_ReadText 0x416b60',
                part, '', '{')
        elif isinstance(c, tf.Node) and not c.value.startswith('CFrame('):
            _raw_braces(c, part if part is not None else (c if c.key == 'Level Part' else None), add)


def _part_checks(p: LevelPart, level: Level, ctx: Context, add) -> None:
    node = p.node
    seen = set()
    for ex in transition.exits(p):
        if ex.map_name.lower() not in seen and not ctx.level_exists(ex.map_name):
            seen.add(ex.map_name.lower())
            add('missing-target-level', translate('levelcheck', 'The transition ({action}) leads to the level “{level}”, '
                                                                'which is neither in the game data nor in the output '
                                                                'folder. What the game does when such a transition runs '
                                                                'was not tested.').format(action=ex.action, level=ex.map_name),
                'zaxtools/usage.py (names the game asks for without a file; the originals: "Demo Mission2" x5, '
                '"Hasbro Start" in 2 levels)', node, 'New Map Name', ex.map_name)
    model = p.model
    if model and ctx.has('model', model):
        seqs = ctx.model(model) or []
        cur = p.sequence
        if cur and not cur.strip().lstrip('-').isdigit() and cur.lower() not in {s.name.lower() for s in seqs}:
            add('missing-sequence', translate('levelcheck', 'The sequence “{sequence}” does not exist in the model '
                                                            '“{model}”: the game looks for it when loading and exits '
                                                            '("Fatal Not Found Error"), other places read a missing '
                                                            'sequence without a test.').format(sequence=cur, model=model),
                f'zax-decomp/docs/ORIGINAL_BUGS.md 2.13; {SRC_FIND_OR_FAIL}; ResourceField_CtorSequence 0x5182d0; '
                'verified 2026-10-28, /Original, Test/CheckSeq (loading stops in "Layer Loading")',
                node, 'Cur Sequence', cur)
        for s in seqs:
            if s.rotations == 0 or (s.rotations > 1 and s.total % s.rotations):
                add('rotation-frames', translate('levelcheck', 'Sequence “{sequence}” of the model “{model}”: {frames} '
                                                               'frames cannot be divided among {rotations} rotations. '
                                                               'The game divides by the rotations and ends with "There '
                                                               'are not an equal number of frames per rotation…" when '
                                                               'it loads the sequence by its name.').format(
                    sequence=s.name, model=model, frames=s.total, rotations=s.rotations),
                    'zax-decomp/docs/ORIGINAL_BUGS.md 2.14; CRotationSequence Slot 27 0x5600f0', node, 'Model', model)
        if ctx.derives(p.cls, 'CEntityMovable'):
            head = ctx.model_head(model)
            bf = head.values.get('Bounce Factor') if head is not None else None
            if isinstance(bf, float) and not (0.0 <= bf <= 1.0):
                add('bounce-factor', translate('levelcheck', 'The model “{model}” has the Bounce Factor {value}: as soon '
                                                             'as the object bounces, the game reports "Model %s has a '
                                                             'Bounce Factor of %f." and exits.').format(
                    model=model, value=f'{bf:g}'),
                    'zax-decomp/docs/ORIGINAL_BUGS.md 2.15; CEntityMovable::BounceMotion 0x491710 (Slot 94), Text 0x6128ec',
                    node, 'Model', model)
        kind = ctx.deployable().get(model.lower())
        if kind == 'mine':
            add('placed-mine', translate('levelcheck', 'A Proximity Mine placed in the level does nothing: it does not '
                                                       'go off, not even with “Tries To Collide”=1, “Stationary”=0, '
                                                       'the sequence “Deploy” or “Created By”. Only a mine laid by the '
                                                       'player (key “Drop Mine”) explodes.'),
                'zax-decomp/docs/EXE_FINDINGS.md, "Deploying devices", '
                '"Proximity Mine" (verified 2026-10-21 and 2026-10-28, /Original)', node, 'Model', model)
        elif kind == 'drone':
            add('placed-drone', translate('levelcheck', 'A Companion Drone placed in the level does not follow Zax: its '
                                                        'CCompanionAI finds no owner (“Created By” is no '
                                                        'CEntityWalking when loading) and deletes itself, the drone '
                                                        'stands still. Only a drone deployed by the player works.'),
                'zax-decomp/docs/EXE_FINDINGS.md, "Deploying '
                'devices" (CCompanionAI 0x46e800; verified 2026-10-28, /Original, Test/DroneCreator)',
                node, 'Model', model)
    # AIs in the object's own Activity that treat the object as a character
    act = node.block('Activity')
    if act is not None and ctx.derives(p.cls, CHARACTER) is False:
        for e in act.array_elements():
            if isinstance(e, tf.Node) and ctx.derives(e.value, 'CShieldAI'):
                add('shield-non-character', translate('levelcheck', 'CShieldAI on an object of the class {cls}: the AI '
                                                                    'reads the character\'s inventory without a test, '
                                                                    'on a non-character the game ends.').format(
                    cls=p.cls),
                    'zax-decomp/docs/ORIGINAL_BUGS.md 2.29; CShieldAI::FindItem 0x56d7d0', node, 'Activity', e.value)


def _is(ctx: Context, cls: str, base: str) -> bool:
    """``cls`` derives from ``base``: by the exe schema, else by zaxtools.children's class lists."""
    d = ctx.derives(cls, base)
    return ch.derives(cls, base) if d is None else d


def _child_checks(p: LevelPart, ctx: Context, add, prefix: str = 'Child List', depth: int = 0,
                  root: LevelPart | None = None) -> None:
    """The objects of the part's Child List (zaxtools.children; LevelPart.children), and their own children
    (``root``: the part of the Tree List; the findings name it): a missing model or sequence, an upper body or a
    CSameAsParentAI where the code does nothing with it, a CWalkingUpperBodyAI without a walking root, an upper body
    whose model lacks the parent's start sequence."""
    from . import anim
    root = root or p
    for i, c in enumerate(p.children):
        label = f'{prefix} › {i + 1}: {c.cls}'
        model = c.model
        if not (model or '').strip():
            add('child-no-model', translate('levelcheck', 'The child object ({cls}) has no model: the game has nothing '
                                                          'to draw for it (what else it does with it was not '
                                                          'tested).').format(cls=c.cls),
                'zaxtools/children.py; CLayerPart slot 23 0x4fa9a0 (draws the children with their model)',
                root.node, label + ' › Model', '')
        elif ctx.has('model', model):
            seqs = ctx.model(model) or []
            names = {s.name.lower() for s in seqs}
            cur = c.sequence
            if cur and not cur.strip().lstrip('-').isdigit() and cur.lower() not in names:
                add('missing-sequence', translate('levelcheck', 'The sequence “{sequence}” does not exist in the model '
                                                                '“{model}” of the child object: the game looks for it '
                                                                'when loading and exits ("Fatal Not Found '
                                                                'Error").').format(sequence=cur, model=model),
                    f'zax-decomp/docs/ORIGINAL_BUGS.md 2.13; {SRC_FIND_OR_FAIL}; ResourceField_CtorSequence 0x5182d0',
                    root.node, label + ' › Cur Sequence', cur)
            ai = ch.same_as_parent_ai(c, ctx.schema)
            parent_seq = anim.part_animation(p, None).sequence if p.model else None
            if ai is not None and _is(ctx, c.cls, ch.UPPER_BODY) and _is(ctx, p.cls, 'CEntityAnimated') \
                    and ai.get('Only Show First Sequence', '0').strip() in ('0', '') and parent_seq \
                    and ctx.has('model', p.model or '') and parent_seq.lower() not in names \
                    and parent_seq.lower() not in ('death', 'dead'):
                # Death/Dead: the legs model shows the whole character (docs/FORMATS.md "Composite characters";
                # the two dead Korbos of 07 Village Main)
                add('child-hidden', translate('levelcheck', 'The upper body\'s model “{model}” has no sequence '
                                                            '“{sequence}”, the parent\'s at level start: the game '
                                                            'hides the upper body while the parent plays a sequence '
                                                            'its model lacks.').format(model=model, sequence=parent_seq),
                    'CSameAsParentAI::Update 0x562010 (zax-decomp/reimpl/src/ai_rest_d.cpp); zaxtools/anim.py child_animation',
                    root.node, label + ' › Model', model)
        if _is(ctx, c.cls, ch.UPPER_BODY) and not _is(ctx, p.cls, 'CEntityAnimated'):
            add('child-upper-body-parent', translate('levelcheck', 'An upper body ({cls}) on a parent of the class '
                                                                   '{parent}, which is not animated: it does not turn '
                                                                   'with it (angle 0) and its CSameAsParentAI does '
                                                                   'nothing (it needs an animated parent).').format(
                cls=c.cls, parent=p.cls),
                'CEntityAnimatedUpperBody slot 46 0x4943b0 (zax-decomp/reimpl/src/entity_classes.cpp); CSameAsParentAI::Update '
                '0x562010 (zax-decomp/reimpl/src/ai_rest_d.cpp)', root.node, label, c.cls)
        act = c.node.block('Activity')
        for e in act.array_elements() if act is not None else []:
            if not isinstance(e, tf.Node):
                continue
            if _is(ctx, e.value, ch.WALKING_UPPER_BODY_AI) and not _is(ctx, root.cls, 'CEntityWalking'):
                add('child-walking-ai-root', translate('levelcheck', 'CWalkingUpperBodyAI on a child of a {parent}: '
                                                                     'its update takes the root as a walking character '
                                                                     'and calls it without a test (a null pointer when '
                                                                     'the root does not walk): the game ends right '
                                                                     'after loading. Use CSameAsParentAI '
                                                                     'there.').format(parent=root.cls),
                    'CWalkingUpperBodyAI::Update 0x595ff0, Message 0x596160 (zax-decomp/reimpl/src/quest_ai.cpp); verified '
                    '2026-10-29, /Original, Test/GTChildCrash (a light beam staff with the Rogcoil\'s upper body: '
                    'the game ends after "Preload things on Map"; the control Test/GTChildCtl with CSameAsParentAI '
                    'runs)',
                    root.node, label + ' › Activity', e.value)
            elif _is(ctx, e.value, ch.SAME_AS_PARENT) and not _is(ctx, c.cls, ch.UPPER_BODY):
                add('child-same-as-parent-class', translate('levelcheck', '{ai} on a child of the class {cls}: the AI '
                                                                          'only works on a CEntityAnimatedUpperBody, '
                                                                          'here it does nothing.').format(
                    ai=e.value, cls=c.cls),
                    'CSameAsParentAI::Update 0x562010 (zax-decomp/reimpl/src/ai_rest_d.cpp)', root.node, label + ' › Activity',
                    e.value)
        _child_checks(c, ctx, add, label, depth + 1, root)


def _reference_checks(level: Level, ctx: Context, add) -> None:
    idx = LinkIndex(level)
    seen = set()
    for lk in idx.links:
        if lk.targets:
            if lk.action == 'CSetHomeAction' and lk.key == 'Actor':
                for t in lk.targets:
                    if ctx.derives(t.cls, CHARACTER) is False:
                        add('sethome-non-character', translate('levelcheck', 'CSetHomeAction names “{name}” ({cls}): '
                                                                             'the action calls slot 129 on the target '
                                                                             'as a character without a test; a '
                                                                             'non-character crashes the game.').format(
                            name=lk.name, cls=t.cls),
                            'zax-decomp/docs/ORIGINAL_BUGS.md 2.28; DECOMPILATION.md section 8, "The actions"',
                            lk.source.node, 'Actor', lk.name)
            continue
        k = (id(lk.source.node), lk.key, lk.name)
        if k in seen:
            continue
        seen.add(k)
        add('unresolved-reference', translate('levelcheck', 'No object is called “{name}” ({action}, {key}). The '
                                                            'action finds nothing; actions and AIs that read their '
                                                            'target without a test crash the game when they run with '
                                                            'a missing target.').format(
            name=lk.name, action=lk.action, key=lk.key), 'zax-decomp/docs/ORIGINAL_BUGS.md 2.28; zaxtools/links.py',
            lk.source.node, lk.key, lk.name)


# --- Way point network ------------------------------------------------------------------------------

SRC_WAY = ('docs/FORMATS.md 4; CWayPointMap::Calculate 0x5383f0 (zaxtools/waymap.py, equal to all 112 shipped '
           '.way files)')
SRC_FIND_PATH = 'CWayPointMap::FindPath 0x5386b0 (a way point within 4, 39 or 156 pixels for each end)'
SRC_POLY_LIMIT = 'Polygon_FromText 0x5480e0 → Polygon_Insert 0x5466c0 (nothing from 25 points on)'
WAY_AIS = {'CSpawnPointAI': QT_TRANSLATE_NOOP('levelcheck', 'start point'),
           'CPatrolPathAI': QT_TRANSLATE_NOOP('levelcheck', 'patrol path'),
           'CPatrolAreaAI': QT_TRANSLATE_NOOP('levelcheck', 'patrol area')}
# Characters that walk (and so use the path search of the walking behaviour); flying and stationary ones not
WALKING_CLASSES = {'CEntityWalking', 'CEntityOverlayWalking', 'CEntityOm'}
WAY_ISLAND_MIN = 3        # smaller islands (stray way points) are not reported


def _way_points_of(p: LevelPart, level: Level) -> list[tuple[str, float, float]]:
    """(what, x, y) of a part the AI's path search starts or ends at: characters, start points, the points
    of patrol paths."""
    out = []
    pos = p.position
    acts = [n for n in (p.node.block('Activity') or []) if isinstance(n, tf.Node)]
    if pos is not None:
        if p.cls in WALKING_CLASSES:
            out.append((translate('levelcheck', 'walking character'), *pos))
        elif any(a.value == 'CSpawnPointAI' for a in acts):
            out.append((translate('levelcheck', WAY_AIS['CSpawnPointAI']), *pos))
    for a in acts:
        if a.value == 'CPatrolPathAI':
            name = (a.get('Path Poly') or '').strip()
            poly = next((q for q in level.parts if name and q.name == name and q.polygon), None)
            if poly is not None:
                what = translate('levelcheck', WAY_AIS['CPatrolPathAI'])
                out += [(f'{what} “{name}”', x, y) for x, y in poly.polygon]
    return out


def _way_checks(level: Level, ctx: Context, add) -> None:
    from . import waymap
    for p in level.parts:
        t = p.get('Polygon')
        if t is None:
            continue
        n = len([v for v in t.split(',') if v.strip()]) // 2
        if n > 25:
            add('polygon-points', translate('levelcheck', 'The polygon has {points} points: the game reads only the first '
                                                          '25 and drops the rest, the outline it uses ends there.').format(
                points=n), SRC_POLY_LIMIT, p.node, 'Polygon', f'{n}')
    res = ctx.way_map(level)
    w = res.way
    polys = res.inputs.polygons
    needs = [(p, what, x, y) for p in level.parts for what, x, y in _way_points_of(p, level)]
    if not w.nodes:
        if needs:
            add('way-none', translate('levelcheck', 'The level has no way points (no way point polygon makes any), '
                                                    'so the AI\'s path search never finds a way around an '
                                                    'obstacle.'), f'{SRC_WAY}; {SRC_FIND_PATH}')
        return
    comp = waymap.components(w)
    counts_: dict[int, int] = {}
    for c in comp:
        counts_[c] = counts_.get(c, 0) + 1
    made = [0] * len(polys)
    for o in res.origin:
        if o >= 0:
            made[o] += 1
    for k, wp in enumerate(polys):
        if not made[k]:
            add('way-polygon-empty', translate('levelcheck', 'The way point polygon makes no way point: its outline is '
                                                             'too short, blocked by collision or every point lies '
                                                             'within 20 pixels of a way point already made.'),
                SRC_WAY, level.parts[wp.index].node, 'Polygon')
    idx = waymap.NodeIndex(w)
    import numpy as np
    xy = np.array([(n.x, n.y) for n in w.nodes], np.float64)
    cmp = np.array(comp)
    main_xy = xy[cmp == 0]
    for c in sorted(counts_):
        if c == 0:
            continue
        members = [i for i, ci in enumerate(comp) if ci == c]
        if len(members) < WAY_ISLAND_MIN:
            continue
        owners: dict[int, int] = {}
        for i in members:
            if res.origin[i] >= 0:
                owners[res.origin[i]] = owners.get(res.origin[i], 0) + 1
        mine = xy[members]
        gap = min(float(np.sqrt(((main_xy - q) ** 2).sum(1)).min()) for q in mine)
        node = level.parts[polys[max(owners, key=owners.get)].index].node if owners else None
        add('way-island', translate('levelcheck', '%n way point(s) are not connected to the main network '
                                                  '({main} way points): the gap is {gap} pixels, the game joins way '
                                                  'points only up to {limit} pixels. The AI cannot find a path '
                                                  'between them.', None, len(members)).format(
            main=counts_[0], gap=f'{gap:.0f}', limit=w.max_connect), SRC_WAY, node, 'Polygon')
    for p, what, x, y in needs:
        end = idx.path_end(x, y)
        if end is None:
            add('way-unreachable', translate('levelcheck', '{what} at {x}, {y}: no way point within {reach} pixels; '
                                                           'the path search gives up for paths from or to here '
                                                           '(the AI only walks straight lines).').format(
                what=what, x=f'{x:g}', y=f'{y:g}', reach=w.max_connect * waymap.PATH_END_REACH),
                SRC_FIND_PATH, p.node, 'Position')
        elif comp[end] != 0:
            add('way-other-island', translate('levelcheck', '{what} at {x}, {y}: the nearest way point belongs to an '
                                                            'island of {n} way points, not to the main network; paths '
                                                            'to the rest of the level fail.').format(
                what=what, x=f'{x:g}', y=f'{y:g}', n=counts_[comp[end]]), f'{SRC_FIND_PATH}; {SRC_WAY}', p.node,
                'Position')


# --- Summary ---------------------------------------------------------------------------------------

def counts(findings: list[Finding]) -> dict[str, int]:
    out = {s: 0 for s in SEVERITIES}
    for f in findings:
        out[f.severity] += 1
    return out


def summary(findings: list[Finding]) -> str:
    c = counts(findings)
    if not findings:
        return translate('levelcheck', 'No findings.')
    text = {'error': lambda n: translate('levelcheck', '%n error(s)', None, n),
            'warning': lambda n: translate('levelcheck', '%n warning(s)', None, n),
            'info': lambda n: translate('levelcheck', '%n note(s)', None, n)}
    return ', '.join(text[s](c[s]) for s in SEVERITIES if c[s])
