"""Parseo exploratorio del formato XDM (.mdx).

Regla clave: dentro del cuerpo de un record se mezclan sub-records y
propiedades. Si el primer uint16 tiene el bit alto puesto es una propiedad
(id, size), si no es un record (tag, hdr, a, b, total).
"""
import struct
from pathlib import Path

R = next(p.parent for p in Path("ref").rglob("theme.xml")) / "scene" / "background.raf"
NUL = bytes([0])


def h2f(u):
    s = (u >> 15) & 1
    e = (u >> 10) & 0x1F
    m = u & 0x3FF
    if e == 0:
        v = (m / 1024.0) * 2 ** -14
    elif e == 31:
        v = float("inf") if m == 0 else float("nan")
    else:
        v = (1 + m / 1024.0) * 2 ** (e - 15)
    return -v if s else v


def prop_one(d, s, e, depth):
    pad = "  " * depth
    pid, sz = struct.unpack_from("<HH", d, s)
    if sz < 4 or s + sz > e:
        return None
    data = d[s + 4:s + sz]
    extra = ""
    if pid == 0x84E0 and len(data) >= 8:
        prim, cnt = struct.unpack_from("<II", data, 0)
        idx = struct.unpack_from(f"<{(len(data) - 8) // 2}H", data, 8)
        extra = f"   prim={prim} idx_count={cnt} indices={idx}"
    elif len(data) % 4 == 0 and 8 <= len(data) <= 20 and pid not in (0x8440, 0x847F, 0x84C0, 0x84C1):
        fl = struct.unpack_from(f"<{len(data) // 4}f", data, 0)
        extra = "   floats=" + ", ".join(f"{v:+.5f}" for v in fl)
    print(f"{pad}{s:#06x} PROP {pid:#06x} size={sz:#04x} {data.hex(' ')}{extra}")
    return s + sz


def arrays(d, s, e, depth):
    pad = "  " * depth
    f0, f1 = struct.unpack_from("<HH", d, s)
    stride, count = struct.unpack_from("<II", d, s + 4)
    print(f"{pad}{s:#06x} VERT flags={f0:#06x}/{f1:#06x} stride={stride} count={count}")
    o = s + 12
    for i in range(count):
        v = d[o:o + stride]
        u = struct.unpack_from(f"<{stride // 2}H", v, 0)
        print(f"{pad}  v{i}  {v.hex(' ')}")
        print(f"{pad}      " + "  ".join(f"[{j}]{h2f(x):+.5f}" for j, x in enumerate(u)))
        o += stride
    if o < e:
        print(f"{pad}  cola: {d[o:e].hex(' ')}")


def walk(d, off, end, depth=0):
    pad = "  " * depth
    while off + 4 <= end:
        first = struct.unpack_from("<H", d, off)[0]
        if first & 0x8000:
            nxt = prop_one(d, off, end, depth)
            if nxt is None:
                return
            off = nxt
            continue
        if off + 16 > end:
            return
        tag, hdr = struct.unpack_from("<HH", d, off)
        a, b, tot = struct.unpack_from("<III", d, off + 4)
        if hdr < 0x10 or tot < hdr or off + tot > end:
            print(f"{pad}{off:#06x} <corte tag={tag:#06x} hdr={hdr:#x} tot={tot:#x}>")
            return
        name = d[off + 0x10:off + hdr].split(NUL)[0].decode("ascii", "replace") if hdr > 0x10 else ""
        print(f"{pad}{off:#06x} REC tag={tag:#06x} hdr={hdr:#04x} a={a:#x} b={b:#x} total={tot:#06x} {name!r}")
        if tag == 0x14:
            arrays(d, off + hdr, off + tot, depth + 1)
        else:
            walk(d, off + hdr, off + tot, depth + 1)
        off += tot


for name in ("background.mdx", "neon_l.mdx"):
    d = (R / name).read_bytes()
    print(f"\n{'=' * 72}\n{name}  ({len(d)} B)  magic={d[:12]!r}\n{'=' * 72}")
    walk(d, 0x10, len(d))
