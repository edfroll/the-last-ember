#!/usr/bin/env python3
"""T-034: the checks of the three treasuries of R1 on the saved world (the region files; the server stopped or saved):
  - tools/build/ogre_check.py (the den) and tools/build/grotto_check.py (the grotto, the channel, the boat);
  - the Locked Tower: the room (the floor P+23, air >= 5 over it, the chest in the niche with its lock), the ledges walked from the barbican
    to the window and back over the blocks (tools/build/walkcheck.py steps, + jumps: up one block, over a gap of 1 at the same height):
    the number of jumps over gaps 2..3; every cell of the ledges inside the rock of the colossi (castle.json rock_boxes: no pass, they
    strike) and inside the castle's zone (cyl 450 0 r 100, y 103..260); from the rift's floor under the ledges a walk (with jumps up 1
    and falls) reaches the land in the east (the trace of a death down there is reachable).
Exit 1 on a failure."""
import json, math, os, re, subprocess, sys
from collections import deque
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import worldblocks
from walkcheck import surfaces, DIRS
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "server/build/r1")
ok = True
def fail(msg):
    global ok; ok = False; print("FAIL", msg)

for s in ("ogre_check.py", "grotto_check.py"):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools/build", s)], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode: fail(s)

T = json.load(open(os.path.join(OUT, "tower.json"))); C = json.load(open(os.path.join(OUT, "castle.json")))
WB = worldblocks.World(450, 0, 492, 46, 100, 215)
def get(x, y, z): return WB.get(x, y, z)
x1, y1, z1, x2, y2, z2 = T["room"]; fl = T["floor"]
short = [(x, z) for x in range(x1, x2 + 1) for z in range(z1, z2 + 1)
         if not (get(x, fl, z) or "").endswith(("planks", "bricks", "log[axis=x]", "stone_bricks")) and "planks" not in (get(x, fl, z) or "") and "bricks" not in (get(x, fl, z) or "") and "log" not in (get(x, fl, z) or "")]
if short: fail("the floor of the room missing at %s" % short[:5])
cx, cy, cz = T["chest"]
print("tower check: room %s, the floor at %d, chest %s, lock %s" % (T["room"], fl, (get(cx, cy, cz) or "")[:30], get(cx, cy + 1, cz)))
if not (get(cx, cy, cz) or "").startswith("minecraft:chest") or get(cx, cy + 1, cz) != "minecraft:cracked_stone_bricks": fail("the chest or its lock")
air5 = all((get(477, y, 38) or "") in ("minecraft:air", "minecraft:cave_air") for y in range(fl + 1, fl + 6))
if not air5: fail("air >= 5 over the floor in the middle of the room")

# ---- the ledges: steps + jumps (up 1; over a gap of 1 at the same height)
OPP = {"east": "west", "west": "east", "north": "south", "south": "north"}
def walk(start, goal_xz, box):
    bx1, bz1, bx2, bz2 = box
    seen = {start: (None, "solid", 0)}; q = deque([start]); end = None
    while q:
        cur = q.popleft(); x, z, s = cur
        if (x, z) == goal_xz: end = cur; break
        for (dx, dz), face in DIRS.items():
            nx, nz = x + dx, z + dz
            if not (bx1 <= nx <= bx2 and bz1 <= nz <= bz2): continue
            surf = surfaces(get, nx, nz, int(s) - 3, int(s) + 2)
            for ns, k in surf:
                up = ns - s
                if up <= 0.5 + 1e-9 or (up <= 1.0 + 1e-9 and k == "stair:" + face):
                    if up >= -1.01 and (nx, nz, ns) not in seen: seen[(nx, nz, ns)] = (cur, k, 0); q.append((nx, nz, ns))
                elif up <= 1.0 + 1e-9 and (nx, nz, ns) not in seen: seen[(nx, nz, ns)] = (cur, k, 1); q.append((nx, nz, ns))   # a jump up 1
            if not any(abs(ns - s) <= 1.01 for ns, k in surf):                       # a gap: a jump over 1 to the same height or lower by 1
                fx, fz = x + 2 * dx, z + 2 * dz
                if not (bx1 <= fx <= bx2 and bz1 <= fz <= bz2): continue
                if any(not walkair(get(nx, yy, nz)) for yy in range(int(s), int(s) + 3)): continue
                for ns, k in surfaces(get, fx, fz, int(s) - 2, int(s) + 1):
                    if -1.01 <= ns - s <= 0.01 and (fx, fz, ns) not in seen: seen[(fx, fz, ns)] = (cur, k, 2); q.append((fx, fz, ns))
    if end is None: return None
    path = []; c = end
    while c: path.append((c, seen[c][2])); c = seen[c][0]
    return path[::-1]
def walkair(s): return s is None or s.split("[")[0] in ("minecraft:air", "minecraft:cave_air", "minecraft:iron_chain")
st = T["start"]; win = T["window"]
start = (int(math.floor(st[0])), int(math.floor(st[2])), float(st[1]))
p = walk(start, (win[0], win[2] + 1), (450, 20, 492, 44))
if p is None: fail("no way over the ledges from the barbican to the window")
else:
    gaps = sum(1 for c, k in p if k == 2); ups = sum(1 for c, k in p if k == 1)
    back = walk(p[-1][0], (start[0], start[1]), (450, 20, 492, 44))
    print("tower check: the ledges walked %d cells from %s to the window %s: jumps over a gap %d, jumps up %d; back: %s"
          % (len(p), start, (win[0], win[2]), gaps, ups, "OK" if back else "NO"))
    if not (2 <= gaps <= 3) or back is None: fail("the jumps over gaps (%d) or the way back" % gaps)
    json.dump([[c[0] + 0.5, c[1] + 0.5, c[2]] + ([1] if k == 2 else []) for c, k in p], open(os.path.join(OUT, "tower_walk.json"), "w"))
# ---- the rock of the colossi and the castle's zone
rock = [b for n, b in C["rock_boxes"]]
def in_rock(x, y, z): return any(b[0] <= x <= b[3] and b[1] <= y <= b[4] and b[2] <= z <= b[5] for b in rock)
outr = [(c["x"], c["f"], c["z"]) for c in T["ledges"] if not in_rock(c["x"], c["f"], c["z"])]
outz = [(c["x"], c["f"], c["z"]) for c in T["ledges"] if math.hypot(c["x"] + 0.5 - 450.5, c["z"] + 0.5 - 0.5) > 100 or not 103 <= c["f"] <= 260]
print("tower check: ledge cells outside the rock of the colossi %d, outside the castle's zone %d" % (len(outr), len(outz)))
if outr or outz: fail("ledges outside the rock %s / the zone %s" % (outr[:3], outz[:3]))
# ---- the rift: from its floor under the ledges to the land in the east (heights of the blocks; up 1 with a jump, down any)
def top(x, z):
    for y in range(214, 100, -1):
        s = get(x, y, z)
        if s and not walkair(s) and s.split("[")[0] not in ("minecraft:short_grass", "minecraft:snow", "minecraft:water"): return y
    return None
H = {(x, z): top(x, z) for x in range(455, 493) for z in range(3, 29)}
s0 = (476, 20); seen = {s0}; q = deque([s0]); east = None
while q:
    x, z = q.popleft()
    if x >= 489 and H[(x, z)] is not None and H[(x, z)] <= 140: east = (x, z); break
    for (dx, dz) in DIRS:
        n = (x + dx, z + dz)
        if n in H and n not in seen and H[n] is not None and H[(x, z)] is not None and H[n] - H[(x, z)] <= 1: seen.add(n); q.append(n)
print("tower check: from the rift's floor %s (y %s) to the east %s: %s" % (s0, H[s0], east, "OK" if east else "NO"))
if not east: fail("the rift's floor does not lead out to the east")
print("treasury check: %s" % ("OK" if ok else "FAIL"))
sys.exit(0 if ok else 1)
