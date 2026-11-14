"""Guards for files the tools write: names taken from untrusted game files, the game's own files, atomic writes.

* ``relative_problem``: a path that comes from a level or a script (``Partial File Name``, ``Script=``) and that a
  tool joins below a folder must stay below it: no absolute path, no drive letter, no ``..``.
* ``inside`` / ``join_inside``: a derived path resolved (links followed) must lie inside its root.
* ``is_game_data``: a file of a game installation of any edition (a folder holding ``Zax.exe``, ``Data.dat`` or a
  language pack ``*.RED`` above it, or below one of the given roots) is never written.
* ``atomic_write``: write a temporary file next to the target and replace the target with it, so a crash or a full
  disk never leaves a truncated level, script or Rules.txt.
"""
from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

from .i18n import translate

# names that mark a folder as (part of) a game installation; compared without case, as the game's file system
GAME_FILES = ('zax.exe', 'data.dat')
PACK_SUFFIX = '.red'
_DRIVE = re.compile(r'^[A-Za-z]:')


def relative_problem(name: str) -> str | None:
    """Why ``name`` (``/`` or ``\\`` between folders) cannot be used as a path below a folder, or None. The text is
    for a user interface (translated through ``zaxtools.i18n``)."""
    if not name or not name.strip():
        return translate('safepath', 'the name is empty')
    if '\0' in name:
        return translate('safepath', 'the name contains a NUL character')
    if name[0] in '/\\' or _DRIVE.match(name):
        return translate('safepath', 'the name is an absolute path')
    if ':' in name:
        return translate('safepath', 'the name contains “:”')
    for seg in re.split(r'[/\\]', name):
        if seg.strip(' .') == '' and seg:
            return translate('safepath', 'the name contains a folder “{segment}”').format(segment=seg)
        if seg == '':
            return translate('safepath', 'the name contains an empty folder name (“//”)')
    return None


def inside(path: str | os.PathLike, root: str | os.PathLike) -> bool:
    """Does ``path`` (resolved, links followed) lie inside ``root`` or equal it?"""
    p = Path(path).expanduser().resolve()
    r = Path(root).expanduser().resolve()
    return p == r or r in p.parents


def join_inside(root: str | os.PathLike, rel: str) -> Path:
    """``root/rel``; ValueError if ``rel`` is not a safe relative name or the result leaves ``root``."""
    why = relative_problem(rel)
    if why is not None:
        raise ValueError(why)
    p = Path(root) / rel.replace('\\', '/')
    if not inside(p, root):
        raise ValueError(translate('safepath', 'the path leads outside the folder'))
    return p


def _marks_game(folder: Path) -> bool:
    try:
        names = os.listdir(folder)
    except OSError:
        return False
    for n in names:
        low = n.lower()
        if low in GAME_FILES or low.endswith(PACK_SUFFIX):
            return True
    return False


def is_game_data(path: str | os.PathLike, roots=()) -> bool:
    """Is ``path`` (a file or folder, existing or not) part of a game installation: inside one of ``roots`` (the
    configured game data, the gamedata folder of the workspace) or below a folder that holds ``Zax.exe``,
    ``Data.dat`` or a language pack ``*.RED`` (any case; an unpacked ``Data/`` lies in such a folder)?"""
    p = Path(path).expanduser().resolve()
    for r in roots:
        if r and inside(p, r):
            return True
    return (p.is_dir() and _marks_game(p)) or any(_marks_game(f) for f in p.parents)


def atomic_write(path: str | os.PathLike, data: bytes) -> None:
    """Write ``data`` to ``path`` through a temporary file in the same folder and ``os.replace`` (the folder must
    exist). An existing file keeps its permissions; a new one gets 0644."""
    path = Path(path)
    try:
        mode = path.stat().st_mode & 0o7777
    except OSError:
        mode = 0o644
    fd, tmp = tempfile.mkstemp(prefix=f'.{path.name}.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
