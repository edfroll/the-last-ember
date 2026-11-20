#!/usr/bin/env python3
"""Compare two saved worlds block by block (overworld): block states, biomes and block entities of every chunk.
Used to prove that a world restored from the cache and rebuilt from there equals a world built from scratch (tools/world_cache.sh).
Entities (mobs, displays, interactions) are not compared: their UUIDs are random; the datapack rebuilds them anyway.

  python3 tools/world_diff.py <world_a> <world_b> [x1 z1 x2 z2]     -> summary; exit 1 when the blocks differ
Output: chunks only in one world, chunks with different blocks (count of differing blocks, first examples), biomes, block entities.
Fast path: a section whose palette and packed data are byte-equal is equal; only differing sections are decoded."""
import os, struct, sys, zlib, gzip, collections
from multiprocessing import Pool

IGN_BE = {"x", "y", "z", "keepPacked"}   # block entity keys that say nothing about content


def read_nbt(buf):
    pos = 0
    def u(fmt, n):
        nonlocal pos
        v = struct.unpack_from(">" + fmt, buf, pos)[0]; pos += n; return v
    def string():
        nonlocal pos
        n = u("H", 2); s = buf[pos:pos + n].decode("utf-8", "replace"); pos += n; return s
    def payload(t):
        nonlocal pos
        if t == 1: return u("b", 1)
        if t == 2: return u("h", 2)
        if t == 3: return u("i", 4)
        if t == 4: return u("q", 8)
        if t == 5: return u("f", 4)
        if t == 6: return u("d", 8)
        if t == 7: n = u("i", 4); v = bytes(buf[pos:pos + n]); pos += n; return v
        if t == 8: return string()
        if t == 9:
            it = u("b", 1); n = u("i", 4)
            return [payload(it) for _ in range(n)]
        if t == 10:
            d = {}
            while True:
                tt = u("b", 1)
                if tt == 0: return d
                k = string(); d[k] = payload(tt)
        if t == 11: n = u("i", 4); v = ("I", bytes(buf[pos:pos + 4 * n])); pos += 4 * n; return v
        if t == 12: n = u("i", 4); v = ("L", bytes(buf[pos:pos + 8 * n])); pos += 8 * n; return v
        raise ValueError(t)
    t = u("b", 1); string()
    return payload(t)


def region_chunks(path):
    """{(cx, cz): nbt} of one region file"""
    out = {}
    if not os.path.exists(path): return out
    data = open(path, "rb").read()
    for i in range(1024):
        if len(data) < 4096: break
        off = struct.unpack_from(">I", data, i * 4)[0]
        if not off: continue
        sector = off >> 8
        length, comp = struct.unpack_from(">IB", data, sector * 4096)
        raw = data[sector * 4096 + 5: sector * 4096 + 4 + length]
        if comp == 2: raw = zlib.decompress(raw)
        elif comp == 1: raw = gzip.decompress(raw)
        elif comp == 3: pass
        else: continue
        c = read_nbt(raw)
        out[(c.get("xPos"), c.get("zPos"))] = c
    return out


def pal_name(p):
    if isinstance(p, str): return p
    nm = p.get("id") or p.get("Name") or p.get("")
    props = p.get("properties") or p.get("Properties")
    if props: nm += "[" + ",".join("%s=%s" % kv for kv in sorted(props.items())) + "]"
    return nm


def decode(container, n):
    """palette container -> list of n names"""
    pal = [pal_name(p) for p in container.get("palette", [])]
    if len(pal) <= 1: return pal * n if pal else [None] * n
    data = container.get("data")
    raw = data[1] if data else b""
    longs = struct.unpack(">%dq" % (len(raw) // 8), raw)
    bits = max(4 if n == 4096 else 1, (len(pal) - 1).bit_length()); per = 64 // bits; mask = (1 << bits) - 1; idx = []
    for v in longs:
        v &= (1 << 64) - 1
        for k in range(per):
            if len(idx) < n: idx.append((v >> (k * bits)) & mask)
    return [pal[i] if i < len(pal) else "?" for i in idx]


def freeze(v):
    if isinstance(v, dict): return tuple(sorted((k, freeze(x)) for k, x in v.items()))
    if isinstance(v, list): return tuple(freeze(x) for x in v)
    return v


def cmp_chunk(a, b, ck):
    """(differing block count, examples, differing biome cells, differing block entities)"""
    cx, cz = ck; nb = 0; ex = []; nbio = 0
    sa = {s.get("Y"): s for s in a.get("sections", [])}; sb = {s.get("Y"): s for s in b.get("sections", [])}
    for y in sorted(set(sa) | set(sb)):
        A = sa.get(y, {}); B = sb.get(y, {})
        for key, n in (("block_states", 4096), ("biomes", 64)):
            ca = A.get(key) or {}; cb = B.get(key) or {}
            if freeze(ca) == freeze(cb): continue
            da = decode(ca, n) if ca else ["minecraft:air" if n == 4096 else None] * n
            db = decode(cb, n) if cb else ["minecraft:air" if n == 4096 else None] * n
            for i, (p, q) in enumerate(zip(da, db)):
                if p == q: continue
                if n == 4096:
                    nb += 1
                    if len(ex) < 4: ex.append((cx * 16 + i % 16, y * 16 + i // 256, cz * 16 + (i // 16) % 16, p, q))
                else: nbio += 1
    def bes(c):
        return {(e.get("x"), e.get("y"), e.get("z")): freeze({k: v for k, v in e.items() if k not in IGN_BE}) for e in c.get("block_entities", [])}
    ea, eb = bes(a), bes(b)
    nbe = sum(1 for k in set(ea) | set(eb) if ea.get(k) != eb.get(k))
    return nb, ex, nbio, nbe


def cmp_region(args):
    wa, wb, fn, box = args
    rel = "dimensions/minecraft/overworld/region"
    A = region_chunks(os.path.join(wa, rel, fn)); B = region_chunks(os.path.join(wb, rel, fn))
    res = []
    for ck in sorted(set(A) | set(B)):
        if box:
            x1, z1, x2, z2 = box
            if ck[0] * 16 + 15 < x1 or ck[0] * 16 > x2 or ck[1] * 16 + 15 < z1 or ck[1] * 16 > z2: continue
        a, b = A.get(ck), B.get(ck)
        if a is None or b is None: res.append((ck, "only_" + ("b" if a is None else "a"), None)); continue
        if a.get("Status") != b.get("Status") and "full" in (a.get("Status"), b.get("Status")):
            res.append((ck, "status %s/%s" % (a.get("Status"), b.get("Status")), None)); continue
        if a.get("Status") != "minecraft:full" and b.get("Status") != "minecraft:full": continue   # proto chunks: not part of the map
        r = cmp_chunk(a, b, ck)
        if any(r[i] for i in (0, 2, 3)): res.append((ck, "diff", r))
    return res


def main():
    wa, wb = sys.argv[1], sys.argv[2]
    box = tuple(int(v) for v in sys.argv[3:7]) if len(sys.argv) >= 7 else None
    rel = "dimensions/minecraft/overworld/region"
    names = sorted(set(os.listdir(os.path.join(wa, rel))) | set(os.listdir(os.path.join(wb, rel))))
    names = [n for n in names if n.endswith(".mca")]
    with Pool(min(4, os.cpu_count() or 1)) as p:
        res = [r for part in p.map(cmp_region, [(wa, wb, n, box) for n in names]) for r in part]
    kinds = collections.Counter(k if k == "diff" else k.split()[0] for _, k, _ in res)
    blocks = sum(r[2][0] for r in res if r[2]); bio = sum(r[2][2] for r in res if r[2]); be = sum(r[2][3] for r in res if r[2])
    print("world_diff: %d region files; chunks differing: %s; blocks %d, biome cells %d, block entities %d" % (len(names), dict(kinds) or 0, blocks, bio, be))
    for ck, k, r in sorted(res, key=lambda t: -(t[2][0] if t[2] else 0))[:15]:
        print("  chunk %s %s %s" % (ck, k, ("blocks %d bio %d be %d e.g. %s" % (r[0], r[2], r[3], r[1][:2])) if r else ""))
    sys.exit(1 if blocks or bio or be or kinds.get("only_a") or kinds.get("only_b") or kinds.get("status") else 0)


if __name__ == "__main__":
    main()
