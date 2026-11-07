"""The level header (``CLayerSaveData``, the root of a ``.zax``) for a settings view: which fields belong
together, which ones the game never reads, the Team Info entries and the music.

Everything works on the text tree (``Level.root``), so a change rewrites only its own line; unknown and
run-time fields stay untouched.

Field registration and groups: ``zax-decomp/reimpl/src/layer.cpp`` (``SaveData_RegisterFields``, the exe's own group
prefixes "Game Type/", "Listener Settings/", "Team/", "Mini-Map/", "Debug/"), kept in the schema as
``group`` (``zaxtools.exeschema``).
"""
from __future__ import annotations

from . import textformat as tf
from .datasource import DataSource
from .i18n import QT_TRANSLATE_NOOP
from .level import Level

# (id, title, fields in display order). The titles are shown translated (translate('header', title)).
GROUPS = [
    ('general', QT_TRANSLATE_NOOP('header', 'General'),
     ['Map Description', 'Partial File Name', 'Width', 'Height', 'First Load Action', 'First Fire Action',
      'Custom Map Properties']),
    ('music', QT_TRANSLATE_NOOP('header', 'Music'), ['Music Mix']),
    ('team', QT_TRANSLATE_NOOP('header', 'Team Info (start points)'), ['Team Info']),
    ('game', QT_TRANSLATE_NOOP('header', 'Game types'),
     ['Default Game Type', 'Allowable Games', 'Suggested Num Players', 'Max Players']),
    ('sound', QT_TRANSLATE_NOOP('header', 'Sound (Listener Settings)'),
     ['Environment Type', 'Environment Size', 'Rolloff', 'Ambient Sounds']),
    ('minimap', QT_TRANSLATE_NOOP('header', 'Mini map'),
     ['Disable Mini-Map', 'MiniMap X Scale', 'MiniMap X Offset', 'MiniMap Y Scale', 'MiniMap Y Offset',
      'Left Mini-Map Clipping', 'Top Mini-Map Clipping', 'Right Mini-Map Clipping', 'Bottom Mini-Map Clipping']),
    ('state', QT_TRANSLATE_NOOP('header', 'Saved run-time state (leave unchanged)'),
     ['Has Begin Been Called', 'View Position', 'Int View Position', 'Shake Time', 'Max Shake Time',
      'Last Shake Delta', 'Pixels To Shake']),
]
OTHER = ('other', QT_TRANSLATE_NOOP('header', 'Other fields'))

# Blocks that have editors of their own (objects, ground, mini map) or are caches the game rebuilds
# (way points, paths, fog of war): not shown in the settings view.
HIDDEN = {'Tree List', 'Plasma Ground', 'Path Data', 'Active Paths', 'Fog Of War', 'Monitor', 'Action Queue',
          'Mini Map'}

# Shown but not editable here: the size goes with the ground grid (Plasma Ground), the name with the file's
# place below Levels/ (the editor sets it when it creates a level).
READ_ONLY = {
    'Width': QT_TRANSLATE_NOOP('header', 'The ground grid (Plasma Ground) has the size of the level; changing '
                                         'the size is not supported here.'),
    'Height': QT_TRANSLATE_NOOP('header', 'The ground grid (Plasma Ground) has the size of the level; changing '
                                          'the size is not supported here.'),
    'Partial File Name': QT_TRANSLATE_NOOP('header', 'The level\'s path below Levels/ without extension; it '
                                                     'belongs to the file\'s place and is set when the level is '
                                                     'created.'),
}

# Fields the retail exe never reads (zax-decomp/docs/ORIGINAL_BUGS.md 1.6, 1.17; zaxtools/levelcheck.py)
NO_EFFECT = {
    'Disable Mini-Map': QT_TRANSLATE_NOOP('header', 'No effect in the game: the game shows the mini map also with '
                                                    '1, no code reads the field (CLayerSaveData +0x168, '
                                                    'zax-decomp/docs/ORIGINAL_BUGS.md 1.6).'),
    'Environment Type': QT_TRANSLATE_NOOP('header', 'No effect in the game: the setter 0x4e6c20 passes the type '
                                                    'to the empty function 0x4186e0 (zax-decomp/docs/ORIGINAL_BUGS.md '
                                                    '1.17).'),
    'Environment Size': QT_TRANSLATE_NOOP('header', 'No effect in the game: the setter 0x4e6c80 stores 0x7136f0, '
                                                    'which no instruction reads (zax-decomp/docs/ORIGINAL_BUGS.md 1.17).'),
    'Rolloff': QT_TRANSLATE_NOOP('header', 'No effect in the game: the setter 0x4e6c50 stores 0x713698, which '
                                           'only the never reached debug drawing of CAmbientSoundAI reads '
                                           '(zax-decomp/docs/ORIGINAL_BUGS.md 1.17). The editor\'s AI overlays use it for '
                                           'the ambient sound fall-off.'),
}

# Our explanations of the mini map mapping (the exe has no help texts for them) [confirmed: docs/FORMATS.md 5,
# mini maps; 0x4ec3c0; zaxtools/minimap.py]
_MAPPING = QT_TRANSLATE_NOOP('header', 'Mapping of the world onto the mini map (176 × 121): mini map x = world x · '
                                       'X Scale + X Offset, y likewise. With a Scale of 0 (42 of 112 levels) the '
                                       'game computes the mapping itself from the visible area (level without '
                                       'the clipping margins). The editor sets it for new levels and uses it when '
                                       'it draws the mini map.')
MINIMAP_HELP = {k: _MAPPING for k in ('MiniMap X Scale', 'MiniMap X Offset', 'MiniMap Y Scale', 'MiniMap Y Offset')}

# Our explanations of the Team Info fields (the exe has no help texts for them) [confirmed: code,
# zax-decomp/reimpl/src/world_class.cpp World::MoveToTeamSpawn 0x4f4950, team_landscape.cpp CTeamInfo]
TEAM_HELP = {
    'Spawn Point Name': QT_TRANSLATE_NOOP('header', 'Start point of the team (Team Info index = team number) when '
                                                    'the game places a figure without a start point name, e.g. '
                                                    'the “Select Map” dialog (F9).'),
    'Re-Spawn Point Name': QT_TRANSLATE_NOOP('header', 'Start point instead of Spawn Point Name when the figure\'s '
                                                       'player was placed before (when not empty; the multiplayer '
                                                       'levels use “random”).'),
    'Model Type': QT_TRANSLATE_NOOP('header', 'A name of the model list (resource field). All 112 original levels '
                                              'have “!Unknown Model”.'),
}

# The music fields: file names relative to Music/ with extension, from the music folder list 0x6c0f10,
# which the game fills from "Music/" with the extensions wav and ogg (subfolders included) [confirmed:
# zax-decomp/reimpl/src/app_start.cpp 0x4a0a60/0x4a0a30 "Music/", "wav", "ogg"; music.cpp; CRules "Startup Song"
# game_types.cpp]
MUSIC_FOLDER = 'Music/'
MUSIC_EXTENSIONS = ('.wav', '.ogg')
MUSIC_FIELDS = {('CMusicMixerData', 'Full Mix Song'), ('CMusicMixerData', 'Med Mix Song'),
                ('CMusicMixerData', 'Ambiant Song'), ('CRules', 'Startup Song')}
SONG_KEYS = ('Full Mix Song', 'Med Mix Song', 'Ambiant Song')
# "Num Seconds To Switch" of a new Music Mix: 3 like 73 of the 102 original levels with music and
# zaxtools.newlevel (the exe's default is 5)
NEW_MIX_SECONDS = '3'


def music_names(ds: DataSource) -> list[str]:
    """The names of the music folder list as the levels write them ("Jungle/01- Jungle 01.ogg")."""
    names = {f[len(MUSIC_FOLDER):] for ext in MUSIC_EXTENSIONS for f in ds.list(MUSIC_FOLDER, ext)}
    return sorted(names, key=str.lower)


def is_music_name(names: list[str], value: str) -> bool:
    low = value.lower()
    return any(n.lower() == low for n in names)


def music_node(songs: tuple[str, str, str], seconds: str = NEW_MIX_SECONDS) -> tf.Node:
    """A new ``Music Mix=CMusicMixerData`` block (field order of the exe's registration)."""
    return tf.Node('Music Mix', 'CMusicMixerData', [tf.Entry('Num Seconds To Switch', seconds)] +
                   [tf.Entry(k, s) for k, s in zip(SONG_KEYS, songs)])


def layout(root: tf.Node) -> list[tuple[str, str, list[tf.Entry | tf.Node]]]:
    """The header's items by group (``GROUPS`` order, then ``OTHER`` for fields of no group); hidden
    blocks and raw lines left out. Groups without items are omitted."""
    by_key: dict[str, list] = {}
    for c in root.children:
        if not isinstance(c, tf.Raw):
            by_key.setdefault(c.key, []).append(c)
    out, used = [], set(HIDDEN)
    for gid, title, keys in GROUPS:
        items = [it for k in keys for it in by_key.get(k, [])]
        used.update(keys)
        if items:
            out.append((gid, title, items))
    rest = [c for c in root.children if not isinstance(c, tf.Raw) and c.key not in used]
    if rest:
        out.append((OTHER[0], OTHER[1], rest))
    return out


# --- Team Info ------------------------------------------------------------------------------------------
def team_infos(level: Level) -> list[tf.Node]:
    """The ``CTeamInfo`` elements of the header's ``Team Info`` array (index = team number)."""
    arr = level.root.block('Team Info')
    if arr is None:
        return []
    return [c for c in arr.children if isinstance(c, tf.Node) and c.key == 'Team Info']


def spawn_name_state(names: list[str], value: str) -> str:
    """'found' (an object of that exact name), 'spaces' (only after removing blanks at the ends, e.g.
    the shipped ``First Map Spawn Point=Game Start ``), 'empty' or 'missing'."""
    if not value.strip():
        return 'empty'
    if value in names:
        return 'found'
    if value.strip() in [n.strip() for n in names]:
        return 'spaces'
    return 'missing'
