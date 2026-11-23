#!/usr/bin/env python3
"""T-031: walk-bot routes of the Village of Heather and the Dragon Ridge -> server/build/walk/h_*.json (tools/walkbot.py, no jumps),
from server/build/r1/heather.json:
  h_in         the pad of bonfire 9 -> the bridge -> the street -> the square -> the church door -> the nave -> the tower stair -> the
               ringer's place at the bell; h_in_b the same way back
  h_house<N>   from the street in front of house N into it and back: through the window of the walled-up house, down the cellar into the
               small house of the house in the house, up the outer stair of the ladder house, up the ladder onto the roof table, out of
               the reversed house through the door in the hearth into its yard
  h_ridge      the church door -> round the church to the start of the trail -> the trail along the seams -> the jaw passage -> the mouth
               platform; h_ridge_b back
  h_approach   the approaches of T-022 to the pad of bonfire 9 (from the south, the place's seam) and back (h_approach_b)
Points: centres of cells with the feet level, reduced to the turns."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heather_plan as P
OUT = os.path.join(ROOT, "server/build/walk"); os.makedirs(OUT, exist_ok=True)
M = json.load(open(os.path.join(ROOT, "server/build/r1/heather.json")))

def c(x, z, f): return [x + 0.5, z + 0.5, float(f)]
def simplify(pts):
    if len(pts) < 3: return pts
    out = [pts[0]]
    for a, b, cc in zip(pts, pts[1:], pts[2:]):
        if (round(b[0] - a[0], 3), round(b[1] - a[1], 3)) != (round(cc[0] - b[0], 3), round(cc[1] - b[1], 3)) or abs((b[2] - a[2]) - (cc[2] - b[2])) > 0.01: out.append(b)
    out.append(pts[-1]); return out

# houses: the way in is searched on the blocks (the rules of tools/build/walkcheck.py: no jumps), from the street cell in front of the
# door to the goal of the house's oddity; the ladder of the roof house is climbed by the bot from the cell at its foot
import numpy as np
from walkcheck import surfaces, DIRS
_d = np.load(os.path.join(ROOT, "server/build/r1/heather_T.npz")); _T = _d["T"]; _tx, _tz = int(_d["x1"]), int(_d["z1"])
_B = {}
for line in open(os.path.join(ROOT, "server/build/r1/heather.txt")):
    x, y, z, s_ = line.split(" ", 3); _B[(int(x), int(y), int(z))] = s_.strip()
def get(x, y, z):
    s_ = _B.get((x, y, z))
    if s_ is not None:
        if "_door" in s_: return "minecraft:air"
        if "campfire" in s_: return "minecraft:stone_slab[type=bottom]"      # 7/16 high: walked onto like a slab
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
                    if n not in cost or cc + 1 < cost[n]: cost[n] = cc + 1; prev[n] = (x, z, s_); kinds[n] = k; heapq.heappush(q, (cc + 1 + hh(n), cc + 1, n))
    if end is None: raise SystemExit("no way from %s to %s" % (a, goal))
    out = []
    while end: out.append(c(end[0], end[1], end[2])); end = prev[end]
    return out[::-1]
pad = (P.HEARTH[0], P.PAD[1] + 2, float(P.PAD_Y + 1))          # on the pad, north of the bonfire, on the line of the bridge
sq = M["square"]; sL = M["sL"]; ch = M["church"]; L = ch["L"]; dx, dy, dz = ch["door"]
wx, wy, wz = M["well"]
rx, ry, rz = ch["ringer"]
legs = [(wx + 3, wz + 3, float(sL + 1)), (dx, dz, float(L + 1)), (int(rx), int(rz), float(ry))]
h_in = [c(pad[0], pad[1], pad[2])]; a = pad
for g in legs:
    seg = simplify(path(a, g)); h_in += seg[1:]; a = (g[0], g[1], seg[-1][2])
routes = {"h_in": h_in, "h_in_b": h_in[::-1]}
for h in M["houses"]:
    fx, fz = h["front"]; L_ = h["L"]
    st_ = [s_ for (s_, k) in surfaces(get, fx, fz, L_ - 3, L_ + 3)]
    a = (fx, fz, min(st_, key=lambda v: abs(v - (L_ + 1))))
    k = h["kind"]
    if k == "walled": g = (h["inside"][0], h["inside"][2], h["inside"][1])
    elif k == "deep": g = (h["small_in"][0], h["small_in"][2], h["small_in"][1])
    elif k == "ladder": g = (h["upper_in"][0], h["upper_in"][2], h["upper_in"][1])
    elif k == "reversed": g = (h["back_door"][0], h["back_door"][2], h["back_door"][1])
    else: g = (h["ladder"][0], h["ladder"][2], None)
    pts = simplify(path(a, g))
    if k == "ladder":            # first the room under the low ceiling, then out and up the outer stair
        pts = simplify(path(a, (h["inside"][0], h["inside"][2], h["inside"][1]))) + simplify(path(a, (h["inside"][0], h["inside"][2], h["inside"][1])))[::-1][1:] + pts[1:]
    if k == "roof":              # first in and out of the door, then up the ladder onto the roof table
        pts = simplify(path(a, (h["inside"][0], h["inside"][2], h["inside"][1]))) + simplify(path(a, (h["inside"][0], h["inside"][2], h["inside"][1])))[::-1][1:] + pts[1:]
        rx_, ry_, rz_ = h["roof"]; pts = pts + [c(rx_, rz_, ry_)]
    routes["h_house%d" % (h["k"] + 1)] = pts + pts[::-1][1:]
# the ridge: the church door -> the trail -> the jaw passage -> the mouth platform (searched on the blocks)
mo = M["mouth"]; my = M["mouth_y"]
h_ridge = simplify(path((dx, dz, float(L + 1)), ((mo[0] + mo[2]) // 2, (mo[1] + mo[3]) // 2, float(my))))
routes["h_ridge"] = h_ridge; routes["h_ridge_b"] = h_ridge[::-1]
# the approaches of T-022 (south of the pad): the trail r1_heather->r1_garden and refuge->r1_heather end at (70, -411)
r1 = json.load(open(os.path.join(ROOT, "server/build/r1/r1.json")))
tr = next((t for t in r1["trails"] if 9 in (t["a"], t["b"]) and any(abs(p[0] - 70) < 1 and abs(p[1] + 411) < 2 for p in t["prof"])), None)
if tr:
    prof = [p for p in tr["prof"] if abs(p[0] - 70) <= 30 and -411 <= p[1] <= -380]
    prof.sort(key=lambda p: -p[1])
    app = [[p[0], p[1], p[2]] for p in prof]
    app = [app[0]] + app[1:-1][::4] + [app[-1]] + [c(70, P.PAD[3] - 1, P.PAD_Y + 1)]
    routes["h_approach"] = app; routes["h_approach_b"] = app[::-1]
for f_ in os.listdir(OUT):                                   # the routes of an earlier layout go (heather_walk.sh walks every h_*.json)
    if f_.startswith("h_") and f_.endswith(".json"): os.remove(os.path.join(OUT, f_))
for n, pts in routes.items():
    s = pts[0]
    json.dump(dict(start=[s[0], s[2], s[1]], points=[[p[0], p[1], p[2]] for p in pts[1:]]), open(os.path.join(OUT, n + ".json"), "w"))
    print(n, len(pts), "points")
