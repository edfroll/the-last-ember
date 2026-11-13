#!/usr/bin/env python3
"""T-022: walk-bot routes of the R1 trails (server/build/r1/r1.json from tools/build/r1.py) -> server/build/walk/r1_*.json
  r1_<a>_<b>.json       the trail itself (no jumps allowed: tools/walkbot.py without --jump)
  r1_<a>_<b>_stub.json  from the trail's end over the natural ground of the place to the bonfire (the place is not sculpted: --jump)
Also prints the length table (from the Refuge walls, r 200, like the card's table) -> server/build/r1/lengths.txt"""
import json, math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "server/build/walk"); os.makedirs(OUT, exist_ok=True)
m = json.load(open(os.path.join(ROOT, "server/build/r1/r1.json")))
B = {n: (x, y, z) for n, bid, x, y, z in m["bonfires"]}; NAME = {n: bid for n, bid, x, y, z in m["bonfires"]}
def name(k): return {"R": "refuge", "W": "pass"}.get(k, NAME.get(k, str(k)))
def L(pts): return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
sys.path.insert(0, os.path.join(ROOT, "tools/build")); from scanio import Scan
_scan = os.path.join(ROOT, "server/build/r1/after.bin"); GS = Scan(_scan if os.path.exists(_scan) else os.path.join(ROOT, "server/build/r1/base.bin"))
def gy(x, z): return GS.g(int(math.floor(x)), int(math.floor(z))) + 1          # stubs: the natural ground of the place (scan of the built world)
rows = []
for t in m["trails"]:
    a, b = t["a"], t["b"]; pr = t["prof"]
    if not pr: pts = []
    else:
        pts = [pr[0]] + [p for i, p in enumerate(pr[1:-1], 1) if i % 3 == 0] + [pr[-1]]
    nm = "r1_%s_%s" % (name(a), name(b))
    if pts:
        json.dump({"start": [pts[0][0], pts[0][2] + 0.2, pts[0][1]], "points": pts[1:]}, open(os.path.join(OUT, nm + ".json"), "w"))
    bx, by, bz = B[b]; stub = t["stub_b"]
    sp = [[x + 0.5, z + 0.5, gy(x, z)] for x, z in stub] + [[bx + 0.5, bz - 2.5, by]]     # ends on the respawn pad side of the hearth (z-? north stela)
    sp = [p for i, p in enumerate(sp) if i % 2 == 0 or i == len(sp) - 1]
    st = [pts[-1][0], pts[-1][2] + 0.2, pts[-1][1]] if pts else [stub[0][0] + 0.5, gy(*stub[0]) + 0.2, stub[0][1] + 0.5]
    json.dump({"start": st, "points": [[x, z, y if y is not None else -999] for x, z, y in sp]}, open(os.path.join(OUT, nm + "_stub.json"), "w"))
    trail = [tuple(p) for p in t["line"]]       # the smoothed centre line (the cells of the profile are 4-connected: their length is Manhattan)
    outside = [p for p in trail if math.hypot(*p) >= 200] if a == "R" else trail
    sa = [(x + .5, z + .5) for x, z in t["stub_a"]]; sb = [(x + .5, z + .5) for x, z in stub]
    total = L(outside) + L(sa) + L(sb)
    rows.append((name(a), name(b), t["card"], round(L(trail)), round(L(sa) + L(sb)), round(total), (round(100 * (total / t["card"] - 1)) if t["card"] else None)))
with open(os.path.join(ROOT, "server/build/r1/lengths.txt"), "w") as f:
    f.write("%-12s %-12s %6s %7s %6s %8s %6s\n" % ("from", "to", "card", "trail", "stubs", "total*", "diff%"))
    for r in rows: f.write("%-12s %-12s %6s %7s %6s %8s %6s\n" % r)
    f.write("* total = trail outside the Refuge walls (r 200) + walks over the natural ground of the places at both ends\n")
print(open(os.path.join(ROOT, "server/build/r1/lengths.txt")).read())
