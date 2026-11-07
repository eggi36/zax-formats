"""Access to the game data.

The game loads everything either from a folder ``Data`` or from ``Data.dat`` (an uncompressed
zip file with the same content; the game's Data.dat carries the signature ``RE\\5\\6`` instead of
``PK\\5\\6`` at the end of the central directory, see ``_ZipSignatureFile``). Paths in the game files
are resolved case-insensitively on Windows (e.g. the .zax says ``Act 1/M1m2/01 Main``, the folder
is called ``ACT 1/M1M2``). This class reproduces that so the code also works on Linux/macOS.

All paths are relative to the folder ``Data`` and use ``/``.

Optionally a language pack (``GERMAN.RED`` of the German edition: zip with translated ``.RDS``,
voice recordings, ``Local.txt``). The game mounts ``*.RED`` after ``Data.dat``; entries of the
``.RED`` with the same name win [verified, docs/FORMATS.md 1]. Here the language pack also wins
against a folder ``Data``: that counts as an unpacked ``Data.dat`` (in the game, files on disk
would come before the ``.RED``).
"""
from __future__ import annotations

import os
import zipfile
from pathlib import Path


class DataSource:
    def __init__(self, root: str | os.PathLike, language_pack: str | os.PathLike | None = None):
        """``root``: the folder ``Data`` or the file ``Data.dat``/``Data.zip``.
        ``language_pack``: language pack (zip, e.g. ``GERMAN.RED``) whose entries win."""
        self.root = Path(root)
        self._zip = None
        self._index: dict[str, str] = {}
        self.language_pack = Path(language_pack) if language_pack else None
        self._pack = None
        self._pack_index: dict[str, str] = {}
        if self.root.is_file():
            self._zip = zipfile.ZipFile(_ZipSignatureFile(self.root))
            names = [n for n in self._zip.namelist() if not n.endswith('/')]
            prefix = _common_data_prefix(names)
            for n in names:
                if n.lower().startswith(prefix):
                    self._index[n[len(prefix):].lower()] = n
        elif self.root.is_dir():
            for dirpath, _, files in os.walk(self.root):
                for f in files:
                    full = Path(dirpath, f)
                    rel = full.relative_to(self.root).as_posix()
                    self._index[rel.lower()] = str(full)
        else:
            raise FileNotFoundError(f'game data not found: {self.root}')
        if self.language_pack is not None:
            self._pack = zipfile.ZipFile(_ZipSignatureFile(self.language_pack))
            names = [n for n in self._pack.namelist() if not n.endswith('/')]
            prefix = _common_data_prefix(names)
            for n in names:
                if n.lower().startswith(prefix):
                    self._pack_index[n[len(prefix):].lower()] = n

    @staticmethod
    def check_language_pack(path: str | os.PathLike) -> int:
        """Number of entries; ValueError if the file is not a zip."""
        f = _ZipSignatureFile(Path(path))
        try:
            return len(zipfile.ZipFile(f).namelist())
        except zipfile.BadZipFile as e:
            raise ValueError(str(e)) from e
        finally:
            f.close()

    # ------------------------------------------------------------------
    def resolve(self, rel: str) -> str | None:
        """Actual name in the game data (zip entry or file path) or None; the language pack does
        not count here (see ``in_pack``)."""
        return self._index.get(_key(rel))

    def in_pack(self, rel: str) -> bool:
        """Does the file come from the language pack?"""
        return _key(rel) in self._pack_index

    def exists(self, rel: str) -> bool:
        return self.in_pack(rel) or self.resolve(rel) is not None

    def read(self, rel: str) -> bytes:
        if self.in_pack(rel):
            return self._pack.read(self._pack_index[_key(rel)])
        name = self.resolve(rel)
        if name is None:
            raise FileNotFoundError(rel)
        if self._zip is not None:
            return self._zip.read(name)
        return Path(name).read_bytes()

    def size(self, rel: str) -> int:
        """Size of a file in bytes (the language pack's entry if it has one)."""
        if self.in_pack(rel):
            return self._pack.getinfo(self._pack_index[_key(rel)]).file_size
        name = self.resolve(rel)
        if name is None:
            raise FileNotFoundError(rel)
        if self._zip is not None:
            return self._zip.getinfo(name).file_size
        return os.stat(name).st_size

    def list(self, prefix: str = '', suffix: str = '') -> list[str]:
        """Relative paths (in original spelling) below ``prefix`` with extension ``suffix``."""
        p, s = prefix.lower().replace('\\', '/'), suffix.lower()
        out = {}
        for low, name in self._index.items():
            if low.startswith(p) and low.endswith(s):
                out[low] = self._original_rel(name)
        for low, name in self._pack_index.items():
            if low.startswith(p) and low.endswith(s) and low not in out:
                out[low] = name[len(_common_data_prefix([name])):]
        return sorted(out.values())

    def _original_rel(self, name: str) -> str:
        if self._zip is not None:
            prefix = _common_data_prefix([name])
            return name[len(prefix):] if name.lower().startswith(prefix) else name
        return Path(name).relative_to(self.root).as_posix()


class _ZipSignatureFile:
    """Read-only file that returns a signature ``RE\\5\\6`` at the end of the central directory
    as ``PK\\5\\6``.

    Zax.exe accepts both signatures; Python's ``zipfile`` only ``PK``. The file on disk stays
    unchanged. Without an ``RE`` signature the bytes are passed through unchanged.
    """

    _SEARCH_RANGE = 22 + 0xFFFF  # end record + largest comment

    def __init__(self, path: Path):
        self._f = open(path, 'rb')
        self._patch_at = -1
        size = self._f.seek(0, os.SEEK_END)
        start = max(0, size - self._SEARCH_RANGE)
        self._f.seek(start)
        tail = self._f.read()
        # The last end record counts; only replace if no PK end record follows it.
        re_pos, pk_pos = tail.rfind(b'RE\x05\x06'), tail.rfind(b'PK\x05\x06')
        if re_pos >= 0 and re_pos > pk_pos and len(tail) - re_pos >= 22:
            self._patch_at = start + re_pos
        self._f.seek(0)

    def read(self, n: int = -1) -> bytes:
        pos = self._f.tell()
        data = self._f.read(n)
        a = self._patch_at
        if a >= 0 and pos < a + 2 and pos + len(data) > a:
            buf = bytearray(data)
            for i, b in enumerate(b'PK'):
                j = a + i - pos
                if 0 <= j < len(buf):
                    buf[j] = b
            data = bytes(buf)
        return data

    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        return self._f.seek(offset, whence)

    def tell(self) -> int:
        return self._f.tell()

    def seekable(self) -> bool:
        return True

    def close(self) -> None:
        self._f.close()


def _key(rel: str) -> str:
    return rel.replace('\\', '/').lstrip('/').lower()


def _common_data_prefix(names: list[str]) -> str:
    """Zip entries usually start with ``Data/``; this prefix is removed."""
    if names and all(n.lower().startswith('data/') for n in names[:50]):
        return 'data/'
    return ''
