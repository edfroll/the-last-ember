#!/usr/bin/env python3
"""T-034: the Ogre's Den (Нора Людоеда, Р1, card 5.1) on the place `ogre_den` (rect 250 180 40 30) + the chain of bones from the trail
refuge -> bonfire 2 (T-022).

  python3 tools/build/r1_ogre.py   -> server/build/r1/ogre.txt (tools/blockwriter.sh apply), ogre.json (points for the datapack, the
                                      tests, the bot), ogre_deco.json (the columns of the chain of bones outside the place: decoration on
                                      the ground, excused by `r1_check.py places`), datapack function/treasury/gen/ogre_* (treasury_dp.py),
                                      the zone lines, the vault line
Inputs: server/build/r1/ogre_pre.bin (the box now; the first run keeps the ground in ogre_before.npz), base.bin, terrain.bin, r1.json.

HQ T-034, 2: the cave (a search, tools/build/treasury_ogre.py) with its box + 6 filled with rock (vanilla caves, water, lava), the stair up
to the mouth by the old oak with the fallen trunk across it, the lair (uneven floor of half slabs, bone heaps, cages with remains on
chains, the bed of hides with the chest under it, the cold campfire), dark. Re-run on the built place: 0 columns changed."""
import json, math, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import treasury_ogre as P
from lib import B, Mix, h as hsh
from treasury_ogre import right, FACE

ROOT = P.ROOT; OUT = P.OUT
ROCK_OK = re.compile(r"minecraft:(stone|andesite|diorite|granite|tuff|deepslate|dirt|coarse_dirt|calcite|grass_block|cobblestone|mossy_cobblestone|cobbled_deepslate)$")
WALL = Mix({"stone": 34, "cobbled_deepslate": 18, "tuff": 10, "coarse_dirt": 12, "rooted_dirt": 10, "andesite": 10, "cobblestone": 6}, salt=31)
FLOOR = Mix({"coarse_dirt": 34, "rooted_dirt": 18, "cobbled_deepslate": 24, "packed_mud": 8, "stone": 16}, salt=32)
FLOOR_SLAB = Mix({"cobbled_deepslate_slab[type=bottom]": 60, "mud_brick_slab[type=bottom]": 15, "tuff_slab[type=bottom]": 25}, salt=33)
RAISE = Mix({"coarse_dirt": 40, "rooted_dirt": 30, "cobbled_deepslate": 30}, salt=34)
STEP = Mix({"cobblestone_stairs": 55, "mossy_cobblestone_stairs": 30, "stone_stairs": 15}, salt=35)
LAND = Mix({"cobblestone": 50, "mossy_cobblestone": 35, "stone": 15}, salt=36)
TUNNEL = Mix({"stone": 30, "cobblestone": 20, "mossy_cobblestone": 15, "cobbled_deepslate": 15, "rooted_dirt": 20}, salt=37)
NEAR_TOP = Mix({"rooted_dirt": 60, "coarse_dirt": 25, "mossy_cobblestone": 15}, salt=38)


def under_blocks(gr, box, ylo, name="ogre_under"):
    """the blocks of the fill box that are not plain rock (air pockets, cave air, water, lava, gravel, ores...), read from the world before
    the step (the first run), kept in ogre_under.npz by the key of the plan: {(x, y, z): name}"""
    cp = os.path.join(OUT, name + ".npz"); key = gr.key + repr(box) + str(ylo)
    if os.path.exists(cp):
        d = np.load(cp, allow_pickle=True)
        if str(d["key"]) == key: return {tuple(int(t) for t in k): str(n) for k, n in zip(d["pos"], d["name"])}
    import fens_scan
    old = fens_scan.BAN; fens_scan.BAN = re.compile(r"(?!%s).*" % ROCK_OK.pattern)
    try: found = fens_scan.scan(os.path.join(ROOT, "server/world"), box=box)
    finally: fens_scan.BAN = old
    found = [(x, y, z, n) for (x, y, z, n) in found if ylo <= y <= gr.g(x, z)]
    np.savez_compressed(cp, pos=np.array([[x, y, z] for (x, y, z, n) in found] or np.zeros((0, 3)), np.int32),
                        name=np.array([n for (x, y, z, n) in found], object), key=key)
    return {(x, y, z): n for (x, y, z, n) in found}


class Den:
    def __init__(self, gr, pl):
        self.gr, self.pl = gr, pl
        self.cave = pl["cave"]; self.F = pl["cave"]["F"]; self.r = tuple(pl["cave"]["r"])
        st = pl["stair"]
        self.cells = [(c[0], c[1], c[2], c[3], tuple(c[4])) for c in st["cells"]]
        self.exit = [tuple(c) for c in st["exit"]]; self.top = st["top"]
        self.air = set(); self.h = {}; self.ceil = {}
        self.meta = {}


def cave_shape(b, dn):
    """the air of the cave: the rect with walls nibbled by up to 1 (noise), a vault (8 in the middle, 6 at the walls), the floor uneven by
    half blocks (0, a slab, a block: neighbours differ by half a block at most); flat at the foot of the stair, under the bed and round
    the decor spots (dn.flat)"""
    x1, z1, x2, z2 = dn.r; F = dn.F
    foot = {(c[0] - 1, c[1]) for c in dn.cells[:2]} | {(c[0] - 2, c[1]) for c in dn.cells[:2]}
    cols = {}
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            e = min(x - x1, x2 - x, z - z1, z2 - z)
            if e == 0 and hsh(x, 0, z, 41) < 0.35 and (x, z) not in foot: continue     # the wall nibbled
            if e == 0 and min(x - x1, x2 - x) == 0 and min(z - z1, z2 - z) == 0: continue  # round corners
            c = F + P.AIR - max(0, 2 - e) - (1 if e == 2 and hsh(x, 1, z, 42) < 0.5 else 0)
            cols[(x, z)] = c
    # the floor: half steps 0..2 from smooth noise, smoothed to neighbours +-1
    hgt = {}
    for (x, z) in cols:
        n = math.sin(x * 0.37 + 1.3) * math.cos(z * 0.29 - 0.7) + 0.6 * math.sin((x + z) * 0.21) + 0.5 * (hsh(x, 2, z, 43) - 0.5)
        hgt[(x, z)] = 0 if n < -0.15 else (1 if n < 0.55 else 2)
    for (x, z) in dn.flat | foot:
        if (x, z) in hgt: hgt[(x, z)] = 0
    for _ in range(4):
        for (x, z) in sorted(hgt):
            m = min([hgt.get((x + a, z + c), 9) for (a, c) in P.DIRS] + [9])
            if hgt[(x, z)] > m + 1: hgt[(x, z)] = m + 1
    dn.h = hgt; dn.ceil = cols
    for (x, z), c in cols.items():
        hh = hgt[(x, z)]
        b.set(x, F, z, FLOOR)
        if hh == 1: b.set(x, F + 1, z, FLOOR_SLAB)
        elif hh == 2: b.set(x, F + 1, z, RAISE)
        for y in range(F + 1 + (1 if hh == 2 else 0) + (0 if hh < 2 else 0), c + 1):
            if not (hh == 1 and y == F + 1): b.set(x, y, z, "minecraft:air"); dn.air.add((x, y, z))
    # the shell: every rock cell next to the air
    for (x, y, z) in list(dn.air):
        for (a, e, c) in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            q = (x + a, y + e, z + c)
            if q not in dn.air and b.get(*q) is None: b.set(*q, WALL)


def feet(dn, x, z):
    """the feet level on the floor of the cave at (x, z): F + 1, + 0.5 on a slab, + 1 on a raised block"""
    return dn.F + 1 + dn.h.get((x, z), 0) * 0.5


def stair(b, dn):
    """the stairs and landings, HEAD of air over each, the walls and the roof of the tunnel (rock where the ground before is high enough,
    else open: a trench with rooted dirt edges), the mouth (the exit cells set to the top - 1, air over them)"""
    gr = dn.gr
    occ = {(c[0], c[1]) for c in dn.cells}
    for (x, z, y, kind, d) in dn.cells:
        if kind == "stair": b.set(x, y, z, "minecraft:%s[facing=%s,half=bottom,shape=straight,waterlogged=false]" % (STEP.at(x, y, z).replace("minecraft:", ""), FACE[d]))
        else: b.set(x, y, z, LAND)
        b.set(x, y - 1, z, TUNNEL if b.get(x, y - 1, z) is None else b.get(x, y - 1, z))
        g = gr.g(x, z)
        for yy in range(y + 1, y + P.HEAD + 1): b.set(x, yy, z, "minecraft:air")
        for yy in range(y + P.HEAD + 1, g + 1): b.set(x, yy, z, "minecraft:air") if g < y + P.HEAD + 1 else None
        if g >= y + P.HEAD + 1: b.set(x, y + P.HEAD + 1, z, NEAR_TOP if g - (y + P.HEAD + 1) <= 2 else TUNNEL)
        for (a, c) in P.DIRS:
            nx, nz = x + a, z + c
            if (nx, nz) in occ or (nx, nz) in dn.ceil: continue
            gn = gr.g(nx, nz)
            for yy in range(y, min(y + P.HEAD + 1, gn) + 1):
                if b.get(nx, yy, nz) is None: b.set(nx, yy, nz, NEAR_TOP if gn - yy <= 2 else TUNNEL)
    # the mouth: the two exit cells at top - 1 (cut or fill), air over the exit rows
    for k, (x, z) in enumerate(dn.exit):
        g = gr.g(x, z)
        if k < 2:
            for yy in range(min(g, dn.top - 1), dn.top - 1): b.set(x, yy, z, "minecraft:coarse_dirt")
            b.set(x, dn.top - 1, z, "minecraft:rooted_dirt")
            for yy in range(dn.top, max(g, dn.top + 2) + 1): b.set(x, yy, z, "minecraft:air")


def oak(b, dn):
    """the old oak: a 2 x 2 trunk 16 high, its root flare (oak wood, rooted dirt, mangrove roots in patches on the ground round it, not on
    the way), four limbs, leaf crowns; persistent leaves. Returns the perches for the ravens (a limb end) and the trunk's top"""
    gr = dn.gr; o = dn.pl["oak"]; cells = [tuple(c) for c in o["cells"]]; y0 = o["y"]
    H = 16
    xs = [c[0] for c in cells]; zs = [c[1] for c in cells]; cx, cz = (min(xs) + max(xs) + 1) / 2, (min(zs) + max(zs) + 1) / 2
    way = {(c[0], c[1]) for c in dn.cells} | set(dn.exit)
    for (x, z) in cells:
        for yy in range(gr.g(x, z) + 1, y0): b.set(x, yy, z, "minecraft:oak_wood[axis=y]")
        for yy in range(y0, y0 + H): b.set(x, yy, z, "minecraft:oak_log[axis=y]")
    # the flare and the roots
    for (x, z) in [(x + a, z + c) for (x, z) in cells for (a, c) in P.DIRS]:
        if (x, z) in cells or (x, z) in way: continue
        g = gr.g(x, z)
        b.set(x, g + 1, z, "minecraft:oak_wood[axis=y]" if hsh(x, 3, z, 44) < 0.6 else "minecraft:mangrove_roots[waterlogged=false]")
    for dx in range(-4, 6):
        for dz in range(-4, 6):
            x, z = int(min(xs) + dx), int(min(zs) + dz)
            if (x, z) in cells or (x, z) in way or abs(x - cx) + abs(z - cz) > 5.5: continue
            g = gr.g(x, z)
            if b.get(x, g, z) is None: b.set(x, g, z, "minecraft:rooted_dirt")
            if b.get(x, g + 1, z) is None and hsh(x, 4, z, 45) < 0.22 and not any((x + a, z + c) in way for (a, c) in P.DIRS):
                b.set(x, g + 1, z, "minecraft:mangrove_roots[waterlogged=false]")
    # the limbs and the crowns
    perches = []; top = y0 + H
    limbs = [((1, 1), 9, 5), ((-1, 1), 11, 4), ((-1, -1), 10, 5), ((1, -1), 12, 4)]
    leaves = set()
    for (d, at, ln) in limbs:
        x, y, z = cx + d[0] * 0.5, y0 + at, cz + d[1] * 0.5
        for k in range(ln):
            x += d[0] * 0.9; z += d[1] * 0.9; y += 0.5
            bx, by, bz = int(math.floor(x)), int(round(y)), int(math.floor(z))
            if (bx, bz) not in way: b.set(bx, by, bz, "minecraft:oak_log[axis=%s]" % ("x" if k % 2 else "z"))
        perches.append([math.floor(x) + 0.5, int(round(y)) + 1, math.floor(z) + 0.5])
        for a in range(-3, 4):
            for e in range(-1, 3):
                for c in range(-3, 4):
                    if a * a + (e * 1.6) ** 2 + c * c <= 10.5 + 2 * hsh(int(x) + a, int(y) + e, int(z) + c, 46): leaves.add((int(math.floor(x)) + a, int(round(y)) + e, int(math.floor(z)) + c))
    for a in range(-4, 5):
        for e in range(-2, 4):
            for c in range(-4, 5):
                if a * a + (e * 1.4) ** 2 + c * c <= 17 + 3 * hsh(a, e, c, 47): leaves.add((int(cx) + a, top + e, int(cz) + c))
    low = y0 + 6
    for (x, y, z) in leaves:
        if y < low or b.get(x, y, z) is not None or y <= dn.gr.g(x, z): continue
        b.set(x, y, z, "minecraft:oak_leaves[distance=7,persistent=true,waterlogged=false]")
    return perches, top


def fallen(b, dn):
    """the fallen trunk across the mouth: an oak log 9 long lying along the perpendicular of the last flight over the first exit row, 2
    over the exit's feet (the way passes under it), its ends on the ground or propped by a stump of oak wood; hanging roots under it over
    the way (no collision: they hide the opening from afar); two short branches with leaves. Returns the trunk's cells (ravens)"""
    gr = dn.gr; d = dn.cells[-1][4]; p = right(d)
    oakc = {tuple(c) for c in dn.pl["oak"]["cells"]}
    way = set(dn.exit) | {(c[0], c[1]) for c in dn.cells}
    axis = "x" if p[0] else "z"
    best = None
    for row in (0, 1, 2):                                   # the first exit row the trunk crosses clear of the oak, >= 6 logs in the air
        ex0, ex1 = dn.exit[2 * row], dn.exit[2 * row + 1]
        y = max(dn.top, max(gr.g(*ex0), gr.g(*ex1)) + 1) + 2
        mid = ((ex0[0] + ex1[0]) / 2, (ex0[1] + ex1[1]) / 2)
        cells = []
        for k in range(-4, 5):
            x = int(math.floor(mid[0] + k * p[0] + (0.5 if p[0] else 0))); z = int(math.floor(mid[1] + k * p[1] + (0.5 if p[1] else 0)))
            cells.append((k, x, z))
        if any((x, z) in oakc for (k, x, z) in cells): continue
        n = sum(1 for (k, x, z) in cells if gr.g(x, z) < y)
        if n >= 6: best = (y, cells); break
    if best is None: raise SystemExit("no row of the mouth takes the fallen trunk (>= 6 logs over the ground, clear of the oak)")
    y, cells = best
    out = []
    for (k, x, z) in cells:
        g = gr.g(x, z)
        if g >= y: continue                                   # buried in the slope there: the trunk ends in the ground
        b.set(x, y, z, "minecraft:oak_log[axis=%s]" % axis); out.append((x, y, z))
        if (x, z) in way:
            if b.get(x, y - 1, z) in (None, "minecraft:air"): b.set(x, y - 1, z, "minecraft:hanging_roots[waterlogged=false]")
        elif g < y - 1 and abs(k) >= 3:
            for yy in range(g + 1, y): b.set(x, yy, z, "minecraft:oak_wood[axis=y]")
    if len(out) < 6: raise SystemExit("the fallen trunk has %d logs over the ground (< 6)" % len(out))
    for (x, yy, z) in (out[1], out[-2]):
        bx, bz = x + d[0], z + d[1]
        if (bx, bz) not in way and b.get(bx, yy + 1, bz) is None:
            b.set(bx, yy + 1, bz, "minecraft:oak_log[axis=%s]" % ("z" if d[1] else "x"))
            for (a, c) in ((0, 0), (d[0], d[1]), (p[0], p[1])):
                if b.get(bx + a, yy + 2, bz + c) is None: b.set(bx + a, yy + 2, bz + c, "minecraft:oak_leaves[distance=7,persistent=true,waterlogged=false]")
    return out


def lair(b, dn):
    """the decor of the lair, after the shape: the bed of hides (brown wool, carpet on top) with the chest under its head end and its lock
    (brown wool over it), the cold campfire, 3 heaps of bone blocks, 4 cages hanging on chains (iron bars round a skull), the spots of the
    seat, the cauldron, the loose bones. Points to dn.meta"""
    x1, z1, x2, z2 = dn.r; F = dn.F
    m = dn.meta
    # the bed: the far end from the stair (the stair comes from the east wall near the south-east corner): west wall, north half
    bx1, bz1 = x1 + 2, z1 + 3; bx2, bz2 = bx1 + 3, bz1 + 4       # 4 x 5
    for x in range(bx1, bx2 + 1):
        for z in range(bz1, bz2 + 1):
            b.set(x, F + 1, z, "minecraft:brown_wool")
            b.set(x, F + 2, z, "minecraft:brown_carpet" if hsh(x, 5, z, 48) < 0.8 else "minecraft:air")
    # the chest at the head of the bed (its west end), facing east into the cave? no: facing out of the bed's front (east), the bed round it
    cx, cz = bx1, bz1 + 2
    b.set(cx, F + 1, cz, 'minecraft:chest[facing=east,type=single,waterlogged=false]{LootTable:"last_ember:vault/r1_ogre"}')
    b.set(cx, F + 2, cz, "minecraft:brown_wool")
    b.set(cx + 1, F + 1, cz, "minecraft:air"); b.set(cx + 1, F + 2, cz, "minecraft:air")   # the front of the chest: a gap in the hides
    b.set(cx + 1, F + 1, cz, "minecraft:brown_carpet")
    m["chest"] = [cx, F + 1, cz]; m["lock"] = [cx, F + 2, cz]; m["lock_block"] = "minecraft:brown_wool"
    m["seat"] = [bx1 + 2.5, F + 2.0, bz1 + 3.5]
    m["bed"] = [bx1, bz1, bx2, bz2]
    # the campfire, cold, by the bed's foot
    b.set(bx2 + 2, F + 1, bz2 - 1, "minecraft:campfire[facing=west,lit=false,signal_fire=false,waterlogged=false]")
    m["campfire"] = [bx2 + 2, F + 1, bz2 - 1]
    # bone heaps
    heaps = [(x1 + 9, z2 - 4, 2.2), (x1 + 17, z1 + 3, 1.8), (x2 - 6, z1 + 4, 1.6)]
    for (hx, hz, r) in heaps:
        for a in range(-3, 4):
            for c in range(-3, 4):
                d = math.hypot(a, c)
                x, z = hx + a, hz + c
                if (x, z) not in dn.ceil or d > r + 0.4 * hsh(x, 6, z, 49): continue
                b.set(x, F + 1, z, "minecraft:bone_block[axis=%s]" % "xyz"[int(hsh(x, 7, z, 50) * 3)])
                if d < r - 1.0: b.set(x, F + 2, z, "minecraft:bone_block[axis=y]")
                elif d < r - 0.3 and hsh(x, 8, z, 51) < 0.3: b.set(x, F + 2, z, "minecraft:skeleton_skull[rotation=%d]" % int(hsh(x, 9, z, 52) * 16))
    m["heaps"] = [[h[0] + 0.5, F + 3, h[1] + 0.5] for h in heaps]
    # cages: 3 x 3, the bottom slab at F + 3, bars F + 4 .. F + 5, the top slab F + 6, a skull inside, the chain to the roof
    cages = [(x1 + 6, z1 + 3), (x1 + 13, z2 - 3), (x2 - 9, z2 - 3), (x2 - 4, z1 + 9)]
    for (gx, gz) in cages:
        y0 = F + 3
        for a in (-1, 0, 1):
            for c in (-1, 0, 1):
                b.set(gx + a, y0, gz + c, "minecraft:cobbled_deepslate_slab[type=top,waterlogged=false]")
                b.set(gx + a, y0 + 3, gz + c, "minecraft:cobbled_deepslate_slab[type=bottom,waterlogged=false]")
                for e in (1, 2):
                    b.set(gx + a, y0 + e, gz + c, "minecraft:air" if (a, c) == (0, 0) else "minecraft:iron_bars")
        b.set(gx, y0 + 1, gz, "minecraft:skeleton_skull[rotation=%d]" % int(hsh(gx, 10, gz, 53) * 16))
        b.set(gx, y0 + 2, gz, "minecraft:air")
        for yy in range(y0 + 4, dn.ceil[(gx, gz)] + 1): b.set(gx, yy, gz, "minecraft:iron_chain[axis=y,waterlogged=false]")
        for (a, c) in ((-1, -1), (1, 1)):
            for yy in range(y0 + 4, dn.ceil.get((gx + a, gz + c), y0 + 3) + 1): b.set(gx + a, yy, gz + c, "minecraft:iron_chain[axis=y,waterlogged=false]")
    m["cages"] = [[g[0], F + 3, g[1]] for g in cages]
    m["cauldron"] = [x1 + 11 + 0.5, F + 1.0, z1 + 9 + 0.5]
    m["bones"] = [[x1 + 8.3, F + 1.05, z1 + 11.6, 30], [x1 + 21.6, F + 1.05, z2 - 7.4, 110], [bx2 + 2.6, F + 1.05, bz1 + 0.4, 200]]


def flat_spots(dn):
    x1, z1, x2, z2 = dn.r
    bx1, bz1 = x1 + 2, z1 + 3
    s = set()
    for x in range(bx1 - 1, bx1 + 7):
        for z in range(bz1 - 1, bz1 + 7): s.add((x, z))
    for (hx, hz) in [(x1 + 9, z2 - 4), (x1 + 17, z1 + 3), (x2 - 6, z1 + 4), (x1 + 11, z1 + 9), (x1 + 8, z1 + 11), (x1 + 21, z2 - 8)]:
        for a in range(-3, 4):
            for c in range(-3, 4): s.add((hx + a, hz + c))
    return s


def fill(b, dn, under):
    """HQ T-034, 2: in the box of the cave + 6 (and round the stair, 3) only our blocks and solid rock: vanilla caves, water, lava, gravel
    there (up to the ground before) become stone"""
    n = 0
    x1, z1, x2, z2 = dn.r; F = dn.F
    near = set()
    for (x, z, y, *_) in dn.cells:
        for a in range(-3, 4):
            for c in range(-3, 4):
                for e in range(-3, P.HEAD + 4): near.add((x + a, y + e, z + c))
    for (x, y, z), nm in sorted(under.items()):
        if b.get(x, y, z) is not None or y > dn.gr.g(x, z): continue
        inbox = x1 - 6 <= x <= x2 + 6 and z1 - 6 <= z <= z2 + 6 and F - 6 <= y <= F + P.AIR + 1 + 6
        if not (inbox or (x, y, z) in near): continue
        b.set(x, y, z, "minecraft:stone"); n += 1
    dn.meta["filled"] = n


def chain(b, dn):
    """the signs of the chain of bones: skulls (blocks), ribs (1 or 2 bone blocks lying on the ground), bones (item_displays: the
    datapack). Returns (the item_display points, the deco columns outside the place)"""
    disp = []; deco = []
    for (x, y, z, kind) in dn.pl["signs"]:
        if kind == "skull": b.set(x, y, z, "minecraft:skeleton_skull[rotation=%d]" % int(hsh(x, 11, z, 54) * 16)); cells = [(x, z)]
        elif kind == "ribs":
            ax = "x" if hsh(x, 12, z, 55) < 0.5 else "z"
            b.set(x, y, z, "minecraft:bone_block[axis=%s]" % ax); cells = [(x, z)]
            if hsh(x, 13, z, 56) < 0.5:
                nx, nz = (x + 1, z) if ax == "x" else (x, z + 1)
                if abs(dn.gr.g(nx, nz) + 1 - y) == 0: b.set(nx, y, nz, "minecraft:bone_block[axis=%s]" % ax); cells.append((nx, nz))
        else:
            disp.append([x + 0.5, y + 0.03, z + 0.5, int(hsh(x, 14, z, 57) * 360)]); cells = []
        for c in cells:
            if not P.in_place(*c): deco.append(list(c))
    return disp, deco


def zone_lines(dn):
    from r1 import replace_lines
    x1, z1, x2, z2 = dn.r; F = dn.F
    xs = [c[0] for c in dn.cells] + [e[0] for e in dn.exit]; zs = [c[1] for c in dn.cells] + [e[1] for e in dn.exit]
    ys = [c[2] for c in dn.cells]
    cave = (x1 - 1, F - 1, z1 - 1, x2 + 1, F + P.AIR + 2, z2 + 1)
    st = (min(xs) - 1, min(ys) - 1, min(zs) - 1, max(xs) + 1, dn.top + 4, max(zs) + 1)
    replace_lines(os.path.join(ROOT, "zones/zones.txt"), ["ogre_den ", "ogre_den_stair "],
                  ["ogre_den        overworld box  %d %d %d %d %d %d   dungeon   # T-034: the Ogre's Den (the cave)" % cave,
                   "ogre_den_stair  overworld box  %d %d %d %d %d %d   dungeon   # T-034: the Ogre's Den (the stair and its mouth)" % st])
    return cave, st


def vault_line(dn):
    from r1 import replace_lines
    x, y, z = dn.meta["chest"]
    replace_lines(os.path.join(ROOT, "treasury/vaults.txt"), ["vault r1_ogre "],
                  ["vault r1_ogre r1 overworld %d %d %d block=chest[facing=east] build=0   # T-034: the Ogre's Den, under the bed of hides" % (x, y, z)])


def main():
    gr, pl = P.plan()
    dn = Den(gr, pl)
    dn.flat = flat_spots(dn)
    b = B("ogre")
    x1, z1, x2, z2 = dn.r
    under = under_blocks(gr, (x1 - 6, z1 - 6, x2 + 6, z2 + 6), dn.F - 6)
    ux = [c[0] for c in dn.cells]; uz = [c[1] for c in dn.cells]
    under.update(under_blocks(gr, (min(ux) - 3, min(uz) - 3, max(ux) + 3, max(uz) + 3), min(c[2] for c in dn.cells) - 4, "ogre_under_stair"))
    cave_shape(b, dn)
    stair(b, dn)
    lair(b, dn)
    perches, oak_top = oak(b, dn)
    trunk = fallen(b, dn)
    disp, deco = chain(b, dn)
    fill(b, dn, under)
    from connect import connect
    connect(b)
    bad = [k for k in b.v if not (P.BOX[0] <= k[0] <= P.BOX[2] and P.BOX[1] <= k[2] <= P.BOX[3])]
    if bad: raise SystemExit("blocks outside the box: %s" % bad[:5])
    lit = [(k, s) for k, s in b.v.items() if re.search(r"torch|lantern|glowstone|shroomlight|froglight|lava|campfire\[.*lit=true|sea_lantern|candle\[.*lit=true", s)]
    if lit: raise SystemExit("light in the den: %s" % lit[:3])
    n = b.write_placements(os.path.join(OUT, "ogre.txt"))
    cave_box, stair_box = zone_lines(dn)
    vault_line(dn)
    m = dn.meta
    ravens = [[trunk[2][0] + 0.5, trunk[2][1] + 1.0, trunk[2][2] + 0.5, 0], [trunk[-3][0] + 0.5, trunk[-3][1] + 1.0, trunk[-3][2] + 0.5, 120],
              perches[0] + [240]]
    out = dict(place=list(P.PLACE), box=list(P.BOX), cave=list(dn.r), F=dn.F, top=dn.top, exit=[list(e) for e in dn.exit],
               stair=[[c[0], c[1], c[2], c[3], list(c[4])] for c in dn.cells], stairs=pl["stair"]["stairs"], oak=pl["oak"], oak_top=oak_top,
               trunk=[list(t) for t in trunk], ravens=ravens, signs=pl["signs"], sign_disp=disp, way=pl["way"], trail_start=list(pl["trail_start"]),
               way_len=pl["way_len"], zone_cave=list(cave_box), zone_stair=list(stair_box), blocks=n, h={"%d,%d" % k: v for k, v in dn.h.items()},
               ceil={"%d,%d" % k: v for k, v in dn.ceil.items()}, **m)
    json.dump(dict(deco=deco), open(os.path.join(OUT, "ogre_deco.json"), "w"))
    try:
        import treasury_dp
        treasury_dp.run_ogre(out)
    except ImportError: pass
    json.dump(out, open(os.path.join(OUT, "ogre.json"), "w"), ensure_ascii=False)
    print("ogre: %d blocks, cave %s F %d, stairs %d (top %d), signs %d (way %.0f), filled %d, deco columns outside the place %d"
          % (n, dn.r, dn.F, pl["stair"]["stairs"], dn.top, len(pl["signs"]), pl["way_len"], m["filled"], len(deco)))


if __name__ == "__main__":
    main()
