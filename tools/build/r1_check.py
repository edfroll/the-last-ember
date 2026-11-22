#!/usr/bin/env python3
"""T-022 checks on a scan of the built world (tools/terrain.sh scan ... server/build/r1/after.bin):
  wall     the Wall's profiles (docs/design/heightmaps/the_wall_profiles.csv): ridge ±3, Wall body 0 (ice scree on the faces ignored)
  seam     steps > 4 between neighbouring ground columns in the low part of the sculpted relief (and how many are steeper than natural)
  plots    places of locations untouched: ground of every plot column equals the natural scan (except bonfire pads and the ledge)
  water    no water on the rift floor, no water in rewritten columns that was not there
  places   T-023/T-024: the build step of a place changed nothing outside it: scans <id>_pre.bin / <id>_post.bin (r1_apply.sh)
Usage: python3 tools/build/r1_check.py [after.bin] [wall seam plots water] | places [weepers maze cemetery+lodge]"""
import csv, os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import Scan, NONE
import r1
ROOT = r1.ROOT
args = sys.argv[1:]; path = args[0] if args and args[0].endswith(".bin") else os.path.join(ROOT, "server/build/r1/after.bin")
what = [a for a in args if not a.endswith(".bin")] or ["wall", "seam", "plots", "water"]
BUILT = {"weepers", "maze", "garden", "fens", "cemetery", "lodge", "castle", "grove"}      # places built by their own tools (T-023+): not natural any more, checked by `places`
if what[:1] == ["places"]:
    W0 = r1.World(); bad = False
    for pid in what[1:] or ["weepers"]:
        ids = pid.split("+"); pid = ids[0]           # T-027: places built in one step (cemetery+lodge): one pair of scans, outside of all of them
        pre = Scan(os.path.join(r1.OUT, f"{pid}_pre.bin")); post = Scan(os.path.join(r1.OUT, f"{pid}_post.bin"))
        X, Z = np.meshgrid(np.arange(pre.x0, pre.x0 + pre.w), np.arange(pre.z0, pre.z0 + pre.h))
        outside = np.ones(X.shape, bool)
        for q in W0.plots:
            if q["id"] in ids: outside &= r1.plot_dist(q, X, Z) - q["m"] > 0
        d = outside & ((pre.ground != post.ground) | (pre.top != post.top) | (pre.water != post.water))
        inside_changed = int((~outside & ((pre.ground != post.ground) | (pre.top != post.top))).sum())
        print(f"places: {pid}: {int(outside.sum())} columns around the place checked, {int(d.sum())} changed (inside the place {inside_changed} changed)")
        if d.any(): zz, xx = np.nonzero(d); print("   e.g.", [(int(x + pre.x0), int(z + pre.z0)) for z, x in list(zip(zz, xx))[:8]]); bad = True
    print("OK" if not bad else "CHECK"); sys.exit(1 if bad else 0)
S = Scan(path); ok = True
def g(x, z): return int(S.ground[z - S.z0, x - S.x0])
if "wall" in what:
    from PIL import Image
    mk = np.array(Image.open(os.path.join(ROOT, "docs/design/heightmaps/the_wall_material.png")))
    rows = list(csv.reader(open(os.path.join(ROOT, "docs/design/heightmaps/the_wall_profiles.csv"))))
    zs = [int(c.split("=")[1]) for c in rows[0][1:]]; worst_r = worst_w = 0; n = 0; bad = []; inplot = []
    Wp = r1.World()
    for r in rows[1:]:
        x = int(r[0])
        for z, e in zip(zs, r[1:]):
            if (-860 <= z <= -840 or -899 <= z <= -880) and mk[z + 1000, x + 1000] != 100: continue     # ice scree strips on both faces
            if Wp.pd[z - Wp.z0, x - Wp.x0] <= 16: inplot.append((x, z)); continue                 # the place of a location (Сгоревшая Дозорная): natural ground
            d = abs(g(x, z) - int(e)); n += 1
            if mk[z + 1000, x + 1000] == 100: worst_w = max(worst_w, d)
            else:
                worst_r = max(worst_r, d)
                if d > 3: bad.append((x, z, g(x, z), int(e)))
    print(f"wall profiles: {n} points; ridge max |diff| {worst_r} (tolerance 3), Wall body max |diff| {worst_w} (tolerance 0)" + (f"; out: {bad[:6]}" if bad else "") + f"; {len(inplot)} points inside places of locations or their 16-block seam skipped {inplot[:8]}")
    ok &= worst_r <= 3 and worst_w == 0
if "plots" in what or "seam" in what or "water" in what:
    W = r1.World(); N = W.nat
if "plots" in what:
    inside = W.pd <= 0
    for p in W.plots:
        if p["id"] in BUILT: inside &= ~(r1.plot_dist(p, W.X, W.Z) - p["m"] <= 0)
    # allowed inside plots: bonfire pads and their slopes, approaches to them (HQ review T-022, 1), the shortcut ledge
    # bonfire pads with their slopes and the approach strips (trail + berm + shoulders): server/build/r1/allow.npz from r1.py
    allow = np.load(os.path.join(r1.OUT, "allow.npz"))["allow"].copy()
    allow[-207 - W.z0:-187 - W.z0, -398 - W.x0:-372 - W.x0] = True
    m = inside & ~allow & ((S.flags & 16) == 0)
    base = W.base.ground
    diff = m & (S.ground != base)
    print(f"plots: {int(m.sum())} columns checked, {int(diff.sum())} differ from the ground before R1 (trees and trails excluded? no: ground only)")
    if diff.any():
        zz, xx = np.nonzero(diff); print("   e.g.", [(int(x + W.x0), int(z + W.z0), int(S.ground[z, x]), int(base[z, x])) for z, x in list(zip(zz, xx))[:8]])
    ok &= not diff.any()
if "water" in what:
    fl = (S.water != NONE) & (np.abs(W.Z - 650) < 22) & (S.water < 20)
    print(f"water: {int(fl.sum())} wet columns on the rift floor (y < 20)")
    ok &= fl.sum() == 0
if "seam" in what:
    gd = S.ground.astype(int); bad = 0; worst = 0
    sel = W.touch if hasattr(W, "touch") else None
    # seam strips: columns written by the R1 tool whose height is within 16 of the natural ground (feet of the ridges, Wall map seam)
    import r1 as R
    gy = np.abs(np.diff(gd, axis=0)); gx = np.abs(np.diff(gd, axis=1))
    d0 = np.abs(gd - W.base.ground)
    seam = (d0 > 0) & (d0 <= 16) & (np.abs(W.Z - 650) > 30) & (W.X > -1000)
    sy = seam[1:, :] & seam[:-1, :]; sx = seam[:, 1:] & seam[:, :-1]
    b = W.base.ground.astype(int); by = np.abs(np.diff(b, axis=0)); bx = np.abs(np.diff(b, axis=1))
    big = int((gy[sy] > 4).sum() + (gx[sx] > 4).sum()); tot = int(sy.sum() + sx.sum())
    my = sy & (gy > 4) & (gy > by); mx = sx & (gx > 4) & (gx > bx); new = int(my.sum() + mx.sum())
    print(f"seam: {tot} neighbour pairs in the low part of the sculpted relief, {big} with a step > 4, of them {new} steeper than the natural ground there"
          f" ({100 * new / max(tot, 1):.2f}%, max {int(max(gy[my].max(initial=0), gx[mx].max(initial=0)))})")
print("OK" if ok else "CHECK")
