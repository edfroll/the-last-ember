#!/usr/bin/env python3
"""T-027: the Cemetery of the Fallen Knights and the Keeper's Lodge (Р1) on the places `cemetery` (rect 152x152 round (200,450)) and
`lodge` (rect 32x28 round (100,445)) of tools/build/r1_plots.txt, both + 16 of seam.

  python3 tools/build/r1_cemetery.py         -> server/build/r1/cemetery_terrain.bin (tools/terrain.sh apply), cemetery.txt (tools/blockwriter.sh
                                                apply), cemetery.json (points for the tests, the bot and the datapack), docs/reports/T-027/
                                                cemetery_plan.png + lodge_plan.png, structure/cemetery/*.nbt, datapack function/cemetery/gen/*
                                                (tools/build/cemetery_dp.py), zones, the collapse traps and the crypt trap
  python3 tools/build/r1_cemetery.py plan    only the plans
  python3 tools/build/r1_cemetery.py paths   search the descent and the hill stair again (tools/build/cemetery_paths.json)
Inputs: server/build/r1/base.bin (the ground before the R1 frame), terrain.bin (the frame), cemetery_pre.bin (scan of both places now),
        allow.npz (r1.py: the pad of bonfire 2 with its slopes and the approach; only the pad itself is never written here - its slopes
        and the end of the approach inside the places are rebuilt: the lodge terrace and the gate of the descent stand on them).

Layout (HQ T-027, 1: the relief of seed 10845): W = the 30th percentile of the floor of the hollow. The floor stays natural in W-2..W+6
(pits filled to W-2, bumps cut by at most 6); the slopes of the mountain and of the ridge stay natural except where the descent, the
barrows, the crypt and the hill stair are cut into them. The descent: flights of 8..12 stairs with landings from the gate at the pad
of bonfire 2 down the west slope (a beam search, cemetery_plan.py). The lodge: one terrace at 196 (bonfire 192 + 4) cut into the shoulder
west of the pad, retaining walls <= 10; the stream between the yard and the road. Re-run: the same place, 0 columns changed."""
import json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import Scan, write_grid, NONE
from lib import B, Mix, h as hsh
import cemetery_plan as P
from cemetery_plan import ix, DIRS, BACK

ROOT = P.ROOT; OUT = P.OUT
DP = os.path.join(ROOT, "datapack/data/last_ember")
S_FOREST = 2
R_STONE = 0
# ---------------------------------------------------------------- the lodge (card: plot 32x28, house 13x11, shed 7x5)
TER_Y = 196                                # the terrace: ground top (feet 197), bonfire 192 + 4
TERRACE = (98, 431, 110, 455)              # x1 z1 x2 z2
HOUSE = (100, 438, 110, 450)               # 11 (x) x 13 (z); door north to the yard, back door south to the garden, the window on the cemetery east
SHED = (100, 451, 106, 455)                # 7 x 5, door west (from the strip x 98..99 along the house)
GARDEN = (107, 451, 110, 455)
STREAM = (111, 112)                        # the channel x, from the spring (z 428) to the pool (z 437..441)
ROAD_X = (114, 116)                        # the road (x 113 is the curb of the stream)
BRIDGE_Z = (434, 435)

def relief(gr, W, paths):
    """T (ground top per column), walk {(x, z): (y, kind, stairs facing)}, ring {(x, z): ('wall'|'parapet', y)} and the masks"""
    bf = gr["before"]; X, Z = gr["X"], gr["Z"]
    T = bf.copy()
    fl, holes = P.floor_mask(gr, W)
    T = np.where(fl, np.maximum(bf, W - 2), T)
    T = np.where(holes, np.maximum(bf - 6, W + 6), T)
    walk = {}
    def add_path(cells):
        for (x, z, y, dr, k) in cells:
            if k == "L":
                for a in (-1, 0, 1):
                    for c in (-1, 0, 1):
                        q = (x + a, z + c)
                        if P.on_pad(*q): continue
                        if q not in walk or walk[q][1] == "L": walk[q] = (min(y, walk[q][0]) if q in walk else y, "L", None)
        for (x, z, y, dr, k) in cells:
            if k == "S":
                for q in P.foot((x, z), dr): walk[q] = (y, "S", BACK[dr])
    add_path(paths["desc"]); add_path(paths["hill"])
    L = paths["hill_level"]
    for x in range(P.HILL[0], P.HILL[2] + 1):
        for z in range(P.HILL[1], P.HILL[3] + 1): walk[(x, z)] = (L, "P", None)
    gate = [(x, z) for (x, z) in walk if x <= P.PAD[2] + 3 and P.PAD[1] <= z <= P.PAD[3]]
    for (x, z), (y, k, f) in walk.items(): T[ix(gr, x, z)] = y
    # the ring round the walks: cut faces (retaining walls) and fill with a parapet; then the 1:1 embankment
    ring = {}
    nbrs = {}
    for (x, z), (y, k, f) in walk.items():
        for a in (-1, 0, 1):
            for c in (-1, 0, 1):
                q = (x + a, z + c)
                if q in walk or P.on_pad(*q): continue
                nbrs.setdefault(q, []).append(y)
    for q, ys in nbrs.items():
        i, j = ix(gr, *q); top = max(ys); nat = int(T[i, j])
        if nat >= top + 1: ring[q] = ("wall", top)
        else:
            T[i, j] = top; ring[q] = ("parapet", top) if nat < top - 1 or any(v < top for v in ys) else ("edge", top)
    emb = np.full(T.shape, -999)
    for (x, z), (kind, y) in ring.items():
        if kind != "wall": emb[ix(gr, x, z)] = y
    for (x, z), (y, k, f) in walk.items(): emb[ix(gr, x, z)] = max(emb[ix(gr, x, z)], y)
    for _ in range(14):
        p = np.pad(emb, 1, constant_values=-999); m = emb.copy()
        for dz in (0, 1, 2):
            for dx in (0, 1, 2): m = np.maximum(m, p[dz:dz + emb.shape[0], dx:dx + emb.shape[1]] - 1)
        emb = m
    raise_ = gr["place"] & ~gr["pad"] & (emb > T)
    T = np.where(raise_, emb, T)
    return dict(T=T, walk=walk, ring=ring, floor=fl, holes=holes, gate=gate)

def barrow_relief(gr, rl, W):
    """the mounds of the 5 barrows (flat top E+6, the dromos trench at E, its walls stepping down to the front) + 1:1 round them"""
    T = rl["T"]; out = []
    for b in P.BARROWS:
        cells = P.barrow_cells(b); (fx, fz), f = P.barrow_front(b)
        E = int(T[ix(gr, fx, fz)])
        top = {}
        for (x, z), (lx, lz) in cells.items():
            if lz <= 8: m = E + 6
            elif 3 <= lx <= 5: m = E
            elif lx in (2, 6): m = E + 5 - (lz - 9)
            else: m = E + 4 - (lz - 9)
            if lx == 1 and 4 <= lz <= 8: m = E                 # the shaft of the stair to the top (open)
            top[(x, z)] = m
        for (x, z), m in top.items():
            i, j = ix(gr, x, z); T[i, j] = m if (m <= E or cells[(x, z)][1] > 8 or (cells[(x, z)][0] == 1 and 4 <= cells[(x, z)][1] <= 8)) else max(int(T[i, j]), m)
        # 1:1 round the mound (fill only)
        emb = np.full(T.shape, -999)
        for (x, z), m in top.items(): emb[ix(gr, x, z)] = T[ix(gr, x, z)] if m > E else -999
        for _ in range(8):
            p = np.pad(emb, 1, constant_values=-999); mm = emb.copy()
            for dz in (0, 1, 2):
                for dx in (0, 1, 2): mm = np.maximum(mm, p[dz:dz + emb.shape[0], dx:dx + emb.shape[1]] - 1)
            emb = mm
        sel = gr["place"] & (emb > T)
        for (x, z) in cells: sel[ix(gr, x, z)] = False
        # keep the trench in front of the dromos open: the cells in front stay on the floor
        dx, dz = DIRS[f]
        for k in range(1, 5):
            for a in (-2, -1, 0, 1, 2):
                q = (fx + dx * (k - 1) - dz * a, fz + dz * (k - 1) + dx * a)
                sel[ix(gr, *q)] = False
                if T[ix(gr, *q)] > E: T[ix(gr, *q)] = E
        T[sel] = emb[sel]
        out.append(dict(id=b[0], E=E, facing=f, front=[fx, fz], cells=cells))
    return out

CRYPT_FAC = (233, 247)                     # x range of the facade (the skulls stand in front of it)
def crypt_relief(gr, rl, W):
    T = rl["T"]; E = W                     # the threshold block level (feet W+1)
    for x in range(CRYPT_FAC[0] - 2, CRYPT_FAC[1] + 3):
        for z in range(P.CRYPT_FRONT + 1, P.CRYPT_FRONT + 6): T[ix(gr, x, z)] = E
    # the exit of the hall (after the victory) comes out at the foot west of the facade
    for x in range(225, 232):
        for z in range(P.CRYPT_FRONT + 1, P.CRYPT_FRONT + 5): T[ix(gr, x, z)] = E
    return E

def chapel_relief(gr, rl):
    T = rl["T"]; x1, z1, x2, z2 = P.CHAPEL
    vals = [int(T[ix(gr, x, z)]) for x in range(x1, x2 + 1) for z in range(z1, z2 + 1)]
    y = int(round(np.median(vals)))
    for x in range(x1 - 1, x2 + 2):
        for z in range(z1 - 1, z2 + 2): T[ix(gr, x, z)] = y
    return y

def grave_relief(gr, rl):
    T = rl["T"]; out = []
    for (n, x, z, kind, ep) in P.GRAVES:
        y = int(T[ix(gr, x, z)])
        for (a, c) in ((0, -1), (0, 0), (0, 1), (-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1), (0, 2), (-1, 2), (1, 2)): T[ix(gr, x + a, z + c)] = y
        out.append(dict(n=n, x=x, z=z, y=y, kind=kind, ep=ep))
    return out

def lodge_relief(gr, rl):
    """the terrace at 196 (house, yard, shed, garden), the stream channel, the road from the approach to the pad (half blocks)"""
    T = rl["T"]
    x1, z1, x2, z2 = TERRACE
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1): T[ix(gr, x, z)] = TER_Y
    # the stream: bottoms (the water stands 1 over them): 429..431 water 196, 432..436 water 195, 437..441 water 193 (the pool)
    stream = {}
    for z in range(428, 442):
        w = 196 if z <= 431 else (195 if z <= 434 else (193 if z <= 437 else 191))
        for x in STREAM: stream[(x, z)] = w; T[ix(gr, x, z)] = w - 1
    # the road: from the approach of T-022 at (108, 425) round to x 114 and down to the pad at z 442; levels in half blocks
    pts = [(108, 425), (109, 426), (110, 427), (111, 427), (112, 427), (113, 427), (114, 428), (115, 429)] + [(115, z) for z in range(430, 442)]
    y0 = int(gr["live"][ix(gr, 108, 425)]) if "live" in gr else int(gr["before"][ix(gr, 108, 425)]); y_end = P.PAD_Y   # the trail as it is in the world
    n = len(pts); s0 = 2 * y0 + 2; s1 = 2 * y_end + 2          # feet levels x2
    # the bridge at z 434..435 must be level with the terrace (feet 197 -> s 394)
    kb = pts.index((115, BRIDGE_Z[0]))
    prof = []
    for k in range(n):
        if k <= kb: v = int(round(s0 + (2 * (TER_Y + 1) - s0) * k / kb))
        else: v = 2 * int(round((2 * (TER_Y + 1) + (s1 - 2 * (TER_Y + 1)) * (k - kb) / (n - 1 - kb)) / 2))   # whole blocks: stairs
        prof.append(v)
    for k in range(1, n):                      # half a block per step (slabs), a whole block only as a stair between whole blocks
        dd = abs(prof[k] - prof[k - 1])
        if dd > 2 or (dd == 2 and prof[k] % 2): raise SystemExit("lodge road: a step a bot cannot walk at %s" % (pts[k],))
    road = {}; up = {}
    for k, ((x, z), s2) in enumerate(zip(pts, prof)):
        lower = k + 1 < n and prof[k] - prof[k + 1] == 2
        if lower:
            nx, nz = pts[k + 1]; f = {(0, 1): "north", (0, -1): "south", (1, 0): "west", (-1, 0): "east"}[(nx - x, nz - z)]
        for a in (-1, 0, 1):
            q = (x + a, z) if z >= 429 else (x, z + a)
            if q in stream or P.on_pad(*q) or q in road: continue
            road[q] = s2
            if lower: up[q] = f
            T[ix(gr, *q)] = (s2 - 1) // 2 if s2 % 2 else s2 // 2 - 1
    return dict(stream=stream, road_list=list(road.items()), roadset=set(road), road_up=up)

# ---------------------------------------------------------------- trees (our own repeatable models instead of the spruces)
def dark_oak(b, c, x, z, salt):
    y = c.g(x, z); hgt = 6 + int(hsh(x, 0, z, salt) * 4)
    for yy in range(y + 1, y + hgt + 1):
        for (a, d) in ((0, 0), (1, 0), (0, 1), (1, 1)): b.set(x + a, yy, z + d, "minecraft:dark_oak_log[axis=y]")
    cy = y + hgt
    for a in range(-3, 5):
        for d in range(-3, 5):
            for e in (0, 1, 2):
                r = abs(a - 0.5) + abs(d - 0.5) + e * 1.6
                if r <= 5.2 - hsh(x + a, cy + e, z + d, salt) * 1.6 and b.get(x + a, cy + e, z + d) in (None, "minecraft:air"):
                    b.set(x + a, cy + e, z + d, "minecraft:dark_oak_leaves[distance=1,persistent=true,waterlogged=false]")
def pale_oak(b, c, x, z, salt):
    y = c.g(x, z); hgt = 5 + int(hsh(x, 1, z, salt) * 4)
    for yy in range(y + 1, y + hgt + 1): b.set(x, yy, z, "minecraft:pale_oak_log[axis=y]")
    for (a, d, yy) in ((1, 0, hgt - 2), (-1, 0, hgt - 1), (0, 1, hgt - 3)):
        b.set(x + a, y + yy, z + d, "minecraft:pale_oak_log[axis=%s]" % ("x" if a else "z"))
    cy = y + hgt
    for a in range(-2, 3):
        for d in range(-2, 3):
            for e in (-1, 0, 1):
                if abs(a) + abs(d) + abs(e) <= 3 and hsh(x + a, cy + e, z + d, salt) < 0.8 and b.get(x + a, cy + e, z + d) in (None, "minecraft:air"):
                    b.set(x + a, cy + e, z + d, "minecraft:pale_oak_leaves[distance=1,persistent=true,waterlogged=false]")
            if abs(a) + abs(d) == 2 and hsh(x + a, 9, z + d, salt) < 0.4 and b.get(x + a, cy - 2, z + d) in (None, "minecraft:air"):
                b.set(x + a, cy - 2, z + d, "minecraft:pale_hanging_moss[tip=true]")

# ---------------------------------------------------------------- build
def build(gr, W, paths):
    import cemetery_build as CB, cemetery_lodge as CL
    rl = relief(gr, W, paths)
    brs = barrow_relief(gr, rl, W)
    E = crypt_relief(gr, rl, W)
    chy = chapel_relief(gr, rl)
    gvs = grave_relief(gr, rl)
    lr = lodge_relief(gr, rl)
    c = CB.Ctx(gr, rl, W); b = B("cemetery")
    meta = dict(W=W)
    CB.walks(b, c)
    meta["gate"] = CB.gate(b, c)
    meta["lights"] = CB.lights(b, c, paths["desc"])
    L = paths["hill_level"]
    sw = CB.three_swords(b, c, L)
    stair = {cc[1]: cc[2] for cc in paths["hill"] if cc[4] == "S" and cc[0] == paths["hill"][2][0]}
    fall = next(s for s in sw if s["role"] == "fall")
    meta["sword_up"] = fall["cells"]; meta["sword_down"] = CB.fallen_sword(L, stair)
    for p, s in fall["cells"].items(): b.set(*p, s)
    # graves, barrows, crypt, chapel
    meta["graves"] = [CB.grave(b, c, gv) for gv in gvs]
    n_loot = {1: 2, 2: 1, 3: 1, 4: 1, 5: 1}
    meta["barrows"] = [CB.barrow(b, c, br, n_loot[br["id"]]) for br in brs]
    meta["crypt"] = CB.crypt(b, c, E, W)
    meta["chapel"] = CB.chapel(b, c, chy)
    cr = meta["crypt"]
    b.set(CB.CX + 6, E + 1, P.CRYPT_FRONT + 3, CB.st("lectern", facing="west", has_book="true", powered="false") +
          CB.book_nbt("Записка", "оруженосец", ["Сир велел запереть и зарыть ключ со мной. Сказал: я буду стоять, пока огонь не вернётся. Огонь прошёл мимо. Он стоит."]))
    hl = (P.HILL[0] - 2, L + 0, P.HILL[1] + 3)
    meta["hill_lectern"] = [P.HILL[0] + 1, L + 1, P.HILL[1] + 3]
    b.set(P.HILL[0] + 1, L + 1, P.HILL[1] + 3, CB.st("lectern", facing="west", has_book="true", powered="false") +
          CB.book_nbt("Записка", "", ["Три меча поставили те, кто шёл после них. Имена стёрлись. Мы их не знали."]))
    # the lodge
    meta["lodge"] = CL.build(b, c, sys.modules[__name__], lr)
    # what must stay free of the swords, the old graves and the fence
    taken = set(rl["walk"]) | set(rl["ring"])
    for gv in meta["graves"]:
        for a in (-2, -1, 0, 1, 2):
            for d in range(-3, 5): taken.add((gv["x"] + a, gv["z"] + d))
    for br in brs:
        for (x, z) in br["cells"]: taken.add((x, z))
        (fx, fz), f = br["front"], br["facing"]; dx, dz = DIRS[f]
        for k in range(0, 7):
            for a in (-3, -2, -1, 0, 1, 2, 3): taken.add((fx + dx * k - dz * a, fz + dz * k + dx * a))
    for x in range(CB.CX - 10, CB.CX + 11):
        for z in range(P.CRYPT_FRONT - 2, P.CRYPT_FRONT + 9): taken.add((x, z))
    for x in range(222, 233):
        for z in range(P.CRYPT_FRONT - 1, P.CRYPT_FRONT + 7): taken.add((x, z))
    x1, z1, x2, z2 = P.CHAPEL
    for x in range(x1 - 3, x2 + 4):
        for z in range(z1 - 3, z2 + 4): taken.add((x, z))
    for x in range(P.HILL[0] - 3, P.HILL[2] + 4):
        for z in range(P.HILL[1] - 3, P.HILL[3] + 4): taken.add((x, z))
    desc_cells = [(cc[0], cc[1]) for cc in paths["desc"]]
    # the small swords
    swords = P.sword_sites(gr, W, rl["floor"], taken, desc_cells)
    for (x, z, hh) in swords:
        CB.small_sword(b, c, x, z, hh, 7100); taken |= {(x + a, z + d) for a in (-1, 0, 1) for d in (-1, 0, 1)}
    meta["swords"] = swords
    # old graves: 24 stones on the floor and along the descent, 8 of them with a stand in rusty armour (the datapack)
    sites = []
    for z in range(P.CEM[1] + 6, P.CEM[3] - 4, 5):
        for x in range(P.CEM[0] + 6, P.CEM[2] - 4, 5):
            xx = x + int(hsh(x, 0, z, 7110) * 3); zz = z + int(hsh(x, 1, z, 7111) * 3)
            i, j = ix(gr, xx, zz)
            if not (rl["floor"][i, j] or any(abs(xx - a) + abs(zz - d) <= 4 for (a, d) in desc_cells[::2])): continue
            if any((xx + a, zz + d) in taken for a in (-1, 0, 1) for d in (-1, 0, 1, 2, 3)): continue
            if abs(int(rl["T"][i, j]) - int(rl["T"][i + 2, j])) > 1: continue
            if hsh(xx, 2, zz, 7112) < 0.55: continue
            sites.append((xx, zz)); taken |= {(xx + a, zz + d) for a in (-1, 0, 1) for d in (-1, 0, 1, 2, 3)}
    sites = sites[:24]
    stands = set(sorted(range(len(sites)), key=lambda k: hsh(sites[k][0], 3, sites[k][1], 7113))[:8])
    meta["stands"] = CB.old_graves(b, c, [(x, z, k in stands) for k, (x, z) in enumerate(sites)])
    # the fence: the floor's edge where the slopes start (+ across the east opening, with 2 breaches); gaps at every way in
    fl = rl["floor"]; fcells = []
    H_, W_ = fl.shape
    for i in range(1, H_ - 1):
        for j in range(1, W_ - 1):
            if not fl[i, j]: continue
            x, z = j + gr["x1"], i + gr["z1"]
            if not (P.CEM[0] + 2 <= x <= P.CEM[2] - 3 and P.CEM[1] <= z <= P.CEM[3] - 2): continue
            if any((not fl[i + a, j + d]) and rl["T"][i + a, j + d] > rl["T"][i, j] + 1 for a, d in ((1, 0), (-1, 0), (0, 1), (0, -1))): fcells.append((x, z))
    for z in range(P.CEM[1], P.CEM[3] + 1):
        i, j = ix(gr, P.CEM[2] - 3, z)
        if fl[i, j]: fcells.append((P.CEM[2] - 3, z))
    breach = set()
    east = sorted(z for (x, z) in fcells if x == P.CEM[2] - 3)
    if east:
        for zc in (east[len(east) // 4], east[3 * len(east) // 4]):
            for d in range(-2, 3): breach.add((P.CEM[2] - 3, zc + d))
    gaps = breach | {q for q in taken if q not in set((s[0], s[1]) for s in swords)}
    meta["fence"] = CB.fence(b, c, sorted(set(fcells)), gaps)
    meta["breaches"] = sorted(breach)
    # trees: where the old trees stood (base.bin), our dark and pale oaks, away from everything built
    tr = gr["trees"]; X, Z = gr["X"], gr["Z"]; T = rl["T"]
    nt = 0
    for z in range(P.BOX[1] + 4, P.BOX[3] - 4, 6):
        for x in range(P.BOX[0] + 4, P.BOX[2] - 4, 6):
            xx = x + int(hsh(x, 4, z, 7120) * 3); zz = z + int(hsh(x, 5, z, 7121) * 3)
            if not P.in_place(xx, zz) or P.rect_dist(P.CEM, xx, zz) > P.MARGIN - 4 and P.rect_dist(P.LODGE, xx, zz) > P.MARGIN - 4: continue
            i, j = ix(gr, xx, zz)
            if tr[i - 1:i + 2, j - 1:j + 2].max() < 5: continue
            if any((xx + a, zz + d) in taken for a in range(-4, 5) for d in range(-4, 5)): continue
            if P.rect_dist(P.LODGE, xx, zz) <= 3 or abs(xx - 120) < 12 and abs(zz - 448) < 12: continue
            if np.abs(T[i - 1:i + 3, j - 1:j + 3] - T[i, j]).max() > 2 or gr["allow"][i, j] and P.rect_dist(P.CEM, xx, zz) > 0 and P.rect_dist(P.LODGE, xx, zz) > 0: continue
            (dark_oak if hsh(xx, 6, zz, 7122) < 0.6 else pale_oak)(b, c, xx, zz, 7123 + (xx * 7 + zz) % 31); nt += 1
            taken |= {(xx + a, zz + d) for a in range(-3, 4) for d in range(-3, 4)}
    meta["trees"] = nt
    return b, c, rl, lr, meta

PAL_FLOOR = None
def surface(b, c, gr, rl, lr):
    """every column of the places (not the pad): the changed ground gets the palette of the card on top (2 of dirt under), the old trees
    and the snow layers go (air from the ground to what stood there where nothing of ours is)"""
    import cemetery_build as CB
    T = rl["T"]; bf = gr["before"]; n = 0
    for i in range(T.shape[0]):
        for j in range(T.shape[1]):
            if not gr["place"][i, j] or gr["pad"][i, j]: continue
            x, z = j + gr["x1"], i + gr["z1"]; y = int(T[i, j])
            changed = y != int(gr["live"][i, j]) if "live" in gr else y != int(bf[i, j])
            if b.get(x, y, z) is None:
                if rl["floor"][i, j] or rl["holes"][i, j] or changed or y != int(bf[i, j]):
                    nb = [T[i + a, j + d] for a, d in ((1, 0), (-1, 0), (0, 1), (0, -1))]
                    steep = max(abs(v - y) for v in nb) >= 3
                    b.set(x, y, z, CB.WALLB.at(x, y, z) if steep and not rl["floor"][i, j] else CB.GROUND.at(x, y, z))
                    for k in (1, 2):
                        if b.get(x, y - k, z) is None: b.set(x, y - k, z, "minecraft:dirt" if not steep else "minecraft:stone")
            top = max(int(gr["top"][i, j]) if "top" in gr else y + 1, y + 1)
            for yy in range(y + 1, min(top, y + 48) + 1):
                if b.get(x, yy, z) is None: b.set(x, yy, z, "minecraft:air"); n += 1
    return n

def unsnow(b, gr, rl):
    """HQ T-027, 1: no snow in the places (snow blocks and powder snow under the ground: dirt within 3, stone deeper; snow layers: air),
    no spruces (air: our trees stand elsewhere); read from the world (tools/build/fens_scan.py's reader)"""
    import fens_scan, cemetery_build as CB
    T = rl["T"]; n = 0
    box = P.BOX
    for (x, y, z, nm) in fens_scan.scan(os.path.join(ROOT, "server/world"), box=box, inside=lambda x, z: bool(P.in_place(x, z)) and not P.on_pad(x, z)):
        if b.get(x, y, z) is not None: continue
        g = int(T[ix(gr, x, z)])
        if nm in ("minecraft:snow_block", "minecraft:powder_snow") and y <= g:
            b.set(x, y, z, (CB.GROUND.at(x, y, z) if y == g else "minecraft:dirt") if y >= g - 3 else "minecraft:stone")
        else: b.set(x, y, z, "minecraft:air")
        n += 1
    return n

KIND_SKIP = None
def write_terrain(gr, rl, b):
    """only the columns whose scan is not yet what it should be (a re-run on the built place rewrites nothing)"""
    import r1_fens as RF
    T = rl["T"]; Wt = np.full(T.shape, NONE, np.int32)
    now, nw = gr["live"], gr["lwater"]
    cols = {}
    for (x, y, z), s_ in b.v.items(): cols.setdefault((x, z), {})[y] = s_
    cand = gr["place"] & ~gr["pad"]
    touch = np.zeros(T.shape, bool)
    for i, j in zip(*np.nonzero(cand)):
        x, z = j + gr["x1"], i + gr["z1"]
        eg, ew = RF.expected_scan(T, Wt, cols, x, z, i, j)
        if now[i, j] != eg or nw[i, j] != ew: touch[i, j] = True
    H = np.where(touch, T, NONE).astype(np.int32)
    lo = T.copy()
    for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): lo = np.minimum(lo, np.roll(np.roll(lo, dz, 0), dx, 1))
    F = np.minimum(np.minimum(T, now), lo) - 4
    S = np.full(T.shape, S_FOREST, np.uint8)
    write_grid(os.path.join(OUT, "cemetery_terrain.bin"), gr["x1"], gr["z1"], H, F, np.full(T.shape, NONE, np.int32), S, np.full(T.shape, R_STONE, np.uint8), np.zeros(T.shape, np.uint8))
    return int(touch.sum())

# ---------------------------------------------------------------- plans, data files, main
def plan_png(gr, rl, b, meta, path, box, S, title):
    from PIL import Image, ImageDraw
    x1, z1, x2, z2 = box; w, h = (x2 - x1 + 1) * S, (z2 - z1 + 1) * S
    img = Image.new("RGB", (w, h + 76), (20, 20, 24)); d = ImageDraw.Draw(img)
    T = rl["T"]; W = meta["W"]
    tops = {}
    for (x, y, z), s in b.v.items():
        if s == "minecraft:air" or not (x1 <= x <= x2 and z1 <= z <= z2): continue
        if y >= tops.get((x, z), (-999, ""))[0]: tops[(x, z)] = (y, s)
    for z in range(z1, z2 + 1):
        for x in range(x1, x2 + 1):
            i, j = ix(gr, x, z); y = int(T[i, j])
            g = int(np.clip(60 + (y - W) * 1.6, 30, 250)); col = (g // 2 + 20, g // 2 + 35, g // 2 + 20)
            if rl["floor"][i, j]: col = (95, 105, 80) if y <= W + 2 else (110, 118, 90)
            t = tops.get((x, z))
            if t:
                s = t[1].split("[")[0].split("{")[0]
                if "stairs" in s or "stone_brick" in s: col = (200, 180, 120)
                if "wall" in s and "sign" not in s: col = (150, 150, 160)
                if "soul_soil" in s: col = (120, 70, 40)
                if "candle" in s: col = (255, 220, 120)
                if "leaves" in s: col = (60, 90, 55)
                if "deepslate" in s or "skull" in s or "bone" in s: col = (70, 70, 85)
                if "water" in s: col = (50, 90, 170)
                if "spruce" in s or "planks" in s or "door" in s: col = (170, 120, 70)
                if "cobblestone" in s and "wall" not in s: col = (140, 140, 140)
                if "lantern" in s: col = (255, 200, 60)
            if not gr["place"][i, j]: col = tuple(v // 3 for v in col)
            d.rectangle([(x - x1) * S, (z - z1) * S, (x - x1) * S + S - 1, (z - z1) * S + S - 1], fill=col)
    def lab(x, z, t, c=(255, 255, 255)): d.text(((x - x1) * S + 3, (z - z1) * S - 5), t, fill=c)
    for r, c_ in ((P.CEM, (230, 60, 60)), (P.LODGE, (230, 160, 60))):
        d.rectangle([(r[0] - x1) * S, (r[1] - z1) * S, (r[2] + 1 - x1) * S, (r[3] + 1 - z1) * S], outline=c_, width=2)
    for gv in meta["graves"]:
        cc = {"right": (80, 255, 120), "thane": (80, 200, 255), "wrong": (255, 120, 80), "pit": (255, 60, 255)}[gv["kind"]]
        d.ellipse([(gv["x"] - x1) * S - 4, (gv["z"] - z1) * S - 4, (gv["x"] - x1) * S + 4 + S, (gv["z"] - z1) * S + 4 + S], outline=cc, width=2); lab(gv["x"] + 1, gv["z"], str(gv["n"]), cc)
    for br in meta["barrows"]: lab(br["door"][0], br["door"][1], "B%d" % br["id"], (255, 255, 120))
    cr = meta["crypt"]; hx1, _, hz1, hx2, _, hz2 = cr["hall"]
    d.rectangle([(hx1 - x1) * S, (hz1 - z1) * S, (hx2 + 1 - x1) * S, (hz2 + 1 - z1) * S], outline=(160, 160, 255), width=2); lab(hx1 + 1, hz1 + 2, "hall (y %d)" % cr["HF"], (180, 180, 255))
    c0 = cr["corridor"]; d.rectangle([(c0[0] - x1) * S, (c0[2] - z1) * S, (c0[3] + 1 - x1) * S, (c0[5] + 1 - z1) * S], outline=(160, 160, 255), width=2)
    for (px, py, pz) in cr["exit_path"][::4]: d.point(((px - x1) * S + S // 2, (pz - z1) * S + S // 2), fill=(160, 160, 255))
    lab(cr["door"][0], cr["door"][2] + 3, "Crypt", (180, 180, 255))
    ch = meta["chapel"]; lab(ch["tree"][0] - 3, ch["tree"][2] - 8, "chapel", (220, 220, 220))
    lab(P.HILL[0] + 2, P.HILL[1] + 8, "Hill y%d" % meta["hill_level"], (255, 230, 150))
    for (x, z, hh) in meta["swords"]: d.rectangle([(x - x1) * S, (z - z1) * S, (x - x1) * S + S, (z - z1) * S + S], fill=(220, 220, 230))
    gx, gy, gz = meta["gate"]; lab(gx, gz - 3, "gate", (255, 200, 80))
    bx, bz = P.HEARTH2[0], P.HEARTH2[2]; d.ellipse([(bx - x1) * S - 5, (bz - z1) * S - 5, (bx - x1) * S + 5, (bz - z1) * S + 5], fill=(255, 140, 0))
    for k, t in enumerate(title): d.text((6, h + 4 + 16 * k), t, fill=(255, 255, 255))
    img.save(path)

def data_files(meta, W):
    from r1 import replace_lines
    Z = os.path.join(ROOT, "zones/zones.txt")
    top = max(p[1] for p in list(meta["sword_up"].keys())) + 4
    x1, z1, x2, z2 = P.CEM
    lines = ["cemetery        overworld box  %d %d %d  %d %d %d   # T-027: the Cemetery of the Fallen Knights (W-30 .. the swords +4; adventure: only the graves by the shovel)" % (x1, W - 30, z1, x2, top, z2)]
    cb = meta["crypt"]["box"]
    lines.append("cemetery_crypt  overworld box  %d %d %d  %d %d %d   dungeon   # T-027: the crypt of the Magister" % tuple(cb))
    for br in meta["barrows"]:
        lines.append("cemetery_barrow_%d overworld box  %d %d %d  %d %d %d   dungeon   # T-027: barrow %d" % ((br["id"],) + tuple(br["box"]) + (br["id"],)))
    lx, ly, lz = meta["lodge"]["centre"]
    lines.append("lodge           overworld cyl %d %d 16 %d %d   no_spawn   # T-027: the Keeper's Lodge (r 16 round the house)" % (lx, lz, ly - 20, ly + 30))
    replace_lines(Z, ["cemetery ", "cemetery_crypt ", "cemetery_barrow_", "lodge "], lines)
    # the traps: the 2 pits (collapse), the crypt corridor (4 plates -> the arrows)
    TR = os.path.join(ROOT, "traps/traps.txt"); tl = []
    for gv in meta["graves"]:
        if gv["kind"] != "pit": continue
        tl.append("cem_pit_%d collapse overworld %d %d %d %d %d %d floor=minecraft:soul_soil   # T-027: the sunken grave %d" % (gv["n"], gv["x"], gv["y"] + 1, gv["z"], gv["x"], gv["y"] + 3, gv["z"] + 1, gv["n"]))
    cr = meta["crypt"]; c0 = cr["corridor"]
    tl.append("cem_arrows arrows overworld %d %d %d %d %d %d pts=%s   # T-027: the trap corridor of the crypt" % (c0[0], c0[1], c0[2], c0[3], c0[1] + 3, c0[5], ";".join("%d,%d,%d" % tuple(p) for p in cr["arrow_pts"])))
    for k, (x, y, z) in enumerate(cr["plates"], 1):
        tl.append("cem_plate_%d plate overworld %d %d %d %d %d %d link=cem_arrows   # T-027: plate %d of the crypt corridor" % (k, x, y, z, x, y + 1, z, k))
    replace_lines(TR, ["cem_pit_", "cem_arrows ", "cem_plate_"], tl)

def plan_main(gr=None):
    gr = gr or P.grids(); paths = P.load_paths(); W = paths["W"]
    return gr, paths, W

def main(plan_only=False):
    gr, paths, W = plan_main()
    if W != P.floor_level(gr): raise SystemExit("the floor level changed (%d -> %d): search the paths again (r1_cemetery.py paths)" % (W, P.floor_level(gr)))
    b, c, rl, lr, meta = build(gr, W, paths)
    meta["hill_level"] = paths["hill_level"]
    nair = surface(b, c, gr, rl, lr) if not plan_only else 0
    nsnow = unsnow(b, gr, rl) if not plan_only else 0
    from connect import connect
    connect(b)
    bad = [k for k in b.v if not P.in_place(k[0], k[2])]
    if bad: raise SystemExit("blocks outside the places: %s" % bad[:5])
    for k in [k for k in b.v if P.on_pad(k[0], k[2]) and k[1] > P.PAD_Y + 6]: del b.v[k]     # the eave of the house over the pad's edge
    pad = [k for k in b.v if P.on_pad(k[0], k[2])]
    if pad: raise SystemExit("blocks on the pad of bonfire 2: %s" % pad[:5])
    os.makedirs(os.path.join(ROOT, "docs/reports/T-027"), exist_ok=True)
    t1 = ["T-027 Cemetery of the Fallen Knights: plan (1 block = 3 px, north up). Red = place core, orange = the lodge; W = %d (floor), hill platform y %d" % (W, paths["hill_level"]),
          "descent: %d cells from the gate (bonfire 2, y %d) to the floor; green rings = right graves, blue = Thane, red = wrong, magenta = pits; B1..B5 barrows," % (len(paths["desc"]), P.PAD_Y),
          "blue boxes = crypt corridor (y %d) and hall (y %d), dots = its exit; white squares = small swords; brown = soul soil; grey = the fence" % (meta["crypt"]["C"], meta["crypt"]["HF"]),
          "the floor: light green; changed relief shown by height (darker = lower)"]
    plan_png(gr, rl, b, meta, os.path.join(ROOT, "docs/reports/T-027/cemetery_plan.png"), (P.CEM[0] - 20, P.CEM[1] - 20, P.CEM[2] + 16, P.CEM[3] + 16), 3, t1)
    t2 = ["T-027 Keeper's Lodge: plan (1 block = 8 px, north up). Orange = the place core; terrace y %d (bonfire 192 + 4), retaining walls <= 10;" % TER_Y,
          "house 11 x 13 (door north, window east on the cemetery), shed 7 x 5 (door west), garden; stream (blue) from the spring (z 427) to the pool and the crack;",
          "the footbridge z %d..%d from the wicket to the road; the road (x %d..%d) graded down to the pad of bonfire 2 (orange disc)" % (BRIDGE_Z[0], BRIDGE_Z[1], ROAD_X[0], ROAD_X[1])]
    plan_png(gr, rl, b, meta, os.path.join(ROOT, "docs/reports/T-027/lodge_plan.png"), (P.LODGE[0] - 8, P.LODGE[1] - 10, P.LODGE[2] + 14, P.LODGE[3] + 6), 8, t2)
    if plan_only: return meta
    ncol = write_terrain(gr, rl, b)
    n = b.write_placements(os.path.join(OUT, "cemetery.txt"))
    data_files(meta, W)
    out = {k: v for k, v in meta.items() if k not in ("sword_up", "sword_down")}
    out.update(terrain_columns=ncol, blocks=n, air=nair, snow=nsnow, desc=paths["desc"], hill=paths["hill"], hearth=list(P.HEARTH2), walk_levels=None)
    import cemetery_dp
    cemetery_dp.run(sys.modules[__name__], meta, out)
    json.dump(out, open(os.path.join(OUT, "cemetery.json"), "w"), ensure_ascii=False, default=lambda o: list(o) if isinstance(o, (set, tuple)) else str(o))
    print(f"cemetery: terrain {ncol} columns, {n} blocks (air {nair}, snow replaced {nsnow}), trees {meta['trees']}, swords {len(meta['swords'])}, fence {meta['fence']}, W {W}, hill {paths['hill_level']}")

if __name__ == "__main__" and sys.argv[1:2] == ["paths"]:
    P.search_paths(P.grids())
elif __name__ == "__main__" and sys.argv[1:2] == ["plan"]:
    main(plan_only=True)
elif __name__ == "__main__":
    main()
