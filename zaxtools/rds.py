"""Dialogue scripts ``.RDS``: lossless reading/writing and the game's view of them.

The game reads a script as a property list (``CPropertyList``, docs/FORMATS.md 3) [confirmed: code,
zax-decomp/reimpl/src/ai_triggers.cpp ``PropertyList_Load`` 0x41e0f0]:

* The file is opened in memory (``CFileBuf`` flag 0x204 -> ``MemoryStream``) and read line by line with
  ``MemoryStream_ReadLine`` 0x506140: a line runs up to the next CR (a lone LF stays part of the line),
  then one CR and one LF are skipped; the last line needs no line end. A line of 3,999 bytes or more
  ends the reading (the rest of the file is ignored).
* The list starts with an item ``!None`` (index 0). ``:Name`` starts a new item (the name is the rest
  of the line, not trimmed); ``//`` lines are skipped; every other line is appended to the current
  item's text with ``\\n`` (lines before the first ``:`` line are dropped). When the next item starts
  and at the end the text loses its trailing white space (``ZString::TrimRight`` 0x4e0f20). Blank
  lines therefore separate nothing: they only add ``\\n`` that the trim removes.
* ``CZaxDialogAction`` names a script (``Script=``, path below ``Levels/`` without ``.RDS``) and an item
  (``Line=``). ``CZaxDialogAction::SplitLine`` 0x5a4bd0 splits the text at the first ``": "`` if it lies
  within the first 20 characters (speaker, the rest left-trimmed), else the whole text is the line and
  the speaker is empty. The dialogue window trims the speaker and shows ``???`` for an empty one
  (``DialogueWindow_AddLine`` 0x47cd20); its portrait is the sequence
  ``Dialog Display/Dialog Window Frame/Portraits/<speaker> Portrait`` of the list "Inventory Frames"
  (``Inventory/Frames``), else ``!Unknown Portrait`` (0x47ccc0); the lookup falls back to the file name
  (``ZNamedList::FindFileName`` 0x591ac0), so the files lie in ``Dialog Display/Portraits/``.
* The voice of a line is the sound ``<item name>.wav`` of the list "Voiceovers" (all ``.wav``/``.ogg``
  below ``Levels``, sorted, ``SoundList_Load`` 0x57e2f0); a missing ``.wav`` is looked up as ``.ogg``
  (``SoundList_Find`` 0x57e690). The full name never matches (the records carry their folder), so the
  file name decides (0x591ac0): the first file of that name in the sorted list, in any folder
  (``CZaxDialogAction`` slot 29 0x41d830, precache 0x5a4c90).

``Script`` keeps every byte (line ends as found, preamble, comments, blank lines), so an unchanged
script is written back byte for byte; edits change only the lines of the item concerned.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

NONE_ITEM = '!None'          # item 0 of every property list (0x60b0a0)
READ_LIMIT = 0xfa0           # line buffer of PropertyList_Load; a line needs length + 1 < READ_LIMIT
SPEAKER_LIMIT = 0x14         # ": " must start before this many characters (SplitLine)
UNKNOWN_SPEAKER = '???'      # 0x611084
PORTRAIT_FOLDER = 'Cache/Inventory/Frames'
PORTRAIT_UNKNOWN = '!Unknown'
EOL = '\r\n'                 # what the editor writes (all shipped scripts use CRLF)
_WS = ' \t\r\n\v\f'


@dataclass
class Line:
    text: str                 # without the line end (may contain a lone LF, see the module text)
    end: str = EOL            # '\r\n', '\r' or '' (last line of the file)


@dataclass
class Item:
    """A ``:Name`` line and the lines below it up to the next ``:`` line."""
    name: str
    end: str = EOL
    body: list[Line] = field(default_factory=list)

    def text(self) -> str:
        """The item's text as the game builds it (comments skipped, lines joined with ``\\n``, trimmed)."""
        return ''.join(l.text + '\n' for l in self.body if not l.text.startswith('//')).rstrip(_WS)

    def _split(self) -> tuple[list[Line], list[Line], list[Line]]:
        """(comment lines among the text, text lines, blank lines after the last text line)."""
        last = max((i for i, l in enumerate(self.body) if l.text.strip(_WS) and not l.text.startswith('//')),
                   default=-1)
        head = self.body[:last + 1]
        return ([l for l in head if l.text.startswith('//')], [l for l in head if not l.text.startswith('//')],
                self.body[last + 1:])


class Script:
    def __init__(self, preamble: list[Line] | None = None, items: list[Item] | None = None, rest: bytes = b''):
        self.preamble = preamble or []
        self.items = items or []
        self.rest = rest          # bytes the game no longer reads (after a too long line), kept as they are

    # --- reading / writing ---------------------------------------------------------------------
    @classmethod
    def loads(cls, data: bytes) -> 'Script':
        s = cls()
        cur = None
        for line, raw_rest in _lines(data):
            if raw_rest is not None:
                s.rest = raw_rest
                break
            if line.text.startswith(':'):
                cur = Item(line.text[1:], line.end)
                s.items.append(cur)
            elif cur is None:
                s.preamble.append(line)
            else:
                cur.body.append(line)
        return s

    def dumps(self) -> bytes:
        out = [l.text + l.end for l in self.preamble]
        for it in self.items:
            out.append(':' + it.name + it.end)
            out.extend(l.text + l.end for l in it.body)
        return ''.join(out).encode('latin-1') + self.rest

    # --- the game's view ---------------------------------------------------------------------------
    def game_items(self) -> list[tuple[str, str]]:
        """(name, text) of the property list as the game builds it, item 0 ``!None`` included."""
        return [(NONE_ITEM, '')] + [(it.name, it.text()) for it in self.items]

    def find(self, name: str) -> Item | None:
        """The item the game takes for ``Line=name``: the first of that name, any case [assumption: the
        list's Find compares like ``_stricmp`` in file order; all 646 dialogue actions of the originals
        find their item exactly]."""
        low = name.lower()
        return next((it for it in self.items if it.name.lower() == low), None)

    def labels(self) -> list[str]:
        return [it.name for it in self.items]

    # --- editing -------------------------------------------------------------------------------------
    def set_text(self, name: str, text: str) -> None:
        """Replace the item's text lines; its comments stay in front, the blank lines after it stay."""
        it = self.find(name)
        if it is None:
            raise KeyError(name)
        comments, old, tail = it._split()
        lines = [Line(t) for t in _text_lines(text)]
        if lines and not tail and old and old[-1].end == '':
            lines[-1].end = ''        # the file ended without a line end: keep it so
        it.body = comments + lines + tail

    def add(self, name: str, text: str = '') -> Item:
        """Append an item as the shipped scripts write them: ``:Name``, the text, a blank line."""
        check_name(name)
        if self.find(name) is not None:
            raise ValueError(f'label exists: {name}')
        if self.items:
            prev = self.items[-1]
            tail = prev.body[-1] if prev.body else None
            if tail is None:
                if prev.end == '':
                    prev.end = EOL
            elif tail.end == '':
                tail.end = EOL
            if not prev.body or prev.body[-1].text.strip(_WS):
                prev.body.append(Line(''))          # blank line between the items
        elif self.preamble and self.preamble[-1].end == '':
            self.preamble[-1].end = EOL
        it =Item(name, EOL, [Line(t) for t in _text_lines(text)] + [Line('')])
        self.items.append(it)
        return it

    def rename(self, old: str, new: str) -> None:
        check_name(new)
        it = self.find(old)
        if it is None:
            raise KeyError(old)
        other = self.find(new)
        if other is not None and other is not it:
            raise ValueError(f'label exists: {new}')
        it.name = new

    def remove(self, name: str) -> None:
        it = self.find(name)
        if it is None:
            raise KeyError(name)
        self.items.remove(it)


def check_name(name: str) -> None:
    """A label the game reads back as written: one line, no CR/LF, not empty."""
    if not name or '\r' in name or '\n' in name:
        raise ValueError('a label is one non-empty line')
    if len(name) + 2 >= READ_LIMIT:
        raise ValueError('label too long')


def _text_lines(text: str) -> list[str]:
    """Text (``\\n`` between lines) -> file lines; trailing blank lines dropped (the game trims them)."""
    text = text.replace('\r\n', '\n').replace('\r', '\n').rstrip(_WS)
    return text.split('\n') if text else []


def _lines(data: bytes):
    """(Line, None) per line as ``MemoryStream_ReadLine`` 0x506140 splits them; (None, rest) once a line
    is too long for the game's buffer (the rest is kept as bytes)."""
    pos, n = 0, len(data)
    while pos < n:
        cr = data.find(b'\r', pos)
        stop = n if cr < 0 else cr
        if stop - pos + 1 >= READ_LIMIT:
            yield None, data[pos:]
            return
        text = data[pos:stop].decode('latin-1')
        p = stop
        if p < n and data[p] == 0x0d:
            p += 1
        if p < n and data[p] == 0x0a:
            p += 1
        yield Line(text, data[stop:p].decode('latin-1')), None
        pos = p


def loads(data: bytes) -> Script:
    return Script.loads(data)


# --- Speakers, portraits, voices -------------------------------------------------------------------

def split_line(text: str) -> tuple[str, str]:
    """(speaker, line) as ``CZaxDialogAction::SplitLine`` 0x5a4bd0: at the first ``": "`` when it starts
    within the first 20 characters; otherwise ('', text)."""
    i = text.find(': ')
    if 0 <= i < SPEAKER_LIMIT:
        return text[:i], text[i + 2:].lstrip(_WS)
    return '', text


def shown_speaker(speaker: str) -> str:
    """The speaker as the dialogue window shows it (trimmed, ``???`` when empty)."""
    return speaker.strip(_WS) or UNKNOWN_SPEAKER


def voice_name(label: str) -> str:
    return f'{label}.wav'


class Resources:
    """Voice files and portraits as the game finds them, from a ``DataSource`` plus optional folders on
    disk laid out like ``Data`` that win (the output folder: files below ``Data/`` win in the game)."""

    def __init__(self, ds, extra_roots=()):
        self.ds = ds
        self.extra_roots = [r for r in extra_roots if r]
        self._voices: dict[str, str] | None = None
        self._portraits: dict[str, str] | None = None

    def _all(self, folder: str) -> list[str]:
        out = {f.lower(): f for f in self.ds.list(folder + '/', '')}
        for root in self.extra_roots:
            base = root / folder
            if base.is_dir():
                for p in base.rglob('*'):
                    if p.is_file():
                        rel = p.relative_to(root).as_posix()
                        out.setdefault(rel.lower(), rel)
        return list(out.values())

    def voices(self) -> dict[str, str]:
        """File name (lower case) -> path, the first in the game's order (sorted below ``Levels``)."""
        if self._voices is None:
            files = [f for f in self._all('Levels') if f.lower().endswith(('.wav', '.ogg'))]
            files.sort(key=lambda f: f[len('Levels/'):].lower())
            self._voices = {}
            for f in files:
                self._voices.setdefault(f.rsplit('/', 1)[-1].lower(), f)
        return self._voices

    def voice(self, label: str) -> str | None:
        """Path of the voice file of the item (``.wav`` first, then ``.ogg``) or None."""
        v = self.voices()
        return v.get(f'{label}.wav'.lower()) or v.get(f'{label}.ogg'.lower())

    def portraits(self) -> dict[str, str]:
        """Portrait name without ``Portrait`` (lower case) -> path."""
        if self._portraits is None:
            self._portraits = {}
            for f in sorted(self._all(PORTRAIT_FOLDER), key=str.lower):
                stem = f.rsplit('/', 1)[-1]
                stem = stem.rsplit('.', 1)[0] if '.' in stem else stem
                if stem.lower().endswith(' portrait') and f.lower().endswith(('.frm16', '.frm')):
                    self._portraits.setdefault(stem[:-len(' portrait')].lower(), f)
        return self._portraits

    def portrait(self, speaker: str) -> str | None:
        """Path of the speaker's portrait or None (the game then shows ``!Unknown Portrait``)."""
        return self.portraits().get(shown_speaker(speaker).lower())


def find_file(root: Path, rel: str) -> Path | None:
    """``root/rel`` with the path compared without case (as the game on Windows), or None."""
    p = Path(root)
    for part in rel.split('/'):
        if not p.is_dir():
            return None
        q = p / part
        if not q.exists():
            low = part.lower()
            q = next((c for c in p.iterdir() if c.name.lower() == low), None)
            if q is None:
                return None
        p = q
    return p if p.is_file() else None


def read_script(ds, script: str, extra_roots=()) -> tuple[bytes, str] | None:
    """(bytes, source) of ``Levels/<script>.RDS``: from the first extra root that has it (source = the file
    path), else from the game data (source ``'pack'`` when the language pack supplies it, else ``'data'``);
    None if it is missing."""
    rel = f'Levels/{script}.RDS'
    for root in extra_roots:
        if root:
            p = find_file(root, rel)
            if p is not None:
                return p.read_bytes(), str(p)
    if ds.exists(rel):
        in_pack = getattr(ds, 'in_pack', None)
        return ds.read(rel), 'pack' if in_pack is not None and in_pack(rel) else 'data'
    return None
