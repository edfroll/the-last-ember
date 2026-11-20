"""T-027: the block models of the Cemetery of the Fallen Knights (the descent, the gate, the hill with the three swords, the small swords,
the fresh graves, the barrows, the crypt of the Magister, the chapel, the fence) for tools/build/r1_cemetery.py. Palettes from the card
«Кладбище Павших Рыцарей · Р1»."""
import math
from lib import Mix, h as hsh
import cemetery_plan as P
from cemetery_plan import ix, DIRS, BACK, LEFT, RIGHT

def st(name, **p): return "minecraft:%s[%s]" % (name, ",".join("%s=%s" % kv for kv in p.items())) if p else "minecraft:" + name
def stairs(block, facing, half="bottom", shape="straight"): return st(block, facing=facing, half=half, shape=shape, waterlogged="false")
def slab(block, t="bottom"): return st(block, type=t, waterlogged="false")
def candle(color="", n=1, lit=True): return st((color + "_candle") if color else "candle", candles=n, lit="true" if lit else "false", waterlogged="false")
def lantern(kind="lantern", hanging=False): return st(kind, hanging="true" if hanging else "false", waterlogged="false")
def chain(axis="y"): return st("iron_chain", axis=axis, waterlogged="false")
def sign_nbt(lines):
    msgs = [{"text": t} for t in lines] + [""] * (4 - len(lines))
    m = ",".join(('{"text":"%s"}' % t["text"]) if isinstance(t, dict) else '""' for t in msgs)
    return "{is_waxed:1b,front_text:{messages:[%s]},back_text:{messages:[%s]}}" % (m, m)
def book_nbt(title, author, pages):
    pg = ",".join('{raw:"%s"}' % p.replace('"', '\\"') for p in pages)
    return '{Book:{id:"minecraft:written_book",count:1,components:{"minecraft:written_book_content":{title:{raw:"%s"},author:"%s",pages:[%s]}}}}' % (title, author, pg)
FACES = ("north", "east", "south", "west")
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}
D2F = {"N": "north", "S": "south", "E": "east", "W": "west"}
F2D = {v: k for k, v in D2F.items()}

GROUND = Mix({"grass_block": 30, "podzol": 25, "coarse_dirt": 20, "rooted_dirt": 10, "moss_block": 5}, 7001)
PATHG = Mix({"gravel": 60, "coarse_dirt": 25, "rooted_dirt": 15}, 7002)
HEAD = Mix({"tuff": 30, "calcite": 25, "tuff_bricks": 10, "polished_tuff": 10, "andesite": 15, "mossy_cobblestone": 10}, 7003)
SWORD = Mix({"stone": 30, "andesite": 25, "polished_andesite": 15, "cracked_stone_bricks": 15, "tuff": 10, "brown_terracotta": 3, "packed_mud": 2}, 7004)
CRYPT = Mix({"deepslate_tiles": 35, "cracked_deepslate_tiles": 20, "cobbled_deepslate": 15, "polished_deepslate": 15, "chiseled_deepslate": 5, "mossy_cobblestone": 10}, 7005)
CRYPT_FLOOR = Mix({"deepslate_tiles": 45, "cracked_deepslate_tiles": 25, "cobbled_deepslate": 20, "mossy_cobblestone": 10}, 7006)
CHAPEL = Mix({"stone_bricks": 55, "mossy_stone_bricks": 35, "cracked_stone_bricks": 10}, 7007)
LAND = Mix({"stone_bricks": 45, "mossy_stone_bricks": 30, "cracked_stone_bricks": 15, "cobblestone": 10}, 7008)
WALLB = Mix({"cobblestone": 40, "mossy_cobblestone": 35, "stone": 15, "andesite": 10}, 7009)
EARTH = Mix({"dirt": 55, "coarse_dirt": 25, "rooted_dirt": 20}, 7010)

class Ctx:
    def __init__(self, gr, rl, W):
        self.gr, self.rl, self.W = gr, rl, W; self.T = rl["T"]
    def g(self, x, z): return int(self.T[ix(self.gr, x, z)])
def free(b, x, y, z): return b.get(x, y, z) in (None, "minecraft:air")
def clear(b, x, y1, z, y2):
    for y in range(y1, y2 + 1):
        if b.get(x, y, z) is None: b.set(x, y, z, "minecraft:air")

# ---------------------------------------------------------------- walks: the descent, the hill stair, the platform
def walks(b, c):
    """stairs (stone bricks, mossy), landings, parapets on the fill side, retaining walls on the cut side; 4 of headroom"""
    rl = c.rl; walk, ring = rl["walk"], rl["ring"]
    STAIR = ("stone_brick_stairs", "mossy_stone_brick_stairs")
    for (x, z), (y, k, f) in walk.items():
        if k == "S": b.set(x, y, z, stairs(STAIR[0] if hsh(x, y, z, 7020) < 0.6 else STAIR[1], D2F[f]))
        elif k == "P": b.set(x, y, z, Mix({"gravel": 30, "coarse_dirt": 25, "tuff": 15, "polished_tuff": 15, "moss_block": 15}, 7021).at(x, y, z))
        else: b.set(x, y, z, LAND.at(x, y, z))
        clear(b, x, y + 1, z, y + 4)
    for (x, z), (kind, y) in ring.items():
        if kind == "wall":
            top = min(c.g(x, z), y + 7)
            for yy in range(y + 1, top + 1): b.set(x, yy, z, WALLB.at(x, yy, z))
        elif kind == "parapet":
            b.set(x, y, z, LAND.at(x, y, z))
            b.set(x, y + 1, z, "minecraft:mossy_stone_brick_wall" if hsh(x, y, z, 7022) < 0.4 else "minecraft:stone_brick_wall")
            clear(b, x, y + 2, z, y + 4)
        else:
            clear(b, x, y + 1, z, y + 3)

def gate(b, c):
    """the wrought gate at the start of the descent (at the east edge of the pad of bonfire 2): stone posts, an iron arch, lanterns"""
    walk = c.rl["walk"]
    # the first landing of the descent: 3 cells at z 447..449; posts at z 446 and 450 on the line x 128
    y = P.PAD_Y; x = 128
    for z in (446, 450):
        for yy in range(y + 1, y + 5): b.set(x, yy, z, "minecraft:polished_deepslate" if yy < y + 4 else "minecraft:chiseled_deepslate")
        b.set(x, y + 5, z, lantern())
    for z in range(447, 450):
        b.set(x, y + 4, z, "minecraft:iron_bars"); b.set(x, y + 5, z, "minecraft:iron_bars" if z == 448 else "minecraft:air")
    # the open leaves of the gate, folded back against the posts (iron bars along x)
    for zz, dz in ((446, -1), (450, 1)):
        for yy in (y + 1, y + 2, y + 3): b.set(x + 1, yy, zz, "minecraft:iron_bars"); b.set(x + 2, yy, zz, "minecraft:iron_bars")
    return [x, y + 1, 448]

def lights(b, c, desc):
    """lanterns on posts at the top of the descent (the first three landings), nothing lower: the floor and the barrows stay dark"""
    out = []
    lands = [cc for cc in desc if cc[4] == "L"]
    seen = 0
    for (x, z, y, dr, k) in lands:
        if y < P.PAD_Y - 30: break
        dx, dz = DIRS[dr]; px, pz = x - dz * 2, z + dx * 2
        if (px, pz) in c.rl["walk"] or any(abs(px - a) + abs(pz - bb) < 7 for a, bb, _ in out): continue
        if c.rl["ring"].get((px, pz), ("", 0))[0] not in ("parapet", "edge"): continue
        b.set(px, y + 1, pz, "minecraft:stone_brick_wall"); b.set(px, y + 2, pz, "minecraft:stone_brick_wall"); b.set(px, y + 3, pz, lantern())
        out.append((px, pz, y)); seen += 1
    return out

# ---------------------------------------------------------------- swords
def big_sword(height, tilt):
    """a great sword stuck in the ground: {(dx, dy, dz): state} with the blade up the y axis; tilt = lean of the top along +x (blocks)
    blade 3 wide (2 thick at the root), guard 9 wide, grip, pommel; the lower part of the blade sunk 2 into the ground"""
    out = {}
    blade = int(height * 0.68); grip = max(3, height // 8)
    def lean(dy): return int(round(tilt * dy / height))
    for dy in range(-2, blade):
        w = 1 if dy > blade - 3 else 3; t = 2 if dy < blade // 2 else 1
        for a in range(-(w // 2), w // 2 + 1):
            for d in range(t):
                out[(a + lean(dy), dy, d)] = "S"
        if dy > blade - 3: out[(lean(dy), dy, 0)] = "S"
    gy = blade
    for a in range(-4, 5):
        out[(a + lean(gy), gy, 0)] = "G"; out[(a + lean(gy), gy, 1)] = "G"
        if abs(a) == 4: out[(a + lean(gy), gy + 1, 0)] = "G"
    for dy in range(gy + 1, gy + 1 + grip): out[(lean(dy), dy, 0)] = "H"
    py = gy + 1 + grip
    for a in (-1, 0, 1):
        for d in (0,):
            out[(a + lean(py), py, d)] = "P"
    out[(lean(py + 1), py + 1, 0)] = "P"
    return out
def sword_state(k, x, y, z):
    if k == "S": return SWORD.at(x, y, z)
    if k == "G": return "minecraft:polished_andesite" if hsh(x, y, z, 7030) < 0.7 else "minecraft:andesite"
    if k == "H": return "minecraft:dark_oak_log[axis=y]" if hsh(x, y, z, 7031) < 0.5 else "minecraft:stripped_dark_oak_log[axis=y]"
    return "minecraft:chiseled_stone_bricks"
SWORDS = [(237, 494, 22, 0, "fall"), (241, 501, 30, 2, "lean"), (244, 496, 26, 0, "")]    # (x, z, height, tilt along x, role)
def three_swords(b, c, L):
    """the three great swords on the platform (y L = its top block): 22, 30 (leaning) and 26 high; the plate with the words"""
    out = []
    for (x, z, hgt, tilt, role) in SWORDS:
        m = big_sword(hgt, tilt)
        cells = {}
        for (dx, dy, dz), k in m.items():
            yy = L + 1 + dy
            cells[(x + dx, yy, z + dz)] = sword_state(k, x + dx, yy, z + dz)
        out.append(dict(x=x, z=z, h=hgt, role=role, cells=cells))
        if role != "fall":
            for p, s in cells.items(): b.set(*p, s)
    # the plate at the foot of the swords (north edge of the platform, by the stair) with the words
    px, pz = 236, P.HILL[1] + 1
    b.set(px, L + 1, pz, "minecraft:polished_tuff"); b.set(px + 1, L + 1, pz, "minecraft:polished_tuff")
    b.set(px, L + 2, pz, "minecraft:pale_oak_wall_sign[facing=north,waterlogged=false]" + P_sign(["Трое несли огонь.", "Огонь не дошёл."]))
    return out
def P_sign(lines): return sign_nbt(lines)

def fallen_sword(L, stair):
    """the 22-high sword of the platform after the fading: lying west-east across the north flight of the hill stair, 4 over its steps
    (an arch: the blade rests on its guard and on the slope), {(x, y, z): state}. stair: {z: level of the stair block} of the flight"""
    zb = 482; yb = stair[zb] + 4
    cells = {}
    blade = int(22 * 0.68)
    x0 = 228                                      # the tip in the west, the hilt in the east (on the platform's slope)
    for k in range(blade):
        x = x0 + k
        for d in (0, 1) if k > 2 else (0,):
            cells[(x, yb + d, zb)] = SWORD.at(x, yb + d, zb)
    gx = x0 + blade
    for a in range(-3, 4):
        cells[(gx, yb + a if yb + a > yb - 4 else yb - 3, zb)] = "minecraft:polished_andesite"
    for k in range(1, 4): cells[(gx + k, yb + 1, zb)] = "minecraft:dark_oak_log[axis=x]"
    cells[(gx + 4, yb + 1, zb)] = "minecraft:chiseled_stone_bricks"
    return cells

def small_sword(b, c, x, z, hgt, salt):
    """a small sword (3..6): the blade a deepslate or tuff wall, the guard of slabs or stairs, sometimes leaning (a stair at the top)"""
    y = c.g(x, z)
    wall = "minecraft:polished_deepslate_wall" if hsh(x, 0, z, salt) < 0.55 else "minecraft:tuff_wall"
    blade = hgt - 2
    for k in range(blade): b.set(x, y + 1 + k, z, wall)
    gy = y + 1 + blade
    ax = hsh(x, 1, z, salt) < 0.5
    gb = "polished_deepslate" if "deepslate" in wall else "polished_tuff"
    b.set(x, gy, z, "minecraft:%s" % ("chiseled_tuff" if gb == "polished_tuff" else "chiseled_deepslate"))
    for s_ in (-1, 1):
        q = (x + s_, z) if ax else (x, z + s_)
        if free(b, q[0], gy, q[1]) and free(b, q[0], gy - 1, q[1]):
            f = ("east" if s_ < 0 else "west") if ax else ("south" if s_ < 0 else "north")
            b.set(q[0], gy, q[1], stairs("%s_stairs" % gb, f, "top"))
    b.set(x, gy + 1, z, wall)

# ---------------------------------------------------------------- the fresh graves
def grave(b, c, gv, lit=True):
    """the mound 1x2 of soul soil (2 layers: y+1 over the ground and y in it), the coffin lid (dark oak trapdoors) at y-1, the coffin (air)
    at y-2 in planks; the headstone at (x, z-1) 2 high with the epitaph (a wall sign on its south face, over the head of the mound) and a
    candle on top (lit; unlit on the two pits). Pits: the mound only (the collapse trap's floor), a void 4 deep under it walled round,
    a ladder on the head wall: the way out without jumps."""
    x, z, y = gv["x"], gv["z"], gv["y"]
    hb = HEAD.at(x, y + 1, z - 1)
    b.set(x, y + 1, z - 1, hb); b.set(x, y + 2, z - 1, hb)
    b.set(x, y + 3, z - 1, candle("", 1, gv["kind"] != "pit"))
    b.set(x, y + 2, z, "minecraft:dark_oak_wall_sign[facing=south,waterlogged=false]" + sign_nbt(gv["ep"]))
    pit = gv["kind"] == "pit"
    for dz in (0, 1):
        zz = z + dz
        b.set(x, y + 1, zz, "minecraft:soul_soil")
        if pit:
            for yy in range(y - 3, y + 1): b.set(x, yy, zz, "minecraft:air")
            b.set(x, y - 4, zz, "minecraft:coarse_dirt")
            for a in (-1, 1):
                for yy in range(y - 3, y + 1): b.set(x + a, yy, zz, EARTH.at(x + a, yy, zz) if yy >= y - 1 else "minecraft:stone")
        else:
            b.set(x, y, zz, "minecraft:soul_soil")
            b.set(x, y - 1, zz, "minecraft:dark_oak_trapdoor[facing=north,half=top,open=false,powered=false,waterlogged=false]")
            b.set(x, y - 2, zz, "minecraft:air"); b.set(x, y - 3, zz, "minecraft:dark_oak_planks")
            for a in (-1, 1): b.set(x + a, y - 2, zz, "minecraft:dark_oak_planks"); b.set(x + a, y - 1, zz, EARTH.at(x + a, y - 1, zz))
    if pit:
        for yy in range(y - 3, y + 1):
            b.set(x, yy, z - 1, "minecraft:mossy_cobblestone" if yy < y else hb)
            b.set(x, yy, z + 2, EARTH.at(x, yy, z + 2) if yy >= y - 1 else "minecraft:stone")
            b.set(x, yy, z, "minecraft:ladder[facing=south,waterlogged=false]")
    else:
        b.set(x, y - 2, z - 1, "minecraft:dark_oak_planks"); b.set(x, y - 2, z + 2, "minecraft:dark_oak_planks")
    return dict(n=gv["n"], kind=gv["kind"], ep=gv["ep"], x=x, y=y, z=z, lid=[x, y - 1, z], coffin=[x, y - 2, z], candle=[x, y + 3, z - 1], sign=[x, y + 2, z])

# ---------------------------------------------------------------- the barrows (one template, 3 variants)
LOOT = '{LootTable:"last_ember:chests/r1/common"}'
def barrow(b, c, br, n_loot):
    """a small crypt 9 x 12 under its mound: the chamber 7 x 7 (floor E, vault E+4), the dromos 3 long in front, the stair along the left
    wall up to the top of the mound (the second way out); dark inside; pots and barrels (n_loot of them with chests/r1/common)"""
    E = br["E"]; f = br["facing"]; F = D2F[f]
    L2G = {v: k for k, v in br["cells"].items()}
    def G(lx, lz): return L2G[(lx, lz)]
    def S(lx, y, lz, s): x, z = G(lx, lz); b.set(x, y, z, s)
    var = br["id"] % 3
    lf = D2F[LEFT[f]]; rf = D2F[RIGHT[f]]                  # facings toward the left / right wall (seen from the dromos looking in)
    for lz in range(0, 9):
        for lx in range(0, 9):
            wall = lx in (0, 8) or lz in (0, 8)
            for y in range(E, E + 5):
                x, z = G(lx, lz)
                if y == E: S(lx, y, lz, CRYPT_FLOOR.at(x, y, z) if not wall else CRYPT.at(x, y, z))
                elif y == E + 4: S(lx, y, lz, CRYPT.at(x, y, z))
                elif wall: S(lx, y, lz, CRYPT.at(x, y, z))
                else: S(lx, y, lz, "minecraft:air")
            S(lx, E - 1, lz, "minecraft:cobbled_deepslate")
            if lz <= 8: S(lx, E + 5, lz, EARTH.at(*G(lx, lz)[:1], E + 5, G(lx, lz)[1])); S(lx, E + 6, lz, "minecraft:coarse_dirt" if hsh(*G(lx, lz), 7050) < 0.4 else "minecraft:grass_block")
    # the doorway in the front wall and the dromos (walls step down to the front, open to the sky)
    for lx in (3, 4, 5):
        for y in (E + 1, E + 2, E + 3): S(lx, y, 8, "minecraft:air")
    S(4, E + 4, 8, "minecraft:chiseled_deepslate")
    for lz in (9, 10, 11):
        for lx in (3, 4, 5):
            x, z = G(lx, lz); S(lx, E, lz, CRYPT_FLOOR.at(x, E, z)); S(lx, E - 1, lz, "minecraft:cobbled_deepslate")
            for y in range(E + 1, E + 8): S(lx, y, lz, "minecraft:air")
        top = E + 5 - (lz - 9)
        for lx in (2, 6):
            for y in range(E, top + 1): x, z = G(lx, lz); S(lx, y, lz, CRYPT.at(x, y, z))
        if lz == 11:
            for lx in (2, 6): S(lx, top + 1, lz, "minecraft:skeleton_skull[rotation=%d]" % {"S": 0, "W": 4, "N": 8, "E": 12}[f])
    # the stair up along lx 1 (lz 2..7, E+1..E+6), the landing on the front wall (lz 8, E+6), the shaft open to the sky over lz 3..8
    for k, lz in enumerate(range(2, 8)):
        y = E + 1 + k
        S(1, y, lz, stairs("cobbled_deepslate_stairs", F))
        for yy in range(E + 1, y): S(1, yy, lz, "minecraft:cobbled_deepslate")
        for yy in range(y + 1, E + 9): 
            if lz >= 3 or yy <= E + 3: S(1, yy, lz, "minecraft:air")
    for yy in range(E + 1, E + 7): S(1, yy, 8, "minecraft:polished_deepslate" if yy == E + 6 else CRYPT.at(*G(1, 8)[:1], yy, G(1, 8)[1]))
    for yy in range(E + 7, E + 9): S(1, yy, 8, "minecraft:air")
    for lz in range(3, 9):                                  # the rim of the slot: the vault stays round it
        for lx in (0, 2):
            for yy in range(E + 4, E + 7): x, z = G(lx, lz); S(lx, yy, lz, CRYPT.at(x, yy, z) if yy <= E + 5 else "minecraft:mossy_cobblestone")
    # the inside: variant 0 niches with pots both sides, 1 a stone coffin in the middle and barrels at the back, 2 a fallen corner
    spots = []
    if var == 0:
        for lz in (2, 4, 6):
            spots.append((7, lz)); S(7, E + 3, lz, "minecraft:cobweb" if lz == 4 else "minecraft:air")
        spots += [(5, 1), (3, 1)]
    elif var == 1:
        for lz in (3, 4, 5):
            for lx in (4, 5): S(lx, E + 1, lz, "minecraft:polished_deepslate" if lz != 4 else "minecraft:chiseled_deepslate")
        spots += [(3, 1), (5, 1), (7, 1), (7, 6)]
    else:
        for (lx, lz, hh) in ((7, 1, 3), (6, 1, 2), (7, 2, 2), (6, 2, 1), (5, 1, 1)):
            for y in range(E + 1, E + 1 + hh): S(lx, y, lz, "minecraft:cobbled_deepslate" if y < E + hh else "minecraft:gravel")
        spots += [(7, 5), (7, 3), (3, 1), (4, 1)]
    out = []
    for k, (lx, lz) in enumerate(spots):
        x, z = G(lx, lz); loot = k < n_loot
        if var == 1 or (var == 2 and k % 2 == 0):
            s = st("barrel", facing="up", open="false") + (LOOT if loot else "")
        else:
            s = st("decorated_pot", cracked="true" if hsh(x, 0, z, 7051) < 0.5 else "false", facing=F, waterlogged="false") + (LOOT if loot else "")
        b.set(x, E + 1, z, s); out.append(dict(x=x, y=E + 1, z=z, loot=loot))
    # bones, cobwebs, chains, unlit candles (dark inside)
    for (lx, lz, s) in ((2, 6, "minecraft:bone_block[axis=x]"), (6, 2, candle("black", 2, False)), (2, 2, candle("white", 1, False)), (4, 6, "minecraft:cobweb")):
        x, z = G(lx, lz)
        if b.get(x, E + 1, z) == "minecraft:air": b.set(x, E + 1, z, s)
    x, z = G(4, 4); b.set(x, E + 3, z, chain())
    return dict(id=br["id"], E=E, facing=f, front=br["front"], door=list(G(4, 8)), top=list(G(1, 8)) + [E + 6], containers=out,
                inside=list(G(4, 4)), box=[min(k[0] for k in br["cells"]), E - 1, min(k[1] for k in br["cells"]), max(k[0] for k in br["cells"]), E + 7, max(k[1] for k in br["cells"])])

# ---------------------------------------------------------------- the crypt of the Magister
CX = P.CRYPT_X; ZF = P.CRYPT_FRONT
def crypt(b, c, E, W):
    """facade with the iron door between two great skulls; vestibule 7 x 6 (chest 1); stair down to the trap corridor 3 x 15 (4 plates,
    dispenser faces in a row in chiseled deepslate); stair down to the hall 20 x 20 x 8 (4 columns 2 x 2, the sarcophagus in the
    middle, candles round it only, 2 wall niches by the columns, chest 2 behind the sarcophagus under a lock block); the exit of the
    hall (iron bars, opened after the victory) and its passage up to the foot of the slope west of the facade"""
    C = W - 6; HF = W - 20; HC = HF + 9
    m = {}
    def S(x, y, z, s): b.set(x, y, z, s)
    def room(x1, z1, x2, z2, fy, h, floor=CRYPT_FLOOR, shell=CRYPT):
        for x in range(x1 - 1, x2 + 2):
            for z in range(z1 - 1, z2 + 2):
                for y in range(fy - 1, fy + h + 2):
                    inside = x1 <= x <= x2 and z1 <= z <= z2 and fy < y <= fy + h
                    if inside: S(x, y, z, "minecraft:air")
                    elif y == fy and x1 <= x <= x2 and z1 <= z <= z2: S(x, y, z, floor.at(x, y, z))
                    elif b.get(x, y, z) is None: S(x, y, z, shell.at(x, y, z))          # never over a stair or a room already there
    def flight(x1, x2, zs, y0, facing, head=4):
        """stairs over the cells (x1..x2, z in zs), levels y0, y0-1, ... (descending northward), shell round them"""
        for k, z in enumerate(zs):
            y = y0 - k
            for x in range(x1 - 1, x2 + 2):
                for yy in range(y - 1, y + head + 2):
                    if x in (x1 - 1, x2 + 1) or yy == y + head + 1 or yy == y - 1:
                        if b.get(x, yy, z) != "minecraft:air": S(x, yy, z, CRYPT.at(x, yy, z))
                    elif yy == y: S(x, yy, z, stairs("deepslate_tile_stairs", facing))
                    elif yy > y: S(x, yy, z, "minecraft:air")
    # facade (z = ZF) and the vestibule (z ZF-6 .. ZF-1, x CX-3 .. CX+3)
    room(CX - 3, ZF - 6, CX + 3, ZF - 1, E, 4)
    for x in range(CX - 5, CX + 6):
        for y in range(E, E + 8):
            S(x, y, ZF, CRYPT.at(x, y, ZF) if abs(x - CX) > 1 or y > E + 3 else "minecraft:polished_deepslate")
    for y in (E + 1, E + 2): S(CX, y, ZF, "minecraft:iron_door[facing=north,half=%s,hinge=left,open=false,powered=false]" % ("lower" if y == E + 1 else "upper"))
    for x in (CX - 1, CX + 1):
        for y in (E + 1, E + 2, E + 3): S(x, y, ZF, "minecraft:chiseled_deepslate")
    S(CX, E + 3, ZF, "minecraft:chiseled_polished_blackstone")
    for k, x in enumerate(range(CX - 4, CX + 5)): S(x, E + 8, ZF, slab("deepslate_tile_slab"))
    for x in range(CX - 5, CX + 6): S(x, E, ZF + 1, "minecraft:polished_deepslate"); S(x, E, ZF + 2, CRYPT_FLOOR.at(x, E, ZF + 2))
    # the skull guards: two great skulls (5 x 5 x 4 of bone and calcite, dark eye holes and nose, teeth) on both sides of the door
    for sx in (CX - 4, CX + 4):
        for dx in (-1, 0, 1):
            for dy in range(0, 4):
                for dz in range(1, 5):
                    x, y, z = sx + dx, E + 1 + dy, ZF + dz
                    S(x, y, z, "minecraft:bone_block[axis=y]" if hsh(x, y, z, 7060) < 0.6 else "minecraft:calcite")
        for dx in (-1, 1): S(sx + dx, E + 3, ZF + 4, "minecraft:blackstone")           # the eyes (facing south)
        S(sx, E + 2, ZF + 4, "minecraft:polished_blackstone")
        for dx in (-1, 0, 1): S(sx + dx, E + 1, ZF + 4, "minecraft:polished_blackstone_wall" if dx == 0 else "minecraft:iron_bars")
        for dx in (-1, 0, 1): S(sx + dx, E + 5, ZF + 2, slab("smooth_quartz_slab") if dx else "minecraft:calcite")
    m["door"] = [CX, E + 1, ZF]
    S(CX - 3, E + 1, ZF - 6, st("chest", facing="east", type="single", waterlogged="false") + LOOT); m["chest1"] = [CX - 3, E + 1, ZF - 6]
    for (x, z, s) in ((CX + 3, ZF - 1, candle("white", 3, False)), (CX + 3, ZF - 6, "minecraft:cobweb"), (CX - 3, ZF - 1, candle("black", 1, False))): S(x, E + 1, z, s)
    # stair 1: from the vestibule north (z ZF-7 .. ZF-12), 6 stairs E..E-5; the corridor at C from z ZF-13 back to ZF-27 (15)
    flight(CX - 1, CX + 1, range(ZF - 7, ZF - 13, -1), E, "south")
    z1c, z2c = ZF - 27, ZF - 13
    room(CX - 1, z1c, CX + 1, z2c, C, 3)
    plates = []; pts = []
    for k, z in enumerate(range(z2c - 2, z1c, -3)):
        if len(plates) < 4:
            x = CX + (-1, 1, 0, -1)[len(plates)]
            S(x, C + 1, z, "minecraft:polished_blackstone_pressure_plate[powered=false]"); plates.append([x, C + 1, z])
        for side, fx in ((CX - 2, "east"), (CX + 2, "west")):
            S(side, C + 2, z, st("dispenser", facing=fx, triggered="false"))
            S(side, C + 1, z, "minecraft:chiseled_deepslate"); S(side, C + 3, z, "minecraft:chiseled_deepslate")
            pts.append([side + (1 if fx == "east" else -1), C + 2, z])
    for (x, y, z) in ((CX, C + 3, z1c + 4), (CX + 1, C + 3, z2c - 1), (CX - 1, C + 3, z1c + 9)): S(x, y, z, "minecraft:cobweb")
    m.update(corridor=[CX - 1, C, z1c, CX + 1, C + 3, z2c], plates=plates, arrow_pts=pts, C=C)
    # stair 2: 7 stairs, landing 3, 7 stairs down to the hall floor HF
    zz = z1c - 1
    flight(CX - 1, CX + 1, range(zz, zz - 7, -1), C, "south")
    ly = C - 7
    for z in range(zz - 7, zz - 10, -1):
        for x in range(CX - 2, CX + 3):
            for yy in range(ly - 1, ly + 6):
                if abs(x - CX) == 2 or yy in (ly - 1, ly + 5): S(x, yy, z, CRYPT.at(x, yy, z))
                elif yy == ly: S(x, yy, z, CRYPT_FLOOR.at(x, yy, z))
                else: S(x, yy, z, "minecraft:air")
    flight(CX - 1, CX + 1, range(zz - 10, zz - 17, -1), ly, "south")
    # the hall: 20 x 20 (x CX-10 .. CX+9, z hz1 .. hz2), floor HF, 8 of air
    hz2 = zz - 17; hz1 = hz2 - 19; hx1, hx2 = CX - 10, CX + 9
    room(hx1, hz1, hx2, hz2, HF, 8)
    cols = [(hx1 + 5, hz1 + 5), (hx2 - 6, hz1 + 5), (hx1 + 5, hz2 - 6), (hx2 - 6, hz2 - 6)]
    for (x0, z0) in cols:
        for x in (x0, x0 + 1):
            for z in (z0, z0 + 1):
                for yy in range(HF + 1, HF + 9): S(x, yy, z, "minecraft:polished_deepslate" if (yy - HF) % 4 else "minecraft:chiseled_deepslate")
    # the niches of the spirits: in the west and east walls by the middle columns
    niches = []
    for (x, nx) in ((hx1 - 1, hx1), (hx2 + 1, hx2)):
        z = (hz1 + hz2) // 2
        for yy in (HF + 1, HF + 2, HF + 3):
            for dz in (0, 1): S(x, yy, z + dz, "minecraft:air")
        S(x, HF, z, CRYPT_FLOOR.at(x, HF, z)); S(x, HF, z + 1, CRYPT_FLOOR.at(x, HF, z + 1))
        niches.append([nx, HF + 1, z])
    # the sarcophagus (3 x 4: rim of polished blackstone, the hollow 1 x 2 inside, lid of chiseled polished blackstone)
    sx1, sz1 = CX - 1, (hz1 + hz2) // 2 - 1
    for x in range(sx1, sx1 + 3):
        for z in range(sz1, sz1 + 4):
            S(x, HF + 1, z, "minecraft:polished_blackstone" if not (x == sx1 + 1 and z in (sz1 + 1, sz1 + 2)) else "minecraft:air")
            S(x, HF + 2, z, "minecraft:chiseled_polished_blackstone" if (x + z) % 2 == 0 else "minecraft:polished_blackstone_bricks")
    lid = [[x, HF + 2, z] for x in range(sx1, sx1 + 3) for z in range(sz1, sz1 + 4)]
    hollow = [sx1 + 1, HF + 1, sz1 + 1]
    for (x, z) in ((sx1 - 1, sz1 - 1), (sx1 + 3, sz1 - 1), (sx1 - 1, sz1 + 4), (sx1 + 3, sz1 + 4), (sx1 + 1, sz1 - 2), (sx1 + 1, sz1 + 5), (sx1 - 2, sz1 + 1), (sx1 + 4, sz1 + 2)):
        S(x, HF + 1, z, candle("white" if (x + z) % 2 else "black", 2 + (x + z) % 3, True))
    # chest 2 behind the sarcophagus (north), under a lock block (a chest does not open under a solid block)
    ch2 = [sx1 + 1, HF + 1, sz1 - 3]
    S(ch2[0], ch2[1], ch2[2], st("chest", facing="south", type="single", waterlogged="false") + '{LootTable:"last_ember:cemetery/crypt_chest"}')
    S(ch2[0], ch2[1] + 1, ch2[2], "minecraft:chiseled_polished_blackstone")
    # decor: chains, iron bars in the wall niches high up, cobwebs in the corners
    for (x, z) in ((hx1 + 1, hz1 + 1), (hx2 - 1, hz1 + 1), (hx1 + 1, hz2 - 1), (hx2 - 1, hz2 - 1)):
        S(x, HF + 8, z, "minecraft:cobweb")
    for (x0, z0) in cols:
        for yy in (HF + 7, HF + 8): S(x0 - 1 if x0 < CX else x0 + 2, yy, z0, chain())
    # the exit of the hall: bars in the west wall (x hx1-1, z hz1+1..hz1+3), the passage (x hx1-4..hx1-2) south and up to E, out at ZF
    ex = hx1 - 1; ez = (hz1 + 1, hz1 + 3)
    bars = []
    for z in range(ez[0], ez[1] + 1):
        for yy in (HF + 1, HF + 2, HF + 3): S(ex, yy, z, "minecraft:iron_bars"); bars.append([ex, yy, z])
        S(ex, HF, z, CRYPT_FLOOR.at(ex, HF, z))
    px1, px2 = hx1 - 4, hx1 - 2
    room(px1, ez[0], px2, ez[1], HF, 3)
    # flights going south and up: 10 stairs HF+1..HF+10, landing, 10 stairs to E (the top stair at E), then flat to the facade line
    z = ez[1] + 1; y = HF + 1
    path = []
    def up(z, y, n):
        for k in range(n):
            for x in range(px1 - 1, px2 + 2):
                for yy in range(y + k - 1, y + k + 5):
                    if x in (px1 - 1, px2 + 1) or yy == y + k + 4 or yy == y + k - 1:
                        if b.get(x, yy, z + k) != "minecraft:air": S(x, yy, z + k, CRYPT.at(x, yy, z + k))
                    elif yy == y + k: S(x, yy, z + k, stairs("deepslate_tile_stairs", "south"))
                    else: S(x, yy, z + k, "minecraft:air")
            path.append([(px1 + px2) // 2, z + k, y + k])
        return z + n, y + n - 1
    z, y = up(z, y, 10)
    for k in range(3):
        for x in range(px1 - 1, px2 + 2):
            for yy in range(y - 1, y + 5):
                if x in (px1 - 1, px2 + 1) or yy in (y - 1, y + 4): S(x, yy, z + k, CRYPT.at(x, yy, z + k))
                elif yy == y: S(x, yy, z + k, CRYPT_FLOOR.at(x, yy, z + k))
                else: S(x, yy, z + k, "minecraft:air")
        path.append([(px1 + px2) // 2, z + k, y])
    z += 3; y += 1
    z, y = up(z, y, E - y + 1)
    while z <= ZF:
        for x in range(px1 - 1, px2 + 2):
            for yy in range(y - 1, y + 5):
                if x in (px1 - 1, px2 + 1) or yy in (y - 1, y + 4):
                    if z < ZF or yy == y + 4: S(x, yy, z, CRYPT.at(x, yy, z))
                    elif x in (px1 - 1, px2 + 1): S(x, yy, z, "minecraft:polished_deepslate")
                elif yy == y: S(x, yy, z, CRYPT_FLOOR.at(x, yy, z))
                else: S(x, yy, z, "minecraft:air")
        path.append([(px1 + px2) // 2, z, y]); z += 1
    m.update(hall=[hx1, HF, hz1, hx2, HF + 8, hz2], HF=HF, sarc=[sx1 + 1, HF + 1, sz1 + 1], lid=lid, hollow=hollow, chest2=ch2, niches=niches,
             bars=bars, exit_path=path, exit_out=[(px1 + px2) // 2, E + 1, ZF + 2], box=[px1 - 2, HF - 2, hz1 - 2, hx2 + 2, E + 9, ZF + 5], E=E, cols=cols)
    return m

# ---------------------------------------------------------------- the chapel (a ruin without a roof, a dead tree through it)
def chapel(b, c, y):
    x1, z1, x2, z2 = P.CHAPEL; out = {}
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            b.set(x, y, z, CHAPEL.at(x, y, z) if hsh(x, 0, z, 7070) < 0.75 else "minecraft:mossy_cobblestone")
            edge = x in (x1, x2) or z in (z1, z2)
            if not edge:
                for yy in range(y + 1, y + 12): b.set(x, yy, z, "minecraft:air")
                continue
            hh = 2 + int(5 * hsh(x // 2, 1, z // 2, 7071))                   # broken wall heights 2..6
            if x == x2 and abs(z - (z1 + z2) // 2) <= 1: hh = 0                # the doorway (east)
            if x == x1 and abs(z - (z1 + z2) // 2) <= 2: hh = 8 + (1 if z == (z1 + z2) // 2 else 0)   # the apse wall in the west stands higher
            if z in (z1, z2) and (x - x1) % 3 == 2 and hh >= 4: win = True
            else: win = False
            for yy in range(y + 1, y + 1 + hh):
                if win and yy in (y + 2, y + 3): b.set(x, yy, z, "minecraft:air"); continue
                b.set(x, yy, z, CHAPEL.at(x, yy, z))
            for yy in range(y + 1 + hh, y + 12): b.set(x, yy, z, "minecraft:air")
            if hh and hsh(x, 2, z, 7072) < 0.35: b.set(x, y + 1 + hh, z, slab("stone_brick_slab") if hsh(x, 3, z, 7073) < 0.5 else slab("mossy_stone_brick_slab"))
    # rubble inside
    for (x, z) in ((x1 + 1, z1 + 1), (x1 + 2, z1 + 1), (x2 - 1, z2 - 1), (x1 + 1, z2 - 1)):
        b.set(x, y + 1, z, slab("mossy_stone_brick_slab") if (x + z) % 2 else "minecraft:mossy_cobblestone")
    # the dead tree: trunk of stripped pale oak through the middle, dark oak branches over the walls
    tx, tz = (x1 + x2) // 2 - 1, (z1 + z2) // 2
    top = y + 15
    for yy in range(y + 1, top): b.set(tx, yy, tz, "minecraft:stripped_pale_oak_log[axis=y]" if yy < top - 3 else "minecraft:dark_oak_log[axis=y]")
    b.set(tx + 1, y + 1, tz, "minecraft:stripped_pale_oak_wood[axis=y]"); b.set(tx, y + 1, tz + 1, "minecraft:stripped_pale_oak_wood[axis=y]")
    for (dx, dz, yy, n) in ((1, 0, 8, 6), (-1, 0, 10, 5), (0, 1, 11, 5), (0, -1, 7, 6), (1, 1, 13, 3)):
        for k in range(1, n + 1):
            ax = "x" if dz == 0 else ("z" if dx == 0 else "y")
            b.set(tx + dx * k, y + yy + k // 3, tz + dz * k, "minecraft:dark_oak_log[axis=%s]" % ax)
    # 3 old headstones under the tree, the lectern with the keeper's note by the door
    for (x, z) in ((tx - 2, tz - 2), (tx - 2, tz + 2), (tx + 2, tz + 3)):
        b.set(x, y + 1, z, HEAD.at(x, y + 1, z)); b.set(x, y + 2, z, slab("tuff_brick_slab") if (x + z) % 2 else slab("polished_tuff_slab"))
    lx, lz = x2 - 1, (z1 + z2) // 2 - 2
    b.set(lx, y + 1, lz, st("lectern", facing="east", has_book="true", powered="false") + book_nbt("Записка", "смотритель", ["Колокол я повесил у двери. Ударишь — и они затихают. Ненадолго."]))
    return dict(tree=[tx, y + 1, tz], lectern=[lx, y + 1, lz], door=[x2, y + 1, (z1 + z2) // 2], y=y)

# ---------------------------------------------------------------- old graves (stones, armour stands), the fence
def old_graves(b, c, sites):
    out = []
    for (x, z, stand) in sites:
        y = c.g(x, z)
        s = HEAD.at(x, y + 1, z)
        b.set(x, y + 1, z, s)
        if hsh(x, 5, z, 7080) < 0.5: b.set(x, y + 2, z, slab("tuff_brick_slab") if hsh(x, 6, z, 7081) < 0.5 else slab("polished_tuff_slab"))
        b.set(x, y, z + 1, "minecraft:coarse_dirt"); b.set(x, y, z + 2, "minecraft:podzol")
        out.append([x, y + 1, z + 1] if stand else None)
    return [o for o in out if o]

def fence(b, c, cells, gaps):
    """the low broken wall on the edge of the floor: 0 (fallen), 1 or 2 high, mossy and plain cobble with a wall block on top"""
    n = 0
    for (x, z) in cells:
        if (x, z) in gaps: continue
        r = hsh(x // 2, 0, z // 2, 7090)
        if r < 0.28: continue
        y = c.g(x, z); hh = 1 if r < 0.62 else 2
        for k in range(hh): b.set(x, y + 1 + k, z, WALLB.at(x, y + 1 + k, z))
        if hsh(x, 1, z, 7091) < 0.5: b.set(x, y + 1 + hh, z, "minecraft:mossy_cobblestone_wall" if hsh(x, 2, z, 7092) < 0.5 else "minecraft:cobblestone_wall")
        n += 1
    return n
