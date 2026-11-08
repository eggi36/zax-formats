"""The engine's text format (.zax, .txt, .zgt, .can, .sty, .dificulty, .quips, ...).

Layout (CRLF, indented with tabs, ASCII/Latin-1):

    CLayerSaveData            <- root: class name
    {
        Width=5000            <- entry  key=value
        Music Mix=CMusicMixerData
        {                     <- if an entry is followed by a line "{",
            ...               <- the value is the class name of a sub-object
        }
        Items=Array
        {
            Item Count=2      <- arrays: "Array" + counter + elements
            ...
        }
        Fog Of War=CFrame(1,1,8)
        {
            01                <- raw lines without "=" (embedded hex image data)
        }
    }

The parser keeps order, duplicate keys, raw lines, blank lines and the original indentation.
``dumps(loads(text)) == text`` holds for all 292 object text files of the complete Data.zip
(see tools/selftest.py).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, Union

NL = '\r\n'


@dataclass
class Entry:
    """Line ``key=value`` (without a sub-block)."""
    key: str
    value: str
    indent: str | None = None      # None = default (tabs by depth)

    def line(self) -> str:
        return f'{self.key}={self.value}'


@dataclass
class Raw:
    """Line without ``=`` (hex data, blank line, text)."""
    text: str
    indent: str | None = None

    def line(self) -> str:
        return self.text


@dataclass
class Node:
    """Entry with a sub-block. ``key`` is None for blocks without ``=`` (root)."""
    key: str | None
    value: str                         # class name, "Array", "CFrame(1,1,8)", ...
    children: list['Item'] = field(default_factory=list)
    indent: str | None = None
    brace_indent: tuple[str | None, str | None] = (None, None)

    def line(self) -> str:
        return self.value if self.key is None else f'{self.key}={self.value}'

    # --- Queries --------------------------------------------------------
    def __iter__(self) -> Iterator['Item']:
        return iter(self.children)

    def items(self, key: str) -> list['Item']:
        return [c for c in self.children if not isinstance(c, Raw) and c.key == key]

    def item(self, key: str) -> 'Item | None':
        for c in self.children:
            if not isinstance(c, Raw) and c.key == key:
                return c
        return None

    def get(self, key: str, default: str | None = None) -> str | None:
        """Value of an entry (for sub-blocks: the class name)."""
        it = self.item(key)
        return default if it is None else it.value

    def block(self, key: str) -> 'Node | None':
        it = self.item(key)
        return it if isinstance(it, Node) else None

    # --- Changes --------------------------------------------------------
    def set(self, key: str, value: str) -> None:
        """Change the value of an existing entry or append the entry."""
        it = self.item(key)
        if it is None:
            self.children.append(Entry(key, str(value)))
        else:
            it.value = str(value)

    def array_elements(self) -> list['Item']:
        """Elements of an array (everything except the counter)."""
        return [c for c in self.children
                if not isinstance(c, Raw) and c.key not in ('Item Count', 'Array Count')]

    def update_array_count(self) -> None:
        """Update an array's counter after changes."""
        n = len(self.array_elements())
        for k in ('Item Count', 'Array Count'):
            if self.item(k) is not None:
                self.set(k, str(n))


Item = Union[Entry, Raw, Node]


def _split(s: str) -> tuple[str | None, str]:
    if '=' in s:
        k, v = s.split('=', 1)
        return k, v
    return None, s


def loads(text: str) -> Node:
    """Convert text into a tree. Returns an artificial root node whose children are the lines of
    the top level (usually exactly one Node)."""
    trailing_newline = text.endswith(NL)
    lines = text.split(NL)
    if trailing_newline:
        lines = lines[:-1]
    doc = Node(None, '<document>')
    doc.trailing_newline = trailing_newline       # type: ignore[attr-defined]
    stack = [doc]
    children = doc.children
    # indentation is tabs only (lstrip): "default indentation" = as many tabs as the depth
    strips = [line.lstrip('\t') for line in lines]
    n = len(lines)
    i = 0
    while i < n:
        stripped = strips[i]
        nind = len(lines[i]) - len(stripped)
        depth = len(stack) - 1
        if stripped == '}' and depth:
            node = stack.pop()
            children = stack[-1].children
            node.brace_indent = (node.brace_indent[0], None if nind == depth - 1 else lines[i][:nind])
            i += 1
            continue
        own_indent = None if nind == depth else lines[i][:nind]
        k, sep, v = stripped.partition('=')
        if i + 1 < n and strips[i + 1] == '{' and stripped != '{' and stripped != '}':
            node = Node(k, v, indent=own_indent) if sep else Node(None, stripped, indent=own_indent)
            nn = len(lines[i + 1]) - 1
            node.brace_indent = (None if nn == depth else lines[i + 1][:nn], None)
            children.append(node)
            stack.append(node)
            children = node.children
            i += 2
            continue
        children.append(Entry(k, v, own_indent) if sep else Raw(stripped, own_indent))
        i += 1
    if len(stack) != 1:
        raise ValueError('unbalanced braces in the text')
    return doc


def dumps(doc: Node) -> str:
    out: list[str] = []

    def emit(node: Node, depth: int) -> None:
        for c in node.children:
            ind = c.indent if c.indent is not None else '\t' * depth
            out.append(ind + c.line())
            if isinstance(c, Node):
                b0, b1 = c.brace_indent
                out.append((b0 if b0 is not None else '\t' * depth) + '{')
                emit(c, depth + 1)
                out.append((b1 if b1 is not None else '\t' * depth) + '}')

    emit(doc, 0)
    text = NL.join(out)
    if getattr(doc, 'trailing_newline', True):
        text += NL
    return text


def load_bytes(data: bytes) -> Node:
    return loads(data.decode('latin-1'))


def dump_bytes(doc: Node) -> bytes:
    return dumps(doc).encode('latin-1')


def root(doc: Node) -> Node:
    """First object of the file (e.g. CLayerSaveData)."""
    for c in doc.children:
        if isinstance(c, Node):
            return c
    raise ValueError('no object in the file')
