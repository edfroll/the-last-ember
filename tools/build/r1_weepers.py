#!/usr/bin/env python3
"""T-023: the Circle of the Weepers (Р1, Altar I) on its place `weepers` of tools/build/r1_plots.txt (centre (-420,-180), r 32 + 16).

  python3 tools/build/r1_weepers.py      -> server/build/r1/weepers_terrain.bin (tools/terrain.sh apply), weepers.txt (tools/blockwriter.sh apply),
                                            weepers.json (points for the tests and the walk bot), docs/reports/T-023/weepers_plan.png,
                                            datapack structure/weepers/*.nbt (statues in two poses x two orientations, the core of the tree
                                            before / after) and function/weepers/gen/* (template placement, sync probes, tears, labels, markers)
Inputs: server/build/r1/base.bin (the ground before the R1 frame, as r1.py), weepers_pre.bin (scan of the place after the frame: pad
        and approach columns keep their heights), allow.npz (r1.py: the pad and approach columns inside the place).
Writes only inside the place (core + margin) and never the pad / approach columns of T-022 nor the shortcut ledge. A re-run gives the
same Circle. The statues and the core of the tree are not written offline: the datapack places their templates (weepers/gen/sync), so
the state after the event survives re-runs and restarts.

Layout (card «Круг Плакальщиц», HQ T-023): a clearing on a rock ledge level with bonfire 6 (ground y 110), the mosaic circle (d 21)
with an outer paved ring, 8 Weepers on r 14, 4 pedestals of chiseled tuff on r 9 in front of the key statues, the dead tree 5x5 x 28 in
the middle, three ruined arches; the ravine with the stream along the west side (north -> south), the stair of 21 steps cut into its east
wall up to the west arch, the ravine mouth in the south (the spur trail of r1.py leads on to the pass trail)."""
import json, math, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import Scan, write_grid, NONE
from lib import B, Mix, h as hsh, slab
from connect import connect
import weepers_statue as WS
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "server/build/r1")
DP = os.path.join(ROOT, "datapack/data/last_ember")
CX, CZ = -420, -180          # centre of the circle = the trunk's middle column
G = 110                      # ground top of the clearing (bonfire 6: hearth y 111 on the pad y 110)
Y = G + 1
R_PLOT, MARGIN = 32, 16
BOX = (CX - 56, CZ - 56, CX + 56, CZ + 56)          # work grid x1 z1 x2 z2
LEDGE = (-398, -207, -372, -187)                     # the shortcut ledge of r1.py (x1 z1 x2 z2): never written
# surface / rock styles of Terrain.java
S_GRASS, S_FOREST, S_BED, S_MOSS, S_FLAT, S_ROCK = 1, 2, 5, 6, 7, 10
R_STONE, R_WEST = 0, 1
# ---------------------------------------------------------------- the pieces
TRUNK = (CX - 2, CZ - 2, CX + 2, CZ + 2)            # 5x5
CORE = (CX - 2, Y + 3, CZ - 2, CX + 2, Y + 8, CZ + 2)   # template box of the core: x1 y1 z1 x2 y2 z2 (cavity 3x3x6 at y 114..119 + the slits)
CAVITY = [(x, y, z) for x in range(CX - 1, CX + 2) for z in range(CZ - 1, CZ + 2) for y in range(Y + 3, Y + 9)]
SLITS = [(CX - 1, CZ + 2), (CX + 1, CZ + 2), (CX - 1, CZ - 2), (CX + 1, CZ - 2), (CX + 2, CZ), (CX - 2, CZ)]   # 6 slits 1x4 in the bark
SLIT_Y = range(Y + 4, Y + 8)
TOP = (CX, Y + 28, CZ)                               # the point of the strike (over the crown)
R_STATUE = 14
KEYS = {45: ("thread_labyrinth", 45, "Он искал выход между живых стен. Стены помнят его шаги."),
        90: ("tear_creaker", 90, "Он вошёл в белый сад, где никто не говорит. Теперь молчит и он."),
        135: ("signet_king", 90, "Он ушёл служить спящему королю. Король всё ещё спит."),
        180: ("crown_witches", 180, "Он просил у трёх сестёр совета. Они дали ему три.")}
#   ring angle -> (key, facing, inscription): the key Weepers look towards their key points (labyrinth NE, garden E, castle E, witches S;
#   the two that look east stand side by side); the other four look at the tree
def statues():
    out = []
    for a in range(0, 360, 45):
        x = CX + int(round(R_STATUE * math.sin(math.radians(a)))); z = CZ - int(round(R_STATUE * math.cos(math.radians(a))))
        if a in KEYS: key, face, text = KEYS[a]
        else: key, face, text = None, (a + 180) % 360, None
        out.append(dict(a=a, x=x, z=z, face=face, key=key, text=text))
    return out
def pedestals():
    out = []
    for a, (key, face, text) in KEYS.items():
        out.append(dict(a=a, key=key, x=CX + int(round(9 * math.sin(math.radians(a)))), y=Y, z=CZ - int(round(9 * math.cos(math.radians(a))))))
    return out
# the ravine (west side, north -> south) and the stair
RAV_X = (-457, -451)               # floor
STREAM_X = (-456, -455)
RAV_Z = (-205, -146)               # north end .. mouth
RIM_X = (-460, -458)
STAIR_X = (-449, -447)
STAIR_Z0 = -163                    # first step (feet 90 before it), the steps climb north 1 per block
def floor_y(z):
    if z <= -191: return 94
    if z <= -177: return 93
    if z <= -165: return 91
    return 89
def bank_s2(z):
    """walking surface of the floor in half blocks (bank x -453..-451): flat, then the mouth climbs 0.5 per block to the natural ground"""
    if z <= -150: return 2 * (floor_y(z) + 1)
    return min(2 * 92, 2 * 90 + (z + 150) * 1)          # z -149 -> 90.5 ... z -146 -> 92
def stair_y(z): return Y - 1 - (z - (STAIR_Z0 - 20)) if STAIR_Z0 - 20 <= z <= STAIR_Z0 else None   # z -163 -> 90 ... z -183 -> 110
ARCHES = [  # (centre x, z, along the arch (dx, dz) unit, pillar half-gap, state): the west one is the gateway at the stair head
    (-444, -185, (0, 1), 3, "whole"), (-409, -199, (1, 0), 2, "broken_l"), (-428, -160, (1, 0), 2, "broken_r")]
ADVISOR = (-442, Y, -185, -90.0)    # the Advisor's hint point: at the west arch, looking east at the circle (yaw -90)

# ---------------------------------------------------------------- terrain
def vnoise(X, Z, cell, seed):
    """smooth value noise in [0, 1) over world coordinates (deterministic)"""
    gx, gz = np.floor_divide(X, cell), np.floor_divide(Z, cell); fx = (X - gx * cell) / cell; fz = (Z - gz * cell) / cell
    fx = fx * fx * (3 - 2 * fx); fz = fz * fz * (3 - 2 * fz)
    hv = np.vectorize(lambda a, b: hsh(int(a), 0, int(b), seed))
    a, b_, c, d = hv(gx, gz), hv(gx + 1, gz), hv(gx, gz + 1), hv(gx + 1, gz + 1)
    return (a * (1 - fx) + b_ * fx) * (1 - fz) + (c * (1 - fx) + d * fx) * fz
def plot_mask(X, Z):
    r = np.hypot(X - CX, Z - CZ); return r <= R_PLOT + MARGIN
def terrain():
    x1, z1, x2, z2 = BOX; X, Z = np.meshgrid(np.arange(x1, x2 + 1), np.arange(z1, z2 + 1))
    base = Scan(os.path.join(OUT, "base.bin")); pre = Scan(os.path.join(OUT, "weepers_pre.bin"))
    def grid(s, a): return a[z1 - s.z0:z2 - s.z0 + 1, x1 - s.x0:x2 - s.x0 + 1].astype(float)
    nat = grid(base, base.ground); now = grid(pre, pre.ground)
    al = np.load(os.path.join(OUT, "allow.npz")); A = al["allow"]; ax0, az0 = int(al["x0"]), int(al["z0"])
    allow = A[z1 - az0:z2 - az0 + 1, x1 - ax0:x2 - ax0 + 1].copy()
    ledge = (X >= LEDGE[0]) & (X <= LEDGE[2]) & (Z >= LEDGE[1]) & (Z <= LEDGE[3])
    inside = plot_mask(X, Z) & ~allow & ~ledge
    r = np.hypot(X - CX, Z - CZ)
    fixed = np.zeros(X.shape, bool); T = nat.copy(); S = np.full(X.shape, S_FOREST, np.uint8); Rk = np.zeros(X.shape, np.uint8)
    Wt = np.full(X.shape, NONE)
    def fix(m, v, s=None, rk=R_WEST):
        m = m & inside; T[m] = v[m] if isinstance(v, np.ndarray) else v; fixed[m] = True
        if s is not None: S[m] = s
        Rk[m] = rk
    # the clearing and the ledge between it and the ravine
    terr = (r <= 24.5) | ((X >= -446) & (X <= -425) & (Z >= -204) & (Z <= -164))
    fix(terr, G, S_MOSS)
    # the east wall of the ravine north of the stair (a cliff from the floor to the ledge)
    fix((X >= -450) & (X <= -446) & (Z >= RAV_Z[0]) & (Z <= -184), G, S_ROCK, R_WEST)
    # floor of the ravine, the stream, the west rim
    fz = np.vectorize(floor_y)(Z)
    rav = (X >= RAV_X[0]) & (X <= RAV_X[1]) & (Z >= RAV_Z[0]) & (Z <= RAV_Z[1])
    fix(rav, fz, S_FLAT, R_WEST)
    for z in range(RAV_Z[0], RAV_Z[1] + 1):        # the mouth and the walking bank (half blocks: slabs are placements)
        s2 = bank_s2(z); top = s2 // 2 - 1
        fix(rav & (Z == z), np.full(X.shape, float(top)), S_FLAT, R_WEST)
    stream = (X >= STREAM_X[0]) & (X <= STREAM_X[1]) & (Z >= RAV_Z[0]) & (Z <= -152)
    fix(stream, fz - 2, S_FLAT, R_WEST)
    Wt[stream & inside] = (fz - 1)[stream & inside].astype(int)
    rimv = np.maximum(fz + 4, nat)
    rim = (X >= RIM_X[0]) & (X <= RIM_X[1]) & (Z >= RAV_Z[0]) & (Z <= -150)
    fix(rim, np.minimum(rimv, 100), S_ROCK, R_WEST)
    # the stair: its columns, the parapet column on the ravine side
    for z in range(STAIR_Z0 - 20, STAIR_Z0 + 1):
        sy = stair_y(z)
        fix((X >= STAIR_X[0]) & (X <= STAIR_X[1]) & (Z == z), sy - 1, S_ROCK, R_WEST)
        fix((X == STAIR_X[0] - 1) & (Z == z), sy, S_ROCK, R_WEST)
    fix((X >= STAIR_X[0] - 1) & (X <= STAIR_X[1]) & (Z >= STAIR_Z0 + 1) & (Z <= STAIR_Z0 + 2), 89, S_FLAT, R_WEST)    # the stair foot
    fix((X >= STAIR_X[0]) & (X <= STAIR_X[1]) & (Z >= STAIR_Z0 - 23) & (Z <= STAIR_Z0 - 21), G, S_MOSS)             # the landing at the top
    # outside the place: as it is now; inside: free cells keep the natural ground within the 1:1 slopes of the fixed cells
    fixed |= ~inside; T[~inside] = now[~inside]
    U = np.where(fixed, T, 1e9); L = np.where(fixed, T, -1e9)
    SLOPE = 0.75                                    # the seam falls / rises at most 3 blocks per 4 (no wall above 4 except the ravine)
    for _ in range(90):
        Up = np.pad(U, 1, constant_values=1e9); Lp = np.pad(L, 1, constant_values=-1e9)
        nu = U.copy(); nl = L.copy()
        for dz in (0, 1, 2):
            for dx in (0, 1, 2):
                nu = np.minimum(nu, Up[dz:dz + U.shape[0], dx:dx + U.shape[1]] + SLOPE); nl = np.maximum(nl, Lp[dz:dz + L.shape[0], dx:dx + L.shape[1]] - SLOPE)
        U = np.where(fixed, T, nu); L = np.where(fixed, T, nl)
    free = ~fixed
    v = np.where(L <= U, np.clip(nat, L, U), U)       # where the bounds cross (the ravine walls) the lower one wins: the higher side is the cliff
    rough = (vnoise(X, Z, 5, 2361) - 0.5) * 2.2 * np.clip((np.minimum(np.abs(v - nat), 6)) / 3, 0, 1)   # rocky knoll, not terraces: rough where filled/cut
    T[free] = np.round(np.clip(v + rough, L - 0.5, U + 0.5)[free])
    gy, gx = np.gradient(T); slope = np.hypot(gx, gy)
    S[free] = np.where(slope[free] > 0.9, S_ROCK, np.where(vnoise(X, Z, 7, 2362)[free] < 0.45, S_MOSS, S_FOREST)); Rk[free] = R_WEST
    # every column at the top of a drop of more than 2 shows rock, not a band of dirt
    Tn = T.copy()
    for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): Tn = np.minimum(Tn, np.roll(np.roll(T, dz, 0), dx, 1))
    edge = inside & (T - Tn > 2) & (S != S_FLAT)
    S[edge] = S_ROCK
    # water guard: every neighbour of a water column is water or holds it
    for _ in range(3):
        wl = np.where(Wt != NONE, Wt, -10**6)
        for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nwl = np.roll(np.roll(wl, dz, 0), dx, 1)
            low = inside & (Wt == NONE) & (nwl > -10**6) & (T < nwl)
            T[low] = nwl[low]
    # only the columns whose ground is not yet what it should be: a re-run on the built Circle rewrites no column (the entities of the
    # altar, the labels and the templates stay); trees on the clearing are cleared by air placements (blocks()), not by the terrain
    wnow = grid(pre, pre.water)
    return dict(X=X, Z=Z, T=T, nat=nat, now=now, inside=inside, Wt=Wt, wnow=wnow, x1=x1, z1=z1, terr=terr, S=S, Rk=Rk)

def write_terrain(tr, b, sts):
    """only the columns whose ground is not yet what it should be: a re-run on the built Circle rewrites no column (terrain apply removes
    the entities of the touched columns: the altar, the labels). Ground higher than wanted under our own blocks (statues, pedestals,
    arches, the stair, the rock on the faces: the scan sees them as ground) is not a reason to rewrite."""
    T, now, inside, Wt, X, Z, x1, z1, nat = tr["T"], tr["now"], tr["inside"], tr["Wt"], tr["X"], tr["Z"], tr["x1"], tr["z1"], tr["nat"]
    top = np.full(T.shape, -999, int); Tr = np.round(T).astype(int)       # the top of our own blocks over the wanted ground
    for (x, y, z), st in b.v.items():
        if str(st).split("[")[0] in ("minecraft:air", "air", "minecraft:cave_air"): continue
        i, j = z - z1, x - x1
        if 0 <= i < T.shape[0] and 0 <= j < T.shape[1] and y > Tr[i, j]: top[i, j] = max(top[i, j], y)
    for st in sts:
        m = (np.abs(X - st["x"]) <= WS.K) & (np.abs(Z - st["z"]) <= WS.K); top[m] = np.maximum(top[m], Y + WS.H - 1)
    own = now <= top                                                      # the scan sees our blocks (or less), not a hill to cut
    touch = inside & ((now < T - 0.4) | ((now > T + 0.4) & ~own) | ((Wt != NONE) & (tr["wnow"] != Wt)))
    H = np.where(touch, T, NONE).astype(np.int32)
    lo = np.round(T).astype(np.int32)
    for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): lo = np.minimum(lo, np.roll(np.roll(lo, dz, 0), dx, 1))
    F = np.minimum(np.minimum(np.round(T).astype(np.int32), nat.astype(np.int32)), lo) - 4
    write_grid(os.path.join(OUT, "weepers_terrain.bin"), x1, z1, H, F, np.where(touch, Wt, NONE), tr["S"], tr["Rk"], np.zeros(X.shape, np.uint8))
    tr["touch"] = touch

# ---------------------------------------------------------------- blocks
CIRCLE = Mix({"stone_bricks": 30, "mossy_stone_bricks": 20, "tuff_bricks": 15, "mossy_cobblestone": 15, "cracked_stone_bricks": 10, "chiseled_stone_bricks": 0.01}, 2311)
RING = Mix({"tuff_bricks": 30, "mossy_cobblestone": 30, "cracked_stone_bricks": 20, "stone_bricks": 20}, 2312)
def ground_at(x, z):
    """moss with patches of podzol and rooted dirt (patches, not a checkerboard)"""
    n = float(vnoise(np.array(x), np.array(z), 5, 2313)); m = hsh(x, 0, z, 2318)
    if n < 0.28: return "minecraft:podzol[snowy=false]" if m < 0.8 else "minecraft:coarse_dirt"
    if n > 0.78: return "minecraft:rooted_dirt" if m < 0.75 else "minecraft:moss_block"
    return "minecraft:moss_block" if m < 0.9 else "minecraft:podzol[snowy=false]"
class Bark(Mix):
    def __init__(self): pass
    """stripped pale oak with 5 charred patches of dark oak (2x3 .. 3x5: more at the foot and at the crown, where the strike comes;
    HQ review T-023, 3) and a few mangrove roots"""
    # patch: centre (dx, dy, dz) from the trunk's foot centre, horizontal and vertical half-sizes
    PATCHES = [((2, 2, 0), 1.7, 2.6), ((-2, 4, 1), 1.5, 2.2), ((0, 1, -2), 2.0, 1.6), ((1, 12, 2), 1.4, 2.0), ((0, 24, 0), 1.6, 3.4)]
    def at(self, x, y, z):
        for (px, py, pz), rh, rv in self.PATCHES:
            dx, dy, dz = x - CX - px, y - Y - py, z - CZ - pz
            if (dx * dx + dz * dz) / (rh * rh) + dy * dy / (rv * rv) <= 1.0: return "minecraft:dark_oak_log[axis=y]"
        if hsh(x, y, z, 2314) < 0.08: return "minecraft:mangrove_roots[waterlogged=false]"
        return "minecraft:stripped_pale_oak_log[axis=y]"
BARK = Bark()
CORE_ON = Mix({"shroomlight": 55, "ochre_froglight[axis=y]": 45}, 2315)
ARCH = Mix({"stone_bricks": 40, "mossy_stone_bricks": 30, "cracked_stone_bricks": 20, "tuff_bricks": 10}, 2316)
STAIR = Mix({"stone_brick_stairs": 60, "mossy_stone_brick_stairs": 40}, 2317)
def tree(b):
    """the dead tree: trunk 5x5 (corners cut above the root flare) to y 128, 3x3 to 134, 1x1 to 138; roots; bare branches with hanging moss"""
    for y in range(Y, Y + 28):
        for x in range(CX - 2, CX + 3):
            for z in range(CZ - 2, CZ + 3):
                ring = max(abs(x - CX), abs(z - CZ))
                corner = abs(x - CX) == 2 and abs(z - CZ) == 2
                if y <= Y + 17: ok = not corner or y <= Y + 2
                elif y <= Y + 23: ok = ring <= 1
                else: ok = ring == 0
                if ok: b.set(x, y, z, BARK)
    # roots: 8 buttresses on the ground
    for i, (dx, dz) in enumerate(((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1))):
        L = 3 + int(hsh(i, 0, 0, 2321) * 3)
        for k in range(1, L + 1):
            x = CX + dx * (2 + k) - (dx if abs(dx) == abs(dz) else 0); z = CZ + dz * (2 + k) - (dz if abs(dx) == abs(dz) else 0)
            if k == 1: b.set(x, Y + 1, z, "mangrove_roots[waterlogged=false]")
            b.set(x, Y, z, "mangrove_roots[waterlogged=false]" if hsh(x, 0, z, 2322) < 0.6 else ("dark_oak_log[axis=x]" if dx else "dark_oak_log[axis=z]"))
    # branches
    n = 0
    for i in range(14):
        a = math.radians(i * 137.5 + 20); y0 = Y + 12 + int(hsh(i, 1, 0, 2323) * 15); L = 4 + int(hsh(i, 2, 0, 2324) * 6)
        sx = CX + (2 if math.sin(a) > 0.5 else -2 if math.sin(a) < -0.5 else 0); sz = CZ + (-2 if math.cos(a) > 0.5 else 2 if math.cos(a) < -0.5 else 0)
        if y0 > Y + 17: sx = CX + (1 if sx > CX else -1 if sx < CX else 0); sz = CZ + (1 if sz > CZ else -1 if sz < CZ else 0)
        px, pz, py = sx + 0.5, sz + 0.5, y0
        for k in range(L):
            px += math.sin(a); pz -= math.cos(a); py += 0.45 + 0.25 * hsh(i, k, 0, 2325)
            x, y, z = int(math.floor(px)), int(round(py)), int(math.floor(pz))
            if math.hypot(x - CX, z - CZ) > 11: break
            axis = "x" if abs(math.sin(a)) > abs(math.cos(a)) else "z"
            st = ("dark_oak_log[axis=%s]" % axis) if hsh(x, y, z, 2326) < 0.35 else ("stripped_pale_oak_log[axis=%s]" % axis)
            b.set(x, y, z, st); n += 1
            if k > 1 and hsh(x, y, z, 2327) < 0.45 and b.get(x, y - 1, z) in (None, "minecraft:air"):
                h = 1 + int(hsh(x, y, z, 2328) * 4)
                for j in range(1, h + 1):
                    if b.get(x, y - j, z) not in (None, "minecraft:air"): break
                    b.set(x, y - j, z, "pale_hanging_moss[tip=%s]" % ("true" if j == h else "false"))
            if k == L - 1 or hsh(x, y, z, 2329) < 0.2:     # a twig up
                b.set(x, y + 1, z, "stripped_pale_oak_log[axis=y]")
    for y in (Y + 28, Y + 29):                              # the broken crown tip
        b.set(CX, y, CZ, "dark_oak_log[axis=y]")
    return n
def core_cells(after):
    """{(x,y,z): state} of the core template box (the bark around as the tree has it)"""
    t = B("t"); tree(t); out = {}
    x1, y1, z1, x2, y2, z2 = CORE
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            for z in range(z1, z2 + 1): out[(x, y, z)] = t.get(x, y, z) or "minecraft:air"
    for c in CAVITY: out[c] = CORE_ON.at(*c) if after else "minecraft:stripped_pale_oak_log[axis=y]"
    for (x, z) in SLITS:
        for y in SLIT_Y: out[(x, y, z)] = "minecraft:shroomlight" if after else "minecraft:stripped_pale_oak_log[axis=y]"
    return out
def arch(b, cx, cz, d, g, state):
    """two pillars at +-g along d, 7 high, a lintel over them with top-half stairs at the inner corners; ruined: one pillar broken off
    low, the lintel only as a stub on the standing pillar, fallen blocks on the ground"""
    dx, dz = d; hgt = {-1: 7, 1: 7}
    if state == "broken_l": hgt[-1] = 3
    if state == "broken_r": hgt[1] = 4
    for side in (-1, 1):
        px, pz = cx + side * g * dx, cz + side * g * dz
        for y in range(Y, Y + hgt[side]): b.set(px, y, pz, ARCH)
        b.set(px, Y, pz, "chiseled_stone_bricks")
    stand = [-1, 1] if state == "whole" else ([1] if state == "broken_l" else [-1])
    for k in range(-g + 1, g):
        side = -1 if k < 0 else 1
        if state != "whole" and (k * stand[0] < 0 or k == 0 or abs(k) < g - 1): continue
        x, z = cx + k * dx, cz + k * dz; b.set(x, Y + 6, z, ARCH)
        if abs(k) == g - 1:
            f = ("east" if k < 0 else "west") if dx else ("south" if k < 0 else "north")
            b.set(x, Y + 5, z, "stone_brick_stairs[facing=%s,half=top,shape=straight,waterlogged=false]" % f)
    for i in range(0 if state == "whole" else 4):  # fallen blocks beside a ruined arch (the whole one stands on the way: none)
        o = 2 + i % 2; fx = cx + dz * o * (1 if i < 2 else -1) + dx * (i - 1); fz = cz + dx * o * (1 if i < 2 else -1) + dz * (i - 1)
        if b.get(fx, Y, fz) in (None, "minecraft:air"): b.set(fx, Y, fz, ARCH if i % 2 else "cracked_stone_bricks")
def blocks(tr):
    b = B("weepers"); T = tr["T"]
    def gt(x, z): return int(round(T[z - tr["z1"], x - tr["x1"]]))
    skip = set()
    for s in statues():
        px, pz, diag, rot = WS.place_pos(s["x"], s["z"], s["face"])
        for x in range(s["x"] - WS.K, s["x"] + WS.K + 1):
            for z in range(s["z"] - WS.K, s["z"] + WS.K + 1): skip.add((x, z))
    # ground of the clearing, the mosaic, the paved ring
    for x in range(CX - 26, CX + 27):
        for z in range(CZ - 26, CZ + 27):
            if not tr["inside"][z - tr["z1"], x - tr["x1"]] or gt(x, z) != G: continue
            r = math.hypot(x - CX, z - CZ)
            if r <= 10.5:
                inlay = abs(r - 5.0) < 0.5 or abs(r - 10.0) < 0.5 or (abs(r - 7.5) < 0.5 and (round(math.degrees(math.atan2(x - CX, z - CZ))) % 45) < 8)
                b.set(x, G, z, "calcite" if inlay else CIRCLE)
            elif r <= 16.5: b.set(x, G, z, "calcite" if abs(r - 16.0) < 0.5 and hsh(x, 0, z, 2341) < 0.7 else RING)
            elif r <= 24.5 or (x >= -446 and x <= -425):
                b.set(x, G, z, ground_at(x, z))
                if hsh(x, 1, z, 2342) < 0.18 and (x, z) not in skip: b.set(x, Y, z, "pale_moss_carpet[bottom=true,east=none,north=none,south=none,west=none]")
    tree(b)
    for x in range(CX - 26, CX + 27):             # the clearing is open sky: natural trees and plants over it go (air where nothing of ours)
        for z in range(CZ - 26, CZ + 27):
            zi, xi = z - tr["z1"], x - tr["x1"]
            if not (tr["inside"][zi, xi] and tr["terr"][zi, xi]) or (x, z) in skip: continue
            for y in range(gt(x, z) + 1, G + 40):
                if b.get(x, y, z) is None: b.set(x, y, z, "air")
    for c in list(b.v):        # the core box belongs to the templates
        if CORE[0] <= c[0] <= CORE[3] and CORE[1] <= c[1] <= CORE[4] and CORE[2] <= c[2] <= CORE[5]: del b.v[c]
    for p in pedestals():
        b.set(p["x"], p["y"], p["z"], "chiseled_tuff"); b.set(p["x"], p["y"] + 1, p["z"], "air"); b.set(p["x"], p["y"] + 2, p["z"], "air")
    for a in ARCHES: arch(b, *a)
    # the stair, its parapet, slabs of the walking bank
    for z in range(STAIR_Z0 - 20, STAIR_Z0 + 1):
        sy = stair_y(z)
        for x in range(STAIR_X[0], STAIR_X[1] + 1):
            b.set(x, sy, z, STAIR.at(x, sy, z) + "[facing=north,half=bottom,shape=straight,waterlogged=false]")
            for yy in range(sy + 1, sy + 5): b.set(x, yy, z, "air")
        b.set(STAIR_X[0] - 1, sy + 1, z, "stone_brick_wall" if hsh(0, sy, z, 2351) < 0.6 else "mossy_stone_brick_wall")
    for z in range(STAIR_Z0 - 25, STAIR_Z0 - 20):          # a low wall along the landing over the ravine
        b.set(STAIR_X[0] - 1, Y, z, "mossy_stone_brick_wall" if z % 2 else "stone_brick_wall")
    for z in range(RAV_Z[0], RAV_Z[1] + 1):
        s2 = bank_s2(z)
        if s2 % 2:
            for x in range(-454, -450): b.set(x, s2 // 2, z, slab("mossy_cobblestone_slab") if hsh(x, 0, z, 2352) < 0.4 else slab("cobblestone_slab"))
    # rock faces: knobs and ledges of rock stick out of every face higher than 4 (ravine walls, the ledge), above head height
    FACE = Mix({"andesite": 30, "tuff": 25, "cobblestone": 15, "mossy_cobblestone": 20, "stone": 10}, 2371)
    nf = 0
    for x in range(BOX[0] + 1, BOX[2]):
        for z in range(BOX[1] + 1, BOX[3]):
            if not tr["inside"][z - tr["z1"], x - tr["x1"]]: continue
            hi = gt(x, z)
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                qx, qz = x + dx, z + dz; lo = gt(qx, qz)
                if hi - lo <= 4 or not tr["inside"][qz - tr["z1"], qx - tr["x1"]] or (STAIR_X[0] <= qx <= STAIR_X[1] and STAIR_Z0 - 23 <= qz <= STAIR_Z0): continue
                for y in range(lo + 3, hi):
                    r = hsh(qx, y // 2, qz, 2372)
                    if r < 0.16 and b.get(qx, y, qz) is None:
                        b.set(qx, y, qz, FACE); nf += 1
                        if r < 0.03 and b.get(qx, y - 1, qz) is None and y - 1 > lo + 2: b.set(qx, y - 1, qz, "pale_hanging_moss[tip=true]")
    connect(b)
    for (x, y, z) in list(b.v):
        if (x, z) in skip and y >= Y: del b.v[(x, y, z)]
    return b

# ---------------------------------------------------------------- templates and datapack
def write_nbt(name, cells):
    mn = (min(k[0] for k in cells), min(k[1] for k in cells), min(k[2] for k in cells))
    p = os.path.join(OUT, "tpl_" + name + ".txt")
    with open(p, "w") as f:
        for (x, y, z), s in sorted(cells.items()): f.write(f"{x} {y} {z} {s}\n")
    d = os.path.join(DP, "structure/weepers"); os.makedirs(d, exist_ok=True)
    r = subprocess.run([os.path.join(ROOT, "tools/blockwriter.sh"), "nbt", p, str(mn[0]), str(mn[1]), str(mn[2]), os.path.join(d, name + ".nbt")], capture_output=True, text=True)
    if r.returncode or "nbt:" not in r.stdout: raise SystemExit(r.stdout + r.stderr)
    return mn
def gen_datapack(sts):
    G_ = os.path.join(DP, "function/weepers/gen"); os.makedirs(G_, exist_ok=True)
    for f in os.listdir(G_):
        if f.endswith(".mcfunction"): os.remove(os.path.join(G_, f))
    def w(n, lines): open(os.path.join(G_, n + ".mcfunction"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    for pose in ("up", "down"):
        for diag in (False, True): write_nbt("statue_%s_%s" % ("diag" if diag else "ortho", pose), WS.template(pose, diag))
    write_nbt("core_before", core_cells(False)); write_nbt("core_after", core_cells(True))
    hdr = "# generated by tools/build/r1_weepers.py: "
    for pose in ("up", "down"):
        L = [hdr + "the 8 Weepers in the pose '%s' (place template, pivot = template origin)" % pose]
        for s in sts:
            px, pz, diag, rot = WS.place_pos(s["x"], s["z"], s["face"])
            L.append("place template last_ember:weepers/statue_%s_%s %d %d %d %s" % ("diag" if diag else "ortho", pose, px, Y, pz, rot))
        w("statues_" + pose, L)
    w("core_before", [hdr + "the core of the tree: dark", "place template last_ember:weepers/core_before %d %d %d" % (CORE[0], CORE[1], CORE[2])])
    w("core_after", [hdr + "the core of the tree: burning from inside", "place template last_ember:weepers/core_after %d %d %d" % (CORE[0], CORE[1], CORE[2])])
    # sync probes: a cell solid in 'up' / air in 'down' per statue, the cavity centre for the core
    up = []; dn = []
    for s in sts:
        px, pz, diag, rot = WS.place_pos(s["x"], s["z"], s["face"]); c = WS.probe(diag); wx, wy, wz = WS.world_cell(s["x"], Y, s["z"], s["face"], c)
        up.append("execute unless block %d %d %d minecraft:air run return 1" % (wx, wy, wz)); dn.append("execute if block %d %d %d minecraft:air run return 1" % (wx, wy, wz))
    w("probe_up", [hdr + "1 when some Weeper does not stand in the pose 'up'"] + dn + ["return 0"])
    w("probe_down", [hdr + "1 when some Weeper does not stand in the pose 'down'"] + up + ["return 0"])
    cc = (CX, Y + 5, CZ)
    w("probe_core", [hdr + "core: 1 = dark (stripped log), 2 = burning, 0 = something else (not built yet)",
                     "execute if block %d %d %d minecraft:stripped_pale_oak_log run return 1" % cc, "execute if block %d %d %d #last_ember:weepers_core_on run return 2" % cc, "return 0"])
    xs = [s["x"] for s in sts]; zs = [s["z"] for s in sts]
    lo = (min(xs) - WS.K, min(zs) - WS.K); hi = (max(xs) + WS.K, max(zs) + WS.K)
    w("loaded", [hdr + "1 when every chunk of the Circle is loaded"] + ["execute unless loaded %d %d %d run return 0" % (x, Y, z) for x in range(lo[0] - lo[0] % 16, hi[0] + 1, 16) for z in range(lo[1] - lo[1] % 16, hi[1] + 1, 16)] +
      ["execute unless loaded %d %d %d run return 0" % (hi[0], Y, hi[1]), "return 1"])
    # tears: the niches at the eyes
    L = [hdr + "the tears of the 8 Weepers (at the niches by the eyes), called every 2 ticks during the event"]
    for s in sts:
        px, pz, diag, rot = WS.place_pos(s["x"], s["z"], s["face"]); e = WS.world_cell(s["x"], Y, s["z"], s["face"], WS.eye(diag))
        L.append("particle minecraft:dripping_water %.1f %d.3 %.1f 0.12 0.05 0.12 0 2 force @a[distance=..64]" % (e[0] + .5, e[1], e[2] + .5))
        L.append("particle minecraft:falling_dust{block_state:\"minecraft:calcite\"} %.1f %d.2 %.1f 0.1 0.05 0.1 0 1 force @a[distance=..64]" % (e[0] + .5, e[1], e[2] + .5))
    w("tears", L)
    # labels on the plinths of the key Weepers + the markers
    L = [hdr + "the inscriptions on the plinths of the key Weepers (text_display, dim, readable from ~6 blocks)", "kill @e[type=minecraft:text_display,tag=le.wp_lbl]"]
    for s in sts:
        if not s["text"]: continue
        # on the face of the plinth that looks most towards the centre (ortho plinth 5x5: a side; diag plinth: a stepped diagonal side)
        vx, vz = CX - s["x"], CZ - s["z"]; diag = WS.facing_rot(s["face"])[0]
        cands = [(1, 1), (1, -1), (-1, 1), (-1, -1)] if diag else [(1, 0), (-1, 0), (0, 1), (0, -1)]
        nx, nz = max(cands, key=lambda c: (c[0] * vx + c[1] * vz) / math.hypot(*c)); L_ = math.hypot(nx, nz); ux, uz = nx / L_, nz / L_
        off = 2.85 if diag else 2.53
        lx, lz = s["x"] + 0.5 + ux * off, s["z"] + 0.5 + uz * off
        yaw = math.degrees(math.atan2(-ux, uz))                  # the text faces the centre (towards the reader standing at the circle)
        L.append('summon minecraft:text_display %.2f %.2f %.2f {Tags:["le.wp_lbl"],Rotation:[%.1ff,0f],billboard:"fixed",line_width:120,background:0,'
                 'see_through:0b,view_range:0.12f,brightness:{sky:5,block:4},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.42f,0.42f,0.42f]},'
                 'text:{"text":"%s","color":"#8f8a80","italic":true}}' % (lx, Y + 0.35, lz, (yaw + 180) % 360 - 180, s["text"]))
    L.append("data modify storage last_ember:weepers built set value 1b")
    w("labels", L)
    w("markers", [hdr + "mechanic points of the Circle (storage only)", "data remove storage last_ember:r1 m.weepers_advisor",
                  "data modify storage last_ember:r1 m.weepers_advisor set value {pos:[%d,%d,%d],yaw:%.1ff}" % ADVISOR,
                  "data modify storage last_ember:r1 m.weepers_strike set value [%d,%d,%d]" % TOP])
    tag = os.path.join(DP, "tags/block/weepers_core_on.json"); os.makedirs(os.path.dirname(tag), exist_ok=True)
    json.dump({"values": ["minecraft:shroomlight", "minecraft:ochre_froglight"]}, open(tag, "w"), indent=2)
    return [WS.world_cell(s["x"], Y, s["z"], s["face"], WS.eye(WS.facing_rot(s["face"])[0])) for s in sts]

def plan(tr, b, sts, path):
    from PIL import Image, ImageDraw
    x1, z1 = tr["x1"], tr["z1"]; T = tr["T"]; n = T.shape[0]; S = 6
    img = Image.new("RGB", (n * S, n * S)); d = ImageDraw.Draw(img)
    tops = {}
    for (x, y, z), s in b.v.items():
        if s != "minecraft:air" and (y >= tops.get((x, z), (-999,))[0]): tops[(x, z)] = (y, s)
    for s in sts:
        for (x, y, z), st in WS.world(s["x"], Y, s["z"], s["face"], "up").items():
            if st != "minecraft:air" and y >= tops.get((x, z), (-999,))[0]: tops[(x, z)] = (y, st)
    for zi in range(n):
        for xi in range(n):
            x, z = xi + x1, zi + z1; h = T[zi, xi]; c = int(np.clip((h - 80) * 6, 0, 255))
            col = (40 + c // 3, 60 + c // 2, 40 + c // 4)
            if tr["Wt"][zi, xi] != NONE: col = (50, 80, 180)
            if not tr["inside"][zi, xi]: col = tuple(int(v * 0.55) for v in col)
            t = tops.get((x, z))
            if t:
                s = t[1]
                col = (235, 235, 225) if "calcite" in s or "diorite" in s or "smooth_stone" in s else (200, 170, 120) if "pale_oak" in s else (90, 60, 40) if "dark_oak" in s or "mangrove" in s else \
                      (120, 120, 120) if "brick" in s or "cobble" in s or "stairs" in s else (170, 140, 90) if "tuff" in s else (150, 160, 120) if "moss" in s else col
            d.rectangle([xi * S, zi * S, xi * S + S - 1, zi * S + S - 1], fill=col)
    d.ellipse([(CX - x1 - 48) * S, (CZ - z1 - 48) * S, (CX - x1 + 49) * S, (CZ - z1 + 49) * S], outline=(230, 120, 120))
    d.ellipse([(CX - x1 - 32) * S, (CZ - z1 - 32) * S, (CX - x1 + 33) * S, (CZ - z1 + 33) * S], outline=(200, 30, 30), width=2)
    d.text((6, 6), "T-023 Circle of the Weepers: plan (1 block = %d px), red = place (+margin), north up" % S, fill=(255, 255, 255))
    img.save(path)

def data_files(tr):
    """the altar of chapter I and its pedestals (altars/altars.txt), the zones of the Circle (zones/zones.txt)"""
    from r1 import replace_lines
    rows = ["1 weepers overworld %d %d %d ev=last_ember:weepers/ev nofx       # T-023: Circle of the Weepers (tools/build/r1_weepers.py)" % (CX, Y, CZ)]
    rows += ["ped %d %d %d %s" % (p["x"], p["y"], p["z"], p["key"]) for p in pedestals()]
    replace_lines(os.path.join(ROOT, "altars/altars.txt"), ["1 weepers ", "ped "], rows)
    lo = int(min(tr["T"][tr["inside"]].min(), 86)) - 1
    replace_lines(os.path.join(ROOT, "zones/zones.txt"), ["weepers "], ["weepers         overworld cyl  %d %d 32  %d %d                  # T-023: Circle of the Weepers, Altar I (bottom of the ravine .. the crown + 10)" % (CX, CZ, lo, TOP[1] + 10)])
    replace_lines(os.path.join(ROOT, "zones/zones.txt"), ["weepers_circle "], ["weepers_circle  overworld cyl  %d %d 14  %d %d     no_spawn" % (CX, CZ, G - 4, TOP[1] + 10)])
def main():
    tr = terrain(); b = blocks(tr); sts = statues(); write_terrain(tr, b, sts)
    n = b.write_placements(os.path.join(OUT, "weepers.txt"))
    # every write must be inside the place
    bad = [k for k in b.v if math.hypot(k[0] - CX, k[2] - CZ) > R_PLOT + MARGIN]
    if bad: raise SystemExit("blocks outside the place: %s" % bad[:5])
    eyes = gen_datapack(sts); data_files(tr)
    meta = dict(centre=[CX, Y, CZ], top=list(TOP), statues=sts, pedestals=pedestals(), eyes=eyes, advisor=list(ADVISOR),
                stair=dict(bottom=[-448, 90, STAIR_Z0 + 2], top=[-448, Y, STAIR_Z0 - 22]), mouth=[-452, 92, -145],
                core=list(CORE), arches=[a[:2] for a in ARCHES], terrain_columns=int(tr["touch"].sum()), blocks=n)
    json.dump(meta, open(os.path.join(OUT, "weepers.json"), "w"), ensure_ascii=False)
    os.makedirs(os.path.join(ROOT, "docs/reports/T-023"), exist_ok=True)
    plan(tr, b, sts, os.path.join(ROOT, "docs/reports/T-023/weepers_plan.png"))
    print(f"weepers: terrain {int(tr['touch'].sum())} columns, {n} blocks, statues {len(sts)}, pedestals {len(pedestals())}")
if __name__ == "__main__": main()
