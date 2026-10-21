#!/usr/bin/env python3
"""Walk-bot routes through the Refuge (T-008 self-check). Writes server/build/walk/<name>.json for tools/walkbot.py."""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refuge, geo, tower, hall
ROOT = refuge.ROOT; OUT = os.path.join(ROOT, "server/build/walk"); os.makedirs(OUT, exist_ok=True)
nat = refuge.natural(); T = refuge.terrain(nat); gnd = refuge.ground(T, nat)
def save(name, start, pts):
    json.dump({"start": start, "points": [[round(x, 2), round(z, 2), y] for x, z, y in pts]}, open(os.path.join(OUT, name + ".json"), "w"))
F = geo.FLOOR + 1
# 1. plaza -> tower foot (graded path) -> up the tower into the top room
from lib import B
b = B("x"); tx, tz = geo.TOWER
serp = [(tx + (28 - 13 * i / 139) * math.sin(math.radians(135 + 360 * i / 139)), tz - (28 - 13 * i / 139) * math.cos(math.radians(135 + 360 * i / 139))) for i in range(140)]
R = refuge.graded_path(b, gnd, [geo.rot(0, 0, 315, 32, 0), (-60, -50)] + serp + [(tx + 9, tz + 10), (tx + 7.5, tz + 8)], 2, None, end_y=125)
pts = [(-14.5, -14.5, F)] + [(x, z, s) for (x, z), s in R]
tower.build()
for (x, z), s in tower.LINE:
    dx, dz = x - tx, z - tz; r = math.hypot(dx, dz) or 1
    p = (x + 0.5 + 0.5 * dx / r, z + 0.5 + 0.5 * dz / r, s)
    if math.hypot(p[0] - pts[-1][0], p[1] - pts[-1][1]) > 0.3: pts.append(p)
pts += [(tx + 2.5, tz + 6.5, 190), (tx + 2.5, tz + 5.5, 190), (tx + 0.5, tz + 2.5, 190)]
save("tower", [8.5, F, -14.5], pts)
# 2. Hall of Awakening: Cell -> Hall -> Font -> shaft -> corridor -> portico -> plaza
hall.build()
H = 57; pts = [(0.5, -1.5, H), (0.5, 2.5, H), (0.5, 12.5, H), (0.5, 24.5, H), (0.5, 40.5, H), (0.5, 47.5, H), (0.5, 49.5, 55), (0.5, 57.5, 55),
               (7.5, 57.5, 55), (13.5, 57.5, 55), (15.5, 57.5, 55), (28.5, 57.5, 55), (28.5, 44.5, 55)]
pts += [(x, z, y) for x, z, y in hall.SHAFT_PATH]
pts += [(28.5, 36.5, 97), (28.5, 19.5, 97), (-4.5, 19.5, 97), (-4.5, 14.5, 97), (-3.5, 14.5, 98)] + [(x + 0.5, 14.5, 98 + i) for i, x in enumerate(range(-2, 3))]
pts += [(2.5, 12.5, F), (0.5, 12.5, F), (-0.5, 11.5, F), (-0.5, 9.5, F)]
save("hall", [0.5, H, -4.5], pts)
# 3. smithy, tavern, well yard from the plaza
save("smithy", [8.5, F, 8.5], [(20.5, 14.5, F), (geo.rot(0, 0, 125, 33, 0)[0], geo.rot(0, 0, 125, 33, 0)[1], F), (40.5, 21.5, 101), (52.5, 21.5, 101), (52.5, 27.5, 101), (52.5, 32.5, 101)])
save("tavern", [-8.5, F, 8.5], [(-20.5, 14.5, F), (geo.rot(0, 0, 240, 33, 0)[0], geo.rot(0, 0, 240, 33, 0)[1], F), (-40.5, 19.5, 101), (-52.5, 19.5, 101), (-52.5, 21.5, 101), (-52.5, 25.5, 101), (-52.5, 30.5, 101)])
save("well", [4.5, F, -10.5], [(geo.rot(0, 0, 22, 26, 0)[0], geo.rot(0, 0, 22, 26, 0)[1], F), (geo.rot(0, 0, 22, 33, 0)[0], geo.rot(0, 0, 22, 33, 0)[1], F), (18.5, -32.5, 102), (32.5, -32.5, 102), (32.5, -38.5, 102), (37.5, -42.5, 102)])
print("routes:", sorted(os.listdir(OUT)))
