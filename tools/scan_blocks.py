#!/usr/bin/env python3
"""Count block types in saved chunks of a world (anvil .mca) by block-state palettes.

Usage: scan_blocks.py <world_dir> [dimension: overworld|nether|end] [regex of block names, default: ores | 'structures']
Palette-based: counts how many chunk *sections* list a block, plus how many chunks contain it
(enough to prove presence/absence; not exact block counts).
"""
import gzip, os, re, struct, sys, zlib, collections

def read_nbt(buf):
    pos = 0
    def u(fmt, n):
        nonlocal pos
        v = struct.unpack_from(">" + fmt, buf, pos)[0]; pos += n; return v
    def string():
        nonlocal pos
        n = u("H", 2); s = buf[pos:pos+n].decode("utf-8", "replace"); pos += n; return s
    def payload(t):
        nonlocal pos
        if t == 1: return u("b", 1)
        if t == 2: return u("h", 2)
        if t == 3: return u("i", 4)
        if t == 4: return u("q", 8)
        if t == 5: return u("f", 4)
        if t == 6: return u("d", 8)
        if t == 7: n = u("i", 4); pos += n; return None
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
        if t == 11: n = u("i", 4); pos += 4*n; return None
        if t == 12: n = u("i", 4); pos += 8*n; return None
        raise ValueError(t)
    t = u("b", 1); string()
    return payload(t)

def chunks(region_path):
    with open(region_path, "rb") as f:
        data = f.read()
    for i in range(1024):
        off = struct.unpack_from(">I", data, i*4)[0]
        if not off: continue
        sector, = (off >> 8,)
        length, comp = struct.unpack_from(">IB", data, sector*4096)
        raw = data[sector*4096+5: sector*4096+4+length]
        if comp == 2: raw = zlib.decompress(raw)
        elif comp == 1: raw = gzip.decompress(raw)
        elif comp == 3: pass
        else: continue
        yield read_nbt(raw)

def main():
    world = sys.argv[1]
    dim = sys.argv[2] if len(sys.argv) > 2 else "overworld"
    pat = re.compile(sys.argv[3] if len(sys.argv) > 3 else r"minecraft:(\w+_ore|ancient_debris|raw_\w+_block)$")
    sub = {"overworld": "region", "nether": "DIM-1/region", "end": "DIM1/region"}[dim]
    rdir = os.path.join(world, sub)
    if not os.path.isdir(rdir):  # 26.x layout: dimensions/minecraft/<dim>/region
        rdir = os.path.join(world, "dimensions/minecraft", {"overworld": "overworld", "nether": "the_nether", "end": "the_end"}[dim], "region")
    sections = collections.Counter(); in_chunks = collections.Counter(); n = 0
    if len(sys.argv) > 3 and sys.argv[3] == "structures":  # count structure *starts* in chunk NBT
        starts = collections.Counter()
        for fn in sorted(os.listdir(rdir)):
            if not fn.endswith(".mca"): continue
            for c in chunks(os.path.join(rdir, fn)):
                n += 1
                for k in ((c.get("structures") or {}).get("starts") or {}): starts[k] += 1
        print(f"{dim}: {n} chunks scanned in {rdir}; structure starts: {sum(starts.values())}")
        for k, v in sorted(starts.items()): print(f"  {k}: {v}")
        return
    for fn in sorted(os.listdir(rdir)):
        if not fn.endswith(".mca"): continue
        for c in chunks(os.path.join(rdir, fn)):
            n += 1
            seen = set()
            for s in c.get("sections", []):
                for p in (s.get("block_states") or {}).get("palette", []):
                    name = p if isinstance(p, str) else (p.get("id") or p.get("Name") or p.get(""))  # 26.x palette: str, {"id",..} or {"": name}
                    if pat.match(name):
                        sections[name] += 1; seen.add(name)
            for b in seen: in_chunks[b] += 1
    print(f"{dim}: {n} chunks scanned in {rdir}")
    for b, c in sorted(in_chunks.items()):
        print(f"  {b}: in {c} chunks ({sections[b]} sections)")
    if not in_chunks: print("  (none found)")

main()
