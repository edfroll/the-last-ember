#!/usr/bin/env python3
"""T-032: checks of the built Spider Thicket (a step of tools/build/spiders_step.sh, server STOPPED):
  - no snow, no ice and no vanilla tree blocks in the place (the saved chunks, block by block; our dark oaks, oaks and poplars are the
    blocks of spiders.txt);
  - the counts: 15..20 cocoons on chains, 3 barrels with loot, the live cocoon, 3 trip wires (6 hooks), the drop, the burrow;
  - the light of the deep (r1_spiders.light at build time): >= 80 % of the feet cells with sky light <= 7, block light 0;
  - without jumps (tools/build/walkcheck.py), both ways (only steps that can be walked back): from the animal trail's start by the trail
    of T-022 to the live cocoon's clearing, to the 3 cocoons with remains, to the burrow's exit and down the ledge to the pit's floor;
    the ground is the step's T (spiders_T.npz: a scan reads the lid and the giant as ground)
  python3 tools/build/spiders_check.py        (exit 1 on a failure)"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import spiders_plan as P
from walkcheck import reach

def model():
    d = np.load(os.path.join(P.OUT, "spiders_T.npz")); TT = d["T"]; tx1, tz1 = int(d["x1"]), int(d["z1"])
    blocks = {}
    for line in open(os.path.join(P.OUT, "spiders.txt")):
        x, y, z, s = line.split(" ", 3); blocks[(int(x), int(y), int(z))] = s.strip()
    def get(x, y, z):
        s = blocks.get((x, y, z))
        if s is not None:
            if re.search(r"tripwire|leaf_litter|iron_chain", s): return "minecraft:air"
            return s
        i, j = z - tz1, x - tx1
        if 0 <= i < TT.shape[0] and 0 <= j < TT.shape[1] and y <= TT[i, j]: return "minecraft:stone"
        return None
    return get, blocks

def main():
    ok = True
    import r1_spiders as RS
    ours = {}
    get, blocks = model()
    for k, s in blocks.items(): ours[k] = s.split("[")[0].split("{")[0]
    snow = RS.world_scan(RS.SNOW, lambda x, z: P.in_place(x, z, 0))
    trees = [t for t in RS.world_scan(RS.VANILLA_TREE, lambda x, z: P.in_place(x, z, 0)) if ours.get(t[:3]) != t[3] and "leaf_litter" not in t[3]]
    print("spiders check: snow/ice %d, vanilla tree blocks in the place %d%s" % (len(snow), len(trees), (" e.g. %s" % (snow + trees)[:4]) if snow or trees else ""))
    ok &= not snow and not trees
    meta = json.load(open(os.path.join(P.OUT, "spiders.json")))
    nco = len(meta["cocoons"]); nb = sum(1 for s in blocks.values() if s.startswith("minecraft:barrel") and "chests/r1/common" in s)
    nh = sum(1 for s in blocks.values() if s.startswith("minecraft:tripwire_hook")); nw = sum(1 for s in blocks.values() if s.startswith("minecraft:tripwire["))
    lw = sum(1 for s in blocks.values() if s == "minecraft:light_gray_wool")
    print("  cocoons on chains %d (15..20), barrels with loot %d (3), trip wire hooks %d (6), wire %d, live cocoon patch %d" % (nco, nb, nh, nw, lw))
    ok &= 15 <= nco <= 20 and nb == 3 and nh == 6 and nw >= 6 and lw >= 1
    lt = meta["light"]
    print("  light at noon in the deep: %d of %d feet cells with sky light <= 7 (%.1f %%), block light 0" % (lt["dark"], lt["cells"], 100 * lt["share"]))
    ok &= lt["share"] >= 0.8
    web = sum(1 for s in blocks.values() if s == "minecraft:cobweb")
    print("  web %s, cobweb blocks %d" % (meta["web"], web))
    box = (P.BOX[0] + 1, P.BOX[1] + 1, P.BOX[2] - 1, P.BOX[3] - 1)
    a0 = meta["pa"][0]; start = (a0[0], a0[1], a0[2] / 2 + 1)
    seen = reach(get, start, box, 60, 200)
    def hit(seen, x, z, y=None): return any(s[0] == x and s[1] == z and (y is None or abs(s[2] - y) < 0.6) for s in seen)
    F = meta["floor"]; lp = meta["lair_path"][0]
    goals = {"live cocoon clearing": (meta["pv"][-1][0], meta["pv"][-1][1], None), "burrow exit": (meta["lair_exit"][0], meta["lair_exit"][1], None),
             "pit floor (foot of the ledge)": (lp[0] + 1, lp[1] + 2, F + 1)}
    for k, r in enumerate(meta["remains"]): goals["cocoon with remains %d (its mouth)" % (k + 1)] = (r["front"][0], r["front"][1], None)
    for nm, (gx, gz, gy) in goals.items():
        r = hit(seen, gx, gz, gy)
        # and back: from the goal to the start (only reversible steps)
        back = False
        if r:
            g = [s for s in seen if s[0] == gx and s[1] == gz and (gy is None or abs(s[2] - gy) < 0.6)][0]
            back = hit(reach(get, g, box, 60, 200), start[0], start[1])
        print("  walk (no jumps) trail start -> %s: %s, back: %s" % (nm, "OK" if r else "NOT REACHED", "OK" if back else "NO"))
        ok &= r and back
    print("spiders check: %s" % ("OK" if ok else "FAILED"))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
