#!/usr/bin/env python3
"""T-034: checks of the built Ogre's Den (after tools/build/ogre_step.sh; the region files are read, the server stopped):
  - the cover of HQ T-034, 2 on the world: over every column of the cave >= 8 solid blocks between the roof and the first air (or the
    sky); round it, at every level of its air, >= 6 solid to the first air horizontally (the stair's tunnel excepted);
  - no light sources in the cave and the stair; one chest with its lock (brown wool) over it;
  - no jumps both ways (tools/build/walkcheck.py rules): from the front of the bed to the exit of the mouth, and back.
Exit 1 on a failure."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import worldblocks
from walkcheck import surfaces, DIRS
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
M = json.load(open(os.path.join(ROOT, "server/build/r1/ogre.json")))
ok = True
def fail(msg):
    global ok; ok = False; print("FAIL", msg)

x1, z1, x2, z2 = M["cave"]; F = M["F"]
xs = [c[0] for c in M["stair"]] + [e[0] for e in M["exit"]]; zs = [c[1] for c in M["stair"]] + [e[1] for e in M["exit"]]
W = worldblocks.World(min(x1, min(xs)) - 10, min(z1, min(zs)) - 10, max(x2, max(xs)) + 10, max(z2, max(zs)) + 10, F - 10, F + 60)
def get(x, y, z): return W.get(x, y, z)
AIRY = re.compile(r"minecraft:(air|cave_air|void_air|water|lava|snow|short_grass|tall_grass|fern|.*_carpet|hanging_roots|vine)$")
def airy(s): return s is None or bool(AIRY.match(s.split("[")[0]))
tunnel = set()
for (x, z, y, *_) in M["stair"]:
    for a in range(-1, 2):
        for c in range(-1, 2): tunnel.add((x + a, z + c))

# ---- the cover
worst_up = 99; worst_side = 99; where = None
cave_cols = {tuple(int(v) for v in k.split(",")): c for k, c in M["ceil"].items()}
for (x, z), c in cave_cols.items():
    n = 0; y = c + 1
    while not airy(get(x, y, z)) and n < 40: n += 1; y += 1
    if n < worst_up: worst_up = n; where = (x, z)
if worst_up < 8: fail("rock over the roof of the cave: %d at %s (< 8)" % (worst_up, where))
for (x, z), c in cave_cols.items():
    for (dx, dz) in DIRS:
        if (x + dx, z + dz) in cave_cols: continue
        for y in range(F + 1, c + 1):
            n = 0
            while n < 12 and not airy(get(x + dx * (n + 1), y, z + dz * (n + 1))) and (x + dx * (n + 1), z + dz * (n + 1)) not in tunnel \
                    and (x + dx * (n + 1), z + dz * (n + 1)) not in cave_cols: n += 1
            if (x + dx * (n + 1), z + dz * (n + 1)) in tunnel or (x + dx * (n + 1), z + dz * (n + 1)) in cave_cols: continue
            if n < worst_side: worst_side = n; where = (x, y, z, dx, dz)
if worst_side < 6: fail("rock to the side of the cave: %d at %s (< 6)" % (worst_side, where))
print("ogre check: rock over the roof >= %d, to the sides >= %d" % (worst_up, worst_side))

# ---- light and the chest
lit = []; chests = 0
for x in range(x1 - 2, x2 + 3):
    for z in range(z1 - 2, z2 + 3):
        for y in range(F, F + 12):
            s = get(x, y, z) or ""
            if re.search(r"torch|lantern|glowstone|shroomlight|froglight|lava|sea_lantern|lit=true|glow_lichen|magma", s): lit.append((x, y, z, s))
            if s.startswith("minecraft:chest"): chests += 1
for (x, z, y, *_) in M["stair"]:
    for yy in range(y, y + 5):
        s = get(x, yy, z) or ""
        if re.search(r"torch|lantern|glowstone|lava|lit=true|glow_lichen", s): lit.append((x, yy, z, s))
if lit: fail("light sources: %s" % lit[:4])
cx, cy, cz = M["chest"]
if chests != 1 or not (get(cx, cy, cz) or "").startswith("minecraft:chest") or (get(cx, cy + 1, cz) or "") != "minecraft:brown_wool":
    fail("chest %d, at the point %s, over it %s" % (chests, get(cx, cy, cz), get(cx, cy + 1, cz)))
print("ogre check: light sources 0: %s; chests %d, the lock over it: %s" % (not lit, chests, get(cx, cy + 1, cz)))

# ---- no jumps: bed front <-> the exit
OPP = {"east": "west", "west": "east", "north": "south", "south": "north"}
def reach(start, box, both=True):
    seen = {start: "solid"}; q = [start]
    bx1, bz1, bx2, bz2 = box
    while q:
        x, z, s = q.pop()
        for (dx, dz), face in DIRS.items():
            nx, nz = x + dx, z + dz
            if not (bx1 <= nx <= bx2 and bz1 <= nz <= bz2): continue
            for ns, k in surfaces(get, nx, nz, int(s) - 3, int(s) + 2):
                up = ns - s
                fwd = up <= 0.5 + 1e-9 or (up <= 1.0 + 1e-9 and k == "stair:" + face)
                back = -up <= 0.5 + 1e-9 or (-up <= 1.0 + 1e-9 and seen[(x, z, s)] == "stair:" + OPP[face])
                if fwd and (back or not both) and (nx, nz, ns) not in seen: seen[(nx, nz, ns)] = k; q.append((nx, nz, ns))
    return seen
bx1, bz1, bx2, bz2 = M["bed"]
start = None
for (x, z) in [(bx2 + 2, (bz1 + bz2) // 2), (bx2 + 3, (bz1 + bz2) // 2), (bx2 + 2, bz1 + 1)]:
    for s, k in surfaces(get, x, z, F, F + 3):
        start = (x, z, s); break
    if start: break
box = (min(x1, min(xs)) - 2, min(z1, min(zs)) - 2, max(x2, max(xs)) + 2, max(z2, max(zs)) + 2)
r = reach(start, box)
ex = M["exit"]
got = [k for k in r if (k[0], k[1]) in {tuple(e) for e in ex[2:4]}]
print("ogre check: walk (no jumps, both ways) bed %s -> the exit row 2 of the mouth: %s" % (start, "OK" if got else "NO"))
if not got: fail("no way without jumps from the bed to the mouth")
print("ogre check: %s" % ("OK" if ok else "FAIL"))
sys.exit(0 if ok else 1)
