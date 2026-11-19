#!/usr/bin/env python3
"""T-025: the Garden of Silence (Р1) on its place `garden` of tools/build/r1_plots.txt (rect 200x200 round (330,-350) + 16).

  python3 tools/build/r1_garden.py   -> server/build/r1/garden_terrain.bin (tools/terrain.sh apply), garden.txt (tools/blockwriter.sh apply),
                                        garden.json (points for the tests and the walk bot), docs/reports/T-025/garden_plan.png,
                                        datapack function/garden/gen/* (tools/build/garden_dp.py), zones, the key source
Inputs: server/build/r1/base.bin (the ground before the R1 frame), terrain.bin (the frame), garden_pre.bin (scan of the place now),
        allow.npz (r1.py: the pad of bonfire 4 with its slopes and the approaches: never written).

Layout (card «Сад Безмолвия», HQ T-025, 1: the relief of seed 10845): the orangery (40x28, 18 high) on a dry pad south of the bay of
the lake (the "river" of the seed map: water y 62 from the centre to the north-east, it is not filled); a circle r 60 round the
orangery sculpted into soft hills (base = median of the natural land in it, +-6, slopes <= 1:3), blended into the natural ground near
the water and at its rim; the rest of the place keeps its natural relief. Snow and the trees of the place go; pale oaks of our own
model (4 forms x 4 rotations): radial alleys converging on the orangery up to r 50, broken rows to r 72, wild forest further. The
gardener's house (9x7) by bonfire 4, one paved path from its door to the west door of the orangery (half blocks, no jumps).
6 living faces (creaking hearts in pale oak trunks), 12 carved faces (3x3 trunks, day/night/asleep by the datapack), 10 sculk sensors
under moss with bones and signs, eyeblossoms (their points go to the datapack). Re-run: the same garden, 0 columns changed."""
import heapq, json, math, os, struct, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import Scan, write_grid, NONE
from lib import B, Mix, h as hsh, slab

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "server/build/r1")
DP = os.path.join(ROOT, "datapack/data/last_ember")
PCX, PCZ, PW, PD, MARGIN = 330, -350, 200, 200, 16
CORE = (230, -450, 430, -250)                         # the place's core x1 z1 x2 z2
PLACE = (CORE[0] - MARGIN, CORE[1] - MARGIN, CORE[2] + MARGIN, CORE[3] + MARGIN)
def in_built(x, z):
    """the orangery and the house with their pads: their blocks are laid on purpose"""
    return (OX1 - 3 <= x <= OX2 + 3 and OZ1 - 3 <= z <= OZ2 + 3) or (HX1 - 2 <= x <= HX2 + 2 and HZ1 - 2 <= z <= HZ2 + 2)
def in_place(x, z):
    return np.hypot(np.maximum(np.abs(x - PCX) - PW / 2, 0), np.maximum(np.abs(z - PCZ) - PD / 2, 0)) <= MARGIN
def in_core(x, z): return (x >= CORE[0]) & (x <= CORE[2]) & (z >= CORE[1]) & (z <= CORE[3])
# the orangery (x 318..357, z -335..-308), its floor top FY; the trunk 4x4 of the great tree; the dry basin
OX1, OX2, OZ1, OZ2 = 318, 357, -335, -308
OCX, OCZ = (OX1 + OX2 + 1) / 2, (OZ1 + OZ2 + 1) / 2   # 338.0, -321.5 (block corner / middle)
FY = 91
WALL_H = 10; ROOF_H = 18
TRUNK = (336, -323, 339, -320)                         # x1 z1 x2 z2
BASIN = (329, -328, 346, -315)
PED = (343, -317)                                      # the pedestal of the key (in the basin, south-east of the trunk)
DOOR_W = (OX1, -323, -320)                             # west opening: x, z1..z2
DOOR_E = (OX2, -323, -320)
# the gardener's house (9x7) north of the pad of bonfire 4 (14 from the hearth); floor top FH = the pad; door in the south wall (to the
# pad), the stand behind the south window next to it (seen from the path that starts at the door)
HX1, HX2, HZ1, HZ2 = 238, 246, -275, -269
FH = 120
HDOOR = (242, HZ2)                                     # door blocks at y FH+1..FH+2
STAND = (244, -271)
WINDOW = (244, HZ2)
LECTERN = (240, -273)
HEARTH4 = (238, 121, -258)
S_FOREST, S_MOSS, S_FLAT, S_ROCK = 2, 6, 7, 10
R_STONE = 0

# ---------------------------------------------------------------- grids
def grids():
    x1, z1, x2, z2 = PLACE; X, Z = np.meshgrid(np.arange(x1, x2 + 1), np.arange(z1, z2 + 1))
    pre = Scan(os.path.join(OUT, "garden_pre.bin"))
    def grid(s, a): return a[z1 - s.z0:z2 - s.z0 + 1, x1 - s.x0:x2 - s.x0 + 1].astype(np.int32)
    al = np.load(os.path.join(OUT, "allow.npz")); A = al["allow"]; ax0, az0 = int(al["x0"]), int(al["z0"])
    allow = A[z1 - az0:z2 - az0 + 1, x1 - ax0:x2 - ax0 + 1].copy()
    base = Scan(os.path.join(OUT, "base.bin"))
    nat = grid(base, base.ground); bw = grid(base, base.water)
    d = open(os.path.join(OUT, "terrain.bin"), "rb").read(); assert d[:4] == b"LETA"
    tx0, tz0, tw, th = struct.unpack("<4i", d[4:20]); TH = np.frombuffer(d, "<i2", tw * th, 20).reshape(th, tw).astype(np.int32)
    fr = TH[z1 - tz0:z2 - tz0 + 1, x1 - tx0:x2 - tx0 + 1]
    before = np.where(fr != NONE, fr, nat)            # the ground before the garden: the same on every run
    water = np.where((bw != NONE) & (bw > nat), bw, NONE)
    return dict(X=X, Z=Z, x1=x1, z1=z1, before=before, live=grid(pre, pre.ground), top=grid(pre, pre.top), lwater=grid(pre, pre.water),
                allow=allow, water=water, place=in_place(X, Z), core=in_core(X, Z))
def ix(gr, x, z): return z - gr["z1"], x - gr["x1"]

def blur(a, r):
    """box blur (separable, 3 passes ~ gaussian) with edge padding"""
    out = a.astype(float)
    for _ in range(3):
        p = np.pad(out, ((0, 0), (r, r)), mode="edge"); c = np.cumsum(np.pad(p, ((0, 0), (1, 0))), axis=1); out = (c[:, 2 * r + 1:] - c[:, :-2 * r - 1]) / (2 * r + 1)
        p = np.pad(out, ((r, r), (0, 0)), mode="edge"); c = np.cumsum(np.pad(p, ((1, 0), (0, 0))), axis=0); out = (c[2 * r + 1:, :] - c[:-2 * r - 1, :]) / (2 * r + 1)
    return out
def cheb_dist(src, n):
    d = np.where(src, 0, 999)
    for _ in range(n):
        p = np.pad(d, 1, constant_values=999); m = d.copy()
        for dz in (0, 1, 2):
            for dx in (0, 1, 2): m = np.minimum(m, p[dz:dz + d.shape[0], dx:dx + d.shape[1]] + 1)
        d = m
    return d

# ---------------------------------------------------------------- relief
R_SCULPT = 60
def sculpt(gr):
    """the circle r 60 round the orangery: soft hills (base +- 6, slopes <= 1:3); near the water and at the rim back to the natural ground"""
    X, Z, nat = gr["X"], gr["Z"], gr["before"].astype(float)
    r = np.hypot(X + 0.5 - OCX, Z + 0.5 - OCZ); wet = gr["water"] != NONE
    land = (r <= R_SCULPT) & ~wet
    base = float(np.median(nat[land]))
    sm = blur(np.where(wet, base, nat), 9)                         # the lake does not pull the hills down
    hills = base + 6 * np.tanh((sm - base) / 6)                    # soft clip to +-6
    dw = cheb_dist(wet, 30)
    w = np.clip((R_SCULPT - r) / 14, 0, 1) * np.clip((dw - 6) / 14, 0, 1)   # 0 at the rim and within 6 of the water, full 14 further in
    w = w * w * (3 - 2 * w)
    T = np.where(gr["place"], nat * (1 - w) + hills * w, nat)
    return T, base, w
def astar(T, start, goal, block, x1, z1):
    """path search on the target ground: cost of steepness (a graded path likes <= 0.5 per block), blocked cells"""
    H, W_ = T.shape; best = {start: 0.0}; prev = {}; pq = [(0.0, start)]
    while pq:
        f, c = heapq.heappop(pq)
        if c == goal: break
        cx, cz = c; g0 = best[c]
        if f - math.hypot(cx - goal[0], cz - goal[1]) > g0 + 1e-6: continue
        h0 = T[cz - z1, cx - x1]
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, nz = cx + dx, cz + dz; i, j = nz - z1, nx - x1
            if not (0 <= i < H and 0 <= j < W_) or block[i, j]: continue
            st = 1.4142 if dx and dz else 1.0; dh = abs(T[i, j] - h0) / st
            g = g0 + st * (1.0 + 2.5 * dh + 40 * max(0.0, dh - 0.45) ** 2)
            if g < best.get((nx, nz), 1e18): best[(nx, nz)] = g; prev[(nx, nz)] = c; heapq.heappush(pq, (g + math.hypot(nx - goal[0], nz - goal[1]), (nx, nz)))
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
PATH_START = (HDOOR[0], -265)                         # the first cell north of the rim of the pad (the doorstep), then the door front
PATH_DOOR = (HDOOR[0], HZ2 + 1)
PATH_END = (DOOR_W[0] - 1, -322)                      # the cell in front of the west opening of the orangery
def path_route(gr, T):
    """the doorstep (pad rim -> door front), then (A*) -> the entry of the main alley at r 58 -> straight along the alley to r 27 ->
    along the west front of the orangery -> the west opening"""
    a = math.atan2(PATH_DOOR[1] + 0.5 - OCZ, PATH_DOOR[0] + 0.5 - OCX)            # the main alley points at the house
    entry = (int(round(OCX + 58 * math.cos(a))), int(round(OCZ + 58 * math.sin(a))))
    mid = (OCX + 27 * math.cos(a), OCZ + 27 * math.sin(a))
    corner = (OX1 - 3 + 0.5, min(max(mid[1], OZ1 + 4), OZ2 + 2))
    block = gr["allow"] | (gr["water"] != NONE) | ~gr["core"]
    ox = (gr["X"] >= OX1 - 2) & (gr["X"] <= OX2 + 2) & (gr["Z"] >= OZ1 - 2) & (gr["Z"] <= OZ2 + 2); block = block | ox
    hb = (gr["X"] >= HX1 - 1) & (gr["X"] <= HX2 + 1) & (gr["Z"] >= HZ1 - 1) & (gr["Z"] <= HZ2); block = block | hb
    clear = (HX2 + 2, PATH_DOOR[1])                 # along the front of the house to past its corner first (the smoothed line cut the corner)
    p1 = astar(T, clear, entry, block, gr["x1"], gr["z1"])
    pts = [(PATH_START[0] + 0.5, PATH_START[1] + 0.5), (PATH_DOOR[0] + 0.5, PATH_DOOR[1] + 0.5), (clear[0] + 0.5, clear[1] + 0.5)] + smooth_line(p1, 5)[1:-1] + \
          [(entry[0] + 0.5, entry[1] + 0.5), mid, corner, (OX1 - 3 + 0.5, PATH_END[1] + 0.5), (PATH_END[0] + 0.5, PATH_END[1] + 0.5)]
    cells = cells_of(pts)
    inside = [c for c in cells if HX1 - 1 <= c[0] <= HX2 + 1 and HZ1 - 1 <= c[1] <= HZ2 and c != PATH_DOOR]
    if inside: raise SystemExit("the path runs into the house at %s" % inside[:4])
    return cells, entry, a
def grade(gr, T, cells):
    """surfaces in half blocks (s2 = 2 x feet level): the ends pinned (house floor, orangery floor), at most 0.5 per step"""
    t = [2 * (int(round(T[ix(gr, x, z)])) + 1) for x, z in cells]
    t[0] = 2 * (int(gr["before"][ix(gr, cells[0][0], cells[0][1] + 1)]) + 1); t[-1] = 2 * (FY + 1)     # level with the rim of the pad
    fixed = {0: t[0], len(t) - 1: t[-1]}
    for i, c in enumerate(cells):
        if c == PATH_DOOR: t[i] = 2 * (FH + 1); fixed[i] = t[i]
    for _ in range(8):
        for i in range(1, len(t)):
            if i not in fixed: t[i] = max(min(t[i], t[i - 1] + 1), t[i - 1] - 1)
        for i in range(len(t) - 2, -1, -1):
            if i not in fixed: t[i] = max(min(t[i], t[i + 1] + 1), t[i + 1] - 1)
    bad = [i for i in range(1, len(t)) if abs(t[i] - t[i - 1]) > 1]
    if bad: raise SystemExit("path cannot be graded at %s" % [cells[i] for i in bad[:4]])
    surf = {}; best = {}
    for c, s2 in zip(cells, t):                       # width 3 (brush r 1)
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                q = (c[0] + dx, c[1] + dz); d = dx * dx + dz * dz
                if OX1 <= q[0] <= OX2 and OZ1 <= q[1] <= OZ2: continue
                if HX1 <= q[0] <= HX2 and HZ1 <= q[1] <= HZ2: continue
                if q not in best or d < best[q] or (d == best[q] and s2 < surf[q]): best[q] = d; surf[q] = s2
    for _ in range(60):                               # across the width at most half a block
        ch = False
        for (x, z), s2 in list(surf.items()):
            n = [surf[q] for q in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)) if q in surf]
            if s2 > min(n) + 1: surf[(x, z)] = min(n) + 1; ch = True
            elif s2 < max(n) - 1: surf[(x, z)] = max(n) - 1; ch = True
        if not ch: break
    return surf, t

def relief(gr):
    T, base, w = sculpt(gr)
    X, Z = gr["X"], gr["Z"]
    fixed = np.zeros(X.shape, bool); F = T.copy()
    def fix(m, v): F[m] = v; fixed[m] = True
    # the orangery pad (footprint + 3), the house terrace (house + 2)
    fix((X >= OX1 - 3) & (X <= OX2 + 3) & (Z >= OZ1 - 3) & (Z <= OZ2 + 3), FY)
    fix((X >= HX1 - 2) & (X <= HX2 + 2) & (Z >= HZ1 - 2) & (Z <= HZ2 + 1) & ~gr["allow"], FH)
    Tp = np.where(fixed, F, T)
    cells, entry, a = path_route(gr, Tp)
    surf, prof = grade(gr, Tp, cells)
    for (x, z), s2 in surf.items():
        y = (s2 - 1) // 2 - 1 if s2 % 2 else s2 // 2 - 1      # ground top under the path block (a slab cell: the slab sits on y+1)
        i, j = ix(gr, x, z)
        if gr["allow"][i, j]: continue
        F[i, j] = y; fixed[i, j] = True
    # berm 1 round the path level with it (its ground: the path's), then 1:1 slopes; the pads: 1:1 slopes (Chebyshev)
    pathm = np.zeros(X.shape, bool)
    for (x, z) in surf: pathm[ix(gr, x, z)] = True
    keep = ~gr["place"] | gr["allow"] | (gr["water"] != NONE)          # never moved: outside the place, the pad of bonfire 4, the water
    Fv = np.where(keep, gr["before"], F).astype(float)
    src = fixed & ~keep
    U = np.where(src, Fv, 1e9); L = np.where(src, Fv, -1e9)
    # the berm: the 8 neighbours of a path cell share its level
    for _ in range(1):
        Up = np.pad(U, 1, constant_values=1e9); Lp = np.pad(L, 1, constant_values=-1e9); nu = U.copy(); nl = L.copy()
        for dz in (0, 1, 2):
            for dx in (0, 1, 2):
                pm = np.pad(pathm, 1)[dz:dz + U.shape[0], dx:dx + U.shape[1]]
                nu = np.where(pm & ~src, np.minimum(nu, Up[dz:dz + U.shape[0], dx:dx + U.shape[1]]), nu)
                nl = np.where(pm & ~src, np.maximum(nl, Lp[dz:dz + U.shape[0], dx:dx + U.shape[1]]), nl)
        U, L = nu, nl
    for _ in range(40):
        Up = np.pad(U, 1, constant_values=1e9); Lp = np.pad(L, 1, constant_values=-1e9); nu = U.copy(); nl = L.copy()
        for dz in (0, 1, 2):
            for dx in (0, 1, 2):
                nu = np.minimum(nu, Up[dz:dz + U.shape[0], dx:dx + U.shape[1]] + 1); nl = np.maximum(nl, Lp[dz:dz + L.shape[0], dx:dx + L.shape[1]] - 1)
        U = np.where(src, Fv, nu); L = np.where(src, Fv, nl)
    free = ~src & ~keep
    out = Fv.copy()
    v = np.where(L <= U, np.clip(Fv, L, U), U)
    out[free] = v[free]
    out = np.round(out).astype(np.int32)
    out[keep] = gr["before"][keep]
    return dict(T=out, base=base, w=w, cells=cells, surf=surf, prof=prof, entry=entry, alley=a, pathm=pathm)

# ---------------------------------------------------------------- pale oaks
LOG = "minecraft:pale_oak_log[axis=%s]"
LEAF = "minecraft:pale_oak_leaves[distance=1,persistent=true,waterlogged=false]"
STRIP = "minecraft:stripped_pale_oak_log[axis=%s]"
WOOD = "minecraft:pale_oak_wood[axis=y]"
FORMS = [  # trunk height, branches (dx, dz, start above base, length, rise per step), top blob (rx, ry)
    dict(h=7, br=[(1, 0, 5, 3, 0.5), (-1, 1, 6, 2, 0.6), (0, -1, 4, 3, 0.4)], top=(3.5, 2.0)),
    dict(h=6, br=[(1, 1, 4, 3, 0.4), (-1, -1, 5, 3, 0.5)], top=(3.0, 1.6)),
    dict(h=8, br=[(-1, 0, 6, 3, 0.6), (1, -1, 5, 2, 0.5), (0, 1, 6, 3, 0.4), (1, 1, 7, 2, 0.7)], top=(3.8, 2.2)),
    dict(h=7, br=[(0, 1, 5, 4, 0.35), (1, -1, 6, 3, 0.5), (-1, 0, 4, 2, 0.6)], top=(3.2, 1.8)),
]
def rot(dx, dz, r):
    for _ in range(r): dx, dz = -dz, dx
    return dx, dz
class Trees:
    def __init__(self, b, T, gr): self.b, self.T, self.gr = b, T, gr
    def g(self, x, z): return int(self.T[ix(self.gr, x, z)])
    def leaf(self, x, y, z):
        if self.b.get(x, y, z) in (None, "minecraft:air"): self.b.set(x, y, z, LEAF)
    def blob(self, cx, cy, cz, rx, ry, salt):
        ri = int(math.ceil(rx)); cells = []
        for dx in range(-ri, ri + 1):
            for dz in range(-ri, ri + 1):
                for dy in range(-1, int(math.ceil(ry)) + 1):
                    e = (dx * dx + dz * dz) / (rx * rx) + (dy * dy) / (ry * ry if dy > 0 else 1.6)
                    if e > 1.0 or (e > 0.7 and hsh(cx + dx, cy + dy, cz + dz, salt) < 0.35): continue
                    cells.append((cx + dx, cy + dy, cz + dz)); self.leaf(cx + dx, cy + dy, cz + dz)
        for (x, y, z) in cells:                      # pale hanging moss under the leaves
            if self.b.get(x, y - 1, z) not in (None, "minecraft:air") or hsh(x, y, z, salt + 1) > 0.13: continue
            n = 1 + int(hsh(x, y, z, salt + 2) * 3)
            for k in range(1, n + 1):
                if self.b.get(x, y - k, z) not in (None, "minecraft:air") or y - k <= self.g(x, z) + 1: break
                self.b.set(x, y - k, z, "minecraft:pale_hanging_moss[tip=%s]" % ("true" if k == n else "false"))
    def tree(self, x, z, form, r, size=2, extra_h=0):
        """trunk size x size at x..x+size-1, z..z+size-1; returns the base y (first trunk block above the highest ground of the trunk)"""
        f = FORMS[form]; cols = [(x + i, z + k) for i in range(size) for k in range(size)]
        base = max(self.g(cx, cz) for cx, cz in cols) + 1; H = f["h"] + extra_h + (1 if size == 3 else 0)
        for cx, cz in cols:
            for y in range(self.g(cx, cz) + 1, base + H): self.b.set(cx, y, cz, LOG % "y")
        mx, mz = x + (size - 1) / 2, z + (size - 1) / 2
        for k, (bx, bz, s, L, rise) in enumerate(f["br"]):
            dx, dz = rot(bx, bz, r)
            px, pz, py = mx + dx * (size / 2), mz + dz * (size / 2), base + s
            for i in range(L):
                px += dx; pz += dz; py += rise
                ax = "x" if abs(dx) >= abs(dz) and dx else "z"
                self.b.set(int(math.floor(px + 0.5)), int(py), int(math.floor(pz + 0.5)), LOG % ax)
            self.blob(int(math.floor(px + 0.5)), int(py) + 1, int(math.floor(pz + 0.5)), 2.6, 1.4, 4100 + k)
        tx, tz = int(math.floor(mx + 0.5)), int(math.floor(mz + 0.5))
        rx, ry = f["top"]; self.blob(tx, base + H, tz, rx + (0.6 if size == 3 else 0), ry, 4111)
        for cx, cz in cols: self.b.set(cx, base + H, cz, LOG % "y")
        return base

# ---------------------------------------------------------------- the layout of the trees
def tree_sites(gr, rl):
    """(x, z, kind) of the 2x2 trunks (north-west cell): 'alley' on the radial rows up to r 50, 'row' broken rows to r 72, 'wild'"""
    T = rl["T"]; X, Z = gr["X"], gr["Z"]
    blocked = ~gr["core"] | gr["allow"] | (gr["water"] != NONE)
    blocked |= (X >= OX1 - 6) & (X <= OX2 + 6) & (Z >= OZ1 - 6) & (Z <= OZ2 + 6)
    blocked |= (X >= HX1 - 5) & (X <= HX2 + 5) & (Z >= HZ1 - 5) & (Z <= HZ2 + 5)
    near_path = cheb_dist(rl["pathm"], 4) <= 3
    blocked |= near_path
    wd = cheb_dist(gr["water"] != NONE, 3); blocked |= wd <= 1
    def ok(x, z, size=2):
        for i in range(-1, size + 1):
            for k in range(-1, size + 1):
                p, q = ix(gr, x + i, z + k)
                if not (0 <= p < T.shape[0] and 0 <= q < T.shape[1]) or blocked[p, q]: return False
        hs = [T[ix(gr, x + i, z + k)] for i in range(size) for k in range(size)]
        return max(hs) - min(hs) <= 3
    sites = []; taken = set()
    def add(x, z, kind):
        if not ok(x, z): return False
        for (a, b) in taken:
            if abs(a - x) < 5 and abs(b - z) < 5: return False
        sites.append((x, z, kind)); taken.add((x, z)); return True
    a0 = rl["alley"]; n = 26; step = 2 * math.pi / n
    for ring, rr in enumerate((28, 35, 42, 49, 56, 63, 70)):
        lines = [a0 + step / 2 + k * step for k in range(n)]
        if rr >= 42: lines += [a0 + k * step for k in range(n) if abs(((k * step + math.pi) % (2 * math.pi)) - math.pi) > 0.2]
        for k, ang in enumerate(lines):
            jit = 0 if rr <= 49 else (rr - 49) / 8
            if rr > 49 and hsh(k, rr, 0, 4201) < 0.18 + (rr - 49) * 0.012: continue
            jx = (hsh(k, rr, 1, 4202) - 0.5) * 2 * jit; jz = (hsh(k, rr, 2, 4203) - 0.5) * 2 * jit
            x = int(round(OCX - 1 + rr * math.cos(ang) + jx)); z = int(round(OCZ - 1 + rr * math.sin(ang) + jz))
            add(x, z, "alley" if rr <= 49 else "row")
    for gx in range(CORE[0], CORE[2], 7):            # wild forest: jittered grid 7x7, some cells empty (clearings)
        for gz in range(CORE[1], CORE[3], 7):
            x = gx + int(hsh(gx, 0, gz, 4211) * 5); z = gz + int(hsh(gx, 1, gz, 4212) * 5)
            r = math.hypot(x + 1 - OCX, z + 1 - OCZ)
            if r < 74 or hsh(gx, 2, gz, 4213) < 0.22: continue
            add(x, z, "wild")
    return sites

def pick_special(gr, rl, sites):
    """the 6 living faces (hearts) and the 12 carved faces: chosen among the sites (deterministic)"""
    path = rl["cells"]; water = gr["water"] != NONE
    def pd(x, z): return min(math.hypot(x - a, z - b) for a, b in path[::3])
    def r(x, z): return math.hypot(x + 1 - OCX, z + 1 - OCZ)
    wd = cheb_dist(water, 12)
    def wdist(x, z): return int(wd[ix(gr, x, z)])
    used = set(); hearts = []
    def take(cands, key, kind, n=1, sep=30, lst=None):
        lst = hearts if lst is None else lst
        for s in sorted(cands, key=key):
            if s in used or any(math.hypot(s[0] - h[0], s[1] - h[1]) < sep for h in lst): continue
            lst.append((s[0], s[1], kind)); used.add(s)
            if sum(1 for h in lst if h[2] == kind) >= n: return
        raise SystemExit("no site for " + kind)
    al = [s for s in sites if s[2] == "alley" and 35 <= r(s[0], s[1]) <= 49 and pd(s[0], s[1]) > 12]
    take(al, lambda s: hsh(s[0], 0, s[1], 4301), "alley", 2, sep=40)
    wl = [s for s in sites if s[2] == "wild" and r(s[0], s[1]) > 80 and pd(s[0], s[1]) > 20 and s[0] > 300]
    take(wl, lambda s: hsh(s[0], 0, s[1], 4302), "wild", 2, sep=60)
    rv = [s for s in sites if wdist(s[0], s[1]) <= 5 and s[1] < -340 and pd(s[0], s[1]) > 10]
    take(rv, lambda s: math.hypot(s[0] - 362, s[1] + 352), "river")
    nv = [s for s in sites if s[0] > 385 and s[1] < -370]
    take(nv, lambda s: int(rl["T"][ix(gr, s[0], s[1])]) + 0.01 * hsh(s[0], 0, s[1], 4303), "valley")
    faces = []
    np_ = [s for s in sites if 6 <= pd(s[0], s[1]) <= 14 and s not in used]
    take(np_, lambda s: hsh(s[0], 0, s[1], 4311), "path", 4, sep=18, lst=faces)
    al2 = [s for s in sites if s[2] in ("alley", "row") and s not in used and pd(s[0], s[1]) > 6]
    take(al2, lambda s: hsh(s[0], 0, s[1], 4312), "alley", 4, sep=18, lst=faces)
    wl2 = [s for s in sites if s[2] == "wild" and s not in used and pd(s[0], s[1]) > 6]
    take(wl2, lambda s: hsh(s[0], 0, s[1], 4313), "wild", 4, sep=30, lst=faces)
    return hearts, faces

def face_dir(x, z, size=3):
    """outward cardinal (away from the orangery) as (dx, dz)"""
    vx, vz = x + size / 2 - OCX, z + size / 2 - OCZ
    if abs(vx) >= abs(vz): return (1 if vx > 0 else -1, 0)
    return (0, 1 if vz > 0 else -1)
TRAP_FACING = {(0, -1): "north", (0, 1): "south", (-1, 0): "west", (1, 0): "east"}
def face_cells(x, z, base, d, size=3):
    """the 3 trunk cells of the side d (in order) and the 3 air cells in front of them"""
    dx, dz = d
    if dz: zz = z if dz < 0 else z + size - 1; side = [(x + i, zz) for i in range(size)]
    else: xx = x if dx < 0 else x + size - 1; side = [(xx, z + i) for i in range(size)]
    return side, [(cx + dx, cz + dz) for cx, cz in side]
def face_blocks(x, z, base, d, state):
    """{(x,y,z): block} of the face on side d (3 cells wide): a pale mask 3x3 of stripped pale oak (brow, cheeks, nose)
    with the eyes (open: dark sockets of pale oak wood; closed: pale lids of stripped log laid across), under it the mouth (a dark hole
    behind a pale oak trapdoor: teeth) in the bark"""
    side, front = face_cells(x, z, base, d); out = {}
    hax = "x" if d[1] else "z"
    for i, (cx, cz) in enumerate(side):
        mid = i == 1
        out[(cx, base + 1, cz)] = WOOD if mid else LOG % "y"
        out[(cx, base + 2, cz)] = STRIP % "y"
        out[(cx, base + 3, cz)] = STRIP % "y" if mid else (WOOD if state == "open" else STRIP % hax)
        out[(cx, base + 4, cz)] = STRIP % hax
        fx, fz = front[i]
        if mid: out[(fx, base + 1, fz)] = "minecraft:pale_oak_trapdoor[facing=%s,half=bottom,open=true,powered=false,waterlogged=false]" % TRAP_FACING[d]
    return out
def bark_blocks(x, z, base, d):
    side, front = face_cells(x, z, base, d); out = {}
    for (cx, cz) in side:
        for y in range(base + 1, base + 5): out[(cx, y, cz)] = LOG % "y"
    out[(front[1][0], base + 1, front[1][1])] = "minecraft:air"
    return out

# ---------------------------------------------------------------- ground
def ground_block(x, z):
    """pale garden floor (card): pale moss 35 (+ carpets 20), grass 25, podzol 10, coarse dirt 10 - in patches"""
    n = vnoise(x, z, 6, 4401); m = hsh(x, 0, z, 4402)
    if n < 0.22: return "minecraft:podzol[snowy=false]" if m < 0.55 else "minecraft:coarse_dirt"
    if n < 0.48: return "minecraft:grass_block[snowy=false]" if m < 0.85 else "minecraft:pale_moss_block"
    return "minecraft:pale_moss_block" if m < 0.9 else "minecraft:grass_block[snowy=false]"
def vnoise(x, z, cell, seed):
    gx, gz = x // cell, z // cell; fx = (x - gx * cell) / cell; fz = (z - gz * cell) / cell
    fx = fx * fx * (3 - 2 * fx); fz = fz * fz * (3 - 2 * fz)
    a, b_, c, d = hsh(gx, 0, gz, seed), hsh(gx + 1, 0, gz, seed), hsh(gx, 0, gz + 1, seed), hsh(gx + 1, 0, gz + 1, seed)
    return (a * (1 - fx) + b_ * fx) * (1 - fz) + (c * (1 - fx) + d * fx) * fz
CARPET = "minecraft:pale_moss_carpet[bottom=true,east=none,north=none,south=none,west=none]"
ROCK = Mix({"stone": 40, "andesite": 30, "tuff": 20, "cobblestone": 10}, 4403)
MARGIN_TOP = Mix({"grass_block[snowy=false]": 55, "podzol[snowy=false]": 25, "coarse_dirt": 20}, 4404)

# ---------------------------------------------------------------- the orangery
FLOOR_A, FLOOR_B = "minecraft:polished_diorite", "minecraft:polished_deepslate"
def roof_y(z):
    dz = abs(z + 0.5 - OCZ); hw = (OZ2 - OZ1 + 1) / 2
    return FY + WALL_H + int(round((ROOF_H - WALL_H) * math.sqrt(max(0.0, 1 - (dz / hw) ** 2))))
def orangery(b, T, gr):
    pane = Mix({"glass_pane": 1}, 0)
    def hole(x, y, z):
        return vnoise(x * 2 + z, y * 2, 3, 4501) < 0.5
    posts = list(range(OX1, OX2 + 1, 5)) + [OX2]
    # floor (and its bed), broken by roots and moss
    for x in range(OX1, OX2 + 1):
        for z in range(OZ1, OZ2 + 1):
            b.set(x, FY - 1, z, "minecraft:stone")
            b.set(x, FY, z, FLOOR_A if (x + z) % 2 == 0 else FLOOR_B)
            for y in range(FY + 1, FY + ROOF_H + 1): b.set(x, y, z, "minecraft:air")
            r = hsh(x, 0, z, 4502)
            if r < 0.05: b.set(x, FY, z, "minecraft:pale_moss_block")
            elif r < 0.08: b.set(x, FY, z, "minecraft:coarse_dirt")
    # the basin: smooth quartz with calcite cracks, recessed 1, steps on the west side
    x1, z1, x2, z2 = BASIN
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            edge = x in (x1, x2) or z in (z1, z2)
            if edge: b.set(x, FY, z, "minecraft:smooth_quartz" if hsh(x, 1, z, 4503) > 0.2 else "minecraft:calcite"); continue
            b.set(x, FY - 2, z, "minecraft:stone")
            b.set(x, FY - 1, z, "minecraft:calcite" if vnoise(x * 3, z * 3, 2, 4504) < 0.18 else "minecraft:smooth_quartz")
            b.set(x, FY, z, "minecraft:air")
    for z in (-322, -321):         # steps down from the west rim
        b.set(x1, FY, z, "minecraft:smooth_quartz_slab[type=bottom,waterlogged=false]")
        b.set(x1 + 1, FY - 1, z, "minecraft:smooth_quartz")
    # the pedestal of the key with candles round it
    px, pz = PED
    b.set(px, FY, pz, "minecraft:chiseled_quartz_block")
    for i, (dx, dz) in enumerate(((2, 0), (-2, 0), (0, 2), (0, -2), (1, 1), (-1, 1), (1, -1), (-1, -1))):
        cx, cz = px + dx, pz + dz
        if not (x1 < cx < x2 and z1 < cz < z2): continue
        b.set(cx, FY, cz, "minecraft:candle[candles=%d,lit=true,waterlogged=false]" % (1 + i % 3 if abs(dx) + abs(dz) == 2 and dx * dz == 0 else 1 + (i % 2)))
    # walls: socle 1 of deepslate, posts of stripped pale oak every 5, glass panes half broken, iron bars at mid height, the openings
    for x in range(OX1, OX2 + 1):
        for z in range(OZ1, OZ2 + 1):
            wall_x = x in (OX1, OX2); wall_z = z in (OZ1, OZ2)
            if not (wall_x or wall_z): continue
            post = (x in posts and wall_z) or (wall_x and (z - OZ1) % 5 == 0) or (wall_x and z == OZ2)
            top = roof_y(z) if wall_x else FY + WALL_H
            for y in range(FY + 1, top + 1):
                if post: b.set(x, y, z, STRIP % "y"); continue
                if y == FY + 1: b.set(x, y, z, "minecraft:polished_deepslate"); continue
                if y == FY + 5 or y == top: b.set(x, y, z, "minecraft:iron_bars"); continue
                b.set(x, y, z, "minecraft:air" if hole(x, y, z) else "minecraft:glass_pane")
    for (wx, za, zb) in (DOOR_W, DOOR_E):
        for z in range(za, zb + 1):
            for y in range(FY + 1, FY + 6): b.set(wx, y, z, "minecraft:air")
        b.set(wx, FY + 6, za, "minecraft:iron_bars"); b.set(wx, FY + 6, zb, "minecraft:iron_bars")
        for y in range(FY + 1, FY + 7): b.set(wx, y, za - 1, STRIP % "y"); b.set(wx, y, zb + 1, STRIP % "y")
    # the barrel roof along x: ribs over the posts (stripped logs), purlins of iron bars every 4, glass half broken; the hole round the tree
    for x in range(OX1, OX2 + 1):
        rib = x in posts
        for z in range(OZ1, OZ2 + 1):
            y = roof_y(z); yp = roof_y(z - 1) if z > OZ1 else y; yn = roof_y(z + 1) if z < OZ2 else y
            ys = range(min(y, yp, yn), y + 1)
            for yy in ys:
                if yy < FY + WALL_H: continue
                if math.hypot(x + 0.5 - (TRUNK[0] + 2), z + 0.5 - (TRUNK[1] + 2)) < 5.5: b.set(x, yy, z, "minecraft:air"); continue
                if rib: b.set(x, yy, z, STRIP % "x")
                elif (z - OZ1) % 4 == 0: b.set(x, yy, z, "minecraft:iron_bars")
                else: b.set(x, yy, z, "minecraft:air" if hole(x, yy + 7, z) else "minecraft:glass_pane")
    # chains hanging from the ribs, empty tubs
    for i, x in enumerate(posts[1:-1]):
        for z in (-331, -326, -317, -312):
            if hsh(x, 2, z, 4505) < 0.45: continue
            y0 = roof_y(z) - 1; n = 2 + int(hsh(x, 3, z, 4506) * 4)
            for k in range(n): b.set(x, y0 - k, z, "minecraft:iron_chain[axis=y,waterlogged=false]")
    tubs = [(320, -333), (320, -310), (355, -333), (355, -310), (326, -333), (349, -310), (333, -310), (343, -333), (322, -327), (353, -316)]
    for k, (x, z) in enumerate(tubs):
        b.set(x, FY + 1, z, "minecraft:decorated_pot[cracked=%s,facing=north,waterlogged=false]" % ("true" if k % 2 else "false") if k < 6 else "minecraft:cauldron")
    great_tree(b)
def great_tree(b):
    """the great pale oak from the basin: trunk 4x4 with a root flare, 30 high from the floor, branches through the roof, a crown above it"""
    x1, z1, x2, z2 = TRUNK; top = FY + 30
    for x in range(x1 - 1, x2 + 2):
        for z in range(z1 - 1, z2 + 2):
            inner = x1 <= x <= x2 and z1 <= z <= z2
            corner = x in (x1 - 1, x2 + 1) and z in (z1 - 1, z2 + 1)
            h = top if inner else (FY + 3 if not corner else -1)
            for y in range(FY - 1, h + 1): b.set(x, y, z, LOG % "y" if inner or y > FY else "minecraft:pale_oak_wood[axis=y]")
    # roots on the floor: 8 runs of pale oak wood breaking the tiles (some into the basin rim and beyond)
    for i, (dx, dz) in enumerate(((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1))):
        L = 6 + int(hsh(i, 0, 0, 4601) * 8); cx, cz = (x1 + x2 + 1) / 2, (z1 + z2 + 1) / 2
        for k in range(3, 3 + L):
            x = int(math.floor(cx + dx * k + (hsh(i, k, 0, 4602) - 0.5))); z = int(math.floor(cz + dz * k + (hsh(i, k, 1, 4603) - 0.5)))
            if not (OX1 < x < OX2 and OZ1 < z < OZ2) or (x, z) == PED: continue
            y = FY if not (BASIN[0] < x < BASIN[2] and BASIN[1] < z < BASIN[3]) else FY - 1
            b.set(x, y, z, "minecraft:pale_oak_wood[axis=%s]" % ("x" if abs(dx) >= abs(dz) else "z"))
            if k < 5: b.set(x, y + 1, z, "minecraft:pale_oak_wood[axis=y]")
    # branches through the roof and the crown
    cx, cz = (x1 + x2 + 1) / 2, (z1 + z2 + 1) / 2
    blobs = [(cx, top + 1, cz, 6.5, 3.0)]
    for i in range(9):
        a = math.radians(i * 40 + 15); y0 = FY + 19 + int(hsh(i, 1, 0, 4604) * 9); L = 6 + int(hsh(i, 2, 0, 4605) * 5)
        px, pz, py = cx, cz, float(y0)
        for k in range(L):
            px += math.cos(a); pz += math.sin(a); py += 0.55
            x, y, z = int(math.floor(px)), int(round(py)), int(math.floor(pz))
            b.set(x, y, z, LOG % ("x" if abs(math.cos(a)) > abs(math.sin(a)) else "z"))
        blobs.append((px, py + 1, pz, 4.2, 2.2))
    for (bx, by, bz, rx, ry) in blobs:
        ri = int(math.ceil(rx))
        for dx in range(-ri, ri + 1):
            for dz in range(-ri, ri + 1):
                for dy in range(-2, int(ry) + 1):
                    x, y, z = int(math.floor(bx)) + dx, int(by) + dy, int(math.floor(bz)) + dz
                    e = (dx * dx + dz * dz) / (rx * rx) + dy * dy / (ry * ry)
                    if e > 1 or (e > 0.7 and hsh(x, y, z, 4606) < 0.4) or y <= roof_y(z) + 1 and OX1 <= x <= OX2 and OZ1 <= z <= OZ2: continue
                    if b.get(x, y, z) in (None, "minecraft:air"): b.set(x, y, z, LEAF)
                    if hsh(x, y, z, 4607) < 0.1 and b.get(x, y - 1, z) in (None, "minecraft:air") and not (OX1 <= x <= OX2 and OZ1 <= z <= OZ2 and y - 2 <= roof_y(z)):
                        b.set(x, y - 1, z, "minecraft:pale_hanging_moss[tip=true]")
    return top

# ---------------------------------------------------------------- the gardener's house
def house(b):
    y0 = FH
    for x in range(HX1, HX2 + 1):
        for z in range(HZ1, HZ2 + 1):
            b.set(x, y0 - 1, z, "minecraft:stone"); b.set(x, y0, z, "minecraft:pale_oak_planks")
            edge_x = x in (HX1, HX2); edge_z = z in (HZ1, HZ2)
            for y in range(y0 + 1, y0 + 5):
                if edge_x and edge_z: b.set(x, y, z, STRIP % "y")
                elif edge_x or edge_z: b.set(x, y, z, "minecraft:pale_oak_planks" if y != y0 + 4 else STRIP % ("x" if edge_z else "z"))
                else: b.set(x, y, z, "minecraft:air")
            if not (edge_x or edge_z): b.set(x, y0 + 5, z, "minecraft:pale_oak_planks")          # ceiling
    # gable roof: the ridge along x, stairs falling north and south, gables of planks, the attic empty
    for k in range(0, 5):
        y = y0 + 5 + k; zn, zs = HZ1 - 1 + k, HZ2 + 1 - k
        for x in range(HX1 - 1, HX2 + 2):
            if zn < zs:
                b.set(x, y, zn, "minecraft:pale_oak_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]")
                b.set(x, y, zs, "minecraft:pale_oak_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]")
            else: b.set(x, y, zn, "minecraft:pale_oak_slab[type=bottom,waterlogged=false]")
        if k >= 1:
            for z in range(zn + 1, zs):
                b.set(HX1, y - 1, z, "minecraft:pale_oak_planks"); b.set(HX2, y - 1, z, "minecraft:pale_oak_planks")
                for x in range(HX1 + 1, HX2):
                    if y - 1 > y0 + 5: b.set(x, y - 1, z, "minecraft:air")
    # door (south wall, to the pad), windows (glass panes), light inside (hanging lanterns), table, lectern with the notes, a barrel
    dx, dz = HDOOR
    b.set(dx, y0 + 1, dz, "minecraft:pale_oak_door[facing=north,half=lower,hinge=left,open=false,powered=false]")
    b.set(dx, y0 + 2, dz, "minecraft:pale_oak_door[facing=north,half=upper,hinge=left,open=false,powered=false]")
    b.set(WINDOW[0], y0 + 2, WINDOW[1], "minecraft:glass_pane"); b.set(WINDOW[0], y0 + 3, WINDOW[1], "minecraft:glass_pane")
    for (x, z) in ((240, HZ2), (242, HZ1), (HX1, -272), (HX2, -272)): b.set(x, y0 + 2, z, "minecraft:glass_pane")
    for (x, z) in ((240, -271), (244, -273)): b.set(x, y0 + 4, z, "minecraft:lantern[hanging=true,waterlogged=false]")
    b.set(244, y0 + 1, -274, "minecraft:pale_oak_fence"); b.set(244, y0 + 2, -274, "minecraft:pale_oak_pressure_plate[powered=false]")
    b.set(243, y0 + 1, -274, "minecraft:pale_oak_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]")
    book = ('{Book:{id:"minecraft:written_book",count:1,components:{"minecraft:written_book_content":{title:{raw:"Записки садовника"},author:"садовник",'
            'pages:[{raw:"…"}]}}},Page:0}')
    b.set(LECTERN[0], y0 + 1, LECTERN[1], "minecraft:lectern[facing=east,has_book=true,powered=false]" + book)
    b.set(239, y0 + 1, -274, "minecraft:barrel[facing=up,open=false]")
    b.set(245, y0 + 1, -274, "minecraft:flower_pot")

# ---------------------------------------------------------------- the path, sensors, bones, signs, eyeblossoms
PATHM = Mix({"mossy_cobblestone": 70, "cobblestone": 10, "mossy_stone_bricks": 20}, 4701)
def path_blocks(b, gr, rl):
    surf = rl["surf"]
    for (x, z), s2 in surf.items():
        if gr["allow"][ix(gr, x, z)]: continue
        if s2 % 2:
            y = (s2 - 1) // 2
            b.set(x, y - 1, z, "minecraft:dirt"); b.set(x, y, z, slab("mossy_cobblestone_slab" if hsh(x, 0, z, 4702) < 0.5 else "stone_brick_slab"))
            if hsh(x, 1, z, 4703) < 0.0: pass
        else:
            y = s2 // 2 - 1
            b.set(x, y, z, PATHM)
            if hsh(x, 2, z, 4704) < 0.22 and (x, z) not in ((PATH_START), (PATH_END)):
                b.set(x, y + 1, z, CARPET)
        for yy in range(y + 1 + (0 if s2 % 2 == 0 else 0), y + 5):
            if b.get(x, yy, z) is None: b.set(x, yy, z, "minecraft:air")
def sensors(gr, rl):
    """10 sculk sensors: along the path every ~17 blocks (2 off its edge, alternating sides) and 4 round the orangery"""
    cells = rl["cells"]; out = []; acc = 0; side = 1; last = None
    pm = rl["pathm"]
    for i in range(1, len(cells) - 1):
        if last is not None: acc += math.hypot(cells[i][0] - last[0], cells[i][1] - last[1])
        last = cells[i]
        if acc < 16 or len(out) >= 6: continue
        (ax, az), (bx, bz) = cells[i - 1], cells[i + 1]; tx, tz = bx - ax, bz - az; L = math.hypot(tx, tz) or 1
        nx, nz = -tz / L * side, tx / L * side
        x, z = int(round(cells[i][0] + nx * 3)), int(round(cells[i][1] + nz * 3))
        if pm[ix(gr, x, z)]: continue
        out.append((x, z)); acc = 0; side = -side
    for (x, z) in ((OX1 - 5, OZ1 + 3), (OCX, OZ1 - 4), (OX2 + 4, -330), (OX2 + 4, OZ2 - 3)):
        out.append((int(x), int(z)))
    return out
def sensor_blocks(b, gr, T, sens, pathm):
    """the sensor in the ground under a moss carpet; bones: one block standing out of the moss, one flush; every second sensor a sign on
    a post (the cells round the sensor farthest from the path)"""
    pd = cheb_dist(pathm, 6); pts = []
    def far(cands):
        return max(cands, key=lambda c: (pd[ix(gr, *c)], -abs(c[0]) * 0))
    for k, (x, z) in enumerate(sens):
        y = int(T[ix(gr, x, z)])
        b.set(x, y, z, "minecraft:sculk_sensor[power=0,sculk_sensor_phase=inactive,waterlogged=false]"); b.set(x, y + 1, z, CARPET)
        b.set(x, y - 1, z, "minecraft:dirt")
        ring = [(x + a, z + c) for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))]
        ring.sort(key=lambda c: (-pd[ix(gr, *c)], hsh(c[0], k, c[1], 4720)))
        (bx, bz), (fx, fz), (sx, sz) = ring[0], ring[1], ring[2]
        by = int(T[ix(gr, bx, bz)])
        b.set(bx, by + 1, bz, "minecraft:bone_block[axis=%s]" % ("x" if k % 2 else "y")); b.set(bx, by + 2, bz, "minecraft:air")
        b.set(fx, int(T[ix(gr, fx, fz)]), fz, "minecraft:bone_block[axis=z]")
        sign = None
        if k % 2 == 0:
            sy = int(T[ix(gr, sx, sz)])
            rotv = int(round((math.degrees(math.atan2(-(x + 0.5 - (sx + 0.5)), (z + 0.5 - (sz + 0.5)))) % 360) / 22.5)) % 16
            b.set(sx, sy + 1, sz, "minecraft:pale_oak_fence")
            b.set(sx, sy + 2, sz, 'minecraft:pale_oak_sign[rotation=%d,waterlogged=false]{front_text:{messages:["",{"text":"Здесь ходят тихо."},"",""]},back_text:{messages:["",{"text":"Здесь ходят тихо."},"",""]}}' % ((rotv + 8) % 16))
            b.set(sx, sy + 3, sz, "minecraft:air")
            sign = [sx, sy + 2, sz]
        pts.append(dict(id=k + 1, x=x, y=y, z=z, sign=sign))
    return pts
def eyeblossoms(b, gr, T, rl, taken):
    """150..250 closed eyeblossoms, denser on the clearings and along the alleys; the list goes to the datapack"""
    X, Z = gr["X"], gr["Z"]; pts = []
    for z in range(CORE[1] + 2, CORE[3] - 1):
        for x in range(CORE[0] + 2, CORE[2] - 1):
            i, j = ix(gr, x, z)
            if gr["water"][i, j] != NONE or rl["pathm"][i, j] or gr["allow"][i, j] or (x, z) in taken: continue
            if OX1 - 4 <= x <= OX2 + 4 and OZ1 - 4 <= z <= OZ2 + 4: continue
            if HX1 - 3 <= x <= HX2 + 3 and HZ1 - 3 <= z <= HZ2 + 3: continue
            r = math.hypot(x + 0.5 - OCX, z + 0.5 - OCZ)
            dens = 0.012 + (0.03 if 24 <= r <= 60 else 0) + 0.05 * max(0.0, vnoise(x, z, 11, 4801) - 0.62) * 4
            if hsh(x, 3, z, 4802) < dens: pts.append((x, int(T[i, j]) + 1, z))
    pts.sort(key=lambda p: hsh(p[0], 0, p[2], 4803)); pts = pts[:230]
    out = []
    for (x, y, z) in pts:
        i, j = ix(gr, x, z)
        if max(abs(int(T[i + a, j + c]) - (y - 1)) for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1))) >= 3: continue   # steep: rock
        if b.get(x, y, z) not in (None, "minecraft:air") or b.get(x, y - 1, z) is not None: continue
        b.set(x, y, z, "minecraft:closed_eyeblossom"); out.append((x, y, z))
    return sorted(out)

# ---------------------------------------------------------------- terrain write, the blocks of the whole place
def blocks(gr, rl):
    b = B("garden"); T = rl["T"]
    tr = Trees(b, T, gr)
    sites = tree_sites(gr, rl)
    hearts, faces = pick_special(gr, rl, sites)
    special = {(h[0], h[1]) for h in hearts} | {(f[0], f[1]) for f in faces}
    orangery(b, T, gr)
    house(b)
    path_blocks(b, gr, rl)
    sens = sensor_blocks(b, gr, T, sensors(gr, rl), rl["pathm"])
    heart_pts = []; face_pts = []
    for k, (x, z, kind) in enumerate(hearts):
        base = tr.tree(x, z, int(hsh(x, 0, z, 4901) * 4), int(hsh(x, 1, z, 4902) * 4), size=2)
        # the heart in the outer side of the trunk (towards the orangery's opposite), at eye height, between two logs
        d = face_dir(x, z, 2); cx = x + (1 if d[0] > 0 else 0) if d[0] else x + (k % 2); cz = z + (1 if d[1] > 0 else 0) if d[1] else z + (k % 2)
        b.set(cx, base + 1, cz, "minecraft:creaking_heart[axis=y,creaking_heart_state=dormant,natural=true]")
        heart_pts.append(dict(id=k + 1, kind=kind, x=cx, y=base + 1, z=cz, tree=[x, z]))
    for k, (x, z, kind) in enumerate(faces):
        base = tr.tree(x - 0, z - 0, int(hsh(x, 0, z, 4903) * 4), int(hsh(x, 1, z, 4904) * 4), size=3, extra_h=1)
        d = face_dir(x, z, 3)
        for (p, s) in face_blocks(x, z, base, d, "closed").items(): b.set(*p, s)
        face_pts.append(dict(id=k + 1, kind=kind, x=x, z=z, base=base, out=list(d)))
    for (x, z, kind) in sites:
        if (x, z) in special: continue
        tr.tree(x, z, int(hsh(x, 0, z, 4905) * 4), int(hsh(x, 1, z, 4906) * 4), size=2)
    taken = {(x, z) for (x, y, z) in b.v}
    blooms = eyeblossoms(b, gr, T, rl, set())
    return b, hearts, heart_pts, face_pts, sens, blooms, sites

def surface(b, gr, rl):
    """every column of the place (not the water, not the pad of bonfire 4): the ground top by the palette (2 blocks of dirt under it),
    pale moss carpets, air from the ground up to what stood there (trees, snow layers, plants) where nothing of ours is placed"""
    T = rl["T"]; X = gr["X"]; n = 0
    for i in range(T.shape[0]):
        for j in range(T.shape[1]):
            if not gr["place"][i, j] or gr["allow"][i, j] or gr["water"][i, j] != NONE: continue
            x, z = j + gr["x1"], i + gr["z1"]; y = int(T[i, j])
            core = gr["core"][i, j]
            # steep: bare rock
            nb = [T[i + a, j + c] for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= i + a < T.shape[0] and 0 <= j + c < T.shape[1]]
            steep = max(abs(v - y) for v in nb) >= 3
            if b.get(x, y, z) is None:
                b.set(x, y, z, ROCK.at(x, y, z) if steep else (ground_block(x, z) if core else MARGIN_TOP.at(x, y, z)))
                for k in (1, 2):
                    if b.get(x, y - k, z) is None and not steep: b.set(x, y - k, z, "minecraft:dirt")
            if core and not steep and b.get(x, y + 1, z) is None and str(b.get(x, y, z)).split("[")[0] in ("minecraft:pale_moss_block", "minecraft:grass_block") \
                    and hsh(x, 5, z, 4950) < 0.25:
                b.set(x, y + 1, z, CARPET)
            top = max(int(gr["top"][i, j]), y + 1)
            for yy in range(y + 1, min(top, y + 48) + 1):
                if b.get(x, yy, z) is None: b.set(x, yy, z, "minecraft:air"); n += 1
    return n
KIND_SKIP = {"air", "cave_air", "void_air", "barrier", "water", "lava", "short_grass", "tall_grass", "fern", "large_fern", "snow", "vine", "dead_bush",
             "bush", "leaf_litter", "wildflowers", "sugar_cane", "seagrass", "tall_seagrass", "kelp", "kelp_plant", "sweet_berry_bush", "firefly_bush",
             "short_dry_grass", "tall_dry_grass", "pumpkin", "moss_carpet", "pale_moss_carpet", "pale_hanging_moss", "bamboo", "cactus", "cocoa", "lily_pad",
             "glow_lichen", "hanging_roots", "red_bush", "big_dripleaf", "big_dripleaf_stem", "small_dripleaf", "brown_mushroom_block", "red_mushroom_block",
             "mushroom_stem", "bee_nest", "creaking_heart", "resin_clump", "pointed_dripstone"}
def scan_ground_kind(s):
    """True when tools/terrain.sh scan counts the block as ground (a port of Terrain.kind: everything but plants, air, logs, leaves, water)"""
    n = s.split("[")[0].split("{")[0].replace("minecraft:", "")
    if n in ("water", "bubble_column", "lava") or n.endswith("leaves"): return False
    if n.endswith("_log") or n.endswith("_wood") or n.endswith("_stem") or n.endswith("_hyphae") or "mangrove_roots" in n: return False
    if n in KIND_SKIP or n.endswith("sapling") or n in ("poppy", "dandelion", "lilac", "peony") or \
       any(k in n for k in ("flower", "tulip", "mushroom", "orchid", "allium", "bluet", "daisy", "lily", "rose", "cornflower", "dripleaf", "eyeblossom", "petals", "bush", "carpet")):
        return False
    return True
def write_terrain(gr, rl, b):
    """only the columns whose ground is not yet what it should be (a re-run on the built garden rewrites nothing). Our own blocks over the
    wanted ground (house, orangery, path slabs, bones, fences) are what the scan sees there: not a reason to rewrite."""
    T, now = rl["T"], gr["live"]
    top = np.full(T.shape, -999, int)
    for (x, y, z), s in b.v.items():
        if not scan_ground_kind(s): continue
        i, j = ix(gr, x, z)
        if 0 <= i < T.shape[0] and 0 <= j < T.shape[1] and y > T[i, j]: top[i, j] = max(top[i, j], y)
    own = (now <= np.maximum(top, T)) & (now >= T)
    cand = gr["place"] & ~gr["allow"] & (gr["water"] == NONE)
    touch = cand & (now != T) & ~own
    # the rest: what the scan sees after terrain + blocks (our blocks replace the top of the ground: the basin, the roots in the floor)
    cols = {}
    for (x, y, z), s in b.v.items(): cols.setdefault((x, z), {})[y] = s
    for i, j in zip(*np.nonzero(touch)):
        x, z = j + gr["x1"], i + gr["z1"]; c = cols.get((x, z))
        if not c: continue
        for y in range(max(max(c), int(T[i, j])), int(T[i, j]) - 12, -1):
            s = c.get(y)
            if (scan_ground_kind(s) if s is not None else y <= T[i, j]):
                if y == now[i, j]: touch[i, j] = False
                break
    H = np.where(touch, T, NONE).astype(np.int32)
    lo = T.copy()
    for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): lo = np.minimum(lo, np.roll(np.roll(lo, dz, 0), dx, 1))
    F = np.minimum(np.minimum(T, now), lo) - 4
    S = np.full(T.shape, S_FOREST, np.uint8)
    write_grid(os.path.join(OUT, "garden_terrain.bin"), gr["x1"], gr["z1"], H, F, np.full(T.shape, NONE, np.int32), S, np.full(T.shape, R_STONE, np.uint8), np.zeros(T.shape, np.uint8))
    return int(touch.sum())

# ---------------------------------------------------------------- plan, data files, main
def plan_png(gr, rl, b, meta, path):
    from PIL import Image, ImageDraw
    S = 3; x1, z1, x2, z2 = PLACE; w, h = (x2 - x1 + 1) * S, (z2 - z1 + 1) * S
    img = Image.new("RGB", (w, h + 60), (20, 20, 24)); d = ImageDraw.Draw(img)
    T = rl["T"]
    tops = {}
    for (x, y, z), s in b.v.items():
        if s == "minecraft:air": continue
        if y >= tops.get((x, z), (-999, ""))[0]: tops[(x, z)] = (y, s)
    for i in range(T.shape[0]):
        for j in range(T.shape[1]):
            x, z = j + x1, i + z1; g = int(np.clip((T[i, j] - 55) * 2.6, 0, 255))
            col = (g // 2 + 30, g // 2 + 40, g // 2 + 30)
            if gr["water"][i, j] != NONE: col = (40, 70, 160)
            t = tops.get((x, z))
            if t:
                s = t[1]
                if "leaves" in s: col = (150, 160, 150)
                if "pale_oak_log" in s or "heart" in s: col = (70, 66, 60)
                if "cobble" in s or "brick" in s: col = (200, 170, 90)
                if "glass" in s or "iron_bars" in s or "stripped" in s: col = (210, 220, 230)
                if "planks" in s or "pale_oak_stairs" in s: col = (220, 190, 150)
            if not gr["place"][i, j]: col = tuple(v // 3 for v in col)
            d.rectangle([j * S, i * S, j * S + S - 1, i * S + S - 1], fill=col)
    d.ellipse([(OCX - R_SCULPT - x1) * S, (OCZ - R_SCULPT - z1) * S, (OCX + R_SCULPT - x1) * S, (OCZ + R_SCULPT - z1) * S], outline=(255, 200, 80))
    for hp in meta["hearts"]:
        cx, cz = (hp["x"] - x1) * S, (hp["z"] - z1) * S; d.ellipse([cx - 6, cz - 6, cx + 6, cz + 6], outline=(255, 60, 40), width=3); d.text((cx + 8, cz - 6), "H%d %s" % (hp["id"], hp["kind"]), fill=(255, 120, 100))
    for f in meta["faces"]:
        cx, cz = (f["x"] + 1 - x1) * S, (f["z"] + 1 - z1) * S; d.rectangle([cx - 4, cz - 4, cx + 4, cz + 4], outline=(200, 120, 255), width=2); d.text((cx + 6, cz - 6), "F%d" % f["id"], fill=(210, 160, 255))
    for s in meta["sensors"]:
        cx, cz = (s["x"] - x1) * S, (s["z"] - z1) * S; d.ellipse([cx - 4, cz - 4, cx + 4, cz + 4], fill=(60, 220, 230)); d.text((cx + 6, cz + 2), "S%d" % s["id"], fill=(120, 240, 240))
    for (x, y, z) in meta["blooms"]:
        d.point(((x - x1) * S + 1, (z - z1) * S + 1), fill=(255, 140, 40))
    d.rectangle([(CORE[0] - x1) * S, (CORE[1] - z1) * S, (CORE[2] + 1 - x1) * S, (CORE[3] + 1 - z1) * S], outline=(230, 60, 60), width=2)
    bx, bz = HEARTH4[0], HEARTH4[2]; d.ellipse([(bx - x1) * S - 6, (bz - z1) * S - 6, (bx - x1) * S + 6, (bz - z1) * S + 6], fill=(255, 140, 0))
    d.text((6, h + 4), "T-025 Garden of Silence: plan (1 block = %d px, north up). Red = place core (+16 seam), yellow ring = sculpted circle r 60," % S, fill=(255, 255, 255))
    d.text((6, h + 20), "gold = path (house -> orangery), H = living faces (creaking hearts), F = carved faces, S = sculk sensors, orange dots = eyeblossoms,", fill=(255, 255, 255))
    d.text((6, h + 36), "orange disc = bonfire 4; base level %d, orangery floor %d, house floor %d" % (meta["base"], FY, FH), fill=(255, 255, 255))
    img.save(path)
def data_files(meta):
    from r1 import replace_lines
    replace_lines(os.path.join(ROOT, "zones/zones.txt"), ["garden_glass "], ["garden_glass    overworld box  %d %d %d  %d %d %d   # T-025: the orangery of the Garden of Silence (floor -4 .. crown)" %
                  (OX1, FY - 4, OZ1, OX2, meta["crown_top"], OZ2)])
    replace_lines(os.path.join(ROOT, "zones/zones.txt"), ["garden_house "], ["garden_house    overworld box  %d %d %d  %d %d %d   no_spawn   # T-025: the gardener's house (+2)" %
                  (HX1 - 2, FH - 3, HZ1 - 2, HX2 + 2, FH + 12, HZ2 + 2)])
    k = meta["key"]
    replace_lines(os.path.join(ROOT, "altars/keys.txt"), ["tear_creaker "], ["tear_creaker 1 %d,%d,%d Слеза Скрипуна" % (k[0], k[1], k[2])])
def main():
    gr = grids(); rl = relief(gr)
    b, hearts, heart_pts, face_pts, sens, blooms, sites = blocks(gr, rl)
    nair = surface(b, gr, rl)
    from connect import connect
    connect(b)
    bad = [k for k in b.v if not in_place(k[0], k[2])]
    if bad: raise SystemExit("blocks outside the place: %s" % bad[:5])
    for k in [k for k, v in b.v.items() if gr["allow"][ix(gr, k[0], k[2])] and ("leaves" in v or "pale_oak_log" in v or "hanging_moss" in v)]: del b.v[k]
    # tree parts that reach into the wanted ground (low branches and leaves on a slope, the trunk over the higher side of a slope): the
    # ground stays (else the apply writes the ground, the blocks replace its top and a re-run sees a lower ground there)
    T0 = rl["T"]
    for k in [k for k, v in b.v.items() if ("leaves" in v or "pale_oak_log" in v or "hanging_moss" in v) and not in_built(k[0], k[2]) and k[1] <= T0[ix(gr, k[0], k[2])]]: del b.v[k]
    pad = [k for k in b.v if gr["allow"][ix(gr, k[0], k[2])]]
    if pad: raise SystemExit("blocks on the pad / approach of bonfire 4: %s" % pad[:5])
    ncol = write_terrain(gr, rl, b)
    n = b.write_placements(os.path.join(OUT, "garden.txt"))
    crown = max(y for (x, y, z), s in b.v.items() if "leaves" in s and abs(x - OCX) < 14 and abs(z - OCZ) < 14)
    meta = dict(base=int(round(rl["base"])), floor=FY, house_floor=FH, orangery=[OX1, OZ1, OX2, OZ2], trunk=list(TRUNK), key=[PED[0], FY + 1, PED[1]],
                pedestal=[PED[0], FY, PED[1]], house=[HX1, HZ1, HX2, HZ2], door=[HDOOR[0], FH + 1, HDOOR[1]], stand=[STAND[0], FH + 1, STAND[1]],
                lectern=[LECTERN[0], FH + 1, LECTERN[1]], hearth=list(HEARTH4), path=[[c[0], c[1], s2 / 2] for c, s2 in zip(rl["cells"], rl["prof"])],
                hearts=heart_pts, faces=face_pts, sensors=sens, blooms=blooms, crown_top=crown + 2, terrain_columns=ncol, blocks=n, air=nair,
                trees=len(sites), entry=list(rl["entry"]))
    import garden_dp
    garden_dp.run(sys.modules[__name__], meta)
    data_files(meta)
    json.dump(meta, open(os.path.join(OUT, "garden.json"), "w"), ensure_ascii=False)
    os.makedirs(os.path.join(ROOT, "docs/reports/T-025"), exist_ok=True)
    plan_png(gr, rl, b, meta, os.path.join(ROOT, "docs/reports/T-025/garden_plan.png"))
    print(f"garden: terrain {ncol} columns, {n} blocks (air {nair}), trees {len(sites)}, hearts {len(heart_pts)}, faces {len(face_pts)}, sensors {len(sens)}, eyeblossoms {len(blooms)}, base {rl['base']:.0f}, path {len(rl['cells'])} cells")
if __name__ == "__main__": main()
