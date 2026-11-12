"""Shared helpers for the command line tools."""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from zaxtools.datasource import DataSource  # noqa: E402
from zaxtools import game_paths  # noqa: E402


def data_arg(p: argparse.ArgumentParser) -> None:
    p.add_argument('--data', default=os.environ.get('ZAX_DATA'),
                   help='folder "Data" or file "Data.dat"/zip (default: environment variable ZAX_DATA, else DATA.dat of '
                        'the build 1308 game folder below gamedata/, zaxtools/game_paths.py)')


def open_data(args) -> DataSource:
    if not args.data:
        try:
            args.data = str(game_paths.data_dat())
        except game_paths.GamePathError as e:
            sys.exit(f'Please pass --data or set ZAX_DATA (folder Data or Data.dat); game_paths: {e}')
    return DataSource(args.data)
