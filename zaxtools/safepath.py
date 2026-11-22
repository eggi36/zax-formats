"""Guards for files the tools write: names taken from untrusted game files, the game's own files, atomic writes.

* ``relative_problem``: a path that comes from a level or a script (``Partial File Name``, ``Script=``) and that a
  tool joins below a folder must stay below it: no absolute path, no drive letter, no ``..``.
* ``inside`` / ``join_inside``: a derived path resolved (links followed) must lie inside its root.
* ``is_game_data``: a file of a game installation of any edition (below a game folder, ``marks_game``, or below one of
  the given roots) is never written.
* ``atomic_write``: write a temporary file next to the target and replace the target with it, so a crash or a full
  disk never leaves a truncated level, script or Rules.txt.
"""
from __future__ import annotations

import os
import re
import tempfile
import zipfile
from pathlib import Path

from .datasource import _open_zip

from .i18n import translate

# names that mark a folder as (part of) a game installation; compared without case, as the game's file system
GAME_FILES = ('zax.exe', 'data.dat')
PACK_SUFFIX = '.red'
PORT_MARKER = 'zax-data.bin'    # zax-redone's imported copy of the game (DATA.dat, the packs, this file; no Zax.exe)
# entries that only the game's archive holds (the engine's file types; matched without case)
_GAME_ENTRY = re.compile(r'\.(zax|way|rds|frm|frm16|seq|seq16|mdl16)$', re.I)
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


_DEVICE = re.compile(r'^(con|prn|aux|nul|com[1-9]|lpt[1-9])(\.|$)', re.I)


def new_name_problem(name: str) -> str | None:
    """Why ``name`` (one folder or file name the user gives a new file) cannot be created on Windows below the game's
    Data folder or written into a level, or None: control characters, a trailing dot or space, and the reserved
    device names (CON, NUL, COM1, …, with any extension) (review 5 P60-5). The text is for a user interface."""
    if any(ord(c) < 0x20 or ord(c) == 0x7f for c in name):
        return translate('safepath', 'the name contains a control character')
    if name.endswith(('.', ' ')):
        return translate('safepath', 'the name ends with a dot or a space')
    if _DEVICE.match(name):
        return translate('safepath', 'the name is reserved on Windows (CON, NUL, COM1, …)')
    return None


def inside(path: str | os.PathLike, root: str | os.PathLike) -> bool:
    """Does ``path`` (resolved, links followed) lie inside ``root`` or equal it (also when spelled in another case on a
    file system that ignores case)?"""
    p = Path(path).expanduser().resolve()
    r = Path(root).expanduser().resolve()
    if p == r or r in p.parents:
        return True
    # APFS and NTFS ignore case, and resolve() keeps the spelling it was given: ".../casedir/data" names the folder
    # ".../CaseDir/Data" too (review 5 P62-2). The existing ancestors are compared as files (device + inode).
    try:
        rs = r.stat()
    except OSError:
        return False
    for a in (p, *p.parents):
        try:
            st = a.stat()
        except OSError:
            continue
        if (st.st_dev, st.st_ino) == (rs.st_dev, rs.st_ino):
            return True
    return False


def join_inside(root: str | os.PathLike, rel: str) -> Path:
    """``root/rel``; ValueError if ``rel`` is not a safe relative name or the result leaves ``root``."""
    why = relative_problem(rel)
    if why is not None:
        raise ValueError(why)
    p = Path(root) / rel.replace('\\', '/')
    if not inside(p, root):
        raise ValueError(translate('safepath', 'the path leads outside the folder'))
    return p


_archive_cache: dict[tuple, bool] = {}


def _game_archive(path: Path) -> bool:
    """Is ``path`` the game's archive: a zip (also with the game's own end signature, ``datasource._open_zip``) whose
    directory names one of the engine's file types (only the zip's directory is read; cached by path, size and
    time)?"""
    try:
        st = path.stat()
    except OSError:
        return False
    key = (str(path), st.st_size, st.st_mtime_ns)
    if key not in _archive_cache:
        found = False
        try:
            z = _open_zip(path)
        except (OSError, zipfile.BadZipFile, ValueError, EOFError):
            z = None
        if z is not None:
            try:
                found = any(_GAME_ENTRY.search(n) for n in z.namelist()[:20000])
            finally:
                z.close()
                z.fp_owner.close()
        _archive_cache[key] = found
    return _archive_cache[key]


def marks_game(folder: str | os.PathLike) -> bool:
    """Is ``folder`` a game folder: it holds ``Zax.exe`` (any edition, any build; any case), or a ``Data.dat`` that is
    the game's archive (``_game_archive``), or a ``Data.dat`` next to a language pack ``*.RED`` or next to the port's
    marker ``zax-data.bin`` (its imported copy)? A ``data.dat`` or a ``*.RED`` alone (another program's file, a pack
    on its own) does not make one (review 2026-11-21, E4)."""
    folder = Path(folder)
    try:
        names = {n.lower(): n for n in os.listdir(folder)}
    except OSError:
        return False
    if 'zax.exe' in names:
        return True
    if 'data.dat' not in names:
        return False
    if PORT_MARKER in names or any(n.endswith(PACK_SUFFIX) for n in names):
        return True
    return _game_archive(folder / names['data.dat'])



def is_game_data(path: str | os.PathLike, roots=()) -> bool:
    """Is ``path`` (a file or folder, existing or not) part of a game installation: inside one of ``roots`` (the
    configured game data, the gamedata folder of the workspace) or in or below a game folder (``marks_game``; an
    unpacked ``Data/`` lies in such a folder)?"""
    p = Path(path).expanduser().resolve()
    for r in roots:
        if r and inside(p, r):
            return True
    return (p.is_dir() and marks_game(p)) or any(marks_game(f) for f in p.parents)


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
