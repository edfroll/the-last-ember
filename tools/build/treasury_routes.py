#!/usr/bin/env python3
"""T-034: walk-bot routes of the treasuries of R1 -> server/build/walk/{o,g,t}_*.json (tools/walkbot.py), searched on the blocks of the
saved world (tools/build/worldblocks.py; run after a save) with the rules of tools/build/walkcheck.py (every step walked back too):
  o_approach   from the trail refuge -> bonfire 2 (its start of the chain) along the signs of the chain of bones to the mouth by the oak:
               the natural ground of a hill country: steps up of a full block need a jump (tools/build/treasury_walk.sh runs it with
               --jump: the bot jumps where it is stuck; the count is reported); o_approach_b back
  o_in         from the mouth down the stair to the front of the bed (no jumps); o_in_b back up
  g_in         from the water at the foot of the stepping stones up to the front of the chest on the ledge (no jumps); g_in_b back
  t_ledges     from the barbican along the ledges to the window and into the room (3 jumps over the gaps: points [x, z, y, 1]; the walk
               of tools/build/treasury_check.py, server/build/r1/tower_walk.json); t_ledges_b back"""
import heapq, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import worldblocks
from walkcheck import surfaces, DIRS
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "server/build/walk"); os.makedirs(OUT, exist_ok=True)
R1 = os.path.join(ROOT, "server/build/r1")
O = json.load(open(os.path.join(R1, "ogre.json"))); G = json.load(open(os.path.join(R1, "grotto.json"))); TW = json.load(open(os.path.join(R1, "tower_walk.json")))
OPP = {"east": "west", "west": "east", "north": "south", "south": "north"}

def path(get, a, goal, box, jumps=False):
    """A* over standing places from a = (x, z, feet) to goal = (x, z, feet or None); jumps: a step up of a full block allowed (cost 3)"""
    bx1, bz1, bx2, bz2 = box
    hh = lambda n: abs(n[0] - goal[0]) + abs(n[1] - goal[1])
    kinds = {a: "solid"}; prev = {a: None}; cost = {a: 0}; q = [(hh(a), 0, a)]; end = None
    while q:
        _, cc, (x, z, s_) = heapq.heappop(q)
        if cc > cost[(x, z, s_)]: continue
        if (x, z) == goal[:2] and (goal[2] is None or abs(s_ - goal[2]) < 0.6): end = (x, z, s_); break
        for (dx, dz), face in DIRS.items():
            nx, nz = x + dx, z + dz
            if not (bx1 <= nx <= bx2 and bz1 <= nz <= bz2): continue
            for ns, k in surfaces(get, nx, nz, int(s_) - 4, int(s_) + 2):
                up = ns - s_
                fwd = up <= 0.5 + 1e-9 or (up <= 1.0 + 1e-9 and k == "stair:" + face)
                back = -up <= 0.5 + 1e-9 or (-up <= 1.0 + 1e-9 and kinds[(x, z, s_)] == "stair:" + OPP[face])
                jump = jumps and not fwd and up <= 1.0 + 1e-9 or jumps and not back and -up <= 1.0 + 1e-9
                if (fwd and back) or jump:
                    if up < -3: continue
                    n = (nx, nz, ns); nc = cc + 1 + (3 if jump and not (fwd and back) else 0)
                    if n not in cost or nc < cost[n]: cost[n] = nc; prev[n] = (x, z, s_); kinds[n] = k; heapq.heappush(q, (nc + hh(n), nc, n))
    if end is None: raise SystemExit("no way from %s to %s" % (a, goal))
    out = []
    while end: out.append([end[0] + 0.5, end[1] + 0.5, end[2]]); end = prev[end]
    return out[::-1]

def simplify(pts):
    if len(pts) < 3: return pts
    out = [pts[0]]
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        if (round(b[0] - a[0], 3), round(b[1] - a[1], 3)) != (round(c[0] - b[0], 3), round(c[1] - b[1], 3)) or abs((b[2] - a[2]) - (c[2] - b[2])) > 0.01: out.append(b)
    out.append(pts[-1]); return out

def feet(get, x, z, lo, hi, near=None):
    """the standing level in a column (the highest, or the one nearest to `near`: the ground, not a lantern or a sign over it)"""
    s = surfaces(get, x, z, lo, hi)
    if not s: return None
    return (min(s, key=lambda q: abs(q[0] - near)) if near is not None else max(s))[0]

routes = {}
# ---- the Ogre: the approach (natural ground, jumps), the stair
ts = O["trail_start"]; ex = O["exit"]; F = O["F"]
xs = [c[0] for c in O["way"]] + [e[0] for e in ex]; zs = [c[1] for c in O["way"]] + [e[1] for e in ex]
Wo = worldblocks.World(min(xs) - 6, min(zs) - 6, max(xs) + 6, max(zs) + 6, 120, 230)
def go(x, y, z):
    s = Wo.get(x, y, z)
    if s and (s.startswith("minecraft:water") or "leaves" in s.split("[")[0]): return "minecraft:barrier"
    return s
a = (ts[0], ts[1], feet(go, ts[0], ts[1], 150, 225, near=O["signs"][0][1]))
m = (ex[0][0], ex[0][1], float(O["top"]))          # the first exit row, under the fallen trunk (not on top of it)
legs = [a] + [(s[0], s[2], None) for s in O["signs"][::3]] + [m]
pts = [[a[0] + 0.5, a[1] + 0.5, a[2]]]; cur = a
box = (min(xs) - 5, min(zs) - 5, max(xs) + 5, max(zs) + 5)
for g in legs[1:]:
    seg = path(go, cur, g, box, jumps=True); pts += seg[1:]; cur = (int(seg[-1][0] - 0.5), int(seg[-1][1] - 0.5), seg[-1][2])
routes["o_approach"] = simplify(pts)
mouth = cur
bx1, bz1, bx2, bz2 = O["bed"]
bed = (bx2 + 2, (bz1 + bz2) // 2, None)
cx = [c[0] for c in O["stair"]] + [O["cave"][0], O["cave"][2]]; cz = [c[1] for c in O["stair"]] + [O["cave"][1], O["cave"][3]]
Wc = worldblocks.World(min(cx) - 3, min(cz) - 3, max(cx) + 6, max(cz) + 6, F - 2, F + 25)
seg = path(Wc.get, mouth, bed, (min(cx) - 2, min(cz) - 2, max(cx) + 5, max(cz) + 5))
routes["o_in"] = simplify(seg); routes["o_in_b"] = routes["o_in"][::-1]
routes["o_approach_b"] = routes["o_approach"][::-1]
# ---- the Grotto: the water at the stones -> the chest
W = G["W"]; x1, z1, x2, z2 = G["rect"]
Wg = worldblocks.World(x1 - 2, z1 - 2, x2 + 2, z2 + 2, W - 2, W + 6)
def gg(x, y, z):
    s = Wg.get(x, y, z)
    if s and (s.startswith("minecraft:water") or s.startswith("minecraft:glow_lichen")): return "minecraft:air"
    return s
fx, fy, fz = G["water_foot"]; ch = G["chest"]; face = {"south": (0, 1), "north": (0, -1), "east": (1, 0), "west": (-1, 0)}[G["chest_facing"]]
st = (int(fx // 1), int(fz // 1), feet(gg, int(fx // 1), int(fz // 1), W - 1, W + 1))
seg = path(gg, st, (ch[0] + face[0], ch[2] + face[1], float(W + 2)), (x1, z1, x2, z2))
routes["g_in"] = simplify(seg); routes["g_in_b"] = routes["g_in"][::-1]
# ---- the Tower: the ledges (the walk of treasury_check with its jumps), then into the room
pts = [p[:3] + ([1] if len(p) > 3 else []) for p in TW]
pts.append([477.5, 33.5 + 2, pts[-1][2]])
routes["t_ledges"] = pts
back = []
rev = pts[::-1]
for i, p in enumerate(rev):
    q = list(p[:3])
    if i > 0 and len(rev[i - 1]) > 3: q.append(1)           # the jump lands here going back (the gap is before it)
    back.append(q)
routes["t_ledges_b"] = back
for f_ in os.listdir(OUT):
    if f_[:2] in ("o_", "g_", "t_") and f_.endswith(".json"): os.remove(os.path.join(OUT, f_))
for n, p in routes.items():
    s = p[0]
    json.dump(dict(start=[s[0], s[2], s[1]], points=[list(q) for q in p[1:]]), open(os.path.join(OUT, n + ".json"), "w"))
    print(n, len(p), "points", "(jumps %d)" % sum(1 for q in p if len(q) > 3) if n.startswith("t_") else "")
