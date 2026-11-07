"""Shared helpers for the command line tools."""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from zaxtools.datasource import DataSource  # noqa: E402


def data_arg(p: argparse.ArgumentParser) -> None:
    p.add_argument('--data', default=os.environ.get('ZAX_DATA'),
                   help='folder "Data" or file "Data.dat"/zip (default: environment variable ZAX_DATA)')


def open_data(args) -> DataSource:
    if not args.data:
        sys.exit('Please pass --data or set ZAX_DATA (folder Data or Data.dat).')
    return DataSource(args.data)
