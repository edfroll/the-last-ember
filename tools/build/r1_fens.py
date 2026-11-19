#!/usr/bin/env python3
"""T-026: the Crooked Fens and the Hut of the Three Witches (Р1) on the place `fens` of tools/build/r1_plots.txt
(rect 220x180 round (-380,330) + 16).

  python3 tools/build/r1_fens.py   -> server/build/r1/fens_terrain.bin (tools/terrain.sh apply), fens.txt (tools/blockwriter.sh apply),
                                      fens.json (points for the tests, the walk bot and the datapack), docs/reports/T-026/fens_plan.png,
                                      structure/fens/*.nbt (the ruin templates), datapack function/fens/gen/* (tools/build/fens_dp.py),
                                      the zone of the hut, the key source
  python3 tools/build/r1_fens.py plan   only the plan and the checks of HQ (task T-026, 1), nothing written but the plan
Inputs: server/build/r1/base.bin (the ground before the R1 frame), terrain.bin (the frame), fens_pre.bin (scan of the place now),
        allow.npz (r1.py: the pad of bonfire 5 with its slopes and the approaches: never written).

Layout (HQ T-026, 1: the relief of seed 10845): a raised bog in a bowl of the plateau. W = the 40th percentile of the ground of the
plateau (x -480..-356, z 256..400). The bowl = the connected part of the plateau with its ground in W-6..W+8 (and the closed holes in
it: the natural cleft west of the hut is a deep water there); hills above W+8 inside stay (forested islands). Inside: channels (bottom
W-3 main, W-2 side), shallows and mud flats (W-1), tussocks and islets W..W+2. Where the land outside is lower than W+1 the rim is a
berm of mud and mangrove roots at W+1, 3 wide, with a 1:1 slope outward. The north ridge and the east descent keep their relief; the
snow, the spruces and the cherries of the place go (mangroves and swamp oaks of our own model). The climb from bonfire 5 (its pad
untouched) up the east slope to the outer pier: a graded way (half blocks, no jumps), 93 cells. Re-run: the same fens, 0 columns."""
import heapq, json, math, os, struct, sys
from collections import deque
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import Scan, write_grid, NONE
from lib import B, Mix, h as hsh, slab

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "server/build/r1")
DP = os.path.join(ROOT, "datapack/data/last_ember")
PCX, PCZ, PW, PD, MARGIN = -380, 330, 220, 180, 16
CORE = (-490, 240, -270, 420)
PLACE = (CORE[0] - MARGIN, CORE[1] - MARGIN, CORE[2] + MARGIN, CORE[3] + MARGIN)
PLATEAU = (-480, 256, -356, 400)                       # HQ: W = 40th percentile of the natural ground here
HEARTH5 = (-276, 90, 250)
S_FOREST, S_MOSS = 2, 6
R_STONE = 0

def in_place(x, z):
    return np.hypot(np.maximum(np.abs(x - PCX) - PW / 2, 0), np.maximum(np.abs(z - PCZ) - PD / 2, 0)) <= MARGIN
def in_core(x, z): return (x >= CORE[0]) & (x <= CORE[2]) & (z >= CORE[1]) & (z <= CORE[3])

# ---------------------------------------------------------------- the hut (card: (-390, 340), platform 30x24 on piles, floor W+4)
HCX, HCZ = -390, 340
HX1, HX2, HZ1, HZ2 = HCX - 15, HCX + 14, HCZ - 12, HCZ + 11        # -405..-376 x 328..351
LAGOON_R = 21

# ---------------------------------------------------------------- grids
def grids():
    x1, z1, x2, z2 = PLACE; X, Z = np.meshgrid(np.arange(x1, x2 + 1), np.arange(z1, z2 + 1))
    def grid(s, a): return a[z1 - s.z0:z2 - s.z0 + 1, x1 - s.x0:x2 - s.x0 + 1].astype(np.int32)
    al = np.load(os.path.join(OUT, "allow.npz")); A = al["allow"]; ax0, az0 = int(al["x0"]), int(al["z0"])
    allow = A[z1 - az0:z2 - az0 + 1, x1 - ax0:x2 - ax0 + 1].copy()
    base = Scan(os.path.join(OUT, "base.bin"))
    nat = grid(base, base.ground)
    d = open(os.path.join(OUT, "terrain.bin"), "rb").read(); assert d[:4] == b"LETA"
    tx0, tz0, tw, th = struct.unpack("<4i", d[4:20]); TH = np.frombuffer(d, "<i2", tw * th, 20).reshape(th, tw).astype(np.int32)
    fr = TH[z1 - tz0:z2 - tz0 + 1, x1 - tx0:x2 - tx0 + 1]
    before = np.where(fr != NONE, fr, nat)            # the ground before the fens: the same on every run
    gr = dict(X=X, Z=Z, x1=x1, z1=z1, before=before, allow=allow, place=in_place(X, Z), core=in_core(X, Z))
    pre_path = os.path.join(OUT, "fens_pre.bin")
    if os.path.exists(pre_path):
        pre = Scan(pre_path); gr.update(live=grid(pre, pre.ground), top=grid(pre, pre.top), lwater=grid(pre, pre.water))
    return gr
def ix(gr, x, z): return z - gr["z1"], x - gr["x1"]

def cheb_dist(src, n):
    d = np.where(src, 0, 999)
    for _ in range(n):
        p = np.pad(d, 1, constant_values=999); m = d.copy()
        for dz in (0, 1, 2):
            for dx in (0, 1, 2): m = np.minimum(m, p[dz:dz + d.shape[0], dx:dx + d.shape[1]] + 1)
        d = m
    return d
def eucl_dist(src, n):
    """distance (Euclidean, by a chamfer 3-4 pass, in blocks) to the nearest True cell, capped at n"""
    INF = 10 ** 6; d = np.where(src, 0, INF).astype(np.int64)
    H, W_ = d.shape
    for _ in range(max(2, n // 6 + 2)):
        p = np.pad(d, 1, constant_values=INF)
        m = d.copy()
        for dz, dx, c in ((0, 1, 3), (2, 1, 3), (1, 0, 3), (1, 2, 3), (0, 0, 4), (0, 2, 4), (2, 0, 4), (2, 2, 4)):
            m = np.minimum(m, p[dz:dz + H, dx:dx + W_] + c)
        if (m == d).all(): break
        d = m
    return np.minimum(d / 3.0, n)
def vnoise(x, z, cell, seed):
    gx, gz = x // cell, z // cell; fx = (x - gx * cell) / cell; fz = (z - gz * cell) / cell
    fx = fx * fx * (3 - 2 * fx); fz = fz * fz * (3 - 2 * fz)
    a, b_, c, d = hsh(gx, 0, gz, seed), hsh(gx + 1, 0, gz, seed), hsh(gx, 0, gz + 1, seed), hsh(gx + 1, 0, gz + 1, seed)
    return (a * (1 - fx) + b_ * fx) * (1 - fz) + (c * (1 - fx) + d * fx) * fz
def vnoise_grid(X, Z, cell, seed):
    return np.vectorize(lambda x, z: vnoise(int(x), int(z), cell, seed))(X, Z)
def components(mask):
    """4-connected components: label array (0 = none), sizes"""
    lab = np.zeros(mask.shape, np.int32); n = 0; sizes = [0]
    H, W_ = mask.shape
    for i0, j0 in zip(*np.nonzero(mask)):
        if lab[i0, j0]: continue
        n += 1; q = deque([(i0, j0)]); lab[i0, j0] = n; s = 0
        while q:
            i, j = q.popleft(); s += 1
            for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p, r = i + a, j + c
                if 0 <= p < H and 0 <= r < W_ and mask[p, r] and not lab[p, r]: lab[p, r] = n; q.append((p, r))
        sizes.append(s)
    return lab, sizes

# ---------------------------------------------------------------- the bowl
def water_level(gr):
    x1, z1, x2, z2 = PLATEAU; X, Z = gr["X"], gr["Z"]
    m = (X >= x1) & (X <= x2) & (Z >= z1) & (Z <= z2)
    return int(round(np.percentile(gr["before"][m], 40)))
LOW = 7      # HQ: W-6; the shelf east of the cleft at the hut lies at W-7 and closes the cleft (the berm there stands 8 over it)
def bowl(gr, W):
    """the bowl: plateau ground in W-6..W+8, connected; the closed holes in it (lower ground fully surrounded by the bowl: the cleft)
    belong to it; kept 6 blocks off the core edge and off the pad of bonfire 5 so that the berm and its outer slope stay in the place"""
    bf = gr["before"]; X, Z = gr["X"], gr["Z"]
    inset = (X >= CORE[0] + 6) & (X <= CORE[2] - 6) & (Z >= CORE[1] + 6) & (Z <= CORE[3] - 6)
    near_pad = cheb_dist(gr["allow"], 26) <= 24
    b0 = inset & (bf >= W - LOW) & (bf <= W + 8) & ~near_pad
    lab, sizes = components(b0)
    big = int(np.argmax(sizes)); bw = lab == big
    # holes: cells not in the bowl and lower than W-6 that cannot reach the edge of the inset area without crossing the bowl or high land
    low = ~bw & (bf < W - LOW) & inset
    lab2, _ = components(low)
    edge = set(lab2[0, :]) | set(lab2[-1, :]) | set(lab2[:, 0]) | set(lab2[:, -1])
    # a low component touching anything outside the inset or outside the bowl's neighbourhood (low land outside) is open
    H, W_ = bw.shape
    open_ = set()
    out = ~inset | (~bw & ~low & (bf < W + 1))         # low land outside the bowl
    pad_out = np.pad(out, 1, constant_values=True)
    for i, j in zip(*np.nonzero(low)):
        if pad_out[i:i + 3, j:j + 3].any(): open_.add(lab2[i, j])
    holes = low & ~np.isin(lab2, list(open_ | edge | {0}))
    bw = bw | holes
    # smooth the outline a little: no one-cell spikes (a cell in the bowl needs 2 of its 4 neighbours in it)
    for _ in range(3):
        p = np.pad(bw, 1); n4 = p[:-2, 1:-1].astype(int) + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]
        bw = bw & (n4 >= 2)
    lab, sizes = components(bw); bw = lab == int(np.argmax(sizes))
    hills = ~bw & inset & (bf > W + 8)
    # islands: high hills fully inside the bowl (not touching its outline to the outside)
    return bw, holes, hills

# ---------------------------------------------------------------- routes
def astar(cost, start, goal, x1, z1):
    """4/8-neighbour path on a cost grid (np.inf = blocked)"""
    H, W_ = cost.shape; best = {start: 0.0}; prev = {}; pq = [(0.0, start)]
    while pq:
        f, c = heapq.heappop(pq)
        if c == goal: break
        cx, cz = c; g0 = best[c]
        if f - math.hypot(cx - goal[0], cz - goal[1]) > g0 + 1e-6: continue
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, nz = cx + dx, cz + dz; i, j = nz - z1, nx - x1
            if not (0 <= i < H and 0 <= j < W_) or not np.isfinite(cost[i, j]): continue
            st = 1.4142 if dx and dz else 1.0
            g = g0 + st * cost[i, j]
            if g < best.get((nx, nz), 1e18): best[(nx, nz)] = g; prev[(nx, nz)] = c; heapq.heappush(pq, (g + math.hypot(nx - goal[0], nz - goal[1]), (nx, nz)))
    if goal not in prev and goal != start: raise SystemExit("no route %s -> %s" % (start, goal))
    path = [goal]
    while path[-1] != start: path.append(prev[path[-1]])
    return path[::-1]
def smooth_line(path, step=6):
    pts = path[::step] + [path[-1]]
    for _ in range(2):
        q = [pts[0]]
        for a, b in zip(pts, pts[1:]): q += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        pts = q + [pts[-1]]
    return pts
def cells_of(pts):
    """the 4-connected cells along a polyline of points"""
    line = []
    for (ax, az), (bx, bz) in zip(pts, pts[1:]):
        L = max(1, int(math.hypot(bx - ax, bz - az) * 3))
        for i in range(L): line.append((ax + (bx - ax) * i / L, az + (bz - az) * i / L))
    line.append(pts[-1]); cells = []
    for (x, z) in line:
        c = (int(math.floor(x)), int(math.floor(z)))
        if cells and c == cells[-1]: continue
        if cells and abs(c[0] - cells[-1][0]) + abs(c[1] - cells[-1][1]) == 2:
            p1 = (c[0], cells[-1][1]); p2 = (cells[-1][0], c[1]); cells.append(min((p1, p2), key=lambda q: math.hypot(q[0] + .5 - x, q[1] + .5 - z)))
        cells.append(c)
    return cells
def route(gr, cost, waypoints, smooth=5):
    """A* through the waypoints, smoothed; returns the 4-connected cells"""
    pts = []
    for a, b in zip(waypoints, waypoints[1:]):
        p = astar(cost, a, b, gr["x1"], gr["z1"])
        pts += p if not pts else p[1:]
    sm = smooth_line(pts, smooth)
    return cells_of([(x + 0.5, z + 0.5) for x, z in sm])
def brush(cells, r):
    """the set of cells within r (Euclidean, block centres) of a line of cells"""
    out = set(); ri = int(math.ceil(r))
    for (x, z) in cells:
        for dx in range(-ri, ri + 1):
            for dz in range(-ri, ri + 1):
                if dx * dx + dz * dz <= r * r + 0.01: out.add((x + dx, z + dz))
    return out
def mask_of(gr, cells):
    m = np.zeros(gr["X"].shape, bool)
    for (x, z) in cells:
        i, j = ix(gr, x, z)
        if 0 <= i < m.shape[0] and 0 <= j < m.shape[1]: m[i, j] = True
    return m

# the outer pier (top of the climb, on the east rim of the bowl), the main channel's waypoints (it loops west and comes back to the
# lagoon of the hut from the west), the side channels (to dead ends and to the ruins), the boardwalk (outer pier -> the hut, south of
# the main channel's first reach, never crossing it)
PIER_OUT = (-340, 289)          # the water end of the outer pier (boats there)
MAIN_WP = [(-342, 291), (-354, 296), (-368, 298), (-382, 302), (-416, 310), (-446, 328), (-440, 352), (-415, 351)]
SIDE_WP = [[(-340, 284), (-338, 262)],                       # north: a dead end up the east arm of the bowl
           [(-446, 328), (-470, 306), (-476, 278)],          # west: to the ruins of the village
           [(-440, 352), (-456, 372), (-462, 394)],          # south-west: to the ruins
           [(-446, 328), (-472, 340)]]                       # west: a short dead end to a ruin
BOARD_WP = [(-335, 294), (-343, 302), (-346, 310), (-358, 320), (-366, 332), (-373, 339)]
RUINS = [(-476, 290, 0), (-482, 318, 1), (-480, 366, 2), (-470, 404, 3), (-450, 396, 4), (-468, 336, 5)]   # house centres
POOLS = [(-372, 296), (-428, 318), (-470, 346), (-450, 382), (-344, 258)]   # near which channel point the 5 pools go

CLIMB_CUT = 4                   # the climb cuts at most 4 into the slope (a deeper cut would carry its 1:1 slope far up the hill)
TRESTLE = 2                     # higher than 2 over the ground the climb is a deck on piles (no fill)
def climb_route(gr, W, start, end, K):
    """the climb from the pad of bonfire 5: a 4-connected line of exactly K steps from `start` (feet level f0) to `end` (feet level
    f0 + K/2), the level rising 0.5 per step: dynamic programming over (step, cell, direction) minimising the earth work
    |ground - (level - 1)| + a turn cost; cells of the bowl, of the pad and outside the core are not allowed"""
    bf = gr["before"].astype(float); X, Z = gr["X"], gr["Z"]
    x1, z1 = gr["x1"], gr["z1"]
    win = (X >= min(start[0], end[0]) - 30) & (X <= max(start[0], end[0]) + 30) & (Z >= min(start[1], end[1]) - 30) & (Z <= max(start[1], end[1]) + 30)
    ok = win & gr["core"] & ~gr["allow"]
    f0 = gr["f0"]
    INF = 1e18; D = 4; dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))
    H, W_ = bf.shape
    cost = np.full((D, H, W_), INF)
    si, sj = ix(gr, *start)
    for d in range(D): cost[d, si, sj] = 0.0
    back = np.zeros((K + 1, D, H, W_), np.int8)
    for k in range(1, K + 1):
        lvl = f0 + k / 2.0 - 1                          # ground under the path at step k
        cut = np.maximum(bf - lvl, 0); fil = np.maximum(lvl - bf, 0)
        work = 1.0 + cut * 1.5 + np.maximum(cut - 2, 0) ** 2 * 2 + np.minimum(fil, 3) * 0.4 + np.maximum(fil - 3, 0) * 0.15
        work = np.where(ok & (cut <= CLIMB_CUT), work, INF)
        new = np.full((D, H, W_), INF); arg = np.zeros((D, H, W_), np.int8)
        for d, (dx, dz) in enumerate(dirs):
            # arrive at (i, j) moving in direction d from (i - dz, j - dx)
            src = np.full((D, H, W_), INF)
            src[:, max(dz, 0):H + min(dz, 0), max(dx, 0):W_ + min(dx, 0)] = cost[:, max(-dz, 0):H - max(dz, 0), max(-dx, 0):W_ - max(dx, 0)]
            turn = np.array([0.0 if pd == d else (INF if dirs[pd] == (-dx, -dz) else 5.0) for pd in range(D)])[:, None, None]
            tot = src + turn
            a = np.argmin(tot, axis=0); v = np.min(tot, axis=0)
            new[d] = v + work; arg[d] = a
        cost = new; back[k] = arg
    ei, ej = ix(gr, *end)
    d = int(np.argmin(cost[:, ei, ej]))
    if cost[d, ei, ej] >= INF / 2: raise SystemExit("the climb cannot reach the pier in %d steps" % K)
    cells = [end]; i, j = ei, ej
    for k in range(K, 0, -1):
        pd = int(back[k, d, i, j]); dx, dz = dirs[d]; i, j = i - dz, j - dx; d = pd
        cells.append((j + x1, i + z1))
    cells = cells[::-1]
    if cells[0] != start: raise SystemExit("climb: wrong start %s" % (cells[0],))
    if len(set(cells)) != len(cells): raise SystemExit("climb: the line crosses itself")
    return cells

def features(gr, W, bw, holes):
    """the routes and the sites (all in plan): main channel, side channels, boardwalk with its gaps, pools, ruins"""
    bf = gr["before"]; X, Z = gr["X"], gr["Z"]
    inner = cheb_dist(~bw, 8)                                     # distance inside the bowl
    # channels: through the bowl, away from its rim (cost rises near the rim and over high ground)
    cc = np.where(bw & (inner >= 4), 1.0 + np.maximum(bf - W, 0) * 0.08 + np.maximum(6 - inner, 0) * 0.2, np.inf)
    hut = (X >= HX1 - 2) & (X <= HX2 + 2) & (Z >= HZ1 - 2) & (Z <= HZ2 + 2)
    cc = np.where(hut, np.inf, cc)
    main = route(gr, cc, MAIN_WP, 5)
    side = [route(gr, cc, wp, 4) for wp in SIDE_WP]
    mainm = mask_of(gr, brush(main, 2.6))
    sidem = mask_of(gr, set().union(*[brush(c, 2.0) for c in side]))
    # boardwalk: on the bowl, 3 off the main channel, 2 off the side channels
    nearch = (cheb_dist(mainm, 4) <= 1) | (cheb_dist(sidem, 3) <= 1)
    bc = np.where(bw & (inner >= 1) & ~nearch & ~hut, 1.0 + np.abs(bf - W) * 0.2 + (cheb_dist(mainm, 6) <= 3) * 3.0, np.inf)
    board = route(gr, bc, BOARD_WP, 4)
    # its width: the line and the cell on its left (a 2-wide deck); gaps: 5 gaps of 3 cells along it, every ~1/6, the 4th one dark
    deck = []
    for k, (x, z) in enumerate(board):
        a = board[max(0, k - 2)]; b_ = board[min(len(board) - 1, k + 2)]
        tx, tz = b_[0] - a[0], b_[1] - a[1]
        nx, nz = (0, -1 if tx > 0 else 1) if abs(tx) >= abs(tz) else (1 if tz > 0 else -1, 0)    # left of the way
        deck.append(((x, z), (x + nx, z + nz), (nx, nz)))
    n = len(board); gaps = []
    for g in range(5):
        k = int(n * (g + 1) / 6.5) + 3
        gaps.append(dict(k=k, dark=(g == 3)))
    # pools: 5 small ponds beside the channels (3x3 .. 5x5), > 30 from the hut, > 25 apart
    chm = mainm | sidem; allc = main + [c for s_ in side for c in s_]
    pools = []
    chd = cheb_dist(chm, 6)
    for k, (px, pz) in enumerate(POOLS):
        r = 1 + (k % 2)                                   # 3x3 or 5x5
        best = None
        for qz in range(pz - 18, pz + 19):
            for qx in range(px - 18, px + 19):
                cells = [(qx + a, qz + c) for a in range(-r, r + 1) for c in range(-r, r + 1)]
                ok = True; near = False
                for q in cells:
                    i_, j_ = ix(gr, *q)
                    if not (0 <= i_ < bw.shape[0] and 0 <= j_ < bw.shape[1]) or not bw[i_, j_] or inner[i_, j_] < 3 or chd[i_, j_] < 1: ok = False; break
                    if chd[i_, j_] <= 2: near = True
                if not ok or not near: continue
                if math.hypot(qx - HCX, qz - HCZ) <= 30 + r or any(math.hypot(qx - p["x"], qz - p["z"]) <= 25 for p in pools): continue
                sc = math.hypot(qx - px, qz - pz) + hsh(qx, k, qz, 5101)
                if best is None or sc < best[0]: best = (sc, qx, qz)
        if not best: raise SystemExit("no pool site near %s" % ((px, pz),))
        pools.append(dict(id=k + 1, x=best[1], z=best[2], r=r))
    # ruins: 6 houses on piles near the side channels: footprint (+-4) in the bowl, off the channels, the boardwalk, the pools, 14 apart
    boardm = mask_of(gr, [c for d_ in deck for c in d_[:2]]); bd = cheb_dist(boardm, 6); pd_ = cheb_dist(mask_of(gr, [(p["x"], p["z"]) for p in pools]), 9)
    chd2 = cheb_dist(chm, 3)
    ruins = []; KINDS = [(1, 0, "note"), (0, 1, "empty"), (1, 1, "ambush"), (0, 0, "ruin"), (0, 2, "ruin"), (1, 2, "ruin")]
    for k, (rx, rz, _) in enumerate(RUINS):
        kind, rot, role = KINDS[k]; best = None
        for qz in range(rz - 16, rz + 17):
            for qx in range(rx - 16, rx + 17):
                ok = True
                for a in range(-4, 5):
                    for c_ in range(-4, 5):
                        i_, j_ = ix(gr, qx + a, qz + c_)
                        if not (0 <= i_ < bw.shape[0] and 0 <= j_ < bw.shape[1]) or not bw[i_, j_] or holes[i_, j_] or inner[i_, j_] < 2 or chd2[i_, j_] < 2 or bd[i_, j_] < 4 or pd_[i_, j_] < 8: ok = False; break
                    if not ok: break
                if not ok or any(math.hypot(qx - r_["x"], qz - r_["z"]) < 14 for r_ in ruins): continue
                sc = math.hypot(qx - rx, qz - rz) + hsh(qx, k, qz, 5111)
                if best is None or sc < best[0]: best = (sc, qx, qz)
        if not best: raise SystemExit("no ruin site near %s" % ((rx, rz),))
        ruins.append(dict(id=k + 1, x=best[1], z=best[2], kind=kind, rot=rot, role=role))
    return dict(main=main, side=side, mainm=mainm, sidem=sidem, board=board, deck=deck, gaps=gaps, pools=pools, inner=inner, ruins=ruins)

def climb(gr, W):
    """the start cell (west of the pad of bonfire 5, level with it), the end (the land end of the outer pier on the berm), K steps"""
    al = gr["allow"]
    hz = HEARTH5[2]; pad_y = HEARTH5[1] - 1
    start = None
    for x in range(HEARTH5[0], HEARTH5[0] - 40, -1):
        if not al[ix(gr, x, hz)]: start = (x, hz); break
    gr["f0"] = pad_y + 1                                   # feet level on the pad
    K = 2 * ((W + 2) - gr["f0"])
    end = (PIER_OUT[0] + 7, PIER_OUT[1])
    if (abs(end[0] - start[0]) + abs(end[1] - start[1]) - K) % 2: end = (end[0] - 1, end[1])     # a 4-connected line of K steps: parity
    return start, end, K

# ---------------------------------------------------------------- relief
def relief(gr, W, bw, holes, hills, ft, cpath):
    bf = gr["before"].astype(np.int32); X, Z = gr["X"], gr["Z"]
    T = bf.copy()
    # the bog: shallows, mud flats and tussocks by noise; at most 6 cut from the natural ground (islands rise where the ground was high)
    m = 0.65 * vnoise_grid(X, Z, 9, 5001) + 0.35 * vnoise_grid(X, Z, 4, 5002)
    lv = np.select([m < 0.40, m < 0.50, m < 0.62, m < 0.76], [W - 2, W - 1, W, W + 1], W + 2)
    bog = np.maximum(lv, bf - 6)
    bog = np.where(holes, np.maximum(np.minimum(bf, W - 5), W - 8), bog)        # the cleft: deep dark water
    T = np.where(bw, bog, T)
    # no cliffs where the bowl meets the hills: the bog rises 1:1 towards the higher land round it (the channels are cut after)
    hi = ~bw & gr["place"] & (bf > W + 1)
    L = np.where(hi, bf, -10 ** 6).astype(np.int64)
    for _ in range(16):
        Lp = np.pad(L, 1, constant_values=-10 ** 6); nl = L.copy()
        for dz in (0, 1, 2):
            for dx in (0, 1, 2): nl = np.maximum(nl, Lp[dz:dz + L.shape[0], dx:dx + L.shape[1]] - 1)
        L = np.where(hi, bf, nl)
    T = np.where(bw & ~holes, np.maximum(T, np.minimum(L, bf)), T)
    # channels, the lagoon under the hut, the pools
    T = np.where(ft["mainm"], np.minimum(T, W - 3), T)
    T = np.where(ft["sidem"] & ~ft["mainm"], np.minimum(T, W - 2), T)
    hutw = (X >= HX1 - 3) & (X <= HX2 + 3) & (Z >= HZ1 - 3) & (Z <= HZ2 + 3) & bw
    T = np.where(hutw, np.minimum(T, W - 2), T)
    for r_ in ft["ruins"]:                              # the ruins stand in water 2 deep (their floors: W-1 flooded, or W on piles)
        rm = (np.abs(X - r_["x"]) <= 4) & (np.abs(Z - r_["z"]) <= 4); T = np.where(rm, np.minimum(np.maximum(T, W - 2), W - 2), T)
    poolm = np.zeros(T.shape, bool)
    for p in ft["pools"]:
        r = p["r"]; pm = (np.abs(X - p["x"]) <= r) & (np.abs(Z - p["z"]) <= r); poolm |= pm
        ring = (np.abs(X - p["x"]) <= r + 2) & (np.abs(Z - p["z"]) <= r + 2) & bw        # shallow water round the pool: its head is seen over it
        T = np.where(ring, np.minimum(T, W - 1), T)
        T = np.where(pm, W - 3, T)
    # the boardwalk: water or mud under the deck (deck at W+1), the gaps: water each side of a tussock, the dark gap W-5
    deckc = set(); gapc = {}; tuss = set(); dark = set()
    for k, (a, b_, n_) in enumerate(ft["deck"]):
        g = next((g for g in ft["gaps"] if g["k"] - 1 <= k <= g["k"] + 1), None)
        if g:
            for c in (a, b_):
                gapc[c] = g
                if g["dark"]: dark.add(c)
                elif k == g["k"]: tuss.add(c)
        else: deckc.add(a); deckc.add(b_)
    for c in deckc:
        i, j = ix(gr, *c); T[i, j] = min(T[i, j], W)
    for c, g in gapc.items():
        i, j = ix(gr, *c)
        T[i, j] = W - 5 if g["dark"] else (W + 1 if c in tuss else min(T[i, j], W - 1))
    for c in list(dark):                                 # the dark water round the dark gap too (3x3 per cell)
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                q = (c[0] + dx, c[1] + dz); i, j = ix(gr, *q)
                if q not in deckc and bw[i, j]: T[i, j] = min(T[i, j], W - 5)
    # the berm: the rim cells of the bowl where the land outside is lower than W+1, 3 wide, at W+1
    out_low = ~bw & (bf < W + 1)
    rim = bw & ~holes & (cheb_dist(out_low, 2) <= 1)
    berm = bw & ~holes & (cheb_dist(rim, 3) <= 2) & ~ft["mainm"] & ~ft["sidem"]
    T = np.where(berm, W + 1, T)
    # the climb: the graded way from the pad to the outer pier (cut / fill under it, a berm of 1 and 1:1 slopes), outside the bowl
    surf = {}; prof = []
    f0 = gr["f0"]
    for k, c in enumerate(cpath):
        s2 = 2 * f0 + k; prof.append(s2)
    for k, c in enumerate(cpath):                         # width 3 (brush r 1), the lower level wins across
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                q = (c[0] + dx, c[1] + dz); i, j = ix(gr, *q)
                if gr["allow"][i, j]: continue
                if q not in surf or prof[k] < surf[q]: surf[q] = prof[k]
    for _ in range(60):
        ch = False
        for (x, z), s2 in list(surf.items()):
            nb = [surf[q] for q in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)) if q in surf]
            if s2 > min(nb) + 1: surf[(x, z)] = min(nb) + 1; ch = True
        if not ch: break
    climbm = np.zeros(T.shape, bool); fixed = np.zeros(T.shape, bool); F = T.astype(float); trestle = set()
    for (x, z), s2 in surf.items():
        y = (s2 - 1) // 2 - 1 if s2 % 2 else s2 // 2 - 1          # ground top under the path block (a slab cell: the slab on y+1)
        i, j = ix(gr, x, z); climbm[i, j] = True
        if y - bf[i, j] > TRESTLE and not bw[i, j]: trestle.add((x, z)); continue     # a deck on piles: the ground stays
        F[i, j] = y; fixed[i, j] = True
    keep = ~gr["place"] | gr["allow"]
    # 1:1 slopes round the fixed cells (the climb) outside the bowl; and outward of the berm: 1:1 down to the land
    src = fixed & ~keep
    U = np.where(src, F, 1e9); L = np.where(src, F, -1e9)
    for _ in range(40):
        Up = np.pad(U, 1, constant_values=1e9); Lp = np.pad(L, 1, constant_values=-1e9); nu = U.copy(); nl = L.copy()
        for dz in (0, 1, 2):
            for dx in (0, 1, 2):
                nu = np.minimum(nu, Up[dz:dz + U.shape[0], dx:dx + U.shape[1]] + 1); nl = np.maximum(nl, Lp[dz:dz + L.shape[0], dx:dx + L.shape[1]] - 1)
        U = np.where(src, F, nu); L = np.where(src, F, nl)
    free = ~src & ~keep & ~bw & (cheb_dist(src, 8) <= CLIMB_CUT + 2)      # the slopes of the cuts (<= 4) and fills (<= 2) of the climb
    v = np.where(L <= U, np.clip(F, L, U), U)
    T = np.where(free, np.round(v), T).astype(np.int32)
    T = np.where(src, F.astype(np.int32), T)
    bermm = berm.copy()
    out = ~bw & gr["place"] & ~keep & ~climbm
    d = cheb_dist(bermm, 20)
    T = np.where(out, np.maximum(T, W + 1 - d), T)
    # water: every bowl cell below W; containment (a water cell's 4 neighbours are water or ground >= W)
    for _ in range(4):
        wet = bw & (T < W)
        p = np.pad(wet, 1)
        nbw = p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
        leak = nbw & ~wet & (T < W)
        if not leak.any(): break
        T = np.where(leak, W, T)
    wet = bw & (T < W)
    Wt = np.where(wet, W, NONE).astype(np.int32)
    T = np.where(keep, bf, T)
    return dict(trestle=trestle, T=T, Wt=Wt, berm=[(int(j + gr["x1"]), int(i + gr["z1"])) for i, j in zip(*np.nonzero(berm))], bermm=berm, surf=surf, prof=prof,
                cpath=cpath, climbm=climbm, deckc=deckc, gapc=gapc, tuss=tuss, dark=dark, poolm=poolm, hutw=hutw)

# ---------------------------------------------------------------- plan
def plan_png(gr, W, bw, holes, hills, ft, rl, path, out, meta=None):
    from PIL import Image, ImageDraw
    S = 4; x1, z1, x2, z2 = PLACE; w, h = (x2 - x1 + 1) * S, (z2 - z1 + 1) * S
    img = Image.new("RGB", (w, h + 92), (20, 20, 24)); d = ImageDraw.Draw(img)
    T = rl["T"] if rl else gr["before"]; Wt = rl["Wt"] if rl else np.full(T.shape, NONE)
    for i in range(T.shape[0]):
        for j in range(T.shape[1]):
            g = int(np.clip((T[i, j] - 80) * 2.8, 0, 255)); col = (g // 2 + 30, g // 2 + 38, g // 2 + 26)
            if bw[i, j]: col = (g // 2 + 20, g // 2 + 50, g // 2 + 20)
            if hills[i, j]: col = (g // 2 + 60, g // 2 + 50, g // 3 + 20)
            if Wt[i, j] != NONE:
                dep = int(Wt[i, j] - T[i, j]); col = (40, 70 + 14 * min(dep, 5), 60) if dep <= 1 else (30, 50, 90 + 18 * min(dep, 6))
            if gr["allow"][i, j]: col = (230, 130, 20)
            if not gr["place"][i, j]: col = tuple(v // 3 for v in col)
            d.rectangle([j * S, i * S, j * S + S - 1, i * S + S - 1], fill=col)
    def P(x, z): return ((x - x1) * S + S // 2, (z - z1) * S + S // 2)
    if rl:
        for (x, z) in rl["berm"]: d.rectangle([(x - x1) * S, (z - z1) * S, (x - x1) * S + S - 1, (z - z1) * S + S - 1], fill=(120, 80, 50))
    d.line([P(*c) for c in ft["main"]], fill=(90, 170, 255), width=3)
    for s in ft["side"]: d.line([P(*c) for c in s], fill=(70, 130, 220), width=2)
    d.line([P(*c) for c in ft["board"]], fill=(220, 190, 120), width=3)
    if path: d.line([P(*c) for c in path], fill=(255, 220, 60), width=3)
    if meta:
        for g in meta.get("gaps", []):
            cx, cz = P(g["x"], g["z"]); d.ellipse([cx - 6, cz - 6, cx + 6, cz + 6], outline=(255, 40, 40) if g["dark"] else (255, 255, 255), width=2)
        for k, p in enumerate(meta.get("pools", [])):
            cx, cz = P(p["x"], p["z"]); d.ellipse([cx - 7, cz - 7, cx + 7, cz + 7], outline=(200, 255, 120), width=3); d.text((cx + 9, cz - 6), "P%d" % (k + 1), fill=(220, 255, 160))
        for r in meta.get("ruins", []):
            cx, cz = P(r["x"], r["z"]); d.rectangle([cx - 10, cz - 10, cx + 10, cz + 10], outline=(200, 120, 255), width=2); d.text((cx + 12, cz - 6), "R%d %s" % (r["id"], r["role"]), fill=(220, 170, 255))
        for l in meta.get("lanterns", []):
            cx, cz = P(l[0], l[2]); d.ellipse([cx - 2, cz - 2, cx + 2, cz + 2], fill=(255, 240, 120) if l[3] == "lantern" else (120, 220, 255))
    d.rectangle([(HX1 - x1) * S, (HZ1 - z1) * S, (HX2 + 1 - x1) * S, (HZ2 + 1 - z1) * S], outline=(255, 80, 200), width=3)
    d.ellipse([P(HCX - LAGOON_R, HCZ - LAGOON_R), P(HCX + LAGOON_R, HCZ + LAGOON_R)], outline=(255, 120, 200))
    d.ellipse([(HCX - 24 - x1) * S, (HCZ - 24 - z1) * S, (HCX + 24 - x1) * S, (HCZ + 24 - z1) * S], outline=(255, 255, 255))
    bx, bz = HEARTH5[0], HEARTH5[2]; d.ellipse([(bx - x1) * S - 7, (bz - z1) * S - 7, (bx - x1) * S + 7, (bz - z1) * S + 7], fill=(255, 140, 0))
    d.rectangle([(CORE[0] - x1) * S, (CORE[1] - z1) * S, (CORE[2] + 1 - x1) * S, (CORE[3] + 1 - z1) * S], outline=(230, 60, 60), width=2)
    for x in range(-500, -250, 20):
        d.text(((x - x1) * S + 2, 2), str(x), fill=(255, 255, 0))
    for z in range(240, 436, 20):
        d.text((2, (z - z1) * S + 2), str(z), fill=(255, 255, 0))
    t = meta or {}
    d.text((6, h + 4), "T-026 Crooked Fens: plan (1 block = %d px, north up). Red = place core (+16 seam). W = %d (water), the bowl green, hills (> W+8) ochre, berm brown." % (S, W), fill=(255, 255, 255))
    d.text((6, h + 20), "light blue = main channel (%s cells), blue = side channels, sand = boardwalk (gaps: white, dark gap red), yellow = climb from bonfire 5 (orange)," % t.get("main_len", "?"), fill=(255, 255, 255))
    d.text((6, h + 36), "pink = hut platform 30x24 and its lagoon, white ring = zone fens_hut r 24, P = pools, R = ruins, dots = lanterns (yellow lantern / cyan soul).", fill=(255, 255, 255))
    d.text((6, h + 52), t.get("checks", ""), fill=(255, 210, 120))
    d.text((6, h + 68), t.get("checks2", ""), fill=(255, 210, 120))
    img.save(out)

def checks(gr, W, bw, rl):
    """HQ T-026, 1: stop when the berm stands more than 8 above the natural ground, or when more than 15 is cut on 10% of the bowl"""
    T = rl["T"]; bf = gr["before"]
    bm = mask_of(gr, rl["berm"])
    berm_h = int((T[bm] - bf[bm]).max()) if bm.any() else 0         # the berm's ground is W+1
    cut = bf - T
    cut15 = float((cut[bw] > 15).mean())
    fill = T - bf; out = ~bw & gr["place"] & (fill > 0) & ~rl["climbm"]
    if out.any():
        i, j = np.unravel_index(np.argmax(np.where(out, fill, -999)), fill.shape); print("   max fill outside the bowl at", (int(j + gr["x1"]), int(i + gr["z1"])), int(fill[i, j]))
    return dict(berm_max=berm_h, cut15=cut15, cut_max=int(cut[bw].max()), fill_out_max=int(fill[out].max()) if out.any() else 0)

def plan_main():
    gr = grids(); W = water_level(gr); bw, holes, hills = bowl(gr, W)
    ft = features(gr, W, bw, holes)
    start, end, K = climb(gr, W)
    cpath = climb_route(gr, W, start, end, K)
    rl = relief(gr, W, bw, holes, hills, ft, cpath)
    ck = checks(gr, W, bw, rl)
    print("W", W, "bowl", int(bw.sum()), "holes", int(holes.sum()), "main", len(ft["main"]), "board", len(ft["board"]), "climb", len(cpath), "checks", ck)
    meta = dict(main_len=len(ft["main"]), pools=ft["pools"], ruins=ft["ruins"], gaps=[dict(x=ft["board"][g["k"]][0], z=ft["board"][g["k"]][1], dark=g["dark"]) for g in ft["gaps"]],
                checks="checks: berm max %d over the natural ground (stop > 8); cut > 15 on %.1f%% of the bowl (stop >= 10%%), max cut %d" % (ck["berm_max"], 100 * ck["cut15"], ck["cut_max"]),
                checks2="climb %d cells (60..100), main channel %d (150..220), boardwalk %d" % (len(cpath), len(ft["main"]), len(ft["board"])))
    plan_png(gr, W, bw, holes, hills, ft, rl, cpath, os.path.join(ROOT, "docs/reports/T-026/fens_plan.png"), meta)
    return gr, W, bw, holes, hills, ft, cpath, rl, ck
# ---------------------------------------------------------------- the blocks of the whole place
BOTTOM = Mix({"mud": 55, "clay": 25, "coarse_dirt": 10, "muddy_mangrove_roots": 10}, 5701)
BOGLAND = Mix({"mud": 30, "grass_block[snowy=false]": 30, "coarse_dirt": 15, "moss_block": 10, "muddy_mangrove_roots": 15}, 5702)
BERM = Mix({"mud": 50, "muddy_mangrove_roots": 30, "packed_mud": 20}, 5703)
FOREST = Mix({"grass_block[snowy=false]": 50, "podzol[snowy=false]": 20, "coarse_dirt": 15, "moss_block": 15}, 5704)
ROCK = Mix({"stone": 40, "andesite": 25, "tuff": 20, "cobblestone": 15}, 5705)
def build(gr, W, bw, holes, hills, ft, rl):
    import fens_build as FB
    b = B("fens"); c = FB.Ctx(sys.modules[__name__], gr, rl, W)
    meta = {}
    meta["hut"] = FB.hut(b, c, sys.modules[__name__])
    meta["dark_posts"] = FB.boardwalk(b, c, ft)
    meta["climb"] = FB.climb_blocks(b, c, rl, gr, sys.modules[__name__])
    # the outer pier: from the end of the climb west over the water, 3 wide; 2 boats beside its water end
    ex, ez = rl["cpath"][-1]
    cells = [(x, z) for x in range(PIER_OUT[0], ex) for z in (ez - 1, ez, ez + 1)]
    FB.pier(b, c, cells, None)
    for (x, z) in ((PIER_OUT[0], ez - 2), (PIER_OUT[0], ez + 2)):
        for y in range(c.g(x, z) + 1, W + 3): b.set(x, y, z, FB.water_fence(c, x, y, z))
        b.set(x, W + 3, z, FB.lantern("lantern"))
    wet_cells = [(x, z) for (x, z) in ft["main"][:20] if c.wet(x, z) and (x, z) not in cells and all((x + a, z + d) not in cells for a in (-1, 0, 1) for d in (-1, 0, 1))]
    bo = []
    for (x, z) in wet_cells:
        if all(abs(x - p[0]) + abs(z - p[2]) >= 3 for p in bo): bo.append([x, W, z])
        if len(bo) == 2: break
    meta["boats_out"] = bo; meta["pier_out"] = [PIER_OUT[0] + 2, W + 1, ez]
    meta["lanterns"] = FB.lanterns(b, c, ft, sys.modules[__name__], gr)
    meta["ruins"] = [FB.ruin_place(b, c, r_["kind"], r_["x"], r_["z"], r_["rot"], r_["role"]) for r_ in ft["ruins"]]
    for r_, m_ in zip(ft["ruins"], meta["ruins"]): m_["id"] = r_["id"]
    # trees: mangroves in the bog, swamp oaks on the land of the bowl, the islands and outside it (the ridge, the slopes)
    X, Z = gr["X"], gr["Z"]; T = rl["T"]
    block = np.zeros(T.shape, bool)
    block |= cheb_dist(ft["mainm"] | ft["sidem"], 3) <= 2
    block |= cheb_dist(mask_of(gr, [q for d_ in ft["deck"] for q in d_[:2]]), 4) <= 3
    block |= (X >= HX1 - 7) & (X <= HX2 + 7) & (Z >= HZ1 - 7) & (Z <= HZ2 + 7)
    for r_ in ft["ruins"]: block |= (np.abs(X - r_["x"]) <= 7) & (np.abs(Z - r_["z"]) <= 7)
    block |= cheb_dist(rl["poolm"], 5) <= 4
    block |= cheb_dist(rl["climbm"], 5) <= 3
    block |= ~gr["core"] | gr["allow"] | (cheb_dist(gr["allow"], 4) <= 3)
    block |= (np.abs(X - PIER_OUT[0]) <= 12) & (np.abs(Z - ez) <= 6)
    for (x, y, z, kd) in meta["lanterns"]: block |= (np.abs(X - x) <= 2) & (np.abs(Z - z) <= 2)
    for (dx, dz, dd) in [(d_["x"], d_["z"], 0) for d_ in []]: pass
    trees = []
    for gz in range(CORE[1] + 2, CORE[3] - 2, 8):
        for gx in range(CORE[0] + 2, CORE[2] - 2, 8):
            x = gx + int(hsh(gx, 0, gz, 5801) * 6); z = gz + int(hsh(gx, 1, gz, 5802) * 6)
            i, j = ix(gr, x, z)
            if block[max(0, i - 2):i + 3, max(0, j - 2):j + 3].any(): continue
            inb = bw[i, j]; dep = W - T[i, j]
            if inb and dep > 2: continue
            if hsh(gx, 2, gz, 5803) < (0.25 if inb else 0.45): continue
            nb = [T[i + a, j + d] for a, d in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if max(abs(v - T[i, j]) for v in nb) >= 3: continue
            kind = "mangrove" if (inb and (dep > 0 or hsh(x, 3, z, 5804) < 0.6)) else "oak"
            trees.append((x, z, kind))
    for (x, z, kind) in trees:
        (FB.mangrove if kind == "mangrove" else FB.swamp_oak)(b, c, x, z, 5900 + (x * 7 + z) % 97)
    meta["trees"] = len(trees)
    return b, c, meta

def surface(b, c, gr, rl, bw, ft):
    """every column of the place (not the pad of bonfire 5): the ground top by the palette, 2 blocks under it, air from the ground (or
    the water) up to what stood there (trees, snow, plants) where nothing of ours is; water plants and lily pads"""
    T = rl["T"]; Wt = rl["Wt"]; W = c.W; n = 0
    chm = ft["mainm"] | ft["sidem"]; poolring = cheb_dist(rl["poolm"], 3) <= 2
    darkm = mask_of(gr, rl["dark"]); darkring = cheb_dist(darkm, 3) <= 2
    under = set()
    for (x, y, z), s_ in b.v.items():
        if y in (W + 1, W) and s_ != "minecraft:air": under.add((x, z))
    nearland = cheb_dist(Wt == NONE, 2) <= 1
    for i in range(T.shape[0]):
        for j in range(T.shape[1]):
            if not gr["place"][i, j] or gr["allow"][i, j]: continue
            x, z = j + gr["x1"], i + gr["z1"]; y = int(T[i, j])
            wet = Wt[i, j] != NONE
            nb = [T[i + a, j + d] for a, d in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= i + a < T.shape[0] and 0 <= j + d < T.shape[1]]
            steep = (not bw[i, j]) and max(abs(v - y) for v in nb) >= 3
            drop = int(max(y - v for v in nb)) if nb else 0
            if b.get(x, y, z) is None:
                if wet: top = BOTTOM.at(x, y, z)
                elif rl["bermm"][i, j]: top = BERM.at(x, y, z)
                elif bw[i, j]: top = BOGLAND.at(x, y, z)
                elif steep: top = ROCK.at(x, y, z)
                else: top = FOREST.at(x, y, z)
                b.set(x, y, z, top)
                for k in range(1, max(2, min(drop, 24)) + 1):     # the open side faces of the column (a lower neighbour): no old snow shows
                    if b.get(x, y - k, z) is None:
                        b.set(x, y - k, z, ROCK.at(x, y - k, z) if (steep or k > 3) else ("minecraft:mud" if bw[i, j] else "minecraft:dirt"))
            if wet:
                # plants: lily pads near the land (not on channels, not round the pools and the dark gap, not under decks), seagrass, dripleaf
                dep = W - y; r = hsh(x, 6, z, 5750)
                free_top = (x, z) not in under and b.get(x, W + 1, z) is None
                if free_top and nearland[i, j] and not chm[i, j] and not poolring[i, j] and not darkring[i, j] and not rl["hutw"][i, j] and r < 0.24:
                    b.set(x, W + 1, z, "minecraft:lily_pad")
                elif dep >= 2 and r > 0.93 and b.get(x, y + 1, z) is None and not poolring[i, j] and not darkring[i, j]:
                    b.set(x, y + 1, z, "minecraft:seagrass")
                elif dep == 1 and nearland[i, j] and free_top and not chm[i, j] and not poolring[i, j] and 0.24 <= r < 0.30 and b.get(x, W, z) is None:
                    b.set(x, W, z, "minecraft:small_dripleaf[facing=%s,half=lower,waterlogged=true]" % ("north", "east", "south", "west")[int(hsh(x, 7, z, 5751) * 4)])
                    b.set(x, W + 1, z, "minecraft:small_dripleaf[facing=%s,half=upper,waterlogged=false]" % ("north", "east", "south", "west")[int(hsh(x, 7, z, 5751) * 4)])
                elif dep == 1 and nearland[i, j] and free_top and not chm[i, j] and not poolring[i, j] and 0.30 <= r < 0.34 and b.get(x, W, z) is None:
                    f = ("north", "east", "south", "west")[int(hsh(x, 8, z, 5752) * 4)]
                    b.set(x, W, z, "minecraft:big_dripleaf_stem[facing=%s,waterlogged=true]" % f); b.set(x, W + 1, z, "minecraft:big_dripleaf[facing=%s,tilt=none,waterlogged=false]" % f)
                lo = W + 1
            else:
                lo = y + 1
                if bw[i, j] and b.get(x, y + 1, z) is None and str(b.get(x, y, z)).split("[")[0] in ("minecraft:grass_block", "minecraft:moss_block", "minecraft:mud"):
                    r = hsh(x, 9, z, 5753)
                    if r < 0.12: b.set(x, y + 1, z, "minecraft:short_grass")
                    elif r < 0.16: b.set(x, y + 1, z, "minecraft:fern")
                    elif r < 0.17: b.set(x, y + 1, z, "minecraft:brown_mushroom")
                if rl["bermm"][i, j] and b.get(x, y + 1, z) is None and hsh(x, 10, z, 5754) < 0.12:
                    b.set(x, y + 1, z, "minecraft:mangrove_roots[waterlogged=false]")
            top = max(int(gr["top"][i, j]), lo)
            for yy in range(lo, min(top, lo + 60) + 1):
                if b.get(x, yy, z) is None: b.set(x, yy, z, "minecraft:air"); n += 1
    return n

KIND_SKIP = {"air", "cave_air", "void_air", "barrier", "water", "lava", "short_grass", "tall_grass", "fern", "large_fern", "snow", "vine", "dead_bush",
             "bush", "leaf_litter", "wildflowers", "sugar_cane", "seagrass", "tall_seagrass", "kelp", "kelp_plant", "sweet_berry_bush", "firefly_bush",
             "short_dry_grass", "tall_dry_grass", "pumpkin", "moss_carpet", "pale_moss_carpet", "pale_hanging_moss", "bamboo", "cactus", "cocoa", "lily_pad",
             "glow_lichen", "hanging_roots", "red_bush", "big_dripleaf", "big_dripleaf_stem", "small_dripleaf", "brown_mushroom_block", "red_mushroom_block",
             "mushroom_stem", "bee_nest", "creaking_heart", "resin_clump", "pointed_dripstone"}
def scan_kind(s):
    """tools/terrain.sh scan's classes (Terrain.kind): 0 ground, 1 skip, 2 log, 3 leaves, 4 water"""
    n = s.split("[")[0].split("{")[0].replace("minecraft:", "")
    if n in ("water", "bubble_column", "ice"): return 4
    if n == "lava": return 5
    if n.endswith("leaves"): return 3
    if n.endswith("_log") or n.endswith("_wood") or n.endswith("_stem") or n.endswith("_hyphae") or "mangrove_roots" in n: return 2
    if n in KIND_SKIP or n.endswith("sapling") or n in ("poppy", "dandelion", "lilac", "peony") or \
       any(k in n for k in ("flower", "tulip", "mushroom", "orchid", "allium", "bluet", "daisy", "lily", "rose", "cornflower", "dripleaf", "eyeblossom", "petals", "bush", "carpet")):
        return 1
    return 0
def expected_scan(T, Wt, cols, x, z, i, j):
    """what tools/terrain.sh scan sees in the column after the terrain write and our blocks: (ground, water top)"""
    col = cols.get((x, z), {}); w = int(Wt[i, j]); t = int(T[i, j])
    hi = max([t] + list(col.keys()) + ([w] if w != NONE else []))
    wat = NONE
    for y in range(hi, t - 40, -1):
        s_ = col.get(y)
        if s_ is None:
            if y <= t: return y, wat                       # the terrain's own ground
            if w != NONE and y <= w:
                if wat == NONE: wat = y
                continue
            continue
        k = scan_kind(s_)
        if "waterlogged=true" in s_ and k == 1 and wat == NONE: pass
        if k == 4:
            if wat == NONE: wat = y
            continue
        if k == 0: return y, wat
    return t, wat
def write_terrain(gr, rl, b, W):
    """only the columns whose scan is not yet what it should be (a re-run on the built fens rewrites nothing): the expected scan is the
    terrain (T, water) with our blocks over it, read like the scan reads the world"""
    T, Wt = rl["T"], rl["Wt"]
    now, nw = gr["live"], gr["lwater"]
    cols = {}
    for (x, y, z), s_ in b.v.items(): cols.setdefault((x, z), {})[y] = s_
    cand = gr["place"] & ~gr["allow"]
    touch = np.zeros(T.shape, bool)
    for i, j in zip(*np.nonzero(cand)):
        x, z = j + gr["x1"], i + gr["z1"]
        eg, ew = expected_scan(T, Wt, cols, x, z, i, j)
        if now[i, j] != eg or nw[i, j] != ew: touch[i, j] = True
    H = np.where(touch, T, NONE).astype(np.int32)
    lo = T.copy()
    for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): lo = np.minimum(lo, np.roll(np.roll(lo, dz, 0), dx, 1))
    F = np.minimum(np.minimum(T, now), lo) - 4
    S = np.full(T.shape, S_FOREST, np.uint8)
    Wg = np.where(touch, Wt, NONE).astype(np.int32)
    write_grid(os.path.join(OUT, "fens_terrain.bin"), gr["x1"], gr["z1"], H, F, Wg, S, np.full(T.shape, R_STONE, np.uint8), np.zeros(T.shape, np.uint8))
    return int(touch.sum())

def ruin_templates():
    """structure/fens/ruin_a.nbt, ruin_b.nbt (the 2 templates of the ruins; placed in the world by BlockWriter, rotated)"""
    import fens_build as FB, subprocess
    sd = os.path.join(DP, "structure/fens"); os.makedirs(sd, exist_ok=True)
    for k, name in ((0, "ruin_a"), (1, "ruin_b")):
        tb = FB.ruin_template_blocks(k); x1, y1, z1, x2, y2, z2 = tb.bbox()
        path = os.path.join(OUT, "fens_%s.txt" % name); tb.write_placements(path)
        subprocess.run([os.path.join(ROOT, "tools/blockwriter.sh"), "nbt", path, str(x1), str(y1), str(z1), os.path.join(sd, name + ".nbt")], check=True, capture_output=True)

def data_files(meta, W):
    from r1 import replace_lines
    replace_lines(os.path.join(ROOT, "zones/zones.txt"), ["fens_hut "], ["fens_hut        overworld cyl %d %d 24 %d %d   no_spawn   # T-026: the Hut of the Three Witches with its pier (r 24, W-7..W+38)" %
                  (HCX, HCZ, W - 7, W + 38)])
    t = meta["hut"]["table"]
    replace_lines(os.path.join(ROOT, "altars/keys.txt"), ["crown_witches "], ["crown_witches 1 %d,%d,%d Венец Трёх Ведьм" % (t[0], t[1], t[2])])

def main():
    gr, W, bw, holes, hills, ft, cpath, rl, ck = plan_main()
    if ck["berm_max"] > 8 or ck["cut15"] >= 0.10: raise SystemExit("HQ T-026, 1: the berm or the cut is over the limit: stop, send the plan")
    b, c, meta = build(gr, W, bw, holes, hills, ft, rl)
    nair = surface(b, c, gr, rl, bw, ft)
    from connect import connect
    connect(b)
    bad = [k for k in b.v if not in_place(k[0], k[2])]
    if bad: raise SystemExit("blocks outside the place: %s" % bad[:5])
    pad = [k for k in b.v if gr["allow"][ix(gr, k[0], k[2])]]
    if pad: raise SystemExit("blocks on the pad / approach of bonfire 5: %s" % pad[:5])
    ncol = write_terrain(gr, rl, b, W)
    n = b.write_placements(os.path.join(OUT, "fens.txt"))
    ruin_templates()
    gaps = []
    for g in ft["gaps"]:
        a, b2, nv = ft["deck"][g["k"]]
        gaps.append(dict(k=g["k"], dark=g["dark"], x=a[0], z=a[1], cells=[list(ft["deck"][kk][q]) for kk in (g["k"] - 1, g["k"], g["k"] + 1) for q in (0, 1)]))
    dark = next(g for g in gaps if g["dark"])
    amb = next(r_ for r_ in meta["ruins"] if r_["role"] == "ambush")
    out = dict(W=W, floor=W + 4, hut=meta["hut"], hut_centre=[HCX, HCZ], platform=[HX1, HZ1, HX2, HZ2], pools=[dict(p, y=W) for p in ft["pools"]], gaps=gaps, dark=dark,
               dark_posts=meta["dark_posts"], boats=meta["boats_out"] + meta["hut"]["boats_hut"], pier_out=meta["pier_out"], ruins=meta["ruins"],
               lanterns=meta["lanterns"], main=ft["main"], board=ft["board"], deck=[[list(a), list(b2)] for a, b2, _ in ft["deck"]], climb=[[x, y, z, h] for (x, y, z, h) in meta["climb"]],
               cpath=rl["cpath"], cprof=rl["prof"], hearth=list(HEARTH5), chest=amb["chest"], chest_facing=amb["chest_facing"], terrain_columns=ncol, blocks=n, air=nair, trees=meta["trees"], checks=ck)
    import fens_dp
    fens_dp.run(sys.modules[__name__], out)
    data_files(meta, W)
    json.dump(out, open(os.path.join(OUT, "fens.json"), "w"), ensure_ascii=False)
    print(f"fens: terrain {ncol} columns, {n} blocks (air {nair}), trees {meta['trees']}, ruins {len(meta['ruins'])}, lanterns {len(meta['lanterns'])}, W {W}")

if __name__ == "__main__" and sys.argv[1:2] == ["plan"]:
    plan_main()
elif __name__ == "__main__":
    main()
