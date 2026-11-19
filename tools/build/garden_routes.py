#!/usr/bin/env python3
"""T-025: walk-bot routes of the Garden of Silence -> server/build/walk/g_*.json (tools/walkbot.py):
  g_in       bonfire 4 -> in front of the gardener's house -> along the path -> the west door of the orangery -> the steps of the basin
             -> next to the pedestal of the key (no jumps)
  g_out      the same way back to bonfire 4 (no jumps)
  g_heart_N  from the nearest cell of the path to a cell from which heart N can be hit (within 2 blocks of its trunk, at most 3 below
             the heart), with jumps (tools/walkbot.py --jump): the hearts are off the path
The ways are shortest paths on a column grid built from the scan after the garden (server/build/r1/garden_post.bin: the ground) and
the blocks the generator wrote (server/build/r1/garden.txt: trunks, walls, the furniture); a step is up to 1/2 block without jumps
(1 with), down at most 3. The routes are reduced to their turns."""
import heapq, json, math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools/build"))
from scanio import Scan
B = os.path.join(ROOT, "server/build/r1"); OUT = os.path.join(ROOT, "server/build/walk"); os.makedirs(OUT, exist_ok=True)
M = json.load(open(os.path.join(B, "garden.json")))
S = Scan(os.path.join(B, "garden_post.bin"))
BL = {}
for line in open(os.path.join(B, "garden.txt")):
    p = line.split(None, 3)
    if len(p) >= 4: BL[(int(p[0]), int(p[1]), int(p[2]))] = p[3].strip()
PASS = ("air", "carpet", "eyeblossom", "short_grass", "fern", "hanging_moss", "leaf_litter", "wildflowers", "bush", "sign", "torch", "lantern",
        "pressure_plate", "button", "vine", "flower", "dandelion", "poppy", "lily", "tulip", "daisy", "cornflower", "orchid", "allium", "bluet")
def ground(x, z):
    i, j = z - S.z0, x - S.x0
    if not (0 <= i < S.h and 0 <= j < S.w): return None
    return int(S.ground[i, j])
def block(x, y, z):
    b = BL.get((x, y, z))
    if b is not None: return b
    g = ground(x, z)
    return "minecraft:stone" if g is not None and y <= g else "minecraft:air"
def passable(b): return any(k in b for k in PASS) and "trapdoor" not in b
def height(b):
    """the top of a block one stands on, from its bottom"""
    if passable(b): return None
    if "slab" in b and "type=bottom" in b: return 0.5
    if "carpet" in b: return 0.0625
    if "candle" in b or "chain" in b or "bars" in b or "fence" in b or "wall" in b or "pane" in b: return 9      # do not stand on those
    return 1.0
STAND = {}
def stands(x, z):
    """the feet heights in column x z: every support with 2 free blocks above it, from 6 above the ground to 10 below (roofs, floors)"""
    if (x, z) in STAND: return STAND[(x, z)]
    g = ground(x, z); r = []
    if g is not None:
        for y in range(g + 6, g - 10, -1):
            h = height(block(x, y, z))
            if h is None or h > 1: continue
            if all(passable(block(x, yy, z)) for yy in (y + 1, y + 2)): r.append(y + h)
    STAND[(x, z)] = r
    return r
def near(x, z, hp, up):
    """the feet height in x z one gets to from height hp (up to up higher, at most 3 lower), the closest; None if none"""
    c = [h for h in stands(x, z) if -3 <= h - hp <= up + 1e-6]
    return min(c, key=lambda h: abs(h - hp)) if c else None
def route(a, ha, goal, up):
    """A* over (column, height) from a at height ha to the first cell for which goal(x, z, h) is true; up = the highest step"""
    a = (a[0], a[1], ha); best = {a: 0}; prev = {a: None}; q = [(0, a)]
    while q:
        c, p = heapq.heappop(q)
        if goal(*p): break
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            hn = near(p[0] + dx, p[1] + dz, p[2], up)
            if hn is None: continue
            if dx and dz:                                    # no corner cutting: both side cells must be walkable at about that height
                s1, s2 = near(p[0] + dx, p[1], p[2], up), near(p[0], p[1] + dz, p[2], up)
                if s1 is None or s2 is None or abs(s1 - p[2]) > 0.5 or abs(s2 - p[2]) > 0.5 or abs(hn - p[2]) > 0.5: continue
            n = (p[0] + dx, p[1] + dz, hn)
            nc = c + (1.414 if dx and dz else 1.0) + 0.6 * abs(hn - p[2])
            if nc < best.get(n, 1e9): best[n] = nc; prev[n] = p; heapq.heappush(q, (nc, n))
    else: raise SystemExit("no way from %s" % (a,))
    out = [p]
    while prev[out[-1]] is not None: out.append(prev[out[-1]])
    return out[::-1]
def turns(cells):
    pts = [cells[0]]
    for i in range(1, len(cells) - 1):
        d1 = (cells[i][0] - cells[i - 1][0], cells[i][1] - cells[i - 1][1]); d2 = (cells[i + 1][0] - cells[i][0], cells[i + 1][1] - cells[i][1])
        if d1 != d2 or abs(cells[i][2] - cells[i - 1][2]) > 0.01: pts.append(cells[i])
    pts.append(cells[-1])
    return [[x + 0.5, z + 0.5, h] for x, z, h in pts]
def save(name, start, pts):
    json.dump({"start": start, "points": pts}, open(os.path.join(OUT, name + ".json"), "w")); print(name, len(pts), "points")
    return pts
HEARTH = M["hearth"]; PATH = [(c[0], c[1], c[2]) for c in M["path"]]
PX, PZ = M["pedestal"][0], M["pedestal"][2]
def at(t): return lambda x, z, h: (x, z) == (t[0], t[1])
start = (HEARTH[0] + 4, HEARTH[2]); hs = max(stands(*start))         # on the pad of bonfire 4, east of the fire
way = route(start, hs, at(PATH[0]), 0.5)
for i in range(len(PATH) - 1): way += route(PATH[i][:2], PATH[i][2], at(PATH[i + 1]), 0.5)[1:]
def near_ped(x, z, h): return max(abs(x - PX), abs(z - PZ)) == 1 and h < M["floor"] + 0.6 and "candle" not in block(x, int(h), z)
way += route(PATH[-1][:2], PATH[-1][2], near_ped, 0.5)[1:]
save("g_in", [start[0] + 0.5, hs + 0.2, start[1] + 0.5], turns(way))
back = way[::-1]; e = back[0]
save("g_out", [e[0] + 0.5, e[2] + 0.2, e[1] + 0.5], turns(back))
for h in M["hearts"]:
    hx, hy, hz = h["x"], h["y"], h["z"]
    def ok(x, z, f, hx=hx, hy=hy, hz=hz): return max(abs(x - hx), abs(z - hz)) <= 2 and (x, z) != (hx, hz) and hy - 3 <= f <= hy + 1
    p0 = min(PATH, key=lambda c: (c[0] - hx) ** 2 + (c[1] - hz) ** 2)
    r = route(p0[:2], p0[2], ok, 1.0)
    save("g_heart_%d" % h["id"], [p0[0] + 0.5, p0[2] + 0.2, p0[1] + 0.5], turns(r))
    print("   heart %d: %d cells from path cell %s, ends %s (heart y %d)" % (h["id"], len(r), p0, r[-1], hy))
