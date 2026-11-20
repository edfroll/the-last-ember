#!/usr/bin/env python3
"""T-028: walk-bot routes of the castle approaches -> server/build/walk/k_*.json (tools/walkbot.py, no jumps), from the plan
(tools/build/castle_plan.py; the build is server/build/r1/castle.json):
  k_down   the pad of bonfire 7 -> the descent -> the causeway (past the sword) -> the pier between the colossi (the walker carries the
           seal) -> the stair (F1 tunnel, F2 tunnel, the rest platform, F3, F4) -> the arch -> bonfire 8 -> the bridge -> the gate
  k_up     back: the gate -> ... -> the pad of bonfire 7
  k_sand   the way out of the knock zone: from the water up the sandy ramp onto the causeway and along it to the foot of the descent
Points: [x, z, feet]."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import castle_plan as P
OUT = os.path.join(ROOT, "server/build/walk"); os.makedirs(OUT, exist_ok=True)
W = P.W
def pt(x, z, y): return [x + 0.5, z + 0.5, float(y)]
# the descent: lane by lane (landing W, flight, turn landing), feet = block level + 1
xw1, xw2, xf1, xf2, xe1, xe2 = P.DESC_X
cells, order, end = P.descent()
desc = [pt(P.PAD7[2] - 1, P.DESC_Z0, P.PAD7_Y + 1)]
zc = P.DESC_Z0; y = P.PAD7_Y
for k, n in enumerate(P.DESC_FLIGHTS):
    east = k % 2 == 0
    a, b_ = (xw2, xe1 + 1) if east else (xe1, xw2 - 1)
    desc.append(pt(a, zc, y + 1)); y -= n; desc.append(pt(b_, zc, y + 1))     # the landing n lower
    if k < len(P.DESC_FLIGHTS) - 1: zc -= 4; desc.append(pt(b_, zc, y + 1))
cz = [(r[1] + r[3]) // 2 for r in P.CAUSEWAY]; cx = [(r[0] + r[2]) // 2 for r in P.CAUSEWAY]
cause = [pt(P.CAUSEWAY[0][0] + 1, cz[0], W + 2), pt(cx[1], cz[0], W + 2), pt(cx[1], cz[2], W + 2), pt(P.CAUSEWAY[2][2], cz[2], W + 2)]
A, Bl = P.LANE_A, P.LANE_B; za, zb = (A[0] + A[1]) // 2, (Bl[0] + Bl[1]) // 2
st, top = P.stair()
lv = {}
for (x, z1, z2, yy, kd, f) in st:
    for z in range(z1, z2 + 1): lv.setdefault((x, z), []).append(yy)
F = P.FACE_X
stair = [pt(P.PIER[0] + 1, za, W + 2), pt(F - 1, za, W + 2),
         pt(F + 11, za, 128 + 1), pt(F + 13, za, 128 + 1), pt(F + 13, zb, 128 + 1), pt(F + 11, zb, 129 + 1),
         pt(F, zb, 140 + 1), pt(F - 3, zb, 140 + 1), pt(F - 3, za, 140 + 1), pt(F - 1, za, 140 + 1),
         pt(F + 11, za, 152 + 1), pt(F + 13, za, 152 + 1), pt(F + 13, zb, 152 + 1), pt(F + 11, zb, 153 + 1),
         pt(F + 1, zb, P.PRED_Y + 1), pt(F + 1, Bl[1] + 2, P.PRED_Y + 1)]
h8 = P.HEARTH8; bx = (P.BRIDGE_X[0] + P.BRIDGE_X[1]) // 2
head = [pt(F + 1, P.PAD8[3] + 4, P.PRED_Y + 1), pt(bx, P.PAD8[3] + 4, P.PRED_Y + 1),
        pt(bx, P.RIFT[3], P.PRED_Y + 1), pt(bx, P.RIFT[3] + 1, P.PRED_Y + 1)]
down = desc + cause + stair + head
up = down[::-1]
ks = P.KNOCK_PTS[0]; sx = (P.SAND[0] + P.SAND[2]) // 2
sand = [[ks[0], ks[1], W - 0.5], pt(sx, P.SAND[3] + 1, W - 4), pt(sx, P.SAND[1], W + 0.5), pt(P.SAND[0], P.SAND[1], W + 1.5), pt(P.SAND[0], cz[0], W + 2),
        pt(P.CAUSEWAY[0][0] + 1, cz[0], W + 2)]
routes = {"k_down": down, "k_up": up, "k_sand": sand}
for n, pts in routes.items():
    s = pts[0]
    json.dump(dict(start=[s[0], s[2], s[1]], points=[[p[0], p[1], p[2]] for p in pts[1:]]), open(os.path.join(OUT, n + ".json"), "w"))
    print(n, len(pts), "points")
