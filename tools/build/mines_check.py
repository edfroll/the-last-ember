#!/usr/bin/env python3
"""T-033: checks of the built Iron Ore Mines (after tools/build/mines_step.sh; server stopped or not: the region files are read):
  - the ore in the world: the box of the place + 32 round it holds exactly the numbers of HQ T-033, 2 by type and horizon (H1, H2, H3, the
    pocket), all of them in the walls of the workings, each with a face to the air of a working (mines.txt);
  - block entities of the step: chest 1, barrels 4..6, lecterns 2, sculk sensors 3;
  - no jumps (tools/build/walkcheck.py rules, both ways): the approach from the trail to the yard; the yard -> the adit -> H1 -> I12 ->
    H2 -> I23 -> H3 -> through the water to the big collapse, with all three cave-ins in their `after` state; and round each cave-in
    (its two ends joined by its bypass while it is down);
  - the shaft: platforms never more than 6 apart, every flight of ladders whole;
  - snow and vanilla trees on the yard 0.
Exit 1 on a failure."""
import json, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mines_plan as P
from walkcheck import surfaces, DIRS
ROOT = P.ROOT; OUT = P.OUT
M = json.load(open(os.path.join(OUT, "mines.json")))
ok = True
def fail(msg):
    global ok; ok = False; print("FAIL", msg)

B = {}
for line in open(os.path.join(OUT, "mines.txt")):
    x, y, z, s = line.split(" ", 3); B[(int(x), int(y), int(z))] = s.strip()
_d = np.load(os.path.join(OUT, "mines_T.npz")); T = _d["T"]; tx, tz = int(_d["x1"]), int(_d["z1"])
lv = {int(k): v for k, v in M["levels"].items()}

# ---- ore in the world
import fens_scan
fens_scan.BAN = re.compile(r"minecraft:(deepslate_)?(coal|iron|copper|gold|redstone|lapis|diamond|emerald)_ore$")
x1, z1, x2, z2 = P.PLACE
found = fens_scan.scan(os.path.join(ROOT, "server/world"), box=(x1 - 32, z1 - 32, x2 + 32, z2 + 32))
pocket = M["pocket"]
def where(x, y, z):
    if pocket[0] - 1 <= x <= pocket[3] + 1 and pocket[2] - 1 <= z <= pocket[5] + 1 and pocket[1] - 1 <= y <= pocket[4] + 1: return 4
    if abs(y - lv[1] - 2) <= 2 and not (pocket[0] - 1 <= x <= pocket[3] + 1 and pocket[2] - 1 <= z <= pocket[5] + 1 and y < lv[2]): return 1
    if abs(y - lv[2] - 2) <= 2: return 2
    if abs(y - lv[3] - 2) <= 2: return 3
    return 0
cnt = {}
for (x, y, z, n) in found:
    k = (where(x, y, z), n.replace("minecraft:", ""))
    cnt[k] = cnt.get(k, 0) + 1
    inside = x1 <= x <= x2 and z1 <= z <= z2
    face = any(B.get((x + a, y + e, z + f)) in ("minecraft:air", "minecraft:water[level=0]") for (a, e, f) in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, 1, 0), (0, -1, 0)))
    if not inside or not face: fail("ore %s at %s: %s" % (n, (x, y, z), "outside the place" if not inside else "no face to a working's air"))
want = {}
for h, lst in P.ORE.items():
    for (blk, n, _) in lst: want[(h, blk)] = want.get((h, blk), 0) + n
print("ore found:", {"%s %s" % k: v for k, v in sorted(cnt.items())})
if cnt != want: fail("ore numbers differ from HQ T-033, 2: want %s" % {"%s %s" % k: v for k, v in sorted(want.items())})

# ---- block entities
be = {"chest": 0, "barrel": 0, "lectern": 0, "sculk_sensor": 0}
for s in B.values():
    n = s.split("[")[0].split("{")[0].replace("minecraft:", "")
    if n in be: be[n] += 1
print("block entities:", be)
if be["chest"] != 1 or not 4 <= be["barrel"] <= 6 or be["lectern"] != 2 or be["sculk_sensor"] != 3: fail("block entities %s" % be)

# ---- walking
CAVES = {cv["n"]: cv for cv in M["caves"]}
AFTER = {}
for cv in M["caves"]:
    import mines_build as MB
    class _B: pass
    bb = _B(); bb.get = lambda x, y, z: B.get((x, y, z))
    for q, s in MB.cave_after(bb, cv).items(): AFTER.setdefault(cv["n"], {})[q] = s
def getter(down):
    def get(x, y, z):
        for n in down:
            s = AFTER[n].get((x, y, z))
            if s is not None: return s
        s = B.get((x, y, z))
        if s is not None:
            if re.search(r"minecraft:(water|rail|lantern|iron_chain|ladder)$", s.split("[")[0]): return "minecraft:air"
            return s
        i, j = z - tz, x - tx
        if not (0 <= i < T.shape[0] and 0 <= j < T.shape[1]): return "minecraft:barrier"
        return "minecraft:stone" if y <= T[i, j] else None
    return get
def bfs(get, start, box=(P.PLACE[0] - 16, P.PLACE[1] - 16, P.XMAX, P.PLACE[3] + 16)):
    """both ways: a step is kept only when it can be walked back (no jumps either way)"""
    OPP = {"east": "west", "west": "east", "north": "south", "south": "north"}
    seen = {start: "solid"}; q = [start]
    while q:
        x, z, s = q.pop()
        for (dx, dz), face in DIRS.items():
            nx, nz = x + dx, z + dz
            if not (box[0] <= nx <= box[2] and box[1] <= nz <= box[3]): continue
            for ns, k in surfaces(get, nx, nz, int(s) - 4, int(s) + 2):
                up = ns - s
                fwd = up <= 0.5 + 1e-9 or (up <= 1.0 + 1e-9 and k == "stair:" + face)
                back = -up <= 0.5 + 1e-9 or (-up <= 1.0 + 1e-9 and seen[(x, z, s)] == "stair:" + OPP[face])
                if fwd and back and (nx, nz, ns) not in seen: seen[(nx, nz, ns)] = k; q.append((nx, nz, ns))
    return seen
def at(seen, x, z, feet=None):
    return any(k[0] == x and k[1] == z and (feet is None or abs(k[2] - feet) < 0.6) for k in seen)

Y = M["Y"]; pa = M["pa"]
yard_pt = (pa[0][0], pa[0][1] - 1, float(Y + 1))
trail_pt = (pa[-1][0], pa[-1][1], pa[-1][2] / 2 + 1)
s0 = bfs(getter([]), trail_pt)
r = at(s0, yard_pt[0], yard_pt[1], Y + 1); print("walk (no jumps) the trail refuge -> causeway -> the yard: %s" % ("OK" if r else "NO")); ok &= r
big = M["big_rect"]; front = (big[0], big[3] + 1, float(lv[3] + 1))
sa = bfs(getter([1, 2, 3]), yard_pt)
goals = [("the adit's foot on H1", (299, -65, lv[1] + 1)), ("H2 by the shaft", (280, -70, lv[2] + 1)), ("the top of I23", (305, -45, lv[2] + 1)),
         ("H3 past the water", (276, -45, lv[3] + 1)), ("the big collapse (its front)", front), ("the shaft's foot on H3", (274, -66, lv[3] + 1))]
for nm, g in goals:
    r = at(sa, g[0], g[1], g[2]); print("walk (no jumps) the yard -> %s with all three cave-ins down: %s" % (nm, "OK" if r else "NO")); ok &= r
for n, cv in CAVES.items():
    e = cv["ends"]; a = (int(e[0][0]), int(e[0][2]), float(e[0][1])); bnd = (int(e[1][0]), int(e[1][2]), float(e[1][1]))
    sc = bfs(getter([n]), a)
    r = at(sc, bnd[0], bnd[1], bnd[2]); print("walk (no jumps) round cave-in %d while it is down (its bypass): %s" % (n, "OK" if r else "NO")); ok &= r
    sb = bfs(getter([]), a)
    r2 = at(sb, bnd[0], bnd[1], bnd[2]); ok &= r2
# the shaft
pl = M["shaft"]["platforms"]
gaps = [a - b for a, b in zip(pl, pl[1:])]
ld = M["shaft"]["ladders"]
whole = all(all("ladder" in B.get((l["x"], y, P.LADDER_Z), "") for y in range(l["bottom"] + 1, l["top"] + 1)) for l in ld)
alt = all(a["x"] != b["x"] for a, b in zip(ld, ld[1:]))
print("shaft: platforms %s (gaps %s <= 6), ladders whole %s, openings alternate %s" % (pl, gaps, whole, alt))
ok &= max(gaps) <= 6 and whole and alt
# snow and trees on the yard
fens_scan.BAN = re.compile(r"minecraft:(snow|snow_block|powder_snow|oak_log|birch_log|spruce_log|dark_oak_log|oak_leaves|birch_leaves|spruce_leaves|dark_oak_leaves)$")
yx1, yz1, yx2, yz2 = M["yard"]
bad = [(x, y, z, n) for (x, y, z, n) in fens_scan.scan(os.path.join(ROOT, "server/world"), box=(yx1, yz1, yx2, yz2)) if y > Y and B.get((x, y, z)) is None]
print("snow and vanilla trees on the yard: %d" % len(bad)); ok &= not bad
print("mines check: %s" % ("OK" if ok else "FAIL"))
sys.exit(0 if ok else 1)
