"""T-028: the layout of the approaches to the Enchanted Castle (Р1, place `castle`: circle r 100 round (450, 0) + 16 of seam): the gorge
with the lake cut into the plateau between bonfire 7 and the castle rock, the rock (the bridgehead with bonfire 8, the north-east peak, the
castle table), the dry moats that keep its edge sheer, the rift with the bridge, the descent from bonfire 7, the causeway, the pier, the
colossi, the stair in the rock. Only planning here (numpy grids and cell lists); the blocks are tools/build/castle_build.py, the run is
tools/build/r1_castle.py.

Relief (HQ T-028, 1): W = 115 (the top of the rock at bonfire 8, 163, minus 48); P = the 50th percentile of the ground of the table spot
(x 405..485, z 30..95) before the place. Every column is decided from the ground before the place (base.bin + the R1 frame's terrain.bin),
so a re-run gives the same place."""
import os, struct
import numpy as np
from scanio import Scan, NONE

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "server/build/r1")
CX, CZ, R_PLACE, MARGIN = 450, 0, 100, 16
BOX = (324, -126, 576, 126)                # the grids: the place with its seam + 10 (checked by `r1_check.py places castle`)
W = 115                                    # the lake (water top block); "W+1" ground = a block at 116, feet at 117
HEARTH7, PAD7, PAD7_Y = (356, 168, -40), (350, -45, 363, -32), 167      # T-022 pads: x-6..x+7, z-5..z+8; never written here
HEARTH8, PAD8, PAD8_Y = (440, 163, -10), (434, -15, 447, -2), 162
FACE_X = 432                               # the west face of the bridgehead: rock from x 432 east
PRED, PRED_Y = (432, -50, 469, 4), 162     # the bridgehead (top of the stair, bonfire 8, the head of the bridge)
TABLE_SPOT, TABLE_R = (405, 30, 485, 95), 94   # the castle table: the spot clipped to r 94 (the moat and the biome stay inside the circle)
PEAK_MIN, PEAK_R = 170, 96                 # the north-east peak: natural ground >= 170 joined to the bridgehead, within r 96
RIFT = (405, 5, 485, 29)                   # between the bridgehead (z <= 4) and the table (z >= 30)
LAKE = [(381, -56, 431, -34), (374, -33, 431, 4)]   # water (minus the colossi and the pier, which stand in it)
MOAT_D = 5                                 # cells within MOAT_D of the rock are >= 6 under it; further out 1:1 up to the ground
SHEER = 6
# the living rock (HQ review T-028, 1): the contour of the rock grows outward by noise (never inward: the table stays >= its spot), the
# faces get overhangs (cornices and hanging bulges, wider at the top than below, none reachable from below)
GROW_MAX, GROW_RIFT = 5, 3                 # outward growth of the rock contour (blocks); into the rift at most 3 (the rift stays >= 18 wide)
ROCK_RMAX = 95                             # the grown rock stays within r 95..98 (a wobbly circle: the old table edge r 94 +- 2; further out the
                                           # moat would not reach the ground inside the place)
FACE_ZONE = (300, -58, FACE_X + 1, 8)      # the west face over the lake (the colossi, the pier, the stair): no growth, no overhangs
HANG_GAP = 3                               # the lowest block of an overhang is >= 3 over the ground under it (unreachable from below)
# the pier, the colossi, the channel, the knock zone, the causeway, the sword islet, the sandy way out
PIER = (420, -38, 431, -30)                # 12 (x) x 9 (z), deck block at W+1
COL_N = (420, -51, 431, -41)               # footprints of the colossi (plinth), backs to the face, facing west (the lake)
COL_S = (420, -26, 431, -16)
CHANNEL = (400, -39, 419, -28)             # 12 wide, from the open lake to the pier
TRIGGER = [(412, W - 6, -39, 431, W + 7, -28), (432, 116, -38, 446, 133, -30)]   # channel + pier; the first flight up to the first turn
KNOCK = (393, -41, 408, -28)               # 16 x 14 clean water, floor <= W-5
KNOCK_PTS = [(397.5, -36.5), (404.5, -32.5), (400.5, -38.5)]   # landing points (two players: different ones)
SWORD_ISLET = (414, -48, 419, -43)
SAND = (394, -50, 405, -42)                # the ramp of sand and sandstone slabs from the knock zone up to the causeway (+0.5 per cell, turning west at its top)
CAUSEWAY = [(381, -53, 413, -51), (411, -50, 413, -41), (411, -40, 419, -38)]   # W-E along the north shore, south, east to the pier
# the descent from bonfire 7: lanes W-E, U-turns 4 to the north; landing W x 364..366, flight x 367..376, landing E x 377..379
DESC_FLIGHTS = [11, 10, 10, 10, 10]        # 167 -> 116 (each flight n lower; the first one eats a cell of the top landing)
DESC_X = (364, 366, 367, 376, 377, 379)
DESC_Z0 = -36                              # centre of the first lane; lane k centre DESC_Z0 - 4k
# the stair in the rock (a cleft east of the pier): lane A z -37..-35 (F1 tunnel, F3 open), lane B z -33..-31 (F2 tunnel, F4 open)
LANE_A, LANE_B = (-37, -35), (-33, -31)
STAIR_FLIGHTS = [12, 12, 12, 10]           # 116 (deck) -> 128 -> 140 (the rest platform) -> 152 -> 162 (the top)
REST = (425, -37, 431, -31)                # the rest platform 7 x 7 (block level 140), over the pier
NICHES = [(432, LANE_A[0], 434, LANE_A[1]), (432, LANE_B[0], 434, LANE_B[1])]   # 3 x 3 x 4, floor 149, air 150..153
NICHE_Y = 149
BRIDGE_X = (449, 453)                      # the bridge (deck block 162) z 5..29; the barbican on the table's north edge
BARBICAN = (444, 30, 458, 39)

def wob(t, salt, amp, per=(23.0, 11.0, 6.0)):
    """smooth 1-D wobble in [-amp, amp] (sum of three sines with hashed phases): irregular edges of the lake and of the rock"""
    from lib import h as hsh
    v = sum(np.sin(2 * np.pi * (t / p + hsh(int(p), salt, 7, 2899))) * (0.5 ** k) for k, p in enumerate(per))
    return np.round(amp * v / 1.75).astype(int)
def jhash(x, y, z, salt):
    """tools/seedmap/Terrain.java hash() (the same bits: 64-bit wrap-around, logical shifts)"""
    M = (1 << 64) - 1
    n = (x * 374761393 + y * 1442695040888963407 + z * 668265263 + salt * 2654435761) & M
    n = ((n ^ (n >> 13)) * 1274126177) & M; n ^= n >> 16
    return (n & 0xffffff) / 0x1000000
def vnoise2(X, Z, cell, salt):
    """2-D value noise over arrays (smoothstep between lattice points `cell` apart), as Terrain.java vnoise(x / cell, z / cell)"""
    fx, fz = X / cell, Z / cell; xi, zi = np.floor(fx).astype(np.int64), np.floor(fz).astype(np.int64)
    tx, tz = fx - xi, fz - zi; tx = tx * tx * (3 - 2 * tx); tz = tz * tz * (3 - 2 * tz)
    hv = np.vectorize(lambda a, c: jhash(int(a), 0, int(c), salt))
    a, b, c, d = hv(xi, zi), hv(xi + 1, zi), hv(xi, zi + 1), hv(xi + 1, zi + 1)
    return (a * (1 - tx) + b * tx) * (1 - tz) + (c * (1 - tx) + d * tx) * tz
def rank(a):
    """values -> ranks 0..1 (uniform shares)"""
    o = np.argsort(a, axis=None, kind="stable"); r = np.empty(a.size); r[o] = np.arange(a.size) / max(1, a.size - 1); return r.reshape(a.shape)
def chamfer(src, blocked=None):
    """distance (3-4 chamfer / 3, about euclidean) from the cells of `src` and the index of the nearest source cell (flat), over the grid;
    `blocked` cells are never entered"""
    n0, n1 = src.shape; INF = 10 ** 9
    d = np.where(src, 0, INF).astype(np.int64); near = np.where(src, np.arange(src.size).reshape(src.shape), -1)
    blk = np.zeros(src.shape, bool) if blocked is None else blocked
    fw = ((-1, -1, 4), (-1, 0, 3), (-1, 1, 4), (0, -1, 3)); bw = ((1, 1, 4), (1, 0, 3), (1, -1, 4), (0, 1, 3))
    for it in range(2):
        for rng_i, rng_j, nb in ((range(n0), range(n1), fw), (range(n0 - 1, -1, -1), range(n1 - 1, -1, -1), bw)):
            for i in rng_i:
                for j in rng_j:
                    if blk[i, j] and not src[i, j]: continue
                    for a, c, w in nb:
                        p, r = i + a, j + c
                        if 0 <= p < n0 and 0 <= r < n1 and d[p, r] + w < d[i, j]: d[i, j] = d[p, r] + w; near[i, j] = near[p, r]
    return d / 3.0, near
def rect(r, X, Z): return (X >= r[0]) & (X <= r[2]) & (Z >= r[1]) & (Z <= r[3])
def in_place(x, z): return np.hypot(x - CX, z - CZ) <= R_PLACE + MARGIN
def ix(gr, x, z): return z - gr["z1"], x - gr["x1"]

def grids():
    x1, z1, x2, z2 = BOX; X, Z = np.meshgrid(np.arange(x1, x2 + 1), np.arange(z1, z2 + 1))
    def grid(s, a): return a[z1 - s.z0:z2 - s.z0 + 1, x1 - s.x0:x2 - s.x0 + 1].astype(np.int32)
    al = np.load(os.path.join(OUT, "allow.npz")); A = al["allow"]; ax0, az0 = int(al["x0"]), int(al["z0"])
    allow = A[z1 - az0:z2 - az0 + 1, x1 - ax0:x2 - ax0 + 1].copy()
    base = Scan(os.path.join(OUT, "base.bin")); nat = grid(base, base.ground)
    d = open(os.path.join(OUT, "terrain.bin"), "rb").read(); assert d[:4] == b"LETA"
    tx0, tz0, tw, th = struct.unpack("<4i", d[4:20]); TH = np.frombuffer(d, "<i2", tw * th, 20).reshape(th, tw).astype(np.int32)
    fr = TH[z1 - tz0:z2 - tz0 + 1, x1 - tx0:x2 - tx0 + 1]
    before = np.where(fr != NONE, fr, nat)
    trees = grid(base, base.top) - nat
    pads = rect(PAD7, X, Z) | rect(PAD8, X, Z)
    gr = dict(X=X, Z=Z, x1=x1, z1=z1, before=before, nat=nat, allow=allow, pad=pads, place=in_place(X, Z), trees=trees,
              bwater=grid(base, base.water))
    pre_path = os.path.join(OUT, "castle_pre.bin")
    if os.path.exists(pre_path):
        pre = Scan(pre_path); gr.update(live=grid(pre, pre.ground), top=grid(pre, pre.top), lwater=grid(pre, pre.water))
    return gr

def table_level(gr):
    return int(round(np.percentile(gr["before"][rect(TABLE_SPOT, gr["X"], gr["Z"])], 50)))

def minfilter(a, n=1):
    for _ in range(n):
        p = np.pad(a, 1, constant_values=10 ** 6); m = a.copy()
        for dz in (0, 1, 2):
            for dx in (0, 1, 2): m = np.minimum(m, p[dz:dz + a.shape[0], dx:dx + a.shape[1]])
        a = m
    return a
def flood(mask, seeds):
    from collections import deque
    lab = np.zeros(mask.shape, bool); q = deque()
    for s in seeds:
        if mask[s]: lab[s] = True; q.append(s)
    while q:
        i, j = q.popleft()
        for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p, r = i + a, j + c
            if 0 <= p < mask.shape[0] and 0 <= r < mask.shape[1] and mask[p, r] and not lab[p, r]: lab[p, r] = True; q.append((p, r))
    return lab

# ---------------------------------------------------------------- walks: the descent and the stair (cells with block levels)
def descent():
    """cells {(x, z): (block level, 'L'|'S', facing up)}: landings are full blocks at the level, stairs are stair blocks at the level
    (the low side towards the lower neighbour); a landing has the level of the last stair before it (no full-block step)."""
    xw1, xw2, xf1, xf2, xe1, xe2 = DESC_X
    y = PAD7_Y; cells = {}; order = []
    def put(x, z, lv, k, f):
        for dz in (-1, 0, 1): cells[(x, z + dz)] = (lv, k, f)
    zc = DESC_Z0
    for x in range(xw1, xw2 + 1): put(x, zc, y, "L", None); order.append((x, zc, y))
    for k, n in enumerate(DESC_FLIGHTS):
        east = k % 2 == 0
        xs = list(range(xf2 - n + 1, xf2 + 1)) if east else list(range(xf2, xf2 - n, -1))
        if not east and n > xf2 - xf1 + 1: raise SystemExit("descent flight too long")
        for x in xs:                         # the first stair at the landing's level (its high side flush with the landing), then 1 lower each;
            put(x, zc, y, "S", "west" if east else "east"); order.append((x, zc, y)); y -= 1     # the next landing 1 under the last stair
        # the turn landing (3 x 7: this lane, the wall, the next lane) or the end landing
        lx = range(xe1, xe2 + 1) if east else range(xw1, xw2 + 1)
        if east and xs[-1] < xf2:                   # a short flight: flat to the landing
            for x in range(xs[-1] + 1, xf2 + 1): put(x, zc, y, "L", None)
        if not east and xs[-1] > xw2 + 1:
            for x in range(xw2 + 1, xs[-1]): put(x, zc, y, "L", None)
        last = k == len(DESC_FLIGHTS) - 1
        for x in lx:
            for dz in ((-1, 0, 1) if last else (-5, -4, -3, -2, -1, 0, 1)): cells[(x, zc + dz)] = (y, "L", None)
            order.append((x, zc, y))
        zc -= 4
    return cells, order, y

def stair():
    """the cleft stair: F1 lane A east from the pier (tunnel), landing E1, F2 lane B west (tunnel) to the rest platform, F3 lane A east
    (open, over F1), landing E2, F4 lane B west (open, over F2) to the top landing at x 433 (exit south over the cleft wall)."""
    y = W + 1; cells = []           # (x, z1, z2, level, kind, facing up)
    A, Bl = LANE_A, LANE_B
    for k, n in enumerate(STAIR_FLIGHTS):
        east = k % 2 == 0; lane = A if east else Bl
        xs = list(range(FACE_X, FACE_X + n)) if east else list(range(FACE_X + 11, FACE_X + 11 - n, -1))
        for x in xs: y += 1; cells.append((x, lane[0], lane[1], y, "S", "east" if east else "west"))
        if k in (0, 2):
            for x in range(FACE_X + 12, FACE_X + 15): cells.append((x, A[0], Bl[1], y, "L", None))
        elif k == 1:
            for x in range(REST[0], REST[2] + 1): cells.append((x, REST[1], REST[3], y, "L", None))
        else:
            cells.append((FACE_X + 1, Bl[0], Bl[1], y, "L", None))
    return cells, y

# ---------------------------------------------------------------- the relief
def relief(gr):
    X, Z = gr["X"], gr["Z"]; bf = gr["before"].copy(); place = gr["place"]; pad = gr["pad"]
    P = table_level(gr)
    T = bf.copy()
    lake = np.zeros(X.shape, bool)
    for r in LAKE: lake |= rect(r, X, Z)
    # irregular shores (west, north and south) away from the causeway, the descent and the rock face
    lw = (X < LAKE[1][0] + wob(Z, 1, 3)) & (Z > LAKE[1][1]) | (Z > LAKE[1][3] + wob(X, 2, 2)) & (X < FACE_X - 2)
    lake &= ~lw
    lake |= rect((LAKE[1][0] - 3, LAKE[1][1] + 6, LAKE[1][0], LAKE[1][3] - 4), X, Z) & (X >= LAKE[1][0] + wob(Z, 1, 3))
    pred = rect(PRED, X, Z) & (X <= PRED[2] + wob(Z, 3, 3)) & ((Z <= PRED[3] + wob(X, 4, 2)) | (X >= BRIDGE_X[0] - 3) & (X <= BRIDGE_X[1] + 3) & (Z <= PRED[3]))
    pred |= rect((PRED[2], PRED[1], PRED[2] + 3, PRED[3]), X, Z) & (X <= PRED[2] + wob(Z, 3, 3))
    tr = TABLE_R + wob(np.degrees(np.arctan2(Z - CZ, X - CX)), 5, 2, (40.0, 17.0, 9.0))
    table = rect((TABLE_SPOT[0] - 3, TABLE_SPOT[1] - 2, TABLE_SPOT[2], TABLE_SPOT[3]), X, Z) & (np.hypot(X - CX, Z - CZ) <= tr)
    table &= (X >= TABLE_SPOT[0] + wob(Z, 6, 3)) & ((Z >= TABLE_SPOT[1] + wob(X, 7, 2)) | (X >= BARBICAN[0]) & (X <= BARBICAN[2]) & (Z >= TABLE_SPOT[1]))
    rift = rect((RIFT[0], RIFT[1] - 2, RIFT[2], RIFT[3] + 2), X, Z) & ~pred & ~table & ~lake
    pk = (bf >= PEAK_MIN) & (np.hypot(X - CX, Z - CZ) <= PEAK_R) & (Z < -40) & (X >= FACE_X) & ~lake
    seeds = [ix(gr, x, PRED[1] - 1) for x in range(PRED[0], PRED[2] + 1)]
    peak = flood(pk, seeds)
    T[pred] = PRED_Y; T[table] = P
    # the living rock: the contour grows outward by a noise (patches about 6 across + ribs about 2 across: the columnar faces), each grown
    # cell takes the top of the nearest rock cell; never into the lake, the pads, the west face over the lake, the bridge, the barbican,
    # out of r 99; into the rift at most GROW_RIFT
    base = pred | table | peak
    rr = np.hypot(X - CX, Z - CZ)
    prot = lake | pad | (rr > ROCK_RMAX + 3 * rank(vnoise2(X, Z, 2.5, 2897))) | rect(FACE_ZONE, X, Z) | rect((BRIDGE_X[0] - 3, RIFT[1] - 4, BRIDGE_X[1] + 3, RIFT[3] + 4), X, Z) \
        | rect((BARBICAN[0] - 2, BARBICAN[1] - 4, BARBICAN[2] + 2, BARBICAN[3]), X, Z)
    g = np.clip(np.round(3.0 * rank(vnoise2(X, Z, 6.0, 2890)) + 3.6 * rank(vnoise2(X, Z, 1.6, 2891)) - 0.6), 0, GROW_MAX)
    inrift = rect((RIFT[0], RIFT[1] - 2, RIFT[2], RIFT[3] + 2), X, Z); g = np.where(inrift, np.minimum(g, GROW_RIFT), g)
    dist, near = chamfer(base, prot)
    grown = ~base & ~prot & (dist <= g) & (dist > 0)
    src = near.ravel()[grown.ravel()]; T[grown] = T.ravel()[src]
    for msk in (pred, table, peak): msk |= grown & msk.ravel()[near.ravel()].reshape(X.shape)
    # no straight run of the contour longer than 8: in the middle of a longer one a bump out (where allowed) or a grown cell taken back
    for it in range(8):
        rock = pred | table | peak; runs = straight_list(gr, rock, 8)
        if not runs: break
        for (cells, (a, c)) in runs:
            for (i, j) in cells[3::5][:max(1, len(cells) // 5)]:
                p_, r_ = i + a, j + c
                if 0 <= p_ < X.shape[0] and 0 <= r_ < X.shape[1] and not prot[p_, r_] and not rock[p_, r_]:
                    for msk in (pred, table, peak):
                        if msk[i, j]: msk[p_, r_] = True
                    T[p_, r_] = T[i, j]; grown[p_, r_] = True
                elif grown[i, j]:
                    for msk in (pred, table, peak): msk[i, j] = False
                    grown[i, j] = False; T[i, j] = bf[i, j]
    rock = pred | table | peak
    rift &= ~rock                                  # the rift was cut before the growth
    # the lake floor: 4 deep, the channel and the knock zone 5, by the causeway 2..3, by the rock face 6
    Wt = np.full(X.shape, NONE, np.int32)
    fl = np.full(X.shape, W - 4)
    knock = rect(KNOCK, X, Z); chan = rect(CHANNEL, X, Z)
    cw = np.zeros(X.shape, bool)
    for r in CAUSEWAY: cw |= rect(r, X, Z)
    near_cw = ~minfilter(np.where(cw, 0, 1), 2).astype(bool)
    from lib import h as hsh
    for i, j in zip(*np.nonzero(lake)):
        x, z = j + gr["x1"], i + gr["z1"]
        v = W - 4 - (1 if hsh(x, 0, z, 2801) < 0.35 else 0)
        if near_cw[i, j]: v = W - 2 - (1 if hsh(x, 1, z, 2802) < 0.5 else 0)
        if x >= FACE_X - 3: v = W - 6
        if knock[i, j] or chan[i, j]: v = W - 5
        fl[i, j] = v
    T[lake] = fl[lake]; Wt[lake] = W
    # the sandy way out: half a block per cell from W-4 (z -42) up to the causeway (W+1 at z -51)
    sand = rect(SAND, X, Z)
    halves = {}
    for i, j in zip(*np.nonzero(sand)):
        x, z = j + gr["x1"], i + gr["z1"]
        halves[(x, z)] = min(2 * (W + 2), 2 * (W - 4) + 1 + (-42 - z) + max(0, 397 - x))   # surface in half blocks: 111.5 at z -42
        # (the floor of the knock zone is 111) .. 115.5 at z -50, then west 116 .. 117 (x 394): the causeway (117) by +0.5 steps
    # the rift: a dry sill W+2 along the lake, down half a block per cell to W-7, the east end up to the ground
    for i, j in zip(*np.nonzero(rift)):
        x, z = j + gr["x1"], i + gr["z1"]
        if x < FACE_X and z <= 8: v = W + 2
        else:
            v = max(W - 7, W + 2 - (x - 405) // 2 if x < 445 else W - 7)
            if x > 455: v = min(max(v, W - 7 + (x - 455) // 2), int(bf[i, j]))
            if x < FACE_X: v = max(v, W + 2 - max(0, z - 8) // 2)
        T[i, j] = min(int(T[i, j]), v)
    # the sill: no rift cell next to the lake lower than W+2 (the wobbly edge of the bridgehead brings the deep rift to the water)
    nl = np.zeros(X.shape, bool)
    for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): nl |= np.roll(np.roll(lake, dz, 0), dx, 1)
    T[rift & nl] = np.maximum(T[rift & nl], W + 2)
    # gorge walls round the lake (and the rift's west mouth): steep, rough, from W+1 at the shore up to the ground
    wet = lake.copy()
    dist = np.full(X.shape, 999); cur = wet.copy(); dist[wet] = 0
    for k in range(1, 26):
        grow = ~minfilter(np.where(cur, 0, 1)).astype(bool) & ~cur
        dist[grow] = k; cur |= grow
    gw = (dist >= 1) & (dist < 999) & ~rock & ~rift & ~pad & place
    for i, j in zip(*np.nonzero(gw)):
        x, z = j + gr["x1"], i + gr["z1"]
        cap = W + 1 + 5 * (int(dist[i, j]) - 1) + int(hsh(x, 3, z, 2803) * 3)
        T[i, j] = min(int(T[i, j]), cap)
    # overhangs (HQ review T-028, 1): cornices and hanging bulges round the rock, wider at the top than below. A cell next to the rock
    # (outside it, not in the lake or the protected zones) carries blocks only in the top k of its rock's height; the lowest is >= HANG_GAP
    # over the ground under it, so no overhang is reachable from below. Ring 1 (next to the rock): k 2..10 by noise; ring 2 (next to a
    # ring-1 cell with k >= 4): the top 1..2 blocks (the corbel widens upward). The overhang cells count as rock for the moat and the
    # checks (their top is the rock top: no ledge for the sheer-edge test); the terrain under them is written at `floor`.
    hang = {}
    hprot = prot | lake | (Wt != NONE) | rift & rect((BRIDGE_X[0] - 4, RIFT[1] - 4, BRIDGE_X[1] + 4, RIFT[3] + 4), X, Z)
    u1 = rank(vnoise2(X, Z, 4.0, 2892)); u2 = rank(vnoise2(X, Z, 2.2, 2893)); u3 = rank(vnoise2(X, Z, 3.0, 2894))
    n4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for ring in (1, 2):
        cur = rock.copy()
        for (x, z) in hang: cur[ix(gr, x, z)] = True
        for i, j in zip(*np.nonzero(~cur & ~hprot & place)):
            nbs = [(i + a, j + c) for a, c in n4 if 0 <= i + a < X.shape[0] and 0 <= j + c < X.shape[1]]
            x, z = int(X[i, j]), int(Z[i, j])
            if ring == 1:
                srcs = [q for q in nbs if rock[q]]
                if not srcs or u1[i, j] < 0.42: continue
                top = min(int(T[q]) for q in srcs)
                kmax = min(10, top - min(int(T[i, j]), top - SHEER) - HANG_GAP + 1)
                k = int(round(2 + u2[i, j] * (kmax - 2))) if kmax >= 2 else 0
            else:
                srcs = [q for q in nbs if (int(X[q]), int(Z[q])) in hang and hang[(int(X[q]), int(Z[q]))][1] >= 4 and not rock[q]]
                if not srcs or u3[i, j] < 0.5 or any(rock[q] for q in nbs): continue
                top = min(hang[(int(X[q]), int(Z[q]))][0] for q in srcs); k = 1 + int(u2[i, j] > 0.6)
            if k < 1: continue
            fl = min(int(T[i, j]), top - SHEER)
            if top - k + 1 < fl + 1 + HANG_GAP: continue
            hang[(x, z)] = (top, k, fl, ring)
    for (x, z), (top, k, fl, ring) in hang.items():
        i, j = ix(gr, x, z); T[i, j] = top; rock[i, j] = True
    # the moat: within MOAT_D of the rock >= 6 under the nearest rock cells, then 1:1 up (only in the place, never the pads)
    # cap = min over the rock cells r of (T_r - 6 + max(0, Chebyshev distance - MOAT_D)): flat for MOAT_D cells, then a 1:1 cone
    C = np.where(rock, T - SHEER, 10 ** 6)
    for k in range(MOAT_D): C = np.minimum(C, minfilter(C))
    for k in range(70): C = np.minimum(C, minfilter(C) + 1)
    sel = ~rock & place & ~pad & ~lake & (T > C)
    moat = sel & (bf > C)
    T[sel] = C[sel]
    # the descent from bonfire 7 (walk + the ring of walls / parapets round it)
    dcells, dorder, dend = descent()
    walk = {}
    for (x, z), (lv, k, f) in dcells.items():
        walk[(x, z)] = (lv, k, f); T[ix(gr, x, z)] = lv if k == "L" else lv - 1
    ring = {}
    for (x, z), (lv, k, f) in walk.items():
        for a in (-1, 0, 1):
            for c in (-1, 0, 1):
                q = (x + a, z + c)
                if q in walk: continue
                if PAD7[0] <= q[0] <= PAD7[2] and PAD7[1] <= q[1] <= PAD7[3]: continue
                ring.setdefault(q, []).append(lv)
    rings = {}
    for q, ys in ring.items():
        i, j = ix(gr, *q); top = max(ys); cur_t = int(T[i, j])
        if cur_t >= top + 1 and not lake[i, j]: rings[q] = ("wall", top)
        else: T[i, j] = top; rings[q] = ("parapet", top)
        if lake[i, j]: lake[i, j] = False; Wt[i, j] = NONE
    # the causeway end of the descent: no parapet across it
    for z in range(DESC_Z0 - 4 * (len(DESC_FLIGHTS) - 1) - 1, DESC_Z0 - 4 * (len(DESC_FLIGHTS) - 1) + 2):
        q = (DESC_X[5] + 1, z)
        if q in rings: del rings[q]
        T[ix(gr, *q)] = W + 1
    Tw = T.copy()                                  # the ground the terrain writes (under an overhang: its floor)
    for (x, z), (top, k, fl, ring) in hang.items(): Tw[ix(gr, x, z)] = fl
    return dict(T=T, Tw=Tw, Wt=Wt, P=P, lake=lake, pred=pred, table=table, peak=peak, rock=rock, rift=rift, moat=moat, sand=halves,
                knock=knock, chan=chan, walk=walk, rings=rings, desc_order=dorder, desc_end=dend, cw=cw, hang=hang, grow=grown, base=base)

def checks(gr, rl):
    """HQ T-028, 1: the stop conditions and the numbers of the plan"""
    T, bf, rock = rl["T"], gr["before"], rl["rock"]; X, Z = gr["X"], gr["Z"]
    out = {}
    fill = np.where(rock, T - bf, 0); out["max_fill_rock"] = int(fill.max())
    out["max_cut_rock"] = int(np.where(rock, bf - T, 0).max())
    i, j = np.unravel_index(np.argmax(fill), fill.shape); out["max_fill_at"] = (int(j + gr["x1"]), int(i + gr["z1"]))
    # the sheer edge: every rock cell next to a non-rock cell is >= 6 over it (the stair's mouth and the pier excepted)
    edge = []; low = []
    for i, j in zip(*np.nonzero(rock)):
        for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p, r = i + a, j + c
            if rock[p, r]: continue
            o = int(T[p, r]) if rl["Wt"][p, r] == NONE else max(int(T[p, r]), int(rl["Wt"][p, r]))
            hgt = int(T[i, j]) - o; edge.append(hgt)
            if hgt < SHEER: low.append((int(j + gr["x1"]), int(i + gr["z1"]), hgt))
    out["edge_min"], out["edge_cells"], out["edge_low"] = min(edge), len(edge), low[:12]
    out["moat_out_of_place"] = int((rl["moat"] & ~gr["place"]).sum())
    rr = np.hypot(X - CX, Z - CZ); out["rock_max_r"] = float(rr[rock].max())
    # how much the moat leaves at the edge of the place (the outer wall of the moat where the 1:1 slope did not reach the ground)
    ring = (rr > R_PLACE + MARGIN - 1.5) & (rr <= R_PLACE + MARGIN)
    out["moat_outer_step"] = int(np.where(ring & rl["moat"], bf - T, 0).max())
    out["lake_cells"] = int(rl["lake"].sum())
    kn = rl["knock"]; out["knock_min_depth"] = int((W - T[kn]).min()); out["knock_cells"] = int(kn.sum())
    out["desc_cells"] = len(rl["desc_order"]); out["desc_end"] = rl["desc_end"]
    sc, top = stair(); out["stair_top"] = top; out["stair_cells"] = sum(c[2] - c[1] + 1 for c in sc)
    out["P"] = rl["P"]; out["W"] = W
    out["straight_max"], out["straight_at"] = straight_runs(gr, rl)
    tb = rl["table"]; xs, zs = X[tb], Z[tb]; out["table_cells"] = int(tb.sum()); out["table_bbox"] = [int(xs.min()), int(zs.min()), int(xs.max()), int(zs.max())]
    out["grown_cells"] = int(rl["grow"].sum()); out["hang_cells"] = len(rl["hang"]); out["hang_ring2"] = sum(1 for v in rl["hang"].values() if v[3] == 2)
    out["hang_min_gap"] = min((v[0] - v[1] + 1) - (v[2] + 1) for v in rl["hang"].values()) if rl["hang"] else None
    stop = []
    if out["knock_min_depth"] < 4 or out["knock_cells"] != 14 * 16: stop.append("knock zone")
    if top != PRED_Y: stop.append("stair does not reach the bridgehead (%d)" % top)
    if out["max_fill_rock"] > 40: stop.append("fill %d > 40" % out["max_fill_rock"])
    if out["moat_out_of_place"]: stop.append("moat out of the place")
    if out["desc_cells"] > 250: stop.append("descent %d > 250" % out["desc_cells"])
    if out["straight_max"] > 8: stop.append("a straight run of the rock contour %d > 8 at %s" % (out["straight_max"], out["straight_at"]))
    if out["hang_min_gap"] is not None and out["hang_min_gap"] < HANG_GAP: stop.append("an overhang %d over the ground" % out["hang_min_gap"])
    out["stop"] = stop
    return out

def straight_list(gr, rock, limit):
    """the straight runs of the contour longer than `limit`: [(cells [(i, j)...], facing (a, c))] (same zones skipped as straight_runs)"""
    X, Z = gr["X"], gr["Z"]
    skip = rect(FACE_ZONE, X, Z) | rect((BRIDGE_X[0] - 1, RIFT[1] - 2, BRIDGE_X[1] + 1, RIFT[3] + 2), X, Z) | gr["pad"]
    out = []
    for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        e = rock & ~np.roll(np.roll(rock, -a, 0), -c, 1) & ~skip
        n0, n1 = e.shape
        lines = [[(i, j) for j in range(n1)] for i in range(n0)] if a else [[(i, j) for i in range(n0)] for j in range(n1)]
        for ln in lines:
            run = []
            for q in ln + [None]:
                if q is not None and e[q]: run.append(q); continue
                if len(run) > limit: out.append((run, (a, c)))
                run = []
    return out

def straight_runs(gr, rl):
    """the longest straight run of the contour of the rock seen from above (overhangs included: the top outline), outside the west face
    over the lake (the colossi, the pier, the stair) and the bridge: edge cells facing the same side in a row along one line"""
    rock = rl["rock"]; X, Z = gr["X"], gr["Z"]
    skip = rect(FACE_ZONE, X, Z) | rect((BRIDGE_X[0] - 1, RIFT[1] - 2, BRIDGE_X[1] + 1, RIFT[3] + 2), X, Z) | gr["pad"]
    best, at = 0, None
    for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nb = np.roll(np.roll(rock, -a, 0), -c, 1)
        e = rock & ~nb & ~skip
        line = e.T if a == 0 else e                 # runs go across the facing direction (east/west faces run along z)
        for k in range(line.shape[0]):
            run = 0
            for v in line[k]:
                run = run + 1 if v else 0
                if run > best: best = run; at = (a, c, k)
    if at:
        a, c, k = at; at = ("x" if a == 0 else "z", int(X[0, k]) if a == 0 else int(Z[k, 0]), "facing", (a, c))
    return best, at

# ---------------------------------------------------------------- the plan picture
def plan_png(gr, rl, path, extra=None, S=4):
    from PIL import Image, ImageDraw
    x1, z1, x2, z2 = 336, -112, 564, 112
    T, Wt = rl["T"], rl["Wt"]; w, h = (x2 - x1 + 1) * S, (z2 - z1 + 1) * S
    img = Image.new("RGB", (w, h + 110), (20, 20, 24)); d = ImageDraw.Draw(img)
    def px(x, z): return (x - x1) * S, (z - z1) * S
    def box(r, col, width=2):
        a = px(r[0], r[1]); b = px(r[2] + 1, r[3] + 1); d.rectangle([a[0], a[1], b[0] - 1, b[1] - 1], outline=col, width=width)
    for z in range(z1, z2 + 1):
        for x in range(x1, x2 + 1):
            i, j = ix(gr, x, z); v = int(T[i, j]); t = max(0.0, min(1.0, (v - 90) / 120))
            c = (int(50 + 170 * t), int(60 + 160 * t), int(45 + 110 * t))
            if Wt[i, j] != NONE: c = (35, 70, 150) if not rl["knock"][i, j] else (25, 110, 190)
            if rl["rock"][i, j]: c = (int(c[0] * 0.75 + 60), int(c[1] * 0.7), int(c[2] * 0.7))
            if (x, z) in rl["hang"]: c = (150, 70, 60) if rl["hang"][(x, z)][3] == 1 else (180, 100, 90)
            if rl["moat"][i, j]: c = (min(255, c[0] + 40), c[1], min(255, c[2] + 60))
            if rl["rift"][i, j]: c = (int(c[0] * 0.6), int(c[1] * 0.6), int(c[2] * 0.5))
            if gr["pad"][i, j]: c = (230, 140, 40)
            if (x, z) in rl["walk"]: c = (240, 230, 120) if rl["walk"][(x, z)][1] == "S" else (250, 250, 200)
            elif (x, z) in rl["rings"]: c = (120, 120, 120)
            if rl["cw"][i, j]: c = (150, 150, 150)
            if (x, z) in rl["sand"]: c = (225, 205, 140)
            a = px(x, z); d.rectangle([a[0], a[1], a[0] + S - 1, a[1] + S - 1], fill=c)
            if j + 1 < T.shape[1] and i + 1 < T.shape[0] and (T[i, j] // 10 != T[i, j + 1] // 10 or T[i, j] // 10 != T[i + 1, j] // 10):
                d.point(a, fill=(0, 0, 0))
    for c in stair()[0]:
        x, za, zb, y, k, f = c; a = px(x, za); b = px(x + 1, zb + 1)
        d.rectangle([a[0], a[1], b[0] - 1, b[1] - 1], fill=(255, 200, 80) if k == "S" else (255, 240, 170))
    for r in (COL_N, COL_S): box(r, (200, 200, 220), 3)
    box(PIER, (140, 90, 50), 3); box(KNOCK, (120, 220, 255), 2); box(SWORD_ISLET, (230, 230, 230), 2)
    for t in TRIGGER: box((t[0], t[2], t[3], t[5]), (255, 60, 60), 2)
    box(REST, (255, 120, 255), 2)
    for n in NICHES: box(n, (255, 0, 255), 2)
    box((BRIDGE_X[0], RIFT[1], BRIDGE_X[1], RIFT[3]), (200, 200, 200), 3); box(BARBICAN, (210, 210, 210), 3)
    for (kx, kz) in KNOCK_PTS: a = px(kx, kz); d.ellipse([a[0] - 4, a[1] - 4, a[0] + 4, a[1] + 4], outline=(255, 255, 255))
    for (hx, hy, hz) in (HEARTH7, HEARTH8): a = px(hx + 0.5, hz + 0.5); d.ellipse([a[0] - 6, a[1] - 6, a[0] + 6, a[1] + 6], fill=(255, 90, 0))
    for r, col in ((R_PLACE, (90, 220, 190)), (R_PLACE + MARGIN, (255, 70, 70))):
        a = px(CX - r, CZ - r); b = px(CX + r, CZ + r); d.ellipse([a[0], a[1], b[0], b[1]], outline=col, width=2)
    for x in range(x1 - x1 % 20 + 20, x2, 20): d.text((px(x, z1)[0] + 2, 2), str(x), fill=(255, 255, 0))
    for z in range(z1 - z1 % 20 + 20, z2, 20): d.text((2, px(x1, z)[1] + 2), str(z), fill=(255, 255, 0))
    def lab(x, z, t): d.text(px(x, z), t, fill=(255, 255, 255))
    lab(376, -12, "LAKE W=%d" % W); lab(440, 60, "TABLE P=%d" % rl["P"]); lab(470, -30, "BRIDGEHEAD 162"); lab(470, -70, "PEAK")
    lab(470, 14, "RIFT"); lab(405, -45, "SWORD"); lab(392, -26, "KNOCK"); lab(363, -60, "DESCENT"); lab(384, -56, "CAUSEWAY")
    for k, t in enumerate(extra or []): d.text((6, h + 6 + 16 * k), t, fill=(230, 230, 230))
    img.save(path)
