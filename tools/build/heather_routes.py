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

pad = c(P.HEARTH[0] - 3, P.PAD[1] + 2, P.PAD_Y + 1)                     # on the pad, north of the bonfire, west of the line of the bridge
deck = sorted(({(x, z): v for (x, z, v) in M["deck"]}).items(), key=lambda kv: -kv[0][1])
bridge = [c(70, z, v / 2 + 1) for (x, z), v in deck if x == 70]
street = [c(x, z, v / 2 + 1) for (x, z, v) in M["street"]]
sq = M["square"]; sL = M["sL"]
# the street ends at the east edge of the square (leg 1) and starts again at its north edge (leg 2): walk across the square between
i2 = next(k for k, p in enumerate(street) if k > 0 and abs(p[0] - street[k - 1][0]) + abs(p[1] - street[k - 1][1]) > 1.01)
leg1, leg2 = street[:i2], street[i2:]
across = [c(leg1[-1][0] - 1.5, leg1[-1][1] - 0.5, sL + 1), c(leg2[0][0] - 0.5, leg1[-1][1] - 0.5, sL + 1)]
ch = M["church"]; L = ch["L"]; dx, dy, dz = ch["door"]
church_in = [c(dx, dz, L + 1), c(dx, dz - 1, L + 1), c(dx, dz - 2, L + 1)]
ax, ay, az = ch["arch"]
nave = [c(dx, az, L + 1), c(ax + 1, az, L + 1), c(ax, az, L + 1)]
steps = [c(x, z, f) for (x, z, f) in ch["steps"]]
rx, ry, rz = ch["ringer"]
top = [c(int(rx), int(rz), ry)]
h_in = [pad, c(70, P.PAD[1] + 1, P.PAD_Y + 1)] + simplify(bridge + leg1) + across + simplify(leg2) + church_in + nave + simplify(steps) + top
# houses
routes = {"h_in": h_in, "h_in_b": h_in[::-1]}
for h in M["houses"]:
    fx, fz = h["front"]; L_ = h["L"]
    f0 = c(fx, fz, L_ + 1)
    door = h["door"]
    ins = h["inside"]
    if h["kind"] == "walled":
        wx, wz = h["window_in"]
        out = [c(wx + (fx - door[0]), wz + (fz - door[1]), L_ + 1)]
        pts = [f0] + out + [c(wx, wz, L_ + 1), c(ins[0], ins[2], L_ + 1)]
    elif h["kind"] == "deep":
        pts = [f0, c(door[0], door[1], L_ + 1), c(h["stair_top"][0], h["stair_top"][2], L_ + 1), c(h["stair_bot"][0], h["stair_bot"][2], h["stair_bot"][1]),
               c(h["small_door"][0], h["small_door"][2], h["bot"] + 1), c(h["small_in"][0], h["small_in"][2], h["bot"] + 1)]
    elif h["kind"] == "ladder":
        ud = h["upper_door"]
        pts = [f0, c(door[0], door[1], L_ + 1), c(ins[0], ins[2], L_ + 1), c(door[0], door[1], L_ + 1), f0]
        # the outer stair: from the front corner along the right wall outside
        pts += [c(ud[0], ud[2], ud[1]), c(h["upper_in"][0], h["upper_in"][2], h["upper_in"][1])]
    elif h["kind"] == "roof":
        lx, ly, lz = h["ladder"]; rx_, ry_, rz_ = h["roof"]
        pts = [f0, c(door[0], door[1], L_ + 1), c(ins[0], ins[2], L_ + 1), c(door[0], door[1], L_ + 1), f0, c(lx, lz, L_ + 1), c(rx_, rz_, ry_)]
    else:
        bd = h["back_door"]
        pts = [f0, c(door[0], door[1], L_ + 1), c(ins[0], ins[2], L_ + 1), c(bd[0], bd[2], bd[1])]
    routes["h_house%d" % (h["k"] + 1)] = pts + pts[::-1][1:]
# the ridge: the church door -> east along the terrace's south edge -> round the east end to the north side -> the trail -> the mouth
cr = M["church_r"]
trail = [c(x, z, v / 2 + 1) for (x, z, v) in M["trail"]]
ne = M["neck_end"]; my = M["mouth_y"]; mo = M["mouth"]
jaw = [c(x, ne[1], my) for x in range(ne[0] + 1, mo[0] + 3)] + [c((mo[0] + mo[2]) // 2, (mo[1] + mo[3]) // 2, my)]
round_church = [c(dx, cr[3], L + 1), c(cr[2], cr[3], L + 1), c(cr[2], cr[1], L + 1)]
h_ridge = [c(dx, dz, L + 1)] + round_church + simplify(trail) + simplify(jaw)
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
for n, pts in routes.items():
    s = pts[0]
    json.dump(dict(start=[s[0], s[2], s[1]], points=[[p[0], p[1], p[2]] for p in pts[1:]]), open(os.path.join(OUT, n + ".json"), "w"))
    print(n, len(pts), "points")
