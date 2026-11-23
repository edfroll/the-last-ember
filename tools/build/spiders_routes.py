#!/usr/bin/env python3
"""T-032: walk-bot routes of the Spider Thicket -> server/build/walk/s_*.json (tools/walkbot.py, no jumps), from server/build/r1/spiders.json:
  s_in        from the trail Heather -> Garden of T-022 (the animal trail's start beside it) along the animal trail to the south edge, up
              the trail of the victims to the live cocoon's clearing; s_in_b the same way back
  s_roots     from the cocoon's clearing to the burrow's exit, down the ledge of roots to the pit's floor by the Mistress's lair and back
  s_barrels   from the start of the trail of the victims to the mouths of the 3 cocoons with remains and back
  s_approach  the approach of T-022 to the pad of bonfire 4 (from the animal trail's junction along the trail to the pad) and back
Points: centres of cells with the feet level, reduced to the turns."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spiders_plan as P
OUT = os.path.join(ROOT, "server/build/walk"); os.makedirs(OUT, exist_ok=True)
M = json.load(open(os.path.join(ROOT, "server/build/r1/spiders.json")))

def c(x, z, f): return [x + 0.5, z + 0.5, float(f)]
def simplify(pts):
    if len(pts) < 3: return pts
    out = [pts[0]]
    for a, b, cc in zip(pts, pts[1:], pts[2:]):
        if (round(b[0] - a[0], 3), round(b[1] - a[1], 3)) != (round(cc[0] - b[0], 3), round(cc[1] - b[1], 3)) or abs((b[2] - a[2]) - (cc[2] - b[2])) > 0.01: out.append(b)
    out.append(pts[-1]); return out

# the routes are searched on the blocks (the rules of tools/build/walkcheck.py: no jumps, every step walked back too, off the edges)
import numpy as np
from walkcheck import surfaces, DIRS
_d = np.load(os.path.join(ROOT, "server/build/r1/spiders_T.npz")); _T = _d["T"]; _tx, _tz = int(_d["x1"]), int(_d["z1"])
_B = {}
for line in open(os.path.join(ROOT, "server/build/r1/spiders.txt")):
    x, y, z, s_ = line.split(" ", 3); _B[(int(x), int(y), int(z))] = s_.strip()
def get(x, y, z):
    s_ = _B.get((x, y, z))
    if s_ is not None:
        if re.search(r"tripwire|leaf_litter|iron_chain", s_): return "minecraft:air"
        return s_
    i, j = z - _tz, x - _tx
    if not (0 <= i < _T.shape[0] and 0 <= j < _T.shape[1]): return "minecraft:barrier"
    return "minecraft:stone" if y <= _T[i, j] else None
def path(a, goal):
    """A* over standing cells (unit steps, the rules of walkcheck) from a = (x, z, feet) to goal = (x, z, feet or None): the cell centres
    with the feet level"""
    import heapq
    hh = lambda n: abs(n[0] - goal[0]) + abs(n[1] - goal[1])
    OPP = {"east": "west", "west": "east", "north": "south", "south": "north"}
    kinds = {a: "solid"}
    prev = {a: None}; cost = {a: 0}; q = [(hh(a), 0, a)]; end = None
    while q:
        _, cc, (x, z, s_) = heapq.heappop(q)
        if cc > cost[(x, z, s_)]: continue
        if (x, z) == goal[:2] and (goal[2] is None or abs(s_ - goal[2]) < 0.6): end = (x, z, s_); break
        for (dx, dz), face in DIRS.items():
            nx, nz = x + dx, z + dz
            for ns, k in surfaces(get, nx, nz, int(s_) - 4, int(s_) + 2):
                up = ns - s_
                fwd = up <= 0.5 + 1e-9 or (up <= 1.0 + 1e-9 and k == "stair:" + face)
                back = -up <= 0.5 + 1e-9 or (-up <= 1.0 + 1e-9 and kinds[(x, z, s_)] == "stair:" + OPP[face])    # the route is walked back too
                if fwd and back:
                    n = (nx, nz, ns)
                    # keep off walls and edges: +0.6 for every side of the cell with no standing within half a block (the bot is
                    # 0.6 wide and drifts; a path hugging a parapet catches it)
                    edge = sum(1 for (ex, ez) in DIRS if not any(abs(t - ns) <= 0.5 for (t, _) in surfaces(get, nx + ex, nz + ez, int(ns) - 2, int(ns) + 1)))
                    nc = cc + 1 + 0.6 * edge
                    if n not in cost or nc < cost[n]: cost[n] = nc; prev[n] = (x, z, s_); kinds[n] = k; heapq.heappush(q, (nc + hh(n), nc, n))
    if end is None: raise SystemExit("no way from %s to %s" % (a, goal))
    out = []
    while end: out.append(c(end[0], end[1], end[2])); end = prev[end]
    return out[::-1]
def feet(x, z):
    for (a, b_, v) in _d["walk"]:
        if a == x and b_ == z: return v / 2 + 1
    return float(_T[z - _tz, x - _tx] + 1)
def via(points):
    """a route through the given (x, z, feet or None) points, each leg searched on the blocks"""
    a = points[0]; out = [c(a[0], a[1], a[2])]
    for g in points[1:]:
        seg = simplify(path(a, g)); out += seg[1:]; a = (g[0], g[1], seg[-1][2])
    return out
pa, pv = M["pa"], M["pv"]
join = (pa[0][0], pa[0][1], pa[0][2] / 2 + 1)
south = (pv[0][0], pv[0][1], pv[0][2] / 2 + 1)
clear = (pv[-1][0], pv[-1][1], pv[-1][2] / 2 + 1)
routes = {}
s_in = via([join, south, clear]); routes["s_in"] = s_in; routes["s_in_b"] = s_in[::-1]
le = M["lair_exit"]; lm = M["nest"]["lair_mid"]; F = M["floor"]
floor = (lm[0] + 3, lm[2] + 3, float(F + 1))
r = via([clear, (le[0], le[1], None), floor]); routes["s_roots"] = r + r[::-1][1:]
legs = [south] + [(q["front"][0], q["front"][1], q["v"] / 2 + 1) for q in sorted(M["remains"], key=lambda q: q["n"])]
r = via(legs); routes["s_barrels"] = r + r[::-1][1:]
# the approach of T-022 to the pad of bonfire 4: the walked profile of the trail Heather -> Garden from the junction to its end
r1 = json.load(open(os.path.join(ROOT, "server/build/r1/r1.json")))
tr = [t for t in r1["trails"] if (t["a"], t["b"]) in ((9, 4), (4, 9))][0]
prof = [p for p in tr["prof"] if p[1] >= pa[0][1] - 1 and p[0] >= 200]
if (tr["a"], tr["b"]) == (4, 9): prof = prof[::-1]
app = [[p[0], p[1], p[2]] for p in prof]
app = [app[0]] + app[1:-1][::4] + [app[-1]] + [c(234, -258, 121)]
routes["s_approach"] = app; routes["s_approach_b"] = app[::-1]
for f_ in os.listdir(OUT):                                   # the routes of an earlier layout go (spiders_walk.sh walks every s_*.json)
    if f_.startswith("s_") and f_.endswith(".json"): os.remove(os.path.join(OUT, f_))
for n, pts in routes.items():
    s = pts[0]
    json.dump(dict(start=[s[0], s[2], s[1]], points=[[p[0], p[1], p[2]] for p in pts[1:]]), open(os.path.join(OUT, n + ".json"), "w"))
    print(n, len(pts), "points")
