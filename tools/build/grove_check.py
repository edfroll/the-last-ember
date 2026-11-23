#!/usr/bin/env python3
"""T-030: checks of the built Mushroom Grove (a step of tools/build/grove_step.sh, server STOPPED):
  - no snow (snow, snow blocks, powder snow) and no vanilla tree blocks left in the circle (the saved chunks, block by block);
  - without jumps (tools/build/walkcheck.py: step <= 0.5, +1 only onto a stair from its low side) from the pad of bonfire 10 along the path
    through the door up both storeys to the observatory (the Advisor's night point), to the armchair, to the garden bench;
  - the 6 faces stand closed in the world (the eye cells: stripped poplar).
  python3 tools/build/grove_check.py        (exit 1 on a failure)"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grove_plan as P
from walkcheck import reach, kind

def main():
    ok = True
    import r1_grove as RG
    world = os.path.join(P.ROOT, "server/world")
    snow = RG.world_scan(RG.SNOW, lambda x, z: P.in_circle(x, z) and not P.on_pad(x, z))
    trees = RG.world_scan(RG.VANILLA_TREE, lambda x, z: P.in_circle(x, z) and not P.on_pad(x, z))
    print("grove check: snow in the circle %d, vanilla tree blocks %d%s" % (len(snow), len(trees), (" e.g. %s" % (snow + trees)[:4]) if snow or trees else ""))
    ok &= not snow and not trees
    gr = P.grids(); rl = P.relief(gr); T = rl["T"]
    meta = json.load(open(os.path.join(P.OUT, "grove.json")))
    blocks = {}
    for line in open(os.path.join(P.OUT, "grove.txt")):
        x, y, z, s = line.split(" ", 3); blocks[(int(x), int(y), int(z))] = s.strip()
    def get(x, y, z):
        s = blocks.get((x, y, z))
        if s is not None:
            if "_door" in s: return "minecraft:air"
            return s
        i, j = P.ix(gr, x, z)
        if 0 <= i < T.shape[0] and 0 <= j < T.shape[1] and y <= T[i, j]: return "minecraft:stone"
        return None
    box = (P.CX - P.R, P.CZ - P.R, P.CX + P.R, P.CZ + P.R)
    start = (P.PAD[0], P.HZ, float(P.PAD_Y + 1))
    seen = reach(get, start, box, 80, 200)
    goals = {"door (outside)": (meta["door"][0] + 1, meta["door"][2], None), "armchair (beside)": (meta["chair"][0] + 1, meta["chair"][2] + 1, meta["floors"]["f1"]),
             "observatory (night point)": (meta["night"][0], meta["night"][2], meta["night"][1]), "garden bench": (meta["garden"]["bench"][0], meta["garden"]["bench"][2] - 1, None),
             "stump bench": (meta["garden"]["bench_stump"][0] + 1, meta["garden"]["bench_stump"][2], None)}
    for nm, (gx, gz, gy) in goals.items():
        hit = [s for s in seen if s[0] == gx and s[1] == gz and (gy is None or abs(s[2] - gy) < 0.6)]
        print("  walk (no jumps) pad -> %s: %s" % (nm, "OK" if hit else "NOT REACHED"))
        ok &= bool(hit)
    # the faces: closed in the world (BlockWriter wrote the closed templates' blocks)
    import grove_dp
    bad = [f["k"] for f in meta["faces"] if "poplar_log" not in (blocks.get(tuple(grove_dp.eye_cell(f))) or "") or "dark_oak_trapdoor" not in (blocks.get(tuple(grove_dp.eye_front(f))) or "")]
    print("  faces closed in the build: %d of %d%s" % (len(meta["faces"]) - len(bad), len(meta["faces"]), (" (not: %s)" % bad) if bad else ""))
    ok &= not bad
    print("grove check: %s" % ("OK" if ok else "FAILED"))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
