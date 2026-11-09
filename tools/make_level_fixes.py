"""Build the level fix pack from the player's own game data: docs/LEVEL_BUGS.md, the entries marked "in the pack".

    python tools/make_level_fixes.py "<game folder>" -o LevelFixes.RED

The pack holds whole levels, so it is made on the player's machine and never shipped; only these few edits are in the repository.
Every edit is checked against the text it expects and the run stops if it differs, so no level is changed by guesswork.

Put LevelFixes.RED beside the game: the original Zax.exe and the port both mount it for as long as it lies there. The port's launcher
lists it on its Packs page, where it can be unticked.
"""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from zaxtools.datasource import DataSource  # noqa: E402

ALL_MODES = b'MultiPlayer/Capture The Flag,MultiPlayer/Death Match,MultiPlayer/Salvage King,QuestMode'


class EditError(Exception):
    pass


def part_of(text: bytes, marker: bytes) -> tuple[int, int]:
    """The level part whose body holds marker exactly once in the level"""
    if text.count(marker) != 1:
        raise EditError(f'expected {marker!r} once, found {text.count(marker)}')
    at = text.index(marker)
    start = text.rindex(b'Level Part=', 0, at)
    end = text.find(b'Level Part=', at)
    return start, len(text) if end < 0 else end


def fix_valeth_cave(text: bytes) -> bytes:
    """L.1: the first step of the cave spawn's series also succeeds when its targets are already active"""
    start, end = part_of(text, b'\t\t\tName=Spawn Point Cave\r\n')
    part = text[start:end]
    target = b'Target Name=shut gate, ore path\r\n'
    if part.count(target) != 1:
        raise EditError('the series of Spawn Point Cave has changed')
    at = part.index(target)
    count = part.rindex(b'Item Count=1\r\n', 0, at)
    line_start = part.rindex(b'\n', 0, part.rindex(b'Action=CActivateAction', 0, at)) + 1
    indent = part[line_start:part.index(b'Action=', line_start)]
    close = part.index(b'\r\n' + indent + b'}\r\n', at) + len(indent) + 5
    added = indent + b'Action=CSucceedAction\r\n' + indent + b'{\r\n' + indent + b'\tAction=\r\n' + indent + b'}\r\n'
    part = part[:count] + b'Item Count=2\r\n' + part[count + 14:close] + added + part[close:]
    return text[:start] + part + text[end:]


def fix_expired_sign(text: bytes) -> bytes:
    """L.7: the sign of the Expired Zone shows in every game mode"""
    start, end = part_of(text, b'Text=You have been transported to another dimension')
    part = text[start:end]
    old = b'Used In=MultiPlayer/Salvage King\r\n'
    if part.count(old) != 1:
        raise EditError('the sign of the Expired Zone has changed')
    return text[:start] + part.replace(old, b'Used In=' + ALL_MODES + b'\r\n') + text[end:]


EDITS = [
    ('Levels/ACT 1/M1M2/01 Main.zax', fix_valeth_cave),
    ('Levels/Expired Error.zax', fix_expired_sign),
]


def build(data: DataSource, out: Path) -> list[str]:
    done = []
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_STORED) as z:
        for rel, edit in EDITS:
            info = zipfile.ZipInfo(rel, date_time=(2001, 8, 1, 0, 0, 0))
            z.writestr(info, edit(data.read(rel)))
            done.append(rel)
    return done


def game_archive(game: Path) -> Path:
    """The base archive of a game folder, in any case; a file is taken as it is"""
    if game.is_file():
        return game
    for f in game.iterdir():
        if f.name.lower() in ('data.zip', 'data.dat'):
            return f
    sys.exit(f'No Data.dat in {game}')


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('game', type=Path, help='the game folder with DATA.dat')
    p.add_argument('-o', '--output', type=Path, default=Path('LevelFixes.RED'))
    a = p.parse_args()
    try:
        for rel in build(DataSource(game_archive(a.game)), a.output):
            print('fixed', rel)
    except EditError as e:
        a.output.unlink(missing_ok=True)
        print(f'This game data differs from what the fixes expect: {e}. Nothing was written.', file=sys.stderr)
        return 1
    print('written', a.output)
    return 0


if __name__ == '__main__':
    sys.exit(main())
