"""T-028: the block models of the approaches to the Enchanted Castle (the colossi, the sword of the fallen Bearer, the pier, the causeway,
the descent from bonfire 7, the stair in the rock with the rest platform and the niches, the bridge, the barbican, the lanterns, the trees)
for tools/build/r1_castle.py. Palettes from the card «Заколдованный замок и Колоссы · Р1»."""
import math
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
COL_LO = Mix({"stone": 24, "andesite": 20, "tuff": 16, "mossy_cobblestone": 24, "moss_block": 16}, 2810)     # the card: 30/25/20/15/10,
COL = Mix({"stone": 32, "andesite": 27, "tuff": 21, "mossy_cobblestone": 13, "moss_block": 7}, 2811)         # more moss low, less high
COL_HI = Mix({"stone": 36, "andesite": 30, "tuff": 24, "mossy_cobblestone": 10}, 2812)
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
    (cells, meta) with the eye cells, the palm, the raised arm cells (the fade breaks it off) and the strike point."""
    m = {}; arm = set(); eyes = []
    def put(u, v, r, s):
        m[(431 - u, W + r, zc + v)] = s
    def pal(u, v, r): return (COL_LO if r < 16 else COL if r < 34 else COL_HI).at(431 - u, W + r, zc + v)
    for r in range(-6, 6):                                       # the plinth from the lake floor to W+5, sheer sides
        for u in range(0, 12):
            for v in range(-5, 6): put(u, v, r, PLINTH.at(431 - u, W + r, zc + v))
    for r in (6, 7):                                             # the toes under the hem
        for u in (8, 9, 10):
            for v in (-3, -2, -1, 1, 2, 3): put(u, v, r, pal(u, v, r))
    def fold(k): return k % 2 == 0
    for r in range(6, 30):                                       # the robe: vertical folds on the front and the sides
        front = 8 if r < 10 else 7; hw = 4
        for u in range(1, front + 2):
            for v in range(-hw - 1, hw + 2):
                f = front + (1 if fold(v) else 0); s_ = hw + (1 if fold(u) and r < 26 else 0)
                if u <= f and abs(v) <= s_: put(u, v, r, pal(u, v, r))
    for r in (30, 31):                                           # the belt
        for u in range(2, 9):
            for v in range(-4, 5): put(u, v, r, "minecraft:polished_andesite")
    for r in range(32, 39):                                      # the chest
        for u in range(2, 8 + (1 if r >= 35 else 0)):
            for v in range(-4, 5): put(u, v, r, pal(u, v, r))
    for r in (39, 40):                                           # the shoulders
        for u in range(2, 8):
            for v in range(-5, 6): put(u, v, r, pal(u, v, r))
    for r in range(22, 39):                                      # the lowered arm (sleeve) on the outer side, the hand at r 22..23
        for u in range(3, 7):
            put(u, -side * 5, r, pal(u, -side * 5, r))
    # the raised arm on the inner side (over the channel): the upper arm out from the shoulder, the forearm up, the palm 3 x 6 facing
    # the lake (u 10) beside the head, fingers apart at the top
    for (u, vv, r) in [(u, 6, r) for u in (5, 6, 7) for r in (39, 40, 41)] + [(u, 7, r) for u in (7, 8) for r in (41, 42, 43)] + \
                      [(u, vv, r) for u in (8, 9) for vv in (7, 8) for r in (43, 44, 45, 46)]:
        v = side * vv; put(u, v, r, pal(u, v, r)); arm.add((u, v, r))
    palm = []
    for r in range(45, 51):
        for vv in (6, 7, 8):
            if r >= 49 and vv == 7: continue                    # a gap between the fingers
            v = side * vv; put(10, v, r, pal(10, v, r)); arm.add((10, v, r)); palm.append((10, v, r))
            if r <= 48: put(9, v, r, pal(9, v, r)); arm.add((9, v, r))
    for r in (46, 47): put(10, side * 5, r, pal(10, side * 5, r)); arm.add((10, side * 5, r))      # the thumb
    for r in (40, 41):                                           # the neck
        for u in (4, 5, 6):
            for v in (-1, 0, 1): put(u, v, r, pal(u, v, r))
    for r in range(41, 48):                                      # the head (7 wide, 6 deep), the hair falling behind
        for u in range(3, 9):
            for v in range(-3, 4): put(u, v, r, pal(u, v, r))
    for r in range(36, 41):
        for v in range(-3, 4): put(2, v, r, pal(2, v, r))
    for r in range(36, 44):                                      # the beard in front of the chest and the chin
        w_ = 2 if r >= 39 else 1
        for v in range(-w_, w_ + 1): put(9, v, r, pal(9, v, r))
    for v in range(-3, 4): put(9, v, 46, pal(9, v, 46))          # the brow over the eyes
    put(9, 0, 44, pal(9, 0, 44)); put(9, 0, 45, pal(9, 0, 45))   # the nose
    for v in (-2, -1, 1, 2):                                     # the eye sockets: 2 x 2 niches, the eye block one deep (u 7)
        for r in (44, 45):
            put(8, v, r, AIR); put(7, v, r, EYE_SLEEP); eyes.append((431 - 7, W + r, zc + v))
    for u in range(3, 9):                                        # the crown: a band of gold at r 48, tines at r 49..50
        for v in range(-3, 4):
            if u in (3, 8) or abs(v) == 3:
                put(u, v, 48, CROWN.at(431 - u, W + 48, zc + v))
                if (u + v) % 2 == 0: put(u, v, 49, CROWN.at(431 - u, W + 49, zc + v)); put(u, v, 50, "minecraft:gold_block" if (u * 3 + v) % 4 else "minecraft:raw_gold_block")
            else: put(u, v, 48, pal(u, v, 48))
    armw = {(431 - u, W + r, zc + v) for (u, v, r) in arm}
    strike = [420.5, W + 47.5, zc + side * 7 + 0.5]
    return m, dict(eyes=eyes, arm=sorted(armw), strike=strike, zc=zc, side=side, box=[420, W - 6, zc - 8, 431, W + 50, zc + 8])

def fallen_arm(zc, side):
    """the faded lake: the raised arm broken off lies in the shallow water in front of the colossus (along -x), half out of it"""
    m = {}; z0 = zc + side * 7
    for k in range(13):
        x = 417 - k
        for dz in (-1, 0, 1):
            for y in (W - 1, W, W + 1):
                if y == W + 1 and abs(dz) == 1: continue
                m[(x, y, z0 + dz)] = COL.at(x, y, z0 + dz)
    for dz in (-2, -1, 0, 1, 2):                                  # the palm lying flat, fingers
        for x in (402, 403, 404):
            m[(x, W, z0 + dz)] = COL.at(x, W, z0 + dz)
            if dz in (-2, 0, 2) and x == 402: m[(401, W, z0 + dz)] = COL.at(401, W, z0 + dz)
    return m

# ---------------------------------------------------------------- the sword of the fallen Bearer on the islet
def sword(b):
    """the islet (rock up to W+2) and the great sword stuck in it, leaning west over the causeway; the hanging sign under the guard"""
    x1, z1, x2, z2 = P.SWORD_ISLET
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            top = W + 2 if (x1 < x < x2 and z1 < z < z2) else W + 1
            for y in range(W - 5, top + 1): b.set(x, y, z, Mix({"stone": 3, "mossy_cobblestone": 3, "andesite": 2, "moss_block": 1}, 2830).at(x, y, z))
    dx, dy = -math.sin(math.radians(58)), math.cos(math.radians(58))
    ox, oy, zc = 419.5, W + 1.5, -45
    cells = []
    for k in range(12):                                          # the blade: 12 along the line, 2 wide (z), rust streaks
        t = k + 0.5; x = math.floor(ox + dx * t); y = math.floor(oy + dy * t)
        for z in (zc, zc + 1):
            s = "minecraft:polished_andesite" if z == zc else "minecraft:andesite"
            if hsh(x, y, z, 2831) < 0.18: s = "minecraft:brown_terracotta"
            cells.append((x, y, z, s))
    t = 12.5; gx = math.floor(ox + dx * t); gy = math.floor(oy + dy * t)
    for z in range(zc - 2, zc + 4): cells.append((gx, gy, z, "minecraft:polished_tuff"))      # the guard across
    for k in (13.5, 14.5, 15.5):                                 # the grip and the pommel
        x = math.floor(ox + dx * k); y = math.floor(oy + dy * k)
        for z in (zc, zc + 1): cells.append((x, y, z, "minecraft:tuff_bricks" if k < 15 else "minecraft:chiseled_tuff"))
    walk = set()
    for r in P.CAUSEWAY:
        for x in range(r[0], r[2] + 1):
            for z in range(r[1], r[3] + 1): walk.add((x, z))
    for (x, y, z, s) in cells:
        if (x, z) in walk and y < W + 4: raise SystemExit("the sword blocks the causeway at %s" % ((x, y, z),))
        b.set(x, y, z, s)
    sign = (gx, gy - 1, zc + 3)
    b.set(*sign, 'minecraft:dark_oak_hanging_sign[rotation=4,attached=false,waterlogged=false]' + sign_nbt(["Дошёл до воды.", "Короли не узнали", "его руки."]))
    return dict(guard=[gx, gy, zc], sign=list(sign), tip=[419, W + 1, zc])

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
