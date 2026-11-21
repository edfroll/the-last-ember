"""T-028: the block models of the approaches to the Enchanted Castle (the colossi, the sword of the fallen Bearer, the pier, the causeway,
the descent from bonfire 7, the stair in the rock with the rest platform and the niches, the bridge, the barbican, the lanterns, the trees)
for tools/build/r1_castle.py. Palettes from the card «Заколдованный замок и Колоссы · Р1»."""
import math
import numpy as np
from lib import Mix, h as hsh
import castle_plan as P
from castle_plan import W

def st(name, **p): return "minecraft:%s[%s]" % (name, ",".join("%s=%s" % kv for kv in p.items())) if p else "minecraft:" + name
def stairs(block, facing, half="bottom", shape="straight"): return st(block, facing=facing, half=half, shape=shape, waterlogged="false")
def slab(block, t="bottom"): return st(block, type=t, waterlogged="false")
def lantern(hanging=False): return st("lantern", hanging="true" if hanging else "false", waterlogged="false")
def sign_nbt(lines):
    m = ",".join('{"text":"%s"}' % t for t in lines + [""] * (4 - len(lines)))
    return "{is_waxed:1b,front_text:{messages:[%s]},back_text:{messages:[%s]}}" % (m, m)
AIR = "minecraft:air"
LOG = st("stripped_dark_oak_log", axis="y")

class PatchMix:
    """a palette in patches 2..5 blocks across, not block by block (HQ review T-028, 1-2): 3-D value noise (two octaves) made uniform by
    its ranks, the weights cut the ranks; the same salt in several PatchMix keeps the patches in place while the shares change"""
    _cdf = {}
    def __init__(self, weights, salt, cell=3.2):
        tot = sum(weights.values()); acc = 0; self.t = []
        for k, w in weights.items(): acc += w / tot; self.t.append((acc, k if ":" in k.split("[")[0] else "minecraft:" + k))
        self.salt, self.cell = salt, cell
        key = (salt, cell)
        if key not in PatchMix._cdf:
            pts = [(int(P.jhash(i, 1, 2, 9) * 4000), int(P.jhash(i, 3, 4, 9) * 400), int(P.jhash(i, 5, 6, 9) * 4000)) for i in range(5000)]
            PatchMix._cdf[key] = sorted(self.raw(*q) for q in pts)
    def raw(self, x, y, z):
        return 0.72 * vnoise3(x, y, z, self.cell, self.salt) + 0.28 * vnoise3(x + 17, y, z - 9, self.cell / 2.1, self.salt + 1)
    def at(self, x, y, z):
        import bisect
        c = PatchMix._cdf[(self.salt, self.cell)]; r = bisect.bisect_left(c, self.raw(x, y, z)) / len(c)
        for a, k in self.t:
            if r <= a: return k
        return self.t[-1][1]

def vnoise3(x, y, z, cell, salt):
    """Terrain.java vnoise3 (the same values)"""
    fx, fy, fz = x / cell, y / cell, z / cell; xi, yi, zi = math.floor(fx), math.floor(fy), math.floor(fz)
    tx, ty, tz = fx - xi, fy - yi, fz - zi; tx, ty, tz = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty), tz * tz * (3 - 2 * tz)
    acc = 0.0
    for a in (0, 1):
        for b_ in (0, 1):
            for c in (0, 1):
                acc += P.jhash(xi + a, yi + b_, zi + c, salt) * (tx if a else 1 - tx) * (ty if b_ else 1 - ty) * (tz if c else 1 - tz)
    return acc
def vnoise(x, z, salt):
    """Terrain.java vnoise(x, z, salt) (arguments already divided by the cell)"""
    xi, zi = math.floor(x), math.floor(z); fx, fz = x - xi, z - zi; fx, fz = fx * fx * (3 - 2 * fx), fz * fz * (3 - 2 * fz)
    a, b_, c, d = P.jhash(xi, 0, zi, salt), P.jhash(xi + 1, 0, zi, salt), P.jhash(xi, 0, zi + 1, salt), P.jhash(xi + 1, 0, zi + 1, salt)
    return (a * (1 - fx) + b_ * fx) * (1 - fz) + (c * (1 - fx) + d * fx) * fz
STRATA = ["stone", "stone", "tuff", "stone", "cobbled_deepslate", "stone", "tuff"]
def rock_at(x, y, z, H):
    """the castle rock at a block (Terrain.java castleRock, the same function): strata, andesite patches, moss thicker to the top H"""
    d = H - y
    if vnoise3(x, y, z, 2.6, 92) > 0.735 - 0.15 * max(0.0, 1 - d / 10.0): return "minecraft:moss_block" if P.jhash(x, y, z, 93) < 0.6 else "minecraft:mossy_cobblestone"
    if vnoise3(x + 31, y, z - 17, 3.4, 94) > 0.63: return "minecraft:andesite"
    band = y + vnoise(x / 17.0, z / 17.0, 95) * 3 + vnoise(x / 6.0, z / 6.0, 96) * 1.2
    return "minecraft:" + STRATA[math.floor(band / 3.0) % len(STRATA)]
def top_at(x, y, z, depth):
    """the top of the castle rock (Terrain.java castleTop): stone with patches of moss and grass; None = rock"""
    n = vnoise(x / 4.3, z / 4.3, 97) * 0.7 + vnoise(x / 1.9, z / 1.9, 98) * 0.3
    top = ("stone" if vnoise(x / 2.5, z / 2.5, 99) < 0.6 else "andesite") if n < 0.40 else "moss_block" if n < 0.62 else "grass_block[snowy=false]"
    if depth == 0: return "minecraft:" + top
    if depth == 1: return "minecraft:dirt" if top.startswith("grass") else "minecraft:moss_block" if top == "moss_block" else None
    return None
STAIR_OF = {"stone": "stone_stairs", "tuff": "tuff_stairs", "cobbled_deepslate": "cobbled_deepslate_stairs", "andesite": "andesite_stairs",
            "moss_block": "mossy_cobblestone_stairs", "mossy_cobblestone": "mossy_cobblestone_stairs"}

COL_LO = PatchMix({"stone": 24, "andesite": 20, "tuff": 16, "mossy_cobblestone": 24, "moss_block": 16}, 2810)   # the card: 30/25/20/15/10,
COL = PatchMix({"stone": 32, "andesite": 27, "tuff": 21, "mossy_cobblestone": 13, "moss_block": 7}, 2810)       # more moss low, less high
COL_HI = PatchMix({"stone": 36, "andesite": 30, "tuff": 24, "mossy_cobblestone": 10}, 2810)
CROWN = Mix({"gold_block": 7, "raw_gold_block": 3}, 2813)
PLINTH = Mix({"stone_bricks": 4, "mossy_stone_bricks": 4, "cracked_stone_bricks": 1, "mossy_cobblestone": 2}, 2814)
CAUSE = Mix({"cobblestone": 5, "mossy_cobblestone": 4, "stone_brick_slab[type=top,waterlogged=false]": 2}, 2815)
PIER = Mix({"stone_bricks": 5, "mossy_stone_bricks": 3, "cobblestone": 2}, 2816)
CASTLE = Mix({"stone_bricks": 30, "tuff_bricks": 20, "mossy_stone_bricks": 15, "andesite": 15, "cracked_stone_bricks": 10, "polished_tuff": 10}, 2817)
BRIDGE = Mix({"stone_bricks": 6, "mossy_stone_bricks": 2, "cracked_stone_bricks": 1, "tuff_bricks": 1}, 2818)
PAVE = Mix({"stone_bricks": 5, "cobblestone": 3, "mossy_stone_bricks": 2}, 2819)
DEEP = Mix({"cobbled_deepslate": 4, "deepslate_bricks": 1}, 2820)
EYE_SLEEP, EYE_LIT, EYE_DIM = "minecraft:polished_blackstone", "minecraft:pearlescent_froglight[axis=y]", "minecraft:crying_obsidian"

# ---------------------------------------------------------------- the colossi: kings 50 high from W, backs to the face, facing west
def colossus(zc, side):
    """cells {(x, y, z): state} of a colossus whose plinth is x 420..431, z zc-5..zc+5; side = +1 raises the arm on the south (+z)
    side, -1 on the north. Local frame: u = 431 - x (0 at the back, 11 the front of the plinth), v = z - zc, r = y - W. Returns
    (cells, meta) with the eye cells, the raised arm cells (the fade breaks it off) and the strike point (the open palm).
    Pose (HQ review T-028, 2): the head stands clear of the shoulders on a neck one block narrower (and the beard), the crown; the raised
    arm: shoulder -> upper arm out and up -> the forearm upright -> the open palm (4 wide) facing the lake with three fingers and the
    thumb, above the head; the other arm hangs along the body, the hand on the grip of a sword standing on the plinth."""
    m = {}; arm = set(); eyes = []
    def put(u, v, r, s): m[(431 - u, W + r, zc + v)] = s
    def pal(u, v, r): return (COL_LO if r < 16 else COL if r < 34 else COL_HI).at(431 - u, W + r, zc + v)
    def rk(u, v, r): put(u, v, r, pal(u, v, r))
    for r in range(-6, 6):                                       # the plinth from the lake floor to W+5, sheer sides
        for u in range(0, 12):
            for v in range(-5, 6): put(u, v, r, PLINTH.at(431 - u, W + r, zc + v))
    for r in (6, 7):                                             # the toes under the hem
        for u in (8, 9, 10):
            for v in (-3, -2, -1, 1, 2, 3): rk(u, v, r)
    def fold(k): return k % 2 == 0
    for r in range(6, 30):                                       # the robe: vertical folds on the front and the sides
        front = 8 if r < 10 else 7; hw = 4
        for u in range(1, front + 2):
            for v in range(-hw - 1, hw + 2):
                f = front + (1 if fold(v) else 0); s_ = hw + (1 if fold(u) and r < 26 else 0)
                if u <= f and abs(v) <= s_: rk(u, v, r)
    for r in (30, 31):                                           # the belt
        for u in range(2, 9):
            for v in range(-4, 5): put(u, v, r, "minecraft:polished_andesite")
    for r in range(32, 38):                                      # the chest
        for u in range(2, 8 + (1 if r >= 35 else 0)):
            for v in range(-4, 5): rk(u, v, r)
    for r in (38, 39):                                           # the shoulders, round caps over the arms
        for u in range(2, 8):
            for v in range(-5, 6): rk(u, v, r)
    for r in (37, 38, 39):
        for u in (3, 4, 5, 6):
            for v in (-6, 6): rk(u, v, r)
    for u in (4, 5, 6):                                          # the neck (one narrower than the head on each side)
        for v in range(-2, 3): rk(u, v, 40)
    for r in range(36, 42):                                      # the hair falling behind, narrower than the head
        for v in range(-2, 3): rk(2, v, r)
    for r in range(41, 48):                                      # the head (7 wide, 6 deep)
        for u in range(3, 9):
            for v in range(-3, 4): rk(u, v, r)
    for r in range(36, 43):                                      # the beard in front of the chest and the chin (narrower than the head)
        w_ = 1 if r <= 38 else 2
        for v in range(-w_, w_ + 1): rk(9, v, r)
    for v in range(-3, 4): rk(9, v, 46)                          # the brow over the eyes
    rk(9, 0, 44); rk(9, 0, 45)                                   # the nose
    for v in (-2, -1, 1, 2):                                     # the eye sockets: 2 x 2 niches, the eye block one deep (u 7)
        for r in (44, 45):
            put(8, v, r, AIR); put(7, v, r, EYE_SLEEP); eyes.append((431 - 7, W + r, zc + v))
    for u in range(3, 9):                                        # the crown: a band of gold at r 48, tines at r 49..50
        for v in range(-3, 4):
            if u in (3, 8) or abs(v) == 3:
                put(u, v, 48, CROWN.at(431 - u, W + 48, zc + v))
                if (u + v) % 2 == 0: put(u, v, 49, CROWN.at(431 - u, W + 49, zc + v)); put(u, v, 50, "minecraft:gold_block" if (u * 3 + v) % 4 else "minecraft:raw_gold_block")
            else: rk(u, v, 48)
    # the lowered arm (outer side o): the upper arm hangs along the body (v 6..7), the forearm comes forward to the hand on the grip of
    # a sword whose blade stands on the front edge of the plinth (u 10, v 5)
    o = -side
    for r in range(30, 37):
        for u in (3, 4, 5):
            for vv in (6, 7): rk(u, o * vv, r)
    for t in range(8):                                           # the forearm: elbow (u 4, r 29) -> wrist (u 9, r 22)
        uc = 4 + round(t * 5 / 7); r = 29 - t
        for u in (uc, uc + 1):
            for vv in (6, 7): rk(u, o * vv, r)
    for r in range(20, 24):                                      # the fist round the grip
        for u in (9, 10, 11):
            for vv in (4, 5, 6): rk(u, o * vv, r)
    for r in range(6, 19): put(10, o * 5, r, "minecraft:polished_andesite")      # the blade
    for vv in range(3, 8): put(10, o * vv, 19, "minecraft:polished_tuff")       # the guard
    put(10, o * 5, 24, "minecraft:chiseled_tuff")                               # the pommel over the fist
    # the raised arm (inner side, over the channel): the upper arm out and up from the shoulder cap, the forearm upright, the open palm
    # (v 5..8, r 53..56) facing the lake at u 6 with three fingers (gap at v 6) and the thumb towards the head
    cells = [(u, vv, r) for u in (4, 5) for (vv, r) in ((6, 40), (7, 40), (6, 41), (7, 41), (7, 42), (8, 42), (7, 43), (8, 43))]
    cells += [(u, vv, r) for u in (4, 5) for vv in (7, 8) for r in range(44, 53)]
    palm = [(u, vv, r) for u in (5, 6) for vv in (5, 6, 7, 8) for r in range(53, 57)]
    fingers = [(6, 5, r) for r in (57, 58, 59)] + [(6, 7, r) for r in (57, 58, 59, 60)] + [(6, 8, r) for r in (57, 58)]
    thumb = [(6, 4, 54), (6, 4, 55), (6, 3, 56), (6, 3, 57)]
    for (u, vv, r) in cells + palm + fingers + thumb:
        v = side * vv; rk(u, v, r); arm.add((u, v, r))
    armw = {(431 - u, W + r, zc + v) for (u, v, r) in arm}
    strike = [431 - 6 - 0.5, W + 55.0, zc + side * 6.5 + 0.5]
    return m, dict(eyes=eyes, arm=sorted(armw), strike=strike, zc=zc, side=side, box=[420, W - 6, zc - 8, 431, W + 60, zc + 8])

def recess(b, gr, rl):
    """the colossi stand clear of the rock (HQ review T-028, 2): behind each colossus the face of the bridgehead (x 432..433) is hollowed
    from the plinth (W+6) up to 4 under the top, 2 beyond the colossus on each side: a dark gap round its back. The roof stays (the top
    of the rock and its edge do not change)."""
    n = 0
    for zc in (-46, -21):
        for x in (P.FACE_X, P.FACE_X + 1):
            for z in range(zc - 7, zc + 8):
                i, j = P.ix(gr, x, z)
                if not rl["rock"][i, j] or (x, z) in rl["hang"]: continue
                top = int(rl["T"][i, j])
                for y in range(W + 6, top - 3):
                    if b.get(x, y, z) is None: b.set(x, y, z, AIR); n += 1
    return n

def face_grooves(b, gr, rl):
    """the west face of the bridgehead over the lake south of the south colossus (z -13..4: no growth there, the lake is under it): vertical
    grooves 1..2 wide, 1..2 deep, from W+4 (out of reach from the water) up to 3..8 under the top, the roof stays: the columnar rock"""
    n = 0; z = -13
    while z <= 4:
        w = 1 + int(hsh(0, 1, z, 2898) < 0.4); deep = 1 + int(hsh(0, 2, z, 2899) < 0.3)
        for zz in range(z, min(z + w, 5)):
            for x in range(P.FACE_X, P.FACE_X + deep):
                i, j = P.ix(gr, x, zz)
                if not rl["rock"][i, j] or (x, zz) in rl["hang"] or gr["pad"][i, j]: continue
                top = int(rl["T"][i, j]); y2 = top - 3 - int(hsh(x, 3, zz, 2900) * 6)
                for y in range(W + 4 + int(hsh(x, 4, zz, 2901) * 4), y2):
                    if b.get(x, y, zz) is None: b.set(x, y, zz, AIR); n += 1
        z += w + 1 + int(hsh(0, 5, z, 2902) * 2)
    return n

def overhangs(b, gr, rl):
    """the blocks of the overhangs (castle_plan.relief: rl["hang"]): the top k blocks of the rock's palette, the lowest one an upside-down
    stair stepped towards the rock (the overhang widens upward), the top like the rock top, moss carpet on part of the moss"""
    T = rl["T"]; n = 0
    for (x, z), (top, k, fl, ring) in sorted(rl["hang"].items()):
        tow = None
        for (a, c, f) in ((1, 0, "east"), (-1, 0, "west"), (0, 1, "south"), (0, -1, "north")):
            q = (x + a, z + c); i, j = P.ix(gr, *q)
            if rl["rock"][i, j] and (q not in rl["hang"] or rl["hang"][q][1] > k): tow = f; break
        for y in range(top - k + 1, top + 1):
            d = top - y
            s_ = top_at(x, y, z, d) or rock_at(x, y, z, top)
            if y == top - k + 1 and k >= 2 and tow:
                base_ = rock_at(x, y, z, top).split(":")[1]; s_ = stairs(STAIR_OF.get(base_, "stone_stairs"), tow, "top")
            b.set(x, y, z, s_); n += 1
        if top_at(x, top, z, 0).endswith("moss_block") and hsh(x, 5, z, 2895) < 0.55 and b.get(x, top + 1, z) is None:
            b.set(x, top + 1, z, "minecraft:moss_carpet")
    return n

def moss_edges(b, gr, rl, walk_free):
    """moss carpet on the moss of the rock top near its edge (within 3), the table and the peak (not the bridgehead: lanterns, the walk)"""
    X, Z = gr["X"], gr["Z"]; rock = rl["rock"]; T = rl["T"]; n = 0
    cur = ~rock
    for _ in range(3):
        nxt = cur.copy()
        for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)): nxt |= np.roll(np.roll(cur, a, 0), c, 1)
        cur = nxt
    near = cur & rock & (rl["table"] | rl["peak"]) & ~gr["pad"]
    for i, j in zip(*np.nonzero(near)):
        x, z = int(X[i, j]), int(Z[i, j]); y = int(T[i, j])
        if (x, z) in rl["hang"] or not walk_free(x, z): continue
        if top_at(x, y, z, 0).endswith("moss_block") and hsh(x, 6, z, 2896) < 0.5 and b.get(x, y + 1, z) is None and b.get(x, y, z) is None:
            b.set(x, y + 1, z, "minecraft:moss_carpet"); n += 1
    return n

def fallen_arm(zc, side):
    """the faded lake: the raised arm broken off lies in the shallow water in front of the colossus (along -x), half out of it: the
    upper arm (3 wide), the forearm (2 x 2), the open palm lying flat with three fingers and the thumb"""
    m = {}; z0 = zc + side * 7
    def put(x, y, z): m[(x, y, z)] = COL.at(x, y, z)
    for x in range(412, 418):                                    # the upper arm, the broken end at x 417
        for dz in (-1, 0, 1):
            for y in (W - 1, W, W + 1):
                if y == W + 1 and abs(dz) == 1: continue
                put(x, y, z0 + dz)
    for x in range(406, 412):                                    # the forearm
        for dz in (0, side):
            for y in (W - 1, W): put(x, y, z0 + dz)
    for x in range(402, 406):                                    # the palm, flat, the back down
        for dz in (-1, 0, 1, 2):
            put(x, W, z0 + side * dz)
            if x >= 404: put(x, W - 1, z0 + side * dz)
    for (dz, ln) in ((-1, 3), (1, 4), (2, 2)):                   # the fingers (gap at 0), the thumb on the other side
        for k in range(ln): put(401 - k, W, z0 + side * dz)
    put(404, W, z0 - side * 2); put(403, W, z0 - side * 3)
    return m

# ---------------------------------------------------------------- the sword of the fallen Bearer on the islet
def sword(b):
    """the islet (rock up to W+2) and the great sword stuck in it, leaning north towards the causeway (HQ review T-028, 3): a blade 3 wide
    in the plane of its lean (z-y, its flat faces the causeway in the west), polished andesite on the edges (1 thick), andesite on the
    flat with the ridge (2 thick), the guard of
    polished tuff across it (7), the grip and the pommel over the guard; the sign on a plaque on a low post at the edge of the islet"""
    x1, z1, x2, z2 = P.SWORD_ISLET
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            top = W + 2 if (x1 < x < x2 and z1 < z < z2) else W + 1
            for y in range(W - 5, top + 1): b.set(x, y, z, Mix({"stone": 3, "mossy_cobblestone": 3, "andesite": 2, "moss_block": 1}, 2830).at(x, y, z))
    lean = math.radians(22)
    az, ay = -math.sin(lean), math.cos(lean)                     # along the blade (up and north: the lean is seen from the causeway)
    pz, py = math.cos(lean), math.sin(lean)                      # across it in the plane of the lean (z-y)
    oz, oy, xc, L = -44.4, W + 2.4, 416, 12.0                    # where the blade goes into the islet; xc the flat, xc-1 the ridge (west)
    cells = {}
    for z in range(-60, -38):
        for y in range(W + 1, W + 22):
            cz, cy = z + 0.5 - oz, y + 0.5 - oy; t = cz * az + cy * ay; s_ = cz * pz + cy * py
            if 0 <= t <= L and abs(s_) <= 1.3:
                edge = abs(s_) > 0.55
                cells[(xc, y, z)] = "minecraft:polished_andesite" if edge else ("minecraft:brown_terracotta" if hsh(xc, y, z, 2831) < 0.08 else "minecraft:andesite")
                if not edge: cells[(xc - 1, y, z)] = "minecraft:andesite"
            elif L < t <= L + 1.15 and abs(s_) <= 3.3:          # the guard
                for x in (xc - 1, xc, xc + 1): cells[(x, y, z)] = "minecraft:polished_tuff"
            elif L + 1.15 < t <= L + 4.0 and abs(s_) <= 0.55:   # the grip
                for x in (xc - 1, xc): cells[(x, y, z)] = "minecraft:tuff_bricks"
            elif L + 4.0 < t <= L + 5.3 and abs(s_) <= 0.95:    # the pommel
                for x in (xc - 1, xc): cells[(x, y, z)] = "minecraft:chiseled_tuff"
    zc = -45
    walk = set()
    for r in P.CAUSEWAY:
        for x in range(r[0], r[2] + 1):
            for z in range(r[1], r[3] + 1): walk.add((x, z))
    for (x, y, z), s_ in cells.items():
        if (x, z) in walk and y < W + 4: raise SystemExit("the sword blocks the causeway at %s" % ((x, y, z),))
        if y <= W + 2 and x1 <= x <= x2 and z1 <= z <= z2: continue        # inside the islet
        b.set(x, y, z, s_)
    # the sign: a plaque of polished tuff on a low post at the west edge of the islet, north of the blade (nothing in front of the blade
    # seen from the causeway), the wall sign on its north face at the eye level of the causeway (4 lines; a wall sign has no collision)
    sx, sz = x1, z1
    b.set(sx, W + 2, sz, "minecraft:cobblestone_wall[east=none,north=none,south=none,up=true,waterlogged=false,west=none]")
    b.set(sx, W + 3, sz, "minecraft:polished_tuff")
    sign = (sx, W + 3, sz - 1)                                   # on its north face: over the water, not over the causeway
    b.set(*sign, 'minecraft:dark_oak_wall_sign[facing=north,waterlogged=false]' + sign_nbt(["Дошёл до воды.", "Короли", "не узнали", "его руки."]))
    gcells = sorted((z, y) for (x, y, z), s_ in cells.items() if x == xc and "polished_tuff" in s_)
    gz, gy = gcells[len(gcells) // 2]; gx = xc
    top = max(y for (x, y, z) in cells)
    return dict(guard=[gx, gy, gz], sign=list(sign), tip=[xc, W + 2, int(oz)], top=top)

# ---------------------------------------------------------------- the pier and the causeway
def pier(b, gr, rl):
    x1, z1, x2, z2 = P.PIER
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            b.set(x, W + 1, z, PIER.at(x, W + 1, z)); fl = int(rl["T"][P.ix(gr, x, z)])
            if x in (x1, x2) or z in (z1, z2):                    # the deck on walls; water under it
                for y in range(fl + 1, W + 1): b.set(x, y, z, "minecraft:mossy_stone_bricks" if y < W - 1 else "minecraft:stone_bricks")
    posts = [(x1, z1), (x1, z2), (x1 + 5, z1), (x1 + 5, z2)]
    for (x, z) in posts:
        for y in range(int(rl["T"][P.ix(gr, x, z)]) + 1, W + 3): b.set(x, y, z, LOG)
        b.set(x, W + 3, z, lantern())
    for (x, z) in ((x1 + 2, z1), (x1 + 2, z2), (x1 + 8, z1), (x1 + 8, z2)):     # bollards
        b.set(x, W + 2, z, "minecraft:stone_brick_wall")
    return posts

def causeway(b, gr, rl):
    cells = set()
    for r in P.CAUSEWAY:
        for x in range(r[0], r[2] + 1):
            for z in range(r[1], r[3] + 1): cells.add((x, z))
    for (x, z) in cells:
        b.set(x, W + 1, z, CAUSE.at(x, W + 1, z))
        fl = int(rl["T"][P.ix(gr, x, z)])
        for y in range(fl + 1, W + 1): b.set(x, y, z, "minecraft:cobblestone" if hsh(x, y, z, 2832) < 0.6 else "minecraft:mossy_cobblestone")
    piles = []
    for (x, z) in sorted(cells):                                  # piles in the water along both edges, every 4th cell
        for (a, c) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + a, z + c)
            if q in cells or (x + z) % 4: continue
            i, j = P.ix(gr, *q)
            if rl["Wt"][i, j] == P.NONE or q in piles or (q[0], q[1]) in rl["sand"]: continue
            if any(P.rect(r, q[0], q[1]) for r in (P.PIER, P.KNOCK, P.SWORD_ISLET, P.COL_N, P.COL_S)): continue
            for y in range(int(rl["T"][i, j]) + 1, W + 3): b.set(q[0], y, q[1], LOG)
            piles.append(q)
    return sorted(cells), piles

def sand(b, gr, rl):
    """the way out of the knock zone: sand, and bottom sandstone slabs on the half steps (+0.5 a cell, no jumps)"""
    for (x, z), h2 in rl["sand"].items():
        if h2 % 2:
            y = (h2 - 1) // 2; b.set(x, y, z, st("sandstone_slab", type="bottom", waterlogged="true" if y <= W else "false")); top = y - 1
        else: top = h2 // 2 - 1
        b.set(x, top, z, "minecraft:sand")
        for yy in range(int(rl["T"][P.ix(gr, x, z)]) + 1, top): b.set(x, yy, z, "minecraft:sandstone")

# ---------------------------------------------------------------- the descent from bonfire 7
def descent(b, rl):
    for (x, z), (lv, k, f) in rl["walk"].items():
        if k == "S": b.set(x, lv, z, stairs("stone_brick_stairs", f))
        else: b.set(x, lv, z, PAVE.at(x, lv, z))
        for y in range(lv + 1, lv + 5):
            if b.get(x, y, z) is None: b.set(x, y, z, AIR)
    lamps = []
    for (x, z), (kind, top) in rl["rings"].items():
        if kind != "parapet": continue
        b.set(x, top + 1, z, "minecraft:cobblestone_wall")
        land = [rl["walk"][q] for q in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)) if q in rl["walk"]]
        if land and land[0][1] == "L" and (x + 2 * z) % 7 == 0:                 # lanterns on the parapet by the landings
            b.set(x, top + 2, z, lantern()); lamps.append((x, top + 2, z))
    return lamps

# ---------------------------------------------------------------- the stair in the rock
def stair_blocks(b):
    """the cleft stair (castle_plan.stair): F1/F2 in tunnels (air 4 high), F3/F4 open to the sky (air up to the top of the rock),
    the rest platform on corbels over the pier, the two ambush niches, the arch with roots at the top, lanterns every 10..12 cells"""
    cells, top = P.stair()
    A, Bl = P.LANE_A, P.LANE_B
    walk = {}
    for (x, za, zb, y, k, f) in cells:
        for z in range(za, zb + 1):
            walk[(x, z)] = walk.get((x, z), []) + [(y, k, f)]
    open_lane = {}
    for n, (x, za, zb, y, k, f) in enumerate(cells):
        for z in range(za, zb + 1):
            b.set(x, y, z, stairs("stone_brick_stairs", f) if k == "S" else DEEP.at(x, y, z))
            hi = y > 140 and x >= P.FACE_X        # F3, E2, F4, the top: open to the sky
            for yy in range(y + 1, (P.PRED_Y if hi else y + 4) + 1):
                if b.get(x, yy, z) is None or b.get(x, yy, z) == AIR: b.set(x, yy, z, AIR)
            if hi: open_lane[(x, z)] = y
    # the rest platform: parapet ring outside it (on a slab ring), corbels under the edges
    x1, z1, x2, z2 = P.REST
    ry = [c for c in cells if c[4] == "L" and c[0] == x1][0][3]
    for x in range(x1 - 1, x2 + 1):
        for z in (z1 - 1, z2 + 1):
            b.set(x, ry, z, PAVE.at(x, ry, z)); b.set(x, ry + 1, z, "minecraft:stone_brick_wall"); b.set(x, ry - 1, z, stairs("stone_brick_stairs", "north" if z < z1 else "south", "top"))
    for z in range(z1, z2 + 1):
        b.set(x1 - 1, ry, z, PAVE.at(x1 - 1, ry, z)); b.set(x1 - 1, ry + 1, z, "minecraft:stone_brick_wall"); b.set(x1 - 1, ry - 1, z, stairs("stone_brick_stairs", "west", "top"))
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            if (x + z) % 3 == 0: b.set(x, ry - 1, z, stairs("stone_brick_stairs", "west", "top"))
    lamps = [(x1 - 1, ry + 2, z1 - 1), (x1 - 1, ry + 2, z2 + 1)]
    # the niches (3 x 3 x 4, floor P.NICHE_Y + 1 .. +4 air) and the rock bridge over F3 holding the north one
    ny = P.NICHE_Y
    for (nx1, nz1, nx2, nz2) in P.NICHES:
        for x in range(nx1, nx2 + 2):
            for z in range(nz1, nz2 + 1):
                for y in range(ny, ny + 6):
                    inside = x <= nx2 and ny + 1 <= y <= ny + 4
                    b.set(x, y, z, AIR if inside else "minecraft:cobbled_deepslate" if hsh(x, y, z, 2840) < 0.5 else "minecraft:tuff")
    # arches with roots over the open lanes; the arch at the top of the stair on the cliff edge
    roots = []
    for (x, za, zb) in ((P.FACE_X + 6, A[0], A[1]), (P.FACE_X + 10, A[0], A[1]), (P.FACE_X + 8, Bl[0], Bl[1])):
        for z in range(za, zb + 1):
            b.set(x, P.PRED_Y, z, BRIDGE.at(x, P.PRED_Y, z))
            if x != P.FACE_X + 8: b.set(x, P.PRED_Y - 1, z, BRIDGE.at(x, P.PRED_Y - 1, z))
        low = P.PRED_Y - (1 if x == P.FACE_X + 8 else 2)
        b.set(x, low, (za + zb) // 2, lantern(True)); lamps.append((x, low, (za + zb) // 2))
        for z in (za, zb):
            b.set(x, low, z, "minecraft:hanging_roots[waterlogged=false]" if hsh(x, 1, z, 2841) < 0.6 else "minecraft:pale_hanging_moss[tip=true]"); roots.append((x, low, z))
    ax = P.FACE_X; az1, az2 = Bl[0] - 1, Bl[1] + 1
    for z in (az1, az2):
        for y in range(P.PRED_Y + 1, P.PRED_Y + 6): b.set(ax, y, z, CASTLE.at(ax, y, z))
    for z in range(az1, az2 + 1):
        b.set(ax, P.PRED_Y + 6, z, CASTLE.at(ax, P.PRED_Y + 6, z)); b.set(ax + 1, P.PRED_Y + 6, z, CASTLE.at(ax + 1, P.PRED_Y + 6, z))
        if az1 < z < az2:
            b.set(ax, P.PRED_Y + 1, z, "minecraft:stone_brick_wall")
            b.set(ax, P.PRED_Y + 5, z, "minecraft:hanging_roots[waterlogged=false]" if z != Bl[0] + 1 else "minecraft:pale_hanging_moss[tip=true]")
            b.set(ax + 1, P.PRED_Y + 5, z, "minecraft:pale_hanging_moss[tip=true]" if z == Bl[0] + 1 else "minecraft:hanging_roots[waterlogged=false]")
            roots += [(ax, P.PRED_Y + 5, z), (ax + 1, P.PRED_Y + 5, z)]
    b.set(ax + 1, P.PRED_Y + 4, Bl[0] + 1, lantern(True)); lamps.append((ax + 1, P.PRED_Y + 4, Bl[0] + 1))
    # tunnel and landing lanterns (hanging from the tunnel ceiling at level + 4)
    for (x, lane) in ((P.FACE_X + 4, A), (P.FACE_X + 9, A), (P.FACE_X + 8, Bl), (P.FACE_X + 3, Bl)):
        y = [w for w in walk[(x, lane[0] + 1)] if w[0] < 141][0][0]
        b.set(x, y + 4, lane[0] + 1, lantern(True)); b.set(x, y + 5, lane[0] + 1, "minecraft:cobbled_deepslate"); lamps.append((x, y + 4, lane[0] + 1))
    for y in sorted({c[3] for c in cells if c[4] == "L" and c[0] == P.FACE_X + 14}):
        b.set(P.FACE_X + 14, y + 1, (A[0] + Bl[1]) // 2, lantern()); lamps.append((P.FACE_X + 14, y + 1, (A[0] + Bl[1]) // 2))
    # parapets on the rock round the open slots (the top exit south of the top landing stays open)
    exit_ = {(x, Bl[1] + 1) for x in (P.FACE_X + 1, P.FACE_X + 2)}
    for (x, z), y in open_lane.items():
        for (a, c) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + a, z + c)
            if q in open_lane or q in exit_ or q[0] <= P.FACE_X: continue
            if b.get(q[0], P.PRED_Y + 1, q[1]) is None: b.set(q[0], P.PRED_Y + 1, q[1], "minecraft:stone_brick_wall")
    for q in exit_:
        for y in range(P.PRED_Y + 1, P.PRED_Y + 5): b.set(q[0], y, q[1], AIR)
    return dict(lamps=lamps, roots=roots, top=top, rest_y=ry, walk={"%d,%d" % k: v for k, v in walk.items()})

# ---------------------------------------------------------------- the bridge and the barbican
def bridge(b):
    xa, xb = P.BRIDGE_X; za, zb = P.RIFT[1], P.RIFT[3]; y = P.PRED_Y
    for x in range(xa, xb + 1):
        for z in range(za - 1, zb + 2):
            b.set(x, y, z, BRIDGE.at(x, y, z)); b.set(x, y - 1, z, BRIDGE.at(x, y - 1, z))
            for yy in range(y + 1, y + 5):
                if xa < x < xb: b.set(x, yy, z, AIR)
        for z in range(za, zb + 1):                               # two arches on a middle pier
            c = 9.5 if z <= 14 else 24.5
            soffit = y - 2 - int(round(((z - c) / 5.0) ** 2 * 7))
            pier_ = 15 <= z <= 19
            for yy in range((P.W - 10) if pier_ else soffit, y - 1): b.set(x, yy, z, BRIDGE.at(x, yy, z))
    lamps = []
    for z in range(za - 1, zb + 2):
        for x in (xa, xb):
            post = (z - za) % 6 == 0 or z in (zb, zb + 1)
            b.set(x, y + 1, z, BRIDGE.at(x, y + 1, z) if post else "minecraft:stone_brick_wall")
            if post and z not in (zb + 1,): b.set(x, y + 2, z, lantern()); lamps.append((x, y + 2, z))
    return dict(mid=[(xa + xb) / 2 + 0.5, y + 1, (za + zb) / 2 + 0.5], lamps=lamps, deck=y)

def barbican(b, P_):
    x1, z1, x2, z2 = P.BARBICAN; y0 = P.PRED_Y; gx1, gx2 = P.BRIDGE_X[0] + 1, P.BRIDGE_X[1] - 1
    top = P_ + 10
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            tw = x <= x1 + 3 or x >= x2 - 3
            hgt = top + (4 if tw else 0)
            for y in range(y0, hgt + 1): b.set(x, y, z, CASTLE.at(x, y, z))
            edge = x in (x1, x2) or z in (z1, z2) or (tw and (x in (x1 + 3, x2 - 3)))
            if edge and (x + z) % 2 == 0: b.set(x, hgt + 1, z, CASTLE.at(x, hgt + 1, z))
    for z in range(z1, z2 + 1):                                  # the gate passage, the portcullis, the steps up to the table
        for x in range(gx1, gx2 + 1):
            fl = y0 if z <= z1 + 4 else min(P_, y0 + (z - z1 - 4))
            b.set(x, fl, z, DEEP.at(x, fl, z) if fl == y0 or z == z2 else stairs("stone_brick_stairs", "south"))
            for y in range(fl + 1, max(y0 + 5, fl + 4) + 1): b.set(x, y, z, AIR)
    for x in range(gx1, gx2 + 1):
        for y in range(y0 + 1, y0 + 6): b.set(x, y, z1 + 1, "minecraft:iron_bars")
        b.set(x, y0 + 5, z1, stairs("stone_brick_stairs", "west" if x == gx1 else "east" if x == gx2 else "south", "top") if x != (gx1 + gx2) // 2 else "minecraft:chiseled_stone_bricks")
    for (x, y) in ((x1 + 1, top - 2), (x2 - 1, top - 2), (x1 + 1, top - 3), (x2 - 1, top - 3)):      # arrow slits
        b.set(x, y, z1, "minecraft:iron_bars")
    return dict(gate=[(gx1 + gx2) / 2 + 0.5, y0 + 1, z1 + 0.5], portcullis=[gx1, y0 + 1, z1 + 1, gx2, y0 + 5, z1 + 1], top=top + 4)

def dark_oak(b, x, z, y, salt, ground=None):
    """2 x 2 trunk (down to the ground of each of its cells on a slope), a flat crown"""
    hgt = 6 + int(hsh(x, 0, z, salt) * 4)
    for (a, d) in ((0, 0), (1, 0), (0, 1), (1, 1)):
        g = ground(x + a, z + d) if ground else y
        for yy in range(min(g, y) + 1, y + hgt + 1): b.set(x + a, yy, z + d, "minecraft:dark_oak_log[axis=y]")
    cy = y + hgt
    for a in range(-3, 5):
        for d in range(-3, 5):
            for e in (0, 1, 2):
                r = abs(a - 0.5) + abs(d - 0.5) + e * 1.6
                if r <= 5.2 - hsh(x + a, cy + e, z + d, salt) * 1.6 and b.get(x + a, cy + e, z + d) in (None, AIR):
                    b.set(x + a, cy + e, z + d, "minecraft:dark_oak_leaves[distance=1,persistent=true,waterlogged=false]")
