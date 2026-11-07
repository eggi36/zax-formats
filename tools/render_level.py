"""Render a level as PNG.

Example:
    python tools/render_level.py --data "C:/Spiele/Zax/Data.dat" "Levels/ACT 1/M1M2/01 Main.zax" -o main.png --step 2
    python tools/render_level.py "Levels/ACT 1/M1M2/01 Main.zax" -o main.png --polygons --overlays trigger,patrol

--polygons draws the outlines of the collision areas (CFreeRangePoly, turquoise) and way point
polygons (CWayPointsPolygon, green) in the editor's colours, --overlays the AI overlays
(zaxtools.overlays; groups: trigger, spawn, sound, patrol, enemy, scan, area, or "all").
"""
import argparse
from pathlib import Path

from _common import data_arg, open_data
from zaxtools.catalog import Catalog
from zaxtools.exeschema import find_exe
from zaxtools.level import Level
from zaxtools import overlays as ov
from zaxtools.render import Assets, content_box, render_level

POLYGON_SWITCHES = {'free': 'CFreeRangePoly', 'way': 'CWayPointsPolygon', 'surface': 'CRenderablePolygon'}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    data_arg(p)
    p.add_argument('level', help='path relative to Data/, e.g. "Levels/ACT 1/M1M2/01 Main.zax"')
    p.add_argument('-o', '--out', default='level.png')
    p.add_argument('--step', type=int, default=2, help='1 = full resolution, 2 = half, ...')
    p.add_argument('--editor', action='store_true', help='also draw editor objects (Relay, Spawn Point, ...)')
    p.add_argument('--facing', action='store_true', help='use the angle the game draws with (Movement Angle, LevelPart.draw_angle), formula from Zax.exe')
    p.add_argument('--full', action='store_true', help='whole map area instead of only the occupied part')
    p.add_argument('--no-sort-y', action='store_true', help='ignore the models\' "Sorting Y" (sort by Position Y only)')
    p.add_argument('--cache', default=str(Path.home() / 'Library' / 'Caches' / 'Zax-Editor'),
                   help='folder for the model catalogue (as in the editor)')
    p.add_argument('--time', type=float, default=None, metavar='SECONDS',
                   help='animation state this many seconds after level start (default: the frame at level start)')
    p.add_argument('--polygons', nargs='?', const='free,way', default='', metavar='KINDS',
                   help='draw polygon outlines: free (CFreeRangePoly), way (CWayPointsPolygon), surface '
                        '(CRenderablePolygon), comma-separated; without a value free,way')
    p.add_argument('--overlays', default='', metavar='GROUPS',
                   help=f'draw the AI overlays of these groups ({", ".join(ov.GROUPS)} or all), comma-separated')
    a = p.parse_args()
    kinds = [k.strip() for k in a.polygons.split(',') if k.strip()]
    if bad := [k for k in kinds if k not in POLYGON_SWITCHES]:
        p.error(f'unknown polygon kind(s): {", ".join(bad)}')
    groups = list(ov.GROUPS) if a.overlays.strip() == 'all' else [g.strip() for g in a.overlays.split(',') if g.strip()]
    if bad := [g for g in groups if g not in ov.GROUPS]:
        p.error(f'unknown overlay group(s): {", ".join(bad)}')
    ds = open_data(a)
    lv = Level.from_bytes(ds.read(a.level))
    box = None if a.full else content_box(lv)
    assets = Assets(ds)
    exe = find_exe(ds)
    if not a.no_sort_y:
        if exe is None:
            print('Note: Zax.exe not found - objects sorted by Position Y only.')
        else:
            assets.sort_y = Catalog.open(ds, Path(a.cache), exe=exe).sorting_y()
    bounds = None
    if groups:
        if exe is None:
            print('Note: Zax.exe not found - overlays without the models\' bounds polygons.')
        else:
            bounds = model_bounds(ds, exe, Path(a.cache))
    img = render_level(lv, assets, box=box, step=a.step, show_editor=a.editor, use_facing=a.facing, t=a.time,
                       polygons={POLYGON_SWITCHES[k] for k in kinds}, overlays=groups, bounds=bounds)
    img.save(a.out)
    print(f'{a.out}: {img.size[0]}x{img.size[1]}, area {box}')


def model_bounds(ds, exe, cache: Path):
    """The models' "Bounds Poly" from their headers (as the editor's overlays)."""
    from zaxtools.exeschema import Schema
    from zaxtools.modelhead import ModelHead
    head = ModelHead(Schema.open(exe, ds, cache))
    memo = {}

    def bounds(model):
        if model.lower() not in memo:
            try:
                memo[model.lower()] = head.decode(ds.read(f'Cache/Models/{model}.mdl16')).values.get('Bounds Poly') or []
            except Exception:           # noqa: BLE001 - missing or unreadable model
                memo[model.lower()] = None
        return memo[model.lower()]
    return bounds


if __name__ == '__main__':
    main()
