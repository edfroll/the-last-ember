#!/usr/bin/env python3
"""T-027: walk-bot routes of the Cemetery and the Lodge -> server/build/walk/c_*.json (tools/walkbot.py, no jumps), from
server/build/r1/cemetery.json:
  c_lodge     the pad of bonfire 2 -> the road -> the footbridge -> the yard -> the lodge door
  c_lodge_b   the lodge door -> back to the pad
  c_down      the pad -> the gate -> the descent -> the trail -> the crypt door -> the trail -> the hill stair -> the top of the hill
  c_up        the top of the hill -> the hill stair -> the trails -> the descent -> the gate -> the pad
  c_crypt     the crypt (door open, the Magister laid to rest): the vestibule -> the stair -> the trap corridor -> the stair -> the hall ->
              the exit (bars open) -> its passage up -> out at the foot of the slope
  c_barrow_N  barrow N: in front -> the dromos -> the chamber -> the stair up -> out over the top of the mound -> down its side by the dromos
Points: centres of the cells of the ways the generator laid, with the feet level, reduced to the turns."""
import json, math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cemetery_plan as P
OUT = os.path.join(ROOT, "server/build/walk"); os.makedirs(OUT, exist_ok=True)
M = json.load(open(os.path.join(ROOT, "server/build/r1/cemetery.json")))
W = M["W"]; CR = M["crypt"]; LO = M["lodge"]; L = M["hill_level"]
def simplify(pts):
    if len(pts) <= 2: return pts
    out = [pts[0]]
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        d1 = (round(b[0] - a[0], 3), round(b[1] - a[1], 3)); d2 = (round(c[0] - b[0], 3), round(c[1] - b[1], 3))
        if d1 != d2: out.append(b)
    out.append(pts[-1]); return out
def flight(cells):
    """descent / hill cells [x, z, y, dir, kind] -> points [x+.5, z+.5, feet]"""
    return [[c[0] + 0.5, c[1] + 0.5, c[2] + 1.0] for c in cells]
pad = [118.5, 446.5, float(P.PAD_Y + 1)]
desc = simplify(flight(M["desc"]))
t1 = simplify([[c[0] + 0.5, c[1] + 0.5, c[2] / 2.0] for c in M["trails"][0]])
t2 = simplify([[c[0] + 0.5, c[1] + 0.5, c[2] / 2.0] for c in M["trails"][1]])
hill = simplify(flight(M["hill"]))
top = [(P.HILL[0] + P.HILL[2]) / 2 + 0.5, (P.HILL[1] + P.HILL[3]) / 2 - 2.5, L + 1.0]
door = CR["door"]
door_front = [door[0] + 0.5, door[2] + 2.5, W + 1.0]
down = [[124.5, 448.5, pad[2]]] + desc + t1 + [door_front] + t2 + hill[::-1] + [top]
up = [top] + hill + t2[::-1] + [door_front] + t1[::-1] + desc[::-1] + [pad]
# the lodge: the road from the pad north to the bridge, west over it, the yard, the door front
import r1_cemetery as RC
dz = LO["door"]
lodge = [pad, [115.5, 443.5, pad[2]], [115.5, RC.BRIDGE_Z[0] + 0.5, RC.TER_Y + 1.0], [109.5, RC.BRIDGE_Z[0] + 0.5, RC.TER_Y + 1.0],
         [dz[0] + 0.5, RC.BRIDGE_Z[0] + 0.5, RC.TER_Y + 1.0], [dz[0] + 0.5, dz[2] - 0.6, RC.TER_Y + 1.0]]
# the crypt: the vestibule, stair 1 (6 stairs E..E-5), the corridor (C), stair 2 (7, landing, 7), the hall (HF), the exit bars in the
# west wall, the passage up (the generator's exit path) to the foot of the slope
E = CR["E"]; C = CR["C"]; HF = CR["HF"]; cx = door[0] + 0.5; ZF = door[2]
hx1, _, hz1, hx2, _, hz2 = CR["hall"]; zc1, zc2 = CR["corridor"][2], CR["corridor"][5]
bz = CR["bars"][len(CR["bars"]) // 2][2]
crypt = [door_front, [cx, ZF - 1.5, E + 1.0], [cx, ZF - 6.5, E + 1.0], [cx, ZF - 12 + 0.5, E - 4.0], [cx, zc2 + 0.5, C + 1.0], [cx, zc1 + 0.5, C + 1.0],
         [cx, zc1 - 0.5, C + 1.0], [cx, zc1 - 6.5, C - 5.0], [cx, zc1 - 8.5, C - 6.0], [cx, zc1 - 10.5, C - 6.0], [cx, zc1 - 16.5, C - 12.0],
         [cx, hz2 + 0.5, HF + 1.0], [hx1 + 2.5, hz2 - 1.5, HF + 1.0], [hx1 + 2.5, bz + 0.5, HF + 1.0], [hx1 - 2.5, bz + 0.5, HF + 1.0]]
ep = CR["exit_path"]
crypt += simplify([[p[0] + 0.5, p[1] + 0.5, p[2] + 1.0] for p in ep]) + [[ep[-1][0] + 0.5, ep[-1][1] + 3.5, W + 1.0]]
routes = {"c_lodge": lodge, "c_lodge_b": lodge[::-1], "c_down": down, "c_up": up, "c_crypt": crypt}
# the barrows
for br in M["barrows"]:
    b = next(x for x in P.BARROWS if x[0] == br["id"])
    L2G = {v: k for k, v in P.barrow_cells(b).items()}
    def g(lx, lz): x, z = L2G[(lx, lz)]; return [x + 0.5, z + 0.5]
    Eb = br["E"]; (fx, fz), f = br["front"], br["facing"]; dx, dz = P.DIRS[f]
    out_side = [L2G[(0, 8)][0] - (dz * 3 if f in ("S", "N") else 0) * (1 if f == "S" else -1) + 0.5, L2G[(0, 8)][1] + 0.5]
    lx0 = L2G[(0, 8)]; side = (lx0[0] - L2G[(1, 8)][0], lx0[1] - L2G[(1, 8)][1])      # the direction to the left wall, outward
    off = [lx0[0] + side[0] * 4 + 0.5, lx0[1] + side[1] * 4 + 0.5]
    routes["c_barrow_%d" % br["id"]] = [[fx + dx * 2 + 0.5, fz + dz * 2 + 0.5, Eb + 1.0], g(4, 11) + [Eb + 1.0], g(4, 8) + [Eb + 1.0], g(3, 7) + [Eb + 1.0],
                                        g(3, 1) + [Eb + 1.0], g(2, 1) + [Eb + 1.0], g(2, 7) + [Eb + 7.0], g(2, 8) + [Eb + 7.0], g(0, 8) + [Eb + 7.0], g(0, 11) + [Eb + 3.0]]
for n, pts in routes.items():
    s = pts[0]
    json.dump(dict(start=[s[0], s[2], s[1]], points=[[p[0], p[1], p[2]] for p in pts[1:]]), open(os.path.join(OUT, n + ".json"), "w"))
    print(n, len(pts), "points")
