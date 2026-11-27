"""T-034: read the blocks of a box of the saved overworld with their states ("minecraft:oak_stairs[facing=north,half=bottom,...]"),
for checks that walk the world as it is (the natural ground round a place, the bot's way to it). The chunks are read by the readers of
tools/scan_blocks.py (as tools/build/fens_scan.py does); the server should be stopped (or the chunks saved).
  W = worldblocks.World(x1, z1, x2, z2[, y1, y2]); W.get(x, y, z) -> state string or None (outside the box / not generated)"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fens_scan
sb = fens_scan.sb
ROOT = fens_scan.ROOT


_DEF = None
def defaults(n):
    """the default properties of a block (26.3 saves a chunk's palette without the properties at their default: `minecraft:water`,
    `minecraft:oak_stairs[half=bottom]` for facing=north...): from the data generator's report docs/reference/blocks.json"""
    global _DEF
    if _DEF is None:
        import json
        d = json.load(open(os.path.join(ROOT, "docs/reference/blocks.json"))); _DEF = {}
        for k, v in d.items():
            for st in v.get("states", []):
                if st.get("default"): _DEF[k] = st.get("properties", {})
    return _DEF.get(n, {})


def state(p):
    if isinstance(p, str): n, given = p, {}
    else: n = p.get("Name") or p.get("id") or p.get(""); given = p.get("Properties") or p.get("properties") or {}
    props = dict(defaults(n)); props.update(given)
    return n + ("[" + ",".join("%s=%s" % (k, props[k]) for k in sorted(props)) + "]" if props else "")


class World:
    def __init__(self, x1, z1, x2, z2, y1=-64, y2=319, world=None):
        world = world or os.path.join(ROOT, "server/world")
        self.box = (x1, z1, x2, z2); self.y1, self.y2 = y1, y2
        self.sec = {}      # (cx, sy, cz) -> (palette list, idx uint16[4096] or None for one entry)
        for rx in range(x1 // 512, x2 // 512 + 1):
            for rz in range(z1 // 512, z2 // 512 + 1):
                path = os.path.join(world, "dimensions/minecraft/overworld/region", "r.%d.%d.mca" % (rx, rz))
                if not os.path.exists(path): continue
                for c in sb.chunks(path):
                    cx, cz = c.get("xPos"), c.get("zPos")
                    if cx is None or cx * 16 + 15 < x1 or cx * 16 > x2 or cz * 16 + 15 < z1 or cz * 16 > z2: continue
                    for s in c.get("sections", []):
                        sy = s.get("Y", 0)
                        if sy * 16 + 15 < y1 or sy * 16 > y2: continue
                        bs = s.get("block_states") or {}; pal = [state(p) for p in bs.get("palette", [])]
                        if not pal: continue
                        data = bs.get("data") or []
                        if len(pal) == 1 or not data: self.sec[(cx, sy, cz)] = (pal, None); continue
                        bits = max(4, (len(pal) - 1).bit_length()); per = 64 // bits
                        v = np.array([d & ((1 << 64) - 1) for d in data], dtype=np.uint64)
                        sh = np.arange(per, dtype=np.uint64) * np.uint64(bits)
                        idx = ((v[:, None] >> sh[None, :]) & np.uint64((1 << bits) - 1)).reshape(-1)[:4096].astype(np.uint16)
                        self.sec[(cx, sy, cz)] = (pal, idx)

    def get(self, x, y, z):
        e = self.sec.get((x >> 4, y >> 4, z >> 4))
        if e is None: return None
        pal, idx = e
        if idx is None: return pal[0]
        return pal[int(idx[(y & 15) * 256 + (z & 15) * 16 + (x & 15)])]
