#!/usr/bin/env python3
"""T-023: walk-bot routes of the Circle of the Weepers -> server/build/walk/w_*.json (tools/walkbot.py, no jumps):
  w_b6_centre   bonfire 6 -> the circle (between two statues) -> the foot of the tree
  w_stair       the bottom of the stair in the ravine -> up the stair -> the circle
  w_spur        the pass trail (W-6) -> the spur -> the mouth of the ravine -> along the stream -> the stair -> the circle
  w_rubble      the circle -> down the stair and the ravine -> the spur -> the pass trail to the west -> through the rubble of the pass
                (closed: stuck at the rubble; after gate/open west_pass: through)
Expected heights: the scan of the built place (server/build/r1/weepers_post.bin), the trail profile of r1.json outside it."""
import json, math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools/build")); from scanio import Scan
OUT = os.path.join(ROOT, "server/build/walk"); os.makedirs(OUT, exist_ok=True)
S = Scan(os.path.join(ROOT, "server/build/r1/weepers_post.bin")); W = json.load(open(os.path.join(ROOT, "server/build/r1/weepers.json")))
R1 = json.load(open(os.path.join(ROOT, "server/build/r1/r1.json")))
def gy(x, z):
    try: return S.g(int(math.floor(x)), int(math.floor(z))) + 1
    except IndexError: return -999
def line(a, b, step=1.0):
    n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step)); return [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(1, n + 1)]
def path(*pts):
    out = []
    for a, b in zip(pts, pts[1:]): out += line(a, b)
    return out
def stair_y(z):
    """the stair: 21 steps north from y 90 at z -163 to y 110 at z -183 (stand on the step: +1), landing z -184..-186 at 111"""
    bz = math.floor(z)
    if bz > -163: return gy(-447.5, z)
    return min(111, 91 + (-163 - bz))
CX, CZ = W["centre"][0], W["centre"][2]
def gap(deg, r=14.0): a = math.radians(deg); return (CX + 0.5 + r * math.sin(a), CZ + 0.5 - r * math.cos(a))
SX = -447.5                                           # the middle of the stair
CIRCLE_W = [(SX, -185.5), (-440.5, -185.5), gap(292.5, 15), gap(292.5, 9), (-426.5, -183.5)]   # the landing -> the west gap -> the tree
def pts_y(pts, stair=False):
    out = []
    for x, z in pts:
        y = stair_y(z) if stair and abs(x - SX) < 2 and -187 < z < -159 else gy(x, z)
        out.append([round(x, 2), round(z, 2), y])
    return out
def save(name, start, pts):
    json.dump({"start": [start[0], start[2] + 0.2 if len(start) == 3 else 0, start[1]] if False else start, "points": pts}, open(os.path.join(OUT, name + ".json"), "w"))
    print(name, len(pts), "points")
# bonfire 6 -> centre
b6 = [b for b in R1["bonfires"] if b[0] == 6][0]; bx, by, bz = b6[2], b6[3], b6[4]
p = path((bx - 4.5, bz + 0.5), gap(67.5, 18), gap(67.5, 14), gap(67.5, 8), (CX + 6.5, CZ - 1.5))
save("w_b6_centre", [bx - 3.5, by + 0.2, bz + 0.5], pts_y(p))
# the stair
p = path((SX, -160.5), (SX, -185.5)) + path(*CIRCLE_W)
save("w_stair", [SX, 90.2, -160.5], pts_y(p, stair=True))
# the spur from the pass trail
FLOOR_X = -452.5
p = path((-451.5, -127.5), (FLOOR_X, -146.5), (FLOOR_X, -161.5), (SX, -161.5), (SX, -185.5)) + path(*CIRCLE_W)
save("w_spur", [-451.5, gy(-451.5, -127.5) + 0.2, -127.5], pts_y(p, stair=True))
# the circle -> the rubble of the pass (the W-6 trail back to the west)
t = [t for t in R1["trails"] if t["a"] == "W"][0]; k = t["cells"].index([-452, -127])
trail = [[x, z, y + 1] for x, z, y in reversed(t["prof"][:k + 1])][::2]
p = path(*reversed(CIRCLE_W)) + path((SX, -185.5), (SX, -161.5), (FLOOR_X, -161.5), (FLOOR_X, -146.5), (-451.5, -127.5))
save("w_rubble", [-424.5, 111.2, -184.5], pts_y(p, stair=True) + trail)
