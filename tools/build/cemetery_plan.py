"""T-027: the layout of the Cemetery of the Fallen Knights and the Keeper's Lodge (Р1): relief decisions, the descent from bonfire 2,
the stair of the Hill of Three Swords, the barrows, the crypt of the Magister, the chapel, the 16 fresh graves, the field of swords, the
fence, the lodge terraces. Read by tools/build/r1_cemetery.py (the blocks) - only planning here, nothing is written but the plan cache.

The descent and the hill stair are searched (a beam search over flights of 8..12 stairs with landings, turns on landings only, the
earth work |ground - level| minimised) and cached in tools/build/cemetery_paths.json (committed): `python3 tools/build/r1_cemetery.py
paths` searches them again. Everything else is computed from the ground before the place (base.bin + the R1 frame)."""
import json, math, os, struct, sys
from collections import deque
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import Scan, NONE
from lib import h as hsh

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "server/build/r1")
CEM = (124, 374, 276, 526)                 # the core of the place `cemetery` (rect 152x152 round (200,450))
LODGE = (84, 431, 116, 459)                # the core of the place `lodge` (rect 32x28 round (100,445))
MARGIN = 16
BOX = (58, 348, 302, 552)                  # the grids (both places with their seam + 10)
HEARTH2 = (118, 192, 448)
PAD = (111, 443, 125, 456)                 # the flat pad of bonfire 2 (T-022, 14 x 14 at y 191): never written (its rims are)
PAD_Y = 191
FLOOR_BOX = (160, 452, 276, 500)           # HQ T-027, 1: W = 30th percentile of the natural ground here
PATHS = os.path.join(ROOT, "tools/build/cemetery_paths.json")

def rect_dist(r, x, z):
    return np.hypot(np.maximum(np.maximum(r[0] - x, x - r[2]), 0), np.maximum(np.maximum(r[1] - z, z - r[3]), 0))
def in_cem(x, z): return rect_dist(CEM, x, z) <= MARGIN
def in_lodge(x, z): return rect_dist(LODGE, x, z) <= MARGIN
def in_place(x, z): return in_cem(x, z) | in_lodge(x, z)
def in_core(r, x, z): return (x >= r[0]) & (x <= r[2]) & (z >= r[1]) & (z <= r[3])
def on_pad(x, z): return PAD[0] <= x <= PAD[2] and PAD[1] <= z <= PAD[3]

def grids():
    x1, z1, x2, z2 = BOX; X, Z = np.meshgrid(np.arange(x1, x2 + 1), np.arange(z1, z2 + 1))
    def grid(s, a): return a[z1 - s.z0:z2 - s.z0 + 1, x1 - s.x0:x2 - s.x0 + 1].astype(np.int32)
    al = np.load(os.path.join(OUT, "allow.npz")); A = al["allow"]; ax0, az0 = int(al["x0"]), int(al["z0"])
    allow = A[z1 - az0:z2 - az0 + 1, x1 - ax0:x2 - ax0 + 1].copy()
    base = Scan(os.path.join(OUT, "base.bin"))
    nat = grid(base, base.ground)
    d = open(os.path.join(OUT, "terrain.bin"), "rb").read(); assert d[:4] == b"LETA"
    tx0, tz0, tw, th = struct.unpack("<4i", d[4:20]); TH = np.frombuffer(d, "<i2", tw * th, 20).reshape(th, tw).astype(np.int32)
    fr = TH[z1 - tz0:z2 - tz0 + 1, x1 - tx0:x2 - tx0 + 1]
    before = np.where(fr != NONE, fr, nat)            # the ground before the place: the same on every run
    trees = grid(base, base.top) - nat                # natural trees (base.bin: before the R1 frame)
    pad = (X >= PAD[0]) & (X <= PAD[2]) & (Z >= PAD[1]) & (Z <= PAD[3])
    gr = dict(X=X, Z=Z, x1=x1, z1=z1, before=before, nat=nat, allow=allow, pad=pad, place=in_place(X, Z), cem=in_core(CEM, X, Z),
              lodge=in_core(LODGE, X, Z), trees=trees)
    pre_path = os.path.join(OUT, "cemetery_pre.bin")
    if os.path.exists(pre_path):
        pre = Scan(pre_path); gr.update(live=grid(pre, pre.ground), top=grid(pre, pre.top), lwater=grid(pre, pre.water))
    return gr
def ix(gr, x, z): return z - gr["z1"], x - gr["x1"]
def B4(gr, x, z): return int(gr["before"][ix(gr, x, z)])

def floor_level(gr):
    x1, z1, x2, z2 = FLOOR_BOX; X, Z = gr["X"], gr["Z"]
    return int(round(np.percentile(gr["before"][(X >= x1) & (X <= x2) & (Z >= z1) & (Z <= z2)], 30)))
def flood(mask, seed):
    lab = np.zeros(mask.shape, bool); q = deque([seed]); lab[seed] = True
    while q:
        i, j = q.popleft()
        for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p, r = i + a, j + c
            if 0 <= p < mask.shape[0] and 0 <= r < mask.shape[1] and mask[p, r] and not lab[p, r]: lab[p, r] = True; q.append((p, r))
    return lab
def cheb_dist(src, n):
    d = np.where(src, 0, 999)
    for _ in range(n):
        p = np.pad(d, 1, constant_values=999); m = d.copy()
        for dz in (0, 1, 2):
            for dx in (0, 1, 2): m = np.minimum(m, p[dz:dz + d.shape[0], dx:dx + d.shape[1]] + 1)
        d = m
    return d
def floor_mask(gr, W):
    """the floor of the hollow: core ground <= W+6, connected to the middle of the floor; the bumps enclosed by it (ground <= W+12)
    belong to it (smoothed: at most 6 cut, not lower than W+6); the pits under W-2 are filled to W-2"""
    bf = gr["before"]; core = gr["cem"]
    f = flood(core & (bf <= W + 6), ix(gr, 230, 470))
    out = flood(~f, (0, 0))                                # everything reachable from outside without crossing the floor
    holes = ~f & ~out & core & (bf <= W + 12)
    return f, holes

# ---------------------------------------------------------------- flights: the descent and the hill stair
DIRS = {"E": (1, 0), "W": (-1, 0), "S": (0, 1), "N": (0, -1)}
LEFT = {"E": "N", "N": "W", "W": "S", "S": "E"}; RIGHT = {v: k for k, v in LEFT.items()}; BACK = {"E": "W", "W": "E", "N": "S", "S": "N"}
def foot(c, dr):
    dx, dz = DIRS[dr]; return [(c[0] - dz * k, c[1] + dx * k) for k in (-1, 0, 1)]
def search_flights(gr, start, y0, d0, ok, end_ok, beam=3000, depth=16, n_rng=(8, 12), lead=3, corridors=(0, 3, 6), length=None):
    """stair flights 3 wide going DOWN from `start` (block level y0 of the first landing, direction d0): landing 3 x 3 (straight, left,
    right or a U-turn 4 to the side), an optional flat run, then a flight of n stairs (each 1 lower; the first stair at the landing's
    level, the next landing 1 under the last stair: every step up is half a block or a stair). Cost: the earth work |ground - level| (cut cheaper than fill, both steeply penalised past 5 / 4). ok(x, z) = cell allowed;
    end_ok(x, z, y) = the walk may end on the floor there. Returns cells [(x, z, y, dir, kind)] with kind L (flat) or S (stair)."""
    bf = gr["before"]
    def cc(x, z, y):
        if not ok(x, z): return 1e9
        t = int(bf[ix(gr, x, z)]); c = max(t - y, 0); f = max(y - t, 0)
        return c + f * 1.3 + max(c - 5, 0) ** 2 * 3 + max(f - 4, 0) ** 2 * 4
    def seg(cells):
        return sum(cc(q[0], q[1], y) for (c, y, dr, k) in cells for q in foot(c, dr)) / 3
    cells0 = [((start[0] + DIRS[d0][0] * k, start[1] + DIRS[d0][1] * k), y0, d0, "L") for k in range(lead)]
    st = [(seg(cells0), cells0, set(q for (c, y, dr, k) in cells0 for q in foot(c, dr)), cells0[-1][0], y0, d0, 0)]
    finals = []
    for _ in range(depth):
        nxt = []
        for (cost, cells, occ, pos, y, dr, nfl) in st:
            dx, dz = DIRS[dr]
            for turn in (("S", "L", "R", "UL", "UR") if nfl > 0 else ("S",)):
                if nfl > 0:
                    q = (pos[0] + 2 * dx, pos[1] + 2 * dz)
                    land = [(pos[0] + dx * k, pos[1] + dz * k) for k in (1, 2, 3)]
                    if turn == "S": nd = dr
                    elif turn == "L": nd = LEFT[dr]
                    elif turn == "R": nd = RIGHT[dr]
                    else:
                        s = LEFT[dr] if turn == "UL" else RIGHT[dr]; sx, sz = DIRS[s]
                        land = land + [(q[0] + sx * k, q[1] + sz * k) for k in (1, 2, 3, 4)]
                        q = (q[0] + 4 * sx, q[1] + 4 * sz); nd = BACK[dr]
                    lc = set()
                    for (lx, lz) in land + [q]:
                        for a in (-1, 0, 1):
                            for b in (-1, 0, 1): lc.add((lx + a, lz + b))
                    if lc & (occ - set(foot(pos, dr))): continue
                    lcost = sum(cc(a, b, y) for (a, b) in lc) / 3
                else:
                    q = pos; nd = dr; land = []; lc = set(); lcost = 0
                ndx, ndz = DIRS[nd]
                for n in range(n_rng[0], n_rng[1] + 1):
                    for kc in corridors:
                        fl = []; yy = y
                        p0 = (q[0] + 2 * ndx, q[1] + 2 * ndz) if nfl > 0 else (q[0] + ndx, q[1] + ndz)
                        for k in range(kc): fl.append(((p0[0] + ndx * k, p0[1] + ndz * k), yy, nd, "L"))
                        p0 = (p0[0] + ndx * kc, p0[1] + ndz * kc)
                        for k in range(n): fl.append(((p0[0] + ndx * k, p0[1] + ndz * k), yy, nd, "S")); yy -= 1
                        fp = set(qq for (c, _, d_, _k) in fl for qq in foot(c, d_))
                        if fp & (occ | lc): continue
                        sc = seg(fl)
                        if sc >= 1e8: continue
                        ncells = cells + [((a, b), y, nd, "L") for (a, b) in land] + fl
                        nst = (cost + lcost + sc, ncells, occ | lc | fp, fl[-1][0], yy, nd, nfl + 1)     # the next landing 1 under the last stair
                        nxt.append(nst)
                        ex, ez = fl[-1][0][0] + ndx, fl[-1][0][1] + ndz
                        if end_ok(ex, ez, yy):
                            L = len(ncells) + 3
                            pen = 0 if length is None or length[0] <= L <= length[1] else 1e4
                            finals.append((nst[0] + pen, L, ncells, yy))
        nxt.sort(key=lambda s: s[0])
        seen = set(); st = []
        for s in nxt:
            k = (s[3], s[5], s[4])
            if k in seen: continue
            seen.add(k); st.append(s)
            if len(st) >= beam: break
        if not st: break
    if not finals: raise SystemExit("no flight path found from %s" % (start,))
    finals.sort(key=lambda f: f[0])
    cost, L, cells, ye = finals[0]
    out = [[c[0], c[1], y, dr, k] for (c, y, dr, k) in cells]
    # the closing landing (3 cells) at the end level
    lx, lz = out[-1][0], out[-1][1]; dx, dz = DIRS[out[-1][3]]
    for k in (1, 2, 3): out.append([lx + dx * k, lz + dz * k, ye, out[-1][3], "L"])
    return out

HILL = (232, 490, 247, 509)               # the platform of the three swords (16 x 20; the spur takes it with <= 8 cut, see the plan)
def hill_level(gr):
    bf = gr["before"]; i1, j1 = ix(gr, HILL[0], HILL[1]); i2, j2 = ix(gr, HILL[2], HILL[3])
    blk = bf[i1:i2 + 1, j1:j2 + 1]
    best = None
    for L in range(int(blk.min()), int(blk.max()) + 1):
        cut, fill = int(blk.max()) - L, L - int(blk.min())
        if cut <= 8 and (best is None or fill < best[1]): best = (L, fill, cut)
    return best

def search_paths(gr):
    W = floor_level(gr); fl, holes = floor_mask(gr, W)
    def ok_desc(x, z):
        if on_pad(x, z): return False
        if not (CEM[0] <= x <= CEM[2] and CEM[1] <= z <= CEM[3]) and not (126 <= x <= 133 and 438 <= z <= 458): return False
        if HILL[0] - 6 <= x <= HILL[2] + 6 and HILL[1] - 6 <= z <= HILL[3] + 6: return False
        return True
    def end_desc(x, z, y):
        i, j = ix(gr, x, z); return bool(fl[i, j]) and abs(int(gr["before"][i, j]) - y) <= 2 and gr["before"][i, j] <= W + 5
    desc = search_flights(gr, (126, 448), PAD_Y, "E", ok_desc, end_desc, length=(150, 250))
    L, fill, cut = hill_level(gr)
    hx, hz = HILL[0] + 1, HILL[1] - 1
    def ok_hill(x, z):
        return CEM[0] <= x <= CEM[2] and CEM[1] <= z <= CEM[3] and not (HILL[0] <= x <= HILL[2] and HILL[1] <= z <= HILL[3])
    hill = search_flights(gr, (hx, hz), L, "N", ok_hill, end_desc, beam=1500, depth=6, lead=2, corridors=(0, 2))
    json.dump(dict(W=W, desc=desc, hill=hill, hill_level=L), open(PATHS, "w"))
    return desc, hill

def load_paths():
    return json.load(open(PATHS))

# ---------------------------------------------------------------- the layout (fixed points, checked against the ground in the plan)
# barrows 9 x 12: (id, anchor x, anchor z, facing = the side of the dromos); the footprint is the box anchor .. anchor + (8, 11) for S/N
# and anchor .. anchor + (11, 8) for E/W
BARROWS = [(1, 215, 448, "S"), (2, 252, 448, "S"), (3, 206, 480, "W"), (4, 257, 494, "E"), (5, 140, 509, "N")]
CRYPT_X = 240                             # the axis of the crypt of the Magister (entrance in the south, at the foot of the north slope)
CRYPT_FRONT = 458                         # z of the facade (the door); vestibule, stair, corridor 3 x 15, stair, hall 20 x 20 go north
CHAPEL = (166, 492, 176, 504)             # the ruined chapel on the west part of the floor (x1 z1 x2 z2), door east
# the 16 fresh graves: number, x, z (the mound is (x, z) and (x, z+1), the headstone at (x, z-1)), kind, epitaph (lines)
GRAVES = [
    (1, 204, 468, "right", ["Сир Кадан", "Меч не выпустил", "и мёртвым."]),
    (2, 268, 478, "right", ["Марта Ясень", "Держала ворота", "до последнего."]),
    (3, 172, 510, "right", ["Брат Гест", "Пал лицом", "к врагу."]),
    (4, 270, 514, "right", ["Ивор Серый", "Остался, когда", "ушли все."]),
    (5, 226, 467, "right", ["Сира Лейн", "Стояла", "за троих."]),
    (6, 248, 464, "thane", ["Тейн,", "оруженосец.", "Шёл за щитом", "до конца."]),
    (7, 214, 470, "wrong", ["Сир Тоберт", "Ушёл в ночь", "до рассвета."]),
    (8, 235, 468, "wrong", ["Ренн Лис", "Открыл калитку", "чужим."]),
    (9, 257, 471, "wrong", ["Сир Аларик", "Сдал меч", "без боя."]),
    (10, 182, 496, "wrong", ["Годвин", "Бросил щит", "у Брода."]),
    (11, 158, 502, "wrong", ["Сир Освин", "Повернул коня."]),
    (12, 198, 488, "wrong", ["Хальд", "Ушёл за водой", "и не вернулся."]),
    (13, 273, 500, "wrong", ["Сир Мерек", "Просил пощады."]),
    (14, 190, 508, "wrong", ["Сира Ода", "Отдала знамя."]),
    (15, 263, 464, "pit", ["Безымянный."]),
    (16, 273, 489, "pit", ["Безымянная."]),
]
def barrow_cells(b):
    """{(x, z): (lx, lz)}: lx 0..8 across, lz 0 (back) .. 11 (front, the dromos)"""
    _, ax, az, f = b; out = {}
    for lx in range(9):
        for lz in range(12):
            if f == "S": d = (lx, lz)
            elif f == "N": d = (8 - lx, 11 - lz)
            elif f == "E": d = (lz, 8 - lx)
            else: d = (11 - lz, lx)
            out[(ax + d[0], az + d[1])] = (lx, lz)
    return out
def barrow_front(b):
    """the cell in front of the dromos (outside, on the axis) and the outward direction"""
    cells = barrow_cells(b); f = b[3]; dx, dz = DIRS[f]
    c = next(k for k, v in cells.items() if v == (4, 11)); return (c[0] + dx, c[1] + dz), f

def sword_sites(gr, W, fl, taken, desc_cells, n=60):
    """~60 small swords in clumps on the floor and the lower slopes (a density mask: dense near the hill and along the descent)"""
    X, Z = gr["X"], gr["Z"]; bf = gr["before"]
    hx, hz = (HILL[0] + HILL[2]) / 2, (HILL[1] + HILL[3]) / 2
    dd = np.full(X.shape, 99.0)
    for (x, z) in desc_cells[::3]: dd = np.minimum(dd, np.hypot(X - x, Z - z))
    dens = 0.15 + 0.85 * np.exp(-np.maximum(np.hypot(X - hx, Z - hz) - 12, 0) / 14) + 0.7 * np.exp(-dd / 8)
    cand = []
    for z in range(CEM[1] + 4, CEM[3] - 3, 3):
        for x in range(CEM[0] + 4, CEM[2] - 3, 3):
            i, j = ix(gr, x, z)
            if not (fl[i, j] or bf[i, j] <= W + 14): continue
            if (x, z) in taken: continue
            r = hsh(x, 0, z, 7101)
            cand.append((r / dens[i, j], x, z))
    cand.sort(); out = []
    for _, x, z in cand:
        if any(abs(x - a) + abs(z - b) < 4 for a, b, _ in out): continue
        if any((x + a, z + b) in taken for a in (-1, 0, 1) for b in (-1, 0, 1)): continue
        out.append((x, z, 3 + int(hsh(x, 1, z, 7102) * 4)))
        if len(out) >= n: break
    return out
