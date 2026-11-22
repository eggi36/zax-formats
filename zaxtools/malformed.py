"""One error type for malformed files: the binary readers raise ``ValueError`` only.

``struct.error`` (data cut off), ``IndexError`` (an offset past the end), ``OverflowError`` (a number no
integer or list can hold) and ``RecursionError`` (nesting without end) are no ``ValueError``; callers that
report a broken file (the editor, the level check, the catalogue) catch ``ValueError`` and should not need to
know every way a reader can stumble. ``reader`` wraps a public reader so that these become ``ValueError`` (or
the reader's own subclass of it, ``error``) (review 4 G-5, review 5 L1-4); a valid file never reaches the
wrapper's ``except``, so its result is unchanged.
"""
from __future__ import annotations

import functools
import struct

CAUGHT = (struct.error, IndexError, OverflowError, RecursionError)


def reader(fn=None, *, error: type[ValueError] = ValueError):
    def wrap(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except CAUGHT as e:
                raise error(f'malformed data ({fn.__module__.rsplit(".", 1)[-1]}.{fn.__qualname__}: '
                            f'{type(e).__name__}: {e})') from e
        return wrapped
    return wrap(fn) if fn is not None else wrap
