"""Model catalogue: all models from Cache/Models with everything needed for placing them.

New objects are created with the **real default of the model**. Every model contains a CModel
object in its header (zaxtools.modelhead); its "Default Entity" is the default object the original
editor creates when placing - for characters with AI, upper body and weapon [verified in the game
2026-10-18]. This needs Zax.exe (field descriptions, exeschema).

Models without "Default Entity" (mostly decoration and pickups), without a readable header or
without the exe get a minimal object (class, name, model, position, start sequence); the game sets
missing fields to the class defaults, which is enough for decoration, effects and pickups
[verified].

The catalogue is built once and cached as JSON; ``signature`` detects changed game data or a
different exe.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import struct
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from . import mdl
from . import textformat as tf
from .datasource import DataSource
from .i18n import translate
from .level import Level

from . import exeschema as _exeschema, modelhead as _modelhead
VERSION = f'11-{_exeschema.VERSION}-{_modelhead.VERSION}'   # catalogue + schema + decoder
MODEL_DIR = 'Cache/Models/'
_SEQ_TAG = struct.pack('<ff', 27.0, 758.0)
_CLASS_RE = re.compile(rb'C[A-Z][A-Za-z0-9]{3,}')
_NOT_ENTITY = ('CEntityAnimatedUpperBody',)


@dataclass
class ModelInfo:
    path: str                         # e.g. "Environments/Jungle/Trees/Palm Tree 3"
    cls: str                          # class of a new object
    ai: str                           # first AI class in the model header ('' = none)
    sequences: list[str]
    uses: int = 0                     # objects with this model in all levels
    header_cls: str = ''              # class according to the model header (rough, without exe)
    level_sequence: str = ''          # most frequent start sequence in the levels
    example: str = ''                 # a level in which the model occurs
    head: str = ''                    # 'default' | 'no-default' | 'unreadable' | 'no-exe'
    head_error: str = ''
    default: str = ''                 # default object as text (only if head == 'default')
    hit_points: float = 0.0
    model_sequence: str = ''          # "Default Sequence" from the model header
    sorting_y: int = 0
    own: bool = False                 # a model file in the output folder (zaxtools.imageimport; not cached)

    @property
    def folder(self) -> str:
        return self.path.rsplit('/', 1)[0] if '/' in self.path else ''

    @property
    def name(self) -> str:
        return self.path.rsplit('/', 1)[-1]

    @property
    def default_sequence(self) -> str:
        """Start sequence: the model's "Default Sequence", else 'Idle', else the most frequent one
        in the levels, else the first base sequence (not a layer like '<x> Shadow')."""
        names = self.sequences
        if self.model_sequence and self.model_sequence.lower() in (n.lower() for n in names):
            return self.model_sequence
        if any(n.lower() == 'idle' for n in names):
            return next(n for n in names if n.lower() == 'idle')
        if self.level_sequence:
            return self.level_sequence
        low = [n.lower() for n in names]
        for n in names:
            if not any(n.lower().startswith(o + ' ') for o in low if o != n.lower()):
                return n
        return names[0] if names else ''


def header_info(data: bytes) -> tuple[str, str]:
    """(object class, AI class) roughly from the header (without exe; class names in plain text)."""
    end = data.find(_SEQ_TAG)
    head = data[:end if end > 0 else len(data)]
    classes = [c.decode('latin-1') for c in _CLASS_RE.findall(head)]
    ents = [c for c in classes if c.startswith('CEntity') and 'Behavior' not in c and c not in _NOT_ENTITY]
    ai = next((c for c in classes if not c.startswith('CEntity') and c.endswith('AI')), '')
    return (ents[0] if ents else 'CEntityBase'), ai


def signature(ds: DataSource, exe: str | Path | None = None) -> str:
    """Signature of the data state: path, size and modification time of levels, models and exe."""
    h = hashlib.sha1(str(ds.root.resolve()).encode())
    for rel in ds.list('Levels/', '.zax') + ds.list(MODEL_DIR, '.mdl16'):
        name = ds.resolve(rel)
        st = os.stat(name) if ds._zip is None and not ds.in_pack(rel) else None
        h.update(f'{rel}|{st.st_size if st else 0}|{int(st.st_mtime) if st else 0}\n'.encode())
    if ds._zip is not None:
        st = os.stat(ds.root)
        h.update(f'zip|{st.st_size}|{int(st.st_mtime)}'.encode())
    # language pack only if it replaces levels or models (GERMAN.RED does not)
    if ds.language_pack is not None and any(ds.in_pack(r) for r in ds.list('Levels/', '.zax') + ds.list(MODEL_DIR, '.mdl16')):
        st = os.stat(ds.language_pack)
        h.update(f'pack|{ds.language_pack.resolve()}|{st.st_size}|{int(st.st_mtime)}'.encode())
    if exe:
        st = os.stat(exe)
        h.update(f'exe|{st.st_size}|{int(st.st_mtime)}'.encode())
    return h.hexdigest()


class Catalog:
    def __init__(self, models: dict[str, ModelInfo], sig: str = ''):
        self.models = models
        self.signature = sig

    def __len__(self):
        return len(self.models)

    def __getitem__(self, path: str) -> ModelInfo:
        return self.models[path]

    # --- Build ----------------------------------------------------------------
    @classmethod
    def build(cls, ds: DataSource, progress=None, exe: str | Path | None = None,
              cache_dir: Path | None = None) -> 'Catalog':
        """``progress(i, n, text)`` is called regularly. With ``exe`` (Zax.exe) the model headers are
        read and real default objects are created."""
        head = None
        if exe:
            from .exeschema import Schema
            from .modelhead import ModelHead
            if progress:
                progress(0, 1, translate('catalog', 'reading Zax.exe …'))
            head = ModelHead(Schema.open(exe, ds, cache_dir) if cache_dir else Schema.build(exe, ds))
        model_files = ds.list(MODEL_DIR, '.mdl16')
        level_files = ds.list('Levels/', '.zax')
        total = len(model_files) + len(level_files)
        models: dict[str, ModelInfo] = {}
        for i, f in enumerate(model_files):
            if progress and i % 50 == 0:
                progress(i, total, translate('catalog', 'reading models …'))
            path = f[len(MODEL_DIR):-len('.mdl16')]
            d = ds.read(f)
            c, ai = header_info(d)
            info = ModelInfo(path, c, ai, [s.name for s in mdl.read_sequences(d)], header_cls=c)
            if head is None:
                info.head = 'no-exe'
            else:
                _read_head(head, d, info)
            models[path] = info
        by_lower = {m.lower(): m for m in models}
        classes: dict[str, Counter] = {}
        seqs: dict[str, Counter] = {}
        for i, f in enumerate(level_files):
            if progress:
                progress(len(model_files) + i, total, translate('catalog', 'counting the use in levels …'))
            for p in Level.from_bytes(ds.read(f)).parts:
                m = by_lower.get((p.model or '').lower())
                if m is None or p.position is None:
                    continue
                info = models[m]
                info.uses += 1
                info.example = info.example or f
                classes.setdefault(m, Counter())[p.cls] += 1
                if p.sequence:
                    seqs.setdefault(m, Counter())[p.sequence] += 1
        for m, c in classes.items():
            if models[m].head != 'default':          # the class of the default object takes precedence
                models[m].cls = c.most_common(1)[0][0]
        for m, c in seqs.items():
            models[m].level_sequence = c.most_common(1)[0][0]
        return cls(models, signature(ds, exe))

    def add_own(self, out_dir: Path, schema=None) -> list[str]:
        """Add (or mark) the models in ``<out_dir>/Cache/Models`` (own models from the import; a file there with the
        path of a shipped model is a changed copy, which wins in the game when copied below Data/). They are read
        anew every time and are not part of the cached catalogue. ``schema``: the exe's (``exeschema.Schema``) for
        the headers, None = without. Returns their paths."""
        base = Path(out_dir) / MODEL_DIR
        if not base.is_dir():
            return []
        head = None
        if schema is not None:
            from .modelhead import ModelHead
            head = ModelHead(schema)
        by_lower = {m.lower(): m for m in self.models}
        out = []
        for f in sorted(base.rglob('*.mdl16')):
            path = f.relative_to(base).with_suffix('').as_posix()
            known = by_lower.get(path.lower())
            if known is not None:
                self.models[known].own = True
                out.append(known)
                continue
            d = f.read_bytes()
            c, ai = header_info(d)
            info = ModelInfo(path, c, ai, [s.name for s in mdl.read_sequences(d)], header_cls=c, own=True)
            if head is None:
                info.head = 'no-exe'
            else:
                _read_head(head, d, info)
            self.models[path] = info
            out.append(path)
        return out

    def sorting_y(self) -> dict[str, int]:
        """Model path (lower case) -> "Sorting Y" for render.Assets.sort_y (only values other than 0)."""
        return {m.path.lower(): m.sorting_y for m in self.models.values() if m.sorting_y}

    # --- Create objects -----------------------------------------------------------
    def make_node(self, path: str) -> tf.Node:
        """New object (``Level Part``, empty name, position 0/0): the model's default object, otherwise
        a minimal object."""
        info = self.models[path]
        if info.head == 'default' and info.default:
            return next(c for c in tf.loads(info.default).children if isinstance(c, tf.Node))
        node = tf.Node('Level Part', info.cls)
        for k, v in (('Name', ''), ('Model', info.path), ('Position X', '0'), ('Position Y', '0'),
                     ('Cur Sequence', info.default_sequence)):
            node.children.append(tf.Entry(k, v))
        return node

    # --- Cache ------------------------------------------------------------------
    def save(self, file: Path) -> None:
        file.parent.mkdir(parents=True, exist_ok=True)
        data = {'version': VERSION, 'signature': self.signature,
                'models': [asdict(m) for m in self.models.values()]}
        tmp = file.with_suffix('.tmp')
        tmp.write_text(json.dumps(data), encoding='utf-8')
        tmp.replace(file)

    @classmethod
    def load(cls, file: Path, sig: str | None = None) -> 'Catalog | None':
        """Load the saved catalogue; None if missing, outdated or a different version."""
        try:
            data = json.loads(file.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None
        if data.get('version') != VERSION or (sig is not None and data.get('signature') != sig):
            return None
        return cls({m['path']: ModelInfo(**m) for m in data['models']}, data['signature'])

    @classmethod
    def open(cls, ds: DataSource, cache_dir: Path, progress=None, exe: str | Path | None = None) -> 'Catalog':
        """Load from the cache or build anew and save."""
        sig = signature(ds, exe)
        file = Path(cache_dir) / f'katalog-{sig[:16]}.json'
        cat = cls.load(file, sig)
        if cat is None:
            cat = cls.build(ds, progress, exe, cache_dir)
            cat.save(file)
            for old in Path(cache_dir).glob('katalog-*.json'):     # remove outdated catalogues
                if old != file:
                    old.unlink(missing_ok=True)
        return cat


def _read_head(head, data: bytes, info: ModelInfo) -> None:
    from .modelhead import DecodeError
    try:
        m = head.decode(data)
    except DecodeError as e:
        info.head, info.head_error = 'unreadable', str(e)[:200]
        return
    v = m.values
    info.hit_points = float(v.get('Hit Points') or 0)
    info.model_sequence = v.get('Default Sequence') or ''
    info.sorting_y = int(v.get('Sorting Y') or 0)
    node = head.default_part(m, info.path)
    if node is None:
        info.head = 'no-default'
        return
    info.head, info.cls = 'default', node.value
    if node.item('Cur Sequence') is not None:
        node.set('Cur Sequence', info.default_sequence)
    info.default = tf.dumps(tf.Node(None, '<document>', [node]))
