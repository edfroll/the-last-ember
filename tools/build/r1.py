#!/usr/bin/env python3
"""T-022: the frame of the Twilight Vale (Р1) — border relief, the Wall body, the rift with the bridge, the west pass gorge,
the shortcut ledge, bonfire pads, trails with fords and boardwalks, signposts, ridge forests, the plan picture.

  python3 tools/build/r1.py [build]   -> server/build/r1/: terrain.bin (tools/terrain.sh apply), r1.txt (tools/blockwriter.sh apply),
                                         trails.json (routes for the walk bot), plan.png (+ docs/reports/T-022/r1_plan.png),
                                         bonfires/bonfires.txt rows (r1), gate templates structure/gates/*.nbt
  python3 tools/build/r1.py plan      -> only the plan picture
Inputs: server/build/r1/nat.bin   natural ground before any sculpting (tools/terrain.sh scan of the fresh world; kept for re-runs)
        server/build/r1/base.bin  ground after the Refuge and the Ring Mountain (scan right before the R1 terrain; kept for re-runs)
        tools/build/r1_plots.txt  places of the future R1 locations: never sculpted, trails end at their edge
Every write is limited to its own feature area and never touches a plot (bonfire pads and the shortcut ledge are put where the cards
put them, inside the plots of the Circle and the other places). numpy + Pillow."""
import heapq, json, math, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import Scan, write_grid, NONE
from lib import Mix, h as hsh, slab
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "server/build/r1")
# surface styles / rock styles of tools/seedmap/Terrain.java
S_GRASS, S_FOREST, S_COARSE, S_SNOW, S_BED, S_MOSS, S_FLAT, S_CHAR, S_RIVER, S_ROCK = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
R_STONE, R_WEST, R_EAST, R_RIFT_N, R_RIFT_S, R_NORTH, R_WALL_S, R_WALL_N, R_DEEP = 0, 1, 2, 3, 4, 5, 6, 7, 8

# ------------------------------------------------------------------ data from the cards
BONFIRES = [  # (number, id, x, z, card y note) — «Карточки локаций Р1, партия 3», раздел 6 (number = card number + 1: 1 is the Refuge)
    (2, "r1_cemetery", 118, 448), (3, "r1_maze", -150, -362), (4, "r1_garden", 238, -258), (5, "r1_fens", -276, 250),
    (6, "r1_weepers", -392, -180), (7, "r1_causeway", 356, -40), (8, "r1_bridge", 440, -10), (9, "r1_heather", 70, -420), (10, "r1_grove", -404, 72)]
# trails: Refuge -> each bonfire (table «Расстояния по путям»), then the ring links; (from, to, card length)
TRAILS = [("R", 6, 210), ("R", 5, 190), ("R", 3, 230), ("R", 9, 220), ("R", 4, 150), ("R", 2, 270), ("R", 7, 160),
          (7, 8, 100), (6, 10, 220), (10, 5, 225), (3, 9, 230), (9, 4, 250), (4, 7, 250), ("W", 6, 0),   # W = the west pass gorge (not in the table)
          ("R", "S", 450)]   # S = the South road: from the south gate of the Refuge (r4, 160°) to the north ramp of the bridge (HQ review T-022, 4)
NOFADE = {6, 10}          # T-023: bonfires of R1 that never fade (the Circle: the altar keeps the memory; the Grove never fades)
NO_APPROACH = {(7, 8)}    # causeway -> before the bridge: the castle stairs (castle task); every other trail runs on to the bonfire pad (HQ review, 1)
SOUTH_GATE = 160          # compass angle of the Refuge gate r4 (tools/build/plaza.py GATES)
REFUGE_R = 200            # «стены Приюта» of the distance table = the Refuge zone (r 200)
TRAILHEAD_R = 92          # the trails start where the sculpted plateau of the hub ends (T-008: y 99 at r 90)
DOOR = (-380, -196)       # shortcut door of R1 (card, party 2), faces east
PASS = (-640, -190); GORGE_Z = (-194, -186)    # west pass: gorge 9 wide through the ridge, rubble template at the axis
BRIDGE_X = (-2, 2); BRIDGE_Z = (625, 675)       # bridge of the South road over the rift: 5 x 50

def smooth(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
def fbm1(n, cells, seed):
    """1-D fractal noise in [-1, 1] over n samples (deterministic)"""
    rng = np.random.default_rng(seed); out = np.zeros(n)
    for c, a in zip(cells, (1, .5, .25, .125)):
        g = rng.random(n // c + 3); t = np.arange(n) / c; i = t.astype(int); f = t - i; f = f * f * (3 - 2 * f)
        out += a * (g[i] + (g[i + 1] - g[i]) * f)
    return out / sum((1, .5, .25, .125)[:len(cells)]) * 2 - 1
def vnoise2(shape, cell, seed):
    rng = np.random.default_rng(seed); gh, gw = shape[0] // cell + 3, shape[1] // cell + 3; g = rng.random((gh, gw))
    ys = np.arange(shape[0]) / cell; xs = np.arange(shape[1]) / cell; y0 = ys.astype(int); x0 = xs.astype(int)
    fy = ys - y0; fx = xs - x0; fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
    a = g[y0][:, x0]; b = g[y0][:, x0 + 1]; c = g[y0 + 1][:, x0]; d = g[y0 + 1][:, x0 + 1]
    top = a + (b - a) * fx[None, :]; bot = c + (d - c) * fx[None, :]
    return top + (bot - top) * fy[:, None]

# ------------------------------------------------------------------ plots
def read_plots():
    out = []
    for line in open(os.path.join(ROOT, "tools/build/r1_plots.txt"), encoding="utf-8"):
        a = line.split("#", 1)[0].split()
        if not a: continue
        kv = dict(t.split("=", 1) for t in a if "=" in t); a = [t for t in a if "=" not in t]
        m = int(kv.get("margin", 16))
        if a[1] == "rect": out.append(dict(id=a[0], kind="rect", cx=int(a[2]), cz=int(a[3]), w=int(a[4]), d=int(a[5]), m=m))
        else: out.append(dict(id=a[0], kind="circle", cx=int(a[2]), cz=int(a[3]), r=int(a[4]), m=m))
    return out
def plot_dist(p, X, Z):
    """distance outside the plot core (0 inside)"""
    if p["kind"] == "rect":
        dx = np.maximum(np.abs(X - p["cx"]) - p["w"] / 2, 0); dz = np.maximum(np.abs(Z - p["cz"]) - p["d"] / 2, 0); return np.hypot(dx, dz)
    return np.maximum(np.hypot(X - p["cx"], Z - p["cz"]) - p["r"], 0)

class World:
    def __init__(self):
        self.nat = Scan(os.path.join(OUT, "nat.bin")); self.base = Scan(os.path.join(OUT, "base.bin"))
        s = self.base; self.x0, self.z0, self.w, self.h = s.x0, s.z0, s.w, s.h
        self.X, self.Z = np.meshgrid(np.arange(s.x0, s.x0 + s.w), np.arange(s.z0, s.z0 + s.h))
        self.G = s.ground.astype(float); self.missing = (s.flags & 16) > 0; self.G[self.missing] = 63
        self.Wn = np.where((s.water != NONE) & (s.water > s.ground), s.water, NONE)     # natural water surface
        self.H = self.G.copy(); self.S = np.zeros_like(self.G, np.uint8); self.R = np.zeros_like(self.G, np.uint8); self.A = np.zeros_like(self.G, np.uint8)
        self.Wset = np.full(self.G.shape, NONE); self.touch = np.zeros(self.G.shape, bool); self.allow = np.zeros(self.G.shape, bool)
        self.plots = read_plots(); self.pd = np.full(self.G.shape, 1e9)
        for p in self.plots: self.pd = np.minimum(self.pd, plot_dist(p, self.X, self.Z) - p["m"])
        self.pd = np.maximum(self.pd, 0)             # 0 = inside a plot (core + margin)
        self.pw = smooth(self.pd / 16)              # sculpt weight: 0 in plots, full 16 blocks outside them
    def sl(self, x1, z1, x2, z2):
        return (slice(max(0, z1 - self.z0), min(self.h, z2 - self.z0 + 1)), slice(max(0, x1 - self.x0), min(self.w, x2 - self.x0 + 1)))
    def at(self, x, z): return int(round(self.H[z - self.z0, x - self.x0]))
    def inplot(self, x, z): return self.pd[z - self.z0, x - self.x0] <= 0

# ------------------------------------------------------------------ relief features
def ridge(W, axis, along, a_lo, a_hi, crest, dol_w, out_w, dol_sign, rock, dol_surf, out_surf, snow, seed, teeth=8, taper=30):
    """a ridge along x = axis (along='z') or z = axis (along='x'). Profile: crest(a) above the natural ground, falling to it over dol_w
    blocks on the Vale side and out_w on the outer side (concave, steep at the top, forested foot)."""
    if along == "z": d = (W.X - axis) * dol_sign; a = W.Z
    else: d = (W.Z - axis) * dol_sign; a = W.X
    n = a_hi - a_lo + 2 * taper + 1; cr = crest(n)           # crest along the axis
    ai = np.clip(a - (a_lo - taper), 0, n - 1).astype(int); C = cr[ai]
    end = smooth((a - (a_lo - taper)) / taper) * smooth(((a_hi + taper) - a) / taper)
    t = np.where(d >= 0, d / dol_w, -d / out_w)
    inside = (t < 1) & (end > 0)
    p = np.where(d >= 0, (1 - np.clip(t, 0, 1)) ** 1.9, (1 - np.clip(t, 0, 1)) ** 1.5)
    jag = vnoise2(W.G.shape, 3, seed + 1) * vnoise2(W.G.shape, 11, seed + 2)
    T = W.G + np.maximum(C - W.G, 0) * p * end + teeth * np.maximum(jag - 0.25, 0) * 2 * (p > 0.55) * end
    sel = inside & (T > W.H + 0.5)
    raise_to(W, sel, T, rock)
    # surfaces: slope from the target field
    gy, gx = np.gradient(W.H); slope = np.hypot(gx, gy)
    vale = d >= 0
    s = np.where(vale, np.where((slope < 1.15) & (W.H < 150), dol_surf, S_ROCK), np.where((W.H - W.G) < 4, S_GRASS, out_surf))
    s = np.where(W.H >= snow, S_SNOW, s)
    W.S[sel] = s[sel]
    return sel
def raise_to(W, sel, T, rock):
    w = W.pw; T2 = W.G + (T - W.G) * w        # plots stay natural, 16-block seam outside them
    m = sel & (np.abs(T2 - W.H) > 0.5)
    W.H[m] = T2[m]; W.R[m] = rock; W.touch[m] = True; W.S[m] = S_GRASS
def north_ridge(W):
    """the Wall's height map (x -1000..399, z -1000..-681) as a whole, its material mask; west and east of it the ridge continues
    along the same profile (x -1504..-1001 and 400..751), crossfaded 30 blocks into the map."""
    from PIL import Image
    hp = np.array(Image.open(os.path.join(ROOT, "docs/design/heightmaps/the_wall_height.png"))).astype(float) + 40
    mk = np.array(Image.open(os.path.join(ROOT, "docs/design/heightmaps/the_wall_material.png")))
    MX0, MZ0 = -1000, -1000; mh, mw = hp.shape
    # extension field E over the whole north band (z -1000..-681): profile of the map's end column, crest varied by noise
    zz = np.arange(MZ0, MZ0 + mh)
    def ext(col, xs, seed):
        P = hp[:, col]; amp = 1 + 0.10 * fbm1(len(xs), (64, 24, 8), seed)              # crest 230..270
        shift = (6 * fbm1(len(xs), (90, 30), seed + 5)).astype(int)
        out = np.zeros((mh, len(xs)))
        for j in range(len(xs)):
            Pj = np.roll(P, shift[j]); out[:, j] = 78 + np.maximum(Pj - 78, 0) * amp[j]
        return out
    sl_z = slice(MZ0 - W.z0, MZ0 + mh - W.z0)
    E = np.full((mh, W.w), np.nan)
    xm0 = MX0 - W.x0; E[:, xm0:xm0 + mw] = hp
    xw = np.arange(W.x0, MX0); xe = np.arange(MX0 + mw, W.x0 + W.w)
    Ew = ext(10, xw, 701); Ee = ext(mw - 1, xe, 702)
    G = W.G[sl_z]
    # outside the map: add the ridge's rise over 78 onto the natural ground (the foot rows stay natural)
    Ew_ = G[:, :len(xw)] + np.maximum(Ew - 78, 0); Ee_ = G[:, xm0 + mw:] + np.maximum(Ee - 78, 0)
    for k in range(30):     # crossfade into the map
        s = smooth((k + 0.5) / 30)
        if k < len(xw): Ew_[:, -1 - k] = Ew_[:, -1 - k] * s + hp[:, 0] * (1 - s)
        if k < len(xe): Ee_[:, k] = Ee_[:, k] * s + hp[:, mw - 1] * (1 - s)
    E[:, :len(xw)] = Ew_; E[:, xm0 + mw:] = Ee_
    # south seam 24 below the map (z -680..-657): blend into the natural ground
    T = W.G.copy(); T[sl_z] = E
    for k in range(1, 25):
        zi = MZ0 + mh - 1 + k - W.z0; t = 1 - smooth(k / 24)
        T[zi] = t * T[MZ0 + mh - 1 - W.z0] + (1 - t) * W.G[zi]
    sel = np.zeros(W.G.shape, bool); sel[MZ0 - W.z0:MZ0 + mh - W.z0 + 24] = True
    sel &= np.abs(T - W.H) > 0.5
    # materials
    M = np.zeros(W.G.shape, np.uint8); M[sl_z, xm0:xm0 + mw] = mk
    raise_cut(W, sel, T, R_NORTH)
    gy, gx = np.gradient(W.H); slope = np.hypot(gx, gy)
    s = np.where(W.H >= 200, S_SNOW, np.where((slope < 1.0) & (W.H < 140), S_GRASS, S_ROCK))
    W.S[sel] = s[sel]
    wall = (M == 100) & W.touch; post = (M == 200) & W.touch
    ds = -850 - W.Z; dn = W.Z + 889
    W.R[wall] = np.where(dn[wall] < ds[wall], R_WALL_N, R_WALL_S); W.A[wall] = np.clip(np.minimum(ds, dn)[wall], 0, 255).astype(np.uint8); W.S[wall] = 0
    W.S[post] = S_FLAT; W.R[post] = R_STONE
    return M
def raise_cut(W, sel, T, rock):
    T2 = W.G + (T - W.G) * W.pw; m = sel & (np.abs(T2 - W.H) > 0.5)
    W.H[m] = T2[m]; W.R[m] = rock; W.touch[m] = True; W.S[m] = S_GRASS
def rift(W):
    """Ржавый Разлом: canyon along z 650, 30..50 wide, floor y 0..3 with a dry riverbed; dark stone on the Vale side, red clay and
    sandstone on the south side. The land cracked here: each rim wanders on its own (±3..5 blocks over 10..30), the walls lean
    differently (profile exponent and width vary), uneven ledges at different heights (HQ review T-022, 5). Natural water at the rims
    is dammed (raised to its level) so nothing pours in. Overhangs and the scree on the floor: rift_details()."""
    xs = np.arange(W.x0, W.x0 + W.w); n = len(xs); ax = np.abs(xs)
    base = 20 + 4 * fbm1(n, (120, 40), 11)
    hn = base + 4 * fbm1(n, (22, 9, 4), 16); hs = base + 4 * fbm1(n, (26, 11, 5), 17)
    near = ax < 40; k = smooth((ax - 25) / 15)                              # at the bridge: 22 each side
    hn = np.where(near, 22 + (hn - 22) * k, hn); hs = np.where(near, 22 + (hs - 22) * k, hs)
    hn = np.clip(hn, 15, 25); hs = np.clip(hs, 15, 25)
    fl = 1.5 + 1.5 * fbm1(n, (60, 20), 12); cen = 5 * fbm1(n, (80, 25), 13)
    FL = fl[None, :]; CE = cen[None, :]
    d = W.Z - 650 - CE * 0.3; dz = np.abs(d)
    HW = np.where(d < 0, hn[None, :], hs[None, :])
    wallw = 5 + 9 * vnoise2(W.G.shape, 13, 14)                             # 5..14: from a sheer face to a leaning one
    ex = 0.3 + 0.6 * vnoise2(W.G.shape, 17, 19)                             # profile exponent: convex / straight
    t = (dz - (HW - wallw)) / wallw
    prof = np.where(dz <= HW - wallw, 0, np.clip(t, 0, 1) ** ex)
    nst = 4 + np.floor(4 * vnoise2(W.G.shape, 31, 20))                      # 4..7 ledges, their heights vary along the wall
    ledge = np.floor(prof * nst + vnoise2(W.G.shape, 6, 15) * 0.8) / nst
    prof = np.clip(0.45 * prof + 0.55 * ledge, 0, 1)
    bed = (np.abs(W.Z - 650 - CE) < 3) * 1.0
    T = FL - bed + (W.G - FL + bed) * prof
    band = (dz < HW) & (W.X >= -744)
    near = (dz < HW + 6) & (W.Wn != NONE) & (W.X >= -744)
    T = np.where(band, np.minimum(T, W.H), W.H)
    sel = band & (T < W.H - 0.5)
    m = sel & (W.pw > 0)
    W.H[m] = T[m]; W.touch[m] = True
    W.R[m] = np.where(W.Z[m] < 650, R_RIFT_N, R_RIFT_S)
    W.S[m] = np.where(prof[m] < 0.05, S_RIVER, 0)
    dam = near & ~band
    W.H[dam] = np.maximum(W.H[dam], W.Wn[dam]); W.touch[dam] = True; W.S[dam] = S_BED; W.R[dam] = R_STONE
    W.rift = dict(cen=cen, fl=fl, prof=prof, hn=hn, hs=hs)
    return np.minimum(hn, hs), fl
RIFT_N = Mix({"deepslate[axis=y]": 40, "tuff": 25, "cobbled_deepslate": 25, "andesite": 10}, 811)
RIFT_S = {0: "red_terracotta", 1: "terracotta", 2: "red_sandstone", 3: "orange_terracotta", 4: "sandstone", 5: "brown_terracotta", 6: "red_sandstone"}
def rift_rock(x, y, z):
    if z < 650: return RIFT_N.at(x, y, z)
    return RIFT_S[(y // 3) % 7]                         # horizontal strata, as tools/seedmap/Terrain.java rock style 4
def rift_details(W, P):
    """overhangs (cornices) on both walls at different heights and the scree of fallen blocks on the floor at the foot of the walls
    (not in the riverbed, not under the bridge)"""
    cen = W.rift["cen"]; nc = ns = 0
    for x in range(-740, 740):
        if abs(x) < 12: continue
        xi = x - W.x0; c = 650 + int(round(cen[xi]))
        for side in (-1, 1):
            # cornice: every ~14 blocks a shelf 1..3 out of the wall, 4..9 long, 1..2 thick, at 25..75% of the wall height
            if hsh(x // 14, side, 0, 821) < 0.55 and x % 14 == 0:
                L = 4 + int(hsh(x, side, 1, 822) * 6); out = 1 + int(hsh(x, side, 2, 823) * 3); th = 1 + int(hsh(x, side, 3, 824) * 2)
                fr = 0.25 + 0.5 * hsh(x, side, 4, 825)
                for xx in range(x, x + L):
                    if abs(xx) < 12 or xx >= 740: continue
                    rim = W.at(xx, c + side * 30); flo = W.at(xx, c); yc = int(flo + (rim - flo) * fr)
                    zz = c                                          # the wall at that height: first column outwards whose ground >= yc
                    while abs(zz - c) < 28 and W.at(xx, zz) < yc: zz += side
                    if abs(zz - c) >= 28: continue
                    o = out - (1 if xx in (x, x + L - 1) else 0)
                    for k in range(1, o + 1):
                        q = zz - side * k
                        if W.inplot(xx, q): continue
                        for yy in range(yc - th + 1, yc + 1):
                            if yy > W.at(xx, q): P.set(xx, yy, q, rift_rock(xx, yy, q)); nc += 1
            # scree: blocks and small heaps on the floor near the foot of the wall
            for k in range(3, 18):
                z = c + side * k
                if abs(z - 650 - cen[xi]) < 4: continue
                pr = W.rift["prof"][z - W.z0, xi]
                if pr > 0.12 or hsh(x, z, 5, 826) > 0.06 + 0.05 * (k > 8): continue
                g = W.at(x, z); r = 1 + int(hsh(x, z, 6, 827) * 2)
                for dx in range(-r, r + 1):
                    for dz in range(-r, r + 1):
                        hgt = r + 1 - max(abs(dx), abs(dz)) - (1 if hsh(x + dx, z + dz, 7, 828) < 0.3 else 0)
                        gq = W.at(x + dx, z + dz)
                        if abs(z + dz - 650 - cen[xi]) < 3 or abs(x + dx) < 8 or abs(gq - g) > 2 or W.inplot(x + dx, z + dz): continue
                        for yy in range(gq + 1, gq + 1 + hgt): P.set(x + dx, yy, z + dz, rift_rock(x + dx, yy, z + dz)); ns += 1
    return nc, ns
def gorge(W):
    """the west pass: a gorge 9 wide (z -194..-186) through the ridge, vertical walls; the floor follows the natural ground at both
    mouths and is graded in half blocks by the trail through it."""
    z1, z2 = GORGE_Z; xa, xb = -712, -590
    ga = W.G[(z1 + z2) // 2 - W.z0, xa - W.x0]; gb = W.G[(z1 + z2) // 2 - W.z0, xb - W.x0]
    xs = np.arange(xa, xb + 1); f = ga + (gb - ga) * smooth((xs - xa) / (xb - xa)); sel = np.zeros(W.G.shape, bool)
    for i, x in enumerate(xs):
        for z in range(z1, z2 + 1):
            zi, xi = z - W.z0, x - W.x0
            if W.H[zi, xi] > f[i] + 0.5: W.H[zi, xi] = f[i]; W.S[zi, xi] = S_FLAT; W.R[zi, xi] = R_WEST; W.touch[zi, xi] = True; sel[zi, xi] = True
    return sel
def ledge(W):
    """rock outcrop for the shortcut door (card: «дверь врезана в скальный выступ»): face at x -380, 12..15 high"""
    x0, z0 = DOOR; g = W.G[z0 - W.z0, x0 + 1 - W.x0]
    floor = int(round(np.median(W.G[z0 - 4 - W.z0:z0 + 5 - W.z0, x0 + 1 - W.x0:x0 + 4 - W.x0])))
    for x in range(-398, -379):
        for z in range(-207, -187):
            u = (-379 - x); v = abs(z + 196.5)
            top = floor + 13 + 2 * hsh(x // 2, 0, z // 2, 91) - max(0, v - 7) * 1.6 - max(0, u - 14) * 2.5
            if top > W.H[z - W.z0, x - W.x0] + 0.5:
                zi, xi = z - W.z0, x - W.x0; W.H[zi, xi] = top; W.S[zi, xi] = S_ROCK; W.R[zi, xi] = R_WEST; W.touch[zi, xi] = True
    for x in range(-379, -372):          # the floor in front of the door: level
        for z in range(-200, -192):
            zi, xi = z - W.z0, x - W.x0; W.H[zi, xi] = floor; W.S[zi, xi] = S_FOREST; W.R[zi, xi] = R_STONE; W.touch[zi, xi] = True
    return floor + 1
def pads(W):
    """flat 14x14 pads round the bonfires (hearth y = pad + 1); the rim falls/rises 1 block per block (Chebyshev) to the ground, no
    vertical step (HQ review T-022, 3). Every written column goes to W.allow (the exception of r1_check plots)."""
    out = []
    for n, bid, x, z in BONFIRES:
        sub = W.G[z - 5 - W.z0:z + 9 - W.z0, x - 6 - W.x0:x + 8 - W.x0]; ws = W.Wn[z - 5 - W.z0:z + 9 - W.z0, x - 6 - W.x0:x + 8 - W.x0]
        y = int(round(np.median(sub)))
        if (ws != NONE).any(): y = max(y, int(ws.max()) + 1)        # never under water: the pad is raised over the shore
        for zz in range(z - 29, z + 33):
            for xx in range(x - 30, x + 32):
                d = max(x - 6 - xx, xx - (x + 7), z - 5 - zz, zz - (z + 8), 0)
                zi, xi = zz - W.z0, xx - W.x0; cur = W.at(xx, zz)
                t = y if d == 0 else min(max(cur, y - d), y + d)
                if t != cur or d == 0:
                    W.H[zi, xi] = t; W.S[zi, xi] = S_FOREST; W.R[zi, xi] = R_STONE; W.touch[zi, xi] = True; W.allow[zi, xi] = True
        out.append((n, bid, x, y + 1, z))
    return out

# ------------------------------------------------------------------ trails
USED = 1.2                  # cost of a cell next to an already laid trail (base 1.6): joins trails into shared stretches
SLOPE = [1.5, 4.0, 1.0]     # trail search: cost per block of height step, and of the step above the third value (squared)
def astar(W, start, goal, cost, box):
    x1, z1, x2, z2 = box; sx, sz = start; gx, gz = goal
    Hs = W.H; best = {start: 0.0}; prev = {}; pq = [(0.0, start)]; diag = math.sqrt(2)
    while pq:
        f, c = heapq.heappop(pq)
        if c == goal: break
        cx, cz = c; g0 = best[c]
        if f - math.hypot(cx - gx, cz - gz) > g0 + 1e-6: continue
        h0 = Hs[cz - W.z0, cx - W.x0]
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, nz = cx + dx, cz + dz
            if not (x1 <= nx <= x2 and z1 <= nz <= z2): continue
            k = cost[nz - z1, nx - x1]
            if k >= 1e6: continue
            dh = abs(Hs[nz - W.z0, nx - W.x0] - h0); st = diag if dx and dz else 1.0
            g = g0 + st * (k + SLOPE[0] * dh + SLOPE[1] * max(0.0, dh - SLOPE[2]) ** 2)
            if g < best.get((nx, nz), 1e18):
                best[(nx, nz)] = g; prev[(nx, nz)] = c; heapq.heappush(pq, (g + math.hypot(nx - gx, nz - gz), (nx, nz)))
    path = [goal]
    while path[-1] != start: path.append(prev[path[-1]])
    return path[::-1]
def cost_field(W, box, used):
    x1, z1, x2, z2 = box; s = W.sl(x1, z1, x2, z2)
    c = np.ones((z2 - z1 + 1, x2 - x1 + 1)) * 1.6
    fl = W.base.flags[s]; wn = W.Wn[s]; g = W.G[s]
    c += np.where((fl & 1) > 0, 14, 0)                         # tree trunks
    depth = np.where(wn != NONE, wn - g, 0)
    c += np.where(depth > 0, np.where(depth <= 2, 2, 4), 0)     # fords / boardwalks
    c += np.where(W.pd[s] <= 0, 40, 0)                          # plots: only to leave/enter towards a bonfire inside
    c += np.where(W.touch[s] & (W.R[s] != R_STONE), 1e6, 0)     # ridges, rift, wall
    for (x, z) in used:
        if x1 <= x <= x2 and z1 <= z <= z2 and not W.inplot(x, z): c[z - z1, x - x1] = min(c[z - z1, x - x1], USED)   # not inside places:
        # a ring trail leaves its bonfire's place by its own shortest approach instead of riding another trail's approach out
    return c
def simplify(path, step=5):
    pts = path[::step] + [path[-1]]
    for _ in range(2):   # Chaikin
        q = [pts[0]]
        for a, b in zip(pts, pts[1:]): q += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        pts = q + [pts[-1]]
    return pts
TRAILM = Mix({"dirt_path": 55, "coarse_dirt": 20, "gravel": 15, "mossy_cobblestone": 10}, 222)
class Placer:
    def __init__(self): self.v = {}
    def set(self, x, y, z, s): self.v[(x, y, z)] = s if ":" in s.split("[")[0] else "minecraft:" + s
    def get(self, x, y, z): return self.v.get((x, y, z))
LAID = {}      # (x, z) -> surface in half blocks of the trails already laid: a later trail joins them and never rewrites them
def lay_trail(W, P, cells, w=1, end_y=None, start_y=None, inplot=False):
    """graded path (T-008 rules): surfaces in half blocks change by at most 0.5 per step along the line and across the width;
    cut into slopes, banked over hollows (earth down to the ground), fords (gravel up to the water level) and boardwalks over deeper water."""
    def surf0(c):
        x, z = c; wn = W.Wn[z - W.z0, x - W.x0]; g = W.at(x, z)
        return 2 * (max(g, wn) + 1) if wn != NONE else 2 * (g + 1)
    t = [surf0(c) for c in cells]
    if start_y is not None: t[0] = 2 * start_y
    if end_y is not None: t[-1] = 2 * end_y
    fixed = {i: LAID[c] for i, c in enumerate(cells) if c in LAID}
    if start_y is not None and 0 not in fixed: fixed[0] = 2 * start_y              # anchors are pinned: the end meets the pad / the deck
    if end_y is not None and len(t) - 1 not in fixed: fixed[len(t) - 1] = 2 * end_y
    for i, v in fixed.items(): t[i] = v
    for _ in range(6):
        for i in range(1, len(t)):
            if i not in fixed: t[i] = max(min(t[i], t[i - 1] + 1), t[i - 1] - 1)
        for i in range(len(t) - 2, -1, -1):
            if i not in fixed: t[i] = max(min(t[i], t[i + 1] + 1), t[i + 1] - 1)
    surf = {}; best = {}; fill = {}; cut = {}
    for c, s2 in zip(cells, t):
        for dx in range(-w, w + 1):
            for dz in range(-w, w + 1):
                if dx * dx + dz * dz > w * w + 1: continue
                q = (c[0] + dx, c[1] + dz); d = dx * dx + dz * dz
                if q not in best or d < best[q] or (d == best[q] and s2 < surf[q]): best[q] = d; surf[q] = s2
    for q in surf:
        if q in LAID: surf[q] = LAID[q]
    def nb(x, z): return [surf.get(q, LAID.get(q)) for q in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)) if q in surf or q in LAID]
    changed = True; it = 0
    while changed and it < 300:                     # across the width (and against older trails next to it) at most half a block
        changed = False; it += 1
        for (x, z), s2 in list(surf.items()):
            if (x, z) in LAID: continue
            n = nb(x, z)
            if not n: continue
            if s2 > min(n) + 1: surf[(x, z)] = min(n) + 1; changed = True
            elif s2 < max(n) - 1: surf[(x, z)] = max(n) - 1; changed = True
    for (x, z), s2 in surf.items():
        if (x, z) in LAID: continue
        if best[(x, z)] > 0 and W.inplot(x, z) and math.hypot(x, z) > REFUGE_R and not inplot: continue
        LAID[(x, z)] = s2
        if W.inplot(x, z): W.allow[z - W.z0, x - W.x0] = True
        y = (s2 - 1) // 2 if s2 % 2 else s2 // 2 - 1
        g = W.at(x, z); wn = W.Wn[z - W.z0, x - W.x0]; wet = wn != NONE and wn >= y - 1
        if wet and wn - W.at(x, z) > 2:                        # boardwalk
            top = "spruce_slab[type=bottom,waterlogged=false]" if s2 % 2 else "spruce_planks"
            P.set(x, y, z, top)
            if (x + z) % 4 == 0 and best[(x, z)] > 0:
                for yy in range(g + 1, y): P.set(x, yy, z, "spruce_log[axis=y]")
        else:
            top = slab("mossy_cobblestone_slab") if s2 % 2 and hsh(x, 0, z, 5) < 0.3 else (slab("cobblestone_slab") if s2 % 2 else TRAILM.at(x, y, z))
            P.set(x, y, z, top)
            for yy in range(min(g, y - 1) - 1 if not wet else g + 1, y):
                P.set(x, yy, z, "gravel" if wet else ("dirt" if yy >= y - 3 else "stone"))
        for yy in range(y + 1, max(y + 4, g + 1)): P.set(x, yy, z, "air")
        if best[(x, z)] > 0 and (y - g >= 1 or g - y >= 2):
            # an embankment: a berm 1 wide level with the trail (HQ review T-022, 2), then earth shoulders falling 1 per block;
            # a cutting: the side walls go back 1 per block from a berm level with the trail (no vertical wall at the trail)
            k = min(abs(y - g), 14) + 1; emb = y > g
            for dx in range(-k, k + 1):
                for dz in range(-k, k + 1):
                    q = (x + dx, z + dz); r = max(abs(dx), abs(dz))
                    qi = (q[1] - W.z0, q[0] - W.x0)
                    if not (0 <= qi[0] < W.h and 0 <= qi[1] < W.w): continue
                    if r == 0 or q in surf or q in LAID or (W.inplot(*q) and not inplot): continue
                    if emb: top = y - max(0, r - 1); fill[q] = max(fill.get(q, -999), top)
                    else:
                        if W.touch[qi] and W.R[qi] != R_STONE: continue      # ridges, the Wall, the rift
                        top = y + max(0, r - 1); cut[q] = min(cut.get(q, 9999), top)
    # applied after the whole trail: the highest shoulder / the lowest cut of all trail cells wins (no layered leftovers)
    for q in set(fill) | set(cut):
        gq = W.at(*q); qi = (q[1] - W.z0, q[0] - W.x0)
        if q in fill and fill[q] > gq:
            top = fill[q]
            for yy in range(gq + 1, top + 1):
                if P.get(q[0], yy, q[1]) in (None, "minecraft:air"): P.set(q[0], yy, q[1], "grass_block[snowy=false]" if yy == top else "dirt")
        elif q in cut and cut[q] < gq:
            top = cut[q]
            if P.get(q[0], top, q[1]) in (None, "minecraft:air"): P.set(q[0], top, q[1], "grass_block[snowy=false]")
            for yy in range(top + 1, gq + 12):
                if P.get(q[0], yy, q[1]) in (None, "minecraft:grass_block[snowy=false]", "minecraft:dirt"): P.set(q[0], yy, q[1], "air")
        else: continue
        if W.inplot(*q): W.allow[qi] = True
    return [((c[0] + 0.5, c[1] + 0.5), surf.get(c, s2) / 2) for c, s2 in zip(cells, t)]
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
def trails(W, P, bonf, door_y):
    B = {n: (x, z) for n, bid, x, y, z in bonf}; BY = {n: y for n, bid, x, y, z in bonf}
    used = set(); out = []; heads = {}
    for a, b, card in TRAILS:
        if a == "R" and b == "S": pass               # start set below
        elif a == "R":                                 # from the hub plateau edge towards the bonfire
            gx, gz = B[b]; ang = math.atan2(gz, gx); start = (int(round(TRAILHEAD_R * math.cos(ang))), int(round(TRAILHEAD_R * math.sin(ang))))
        elif a == "W": start = (-716, (GORGE_Z[0] + GORGE_Z[1]) // 2)
        else: start = B[a]
        if b == "S":
            ang = math.radians(SOUTH_GATE); start = (int(round(TRAILHEAD_R * math.sin(ang))), int(round(-TRAILHEAD_R * math.cos(ang))))
            goal = (0, BRIDGE_Z[0] - 106)            # the far end of the bridge's north ramp (bridge())
        else: goal = B[b]
        appr = (a, b) not in NO_APPROACH
        box = (min(start[0], goal[0]) - 120, min(start[1], goal[1]) - 120, max(start[0], goal[0]) + 120, max(start[1], goal[1]) + 120)
        box = (max(box[0], -760), max(box[1], -900), min(box[2], 740), min(box[3], 640))
        cost = cost_field(W, box, used)
        if b == "S": cost[W.pd[W.sl(*box)] <= 0] = 1e6         # the South road never crosses a place (branching off the cemetery trail is fine)
        if a == "W":   # the gorge is the only way through the ridge here
            s = W.sl(-716, GORGE_Z[0], -596, GORGE_Z[1]); zz, xx = np.nonzero(np.ones((GORGE_Z[1] - GORGE_Z[0] + 1, 121)))
            for z in range(GORGE_Z[0] + 2, GORGE_Z[1] - 1):
                for x in range(-716, -596): cost[z - box[1], x - box[0]] = 1.0
        path = astar(W, start, goal, cost, box)
        # cut at the plot edges: the trail runs only outside the places of locations
        inp = [W.inplot(x, z) for x, z in path]
        i0 = 0
        if appr:   # approaches: the trail runs on through the place to the edge of the bonfire pad (inside 8 of the hearth = the pad)
            inp = [b != "S" and max(abs(x - goal[0] - 0.5), abs(z - goal[1] - 1.5)) <= 6.5 or a not in ("R", "W") and max(abs(x - start[0] - 0.5), abs(z - start[1] - 1.5)) <= 6.5 for x, z in path]
        while i0 < len(path) - 1 and inp[i0] and a != "R" and a != "W": i0 += 1
        i1 = len(path) - 1
        while i1 > i0 and inp[i1]: i1 -= 1
        core = path[i0:i1 + 1]
        pts = simplify(core) if len(core) > 6 else core
        cells = [c for c in cells_of(pts) if appr or not W.inplot(*c) or a in ("R", "W") and math.hypot(*c) < REFUGE_R]
        # the ends at a plot edge meet the natural ground of the place (no step down from an embankment into it)
        ey = W.at(*cells[-1]) + 1 if cells and i1 < len(path) - 1 else None
        sy = W.at(*cells[0]) + 1 if cells and i0 > 0 else None
        if appr:
            ey = BY[b] if cells and b != "S" else None; sy = BY[a] if cells and a not in ("R", "W") else None   # = the pad surface
        prof = lay_trail(W, P, cells, 1, end_y=ey, start_y=sy, inplot=appr)
        for c in cells:
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1): used.add((c[0] + dx, c[1] + dz))
        apc = [c for c in cells if W.inplot(*c)] if appr else []
        out.append(dict(a=a, b=b, card=card, cells=cells, approach=[list(c) for c in apc[::6] + apc[-1:]], line=[[round(x, 1), round(z, 1)] for x, z in pts], prof=[[round(x, 2), round(z, 2), s] for (x, z), s in prof],
                        stub_a=[list(c) for c in path[:i0 + 1]] if a not in ("R", "W") else [], stub_b=[list(c) for c in path[i1:]],
                        trail_len=round(sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(pts, pts[1:]))),
                        total_len=round(sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(path, path[1:])))))
        print(f"trail {a}->{b}: trail {out[-1]['trail_len']} (+stubs {len(out[-1]['stub_a'])}/{len(out[-1]['stub_b'])}), path {out[-1]['total_len']}, card {card}")
    return out
SPURS = [("weepers_mouth", (-452, -145), 92, "W")]   # T-023: (name, start at the edge of a place, feet y there, the trail it joins ('a' of TRAILS))
def spurs(W, P, tr):
    """short trails from an exit of a built place (its edge) to the nearest cell of a frame trail: the place itself is built by its own
    tool (T-023: the mouth of the Weepers' ravine -> the pass trail)"""
    out = []
    for name, (sx, sz), sy, ta in SPURS:
        cells = [t for t in tr if t["a"] == ta][0]["cells"]
        goal = min(cells, key=lambda c: math.hypot(c[0] - sx, c[1] - sz))
        box = (min(sx, goal[0]) - 30, min(sz, goal[1]) - 30, max(sx, goal[0]) + 30, max(sz, goal[1]) + 30)
        cost = cost_field(W, box, set())
        path = astar(W, (sx, sz), tuple(goal), cost, box)
        cl = cells_of(simplify(path, 3) if len(path) > 6 else path)
        prof = lay_trail(W, P, cl, 1, start_y=sy, inplot=True)
        out.append(dict(name=name, cells=cl, prof=[[round(x, 2), round(z, 2), s] for (x, z), s in prof]))
        print(f"spur {name}: {len(cl)} cells -> {goal}")
    return out
def signposts(W, P, tr):
    """at the forks: a post with an empty hanging sign towards each branch"""
    cnt = {}
    for t in tr:
        for c in set(t["cells"]): cnt[c] = cnt.get(c, 0) + 1
    posts = []
    for t in tr:
        cs = t["cells"]
        for i in range(1, len(cs)):
            if cnt.get(cs[i - 1], 0) >= 2 and cnt.get(cs[i], 0) == 1:     # leaving a shared stretch
                x, z = cs[min(i + 2, len(cs) - 1)]
                if any(math.hypot(x - px, z - pz) < 12 for px, pz in posts): continue
                posts.append((x, z))
    n = 0
    for (x, z) in posts:
        for (dx, dz) in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            px, pz = x + dx, z + dz
            if (px, W.at(px, pz) + 1, pz) in P.v: continue
            y = max([k[1] for k in P.v if k[0] == px and k[2] == pz and P.v[k] != "minecraft:air"] + [W.at(px, pz)])
            if any((px, yy, pz) in P.v and P.v[(px, yy, pz)] != "minecraft:air" for yy in range(y + 1, y + 4)): continue
            P.set(px, y + 1, pz, "spruce_fence"); P.set(px, y + 2, pz, "spruce_fence")
            P.set(px, y + 3, pz, "spruce_fence[east=true]" if dx >= 0 else "spruce_fence[west=true]")
            ax = px + (1 if dx >= 0 else -1)
            P.set(ax, y + 3, pz, "spruce_fence[west=true]" if dx >= 0 else "spruce_fence[east=true]")
            P.set(ax, y + 2, pz, "spruce_hanging_sign[rotation=%d]" % (4 if dx >= 0 else 12)); n += 1
            break
    return n

# ------------------------------------------------------------------ trees
def tree_spruce(P, x, y, z, hgt, leaves):
    for k in range(1, hgt + 1): P.set(x, y + k, z, "spruce_log[axis=y]")
    for k in range(3, hgt + 2):
        r = max(0, int((hgt + 1 - k) * 0.45)) if k < hgt + 1 else 0
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if abs(dx) + abs(dz) <= r + (k % 2) and (dx or dz or k > hgt): P.set(x + dx, y + k, z + dz, leaves)
    P.set(x, y + hgt + 1, z, leaves)
def tree_poplar(P, x, y, z, hgt, leaves):
    for k in range(1, hgt + 1): P.set(x, y + k, z, "poplar_log[axis=y]")
    for k in range(hgt // 2, hgt + 3):
        r = 1 if k < hgt + 1 else 0
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if (dx or dz or k > hgt) and not (abs(dx) == 1 and abs(dz) == 1 and hsh(x + dx, k, z + dz, 3) < 0.6): P.set(x + dx, y + k, z + dz, leaves)
def tree_dead(P, x, y, z, hgt, s):
    log = "dark_oak_log" if hsh(x, 0, z, 4) < 0.5 else "stripped_dark_oak_log"
    for k in range(1, hgt + 1): P.set(x, y + k, z, log + "[axis=y]")
    for i, (dx, dz, ax) in enumerate(((1, 0, "x"), (-1, 0, "x"), (0, 1, "z"), (0, -1, "z"))):
        if hsh(x, i, z, 6 + s) < 0.45:
            k = hgt - 1 - int(hsh(x, i, z, 9) * 3); L = 1 + int(hsh(x, i, z, 10) * 2)
            for l in range(1, L + 1): P.set(x + dx * l, y + k, z + dz * l, log + "[axis=%s]" % ax)
def forests(W, P, west_sel, east_sel, trail_cells):
    near = set()
    for (x, z) in trail_cells:
        for dx in range(-3, 4):
            for dz in range(-3, 4): near.add((x + dx, z + dz))
    gy, gx = np.gradient(W.H); slope = np.hypot(gx, gy); n = [0, 0]
    LEAVES = ["spruce_leaves[persistent=true,distance=1,waterlogged=false]", "red_poplar_leaves[persistent=true,distance=1,waterlogged=false]",
              "orange_poplar_leaves[persistent=true,distance=1,waterlogged=false]", "yellow_poplar_leaves[persistent=true,distance=1,waterlogged=false]"]
    for zi, xi in zip(*np.nonzero(west_sel | east_sel)):
        x, z = xi + W.x0, zi + W.z0
        if (x * 7 + z * 13) % 5: continue
        if hsh(x, 1, z, 77) > 0.22 or (x, z) in near or slope[zi, xi] > 1.15 or W.S[zi, xi] not in (S_FOREST, S_CHAR, S_GRASS): continue
        y = int(round(W.H[zi, xi]))
        if west_sel[zi, xi]:
            if W.H[zi, xi] > 140 or (x + 665) <= 0: continue
            r = hsh(x, 2, z, 78)
            if r < 0.55: tree_spruce(P, x, y, z, 7 + int(hsh(x, 3, z, 79) * 6), LEAVES[0])
            else: tree_poplar(P, x, y, z, 8 + int(hsh(x, 3, z, 80) * 5), LEAVES[1 + int(hsh(x, 4, z, 81) * 3)])
            n[0] += 1
        else:
            if W.H[zi, xi] > 150 or (x - 665) >= 0: continue
            tree_dead(P, x, y, z, 5 + int(hsh(x, 3, z, 82) * 6), 0); n[1] += 1
    return n

# ------------------------------------------------------------------ bridge and the pass rubble (gate templates)
def notch(W):
    """the north approach of the south bridge: the rim on the Dol side is ~30 higher than the south one (deck = the lower rim), so the
    road comes down to the deck in a cutting: graded 0.5 per block along x 0, side slopes 1:1.5, only lowering the ground"""
    gn = W.H[BRIDGE_Z[0] - 3 - W.z0, -W.x0]; gs = W.H[BRIDGE_Z[1] + 3 - W.z0, -W.x0]; deck = int(round(min(gn, gs)))
    for z in range(BRIDGE_Z[0] - 140, BRIDGE_Z[0] + 8):
        t = deck + 0.5 * max(0, BRIDGE_Z[0] - 6 - z)
        for x in range(-40, 41):
            zi, xi = z - W.z0, x - W.x0
            if W.touch[zi, xi] and W.R[zi, xi] != R_STONE and abs(W.Z[zi, 0] - 650) > 30: continue     # ridges, wall
            want = t + max(0, abs(x) - 3) * 1.5 if z < BRIDGE_Z[0] else (deck if abs(x) <= 3 else W.H[zi, xi])
            if want < W.H[zi, xi] - 0.4:
                W.H[zi, xi] = want; W.touch[zi, xi] = True
                W.S[zi, xi] = S_COARSE if abs(x) <= 6 else S_ROCK; W.R[zi, xi] = R_STONE
    return deck
def bridge(W, P):
    """South road bridge: deck 5 wide x 50 (z 625..674), three piers (z 632, 650, 668) down to the canyon floor; the middle part
    between the outer piers is a double bascule: closed = both leaves raised upright, open = deck through. Static: the end spans,
    the piers, the abutments. Template (x -2..2, z 633..667) is placed by the datapack (gate south_bridge)."""
    gn = W.at(0, BRIDGE_Z[0] - 3); gs = W.at(0, BRIDGE_Z[1] + 3)
    deck = int(round(min(gn, gs)))
    M = Mix({"stone_bricks": 50, "mossy_stone_bricks": 20, "cracked_stone_bricks": 15, "andesite": 15}, 501)
    floor_y = {}
    for z in range(BRIDGE_Z[0] - 6, BRIDGE_Z[1] + 7):
        for x in range(-4, 5): floor_y[(x, z)] = W.at(x, z)
    static = {}; tpl_closed = {}; tpl_open = {}
    def put(d, x, y, z, s): d[(x, y, z)] = s if ":" in s.split("[")[0] else "minecraft:" + s
    for z in range(BRIDGE_Z[0] - 6, BRIDGE_Z[1] + 7):
        lift = 633 <= z <= 667
        for x in range(-3, 4):
            edge = abs(x) == 3
            if lift: continue
            put(static, x, deck, z, "stone_bricks" if not edge else "stone_bricks")
            for yy in range(deck - 2, deck): put(static, x, yy, z, M.at(x, yy, z))
            if edge: put(static, x, deck + 1, z, "stone_brick_wall[east=none,north=low,south=low,up=true,waterlogged=false,west=none]")
            else:
                put(static, x, deck + 1, z, "air"); put(static, x, deck + 2, z, "air"); put(static, x, deck + 3, z, "air")
            # abutments down to the ground at the rims
            g = floor_y[(x, z)]
            for yy in range(min(g, deck - 3), deck - 2): put(static, x, yy, z, M.at(x, yy, z))
    for pz in (632, 650, 668):                 # piers 7x5 down to the floor, with cutwater ends
        for x in range(-4, 5):
            for z in range(pz - 2, pz + 3):
                if abs(x) == 4 and abs(z - pz) == 2: continue
                for yy in range(W.at(x, z) - 1, deck - (0 if pz != 650 else 0)): put(static, x, yy, z, M.at(x, yy, z))
        for x in range(-3, 4):
            put(static, x, deck, pz, "chiseled_stone_bricks" if x == 0 else "stone_bricks")
        if pz != 650:
            put(static, -3, deck + 1, pz, "stone_bricks"); put(static, 3, deck + 1, pz, "stone_bricks")
            put(static, -3, deck + 2, pz, "lantern[hanging=false,waterlogged=false]"); put(static, 3, deck + 2, pz, "lantern[hanging=false,waterlogged=false]")
    # bascule leaves: north leaf hinged at z 633, south leaf at z 667; length 16 (633..649 / 651..667), pier 650 in between
    for z in range(633, 668):
        if z == 650: continue
        for x in range(-3, 4):
            s = "stone_brick_wall[east=none,north=low,south=low,up=true,waterlogged=false,west=none]" if abs(x) == 3 else ("spruce_planks" if abs(x) < 3 else "stone_bricks")
            put(tpl_open, x, deck, z, "stone_bricks" if abs(x) == 3 else "spruce_planks")
            if abs(x) == 3: put(tpl_open, x, deck + 1, z, s)
            for yy in range(deck + 1 if abs(x) < 3 else deck + 2, deck + 18): put(tpl_open, x, yy, z, "air")
            put(tpl_closed, x, deck, z, "air"); put(tpl_closed, x, deck + 1, z, "air")
            for yy in range(deck + 2, deck + 18): put(tpl_closed, x, yy, z, "air")
    for hz, sgn in ((633, 1), (667, -1)):      # raised leaves: upright plank walls at the hinge, chains to the pier tops
        for x in range(-3, 4):
            for k in range(0, 16):
                put(tpl_closed, x, deck + k, hz, "spruce_planks" if abs(x) < 3 else "stone_bricks")
        for x in (-2, 2):
            put(tpl_closed, x, deck + 16, hz, "iron_chain[axis=y]"); put(tpl_closed, x, deck + 17, hz, "iron_chain[axis=y]")
    put(tpl_closed, 0, deck, 650, "chiseled_stone_bricks")
    for d in (static,): pass
    for k, s in static.items(): P.v[k] = s
    # approaches: graded ramps from the deck ends into the ground on both sides (5 wide)
    lay_trail(W, P, cells_of([(0.5, BRIDGE_Z[0] - 6.5), (0.5, BRIDGE_Z[0] - 105.5)]), 2, start_y=deck + 1)
    lay_trail(W, P, cells_of([(0.5, BRIDGE_Z[1] + 6.5), (0.5, BRIDGE_Z[1] + 70.5)]), 2, start_y=deck + 1)
    return deck, tpl_closed, tpl_open
def rubble(W, P, gorge_floor):
    """west pass rubble (card «Завал на Западном перевале»): closed = rock fall across the whole gorge up to 14 high, a fallen dead
    tree across; open = a 5-wide passage in the middle, blocks pushed to the walls, scorched faces of basalt and blackstone,
    the tree charred along the wall. Template 24x24x20, origin (x -652, z -202, y floor)."""
    ox, oz = -652, -202; fl = gorge_floor; cl = {}; op = {}
    z1, z2 = GORGE_Z
    def put(d, x, y, z, s): d[(x, y, z)] = s if ":" in s.split("[")[0] else "minecraft:" + s
    R = Mix({"stone": 35, "tuff": 25, "andesite": 25, "cobbled_deepslate": 15}, 601)
    for x in range(ox + 4, ox + 20):
        for z in range(z1, z2 + 1):
            base = int(round(W.H[z - W.z0, x - W.x0]))
            top = base + int(14 - abs(x - (ox + 12)) * 1.2 - hsh(x, 0, z, 602) * 3)
            for y in range(base + 1, top + 1): put(cl, x, y, z, R.at(x, y, z))
            # open: middle 5 (z -192..-188) cleared, sides keep a low heap
            mid = abs(z - (z1 + z2) / 2) <= 2
            for y in range(base + 1, top + 1): put(op, x, y, z, "air")
            if not mid:
                side = int(3 + hsh(x, 1, z, 603) * 4)
                for y in range(base + 1, base + side + 1):
                    put(op, x, y, z, ("basalt[axis=y]" if hsh(x, y, z, 604) < 0.5 else "blackstone") if y == base + side else R.at(x, y, z))
    tree_y = None
    for z in range(z1 - 0, z2 + 1):            # fallen dead tree across the gorge on top of the fall
        x = ox + 13; base = int(round(W.H[z - W.z0, x - W.x0])); top = max(k[1] for k in cl if k[0] == x and k[2] == z)
        put(cl, x, top + 1, z, "dark_oak_log[axis=z]")
    for x in range(ox + 6, ox + 17):            # open: the charred trunk along the north wall
        z = z1; base = int(round(W.H[z - W.z0, x - W.x0])); hp = max([k[1] for k in op if k[0] == x and k[2] == z and op[k] != "minecraft:air"] + [base])
        put(op, x, hp + 1, z, "stripped_dark_oak_log[axis=x]" if x % 3 else "coal_block" if False else "dark_oak_log[axis=x]")
    for k in list(cl):
        if k not in op: op[k] = "minecraft:air"
    return (ox, fl, oz), cl, op
def write_template(name, cells, origin):
    p = os.path.join(OUT, name + ".txt")
    mn = (min(k[0] for k in cells), min(k[1] for k in cells), min(k[2] for k in cells))
    with open(p, "w") as f:
        for (x, y, z), s in sorted(cells.items()): f.write(f"{x} {y} {z} {s}\n")
    d = os.path.join(ROOT, "datapack/data/last_ember/structure/gates"); os.makedirs(d, exist_ok=True)
    r = subprocess.run([os.path.join(ROOT, "tools/blockwriter.sh"), "nbt", p, str(mn[0]), str(mn[1]), str(mn[2]), os.path.join(d, name + ".nbt")], capture_output=True, text=True)
    out = [l for l in r.stdout.splitlines() if l.startswith("nbt:")]
    if r.returncode or not out: raise SystemExit(r.stdout + r.stderr)
    print(out[0]); return mn

# ------------------------------------------------------------------ plan picture
def plan(W, tr=None, bonf=None, path=None):
    from PIL import Image, ImageDraw
    X0, Z0, X1, Z1 = -760, -940, 760, 700
    s = W.sl(X0, Z0, X1 - 1, Z1 - 1); H = W.H[s]; wat = (W.Wn[s] != NONE) & ~W.touch[s]
    cols = np.array([[52, 92, 50], [86, 124, 60], [140, 150, 80], [160, 132, 88], [140, 110, 92], [128, 128, 128], [235, 235, 235]])
    lv = np.clip(((H - 60) / 22).astype(int), 0, 6); rgb = cols[lv].astype(np.uint8)
    cont = (np.floor(H / 10) != np.floor(np.roll(H, 1, 0) / 10)) | (np.floor(H / 10) != np.floor(np.roll(H, 1, 1) / 10)); rgb[cont] = (rgb[cont] * 0.6).astype(np.uint8)
    rgb[wat] = [50, 80, 170]
    wall = (W.R[s] == R_WALL_N) | (W.R[s] == R_WALL_S); rgb[wall & W.touch[s]] = [170, 210, 235]
    im = Image.fromarray(rgb); d = ImageDraw.Draw(im)
    P_ = lambda x, z: (x - X0, z - Z0)
    for p in W.plots:
        if p["kind"] == "rect":
            d.rectangle([P_(p["cx"] - p["w"] / 2, p["cz"] - p["d"] / 2), P_(p["cx"] + p["w"] / 2, p["cz"] + p["d"] / 2)], outline=(200, 30, 30), width=3)
            m = p["m"]; d.rectangle([P_(p["cx"] - p["w"] / 2 - m, p["cz"] - p["d"] / 2 - m), P_(p["cx"] + p["w"] / 2 + m, p["cz"] + p["d"] / 2 + m)], outline=(230, 120, 120), width=1)
            d.text(P_(p["cx"] - p["w"] / 2 + 4, p["cz"] - p["d"] / 2 + 4), p["id"], fill=(255, 255, 210))
        else:
            r = p["r"]; m = p["m"]
            d.ellipse([P_(p["cx"] - r, p["cz"] - r), P_(p["cx"] + r, p["cz"] + r)], outline=(200, 30, 30), width=3)
            d.ellipse([P_(p["cx"] - r - m, p["cz"] - r - m), P_(p["cx"] + r + m, p["cz"] + r + m)], outline=(230, 120, 120), width=1)
            d.text(P_(p["cx"] - r + 4, p["cz"] - 6), p["id"], fill=(255, 255, 210))
    d.ellipse([P_(-REFUGE_R, -REFUGE_R), P_(REFUGE_R, REFUGE_R)], outline=(255, 230, 160), width=2)
    for b in (("x", -665, -620, 650), ("x", 665, -870, 650), ("z", -870, -720, 720), ("z", 650, -720, 720), ("z", -620, -720, -665)):
        if b[0] == "x": d.line([P_(b[1], b[2]), P_(b[1], b[3])], fill=(10, 10, 10), width=2)
        else: d.line([P_(b[2], b[1]), P_(b[3], b[1])], fill=(10, 10, 10), width=2)
    if tr:
        for t in tr:
            d.line([P_(x + .5, z + .5) for x, z in t["cells"]], fill=(250, 220, 120), width=4)
            for st in (t["stub_a"], t["stub_b"]):
                if len(st) > 1: d.line([P_(x + .5, z + .5) for x, z in st], fill=(250, 220, 120), width=1)
    for n, bid, x, y, z in (bonf or []):
        d.ellipse([P_(x - 7, z - 7), P_(x + 7, z + 7)], fill=(255, 130, 0), outline=(0, 0, 0)); d.text(P_(x + 9, z - 6), str(n), fill=(255, 255, 255))
    d.rectangle([P_(DOOR[0] - 3, DOOR[1] - 5), P_(DOOR[0] + 3, DOOR[1] + 5)], fill=(120, 220, 120)); d.text(P_(DOOR[0] + 5, DOOR[1] + 4), "sc", fill=(200, 255, 200))
    for (x, z, t_) in ((PASS[0], PASS[1], "pass"), (0, 650, "bridge")):
        d.rectangle([P_(x - 6, z - 6), P_(x + 6, z + 6)], fill=(255, 255, 255)); d.text(P_(x + 8, z + 4), t_, fill=(255, 255, 255))
    for x in range(-700, 701, 100):
        for z in range(-900, 700, 100): d.point(P_(x, z), fill=(255, 255, 255))
    d.text((8, 8), "T-022 R1 plan: places of locations (red, pale = +margin), trails (yellow), bonfires (orange), borders (black), 1px = 1 block, dots every 100", fill=(255, 255, 255))
    im.save(path)

# ------------------------------------------------------------------ main
def build():
    W = World(); feats = {}
    # 1. borders' relief
    wcrest = lambda n: np.clip(170 + 22 * fbm1(n, (140, 50, 18), 21), 150, 190)
    feats["west"] = ridge(W, -665, "z", -650, 680, wcrest, 70, 34, 1, R_WEST, S_FOREST, S_ROCK, 172, 30)
    feats["watch"] = ridge(W, -620, "x", -744, -640, lambda n: np.clip(182 + 16 * fbm1(n, (40, 15), 22), 160, 200), 38, 38, 1, R_WEST, S_ROCK, S_ROCK, 172, 40, taper=24)
    M = north_ridge(W)
    ecrest = lambda n: np.clip(175 + 26 * fbm1(n, (150, 50, 18), 23), 150, 200)
    feats["east"] = ridge(W, 665, "z", -900, 680, ecrest, 70, 34, -1, R_EAST, S_CHAR, S_CHAR, 999, 31)
    hw, fl = rift(W)
    gorge(W)
    notch(W)
    door_y = ledge(W)
    bonf = pads(W)
    # 2. water guard: a rewritten column lower than natural water within 2 blocks would let it leak -> keep it water
    Wn = W.Wn.astype(float); Wn[Wn == NONE] = -1e9; mx = Wn.copy()
    for dz in (-2, -1, 0, 1, 2):
        for dx in (-2, -1, 0, 1, 2): mx = np.maximum(mx, np.roll(np.roll(Wn, dz, 0), dx, 1))
    wet = W.touch & (mx > W.H + 0.5) & (np.abs(W.Z - 650) > 30)
    W.Wset[wet] = mx[wet].astype(int)
    # 3. grid file (chunks that are not generated are never written)
    W.touch &= ~W.missing
    Hi = np.where(W.touch, np.round(W.H), NONE).astype(np.int32)
    nb = np.round(W.H).astype(np.int32)
    lo = nb.copy()
    for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): lo = np.minimum(lo, np.roll(np.roll(nb, dz, 0), dx, 1))
    F = np.minimum(np.minimum(nb, W.G.astype(np.int32)), lo) - 4
    write_grid(os.path.join(OUT, "terrain.bin"), W.x0, W.z0, Hi, F, W.Wset, W.S, W.R, W.A)
    W.H = np.where(W.touch, np.round(W.H), W.G)
    print(f"terrain: {int(W.touch.sum())} columns rewritten")
    # 4. placements: trails, signposts, bridge, forests, wall scree
    P = Placer()
    tr = trails(W, P, bonf, door_y)
    sp = spurs(W, P, tr)
    nsign = signposts(W, P, tr)
    deck, bc, bo = bridge(W, P)
    gfl = int(round(W.H[(GORGE_Z[0] + GORGE_Z[1]) // 2 - W.z0, PASS[0] - W.x0]))
    origin, rc, ro = rubble(W, P, gfl)
    nf = forests(W, P, feats["west"], feats["east"], [c for t in tr for c in t["cells"]])
    scree(W, P, M)
    ncor, nscr = rift_details(W, P); print(f"rift: cornices {ncor} blocks, scree {nscr} blocks")
    with open(os.path.join(OUT, "r1.txt"), "w") as f:
        for (x, y, z), s in sorted(P.v.items(), key=lambda kv: (kv[0][1], kv[0][0], kv[0][2])): f.write(f"{x} {y} {z} {s}\n")
    mb = write_template("south_bridge_closed", bc, None); mo = write_template("south_bridge_open", bo, None)
    mr = write_template("west_pass_closed", rc, None); write_template("west_pass_open", ro, None)
    update_files(bonf, door_y, mb, mr)
    meta = dict(bonfires=bonf, door=[DOOR[0], door_y, DOOR[1]], bridge=dict(deck=deck, at=list(mb)), pass_=dict(at=list(mr), floor=gfl),
                trails=tr, spurs=sp, signs=nsign, trees=nf, rift_hw=[float(hw.min()), float(hw.max())])
    json.dump(meta, open(os.path.join(OUT, "r1.json"), "w"))
    np.savez_compressed(os.path.join(OUT, "allow.npz"), allow=W.allow, x0=W.x0, z0=W.z0)    # columns r1_check plots may find changed
    name = {n: bid for n, bid, *_ in bonf}; name.update({"R": "refuge", "W": "pass", "S": "south_road"})
    rows = [f"# approach {name[t['a']]}->{name[t['b']]}: " + " ".join(f"{x},{z}" for x, z in t["approach"]) for t in tr if t["approach"]]
    replace_lines(os.path.join(ROOT, "tools/build/r1_plots.txt"), ["# approach "], rows)
    print(f"placements: {len(P.v)} blocks; signposts {nsign}; trees west {nf[0]} east {nf[1]}; bridge deck y {deck} template at {mb}; rubble at {mr}; door y {door_y}")
    os.makedirs(os.path.join(ROOT, "docs/reports/T-022"), exist_ok=True)
    plan(W, tr, bonf, os.path.join(ROOT, "docs/reports/T-022/r1_plan.png"))
def replace_lines(path, keys, new):
    """replace the lines that start with one of keys by `new` (in place of the first one; appended when none)"""
    lines = open(path, encoding="utf-8").read().split("\n"); out = []; done = False
    for l in lines:
        if any(l.startswith(k) for k in keys):
            if not done: out += new; done = True
            continue
        out.append(l)
    if not done:
        while out and out[-1] == "": out.pop()
        out += new + [""]
    open(path, "w", encoding="utf-8").write("\n".join(out))
def update_files(bonf, door_y, mb, mr):
    """bonfires of R1, the two gate templates, the west gap by the gorge, the R1 shortcut door: written into the data files"""
    replace_lines(os.path.join(ROOT, "bonfires/bonfires.txt"), [f"{n} " for n, *_ in bonf] + [f"{n}  " for n, *_ in bonf],
                  [f"{n:<2} {bid:<13} overworld  {x} {y} {z}  normal  r1" + ("  nofade" if n in NOFADE else "") for n, bid, x, y, z in bonf])
    g = os.path.join(ROOT, "gates/gates.txt"); gz = GORGE_Z
    replace_lines(g, ["border west_ridge"], [f"border west_ridge   x -665  -620  650   gap={gz[0]}..{gz[1]}:west_pass"])
    replace_lines(g, ["border rift"], ["border rift         z  650  -1500 1500  gap=-2..2:south_bridge"])
    replace_lines(g, ["gate west_pass"], [f'gate west_pass     r2    chapter=1 at={mr[0]},{mr[1]},{mr[2]} closed=last_ember:gates/west_pass_closed open=last_ember:gates/west_pass_open hold=-664,{gz[0] - 1},{mr[0] - 1},{gz[1] + 1} text="Где-то на западе обрушился завал."'])
    replace_lines(g, ["gate south_bridge"], [f'gate south_bridge  r4    chapter=3 at={mb[0]},{mb[1]},{mb[2]} closed=last_ember:gates/south_bridge_closed open=last_ember:gates/south_bridge_open text="На юге опустился мост."'])
    replace_lines(g, ["# shortcut r1 ", "shortcut r1 "], [f"shortcut r1 door={DOOR[0]},{door_y},{DOOR[1]} yaw=270 open=near:24 build=1      # T-022: у Круга Плакальщиц, лицом на восток, в скальном выступе"])
def scree(W, P, M):
    """ice blocks along both faces of the Wall, a strip 10 wide, up to +8 (card «Стена», осыпь)"""
    ICE = Mix({"packed_ice": 60, "blue_ice": 25, "snow_block": 15}, 701)
    for z0, sgn in ((-850, 1), (-889, -1)):
        for x in range(-650, 101):
            for k in range(1, 11):
                z = z0 + sgn * k
                if hsh(x // 3, k // 3, z, 702) > 0.35 - 0.02 * k or M[z - W.z0, x - W.x0] == 200 or W.pd[z - W.z0, x - W.x0] <= 0: continue
                g = int(round(W.H[z - W.z0, x - W.x0])); ht = int((11 - k) * 0.8 * hsh(x // 2, 0, z // 2, 703))
                for y in range(g + 1, g + 1 + ht): P.set(x, y, z, ICE.at(x, y, z))
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "plan":
        W = World(); plan(W, None, None, os.path.join(OUT, "plan.png"))
    else: build()
