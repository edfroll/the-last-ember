"""T-030: the layout of the Mushroom Grove of the Advisor (Р1): relief decisions (the grove stays on its slope, HQ T-030, 1), the house
terrace, the garden by the pad of bonfire 10, the path from the pad to the door, the places of the giant mushrooms, the poplars and the
6 faces. Read by tools/build/r1_grove.py (the blocks); only planning here.

Everything is computed from the ground before the place (base.bin + the R1 frame terrain.bin), the same on every run."""
import math, os, struct, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import Scan, NONE
from lib import h as hsh

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "server/build/r1")
CX, CZ, R = -420, 60, 45                  # the place `grove circle -420 60 45` (tools/build/r1_plots.txt)
MARGIN = 16
BOX = (CX - R - MARGIN - 10, CZ - R - MARGIN - 10, CX + R + MARGIN + 10, CZ + R + MARGIN + 10)   # the grids: place + seam + 10
PAD = (-410, 67, -397, 80)                 # the pad of bonfire 10 (T-022: 14 x 14, ground 136, feet 137): never written
PAD_Y = 136
HEARTH = (-404, 137, 72)
# the house (HQ T-030: stem 9 x 9, height 26, cap 21 across), its terrace and door (east, to the pad)
HX, HZ = -428, 72
STEM = (HX - 4, HZ - 4, HX + 4, HZ + 4)    # x -432..-424, z 68..76
TERRACE = (HX - 5, HZ - 5, HX + 7, HZ + 5)    # -433..-421 x 67..77: the stem + 1, the porch 3 east (the best of a search: least earth work)
DOOR = (HX + 4, HZ)                        # the door in the east wall
CAP_R = 10.5
HOUSE_H = 26
GARDEN = (-410, 61, -399, 66)              # north of the pad, at the pad's level (the bench at the pad's north edge)
PATH_Z = (HZ - 1, HZ + 1)                  # the path: 3 wide, from the pad's west edge (x -411) to the terrace (x -420)
PATH_X = (TERRACE[2] + 1, PAD[0] - 1)
APPROACHES = ("r1_weepers->r1_grove", "r1_grove->r1_fens")
MAX_TERRACE = 10                           # HQ T-030, 1
MAX_PATH = 4
FILL_REACH = 4                             # cells of 1:1 embankment round a flat
WALL_AT = 3                                # a flat whose neighbour lies more than this lower gets a retaining wall

def in_circle(x, z, r=R): return (x - CX) ** 2 + (z - CZ) ** 2 <= r * r
def in_place(x, z): return in_circle(x, z, R + MARGIN)
def in_rect(r, x, z): return (x >= r[0]) & (x <= r[2]) & (z >= r[1]) & (z <= r[3])
def on_pad(x, z): return PAD[0] <= x <= PAD[2] and PAD[1] <= z <= PAD[3]

def approach_cells():
    """the cells of the two approaches of T-022 inside the place: the polylines of r1_plots.txt, 3 wide"""
    pts = []
    for l in open(os.path.join(ROOT, "tools/build/r1_plots.txt"), encoding="utf-8"):
        if l.startswith("# approach ") and l.split()[2].rstrip(":") in APPROACHES:
            pts.append([tuple(int(v) for v in p.split(",")) for p in l.split(":", 1)[1].split()])
    cells = set()
    for line in pts:
        for (ax, az), (bx, bz) in zip(line, line[1:]):
            n = max(abs(bx - ax), abs(bz - az), 1)
            for k in range(n + 1):
                x = round(ax + (bx - ax) * k / n); z = round(az + (bz - az) * k / n)
                for a in (-1, 0, 1):
                    for c in (-1, 0, 1):
                        if in_place(x + a, z + c) and not on_pad(x + a, z + c): cells.add((x + a, z + c))
    return cells

def grids():
    x1, z1, x2, z2 = BOX; X, Z = np.meshgrid(np.arange(x1, x2 + 1), np.arange(z1, z2 + 1))
    def grid(s, a): return a[z1 - s.z0:z2 - s.z0 + 1, x1 - s.x0:x2 - s.x0 + 1].astype(np.int32)
    base = Scan(os.path.join(OUT, "base.bin"))
    nat = grid(base, base.ground)
    d = open(os.path.join(OUT, "terrain.bin"), "rb").read(); assert d[:4] == b"LETA"
    tx0, tz0, tw, th = struct.unpack("<4i", d[4:20]); TH = np.frombuffer(d, "<i2", tw * th, 20).reshape(th, tw).astype(np.int32)
    fr = TH[z1 - tz0:z2 - tz0 + 1, x1 - tx0:x2 - tx0 + 1]
    before = np.where(fr != NONE, fr, nat)
    trees = grid(base, base.top) - nat
    pad = in_rect(PAD, X, Z)
    circle = (X - CX) ** 2 + (Z - CZ) ** 2 <= R * R
    place = (X - CX) ** 2 + (Z - CZ) ** 2 <= (R + MARGIN) ** 2
    gr = dict(X=X, Z=Z, x1=x1, z1=z1, before=before, nat=nat, frame=fr != NONE, pad=pad, circle=circle, place=place, trees=trees,
              bwater=grid(base, base.water))
    pre_path = os.path.join(OUT, "grove_pre.bin")
    if os.path.exists(pre_path):
        pre = Scan(pre_path); gr.update(live=grid(pre, pre.ground), top=grid(pre, pre.top), lwater=grid(pre, pre.water))
    # the frame cut the approaches (trails 6->10, 10->5) and their 1:1 banks by blocks (r1.txt), not by its terrain: the real ground before
    # the place is the scan of the first run; kept in grove_before.npz (keyed by the frame's inputs) so that a re-run on the built place
    # starts from the same ground
    import hashlib
    key = hashlib.sha1(open(os.path.join(OUT, "terrain.bin"), "rb").read() + open(os.path.join(OUT, "base.bin"), "rb").read()).hexdigest()
    cp = os.path.join(OUT, "grove_before.npz")
    if os.path.exists(cp) and str(np.load(cp)["key"]) == key: before = np.load(cp)["before"].astype(np.int32)
    elif "live" in gr: before = gr["live"].copy(); np.savez_compressed(cp, before=before, key=key)
    gr["before"] = before
    return gr
def ix(gr, x, z): return z - gr["z1"], x - gr["x1"]
def B4(gr, x, z): return int(gr["before"][ix(gr, x, z)])

# ---------------------------------------------------------------- relief
def path_profile(gr, L):
    """heights in half blocks for x = PATH_X[1] (by the pad) .. PATH_X[0] (by the terrace): from the pad's 2*136 down to 2*L, at most
    one half block per cell, |level - ground| <= MAX_PATH on every cell of the 3 wide path; None when impossible (a DP)"""
    xs = list(range(PATH_X[1], PATH_X[0] - 1, -1))
    lo = []
    for x in xs:
        g = [B4(gr, x, z) for z in range(PATH_Z[0], PATH_Z[1] + 1)]
        lo.append((2 * (max(g) - MAX_PATH), 2 * (min(g) + MAX_PATH)))
    start = 2 * PAD_Y; best = {start: (0, [])}
    for k, x in enumerate(xs):
        nb = {}
        for hh, (cost, seq) in best.items():
            for d in (0, -1):
                v = hh + d
                if v < 2 * L: continue
                if not (lo[k][0] <= v <= lo[k][1]): continue
                c = cost + abs(v / 2 - np.mean([B4(gr, x, z) for z in range(PATH_Z[0], PATH_Z[1] + 1)]))
                if v not in nb or c < nb[v][0]: nb[v] = (c, seq + [v])
        best = nb
    if 2 * L not in best: return None
    return dict(zip(xs, best[2 * L][1]))

def terrace_level(gr):
    """the house terrace: the level with the least earth work that keeps every terrace cell within MAX_TERRACE of the ground and lets
    the path reach it"""
    cells = [B4(gr, x, z) for x in range(TERRACE[0], TERRACE[2] + 1) for z in range(TERRACE[1], TERRACE[3] + 1)]
    out = []
    for L in range(PAD_Y - 12, PAD_Y + 1):
        if max(abs(c - L) for c in cells) > MAX_TERRACE: continue
        prof = path_profile(gr, L)
        if prof is None: continue
        out.append((sum(abs(c - L) for c in cells), L, prof))
    if not out: return None
    out.sort(); return out[0][1], out[0][2]

def relief(gr):
    """T (ground top per column), flat {(x, z): height in half blocks} for the terrace, the garden and the path, the masks; cones 1:1 round
    the flats (cut and fill) like the slopes of T-022, the pad and the approaches kept"""
    X, Z = gr["X"], gr["Z"]; bf = gr["before"]
    tl = terrace_level(gr)
    if tl is None: raise SystemExit("STOP (HQ T-030, 1): the house terrace needs more than %d of cut/fill or the path cannot reach it" % MAX_TERRACE)
    L, prof = tl
    flat = {}
    for x in range(TERRACE[0], TERRACE[2] + 1):
        for z in range(TERRACE[1], TERRACE[3] + 1): flat[(x, z)] = 2 * L
    for x in range(GARDEN[0], GARDEN[2] + 1):
        for z in range(GARDEN[1], GARDEN[3] + 1): flat[(x, z)] = 2 * PAD_Y
    for x, v in prof.items():
        for z in range(PATH_Z[0], PATH_Z[1] + 1): flat[(x, z)] = v
    T = bf.copy()
    for (x, z), v in flat.items(): T[ix(gr, x, z)] = v // 2
    # retaining walls where the ground falls away more than WALL_AT beside a flat (a 1:1 fill there would run 10..20 cells down the
    # slope): the ring cell becomes a wall of mossy cobblestone up to the flat's level with a parapet; such flat cells give no fill cone
    walled = set(); wall = {}
    for (x, z), v in flat.items():
        for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + a, z + c)
            if q in flat or on_pad(*q) or not in_circle(*q): continue
            if B4(gr, *q) < v // 2 - WALL_AT: walled.add((x, z)); wall[q] = max(wall.get(q, -999), v // 2)
    for q, y in wall.items(): T[ix(gr, *q)] = y
    # the cones: up(x) = min over flats (and the pad) of level + chebyshev distance, low(x) = max of level - distance
    src = np.full(T.shape, -999); srcu = np.full(T.shape, 9999)
    for (x, z), v in flat.items():
        srcu[ix(gr, x, z)] = (v + 1) // 2
        if (x, z) not in walled: src[ix(gr, x, z)] = v // 2
    for q, y in wall.items(): srcu[ix(gr, *q)] = y
    src[gr["pad"]] = PAD_Y; srcu[gr["pad"]] = PAD_Y
    up, low = srcu.copy(), src.copy()
    for k in range(14):        # cuts: full 1:1 banks; fills: at most FILL_REACH cells of embankment (a fill down a steep slope stops there)
        pu = np.pad(up, 1, constant_values=9999); pl = np.pad(low, 1, constant_values=-999); mu = up.copy(); ml = low.copy()
        for dz in (0, 1, 2):
            for dx in (0, 1, 2):
                mu = np.minimum(mu, pu[dz:dz + T.shape[0], dx:dx + T.shape[1]] + 1)
                if k < FILL_REACH: ml = np.maximum(ml, pl[dz:dz + T.shape[0], dx:dx + T.shape[1]] - 1)
        up, low = mu, ml
    fl = np.zeros(T.shape, bool)
    for (x, z) in flat: fl[ix(gr, x, z)] = True
    app = np.zeros(T.shape, bool)
    for (x, z) in approach_cells(): app[ix(gr, x, z)] = True
    wm = np.zeros(T.shape, bool)
    for q in wall: wm[ix(gr, *q)] = True
    cone = gr["circle"] & ~fl & ~gr["pad"] & ~app & ~wm
    T = np.where(cone, np.clip(bf, low, up), T)
    T = np.where(gr["pad"] | app, bf, T)
    return dict(T=T, L=L, prof=prof, flat=flat, flatm=fl, app=app, wall=wall, wallm=wm)

def checks(gr, rl):
    """HQ T-030, 1: the stop conditions (raise) and the numbers for the report"""
    T, bf = rl["T"], gr["before"]
    ter = in_rect(TERRACE, gr["X"], gr["Z"])
    msgs = []
    tmax = int(np.abs(T - bf)[ter].max())
    if tmax > MAX_TERRACE: raise SystemExit("STOP: terrace cut/fill %d > %d" % (tmax, MAX_TERRACE))
    pth = np.zeros(T.shape, bool)
    for x in range(PATH_X[0], PATH_X[1] + 1):
        for z in range(PATH_Z[0], PATH_Z[1] + 1): pth[ix(gr, x, z)] = True
    pmax = max(abs(rl["flat"][(x, z)] / 2 - B4(gr, x, z)) for x in range(PATH_X[0], PATH_X[1] + 1) for z in range(PATH_Z[0], PATH_Z[1] + 1))
    if pmax > MAX_PATH: raise SystemExit("STOP: path cut/fill %.1f > %d" % (pmax, MAX_PATH))
    d_door = max(0, PAD[0] - DOOR[0]) if DOOR[0] < PAD[0] else 0
    d_door = math.hypot(max(PAD[0] - DOOR[0], 0, DOOR[0] - PAD[2]), max(PAD[1] - DOOR[1], 0, DOOR[1] - PAD[3]))
    if d_door > 30: raise SystemExit("STOP: the door is %.1f from the pad" % d_door)
    cap = math.hypot(HX - CX, HZ - CZ) + CAP_R
    if cap > R - 3: raise SystemExit("STOP: the cap reaches r %.1f (> %d)" % (cap, R - 3))
    gmax = int(np.abs(T - bf)[in_rect(GARDEN, gr["X"], gr["Z"])].max())
    if gmax > MAX_TERRACE: raise SystemExit("STOP: garden cut/fill %d" % gmax)
    if (T != bf)[rl["app"]].any(): raise SystemExit("the approaches of T-022 would change height")
    slope = int(np.abs(T - bf)[gr["circle"] & ~rl["flatm"] & ~gr["pad"] & ~rl["app"]].max())
    return dict(L=rl["L"], terrace_max=tmax, path_max=pmax, garden_max=gmax, door_dist=round(d_door, 1), cap_r=round(cap, 1), slope_max=slope,
                changed=int(((T != bf) & gr["circle"]).sum()))

# ---------------------------------------------------------------- the trees and the giant mushrooms
GIANTS = [  # (kind, stem height, cap radius): 4 templates (card: 4 shapes in rotations); with the cap 11..17 high (card: 10..18), below the house (26)
    ("red_dome", 11, 6), ("red_bell", 10, 5), ("brown_flat", 14, 7), ("brown_small", 10, 4)]

def keepout(gr, rl):
    """cells where nothing grows: the flats, the pad, the approaches, the house cap's footprint + 1, and 2 round them"""
    m = rl["flatm"] | gr["pad"] | rl["app"]
    m = m | ((gr["X"] - HX) ** 2 + (gr["Z"] - HZ) ** 2 <= (CAP_R + 2) ** 2)
    out = m.copy()
    for _ in range(2):
        p = np.pad(out, 1); out = out | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    return out

def tree_spots(gr, rl):
    """the places of the old trees (base.bin: canopy >= 5 over the ground), r <= 44, not on the keep-out"""
    tr = gr["trees"]; ko = keepout(gr, rl); out = []
    for i, j in zip(*np.nonzero(gr["circle"] & (tr >= 5) & ~ko)):
        x, z = int(gr["X"][i, j]), int(gr["Z"][i, j])
        if not in_circle(x, z, R - 1): continue
        out.append((x, z))
    out.sort(key=lambda c: hsh(c[0], 3, c[1], 3030))
    return out

def layout(gr, rl):
    """giants [(x, z, k, rot)], faces [(x, z, side)], poplars [(x, z, h, thick)]"""
    T = rl["T"]; ko = keepout(gr, rl); spots = tree_spots(gr, rl)
    def far(c, lst, d): return all(max(abs(c[0] - q[0]), abs(c[1] - q[1])) >= d for q in lst)
    giants = []
    for (x, z) in spots:
        if len(giants) >= 9: break
        k = len(giants) % 4; kind, hh, cr = GIANTS[k]
        if not in_circle(x, z, R - cr - 1): continue
        if ko[ix(gr, x, z)]: continue
        if math.hypot(x - HX, z - HZ) < CAP_R + cr + 3: continue
        if not far((x, z), giants, 15): continue
        sub = T[ix(gr, x, z)[0] - 1:ix(gr, x, z)[0] + 2, ix(gr, x, z)[1] - 1:ix(gr, x, z)[1] + 2]
        if sub.max() - sub.min() > 4: continue
        cap = T[ix(gr, x, z)[0] - cr - 1:ix(gr, x, z)[0] + cr + 2, ix(gr, x, z)[1] - cr - 1:ix(gr, x, z)[1] + cr + 2]
        if cap.max() - T[ix(gr, x, z)] > hh - 5: continue        # the cap would sit low over the uphill side
        giants.append((x, z, k, int(hsh(x, 1, z, 31) * 4)))
    # the 6 faces: thick poplars 8..22 from the path, the terrace or the garden (seen from the walks, not on them)
    walk = [(x, z) for (x, z) in rl["flat"]]
    wa = np.array(walk)
    faces = []
    for (x, z) in spots:
        if len(faces) >= 6: break
        d = np.abs(wa - np.array([x, z])).max(axis=1).min()
        if not 7 <= d <= 24: continue
        if not far((x, z), [(g[0], g[1]) for g in giants], 9) or not far((x, z), faces, 12): continue
        if any(ko[ix(gr, x + a, z + c)] for a in (-2, -1, 0, 1, 2) for c in (-2, -1, 0, 1, 2)): continue
        sub = T[ix(gr, x, z)[0] - 1:ix(gr, x, z)[0] + 2, ix(gr, x, z)[1] - 1:ix(gr, x, z)[1] + 2]
        if sub.max() - sub.min() > 3: continue
        # the face looks to the nearest walk cell
        q = wa[np.abs(wa - np.array([x, z])).max(axis=1).argmin()]
        dx, dz = q[0] - x, q[1] - z
        side = ("east" if dx > 0 else "west") if abs(dx) >= abs(dz) else ("south" if dz > 0 else "north")
        faces.append((x, z, side))
    poplars = []
    taken = [(g[0], g[1]) for g in giants]
    for (x, z) in spots:
        if not far((x, z), taken, 7) or not far((x, z), faces, 6) or not far((x, z), poplars, 5): continue
        if ko[ix(gr, x, z)]: continue
        poplars.append((x, z))
    return giants, faces, poplars
