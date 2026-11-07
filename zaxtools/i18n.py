"""Translation hook for the texts zaxtools produces for a user interface (level check findings, list
names, field limits). zaxtools stays free of Qt: the texts are English, marked for Qt's ``lupdate``
with ``translate(context, text)`` / ``QT_TRANSLATE_NOOP(context, text)``, and an application installs
its translation function with ``install`` (the editor installs ``QCoreApplication.translate``).

Without an installed function the English text is returned; ``%n`` is replaced by the count and a
plural marker ``(s)`` follows the count (``"%n error(s)"`` -> ``"1 error"``, ``"2 errors"``).
"""
from __future__ import annotations

from typing import Callable

_hook: Callable | None = None


def install(fn: Callable | None) -> None:
    """``fn(context, text, disambiguation, n) -> str`` (the signature of ``QCoreApplication.translate``);
    None restores the English texts."""
    global _hook
    _hook = fn


def translate(context: str, text: str, disambiguation: str | None = None, n: int = -1) -> str:
    if _hook is not None:
        return _hook(context, text, disambiguation, n)
    if n >= 0:
        text = text.replace('%n', str(n)).replace('(s)', '' if n == 1 else 's')
    return text


def QT_TRANSLATE_NOOP(context: str, text: str) -> str:  # noqa: N802 - the name lupdate looks for
    """Marks a text for lupdate where it is defined; ``translate`` it where it is shown."""
    return text
