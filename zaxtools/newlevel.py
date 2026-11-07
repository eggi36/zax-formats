"""Create a new, empty level (without a template level).

The header data (class ``CLayerSaveData``) comes from two sources:

- Fixed values: fields that are equal in the original levels. Structure and order as in 71 of
  112 levels (the rest differ only in single fields, e.g. without music or with a start
  script) [verified]. The exe provides no default values for this class.
- User input: name/location, size, music, environment, description, ground textures.

Added are a start point "Game Start" in the middle (minimal object as in the test level,
verified in the game) and a uniform ground. The mini map mapping is set so that the whole level
fits centred into 176 x 121 pixels (see ``minimap_mapping``).
"""
from __future__ import annotations

import math

import numpy as np

from .i18n import QT_TRANSLATE_NOOP
from .level import GRID_CELL, Level
from .minimap import SIZE
from .render import band_start

# environment types (reverb of the sounds, EAX presets), order as in the exe
# [verified: string table of Zax.exe; the levels use 8 of them]
ENVIRONMENTS = ['Generic', 'Padded Cell', 'Room', 'Bathroom', 'Living Room', 'Stone Room',
                'Auditorium', 'Concert Hall', 'Cave', 'Arena', 'Hangar', 'Carpeted Hallway',
                'Hallway', 'Stone Corridor', 'Alley', 'Forest', 'City', 'Mountains', 'Quarry',
                'Plain', 'Parking Lot', 'Sewer Pipe', 'Under Water', 'Drugged', 'Dizzy', 'Psychotic']

# music: (name, Full Mix, Med Mix, Ambiant) - the combinations of the original levels, by
# frequency [verified]; paths below Music/. The name is only shown (translated: translate('newlevel', name)).
MUSIC = [
    (QT_TRANSLATE_NOOP('newlevel', 'Caves'), 'Caves/Caves 01.ogg', 'Caves/Caves 02.ogg', 'Caves/Caves 03.ogg'),
    (QT_TRANSLATE_NOOP('newlevel', 'Jungle'), 'Jungle/01- Jungle 01.ogg', 'Jungle/02- Jungle 02.ogg',
     'Jungle/01- Jungle 03.ogg'),
    (QT_TRANSLATE_NOOP('newlevel', 'Hydroelectric plant'), 'Hydro/HydroPlant 01.ogg', 'Hydro/HydroPlant 02.ogg',
     'Temple/Temple 03.ogg'),
    (QT_TRANSLATE_NOOP('newlevel', 'Temple'), 'Temple/Temple 01.ogg', 'Temple/Temple 02.ogg', 'Temple/Temple 03.ogg'),
    (QT_TRANSLATE_NOOP('newlevel', 'North'), 'Northern/Northern 01.ogg', 'Northern/Northern 02.ogg',
     'Northern/Northern 03.ogg'),
    (QT_TRANSLATE_NOOP('newlevel', 'Mothership'), 'Om Ship/mothership 01.ogg', 'Om Ship/mothership 02.ogg',
     'Om Ship/mothership 03.ogg'),
]

DEFAULT_SIZE = 4097        # 62 of 112 levels are 4097 x 4097 [verified]
SPAWN_NAME = 'Game Start'  # as in Rules.txt (First Map Spawn Point)


def grid_shape(width: int, height: int) -> tuple[int, int]:
    """Grid points (rows, columns): ceil(size / 64) [verified on all 112 levels, including the 6
    where Width/64 + 1 does not fit]."""
    return math.ceil(height / GRID_CELL), math.ceil(width / GRID_CELL)


def minimap_mapping(width: int, height: int) -> tuple[float, float, float, float]:
    """(X Scale, X Offset, Y Scale, Y Offset): same scale for both axes, as large as possible so
    the level fits into 176 x 121, centred. The values of 01 Main are built like that (visible
    area 4196 x 3204: Y Scale = 121/3204, X Offset = (176 - 4196 * s)/2 = 9) [confirmed]. The
    game places the player marker with exactly these values."""
    w, h = SIZE
    s = min(w / width, h / height)
    return s, (w - width * s) / 2, s, (h - height * s) / 2


def _f(v: float) -> str:
    """Decimal number as in the levels (6 significant digits, without needless zeros)."""
    return f'{v:.6g}'


def new_level(partial: str, width: int, height: int, textures: list[str], ground: int = 0,
              music: tuple[str, str, str] | None = MUSIC[1][1:], environment: str = 'Generic',
              description: str = '') -> Level:
    """New level. ``partial`` = path below Levels/ without extension (``Partial File Name``),
    ``textures`` = ground textures (names below Cache/Textures), ``ground`` = index of the
    texture that covers the whole ground. ``music`` None = without music (like 10 levels)."""
    if not textures:
        raise ValueError('at least one ground texture needed')
    if '\\' in partial:
        raise ValueError('map paths only with / (as the exe expects)')
    cx, cy = width // 2, height // 2
    sx, ox, sy, oy = minimap_mapping(width, height)
    if music:
        mix = ['\tMusic Mix=CMusicMixerData', '\t{', '\t\tNum Seconds To Switch=3',
               f'\t\tFull Mix Song={music[0]}', f'\t\tMed Mix Song={music[1]}',
               f'\t\tAmbiant Song={music[2]}', '\t}']
    else:
        mix = ['\tMusic Mix=']
    lines = [
        'CLayerSaveData', '{',
        '\tCustom Map Properties=',
        *mix,
        f'\tWidth={width}', f'\tHeight={height}',
        '\tAction Queue=CActionQueue', '\t{', '\t\tItems=Array', '\t\t{', '\t\t\tItem Count=0', '\t\t}', '\t}',
        '\tSuggested Num Players=5',
        '\tMax Players=No Limit',
        '\tDefault Game Type=QuestMode',
        '\tAllowable Games=MultiPlayer/Capture The Flag,MultiPlayer/Death Match,MultiPlayer/Salvage King,QuestMode',
        '\tHas Begin Been Called=0',
        f'\tMap Description={description}',
        '\tFirst Fire Action=',
        '\tFirst Load Action=',
        f'\tEnvironment Type={environment}',
        '\tRolloff=5',
        '\tEnvironment Size=7.5',
        f'\tView Position={cx}.000000,{cy}.000000',
        f'\tInt View Position={cx},{cy}',
        f'\tPartial File Name={partial}',
        '\tTeam Info=Array', '\t{', '\t\tItem Count=1', '\t\tTeam Info=CTeamInfo', '\t\t{',
        f'\t\t\tSpawn Point Name={SPAWN_NAME}', '\t\t\tRe-Spawn Point Name=', '\t\t\tModel Type=!Unknown Model',
        '\t\t}', '\t}',
        '\tAmbient Sounds=Array', '\t{', '\t\tItem Count=0', '\t}',
        '\tShake Time=0',
        '\tMax Shake Time=0',
        '\tPixels To Shake=CLengthEnvelope', '\t{', '\t\tStart Value=0', '\t\tEnd Value=0', '\t\tSpeed=0',
        '\t\tEnding Behavior=Stop at end', '\t\tCurrent Value=0', '\t\tUsing Start=1', '\t\tDirection=1', '\t}',
        '\tLast Shake Delta=0.000000,0.000000',
        '\tActive Paths=',
        '\tPath Data=CWayPointMap', '\t{', '\t\tMinDistBetweenWayPoints=20', '\t\tMaxDistToConnect=39', '\t}',
        '\tFog Of War=CFrame(1,1,8)', '\t{', '\t\t01', '\t}',
        '\tMonitor=CUpdateMonitorList', '\t{', '\t\tMonitor List=Array', '\t\t{', '\t\t\tItem Count=0', '\t\t}', '\t}',
        '\tDisable Mini-Map=0',
        '\tLeft Mini-Map Clipping=Left UnClipped',
        '\tTop Mini-Map Clipping=Top UnClipped',
        '\tRight Mini-Map Clipping=Right UnClipped',
        '\tBottom Mini-Map Clipping=Bottom UnClipped',
        f'\tMiniMap X Offset={_f(ox)}', f'\tMiniMap X Scale={_f(sx)}',
        f'\tMiniMap Y Offset={_f(oy)}', f'\tMiniMap Y Scale={_f(sy)}',
        '\tTree List=CSortList2D', '\t{',
        # start point as a minimal object; the game fills in missing fields from the model [verified]
        '\t\tLevel Part=CEntityBase', '\t\t{', f'\t\t\tName={SPAWN_NAME}', '\t\t\tModel=Editor/Spawn Point',
        f'\t\t\tPosition X={cx}', f'\t\t\tPosition Y={cy}', '\t\t\tCur Sequence=Idle', '\t\t}',
        '\t}',
        '\tPlasma Ground=CPlasmaTileMap', '\t{',
        '\t\tBlending=1',               # most frequent value (39 levels); transition across the whole band
        f'\t\tNum Textures={len(textures)}',
        *[f'\t\tTexture {i}={t}' for i, t in enumerate(textures)],
    ]
    rows, cols = grid_shape(width, height)
    value = band_start(ground, len(textures))       # pure texture (render.blend_weight)
    lines += [f'\t\tElevations Row {r}={bytes([value] * cols).hex().upper()}' for r in range(rows)]
    lines += [f'\t\tSeeds Row {r}={"00" * cols}' for r in range(rows)]   # all 0 as in 17 levels
    lines += ['\t}', '}', '']
    return Level.from_bytes('\r\n'.join(lines).encode('latin-1'))
