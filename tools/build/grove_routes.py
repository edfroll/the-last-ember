#!/usr/bin/env python3
"""T-030: walk-bot routes of the Mushroom Grove -> server/build/walk/v_*.json (tools/walkbot.py, no jumps), from server/build/r1/grove.json:
  v_in        the pad of bonfire 10 -> the path down to the terrace -> the door -> the study -> the stair (south and west walls) -> the bedroom in
              the stem -> the observatory under the cap (the Advisor's night point); v_out the same way back
  v_garden    the pad -> through the gap of the bench at its north edge into the garden -> the stump and the bee nest -> back to the pad
  v_approach  the approaches of T-022 in the grove (both share the z 78 line in the circle): from the east edge of the place to the pad
              (v_approach) and back (v_approach_b)
Points: centres of cells with the feet level, reduced to the turns."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grove_plan as P
OUT = os.path.join(ROOT, "server/build/walk"); os.makedirs(OUT, exist_ok=True)
M = json.load(open(os.path.join(ROOT, "server/build/r1/grove.json")))
HX, HZ = M["house"]; L = M["L"]; F1 = M["floors"]["f1"]; F2 = M["floors"]["f2"]; F3 = M["floors"]["f3"]; ng = M["night"]
pad = [P.PAD[0] + 2.5, P.HZ + 0.5, P.PAD_Y + 1.0]              # on the pad, west of the bonfire (r 3), on the line of the path
path = sorted(M["path"], key=lambda p: -p[0])
pz = P.HZ
line = [[x + 0.5, z + 0.5, f] for (x, z, f) in path if z == pz]
door_out = [HX + 5.5, pz + 0.5, L + 1.0]
def c(dx, dz, f): return [HX + dx + 0.5, HZ + dz + 0.5, float(f)]      # the centre of the cell (HX + dx, HZ + dz)
inside = [c(3, 0, F1), c(3, 3, F1)]
stair = [c(2, 3, F1 + 1), c(-2, 3, F1 + 5), c(-3, 3, F1 + 5), c(-3, 2, F1 + 6), c(-3, -1, F1 + 9), c(-3, -2, F2)]
upstairs = [c(-3, -3, F2), c(-2, -3, F2 + 1), c(1, -3, F2 + 4), c(2, -3, F3), c(5, -3, F3), [ng[0] + 0.5, ng[2] + 0.5, float(F3)]]   # bedroom -> observatory
v_in = [pad, [P.PAD[0] + 0.5, pz + 0.5, P.PAD_Y + 1.0]] + line + [door_out] + inside + stair + upstairs
v_out = v_in[::-1]
g = M["garden"]
v_garden = [pad, [P.HEARTH[0] + 0.5, P.PAD[1] + 0.5, P.PAD_Y + 1.0], [P.HEARTH[0] + 0.5, P.GARDEN[3] - 0.5, P.PAD_Y + 1.0],
            [P.HEARTH[0] + 0.5, P.PAD[1] + 0.5, P.PAD_Y + 1.0], [P.GARDEN[0] + 2.5, P.PAD[1] + 0.5, P.PAD_Y + 1.0],
            [P.GARDEN[0] + 2.5, P.GARDEN[3] - 0.5, P.PAD_Y + 1.0], [P.GARDEN[0] + 2.5, P.PAD[1] + 0.5, P.PAD_Y + 1.0], pad]
r1 = json.load(open(os.path.join(ROOT, "server/build/r1/r1.json")))
tr = next(t for t in r1["trails"] if (t["a"], t["b"]) == (10, 5))
prof = [p for p in tr["prof"] if p[0] <= -366 and abs(p[1] - 78.5) < 0.6]
appr = [[p[0], p[1], p[2]] for p in sorted(prof, key=lambda p: p[0], reverse=True)]     # from the east edge of the place west to the pad
def simplify(pts):
    out = [pts[0]]
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        if (round(b[0] - a[0], 3), round(b[1] - a[1], 3)) != (round(c[0] - b[0], 3), round(c[1] - b[1], 3)) or abs((b[2] - a[2]) - (c[2] - b[2])) > 0.01: out.append(b)
    out.append(pts[-1]); return out
v_app = [appr[0]] + appr[1:-1][::5] + [appr[-1]] + [[P.PAD[2] - 1.5, 78.5, P.PAD_Y + 1.0]]          # straight along z 78 onto the pad (east part, off the bonfire)
routes = {"v_in": v_in, "v_out": v_out, "v_garden": v_garden, "v_approach": v_app, "v_approach_b": v_app[::-1]}
for n, pts in routes.items():
    s = pts[0]
    json.dump(dict(start=[s[0], s[2], s[1]], points=[[p[0], p[1], p[2]] for p in pts[1:]]), open(os.path.join(OUT, n + ".json"), "w"))
    print(n, len(pts), "points")
