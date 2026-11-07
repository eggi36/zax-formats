"""``Rules.txt`` (class ``CRules``): what a new game starts with and the layout of the game's windows.

The game reads ``Data/Rules.txt`` once at start (``CRules``, zax-decomp/reimpl/src/game_types.cpp; fields:
``First Map Name``, ``First Map Spawn Point``, ``Camera Bound Width/Height``, ``Startup Song``, ``Window
Font``, ``Custom Rules``). "New Game" starts ``First Map Name`` (path below ``Levels/`` without extension)
at ``First Map Spawn Point`` (StartNewGame ``0x59b7f0`` with 0 takes both from the rules,
zax-decomp/docs/EXE_FINDINGS.md) [verified: docs/OPEN_ISSUES.md item 8].

The editor reads the file from the output folder when it saved one there before, otherwise from the game
data (``DataSource``: the language pack wins as in the game); it writes only into the output folder. The
text tree is kept as it is, so an unchanged file is written back byte for byte and a change rewrites only
its own line.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from . import textformat as tf
from .datasource import DataSource

RULES = 'Rules.txt'
FIRST_MAP = 'First Map Name'
FIRST_SPAWN = 'First Map Spawn Point'


@dataclass
class RulesFile:
    doc: tf.Node
    source: str                 # 'output' (saved by the editor before) or 'data' (game data)
    path: str                   # where it was read from (file path or path in the game data)

    @property
    def root(self) -> tf.Node:
        return tf.root(self.doc)

    @property
    def first_map(self) -> str:
        return self.root.get(FIRST_MAP, '') or ''

    @property
    def first_spawn(self) -> str:
        return self.root.get(FIRST_SPAWN, '') or ''

    def to_bytes(self) -> bytes:
        return tf.dump_bytes(self.doc)


def from_data(ds: DataSource) -> RulesFile:
    return RulesFile(tf.load_bytes(ds.read(RULES)), 'data', RULES)


def load(ds: DataSource, out_dir: Path | None = None) -> RulesFile:
    """The output folder's ``Rules.txt`` if there is one, otherwise the game data's."""
    if out_dir is not None:
        p = Path(out_dir) / RULES
        if p.is_file():
            return RulesFile(tf.load_bytes(p.read_bytes()), 'output', str(p))
    return from_data(ds)


def save(rules: RulesFile, out_dir: Path) -> Path:
    """Write into the output folder (Latin-1, CRLF through textformat)."""
    p = Path(out_dir) / RULES
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(rules.to_bytes())
    return p


def set_start(rules: RulesFile, map_name: str, spawn: str | None = None) -> None:
    """Set the start level (and start point); only these lines change."""
    rules.root.set(FIRST_MAP, map_name)
    if spawn is not None:
        rules.root.set(FIRST_SPAWN, spawn)


def level_files(ds: DataSource, out_dir: Path | None) -> dict[str, Callable[[], bytes]]:
    """Path below ``Levels/`` without extension -> reader of the ``.zax``: the game data's levels,
    overridden by the editor's own in the output folder (same name ignoring case)."""
    found: dict[str, tuple[str, Callable[[], bytes]]] = {}
    for f in ds.list('Levels/', '.zax'):
        name = f[len('Levels/'):-len('.zax')]
        found[name.lower()] = (name, lambda f=f: ds.read(f))
    out = Path(out_dir) / 'Levels' if out_dir is not None else None
    if out is not None and out.is_dir():
        for path in out.rglob('*.zax'):
            name = path.relative_to(out).with_suffix('').as_posix()
            found[name.lower()] = (name, path.read_bytes)
    return {name: read for name, read in found.values()}


def find_level(names, map_name: str) -> str | None:
    """The key of ``names`` that means ``map_name`` (the game's file access ignores case; slashes and
    backslashes alike)."""
    want = map_name.strip().replace('\\', '/').lower()
    return next((n for n in names if n.lower() == want), None)
