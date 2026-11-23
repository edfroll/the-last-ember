#!/usr/bin/env python3
"""T-031: checks of the built Village of Heather and the Dragon Ridge (a step of tools/build/heather_step.sh, server STOPPED):
  - no snow and no vanilla tree blocks in the village box (the saved chunks, block by block);
  - without jumps (tools/build/walkcheck.py: step <= 0.5, +1 only onto a stair from its low side) from the pad of bonfire 9 over the
    bridge and the street to the square, into every house (through the walled-up house's window, down the cellar of the house in the
    house to its small house, up the outer stair of the ladder house, the back door of the reversed house), to the church, up the bell
    tower to the ringer, along the trail to the mouth of the head; the ladder of the roof house is checked by the bot (no ladders here)
  python3 tools/build/heather_check.py        (exit 1 on a failure)"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heather_plan as P
from walkcheck import reach

def main():
    ok = True
    import r1_heather as RH
    snow = RH.world_scan(RH.SNOW, lambda x, z: P.in_village(x, z) or P.in_ridge(x, z))
    ours = {}
    for line in open(os.path.join(P.OUT, "heather.txt")):
        x, y, z, s_ = line.split(" ", 3); ours[(int(x), int(y), int(z))] = s_.strip().split("[")[0]
    trees = [t for t in RH.world_scan(RH.VANILLA_TREE, lambda x, z: P.in_village(x, z)) if ours.get(t[:3]) != t[3]]     # our dark oaks are not vanilla
    print("heather check: snow %d, vanilla tree blocks in the village %d%s" % (len(snow), len(trees), (" e.g. %s" % (snow + trees)[:4]) if snow or trees else ""))
    ok &= not snow and not trees
    gr = P.grids()
    meta = json.load(open(os.path.join(P.OUT, "heather.json")))
    import heather_plan
    T = None
    # the ground of the places as the step wrote it (r1_heather.py: heather_T.npz; a scan would read the roofs as ground)
    import numpy as np
    d = np.load(os.path.join(P.OUT, "heather_T.npz")); TT = d["T"]; tx1, tz1 = int(d["x1"]), int(d["z1"])
    blocks = {}
    for line in open(os.path.join(P.OUT, "heather.txt")):
        x, y, z, s = line.split(" ", 3); blocks[(int(x), int(y), int(z))] = s.strip()
    def get(x, y, z):
        s = blocks.get((x, y, z))
        if s is not None:
            if "_door" in s and "iron" not in s: return "minecraft:air"
            return s
        i, j = z - tz1, x - tx1
        if 0 <= i < TT.shape[0] and 0 <= j < TT.shape[1] and y <= TT[i, j]: return "minecraft:stone"
        return None
    box = (P.BOX[0] + 1, P.BOX[1] + 1, P.BOX[2] - 1, P.BOX[3] - 1)
    start = (P.HEARTH[0], P.PAD[1] + 1, float(P.PAD_Y + 1))
    seen = reach(get, start, box, 30, 160)
    def hit(x, z, y=None): return any(s[0] == x and s[1] == z and (y is None or abs(s[2] - y) < 0.6) for s in seen)
    goals = {"square (well side)": (meta["well"][0] + 3, meta["well"][2], None), "church door (outside)": (meta["church"]["door"][0], meta["church"]["door"][2], None),
             "ringer (belfry)": (int(meta["church"]["ringer"][0]), int(meta["church"]["ringer"][2]), meta["church"]["ringer"][1]),
             "sacristy chest (beside)": (meta["church"]["sacristy"]["door"][0], meta["church"]["sacristy"]["door"][2] - 1, None),
             "mouth platform": ((meta["mouth"][0] + meta["mouth"][2]) // 2, (meta["mouth"][1] + meta["mouth"][3]) // 2, meta["mouth_y"]),
             "mill door (outside)": (meta["mill"]["door"][0], meta["mill"]["door"][2], None)}
    for h in meta["houses"]:
        n = "house %d %s" % (h["k"] + 1, h["kind"])
        goals[n + " inside"] = (h["inside"][0], h["inside"][2], h["inside"][1])
        if h["kind"] == "deep": goals[n + " small house"] = (h["small_in"][0], h["small_in"][2], h["small_in"][1])
        if h["kind"] == "ladder": goals[n + " upstairs"] = (h["upper_in"][0], h["upper_in"][2], h["upper_in"][1])
        if h["kind"] == "reversed": goals[n + " back door (yard)"] = (h["back_door"][0], h["back_door"][2], h["back_door"][1])
        if h["kind"] == "roof": goals[n + " foot of the ladder"] = (h["ladder"][0], h["ladder"][2], None)
    for nm, (gx, gz, gy) in goals.items():
        r = hit(gx, gz, gy)
        print("  walk (no jumps) pad -> %s: %s" % (nm, "OK" if r else "NOT REACHED"))
        ok &= r
    # the lecterns hold their books, the two chests their loot tables
    lec = [l for l in blocks.values() if l.startswith("minecraft:lectern") and "written_book" in l]
    ch = [l for l in blocks.values() if l.startswith("minecraft:chest") and "chests/r1/common" in l]
    print("  lecterns with notes %d (6), chests with loot %d (2)" % (len(lec), len(ch)))
    ok &= len(lec) == 6 and len(ch) == 2
    print("heather check: %s" % ("OK" if ok else "FAILED"))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
