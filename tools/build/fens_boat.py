#!/usr/bin/env python3
"""T-026: can a boat go along the main channel from the outer pier to the pier of the hut? A breadth-first search over the water of
the built fens (server/build/r1/fens_post.bin: the water top; server/build/r1/fens.txt: the blocks the generator laid) for a boat
1.375 wide: a cell is open when it is water at W with nothing solid over it (W+1, W+2: air or a lily pad, which a boat breaks), and
the boat stands on an open cell when the 8 cells round it are open too (half a block of play each side). Prints the length of the
shortest such way and the narrowest place; exit 1 when there is none.
  python3 tools/build/fens_boat.py
  python3 tools/build/fens_boat.py grotto   T-034: from the hut's pier (its boats) to the foot of the stepping stones of the Grotto of the Jelly
                                            and back, over the blocks of the built world (tools/build/worldblocks.py; the server stopped)"""
import json, math, os, sys
from collections import deque
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools/build"))
from scanio import Scan, NONE
B = os.path.join(ROOT, "server/build/r1")
M = json.load(open(os.path.join(B, "fens.json"))); W = M["W"]
S = Scan(os.path.join(B, "fens_post.bin"))
BL = {}
for line in open(os.path.join(B, "fens.txt")):
    p = line.split(None, 3)
    if len(p) >= 4 and int(p[1]) in (W + 1, W + 2): BL[(int(p[0]), int(p[1]), int(p[2]))] = p[3].strip()
def free(s): return s is None or s == "minecraft:air" or "lily_pad" in s
def water(x, z):
    i, j = z - S.z0, x - S.x0
    return 0 <= i < S.h and 0 <= j < S.w and S.water[i, j] == W and free(BL.get((x, W + 1, z))) and free(BL.get((x, W + 2, z)))
def boat(x, z): return all(water(x + a, z + b) for a in (-1, 0, 1) for b in (-1, 0, 1))
if sys.argv[1:2] == ["grotto"]:
    import worldblocks
    G = json.load(open(os.path.join(B, "grotto.json")))
    wx = [c[0] for c in M["boats"]] + [G["rect"][0], G["rect"][2]]; wz = [c[2] for c in M["boats"]] + [G["rect"][1], G["rect"][3]]
    WB = worldblocks.World(min(wx) - 60, min(wz) - 10, max(wx) + 60, max(wz) + 10, W - 1, W + 3)
    def gfree(s): return s is None or s.split("[")[0] in ("minecraft:air", "minecraft:cave_air", "minecraft:lily_pad", "minecraft:hanging_roots")
    def water(x, z):
        s = WB.get(x, W, z) or ""
        return (s.startswith("minecraft:water") and "level=0" in s or "waterlogged=true" in s and "slab" not in s) and gfree(WB.get(x, W + 1, z)) and gfree(WB.get(x, W + 2, z))
    def boat(x, z): return all(water(x + a, z + b) for a in (-1, 0, 1) for b in (-1, 0, 1))
    starts = [(c[0] + a, c[2] + e) for c in M["boats"][2:] for a in range(-2, 3) for e in range(-2, 3) if boat(c[0] + a, c[2] + e)]
    fx, fy, fz = G["water_foot"]; fx, fz = int(math.floor(fx)), int(math.floor(fz))
    goals = {(fx + a, fz + e) for a in range(-3, 4) for e in range(-3, 4)}
    prev = {s: None for s in starts}; q = deque(starts); end = None
    while q:
        c = q.popleft()
        if c in goals: end = c; break
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + dx, c[1] + dz)
            if n not in prev and boat(*n): prev[n] = c; q.append(n)
    if end is None:
        print("boat grotto: NO way for a boat from the hut's pier %s to the stones of the grotto %s (%d cells reached)" % (starts[:1], (fx, fz), len(prev))); sys.exit(1)
    path = [end]
    while prev[path[-1]] is not None: path.append(prev[path[-1]])
    json.dump([[c[0] + 0.5, c[1] + 0.5] for c in path[::-1]], open(os.path.join(B, "grotto_boat.json"), "w"))
    print("boat grotto: a way for a boat (3 x 3 open water, air W+1, W+2) from the hut's pier %s to %s at the stones of the grotto: %d cells, "
          "back the same way" % (path[-1], end, len(path)))
    sys.exit(0)
main = M["main"]
start = next((x, z) for (x, z) in main[:30] if boat(x, z))
goal = next((x, z) for (x, z) in main[::-1][:30] if boat(x, z))
prev = {start: None}; q = deque([start])
while q:
    c = q.popleft()
    if c == goal: break
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        n = (c[0] + dx, c[1] + dz)
        if n not in prev and boat(*n): prev[n] = c; q.append(n)
if goal not in prev:
    print("boat: NO way from", start, "to", goal); sys.exit(1)
path = [goal]
while prev[path[-1]] is not None: path.append(prev[path[-1]])
path = path[::-1]
def width(x, z):
    """open water across the way at this cell (the narrower of the two axes)"""
    w = []
    for dx, dz in ((1, 0), (0, 1)):
        n = 1; k = 1
        while water(x + dx * k, z + dz * k) and k < 12: n += 1; k += 1
        k = 1
        while water(x - dx * k, z - dz * k) and k < 12: n += 1; k += 1
        w.append(n)
    return min(w)
narrow = min(path, key=lambda c: width(*c))
hut = M["hut"]["pier_hut"]
print("boat: a way for a boat from %s (outer pier) to %s (%.0f from the hut's pier): %d cells; the narrowest open water across the way: %d at %s" %
      (start, goal, math.hypot(goal[0] - hut[0], goal[1] - hut[2]), len(path), width(*narrow), narrow))
