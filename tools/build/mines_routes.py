#!/usr/bin/env python3
"""T-033: walk-bot routes of the Iron Ore Mines -> server/build/walk/n_*.json (tools/walkbot.py, no jumps), from server/build/r1/mines.json:
  n_in        from the trail refuge -> causeway (the approach's start) to the yard, down the adit to H1, by the inclines to H2 and H3 (past
              the shaft on H2, through the cave-ins' zones: mines_walk.sh keeps them from falling), through the knee-deep water to the
              front of the big collapse; n_in_b the same way back
  n_bypass1..3  round each cave-in down (its template `after`, mines_walk.sh lets them fall first): from one end of the zone to the other
              by its bypass, and back
  n_approach  the trail refuge -> causeway of T-022 along the place (its walked profile) and back (n_approach_b)
The climb of the shaft is the ladders: the bot does not climb them (tools/test_mines.py shaft: the client Cam).
Points: centres of cells with the feet level, reduced to the turns; every leg searched on the blocks (tools/build/walkcheck.py rules,
every step walked back too, off the edges)."""
import heapq, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from walkcheck import surfaces, DIRS
OUT = os.path.join(ROOT, "server/build/walk"); os.makedirs(OUT, exist_ok=True)
M = json.load(open(os.path.join(ROOT, "server/build/r1/mines.json")))
LV = {int(k): v for k, v in M["levels"].items()}; Y = M["Y"]
_d = np.load(os.path.join(ROOT, "server/build/r1/mines_T.npz")); _T = _d["T"]; _tx, _tz = int(_d["x1"]), int(_d["z1"])
_B = {}
for line in open(os.path.join(ROOT, "server/build/r1/mines.txt")):
    x, y, z, s_ = line.split(" ", 3); _B[(int(x), int(y), int(z))] = s_.strip()
OVER = {}
def get(x, y, z):
    s_ = OVER.get((x, y, z)) or _B.get((x, y, z))
    if s_ is not None:
        if re.search(r"minecraft:(water|iron_chain|lantern|rail|ladder)$", s_.split("[")[0]): return "minecraft:air"
        return s_
    i, j = z - _tz, x - _tx
    if not (0 <= i < _T.shape[0] and 0 <= j < _T.shape[1]): return "minecraft:barrier"
    return "minecraft:stone" if y <= _T[i, j] else None
def c(x, z, f): return [x + 0.5, z + 0.5, float(f)]
def simplify(pts):
    if len(pts) < 3: return pts
    out = [pts[0]]
    for a, b, cc in zip(pts, pts[1:], pts[2:]):
        if (round(b[0] - a[0], 3), round(b[1] - a[1], 3)) != (round(cc[0] - b[0], 3), round(cc[1] - b[1], 3)) or abs((b[2] - a[2]) - (cc[2] - b[2])) > 0.01: out.append(b)
    out.append(pts[-1]); return out
def path(a, goal):
    hh = lambda n: abs(n[0] - goal[0]) + abs(n[1] - goal[1])
    OPP = {"east": "west", "west": "east", "north": "south", "south": "north"}
    kinds = {a: "solid"}; prev = {a: None}; cost = {a: 0}; q = [(hh(a), 0, a)]; end = None
    while q:
        _, cc, (x, z, s_) = heapq.heappop(q)
        if cc > cost[(x, z, s_)]: continue
        if (x, z) == goal[:2] and (goal[2] is None or abs(s_ - goal[2]) < 0.6): end = (x, z, s_); break
        for (dx, dz), face in DIRS.items():
            nx, nz = x + dx, z + dz
            for ns, k in surfaces(get, nx, nz, int(s_) - 4, int(s_) + 2):
                up = ns - s_
                fwd = up <= 0.5 + 1e-9 or (up <= 1.0 + 1e-9 and k == "stair:" + face)
                back = -up <= 0.5 + 1e-9 or (-up <= 1.0 + 1e-9 and kinds[(x, z, s_)] == "stair:" + OPP[face])
                if fwd and back:
                    n = (nx, nz, ns)
                    edge = sum(1 for (ex, ez) in DIRS if not any(abs(t - ns) <= 0.5 for (t, _) in surfaces(get, nx + ex, nz + ez, int(ns) - 2, int(ns) + 1)))
                    nc = cc + 1 + 0.6 * edge
                    if n not in cost or nc < cost[n]: cost[n] = nc; prev[n] = (x, z, s_); kinds[n] = k; heapq.heappush(q, (nc + hh(n), nc, n))
    if end is None: raise SystemExit("no way from %s to %s" % (a, goal))
    out = []
    while end: out.append(c(end[0], end[1], end[2])); end = prev[end]
    return out[::-1]
def via(points):
    a = points[0]; out = [c(a[0], a[1], a[2])]
    for g in points[1:]:
        seg = simplify(path(a, g)); out += seg[1:]; a = (g[0], g[1], seg[-1][2])
    return out
pa = M["pa"]; f1, f2, f3 = LV[1], LV[2], LV[3]
trail = (pa[-1][0], pa[-1][1], pa[-1][2] / 2 + 1)
big = M["big_rect"]
legs = [trail, (pa[0][0], pa[0][1] - 1, float(Y + 1)), (281, -65, float(Y + 1)), (299, -65, float(f1 + 1)), (299, -42, float(f1 + 1)), (264, -42, float(f1 + 1)),
        (263, -59, float(f2 + 1)), (274, -71, float(f2 + 1)), (281, -62, float(f2 + 1)), (305, -59, float(f2 + 1)), (305, -45, float(f2 + 1)),
        (289, -45, float(f3 + 1)), (275, -45, float(f3 + 1)), (264, big[3] + 2, float(f3 + 1))]
routes = {}
r = via(legs); routes["n_in"] = r; routes["n_in_b"] = r[::-1]
import mines_build as MB
class _G: pass
for cv in M["caves"]:
    g = _G(); g.get = lambda x, y, z: _B.get((x, y, z))
    OVER.clear(); OVER.update(MB.cave_after(g, cv))
    e = cv["ends"]; a = (int(e[0][0]), int(e[0][2]), float(e[0][1])); b = (int(e[1][0]), int(e[1][2]), float(e[1][1]))
    r = via([a, b]); routes["n_bypass%d" % cv["n"]] = r + r[::-1][1:]
OVER.clear()
r1 = json.load(open(os.path.join(ROOT, "server/build/r1/r1.json")))
tr = [t for t in r1["trails"] if 7 in (t["a"], t["b"]) and "R" in (t["a"], t["b"])][0]
prof = [p for p in tr["prof"] if 236 <= p[0] <= 322]
if prof and prof[0][0] > prof[-1][0]: prof = prof[::-1]
app = [[p[0], p[1], p[2]] for p in prof]
app = [app[0]] + app[1:-1][::4] + [app[-1]]
routes["n_approach"] = app; routes["n_approach_b"] = app[::-1]
for f_ in os.listdir(OUT):
    if f_.startswith("n_") and f_.endswith(".json"): os.remove(os.path.join(OUT, f_))
for n, pts in routes.items():
    s = pts[0]
    json.dump(dict(start=[s[0], s[2], s[1]], points=[[p[0], p[1], p[2]] for p in pts[1:]]), open(os.path.join(OUT, n + ".json"), "w"))
    print(n, len(pts), "points")
