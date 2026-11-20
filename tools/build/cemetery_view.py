#!/usr/bin/env python3
"""T-027 (review): can the soul lights over the graves be seen from the spyglass? The saved chunks are read block by block (the reader
of tools/build/fens_scan.py); a ray from the eye to each light point is stepped every 0.1 block and blocked by any block one cannot see
through (air, light, barrier, glass, panes, bars, chains, plants, candles, lanterns... are see-through; leaves block).
  python3 tools/build/cemetery_view.py [eye_x eye_y eye_z ...]   -> for each eye: per grave (right ones and Thane) the visible part
                                                                    of the light column (y1 + 1.5 .. top), 'all visible' or not
Without arguments the eye is the player at the spyglass (spyglass_eye of server/build/r1/cemetery.json, on the pad); the top of the
columns is cemetery_dp.SPY_TOP. Run with the server stopped
(or after save-all) so the region files hold the world."""
import json, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fens_scan as FS
ROOT = FS.ROOT
CLEAR = re.compile(r"minecraft:(air|cave_air|void_air|light|barrier|structure_void|.*glass.*|iron_bars|chain|.*_chain|.*candle.*|.*lantern|.*torch|"
                   r"short_grass|tall_grass|fern|large_fern|.*_sapling|dead_bush|.*bush|firefly_bush|.*_flower|poppy|dandelion|.*tulip|azure_bluet|"
                   r"oxeye_daisy|cornflower|lily_of_the_valley|allium|blue_orchid|.*mushroom|vine|.*_vines.*|hanging_roots|.*_carpet|"
                   r"pale_hanging_moss|leaf_litter|.*petals|cobweb|.*button|.*pressure_plate|tripwire.*|lever|rail|.*_rail|snow|"
                   r"water|.*_sign|.*_banner|.*fence_gate|.*_fence|.*_wall|ladder|.*_trapdoor|.*_door|.*_slab|.*_stairs|soul_fire|fire|bubble_column)$")
# fences, walls, slabs, stairs, doors, trapdoors are thin or low: the ray is tested against them as against air (the eye looks over a
# parapet slab, between fence posts); full blocks and leaves block

def grid(world, box, y1, y2):
    """(bool array [y, z, x] of blocking blocks, x1, z1, y1)"""
    x1, z1, x2, z2 = box
    A = np.zeros((y2 - y1 + 1, z2 - z1 + 1, x2 - x1 + 1), bool)
    for rx in range(x1 // 512, x2 // 512 + 1):
        for rz in range(z1 // 512, z2 // 512 + 1):
            path = os.path.join(world, "dimensions/minecraft/overworld/region", "r.%d.%d.mca" % (rx, rz))
            if not os.path.exists(path): continue
            for c in FS.sb.chunks(path):
                cx, cz = c.get("xPos"), c.get("zPos")
                if cx is None or cx * 16 + 15 < x1 or cx * 16 > x2 or cz * 16 + 15 < z1 or cz * 16 > z2: continue
                for s in c.get("sections", []):
                    sy = s.get("Y")
                    if sy is None or sy * 16 + 15 < y1 or sy * 16 > y2: continue
                    bs = s.get("block_states") or {}; pal = bs.get("palette", [])
                    names = [p if isinstance(p, str) else (p.get("id") or p.get("Name") or p.get("")) for p in pal]
                    block = [not CLEAR.match(n or "") for n in names]
                    if len(pal) == 1: idx = [0] * 4096
                    else:
                        bits = max(4, (len(pal) - 1).bit_length()); per = 64 // bits; mask = (1 << bits) - 1; idx = []
                        for v in bs.get("data") or []:
                            v &= (1 << 64) - 1
                            for k in range(per):
                                if len(idx) < 4096: idx.append((v >> (k * bits)) & mask)
                    for i, p in enumerate(idx):
                        if not block[p]: continue
                        x = cx * 16 + (i & 15); z = cz * 16 + ((i >> 4) & 15); y = sy * 16 + (i >> 8)
                        if x1 <= x <= x2 and z1 <= z <= z2 and y1 <= y <= y2: A[y - y1, z - z1, x - x1] = True
    return A, x1, z1, y1

def seen(G, eye, pt):
    A, x1, z1, y1 = G
    e = np.array(eye, float); p = np.array(pt, float); d = p - e; n = int(np.linalg.norm(d) / 0.1)
    for k in range(3, n - 3):                      # not the eye's own block nor the light's
        q = e + d * k / n; x, y, z = int(np.floor(q[0])) - x1, int(np.floor(q[1])) - y1, int(np.floor(q[2])) - z1
        if 0 <= y < A.shape[0] and 0 <= z < A.shape[1] and 0 <= x < A.shape[2] and A[y, z, x]: return False
    return True

def main():
    meta = json.load(open(os.path.join(ROOT, "server/build/r1/cemetery.json")))
    graves = [g for g in meta["graves"] if g["kind"] in ("right", "thane")]
    import cemetery_dp; top = cemetery_dp.SPY_TOP
    eyes = []
    a = [float(v) for v in sys.argv[1:]]
    if a: eyes = [tuple(a[i:i + 3]) for i in range(0, len(a), 3)]
    else:
        e = meta["spyglass_eye"]; eyes = [(e[0] + 0.5, e[1] + 1.62, e[2] + 0.5)]       # the player's cell on the pad by the post (feet)
    xs = [e[0] for e in eyes] + [g["x"] for g in graves]; zs = [e[2] for e in eyes] + [g["z"] for g in graves]
    box = (int(min(xs)) - 2, int(min(zs)) - 2, int(max(xs)) + 2, int(max(zs)) + 2)
    G = grid(os.path.join(ROOT, "server/world"), box, meta["W"] - 10, int(max(e[1] for e in eyes)) + 4)
    ok_all = True
    for e in eyes:
        print("eye %.1f %.1f %.1f" % e); n_ok = 0
        for g in graves:
            ys = [g["y"] + 1.5 + 0.5 * k for k in range(int((top - g["y"] - 1.5) / 0.5) + 1)]
            vis = [y for y in ys if seen(G, e, (g["x"] + 0.5, y, g["z"] + 0.5))]
            low = min(vis) if vis else None
            print("  grave %d (%s) at %d %d %d: %s" % (g["n"], g["kind"], g["x"], g["y"], g["z"], "seen from y %.1f" % low if vis else "hidden up to %d" % top))
            n_ok += bool(vis)
        print("  %d of %d" % (n_ok, len(graves))); ok_all &= n_ok == len(graves)
    sys.exit(0 if ok_all else 1)

if __name__ == "__main__": main()
