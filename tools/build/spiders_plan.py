"""T-032: the layout of the Spider Thicket (Паучья чаща, Р1): relief decisions (HQ T-032, 2: the thicket lies on the natural west slope of
the hill; earth work only at the nest, the burrow of roots, the fallen giant and the trails), the nest search, the fallen giant, the drop,
the burrow, the animal trail (from the trail Heather -> Garden of T-022) and the trail of the victims (from the south edge to the live
cocoon at the pit's edge), the bands (edge / deep), the points of the mechanics. Read by tools/build/r1_spiders.py (the blocks); only
planning here.

Everything is computed from the ground before the place (the first scan spiders_pre.bin, kept in spiders_before.npz), the same on every
run. The stop conditions of HQ T-032, 2 raise SystemExit("STOP ...")."""
import hashlib, json, math, os, struct, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import Scan, NONE
from lib import h as hsh

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "server/build/r1")
PLACE = (110, -340, 190, -260)             # `spiders rect 150 -300 80 80` (tools/build/r1_plots.txt)
MARGIN = 16
BOX = (PLACE[0] - MARGIN - 10, PLACE[1] - MARGIN - 10, PLACE[2] + MARGIN + 10, PLACE[3] + MARGIN + 10)   # 84 -366 216 -234
EDGE = 11                                  # the edge band (HQ T-032, 2: 10..12 along the outline)
PIT = (20, 24)                             # the pit 24 x 20 (either way round)
PIT_DEPTH = 14                             # HQ T-032, 2: the floor = median of the ground under the pit - 14
PIT_STOP = 16                              # stop: the ground under the pit varies more than 16
PIT_PAD = 3                                # stop: the pit with 3 of margin must lie in the place
PIT_OFF_EDGE = 10                          # the pit lies in the deep (off the edge band): it is the heart of the thicket, not its rim
TRUNK_LEN, TRUNK_R = 40, 2.5               # the fallen giant: 5 x 5, 40 long, over the pit along its long side
LAIR_CUT = 6                               # stop: the burrow needs more than 6 of cut (outside the pit)
LAIR_H = 3                                 # the burrow's head room (>= 3)
TRAIL_CUT = 4                              # stop: the trails need a cut or a fill over 4
TRAIL_OF = "r1_heather->r1_garden"
ANIMAL_IN = 4                              # the animal trail: in the seam or at most 4 into the edge band         # the trail of T-022 east and north of the place (never written)

def in_rect(r, x, z): return (x >= r[0]) & (x <= r[2]) & (z >= r[1]) & (z <= r[3])
def in_place(x, z, m=MARGIN): return PLACE[0] - m <= x <= PLACE[2] + m and PLACE[1] - m <= z <= PLACE[3] + m
def edge_dist(x, z): return min(x - PLACE[0], PLACE[2] - x, z - PLACE[1], PLACE[3] - z)    # inside the place: 0 on the outline

def frame_trail():
    """the cells of the trail Heather -> Garden of T-022 near the place (its centre line from r1.json) with 3 cells of its banks"""
    d = json.load(open(os.path.join(OUT, "r1.json")))
    t = [e for e in d["trails"] if (e["a"], e["b"]) in ((9, 4), (4, 9))][0]
    cells = set()
    for (x, z) in t["cells"]:
        if not in_place(x, z, MARGIN + 12): continue
        for a in range(-3, 4):
            for c in range(-3, 4): cells.add((x + a, z + c))
    return cells, [tuple(p) for p in t["cells"] if in_place(p[0], p[1], MARGIN + 12)]

def grids():
    x1, z1, x2, z2 = BOX; X, Z = np.meshgrid(np.arange(x1, x2 + 1), np.arange(z1, z2 + 1))
    def grid(s, a): return a[z1 - s.z0:z2 - s.z0 + 1, x1 - s.x0:x2 - s.x0 + 1].astype(np.int32)
    base = Scan(os.path.join(OUT, "base.bin"))
    nat = grid(base, base.ground)
    gr = dict(X=X, Z=Z, x1=x1, z1=z1, nat=nat, trees=grid(base, base.top) - nat,
              place=in_rect((PLACE[0] - MARGIN, PLACE[1] - MARGIN, PLACE[2] + MARGIN, PLACE[3] + MARGIN), X, Z), inner=in_rect(PLACE, X, Z))
    d = open(os.path.join(OUT, "terrain.bin"), "rb").read(); assert d[:4] == b"LETA"
    tx0, tz0, tw, th = struct.unpack("<4i", d[4:20]); TH = np.frombuffer(d, "<i2", tw * th, 20).reshape(th, tw).astype(np.int32)
    gr["frame"] = TH[z1 - tz0:z2 - tz0 + 1, x1 - tx0:x2 - tx0 + 1] != NONE
    pre_path = os.path.join(OUT, "spiders_pre.bin")
    if not os.path.exists(pre_path): raise SystemExit("no %s: tools/terrain.sh scan %d %d %d %d %s" % ((pre_path,) + BOX + (pre_path,)))
    pre = Scan(pre_path); gr.update(live=grid(pre, pre.ground), top=grid(pre, pre.top), lwater=grid(pre, pre.water))
    # the ground before the place: the first scan (the frame cuts its trails by blocks), kept in spiders_before.npz keyed by the frame's
    # inputs so that a re-run on the built place starts from the same ground (T-030, T-031)
    key = hashlib.sha1(open(os.path.join(OUT, "terrain.bin"), "rb").read() + open(os.path.join(OUT, "base.bin"), "rb").read()).hexdigest()
    cp = os.path.join(OUT, "spiders_before.npz")
    if os.path.exists(cp) and str(np.load(cp)["key"]) == key:
        dd = np.load(cp); gr["before"] = dd["before"].astype(np.int32); gr["btop"] = dd["top"].astype(np.int32); gr["bwat"] = dd["water"].astype(np.int32)
    else:
        gr["before"] = gr["live"].copy(); gr["btop"] = gr["top"].copy(); gr["bwat"] = gr["lwater"].copy()
        np.savez_compressed(cp, before=gr["before"], top=gr["btop"], water=gr["bwat"], key=key)
    ft, fline = frame_trail()
    m = np.zeros(X.shape, bool)
    for (x, z) in ft:
        if x1 <= x <= x2 and z1 <= z <= z2: m[z - z1, x - x1] = True
    gr["ftrail"] = m | gr["frame"]; gr["fline"] = fline
    gr["wet"] = gr["bwat"] > gr["before"]
    return gr
def ix(gr, x, z): return z - gr["z1"], x - gr["x1"]
def B4(gr, x, z): return int(gr["before"][ix(gr, x, z)])
def sub(gr, r): i1, j1 = ix(gr, r[0], r[1]); i2, j2 = ix(gr, r[2], r[3]); return gr["before"][i1:i2 + 1, j1:j2 + 1]

# ---------------------------------------------------------------- the nest
def nest_site(gr):
    """HQ T-032, 2: the pit 24 x 20 where the natural ground under it varies least (max - min, then the spread), in the deep of the
    thicket (PIT_OFF_EDGE from the outline: the whole place's least is the plateau in the south-east corner, on the edge band by the trail
    of T-022); stop when it varies more than 16 or the pit with 3 of margin does not fit"""
    best = None; glob = None
    for (w, d) in (PIT, PIT[::-1]):
        for m, keep in ((PIT_PAD, False), (PIT_OFF_EDGE, True)):
            for x1 in range(PLACE[0] + m, PLACE[2] - m - w + 2):
                for z1 in range(PLACE[1] + m, PLACE[3] - m - d + 2):
                    a = sub(gr, (x1, z1, x1 + w - 1, z1 + d - 1))
                    c = (int(a.max() - a.min()), round(float(a.std()), 3), x1, z1, w, d)
                    if keep:
                        if best is None or c < best: best = c
                    elif glob is None or c < glob: glob = c
    if best is None: raise SystemExit("STOP (HQ T-032, 2): the pit with %d of margin does not fit in the place" % PIT_PAD)
    if best[0] > PIT_STOP: raise SystemExit("STOP (HQ T-032, 2): the ground under the pit varies %d (> %d) at %s" % (best[0], PIT_STOP, best[2:]))
    rng, sd, x1, z1, w, d = best
    r = (x1, z1, x1 + w - 1, z1 + d - 1)
    floor = int(np.median(sub(gr, r))) - PIT_DEPTH
    return dict(r=r, floor=floor, range=rng, glob=dict(range=glob[0], r=(glob[2], glob[3], glob[2] + glob[4] - 1, glob[3] + glob[5] - 1)),
                along="z" if d > w else "x")

def giant(gr, nest, trail_end):
    """the fallen giant along the pit's long side through its middle: 40 long, its root end (the butt, roots up) at the end nearer to the
    south edge (the trail of the victims comes from there); the centre line rests on the ground at the crown end and rises to the butt"""
    x1, z1, x2, z2 = nest["r"]
    assert nest["along"] == "z"
    cx = (x1 + x2) // 2
    ext = (TRUNK_LEN - (z2 - z1 + 1)) // 2
    za, zb = z1 - ext, z2 + ext + (TRUNK_LEN - (z2 - z1 + 1)) % 2      # 40 cells
    butt = "south"                                                     # z grows to the south
    zs = list(range(za, zb + 1))
    gmax = {z: max(B4(gr, cx + a, z) for a in range(-2, 3)) for z in zs}
    # the centre line: y = top of the ground at the crown end + 2, rising linearly to + 5 over the butt's ground (the butt is lifted);
    # never under the ground + 2 along it (straight trunk: a line fitted over the highest points)
    y0 = gmax[za] + 2.0
    yb = max(gmax[zb] + 5.0, y0)
    k = (yb - y0) / (zb - za)
    for z in zs:
        need = gmax[z] + 2.0 if not (z1 <= z <= z2) else nest_lid_y(gr, nest, cx, z) + 2.0
        if y0 + k * (z - za) < need: y0 += need - (y0 + k * (z - za))
    return dict(x=cx, za=za, zb=zb, butt=butt, y0=round(y0, 2), k=round(k, 4), len=zb - za + 1)
def trunk_y(gi, z): return gi["y0"] + gi["k"] * (z - gi["za"])

def nest_lid_y(gr, nest, x, z):
    """the web lid over the pit lies at the natural ground (the forest floor goes on over the nest)"""
    return B4(gr, x, z)

def drop_hole(nest, gi):
    """the drop: 3 x 3 by the middle of the trunk (east side, in the lid), straight down to the floor"""
    zc = (nest["r"][1] + nest["r"][3]) // 2
    return (gi["x"] + 3, zc - 1, gi["x"] + 5, zc + 1)

def lair(gr, nest, gi, cocoon):
    """the burrow of roots: a ramp 2 wide of roots along the pit's walls (the west wall north -> south, the south wall west -> east, level
    at the corner) from the floor up to the exit through the south wall by the live cocoon, half a block per cell; inside the pit it is
    a ledge of roots, its head room LAIR_H under the lid (the lid is lifted over it: the roots of the butt); cut = ground - level at the
    exit cells outside the pit (<= LAIR_CUT). Returns the centre lane [(x, z, v half blocks)] from the floor to the exit and the lanes"""
    x1, z1, x2, z2 = nest["r"]; F = nest["floor"]
    ex = cocoon[0] - 3                          # the exit's lanes ex, ex + 1 at z2 + 1 (just west of the cocoon)
    ve = 2 * max(B4(gr, ex, z2 + 1), B4(gr, ex + 1, z2 + 1))
    # backwards from the exit: the south leg (rows z2, z2 - 1) westwards, the corner level, the west leg (columns x1, x1 + 1) northwards
    back = [(ex, z2 + 1, ve)]; v = ve
    for x in range(ex, x1 - 1, -1):
        if x <= x1 + 1: break
        v -= 1; back.append((x, z2, v))
    back.append((x1 + 1, z2, v)); back.append((x1 + 1, z2 - 1, v))            # the corner (level: 2 cells)
    z = z2 - 2
    while v > 2 * F and z >= z1 + 2:
        v -= 1; back.append((x1 + 1, z, v)); z -= 1
    if v > 2 * F:                                                            # on along the north wall (rows z1 + 1, z1) eastwards
        back.append((x1 + 1, z1 + 1, v)); back.append((x1 + 2, z1 + 1, v))
        x = x1 + 3
        while v > 2 * F and x <= x2 - 4:
            v -= 1; back.append((x, z1 + 1, v)); x += 1
    if v > 2 * F: raise SystemExit("STOP (HQ T-032, 2): the burrow of roots does not reach the floor along the walls (%d left)" % (v - 2 * F))
    path = back[::-1]
    lanes = {}
    for (x, z, v) in path:
        if z == z2 + 1: cells = [(x, z), (x + 1, z)]
        elif z == z1 + 1 and x >= x1 + 1: cells = [(x, z1), (x, z1 + 1)] + ([(x1, z1), (x1, z1 + 1)] if x == x1 + 1 else [])
        elif x == x1 + 1 and z <= z2 - 1: cells = [(x1, z), (x1 + 1, z)]
        elif (x, z) == (x1 + 1, z2): cells = [(x1, z2), (x1 + 1, z2), (x1, z2 - 1)]
        else: cells = [(x, z2), (x, z2 - 1)]
        for q in cells: lanes[q] = max(lanes.get(q, -1), v)
    lanes[(ex + 1, z2 + 1)] = ve; lanes[(ex, z2 + 1)] = ve
    cut = max(B4(gr, x, z) - lanes[(x, z)] / 2 for (x, z) in lanes if not in_rect(nest["r"], x, z))
    if cut > LAIR_CUT: raise SystemExit("STOP (HQ T-032, 2): the burrow of roots needs %.1f of cut (> %d)" % (cut, LAIR_CUT))
    return dict(path=[list(c) for c in path], lanes={"%d,%d" % q: v for q, v in lanes.items()}, cut=max(0.0, cut), exit=[ex, z2 + 1], ve=ve)
def lair_lanes(la): return {tuple(int(t) for t in k.split(",")): v for k, v in la["lanes"].items()}

# ---------------------------------------------------------------- the trails (A* in half blocks)
def astar(start, goal, h, ok, cost_cell, turn=0.4, run=2):
    """heather_plan.astar for a 2 wide trail: over (x, z, v half blocks, direction, straight run), 4 neighbours, v +-1 per cell; after a
    turn at least `run` cells straight; the turn and the step after it are level (the inner lane of a turn on a slope would climb 3 half
    blocks in 2 cells); no folding (lanes of a hairpin never touch)"""
    import heapq
    sx, sz, sv = start
    pq = [(h(sx, sz, sv), 0.0, sx, sz, sv, -1, run)]; best = {(sx, sz, sv, -1, run): 0.0}; prev = {}
    while pq:
        f, c, x, z, v, d, r = heapq.heappop(pq)
        if best.get((x, z, v, d, r), 1e18) < c: continue
        if goal(x, z, v) and r >= run:
            path = [(x, z, v)]; k = (x, z, v, d, r)
            while k in prev: k = prev[k]; path.append(k[:3])
            path = path[::-1]
            if len({(a, b) for (a, b, _) in path}) != len(path): return None
            return path
        for k, (dx, dz) in enumerate(D):
            if d != -1 and (dx, dz) == (-D[d][0], -D[d][1]): continue
            if d != -1 and k != d and r < run: continue
            turning = d != -1 and k != d
            nr = min(run, r + 1) if (d == -1 or k == d) else 1
            nx, nz = x + dx, z + dz
            kk = (x, z, v, d, r); fold = False
            for i_ in range(24):
                kk = prev.get(kk)
                if kk is None: break
                if max(abs(kk[0] - nx), abs(kk[1] - nz)) <= 3 and (i_ + 2) - (abs(kk[0] - nx) + abs(kk[1] - nz)) >= 2: fold = True; break
            if fold: continue
            for dv in ((0,) if turning or r == 1 else (-1, 0, 1)):
                nv = v + dv
                if not ok(nx, nz, nv, k): continue
                nc = c + 1 + cost_cell(nx, nz, nv) + (turn if turning else 0)
                key = (nx, nz, nv, k, nr)
                if nc < best.get(key, 1e18):
                    best[key] = nc; prev[key] = (x, z, v, d, r); heapq.heappush(pq, (nc + h(nx, nz, nv), nc, nx, nz, nv, k, nr))
    return None

def trail_ok(gr, keep, cut, inside):
    def ok(x, z, v, k):
        for (a, c) in ((0, 0), side(k)):
            q = (x + a, z + c)
            if not inside(*q) or q in keep or gr["ftrail"][ix(gr, *q)] or gr["wet"][ix(gr, *q)]: return False
        for (a, c) in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):      # the lanes of a turn's corner lie round the centre
            if abs(v / 2 - B4(gr, x + a, z + c)) > cut - 0.5: return False
        return True
    return ok
D = [(1, 0), (-1, 0), (0, 1), (0, -1)]
def side(k):
    """the second lane of a 2 wide trail: to the right of the direction (east: south, west: north, south: west, north: east)"""
    return {0: (0, 1), 1: (0, -1), 2: (-1, 0), 3: (1, 0), -1: (1, 0)}[k]

def widen2(path):
    """the trail 2 wide: the centre cell and its right-hand neighbour (by the direction of the step into it) take the centre's level; at a
    turn the corner's outer cell takes the corner's level too (the turns are level: astar); centre cells are never overridden"""
    cen = {(x, z): v for (x, z, v) in path}
    surf = dict(cen)
    for n, (x, z, v) in enumerate(path):
        ks = []
        if n > 0: ks.append(D.index((x - path[n - 1][0], z - path[n - 1][1])))
        if n + 1 < len(path): ks.append(D.index((path[n + 1][0] - x, path[n + 1][1] - z)))
        for k in ks:
            q = (x + side(k)[0], z + side(k)[1])
            if q not in cen and q not in surf: surf[q] = v
    return surf
def steps(surf):
    """the worst difference (half blocks) between neighbouring cells of a trail"""
    return max([abs(v - surf[p]) for (x, z), v in surf.items() for p in ((x + 1, z), (x, z + 1)) if p in surf] + [0])

def trails(gr, nest, gi, la, cocoon):
    """the trail of the victims: from the south edge of the place (z PLACE[3] - 1) north to the clearing before the live cocoon (at the
    pit's south edge, east of the trunk); the animal trail: from the trail Heather -> Garden of T-022 (its west side in the seam, near
    the pad of bonfire 4) to the start of the trail of the victims, through the seam and the edge band"""
    x1, z1, x2, z2 = nest["r"]
    keep = {(x, z) for x in range(x1 - 1, x2 + 2) for z in range(z1 - 1, z2 + 2)}
    keep |= {(x, z) for x in range(gi["x"] - 3, gi["x"] + 4) for z in range(gi["za"], gi["zb"] + 1)}
    keep |= set(lair_lanes(la))
    keep |= {(x, z) for x in range(gi["x"] - 6, gi["x"] + 7) for z in range(gi["zb"] - 2, gi["zb"] + 3)}      # the butt's root plate
    keep -= {(x, z) for x in range(cocoon[0] - 1, cocoon[0] + 2) for z in range(z2 + 2, z2 + 6)}
    # the end: the clearing 2 x 2 south of the live cocoon, just outside the pit's south wall
    end = (cocoon[0], cocoon[1] + 2)
    ev = 2 * B4(gr, *end)
    inside_v = lambda x, z: in_place(x, z, 0) and edge_dist(x, z) >= 0
    okv = trail_ok(gr, keep, TRAIL_CUT, inside_v)
    cost = lambda x, z, v: 0.12 * abs(v / 2 - B4(gr, x, z))
    gv = lambda x, z, v: z == PLACE[3] and abs(v / 2 - B4(gr, x, z)) <= 0.5
    hv = lambda x, z, v: abs(z - PLACE[3])
    pv = astar((end[0], end[1], ev), gv, hv, okv, cost, turn=0.4, run=2)
    if pv is None: raise SystemExit("STOP (HQ T-032, 2): the trail of the victims needs a cut or a fill over %d" % TRAIL_CUT)
    pv = pv[::-1]                                       # south edge -> cocoon
    start = pv[0]
    # the animal trail: from beside the trail of T-022 (its banks kept) at z -285 .. -270 (near the pad of bonfire 4)
    near = [(x, z) for (x, z) in gr["fline"] if -286 <= z <= -268]
    keep_a = keep | {(x, z) for (x, z, v) in pv}
    # the animal trail keeps to the seam and the outer cells of the edge band (it leads round to the south edge: the thicket is seen
    # from it, entered by the trail of the victims)
    oka = trail_ok(gr, keep_a, TRAIL_CUT, lambda x, z: in_place(x, z) and (not in_place(x, z, 0) or edge_dist(x, z) <= ANIMAL_IN))
    ga = lambda x, z, v: (x, z) == (start[0], start[1] + 1) and v == start[2]
    ha = lambda x, z, v: abs(x - start[0]) + abs(z - start[1] - 1) + abs(v - start[2]) * 0.5
    pa = None
    for (fx, fz) in sorted(near, key=lambda c: -c[1]):
        x0 = fx - 4                                     # just west of the banks (3) of the trail
        if not in_place(x0, fz) or gr["ftrail"][ix(gr, x0, fz)]: continue
        v0 = 2 * B4(gr, x0, fz)
        if not oka(x0, fz, v0, 1): continue
        pa = astar((x0, fz, v0), ga, ha, oka, cost, turn=0.4, run=2)
        if pa: break
    if pa is None: raise SystemExit("STOP (HQ T-032, 2): the animal trail needs a cut or a fill over %d or columns outside the place and its seam" % TRAIL_CUT)
    return pv, pa

def spur(gr, nest, gi, la, tv):
    """the walk from the burrow's exit (outside the pit's south wall) to the trail of the victims by the live cocoon: A* 2 wide, half a
    block per cell, cut/fill <= TRAIL_CUT (the bot goes down the burrow from the cocoon without jumps)"""
    x1, z1, x2, z2 = nest["r"]
    keep = {(x, z) for x in range(x1 - 1, x2 + 2) for z in range(z1 - 1, z2 + 1)}
    keep |= {(x, z) for x in range(gi["x"] - 6, gi["x"] + 7) for z in range(gi["zb"] - 2, gi["zb"] + 3)}
    lanes = lair_lanes(la)
    keep |= set(lanes)
    ex, ez = la["exit"]
    tvs = dict(tv)
    ok = trail_ok(gr, keep - set(tvs), TRAIL_CUT, lambda x, z: in_place(x, z, 0))
    g = lambda x, z, v: (x, z) in tvs and abs(v - tvs[(x, z)]) <= 1
    h = lambda x, z, v: min(abs(x - a) + abs(z - c) for (a, c) in tvs)
    p = astar((ex, ez + 1, la["ve"]), g, h, ok, lambda x, z, v: 0.12 * abs(v / 2 - B4(gr, x, z)), turn=0.4, run=2)
    if p is None: raise SystemExit("STOP (HQ T-032, 2): no graded walk from the burrow's exit to the trail of the victims (cut/fill <= %d)" % TRAIL_CUT)
    return [(ex, ez, la["ve"])] + p

# ---------------------------------------------------------------- relief
def relief(gr, nest, gi, la, tv, ta, ts):
    """T (the ground per column as the step writes it): the pit floor, the burrow's trench, the trails (half blocks: a slab on top on an
    odd level), 1:1 banks round the trails and the trench (a cut: full banks; a fill: at most 3 cells)"""
    T = gr["before"].copy(); bf = gr["before"]
    x1, z1, x2, z2 = nest["r"]
    pit = in_rect(nest["r"], gr["X"], gr["Z"])
    flat = {}
    for (x, z), v in tv.items(): flat[(x, z)] = v
    for (x, z), v in ta.items(): flat.setdefault((x, z), v)
    for (x, z), v in ts.items(): flat.setdefault((x, z), v)
    lairm = {q: v for q, v in lair_lanes(la).items() if not in_rect(nest["r"], *q)}
    src = np.full(T.shape, -999); srcu = np.full(T.shape, 9999)
    for (x, z), v in list(flat.items()) + list(lairm.items()):
        srcu[ix(gr, x, z)] = v // 2; src[ix(gr, x, z)] = v // 2
    up, low = srcu.copy(), src.copy()
    for k in range(3):
        pu = np.pad(up, 1, constant_values=9999); pl = np.pad(low, 1, constant_values=-999); mu = up.copy(); ml = low.copy()
        for dz in (0, 1, 2):
            for dx in (0, 1, 2):
                if dz != 1 and dx != 1: continue
                mu = np.minimum(mu, pu[dz:dz + T.shape[0], dx:dx + T.shape[1]] + 1)
                if k < 3: ml = np.maximum(ml, pl[dz:dz + T.shape[0], dx:dx + T.shape[1]] - 1)
        up, low = mu, ml
    fm = np.zeros(T.shape, bool)
    for q in list(flat) + list(lairm): fm[ix(gr, *q)] = True
    cone = gr["place"] & ~fm & ~pit & ~gr["ftrail"]
    # the burrow's trench is roofed by the butt's roots: no banks round it (its walls stand)
    lm = np.zeros(T.shape, bool)
    for q in lairm: lm[ix(gr, *q)] = True
    near_l = lm.copy()
    for _ in range(2):
        p = np.pad(near_l, 1); near_l = near_l | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    trail_only = np.where(near_l, False, True)
    T = np.where(cone & trail_only, bf + np.clip(np.clip(bf, low, up) - bf, -TRAIL_CUT, TRAIL_CUT), T)     # banks 3 cells at most, cut/fill <= 4
    for (x, z), v in flat.items(): T[ix(gr, x, z)] = v // 2
    for (x, z), v in lairm.items(): T[ix(gr, x, z)] = v // 2
    T[pit] = nest["floor"]
    return dict(T=T, flat=flat, flatm=fm, lair=lairm, pit=pit)

def checks(gr, nest, la, rl, tv, ta, ts):
    T, bf = rl["T"], gr["before"]
    def mx(cells, sign):
        return max([sign * (cells[q] / 2 - B4(gr, *q)) for q in cells] + [0])
    info = dict(pit=list(nest["r"]), floor=nest["floor"], pit_range=nest["range"], pit_glob=nest["glob"], lair_cut=la["cut"], lair_len=len(la["path"]),
                victims_len=len(tv), animal_len=len(ta), victims_cut=mx(tv, -1), victims_fill=mx(tv, 1), animal_cut=mx(ta, -1), animal_fill=mx(ta, 1))
    info["victims_step"] = steps(tv); info["animal_step"] = steps(ta); info["spur_step"] = steps({**ts, **tv})
    info["spur_len"] = len(ts); info["spur_cut"] = mx(ts, -1); info["spur_fill"] = mx(ts, 1)
    if max(info["victims_step"], info["animal_step"]) > 1: raise SystemExit("the trails step more than half a block: %s" % info)
    if info["spur_step"] > 1: raise SystemExit("the spur steps more than half a block: %s" % info)
    for k in ("victims_cut", "victims_fill", "animal_cut", "animal_fill", "spur_cut", "spur_fill"):
        if info[k] > TRAIL_CUT: raise SystemExit("STOP (HQ T-032, 2): %s %.1f > %d" % (k, info[k], TRAIL_CUT))
    out = [(x, z) for (x, z) in list(tv) + list(ta) if not in_place(x, z)]
    if out: raise SystemExit("STOP (HQ T-032, 2): trail cells outside the place and its seam: %s" % out[:5])
    if (T != bf)[gr["ftrail"]].any(): raise SystemExit("the trail of T-022 would change")
    info["changed"] = int(((T != bf) & gr["place"]).sum())
    info["bank_max"] = int(np.abs(T - bf)[gr["place"] & ~rl["flatm"] & ~rl["pit"]].max())
    return info

def plan(gr):
    """cached in server/build/r1/spiders_plan.pkl (the trails' A* takes minutes), keyed by the ground before and this module's source"""
    import pickle
    src = open(os.path.abspath(__file__), "rb").read()
    key = hashlib.sha1(gr["before"].tobytes() + gr["ftrail"].tobytes() + src).hexdigest()
    cp = os.path.join(OUT, "spiders_plan.pkl")
    if os.path.exists(cp):
        d = pickle.load(open(cp, "rb"))
        if d.get("key") == key: return d["plan"]
    pl = plan_now(gr)
    pickle.dump(dict(key=key, plan=pl), open(cp, "wb"))
    return pl

def plan_now(gr):
    nest = nest_site(gr)
    gi = giant(gr, nest, None)
    x1, z1, x2, z2 = nest["r"]
    cocoon = (gi["x"] + 7, z2 + 1)                     # the live cocoon: over the pit's south wall, east of the trunk
    la = lair(gr, nest, gi, cocoon)
    pv, pa = trails(gr, nest, gi, la, cocoon)
    tv = widen2(pv[::-1]); ta = widen2(pa)          # widened in the A* order: its lanes are the ones the search checked
    for q in list(ta):
        if q in tv: del ta[q]
    ps = spur(gr, nest, gi, la, tv)
    ts = {q: v for q, v in widen2(ps).items() if q not in tv}
    return dict(nest=nest, giant=gi, lair=la, hole=drop_hole(nest, gi), cocoon=cocoon, pv=pv, pa=pa, ps=ps, tv=tv, ta=ta, ts=ts)
