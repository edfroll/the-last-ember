"""T-031: the layout of the Village of Heather (Деревня Вереск) and the Dragon Ridge (Р1): relief decisions (HQ T-031, 1: the village
on the natural shelf over the brook, the church highest on the slope under the ridge, the ridge follows the natural massif, the head on
its east end), the bridge, the street, the square, the house terraces, the east plain (mill, gardens, pasture), the head, the trail to
the mouth. Read by tools/build/r1_heather.py (the blocks); only planning here.

Everything is computed from the ground before the places (the first scan heather_pre.bin, kept in heather_before.npz), the same on
every run. The stop conditions of HQ T-031, 1 raise SystemExit("STOP ...")."""
import hashlib, heapq, math, os, struct, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import Scan, NONE
from lib import h as hsh

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "server/build/r1")
VILLAGE = (20, -515, 120, -425)            # `heather rect 70 -470 100 90` (tools/build/r1_plots.txt)
RIDGE = (-10, -580, 150, -540)             # `dragon_ridge rect 70 -560 160 40`
MARGIN = 16
BOX = (VILLAGE[0] - MARGIN - 40, RIDGE[1] - MARGIN - 10, RIDGE[2] + MARGIN + 10, VILLAGE[3] + MARGIN + 10)   # -36 -606 176 -399
PAD = (64, -425, 77, -412)                 # the pad of bonfire 9 (T-022: 14 x 14 round (70, -420), ground 63, feet 64): never written
PAD_Y = 63
HEARTH = (70, 64, -420)
MAX_EARTH = 8                              # HQ T-031, 1: terraces at most 8 of cut or fill
STREET_CUT = 4                             # the street: a cut at most 4 (a fill: an embankment with walls, at most 8)
TRAIL_CUT = 6                              # the trail to the mouth (the massif is never cut more than 8)
BRIDGE_X = (69, 71)                        # the bridge: 3 wide, straight north from the pad's north edge
BRIDGE_Z0 = -426
CHURCH = (28, 14)                          # the church terrace (x by z): nave along the contour, the tower on the west end
SQUARE = 11
# the head (HQ T-031, 1: 30 x 30 on the east end, the mouth open to the north): x 118..147, z -576..-547 (3 inside the place)
HEAD = (118, -576, 147, -547)
HEAD_TOP = 120
MOUTH_Y = 84                               # the floor of the mouth (the platform of the view north, 5 x 5): 9 over the plain below
MOUTH = (128, -575, 132, -571)             # the platform (x1, z1, x2, z2) at the north edge of the head
NECK_END = (117, -573)                     # where the trail meets the jaw passage on the head's west side (the corner of the mouth)

def in_rect(r, x, z): return (x >= r[0]) & (x <= r[2]) & (z >= r[1]) & (z <= r[3])
def in_village(x, z, m=0): return VILLAGE[0] - m <= x <= VILLAGE[2] + m and VILLAGE[1] - m <= z <= VILLAGE[3] + m
def in_ridge(x, z, m=0): return RIDGE[0] - m <= x <= RIDGE[2] + m and RIDGE[1] - m <= z <= RIDGE[3] + m
def in_place(x, z): return in_village(x, z, MARGIN) or in_ridge(x, z, MARGIN)
def on_pad(x, z): return PAD[0] <= x <= PAD[2] and PAD[1] <= z <= PAD[3]

def grids():
    x1, z1, x2, z2 = BOX; X, Z = np.meshgrid(np.arange(x1, x2 + 1), np.arange(z1, z2 + 1))
    def grid(s, a): return a[z1 - s.z0:z2 - s.z0 + 1, x1 - s.x0:x2 - s.x0 + 1].astype(np.int32)
    base = Scan(os.path.join(OUT, "base.bin"))
    nat = grid(base, base.ground)
    gr = dict(X=X, Z=Z, x1=x1, z1=z1, nat=nat, trees=grid(base, base.top) - nat, bwater=grid(base, base.water),
              village=in_rect(VILLAGE, X, Z), ridge=in_rect(RIDGE, X, Z), pad=in_rect(PAD, X, Z))
    gr["place"] = in_rect((VILLAGE[0] - MARGIN, VILLAGE[1] - MARGIN, VILLAGE[2] + MARGIN, VILLAGE[3] + MARGIN), X, Z) | \
        in_rect((RIDGE[0] - MARGIN, RIDGE[1] - MARGIN, RIDGE[2] + MARGIN, RIDGE[3] + MARGIN), X, Z)
    pre_path = os.path.join(OUT, "heather_pre.bin")
    if not os.path.exists(pre_path): raise SystemExit("no %s: tools/terrain.sh scan %d %d %d %d %s" % ((pre_path,) + BOX + (pre_path,)))
    pre = Scan(pre_path); gr.update(live=grid(pre, pre.ground), top=grid(pre, pre.top), lwater=grid(pre, pre.water), flags=grid(pre, pre.flags))
    # the ground before the places: the first scan (the frame cut its trails by blocks, terrain.bin lies there; T-030), kept in
    # heather_before.npz keyed by the frame's inputs so that a re-run on the built place starts from the same ground
    key = hashlib.sha1(open(os.path.join(OUT, "terrain.bin"), "rb").read() + open(os.path.join(OUT, "base.bin"), "rb").read()).hexdigest()
    cp = os.path.join(OUT, "heather_before.npz")
    if os.path.exists(cp) and str(np.load(cp)["key"]) == key:
        d = np.load(cp); gr["before"] = d["before"].astype(np.int32); gr["bwat"] = d["water"].astype(np.int32); gr["btop"] = d["top"].astype(np.int32)
    else:
        gr["before"] = gr["live"].copy(); gr["bwat"] = gr["lwater"].copy(); gr["btop"] = gr["top"].copy()
        np.savez_compressed(cp, before=gr["before"], water=gr["bwat"], top=gr["btop"], key=key)
    gr["wet"] = gr["bwat"] > gr["before"]
    return gr
def ix(gr, x, z): return z - gr["z1"], x - gr["x1"]
def B4(gr, x, z): return int(gr["before"][ix(gr, x, z)])
def sub(gr, r): i1, j1 = ix(gr, r[0], r[1]); i2, j2 = ix(gr, r[2], r[3]); return gr["before"][i1:i2 + 1, j1:j2 + 1]

def best_level(gr, r, lo=None, hi=None):
    """the level with the least earth work over the rect: (max |cut/fill|, sum, L)"""
    a = sub(gr, r); out = None
    for L in range(int(a.min()) if lo is None else lo, (int(a.max()) if hi is None else hi) + 1):
        d = np.abs(a - L); c = (int(d.max()), int(d.sum()), L)
        if out is None or c < out: out = c
    return out

# ---------------------------------------------------------------- the church, the square
def church_site(gr):
    """HQ T-031, 1: the church on the north edge of the village, highest, on the slope under the ridge: the 28 x 14 terrace (nave along
    the contour) with the least earth work at a level >= 100 in the northern third of the village (<= 8 of cut/fill)"""
    wx, wz = CHURCH; best = None
    for x1 in range(VILLAGE[0] + 2, VILLAGE[2] - wx - 1):
        for z1 in range(VILLAGE[1] + 2, VILLAGE[1] + 30):
            r = (x1, z1, x1 + wx - 1, z1 + wz - 1); a = sub(gr, r)
            for L in range(max(100, int(a.min())), int(a.max()) + 1):
                d = np.abs(a - L); m = int(d.max())
                if m > MAX_EARTH: continue
                c = (int(d.sum()), m, -L, r)
                if best is None or c < best[0]: best = (c, L, r)
    if best is None: raise SystemExit("STOP (HQ T-031, 1): no church terrace within %d of cut/fill" % MAX_EARTH)
    return best[2], best[1]

def square_site(gr):
    """the square with the well: 11 x 11 on the shelf (its middle third), the least earth work"""
    best = None
    for x1 in range(40, 76):
        for z1 in range(-482, -452):
            r = (x1, z1, x1 + SQUARE - 1, z1 + SQUARE - 1)
            m, s_, L = best_level(gr, r)
            c = (m > 3, s_ + abs(x1 - 54) * 6 + abs(z1 + 470) * 6, m, L, r)
            if best is None or c < best: best = c
    return best[4], best[3]

# ---------------------------------------------------------------- the street (A* in half blocks)
def astar(gr, start, goal, h, ok, cost_cell, turn=0.6, run=3):
    """A* over (x, z, v half blocks, direction, straight run): 4 neighbours, v +-1 per cell; after a turn at least `run` cells straight
    (no spirals: a street never folds onto itself, its 3 cells across keep the levels of their centre)"""
    sx, sz, sv = start
    pq = [(h(sx, sz, sv), 0.0, sx, sz, sv, -1, run)]; best = {(sx, sz, sv, -1, run): 0.0}; prev = {}
    D = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    while pq:
        f, c, x, z, v, d, r = heapq.heappop(pq)
        if best.get((x, z, v, d, r), 1e18) < c: continue
        if goal(x, z, v) and r >= run:
            path = [(x, z, v)]; k = (x, z, v, d, r)
            while k in prev: k = prev[k]; path.append(k[:3])
            path = path[::-1]
            if len({(a, c) for (a, c, _) in path}) != len(path): return None      # a loop over the same cells: not a street
            return path
        for k, (dx, dz) in enumerate(D):
            if d != -1 and (dx, dz) == (-D[d][0], -D[d][1]): continue          # no U-turn
            if d != -1 and k != d and r < run: continue                         # a turn only after `run` straight cells
            nr = min(run, r + 1) if (d == -1 or k == d) else 1
            nx, nz = x + dx, z + dz
            # no folding: the new cell keeps 4 from the cells 4..24 steps back (a hairpin's lanes would touch: levels apart across)
            kk = (x, z, v, d, r); fold = False
            for i_ in range(24):
                kk = prev.get(kk)
                if kk is None: break
                if max(abs(kk[0] - nx), abs(kk[1] - nz)) <= 3 and (i_ + 2) - (abs(kk[0] - nx) + abs(kk[1] - nz)) >= 2: fold = True; break
            if fold: continue
            for dv in (-1, 0, 1):
                nv = v + dv
                if not ok(nx, nz, nv, k): continue
                nc = c + 1 + cost_cell(nx, nz, nv) + (turn if d != -1 and k != d else 0)
                key = (nx, nz, nv, k, nr)
                if nc < best.get(key, 1e18):
                    best[key] = nc; prev[key] = (x, z, v, d, r); heapq.heappush(pq, (nc + h(nx, nz, nv), nc, nx, nz, nv, k, nr))
    return None

def corridor(gr):
    """the rows of the bridge: from the pad's north edge north while any of its 3 cells is wet; returns the last wet row"""
    z = BRIDGE_Z0
    while any(gr["wet"][ix(gr, x, z - 1)] for x in range(BRIDGE_X[0], BRIDGE_X[1] + 1)): z -= 1
    return z

def street_ok(gr, keep, zc, flats=None):
    """the 3 x 3 round a centre cell: dry, within STREET_CUT of the level; the bridge corridor (x 70, z -426..zc) only northwards, its
    cells are deck (no ground under them)"""
    mid = BRIDGE_X[0] + 1
    def deck(q): return BRIDGE_X[0] <= q[0] <= BRIDGE_X[1] and zc <= q[1] <= BRIDGE_Z0
    def ok(x, z, v, k):
        if deck((x, z)): return x == mid and k == 3
        if not in_village(x, z, -2): return False
        for a in (-1, 0, 1):
            for c in (-1, 0, 1):
                q = (x + a, z + c)
                if deck(q) or on_pad(*q): continue
                if flats and q in flats:
                    if (a, c) == (0, 0) or abs(v - flats[q]) > 2: return False
                    continue
                if gr["wet"][ix(gr, *q)] or q in keep: return False
                d = v / 2 - B4(gr, *q)
                if d < -(STREET_CUT - 0.5) or d > MAX_EARTH - 0.5: return False   # HQ T-031, 1: a cut <= 4, a fill on walls <= 8 (0.5 kept for the widening)
        return True
    return ok, deck

def street(gr, church, cL, square, sL):
    """the pad's north edge -> over the bridge -> the square (its east edge, at its level) -> the church terrace (its south edge, at its
    level): a centre line in half blocks; the bridge is the part of it over the brook"""
    zc = corridor(gr)
    def rect_cells(r, m=0): return {(x, z) for x in range(r[0] - m, r[2] + m + 1) for z in range(r[1] - m, r[3] + m + 1)}
    sq = rect_cells(square); ch = rect_cells(church)
    ok1, deck = street_ok(gr, set(), zc, {q: 2 * cL for q in ch})
    cc = lambda x, z, v: 0.12 * abs(v / 2 - B4(gr, x, z)) if not deck((x, z)) else 0.0
    sx = (square[0] + square[2]) // 2
    g1 = lambda x, z, v: v == 2 * sL and x == square[2] + 1 and square[1] + 3 <= z <= square[3] - 3
    h1 = lambda x, z, v: max(abs(v - 2 * sL), abs(x - square[2] - 1) + max(0, z - square[3] + 3, square[1] + 3 - z))
    ok1b = lambda x, z, v, k: (x, z) not in sq and ok1(x, z, v, k)
    p1 = astar(gr, (BRIDGE_X[0] + 1, BRIDGE_Z0, 2 * PAD_Y + 1), g1, h1, ok1b, cc, turn=0.5)
    if p1 is None: raise SystemExit("STOP (HQ T-031, 1): the street from the bridge to the square needs more than half a block per step or a cut over %d" % STREET_CUT)
    cx = (church[0] + church[2]) // 2
    g2 = lambda x, z, v: v == 2 * cL and z == church[3] + 1 and abs(x - cx) <= 2
    h2 = lambda x, z, v: max(abs(v - 2 * cL), abs(z - church[3] - 1) + max(0, abs(x - cx) - 2))
    near1 = {(x + a, z + c) for (x, z, v) in p1 for a in range(-2, 3) for c in range(-2, 3)}
    def ok2(x, z, v, k):
        if (x, z) in sq or (x, z) in near1: return False
        return ok1(x, z, v, k)
    starts = [(x, square[1] - 1) for x in range(square[0] + 3, square[2] - 2)]
    p2 = None
    for (x0, z0) in sorted(starts, key=lambda q: abs(q[0] - sx)):
        if not ok2(x0, z0, 2 * sL, 3): continue
        p2 = astar(gr, (x0, z0, 2 * sL), g2, h2, ok2, cc, turn=0.5)
        if p2: break
    if p2 is None: raise SystemExit("STOP (HQ T-031, 1): the street from the square to the church needs more than half a block per step or a cut over %d" % STREET_CUT)
    dk = {}
    for (x, z, v) in p1:
        if deck((x, z)):
            for xx in range(BRIDGE_X[0], BRIDGE_X[1] + 1): dk[(xx, z)] = v
    p1 = [c for c in p1 if not deck(c[:2])]
    return dk, p1, p2

def widen(centre, flats_fixed):
    """the street 3 wide: the side cells take the height of the nearest centre cell, then neighbours across the whole width differ by at
    most half a block (lowered where needed: a cut, never a jump); fixed flats (the square, the bridge) keep their heights"""
    surf = dict(flats_fixed); best = {}
    for (x, z, v) in centre:
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                q = (x + dx, z + dz); d = dx * dx + dz * dz
                if q in flats_fixed: continue
                if q not in best or d < best[q] or (d == best[q] and v < surf[q]): best[q] = d; surf[q] = v
    changed = True
    while changed:
        changed = False
        for q, v in list(surf.items()):
            if q in flats_fixed: continue
            x, z = q
            m = min([surf[p] for p in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)) if p in surf] + [v + 1]) + 1
            if m < v: surf[q] = m; changed = True
    return {q: v for q, v in surf.items() if q not in flats_fixed}

# ---------------------------------------------------------------- the houses along the street
# (kind, w along the street, d deep, storeys): the five oddities of the card (HQ T-031, 2), the repeats in another size and finish
HOUSES = [("walled", 7, 7, 1), ("ladder", 7, 9, 2), ("roof", 7, 7, 1), ("deep", 9, 11, 1), ("reversed", 7, 9, 1),
          ("walled", 9, 7, 2), ("roof", 9, 7, 1), ("ladder", 7, 7, 2), ("reversed", 9, 7, 1),
          ("walled", 7, 9, 1), ("reversed", 7, 7, 1), ("roof", 7, 9, 1), ("walled", 7, 7, 1), ("reversed", 7, 9, 1), ("ladder", 7, 9, 2)]           # spares: the street takes 8..9 (HQ T-031: 8..10 + the miller's)
MAX_HOUSES = 9

VIEW_EYES = [(x + 0.5, PAD_Y + 2.62, z + 0.5) for x in (66, 70, 74) for z in (-423, -418, -414)]
def view_targets():
    """points of the sword over the head (heather_ridge.sword_cells): its upper half"""
    import heather_ridge as HR
    sk, hm = HR.skull_cells(); sw, base = HR.sword_cells(hm["eye"])
    ys = sorted({k[1] for k in sw}); top = [k for k in sw if k[1] >= ys[len(ys) // 2]]
    return [(k[0] + 0.5, k[1] + 0.5, k[2] + 0.5) for k in top[::max(1, len(top) // 12)]]
_VT = []
def lines_cut(r, top):
    """the sight lines (eye, target) from the pad of bonfire 9 to the upper half of the sword that a house (footprint r, highest block
    `top`) would cut"""
    if not _VT: _VT.extend(view_targets())
    out = set()
    for a, e in enumerate(VIEW_EYES):
        for b, t in enumerate(_VT):
            for k in range(1, 200):
                f = k / 200.0; x, y, z = (e[i] + (t[i] - e[i]) * f for i in range(3))
                if y > top + 1: break
                if r[0] - 1 <= x <= r[2] + 2 and r[1] - 1 <= z <= r[3] + 2: out.add((a, b)); break
    return out
def sword_seen(cut):
    """the sword counts as seen from the pad while one of its eyes sees at least a quarter of the targets (the top of the blade)"""
    return any(sum(1 for b in range(len(_VT)) if (a, b) not in cut) * 4 >= len(_VT) for a in range(len(VIEW_EYES)))

def house_sites(gr, surf, taken, n=len(HOUSES)):
    """greedy: along the street, both sides, a footprint w x d set back 1 from the street edge with its door on the street; the floor at
    the street level by the door (cut/fill <= 8 over the footprint), 3 apart from the others, inside the village (2 from its edge)"""
    cells = sorted(surf, key=lambda q: (q[1], q[0]))
    order = []
    for k, spec in enumerate(HOUSES):
        order.append((k, spec))
    out = []
    used = set(taken); hused = set(); cut = set()
    def free(r, m):
        return all((x, z) not in used for x in range(r[0], r[2] + 1) for z in range(r[1], r[3] + 1)) and \
            all((x, z) not in hused for x in range(r[0] - m, r[2] + m + 1) for z in range(r[1] - m, r[3] + m + 1))
    cand_all = []
    for (x, z), v in surf.items():
        for (dx, dz, face) in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
            # the street cell (x, z) is the cell in front of the door; the door at (x + dx, z + dz) only when that is off the street
            dxx, dzz = x + dx, z + dz
            if (dxx, dzz) in surf: continue
            if (x - dx, z - dz) not in surf: continue          # (x, z) is an edge cell of the street, the street lies behind it
            cand_all.append((x, z, v, dx, dz, face))
    cand_all.sort(key=lambda c: hsh(c[0], 7, c[1], 3100))
    for (k, (kind, w, d, st)) in order:
        if len(out) >= MAX_HOUSES: break
        best = None
        for (x, z, v, dx, dz, face) in cand_all:
            # the footprint: the door in the middle of the front wall (front wall at the door cell)
            if dx: r = (x + dx, z - w // 2, x + dx * d, z + w // 2)
            else: r = (x - w // 2, z + dz, x + w // 2, z + dz * d)
            r = (min(r[0], r[2]), min(r[1], r[3]), max(r[0], r[2]), max(r[1], r[3]))
            if not (in_village(r[0], r[1], -2) and in_village(r[2], r[3], -2)): continue
            if not free(r, 2): continue
            if np.any(gr["wet"][ix(gr, r[0], r[1])[0]:ix(gr, r[2], r[3])[0] + 1, ix(gr, r[0], r[1])[1]:ix(gr, r[2], r[3])[1] + 1]): continue
            L = (v + 1) // 2                                   # the floor: the street level or half a block over it (never under: the
                                                               # door is opened from the street at the eye level)
            lc = lines_cut(r, L + 4 * st + (d + 1) // 2 + 3)
            if lc and not sword_seen(cut | lc): continue          # the sword of the ridge stays seen from the pad of bonfire 9
            import heather_build as HB
            fr = HB.Frame(r, face)
            # the ways in that start outside the door: the street must lie by them at the floor's level (within half a block): the
            # corner where the outer stair (ladder house) or the ladder (roof house) starts, the window of the walled-up house
            du_ = fr.W // 2
            need = {"ladder": range(du_ + 1, fr.W + 1), "roof": range(-1, du_), "walled": range(du_ + 1, du_ + 3)}.get(kind, [])
            front_ap = []; bad_ = False
            for u in need:                                     # the front row from the door to there: street at the floor's level or
                q = fr.xz(u, -1)                               # free ground made flat at it (the apron)
                if q in surf:
                    if abs(surf[q] - 2 * L) > 1: bad_ = True; break
                elif q in used or q in hused or gr["wet"][ix(gr, *q)]: bad_ = True; break
                else: front_ap.append(q)
            if bad_: continue
            if kind == "reversed" and any(fr.xz(fr.W // 2, fr.D + k) in used or fr.xz(fr.W // 2, fr.D + k) in hused or
                                          not in_village(*fr.xz(fr.W // 2, fr.D + k), -2) for k in (0, 1)): continue
            a = sub(gr, r); m = int(np.abs(a - L).max())
            if m > MAX_EARTH: continue
            spread = min([max(abs(r[0] - q["r"][0]), abs(r[1] - q["r"][1])) for q in out] + [99])
            c = (m > 5, -min(spread, 14), int(np.abs(a - L).sum()) / 40.0)
            if best is None or c < best[0]: best = (c, dict(k=k, kind=kind, w=w, d=d, storeys=st, r=r, L=L, face=face, door=(x + dx, z + dz), front=(x, z), v=v, earth=m, front_ap=front_ap, cut=lc))
        if best is None: continue
        h_ = best[1]; out.append(h_)
        # the apron at the floor level where a stair or a ladder starts outside: the outer stair of the ladder house (2 columns on the
        # right, front row too), the ladder of the roof house (1 column on the left); street cells stay street
        ap = []
        import heather_build as HB
        fr = HB.Frame(h_["r"], h_["face"])
        if kind in ("ladder", "roof"):
            us = (fr.W, fr.W + 1) if kind == "ladder" else (-1,)
            for u in us:
                for w in range(-1, fr.D):
                    q = fr.xz(u, w)
                    if q not in surf and q not in used and q not in hused: ap.append(q)
        if kind == "reversed":                         # the yard behind the door in the hearth
            for k in (0, 1):
                for a in (-1, 0, 1):
                    q = fr.xz(fr.W // 2 + a, fr.D + k)
                    if q not in surf and q not in used and q not in hused: ap.append(q)
        ap += [q for q in h_.pop("front_ap") if q not in ap]
        cut |= h_.pop("cut")
        h_["apron"] = ap
        for q in ap: hused.add(q)
        for xx in range(h_["r"][0], h_["r"][2] + 1):
            for zz in range(h_["r"][1], h_["r"][3] + 1): hused.add((xx, zz))
    return out

# ---------------------------------------------------------------- the east plain: the mill, the miller's house, gardens, the pasture
PLAIN = dict(mill=(101, -481, 109, -473), miller=(100, -493, 106, -487), garden1=(94, -462, 104, -454), garden2=(106, -462, 116, -454),
             garden3=(108, -472, 117, -466), pasture=(100, -512, 116, -499))

def plain_sites(gr, taken):
    out = {}
    for k, r in PLAIN.items():
        if k == "pasture":                     # a fence over the natural ground: no terrace
            out[k] = dict(r=r, L=None, earth=0); continue
        m, s_, L = best_level(gr, r)
        if m > MAX_EARTH: raise SystemExit("STOP (HQ T-031, 1): the %s needs %d of cut/fill" % (k, m))
        if any((x, z) in taken for x in range(r[0], r[2] + 1) for z in range(r[1], r[3] + 1)): raise SystemExit("the %s lies on the street" % k)
        out[k] = dict(r=r, L=L, earth=m)
    return out

# ---------------------------------------------------------------- the ridge: the spine, the neck, the head mound; the trail
def ridge_axis(gr):
    """the crest line of the natural massif, west -> east: for every x of the ridge place the z of the highest ground (smoothed), the
    crest height; east of the massif's end the axis runs on to the head"""
    xs = list(range(RIDGE[0], RIDGE[2] + 1)); zc = []; yc = []
    for x in xs:
        col = [(B4(gr, x, z), z) for z in range(RIDGE[1] + 2, RIDGE[3] + 8)]
        y, z = max(col); zc.append(z); yc.append(y)
    zc = np.array(zc, float)
    k = 9; zs = np.convolve(np.pad(zc, k, mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), "valid")
    return {x: (int(round(z)), y) for x, z, y in zip(xs, zs, yc)}

def head_mound(gr):
    """the terrain under the head (filled by the terrain step): the skull rests on a mound up to the mouth floor - 1 inside the head's
    rect, 1:1 banks round it down to the ground; the neck (south-west of the head, from the massif's east shoulder to the back of the
    skull): a ridge falling 1 per cell to its sides from 96 at its axis {(x, z): height}"""
    T = {}
    hx1, hz1, hx2, hz2 = HEAD
    for x in range(hx1 - 26, hx2 + 4):
        for z in range(hz1 - 4, hz2 + 6):
            if not in_ridge(x, z, -1): continue
            g = B4(gr, x, z)
            dx = max(hx1 - x, 0, x - hx2); dz = max(hz1 - z, 0, z - hz2)
            t = MOUTH_Y - 1 - max(dx, dz)
            if 96 <= x < hx1 and -560 <= z <= -544:
                t = max(t, 96 - abs(z + 552) - max(0, (x - 96) // 6))
            if t > g: T[(x, z)] = t
    return T

def trail(gr, church, cL, mound, keep):
    """from the north side of the church terrace (its east end) along the seams (z -540..-515) and the neck into the corner of the mouth
    (NECK_END at MOUTH_Y): half a block per cell, cut/fill <= TRAIL_CUT on the ground as the head mound leaves it"""
    def G(x, z): return mound.get((x, z), B4(gr, x, z))
    def ok(x, z, v, k):
        if not (in_village(x, z, MARGIN - 3) or in_ridge(x, z, MARGIN - 3)): return False      # the places and their seams (HQ T-031, 1)
        if z > church[1] - 1 or x < church[0]: return False
        for a in (-1, 0, 1):
            for c in (-1, 0, 1):
                q = (x + a, z + c)
                if q in keep or gr["wet"][ix(gr, *q)]: return False
                if in_rect(HEAD, q[0], q[1]) and abs(q[1] - NECK_END[1]) > 1: return False      # into the head only by its passage
                if abs(v / 2 - G(*q)) > TRAIL_CUT: return False
        return True
    start = (church[2] - 3, church[1] - 1, 2 * cL)
    g = lambda x, z, v: (x, z) == NECK_END and v == 2 * MOUTH_Y
    h = lambda x, z, v: max(abs(v - 2 * MOUTH_Y), abs(x - NECK_END[0]) + abs(z - NECK_END[1]))
    p = astar(gr, start, g, h, ok, lambda x, z, v: 0.1 * abs(v / 2 - G(x, z)), turn=0.4)
    if p is None: raise SystemExit("STOP (HQ T-031, 1): the trail to the mouth finds no way (half a block per step, cut/fill <= %d) in the places and their seams" % TRAIL_CUT)
    return p

def plan(gr):
    church, cL = church_site(gr)
    square, sL = square_site(gr)
    deck, p1, p2 = street(gr, church, cL, square, sL)
    fixed = dict(deck)
    for x in range(square[0], square[2] + 1):
        for z in range(square[1], square[3] + 1): fixed[(x, z)] = 2 * sL
    surf = widen(p1 + p2, fixed)
    taken = set(surf) | set(fixed) | {(x, z) for x in range(church[0], church[2] + 1) for z in range(church[1], church[3] + 1)}
    plain = plain_sites(gr, taken)
    for k, q in plain.items():
        r = q["r"]; taken |= {(x, z) for x in range(r[0] - 1, r[2] + 2) for z in range(r[1] - 1, r[3] + 2)}
    sqc = {(x, z): 2 * sL for x in range(square[0], square[2] + 1) for z in range(square[1], square[3] + 1)}
    houses = house_sites(gr, dict(surf, **{}) | sqc, taken)          # houses face the street and the square
    mound = head_mound(gr)
    tr = trail(gr, church, cL, mound, set())
    tsurf = widen(tr, {})
    return dict(church=church, cL=cL, square=square, sL=sL, deck=deck, street=p1 + p2, surf=surf, plain=plain, houses=houses,
                mound=mound, trail=tr, tsurf=tsurf, axis=ridge_axis(gr))
