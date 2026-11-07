"""Way point graph (.way) - binary, little-endian.

Layout (verified on all 112 levels of Data.zip, see docs/FORMATS.md):

    preamble  float 27.0, float 43.0, int 0              (object signature)
    header    int MinDistBetweenWayPoints  (= value in the .zax, e.g. 20)
              int MaxDistToConnect         (= value in the .zax, e.g. 39)
              int number of nodes N
    N nodes   float 27.0, float 43.0, int 0, int 0,
              int x, int y, int k, k x int edge index
    int number of edges M
    M edges   float 27.0, float 64.0, int 0, int 1, int 0,
              float length, float angle (radians, direction A->B),
              int node A, int node B

Every edge is in the lists of both end points. Length = Euclidean distance.
There are self loops (A == B, length 0, angle pi): a bug in the exe when connecting new nodes
(0x538ae0, docs/FORMATS.md 4), without meaning.

The game rebuilds a missing .way itself when loading ("Calculating Way Point Map", verified in
the game; docs/OPEN_ISSUES.md 2).
"""
from __future__ import annotations

import math
import struct
from dataclasses import dataclass, field

OBJ_NODE = (27.0, 43.0)
OBJ_EDGE = (27.0, 64.0)


@dataclass
class WayNode:
    x: int
    y: int
    edges: list[int] = field(default_factory=list)
    # unknown fields (always 0 so far), for lossless writing back
    unk: tuple[int, int] = (0, 0)


@dataclass
class WayEdge:
    a: int
    b: int
    length: float
    angle: float
    unk: tuple[int, int, int] = (0, 1, 0)


@dataclass
class WayMap:
    min_dist: int
    max_connect: int
    nodes: list[WayNode]
    edges: list[WayEdge]
    head_unk: int = 0


def loads(data: bytes) -> WayMap:
    f0, f1, hu, mind, maxc, n = struct.unpack_from('<ffiiii', data, 0)
    if (f0, f1) != OBJ_NODE:
        raise ValueError('not a .way file (signature %r)' % ((f0, f1),))
    off = 24
    nodes = []
    for _ in range(n):
        g0, g1, u0, u1, x, y, k = struct.unpack_from('<ffiiiii', data, off)
        off += 28
        edges = list(struct.unpack_from('<%di' % k, data, off))
        off += 4 * k
        nodes.append(WayNode(x, y, edges, (u0, u1)))
    m = struct.unpack_from('<i', data, off)[0]
    off += 4
    edges = []
    for _ in range(m):
        g0, g1, u0, u1, u2, ln, ang, a, b = struct.unpack_from('<ffiiiffii', data, off)
        off += 36
        edges.append(WayEdge(a, b, ln, ang, (u0, u1, u2)))
    if off != len(data):
        raise ValueError(f'.way: {len(data) - off} unexplained bytes after the end')
    return WayMap(mind, maxc, nodes, edges, hu)


def dumps(w: WayMap) -> bytes:
    out = [struct.pack('<ffiiii', *OBJ_NODE, w.head_unk, w.min_dist, w.max_connect, len(w.nodes))]
    for nd in w.nodes:
        out.append(struct.pack('<ffiiiii', *OBJ_NODE, *nd.unk, nd.x, nd.y, len(nd.edges)))
        out.append(struct.pack('<%di' % len(nd.edges), *nd.edges))
    out.append(struct.pack('<i', len(w.edges)))
    for e in w.edges:
        out.append(struct.pack('<ffiiiffii', *OBJ_EDGE, *e.unk, e.length, e.angle, e.a, e.b))
    return b''.join(out)


def edge_geometry(ax: float, ay: float, bx: float, by: float) -> tuple[float, float]:
    """Length and angle of an edge as they are stored in the file."""
    if (ax, ay) == (bx, by):
        return 0.0, math.pi
    return math.hypot(bx - ax, by - ay), math.atan2(by - ay, bx - ax) % (2 * math.pi)


def check(w: WayMap) -> list[str]:
    """Consistency check; returns a list of problems (empty = ok)."""
    probs = []
    inc: dict[int, set[int]] = {}
    for i, e in enumerate(w.edges):
        inc.setdefault(e.a, set()).add(i)
        inc.setdefault(e.b, set()).add(i)
        if e.a != e.b:
            na, nb = w.nodes[e.a], w.nodes[e.b]
            ln, _ = edge_geometry(nb.x, nb.y, na.x, na.y)
            if abs(ln - e.length) > 0.01:
                probs.append(f'edge {i}: length {e.length} instead of {ln:.3f}')
    for i, nd in enumerate(w.nodes):
        if set(nd.edges) != inc.get(i, set()):
            probs.append(f'node {i}: edge list does not match')
    return probs
