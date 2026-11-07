"""Read the header of a model (.mdl16/.mdl): the CModel object with the default object ("Default Entity").

Binary format (field order and types from Zax.exe, see exeschema):

    object   = f32 27.0, f32 class signature, u32 n, n x (name + pointer) "Dynamic Properties", fields ...
               (dynamic properties, e.g. "Hue Remap", come before the fields in the text)
    pointer  = class name (u32 length + text; empty = null) + object        (encoding 'ptr')
    embedded = object without class name, class from the text data          ('emb')
    array    = u32 count + pointers ...                                     ('arr')
    named array = u32 count + (key text + embedded object) ...              ('map')
                  or + pointer instead of object ('pmap', exeschema.KEYED_PTR)
    inline list = u32 count + embedded objects without key (``INLINE_LISTS``)
    str = u32 length + Latin-1, u8 = 1 byte (bool/bit flag), i4/f4 = 4 bytes, f8 = 8 bytes,
    pt = 2 x f32, ipt = 2 x i32, poly = "POLY2D\\0" + u8 + u32 n + n x (f32, f32)

Some classes additionally write values without a counterpart in the text format (``HIDDEN``):
the position as an integer after "Rendering Height Float", 4 bytes after "Play Ratio",
8 bytes before "Friction" (all movable objects) [verified on all models].

The CModel is followed by u32 number of sequences and the path "Models/..." (checked in ``decode``).
"""
from __future__ import annotations

import struct

from . import textformat as tf
from .exeschema import Schema

VERSION = 5          # increase when the decoder changes (invalidates catalogues)
SEQ_TAG = struct.pack('<ff', 27.0, 758.0)
HIDDEN_AFTER = {('CEntityBase', 'Rendering Height Float'): 2, ('CEntityAnimated', 'Play Ratio'): 1,
                ('CTouchingOvalTriggerAI', 'YX Ratio'): 1}
HIDDEN_BEFORE = {('CEntityMovable', 'Friction'): 2}
# Lists of embedded objects without a key, whose element class no text file names: (class, field) -> element class
# [confirmed: code, CPlaySoundBySurfaceTypeAction's RegisterFields registers "Sound/Specializations" with the list
# field constructor and the class SyfaceTypeSoundItem (sic, 0x4c0370: "Surface Type", "Sound"), zax-decomp/reimpl/src/
# action_classes.cpp; verified: the footstep triggers of the 4 sequences that hold one (8 triggers) read to their end]
INLINE_LISTS = {('CPlaySoundBySurfaceTypeAction', 'Specializations'): 'SyfaceTypeSoundItem'}


class DecodeError(ValueError):
    pass


class _Reader:
    def __init__(self, d: bytes, end: int):
        self.d, self.o, self.end = d, 0, end

    def need(self, n):
        if self.o + n > self.end:
            raise DecodeError(f'end of header reached at {self.o}')

    def u8(self):
        self.need(1)
        self.o += 1
        return self.d[self.o - 1]

    def i4(self):
        self.need(4)
        self.o += 4
        return struct.unpack_from('<i', self.d, self.o - 4)[0]

    def f4(self):
        self.need(4)
        self.o += 4
        return struct.unpack_from('<f', self.d, self.o - 4)[0]

    def f8(self):
        self.need(8)
        self.o += 8
        return struct.unpack_from('<d', self.d, self.o - 8)[0]

    def str(self):
        n = self.i4()
        if not 0 <= n < 4000:
            raise DecodeError(f'implausible text length {n} at {self.o - 4}')
        self.need(n)
        self.o += n
        return self.d[self.o - n:self.o].decode('latin-1')


class Obj:
    """Decoded object: class, dynamic properties [(name, obj)] and fields (name -> value)."""
    __slots__ = ('cls', 'values', 'dynamic')

    def __init__(self, cls: str, values: dict, dynamic: list | None = None):
        self.cls, self.values, self.dynamic = cls, values, dynamic or []


class ModelHead:
    def __init__(self, schema: Schema):
        self.s = schema
        self.trace: list | None = None      # for debugging: [(offset, path, encoding)]

    # --- Reading -------------------------------------------------------------------
    def decode(self, data: bytes) -> Obj:
        """CModel from the model header. Checks that the path "Models/..." follows."""
        return self.decode_end(data)[0]

    def decode_end(self, data: bytes) -> tuple[Obj, int]:
        """CModel and the offset after it (where the number of sequences and the path follow)."""
        end = data.find(SEQ_TAG)
        r = _Reader(data, end if end > 0 else len(data))
        m = self._body(r, 'CModel', 'CModel')
        if data[r.o + 8:r.o + 15] != b'Models/':
            raise DecodeError(f'CModel ends at {r.o}, no path "Models/" after it')
        return m, r.o

    def decode_object(self, data: bytes, offset: int, cls: str) -> tuple[Obj, int]:
        """An embedded object of class ``cls`` at ``offset`` (e.g. a sequence's CAnimationTrigger):
        (object, offset after it)."""
        r = _Reader(data, len(data))
        r.o = offset
        return self._body(r, cls, cls), r.o

    def _body(self, r: _Reader, cls: str, path: str) -> Obj:
        if r.f4() != 27.0:
            raise DecodeError(f'{path}: object signature 27.0 missing at {r.o - 4}')
        r.f4()          # class signature
        ndyn = r.i4()   # Dynamic Properties
        if not 0 <= ndyn < 50:
            raise DecodeError(f'{path}: {ndyn} dynamische Eigenschaften')
        dynamic = [(r.str(), self._ptr(r, f'{path}#dyn')) for _ in range(ndyn)]
        if not self.s.known(cls):
            raise DecodeError(f'{path}: class {cls} unknown')
        vals = {}
        for f in self.s.fields(cls):
            nm = f['name']
            for _ in range(HIDDEN_BEFORE.get((f['owner'], nm), 0)):
                r.i4()
            if self.trace is not None:
                self.trace.append((r.o, f'{path}.{nm}', f['enc']))
            vals[nm] = self._value(r, f, cls, f'{path}.{nm}')
            for _ in range(HIDDEN_AFTER.get((f['owner'], nm), 0)):
                r.i4()
        return Obj(cls, vals, dynamic)

    def _ptr(self, r: _Reader, path: str) -> Obj | None:
        cls = r.str()
        if cls == '':
            return None
        if not cls[:1] == 'C':
            raise DecodeError(f'{path}: no class name ({cls[:30]!r})')
        return self._body(r, cls, f'{path}<{cls}>')

    def _value(self, r: _Reader, f: dict, cls: str, path: str):
        e = f['enc']
        if e == 'str':
            return r.str()
        if e == 'u8':
            return r.u8()
        if e == 'i4':
            return r.i4()
        if e == 'f4':
            return r.f4()
        if e == 'f8':
            return r.f8()
        if e == 'pt':
            return (r.f4(), r.f4())
        if e == 'ipt':
            return (r.i4(), r.i4())
        if e == 'poly':
            r.need(8)
            if r.d[r.o:r.o + 7] != b'POLY2D\0':
                raise DecodeError(f'{path}: POLY2D erwartet')
            r.o += 7
            r.u8()
            n = r.i4()
            if not 0 <= n < 1000:
                raise DecodeError(f'{path}: {n} points')
            return [(r.f4(), r.f4()) for _ in range(n)]
        if e == 'ptr':
            return self._ptr(r, path)
        if e == 'emb':
            sub = self.s.embedded_class(cls, f['name'])
            if sub is None:
                raise DecodeError(f'{path}: class of the embedded object unknown')
            return self._body(r, sub, f'{path}[{sub}]')
        if e == 'arr':
            n = r.i4()
            if not 0 <= n < 1000:
                raise DecodeError(f'{path}: Anzahl {n}')
            vk = None if self.s.element_class(cls, f['name']) else self.s.element_value_kind(cls, f['name'])
            if vk:                                   # array of values (e.g. Segments, Sounds)
                return [('wert', vk, self._value(r, {'name': f['name'], 'enc': vk}, cls, path)) for _ in range(n)]
            return [self._ptr(r, f'{path}[{i}]') for i in range(n)]
        if e == 'map' and (f.get('owner', cls), f['name']) in INLINE_LISTS:
            n = r.i4()
            sub = INLINE_LISTS[(f.get('owner', cls), f['name'])]
            if not 0 <= n < 1000:
                raise DecodeError(f'{path}: count {n}')
            return [(None, self._body(r, sub, f'{path}[{i}]')) for i in range(n)]
        if e == 'map':
            n = r.i4()
            sub = self.s.element_class(cls, f['name'])
            if not 0 <= n < 1000 or sub is None:
                raise DecodeError(f'{path}: named array not readable')
            return [(r.str(), self._body(r, sub, f'{path}[{i}]')) for i in range(n)]
        if e == 'pmap':
            n = r.i4()
            if not 0 <= n < 1000:
                raise DecodeError(f'{path}: Anzahl {n}')
            return [(r.str(), self._ptr(r, f'{path}[{i}]')) for i in range(n)]
        raise DecodeError(f'{path}: field type {e} unknown')

    # --- As text ---------------------------------------------------------------------
    def node(self, obj: Obj, key: str) -> tf.Node:
        """Object as a text tree node ``key=class { ... }`` (formatted as in the levels)."""
        n = tf.Node(key, obj.cls)
        for k, o in obj.dynamic:
            n.children.append(tf.Entry(k, '') if o is None else self.node(o, k))
        for f in self.s.fields(obj.cls):
            if f['name'] in obj.values:
                n.children.append(self._item(obj.cls, f, obj.values[f['name']]))
        return n

    def _item(self, cls: str, f: dict, v):
        nm, e = f['name'], f['enc']
        enum = {k: t for k, t in f.get('enum') or []}
        if e == 'str':
            return tf.Entry(nm, v)
        if e == 'u8':
            return tf.Entry(nm, str(v))
        if e == 'i4':
            return tf.Entry(nm, enum.get(v, str(v)))
        if e in ('f4', 'f8'):
            lab = next((t for k, t in enum.items() if abs(k - v) < 1e-6), None)
            return tf.Entry(nm, lab if lab is not None else _fmt(v))
        if e == 'pt':
            return tf.Entry(nm, f'{v[0]:f},{v[1]:f}')
        if e == 'ipt':
            return tf.Entry(nm, f'{v[0]},{v[1]}')
        if e == 'poly':
            return tf.Entry(nm, ', '.join(f'{_fmt(x)}, {_fmt(y)}' for x, y in v))
        if e == 'ptr':
            return tf.Entry(nm, '') if v is None else self.node(v, nm)
        if e == 'emb':
            return self.node(v, nm)
        if e == 'arr':
            ek = self.s.element_key(cls, nm)
            a = tf.Node(nm, 'Array', [tf.Entry(self.s.count_key(cls, nm), str(len(v)))])
            for x in v:
                if x is None:
                    a.children.append(tf.Entry(ek, ''))
                elif isinstance(x, tuple):
                    a.children.append(tf.Entry(ek, self._item(cls, {'name': ek, 'enc': x[1]}, x[2]).value))
                else:
                    a.children.append(self.node(x, ek))
            return a
        if e == 'map':
            a = tf.Node(nm, 'Array', [tf.Entry('Array Count', str(len(v)))])
            # an inline list's elements have no key; their text form is ours [assumption: no text file holds one]
            a.children += [self.node(o, k if k is not None else 'Item') for k, o in v]
            return a
        if e == 'pmap':          # text form like 'map' [assumption: does not occur in any text file]
            a = tf.Node(nm, 'Array', [tf.Entry('Array Count', str(len(v)))])
            a.children += [tf.Entry(k, '') if o is None else self.node(o, k) for k, o in v]
            return a
        return tf.Entry(nm, str(v))

    # --- Default object for the editor --------------------------------------------------
    def default_part(self, model: Obj, model_path: str) -> tf.Node | None:
        """``Level Part`` from the model's default object, as the original editor creates it:
        Model = path, Has Hit Points = (Hit Points > 0) [verified on 828 models],
        Cur Sequence = Default Sequence, empty name, position 0/0. None if the model has none."""
        ent = model.values.get('Default Entity')
        if ent is None:
            return None
        n = self.node(ent, 'Level Part')
        n.set('Name', '')
        n.set('Model', model_path)
        if n.item('Has Hit Points') is not None:
            n.set('Has Hit Points', '1' if model.values.get('Hit Points', 0) > 0 else '0')
        if model.values.get('Default Sequence') and n.item('Cur Sequence') is not None:
            n.set('Cur Sequence', model.values['Default Sequence'])
        for k in ('Position X', 'Position Y', 'Home Pos X', 'Home Pos Y'):
            if n.item(k) is not None:
                n.set(k, '0')
        return n


def _fmt(v: float) -> str:
    """Number as in the engine's text format (%g, 6 significant digits)."""
    s = f'{v:g}'
    return '0' if s == '-0' else s
