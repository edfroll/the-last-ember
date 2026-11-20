#!/usr/bin/env python3
"""T-026: no snow, no spruces, no cherries in the place of the fens (HQ T-026, 4). The saved chunks are read block by block (palette
+ packed indices); tools/build/r1_fens.py replaces what it finds (snow blocks and powder snow under the ground: dirt / stone, snow
layers, spruce and cherry parts: air), the check after the build finds none.
  python3 tools/build/fens_scan.py [world_dir]      -> the banned blocks left in the place (exit 1 when any)"""
import os, re, struct, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
class _SB: pass
sb = _SB(); _src = open(os.path.join(ROOT, "tools/scan_blocks.py")).read(); _src = _src[:_src.rindex("\nmain()")]   # its readers, not its main
_src = _src.replace('if t == 12: n = u("i", 4); pos += 8*n; return None', 'if t == 12:\n            n = u("i", 4); v = list(struct.unpack_from(">%dq" % n, buf, pos)); pos += 8*n; return v')   # the long arrays (block states)
exec(compile(_src, "scan_blocks", "exec"), sb.__dict__)
PLACE = (-506, 224, -254, 436)
BAN = re.compile(r"minecraft:(snow|snow_block|powder_snow|spruce_log|spruce_leaves|spruce_wood|cherry_log|cherry_leaves|cherry_wood|pink_petals)$")
def scan(world, box=PLACE, inside=None):
    """[(x, y, z, name)] of the banned blocks in the chunks touching the box (inside(x, z) filters the columns)"""
    x1, z1, x2, z2 = box; out = []
    for rx in range(x1 // 512, x2 // 512 + 1):
        for rz in range(z1 // 512, z2 // 512 + 1):
            path = os.path.join(world, "dimensions/minecraft/overworld/region", "r.%d.%d.mca" % (rx, rz))      # the 26.x layout
            if not os.path.exists(path): continue
            for c in sb.chunks(path):
                cx, cz = c.get("xPos"), c.get("zPos")
                if cx is None or cx * 16 + 15 < x1 or cx * 16 > x2 or cz * 16 + 15 < z1 or cz * 16 > z2: continue
                for s in c.get("sections", []):
                    bs = s.get("block_states") or {}; pal = bs.get("palette", [])
                    names = [p if isinstance(p, str) else (p.get("id") or p.get("Name") or p.get("")) for p in pal]
                    if not any(BAN.match(n or "") for n in names): continue
                    data = bs.get("data") or []
                    if len(pal) == 1: idx = [0] * 4096
                    else:
                        bits = max(4, (len(pal) - 1).bit_length()); per = 64 // bits; idx = []
                        for v in data:
                            v &= (1 << 64) - 1
                            for k in range(per):
                                if len(idx) < 4096: idx.append((v >> (k * bits)) & ((1 << bits) - 1))
                    for n_, i in enumerate(idx):
                        nm = names[i]
                        if not BAN.match(nm or ""): continue
                        x, y, z = cx * 16 + n_ % 16, s.get("Y", 0) * 16 + n_ // 256, cz * 16 + (n_ // 16) % 16
                        if x1 <= x <= x2 and z1 <= z <= z2 and (inside is None or inside(x, z)): out.append((x, y, z, nm))
    return out
if __name__ == "__main__":
    sys.path.insert(0, os.path.join(ROOT, "tools/build"))
    import r1_fens
    world = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "server/world")
    f = scan(world, inside=lambda x, z: bool(r1_fens.in_place(x, z)))
    cnt = collections.Counter(n for *_, n in f)
    print("fens scan: banned blocks in the place: %s%s" % (dict(cnt) or "none", (" e.g. %s" % f[:6]) if f else ""))
    sys.exit(1 if f else 0)
