"""Export a model as a sprite sheet: one row per rotation for every sequence.

Example:
    python tools/export_model.py --data Data.dat "Characters/Crater/Crater" -o crater.png
"""
import argparse

from _common import data_arg, open_data
from zaxtools import mdl, preview


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    data_arg(p)
    p.add_argument('model', help='model name as in the .zax, e.g. "Environments/Jungle/Trees/Jungle 1"')
    p.add_argument('-o', '--out', default='model.png')
    p.add_argument('--max-frames', type=int, default=24, help='at most this many frames per row')
    a = p.parse_args()
    ds = open_data(a)
    m = mdl.load(ds.read(f'Cache/Models/{a.model}.mdl16'), a.model)
    for s in m.sequences:
        print(f'{s.name:28s} {s.total:4d} frames  {s.rotations:2d} rotations x {s.frames_per_rotation:3d}  '
              f'{s.fps:5.1f} fps  {s.mode}  (stored: {len(s.stored)})')
    rows = preview.model_rows(m, a.max_frames)
    if not rows:
        raise SystemExit('No frames found.')
    sheet = preview.sprite_sheet(rows)
    sheet.save(a.out)
    print(f'{a.out}: {sheet.size[0]}x{sheet.size[1]}')


if __name__ == '__main__':
    main()
