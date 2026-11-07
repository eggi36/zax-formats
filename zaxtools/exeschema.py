"""Class and field descriptions of the engine, read from Zax.exe (plus hints from the text files).

The engine registers every class and each of its fields at program start:

    class:   new CClassInfo(&classVar, "CName", version, parent class, size, ...)   -> REG_CLASS
    field:   d = new; d->Ctor("Category/Field name", ..., offset, size, ...)       -> type = ctor address
             classVar->AddField(d)                                                  -> ADD_FIELD
             d->AddEnum(value, "Name")                                              -> ENUM_ADD (optional)
             classVar->LastField()->SetHelp("help text for the editor")             -> LAST_FIELD, HELP
                                                                                       (optional; 254 calls)

The order of the AddField calls is the order in the text and binary formats. The parent class is
passed as a class variable (``mov reg, [classVar]``) or via a getter function
(``mov eax, [classVar]; ...``).

What the exe does not reveal comes from the text files of the game data (``text_hints``): the
class of embedded objects, the keys of array elements and the element class of named arrays.

The addresses apply to the retail version (Zax.exe, 2,572,288 bytes). ``extract`` checks that.
Needs ``capstone`` and ``pefile`` (only for generating; the result is saved as JSON).
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
from collections import Counter
from pathlib import Path

from . import textformat as tf
from .datasource import DataSource
from .i18n import translate

VERSION = 10
REG_CLASS, ADD_FIELD, NEW, ENUM_ADD, HELP = 0x415780, 0x415700, 0x5d033a, 0x54da60, 0x419020
ENUM_ADD_FLOAT = 0x54ed60      # FieldDesc_AddEnumFloat: a name for a float value [confirmed: zax-decomp/reimpl/src/field_text2.cpp]
LAST_FIELD = 0x415770          # CClassInfo::LastField: the field added last [confirmed: zax-decomp/reimpl/src/class_info.cpp]

# constructor address of the field descriptor -> binary encoding (see modelhead)
ENCODING = {
    0x415dd0: 'str', 0x414cf0: 'str', 0x523e30: 'str', 0x5182d0: 'str', 0x54e560: 'str',
    0x415ea0: 'str', 0x54d140: 'str', 0x54e220: 'str', 0x58b840: 'str', 0x4184c0: 'str',
    0x4186f0: 'ptr', 0x54e610: 'ptr', 0x54e690: 'emb', 0x5284c0: 'emb',
    0x419230: 'arr', 0x417a20: 'arr', 0x419110: 'arr', 0x417930: 'map',
    0x54dfc0: 'u8', 0x54ddf0: 'u8',
    0x54ecd0: 'f4', 0x54ec40: 'f4', 0x53f200: 'f4', 0x54f060: 'f8',
    0x54d480: 'i4', 0x54d7f0: 'i4', 0x54d6e0: 'i4', 0x54d590: 'i4', 0x54dc70: 'i4',
    0x4a7fa0: 'pt', 0x545450: 'ipt', 0x545530: 'ipt',
    0x547fd0: 'poly',
}

# Class of embedded objects that occur in no text file: from the class's constructor
# (sub-object at this+offset, last vtable) [confirmed: Zax.exe]
EMBEDDED = {
    'CCompanionAI.Set Target Behavior': 'CEntityBehaviorStateSetClosestTarget',  # +0xec, 0x46e2c2 -> 0x5867a0
    'CAutoGunAI.PickupAI': 'CPickupAI',                                          # +0x30, 0x58ebc4 -> 0x53d8f0
}
# the byte and the bit-of-a-dword kinds: their FromText stores atoi(text) != 0, so the value is 0 or 1
# [confirmed: code 0x54df30, 0x54e130; zax-decomp/reimpl/src/field_text.cpp]
BOOL_CTORS = {0x54ddf0, 0x54dfc0}

# Value kinds by constructor and the position of their arguments (0 = the name; constructors "with units"
# take the units text as argument 1 and shift the rest by one) [confirmed: zax-decomp/reimpl/src/field_kinds.cpp,
# zax-decomp/docs/DECOMPILATION.md section 6 "Field kinds"]:
#   int / enum int: default 5, min 7, max 8 (+1 with units); float: default 5, min 7, max 8, step 9
#   double: default 5/6, min 8/9, max 10/11, step 12/13 (low/high dwords)
#   byte: default 5; bit: mask 4, default 6; flags: name list 4, default names 6 (text)
#   ZString, C string: default text 5; float/int point: pointer to the default x, y at 5 (int point
#   0x545530: x 5, y 6)
VALUE_KINDS = {
    0x54d480: ('int', 0), 0x54dc70: ('int', 0), 0x54d590: ('int', 1),
    0x54d6e0: ('enum', 0), 0x54d7f0: ('enum', 1), 0x53f200: ('enum', 0),
    0x54ecd0: ('float', 0), 0x54ec40: ('float', 1), 0x54f060: ('double', 0),
    0x54ddf0: ('byte', 0), 0x54dfc0: ('bit', 0), 0x414cf0: ('flags', 0),
    0x415dd0: ('zstring', 0), 0x415ea0: ('zstring', 0), 0x54d140: ('cstring', 0),
    0x4a7fa0: ('fpoint', 0), 0x545450: ('ipoint', 0), 0x545530: ('ipoint_xy', 0),
}
UNITS_CTORS = {0x54d590, 0x54d7f0, 0x54ec40}
TYPED_RESOURCE = 0x54e560        # resource with type: name, offset, u14, unused, list (+0x34), u18, default name
ENUM_TABLE_CTORS = {0x591ee0, 0x591f40}   # ZEnumTable constructors (this = the table object, the record table)
# The name lists of the flags kind are definition lists the game fills from the game data at start:
# file names of a folder without folder, extension and a leading '-' of the name, sorted with _stricmp;
# bit i = name i [confirmed: zax-decomp/reimpl/src/definitions.cpp ZDefinitionList::Init, c4_app2.cpp
# App_LoadGameData; the order verified against the texts of all levels, see docs/FORMATS.md]
FLAG_LISTS = {
    0x6bd140: ('Categories', '.txt'),               # g_CategoryList "Entity Categories"
    0x6bd760: ('Damage Types', '.txt'),             # g_DamageTypeList
    0x6c02e8: ('Resources/Game Types', '.zgt'),     # the game type list
}
# arrays of pairs text + pointer (instead of pointers only) [verified: Proximity Mine, game type -> action]
KEYED_PTR = {'CGameTypeSpecificAction.Actions'}


def file_id(path: str | Path) -> str:
    return hashlib.sha1(Path(path).read_bytes()).hexdigest()


def extract(exe_path: str | Path) -> dict:
    """Classes (name, parent) and fields (name, encoding, enum values) from the exe."""
    import capstone
    import pefile

    data = Path(exe_path).read_bytes()
    pe = pefile.PE(data=data, fast_load=True)
    base = pe.OPTIONAL_HEADER.ImageBase
    text = next(s for s in pe.sections if s.Name.rstrip(b'\0') == b'.text')
    tva, tdata = base + text.VirtualAddress, text.get_data()

    def va2off(va):
        for s in pe.sections:
            if base + s.VirtualAddress <= va < base + s.VirtualAddress + s.Misc_VirtualSize:
                return va - base - s.VirtualAddress + s.PointerToRawData
        return None

    def cstr(va):
        o = va2off(va) if va else None
        if o is None:
            return None
        e = data.find(b'\0', o)
        s = data[o:e]
        return s.decode('latin-1') if 0 < len(s) < 120 and all(32 <= c < 127 for c in s) else None

    def long_str(va):
        """Help texts: any length (up to 4 KB), printable Latin-1 plus tab/CR/LF."""
        o = va2off(va) if va else None
        if o is None:
            return None
        e = data.find(b'\0', o)
        s = data[o:e]
        ok = 0 < len(s) < 4096 and all(c >= 32 and c != 127 or c in (9, 10, 13) for c in s)
        return s.decode('latin-1') if ok else None

    def imm(op):
        try:
            return int(op, 16) if op.startswith('0x') else int(op)
        except ValueError:
            return None

    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.skipdata = True

    def getter(t):
        o = t - tva
        if not 0 <= o < len(tdata) - 8:
            return None
        i = next(md.disasm(tdata[o:o + 8], t), None)
        if i and i.mnemonic == 'mov' and i.op_str.startswith('eax, dword ptr [0x'):
            return int(i.op_str.split('[')[1].rstrip(']'), 16)
        return None

    # pass 1: constructors of the field descriptors (name as the last push, this = freshly allocated)
    ctors, pushes, ecx_set = Counter(), [], False
    for i in md.disasm(tdata, tva):
        if i.mnemonic == 'push':
            pushes = (pushes + [i.op_str])[-12:]
        elif i.mnemonic == 'mov' and re.match(r'^ecx, e[a-z]{2}$', i.op_str):
            ecx_set = True                       # this = freshly allocated descriptor
        elif i.mnemonic == 'call':
            t = imm(i.op_str)
            if t and ecx_set and len(pushes) >= 3 and cstr(imm(pushes[-1]) or 0):
                ctors[t] += 1
            pushes, ecx_set = [], False
    ctor_set = set(ctors) - {NEW, ENUM_ADD, ENUM_ADD_FLOAT, HELP, REG_CLASS, LAST_FIELD}

    rdata = next(s for s in pe.sections if s.Name.rstrip(b'\0') == b'.rdata')
    rlo, rhi = base + rdata.VirtualAddress, base + rdata.VirtualAddress + rdata.SizeOfRawData

    def const_dword(va):
        """A dword of .rdata (constants the compiler pushes from memory, e.g. floats)."""
        if not rlo <= va < rhi - 3:
            return None
        o = va2off(va)
        return int.from_bytes(data[o:o + 4], 'little')

    def static_dwords(va, n):
        """n dwords of initialised static data (.rdata or the initialised part of .data), else None."""
        for s in pe.sections:
            lo = base + s.VirtualAddress
            if s.Name.rstrip(b'\0') in (b'.rdata', b'.data') and lo <= va and va + 4 * n <= lo + s.SizeOfRawData:
                o = va2off(va)
                return [int.from_bytes(data[o + 4 * k:o + 4 * k + 4], 'little') for k in range(n)]
        return None

    # constant register values (for arguments pushed from a register, e.g. ``xor ebx, ebx; push ebx``)
    sub_regs = {}
    for r in 'abcd':
        sub_regs.update({f'{r}l': f'e{r}x', f'{r}h': f'e{r}x', f'{r}x': f'e{r}x'})
    sub_regs.update({'si': 'esi', 'di': 'edi', 'bp': 'ebp'})
    imms: dict[str, int] = {}

    def track(m, op):
        if m in ('push', 'cmp', 'test') or m.startswith('j') or not op:
            return
        if m == 'call':
            for r in ('eax', 'ecx', 'edx'):
                imms.pop(r, None)
            return
        dst, _, src = op.partition(', ')
        dst = sub_regs.get(dst, dst)
        if dst not in ('eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp'):
            return
        v = None
        if m == 'mov' and imm(src) is not None and not src.startswith('e'):
            v = imm(src) & 0xffffffff
        elif m in ('xor', 'sub') and src == dst:
            v = 0
        elif m == 'or' and imm(src) in (-1, 0xffffffff):
            v = 0xffffffff
        elif m == 'mov' and src in imms:
            v = imms[src]
        elif m == 'mov' and (mm := re.fullmatch(r'dword ptr \[(0x[0-9a-f]+)\]', src)):
            v = const_dword(int(mm.group(1), 16))          # a constant of .rdata, e.g. a float
        if v is None:
            imms.pop(dst, None)
        else:
            imms[dst] = v

    def push_value(op):
        if op in imms:
            return imms[op]
        v = imm(op)
        if v is not None:
            return v & 0xffffffff
        mm = re.fullmatch(r'dword ptr \[(0x[0-9a-f]+)\]', op)
        return const_dword(int(mm.group(1), 16)) if mm else None

    # pass 2: classes, fields, enums
    classes: dict[int, dict] = {}
    fields: dict[int, list] = {}
    tables: dict[int, int] = {}         # enum table object -> its static record table
    regs: dict[str, int | None] = {}
    pushes, pvals, cur, last, ecx_mem, pushed_parent = [], [], None, None, None, None
    last_of, prev_call = None, None     # result of LastField (a field of [classVar]), previous call
    for i in md.disasm(tdata, tva):
        m, op = i.mnemonic, i.op_str
        ecx_imm = imms.get('ecx')
        track(m, op)
        if m == 'push':
            pushes = (pushes + [op])[-40:]
            pvals = (pvals + [push_value(op)])[-40:]
            if op in regs:
                pushed_parent = regs[op]
        elif m == 'mov' and re.match(r'^(e[a-d]x|e[sd]i), dword ptr \[0x[0-9a-f]+\]$', op):
            regs[op[:3]] = int(op.split('[')[1].rstrip(']'), 16)
            if op.startswith('ecx'):
                ecx_mem = regs['ecx']
        elif m == 'mov' and op == 'ecx, eax' and prev_call is not None and regs.get('eax'):
            ecx_mem = regs['eax']               # classVar from a getter call: AddField(getter(), d)
        elif m == 'call':
            t = imm(op)
            if t and t != REG_CLASS:
                regs['eax'] = getter(t)
            if t == REG_CLASS:
                args = pushes[-9:]
                cp, nm = imm(args[-1]) if args else None, cstr(imm(args[-2]) or 0) if len(args) > 1 else None
                if cp and nm and cp not in classes:
                    parent = pushed_parent if any(a in regs for a in args) else None
                    classes[cp] = {'name': nm, 'parent': parent}
            elif t in ENUM_TABLE_CTORS and ecx_imm and pvals and pvals[-1]:
                tables[ecx_imm] = pvals[-1]
            elif t == ADD_FIELD:
                if ecx_mem and cur:
                    fields.setdefault(ecx_mem, []).append(cur)
                    last = cur
                cur = None
            elif t in ctor_set and len(pushes) >= 3 and cstr(imm(pushes[-1]) or 0):
                cur = {'name': cstr(imm(pushes[-1])), 'ctor': t, 'enum': [],
                       'args': pvals[::-1][:16]}            # argument 0 = the name
            elif t == LAST_FIELD:
                last_of = (fields.get(ecx_mem) or [None])[-1] if ecx_mem else None
            elif t == HELP and pushes and long_str(imm(pushes[-1]) or 0):
                # either classVar->LastField()->SetHelp (231 calls; the RegisterFields functions fetch
                # the class lazily after each AddField) or directly on the descriptor in a register
                target = last_of if prev_call == LAST_FIELD else (cur or last)
                if target is not None:
                    target['help'] = long_str(imm(pushes[-1]))
            elif t in (ENUM_ADD, ENUM_ADD_FLOAT) and (cur or last) and len(pushes) >= 2 \
                    and cstr(imm(pushes[-2]) or 0) and pvals[-1] is not None:
                v = pvals[-1]
                v = _f32(v) if t == ENUM_ADD_FLOAT else (v if v < 2 ** 31 else v - 2 ** 32)
                (cur or last)['enum'].append([v, cstr(imm(pushes[-2]))])
            pushes = []
            prev_call = t

    def table_names(obj):
        """Names of a static enum table {value, name, alternative name} up to the null name."""
        names, alts, va = [], [], tables.get(obj)
        while va:
            rec = static_dwords(va, 3)
            if rec is None or not rec[1]:
                break
            nm = cstr(rec[1])
            if nm is None:
                return None
            names.append(nm)
            alts.append(cstr(rec[2]) if rec[2] else None)
            va += 12
        return (names, alts) if names else None

    out = {}
    for cp, c in classes.items():
        parent = classes.get(c['parent'], {}).get('name') if c['parent'] in classes else None
        if parent == c['name']:
            parent = None
        out[c['name']] = {
            'parent': parent,
            # "group/name": the group of the built-in editor's field tree (e.g. "Listener Settings")
            'fields': [dict({'name': f['name'].split('/')[-1], 'enc': ENCODING.get(f['ctor'], hex(f['ctor'])),
                             'enum': f['enum']}, **({'help': f['help']} if f.get('help') else {}),
                             **({'group': f['name'].rsplit('/', 1)[0]} if '/' in f['name'] else {}),
                             **({'bool': True} if f['ctor'] in BOOL_CTORS else {}),
                             **_value_info(f, cstr, static_dwords, table_names))
                       for f in fields.get(cp, [])],
        }
    if 'CLayerPart' not in out or 'CModel' not in out:
        raise ValueError('Zax.exe does not have the expected layout (different version?)')
    return out


def _f32(bits: int) -> float:
    return struct.unpack('<f', struct.pack('<I', bits & 0xffffffff))[0]


def _f64(lo: int, hi: int) -> float:
    return struct.unpack('<d', struct.pack('<II', lo & 0xffffffff, hi & 0xffffffff))[0]


def _s32(v: int) -> int:
    v &= 0xffffffff
    return v - 2 ** 32 if v >= 2 ** 31 else v


def _value_info(f: dict, cstr, static_dwords, table_names) -> dict:
    """Kind, limits, default, units and step of a field from its constructor's arguments. A value whose
    argument was not a constant (pushed from memory or a register of unknown content) is left out."""
    ctor, args = f['ctor'], f.get('args') or []
    if ctor == TYPED_RESOURCE:
        # a typed resource whose list (+0x34, slot 47 0x54e600 returns it) is a static enum table: the
        # value is the index of a name, read with Find (case-insensitive, also the alternative names) and
        # FindOrFail (an unknown name ends the game) [confirmed: zax-decomp/reimpl/src/resource_fields.cpp, 0x54e490]
        tab = table_names(args[4]) if len(args) > 6 and args[4] else None
        if not tab:
            return {}
        out = {'kind': 'choice', 'choices': tab[0]}
        if any(tab[1]):
            out['alt_choices'] = tab[1]
        if args[6] is not None:
            d = cstr(args[6]) if args[6] else ''
            if d is not None:
                out['default'] = d
        return out
    if ctor not in VALUE_KINDS:
        return {}
    kind, shift = VALUE_KINDS[ctor]
    a = lambda i: args[i + shift] if i + shift < len(args) else None
    out: dict = {'kind': kind}
    if ctor in UNITS_CTORS and args[1:2] and args[1]:
        u = cstr(args[1])
        if u:
            out['units'] = u
    if kind == 'int':
        if a(5) is not None:
            out['default'] = _s32(a(5))
        if a(7) is not None and a(8) is not None:
            out['min'], out['max'] = _s32(a(7)), _s32(a(8))
            out['no_limits'] = a(7) == a(8)
    elif kind == 'enum':
        if a(5) is not None:
            out['default'] = a(5) & 0xffffffff               # compared and written unsigned (%u)
        lo, hi = (0, 0xff) if ctor == 0x53f200 else (a(7), a(8))
        if lo is not None and hi is not None:
            out['no_limits'] = lo == hi
            if lo == hi:                                      # the constructor's "no limits"
                lo, hi = 0, (0xfffffffe if ctor in UNITS_CTORS else 0xffffffff)
            out['min'], out['max'] = lo & 0xffffffff, hi & 0xffffffff
    elif kind == 'float':
        if a(5) is not None:
            out['default'] = _f32(a(5))
        if a(7) is not None and a(8) is not None:
            lo, hi = _f32(a(7)), _f32(a(8))
            out['min'], out['max'] = lo, hi
            out['no_limits'] = not lo != hi                  # equal or NaN (x87 fcomp) [confirmed: 0x54ef30]
        if a(9) is not None:
            out['step'] = _f32(a(9))
    elif kind == 'double':
        if a(5) is not None and a(6) is not None:
            out['default'] = _f64(a(5), a(6))
        if None not in (a(8), a(9), a(10), a(11)):
            lo, hi = _f64(a(8), a(9)), _f64(a(10), a(11))
            out['min'], out['max'] = lo, hi
            out['no_limits'] = not lo != hi
        if a(12) is not None and a(13) is not None:
            out['step'] = _f64(a(12), a(13))
    elif kind == 'byte':
        if a(5) is not None:
            out['default'] = a(5) & 0xff
    elif kind == 'bit':
        if a(6) is not None:
            out['default'] = 1 if a(6) & 0xff else 0
    elif kind == 'flags':
        if a(4) is not None:
            out['list'] = a(4)
        if a(6) is not None:
            out['default'] = cstr(a(6)) if a(6) else ''        # default names; '' = none (value 0)
            if out['default'] is None:
                del out['default']
    elif kind in ('zstring', 'cstring'):
        if a(5) is not None:
            s = cstr(a(5)) if a(5) else ''
            if s is not None:
                out['default'] = s
    elif kind in ('fpoint', 'ipoint'):
        if a(5) is not None:
            xy = static_dwords(a(5), 2) if a(5) else [0, 0]
            if xy is not None:
                out['default'] = [_f32(x) for x in xy] if kind == 'fpoint' else [_s32(x) for x in xy]
    elif kind == 'ipoint_xy':
        out['kind'] = 'ipoint'
        if a(5) is not None and a(6) is not None:
            out['default'] = [_s32(a(5)), _s32(a(6))]
    return out


def flag_names(ds: DataSource, list_id: int) -> list[str] | None:
    """Names of a flags field's name list as the game builds it from the game data (bit i = name i):
    the files of the folder (also in subfolders, but not below a folder starting with '-'), without folder
    and extension, a leading '-' of the file name removed, sorted with _stricmp. None for an unknown list."""
    if list_id not in FLAG_LISTS:
        return None
    folder, ext = FLAG_LISTS[list_id]
    pre = folder.lower() + '/'
    names = []
    for f in ds.list(pre, ext):
        rel = f[len(pre):] if f.lower().startswith(pre) else f
        parts = rel.split('/')
        if any(p.startswith('-') for p in parts[:-1]):
            continue
        stem = parts[-1][:-len(ext)] if parts[-1].lower().endswith(ext) else parts[-1]
        if stem.startswith('-'):
            stem = stem[1:]
        names.append('/'.join(parts[:-1] + [stem]))
    return sorted(names, key=str.lower)


# --- Field values as the game reads and writes them as text ----------------------------------------------
# [confirmed: zax-decomp/reimpl/src/field_text.cpp, field_text2.cpp, field_slots.cpp; zax-decomp/docs/DECOMPILATION.md section 6
# "Field values as text"; checked against the original in the VM there]

def c_atoi(text: str) -> int:
    """The C runtime's atoi: white space, one sign, digits; 0 otherwise (wrapped to 32 bits)."""
    m = re.match(r'[ \t\n\v\f\r]*([+-]?[0-9]+)', text)
    return _s32(int(m.group(1))) if m else 0


def c_atof(text: str) -> float:
    """The C runtime's atof (decimal only: white space, sign, digits, point, exponent); 0 otherwise."""
    m = re.match(r'[ \t\n\v\f\r]*([+-]?([0-9]+\.?[0-9]*|\.[0-9]+)([eEdD][+-]?[0-9]+)?)', text)
    if not m:
        return 0.0
    try:
        return float(m.group(1).replace('d', 'e').replace('D', 'e'))
    except (ValueError, OverflowError):
        return 0.0


def _to_f32(v: float) -> float:
    try:
        return struct.unpack('<f', struct.pack('<f', v))[0]
    except OverflowError:
        return float('inf') if v > 0 else float('-inf')


def _g(v: float) -> str:
    """%g as the game's C runtime formats floats and doubles: 6 significant digits, an exponent with at
    least three digits ("1e+014", as in the game data)."""
    if v != v or abs(v) == float('inf'):
        return '-1.#IND' if v != v else ('1.#INF' if v > 0 else '-1.#INF')
    t = f'{v:g}'
    if 'e' in t:
        mant, ex = t.split('e')
        t = f'{mant}e{ex[0]}{int(ex[1:]):03d}'
    return t


def value_text(f: dict, v) -> str | None:
    """ToText of a value of field ``f`` as the game writes it (None: kind not covered)."""
    kind = f.get('kind')
    if kind == 'int':
        return str(_s32(v))
    if kind == 'enum':
        u = v & 0xffffffff
        return next((n for k, n in f['enum'] if k & 0xffffffff == u), str(u))          # name, else %u
    if kind in ('float', 'double'):
        return next((n for k, n in f['enum'] if k == v), _g(v))                         # name, else %g
    if kind == 'byte':
        return str(v & 0xff)
    if kind == 'bit':
        return '1' if v else '0'
    if kind in ('zstring', 'cstring'):
        return v
    if kind == 'fpoint':
        return f'{v[0]:f},{v[1]:f}'
    if kind == 'ipoint':
        return f'{v[0]},{v[1]}'
    return None


def game_read(f: dict, text: str):
    """The value the game stores when it reads ``text`` into field ``f`` (FromText), or None for kinds
    not covered here. Numbers are clamped to the field's limits unless they are equal ("no limits");
    the int-with-names and float kinds keep a value that has a name and take the value of a name."""
    kind = f.get('kind')
    if kind == 'int':
        v = c_atoi(text)
        if 'min' in f and not f.get('no_limits'):
            v = min(max(v, f['min']), f['max'])
        return v
    if kind == 'enum':
        v = c_atoi(text) & 0xffffffff
        if 'min' not in f or f['min'] == f['max']:
            return v
        vals = [k & 0xffffffff for k, _ in f['enum']]
        if v in vals:
            return v                                  # also for a name text when atoi gives a named 0
        hit = next((k & 0xffffffff for k, n in f['enum'] if n.lower() == text.lower()), None)
        if hit is not None:
            return hit
        return min(max(v, f['min']), f['max'])        # unsigned
    if kind in ('float', 'double'):
        v = c_atof(text)
        if kind == 'float':
            v = _to_f32(v)
        if 'min' not in f or f.get('no_limits'):
            return v
        if any(k == v or k != k or v != v for k, _ in f['enum']):
            return v
        hit = next((k for k, n in f['enum'] if n.lower() == text.lower()), None)
        if hit is not None:
            return hit
        if v < f['min']:
            return f['min']
        if not v <= f['max']:
            return f['max']
        return v
    if kind in ('byte', 'bit'):
        return 1 if c_atoi(text) else 0
    return None


def out_of_limits(f: dict, text: str) -> str | None:
    """What the game makes of ``text`` if it differs from what is written: the text of the stored value
    (e.g. a clamped number); None if the game keeps the value or the kind is not covered."""
    if f.get('kind') not in ('int', 'enum', 'float', 'double'):
        return None
    v = game_read(f, text)
    raw = c_atoi(text) if f['kind'] in ('int', 'enum') else c_atof(text)
    if f['kind'] == 'enum':
        raw &= 0xffffffff
    if f['kind'] == 'float':
        raw = _to_f32(raw)
    shown = value_text(f, v)
    if v == raw or shown.lower() == text.strip().lower():      # kept, or only rounded to the same text
        return None
    return shown


def flags_text(names: list[str], chosen: set[str]) -> str:
    """ToText of the flags kind: the names of the set bits in list order, joined by ',' (no blanks)."""
    low = {c.lower() for c in chosen}
    return ','.join(n for n in names if n.lower() in low)


def flags_parse(text: str, names: list[str]) -> tuple[set[str], list[str]]:
    """The names of a flags text (as the game reads it: split at ',', each name looked up without regard to
    case; an empty text is no name) and the parts the game does not find (unknown or empty names, which
    end the game through FindOrFail)."""
    have, bad = set(), []
    if not text:
        return have, bad
    parts = text.split(',')
    if parts[-1] == '':                  # the reader stops at the end of the text: a final ',' is harmless
        parts = parts[:-1]
    low = {n.lower(): n for n in names}
    for p in parts:
        n = low.get(p.lower())
        if n is None:
            bad.append(p)
        else:
            have.add(n)
    return have, bad


def choice_find(f: dict, text: str) -> int | None:
    """Index of ``text`` in a choice field's name table as the game finds it (Find: the names, then the
    alternative names, without regard to case); None = not found, which ends the game (FindOrFail)."""
    low = text.lower()
    for i, n in enumerate(f['choices']):
        if n.lower() == low:
            return i
    for i, n in enumerate(f.get('alt_choices') or []):
        if n and n.lower() == low:
            return i
    return None


def default_text(f: dict, names: list[str] | None = None) -> str | None:
    """The default value of field ``f`` (slot 10, set for every field before an object is read) as the
    game writes it; None if it is not known. Flags need the name list (``names``)."""
    if 'default' not in f:
        return None
    if f.get('kind') == 'flags':
        d = f['default']
        if not d:
            return ''
        if names is None:
            return None
        if d.lower() == '$all':          # "$all" is only understood by the default [confirmed: 0x414de0]
            return ','.join(names[:16])  # without a setter only the low 16 bits are stored
        have, bad = flags_parse(d, names)
        return None if bad else flags_text(names, have)
    if f.get('kind') == 'choice':        # no default name: index 0; ToText writes the name of the index
        i = choice_find(f, f['default']) if f['default'] else 0
        return None if i is None else f['choices'][i]
    return value_text(f, f['default'])


def limits_text(f: dict) -> str:
    """Kind, limits, default, step and units of a field for a tooltip (translatable, ``zaxtools.i18n``)."""
    kind = f.get('kind')
    if kind not in ('int', 'enum', 'float', 'double', 'byte', 'bit'):
        return ''
    out = []
    num = (lambda v: _g(v)) if kind in ('float', 'double') else str
    if 'min' in f:
        if f.get('no_limits'):
            out.append(translate('exeschema', 'Limits: none'))
        else:
            out.append(translate('exeschema', 'Limits: {min} … {max}').format(min=num(f['min']), max=num(f['max'])))
    if 'default' in f:
        out.append(translate('exeschema', 'Default: {value}').format(value=value_text(f, f['default'])))
    if f.get('step') and kind in ('float', 'double'):
        out.append(translate('exeschema', 'Step: {value}').format(value=_g(f['step'])))
    if f.get('units'):
        out.append(translate('exeschema', 'Unit: {value}').format(value=f['units']))
    return '  ·  '.join(out)


def text_hints(ds: DataSource) -> dict:
    """From all text files: class of embedded objects, element and counter keys of arrays."""
    suffixes = ('.zax', '.txt', '.zgt', '.can', '.sty', '.dificulty', '.quips', '.foo')
    obj: dict[str, Counter] = {}        # "Class.Field" -> Counter(class of the sub-object)
    elem: dict[str, Counter] = {}       # "Class.Field" -> Counter(element key)
    elem_cls: dict[str, Counter] = {}   # "Class.Field" -> Counter(element class)
    count: dict[str, Counter] = {}      # "Class.Field" -> Counter("Item Count"/"Array Count")
    elem_val: dict[str, Counter] = {}   # "Class.Field" -> Counter(kind of values: 'str' | 'pt' | 'ipt')
    layout: dict[str, Counter] = {}     # class -> Counter(field order)
    kind: dict[str, Counter] = {}       # "Class.Field" -> Counter('obj' | 'arr' | 'num' | 'str')

    def walk(node: tf.Node, cls: str) -> None:
        layout.setdefault(cls, Counter())['\t'.join(c.key for c in node.children if not isinstance(c, tf.Raw))] += 1
        for c in node.children:
            if isinstance(c, tf.Entry):
                k = 'num' if re.fullmatch(r'-?\d+(\.\d+)?(e-?\d+)?', c.value) else 'str'
                if c.value:
                    kind.setdefault(f'{cls}.{c.key}', Counter())[k] += 1
            if not isinstance(c, tf.Node):
                continue
            key = f'{cls}.{c.key}'
            kind.setdefault(key, Counter())['arr' if c.value == 'Array' else 'obj'] += 1
            if c.value == 'Array':
                for e in c.children:
                    if isinstance(e, tf.Entry) and e.key in ('Item Count', 'Array Count'):
                        count.setdefault(key, Counter())[e.key] += 1
                for e in c.array_elements():
                    elem.setdefault(key, Counter())[e.key] += 1
                    if isinstance(e, tf.Entry):
                        elem_val.setdefault(key, Counter())[_value_kind(e.value)] += 1
                    if isinstance(e, tf.Node):
                        elem_cls.setdefault(key, Counter())[e.value] += 1
                        walk(e, e.value)
            elif not c.value.startswith('CFrame'):
                obj.setdefault(key, Counter())[c.value] += 1
                walk(c, c.value)

    for f in ds.list('', ''):
        if f.lower().endswith(suffixes):
            try:
                doc = tf.load_bytes(ds.read(f))
            except (ValueError, UnicodeDecodeError):
                continue
            for c in doc.children:
                if isinstance(c, tf.Node):
                    walk(c, c.value)
    top = lambda d: {k: v.most_common(1)[0][0] for k, v in d.items()}
    return {'obj': top(obj), 'elem': top(elem), 'elem_cls': top(elem_cls), 'count': top(count),
            'elem_val': top(elem_val), 'layout': {k: v.most_common(1)[0][0].split('\t') for k, v in layout.items()},
            'kind': top(kind)}


def _value_kind(v: str) -> str:
    """Kind of an array value in the text: number pair (integer/decimal) or text."""
    if re.fullmatch(r'-?\d+,-?\d+', v):
        return 'ipt'
    if re.fullmatch(r'-?[\d.]+,-?[\d.]+', v):
        return 'pt'
    return 'str'


class Schema:
    """Class description for modelhead: fields including base classes, hints from text files."""

    def __init__(self, data: dict):
        self.data = data
        self.classes: dict = data['classes']
        self.hints: dict = data['hints']
        self._full: dict[str, list] = {}

    def chain(self, cls: str) -> list[str]:
        out = []
        while cls in self.classes and cls not in out:
            out.append(cls)
            cls = self.classes[cls]['parent']
        return out[::-1]

    def fields(self, cls: str) -> list[dict]:
        """All fields in serialisation order, with ``owner`` (defining class).
        "Dynamic Properties" (CObject) belongs to the object preamble and is missing here."""
        if cls not in self._full:
            fs = [dict(f, owner=c) for c in self.chain(cls) for f in self.classes[c]['fields']
                  if f['name'] != 'Dynamic Properties']
            for f in fs:
                if f['enc'] == 'arr' and f"{f['owner']}.{f['name']}" in KEYED_PTR:
                    f['enc'] = 'pmap'
            self._full[cls] = fs
        return self._full[cls]

    def _complete(self, cls: str, fs: list[dict]) -> list[dict]:
        """Add fields the exe analysis missed from the text layout of the class (encoding by the kind
        of text values: object -> ptr, array -> arr, text -> str, number -> f4)."""
        lay = self.hints.get('layout', {}).get(cls)
        if not lay:
            return fs
        have = {f['name'] for f in fs}
        out = list(fs)
        for i, k in enumerate(lay):
            if k in have:
                continue
            kind = self.hints.get('kind', {}).get(f'{cls}.{k}', 'str')
            enc = {'obj': 'ptr', 'arr': 'arr', 'num': 'f4'}.get(kind, 'str')
            # insert behind the predecessor in the text layout
            prev = next((lay[j] for j in range(i - 1, -1, -1) if lay[j] in {f['name'] for f in out}), None)
            pos = next((n + 1 for n, f in enumerate(out) if f['name'] == prev), 0)
            out.insert(pos, {'name': k, 'enc': enc, 'enum': [], 'owner': cls, 'from_text': True})
        return out

    def known(self, cls: str) -> bool:
        return cls in self.classes

    def _hint(self, kind: str, cls: str, key: str):
        h = self.hints[kind]
        for c in [cls] + self.chain(cls)[::-1]:
            if f'{c}.{key}' in h:
                return h[f'{c}.{key}']
        return next((v for k, v in h.items() if k.endswith('.' + key)), None)

    def help(self, cls: str, key: str) -> str | None:
        """Help text of field ``key`` of ``cls`` (searched from ``cls`` up through its base classes), as
        the game's built-in editor would show it; None if the field has none or is unknown."""
        for c in self.chain(cls)[::-1]:
            for f in self.classes[c]['fields']:
                if f['name'] == key:
                    return f.get('help')
        return None

    def is_bool(self, cls: str, key: str) -> bool:
        """Field ``key`` of ``cls`` (or of a base class) is a switch: the game reads any text as 0 or 1."""
        for c in self.chain(cls)[::-1]:
            for f in self.classes[c]['fields']:
                if f['name'] == key:
                    return bool(f.get('bool'))
        return False

    def field(self, cls: str, key: str) -> dict | None:
        """The description of field ``key`` of ``cls`` (searched up through the base classes)."""
        for c in self.chain(cls)[::-1]:
            for f in self.classes[c]['fields']:
                if f['name'] == key:
                    return dict(f, owner=c)
        return None

    def names(self, cls: str, key: str) -> list[str]:
        """Value names of an int-with-names or float field (FieldDesc_AddEnum), in registration order."""
        f = self.field(cls, key)
        return [n for _, n in f['enum']] if f and f.get('kind') in ('enum', 'float', 'double') else []

    def missing_fields(self, cls: str, have: set[str]) -> list[dict]:
        """The fields of ``cls`` (with base classes, in the writer's order) that are not in ``have``."""
        return [f for f in self.fields(cls) if f['name'] not in have]

    def embedded_class(self, cls: str, key: str) -> str | None:
        for c in self.chain(cls)[::-1]:
            if f'{c}.{key}' in EMBEDDED:
                return EMBEDDED[f'{c}.{key}']
        return self._hint('obj', cls, key)

    def element_key(self, cls: str, key: str) -> str:
        return self._hint('elem', cls, key) or 'Item'

    def element_class(self, cls: str, key: str) -> str | None:
        return self._hint('elem_cls', cls, key)

    def element_value_kind(self, cls: str, key: str) -> str | None:
        """For arrays of values (instead of objects): 'str', 'pt' or 'ipt'."""
        return self._hint('elem_val', cls, key)

    def count_key(self, cls: str, key: str) -> str:
        return self._hint('count', cls, key) or 'Item Count'

    # --- Generate / cache ---------------------------------------------------------
    @classmethod
    def build(cls, exe_path: str | Path, ds: DataSource) -> 'Schema':
        return cls({'version': VERSION, 'exe': file_id(exe_path),
                    'classes': extract(exe_path), 'hints': text_hints(ds)})

    @classmethod
    def open(cls, exe_path: str | Path, ds: DataSource, cache_dir: Path) -> 'Schema':
        """Load from the cache or generate from exe + text files (a few seconds)."""
        fid = file_id(exe_path)
        file = Path(cache_dir) / f'schema-{fid[:16]}.json'
        try:
            data = json.loads(file.read_text(encoding='utf-8'))
            if data.get('version') == VERSION and data.get('exe') == fid:
                return cls(data)
        except (OSError, ValueError):
            pass
        sch = cls.build(exe_path, ds)
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps(sch.data), encoding='utf-8')
        return sch


def find_exe(ds: DataSource) -> Path | None:
    """Look for Zax.exe next to the data folder or Data.dat (or one level up)."""
    root = Path(ds.root).resolve()
    for d in (root.parent, root.parent.parent, root):
        for name in ('Zax.exe', 'zax.exe', 'ZAX.EXE'):
            if (d / name).is_file():
                return d / name
    return None
