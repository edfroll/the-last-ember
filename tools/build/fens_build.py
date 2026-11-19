"""T-026: the blocks of the Crooked Fens (models), used by tools/build/r1_fens.py: the hut of the three witches, the ruins of the village
on piles (2 templates x 3 rotations), mangroves and swamp oaks, the boardwalk and the piers, the climb, the lanterns, the water plants.
All functions write into a lib.B voxel model; R is the r1_fens module (constants, grids)."""
import math
from lib import B, Mix, h as hsh, slab

def st(name, **p):
    return "minecraft:%s[%s]" % (name, ",".join("%s=%s" % kv for kv in p.items())) if p else "minecraft:" + name
def stairs(block, facing, half="bottom", shape="straight", wl=False):
    return "minecraft:%s[facing=%s,half=%s,shape=%s,waterlogged=%s]" % (block, facing, half, shape, "true" if wl else "false")
def sl(block, t="bottom", wl=False): return "minecraft:%s[type=%s,waterlogged=%s]" % (block, t, "true" if wl else "false")
def fence(block, wl=False): return "minecraft:%s[waterlogged=%s]" % (block, "true" if wl else "false")     # connections: lib connect() fills them
LOGY = "minecraft:mangrove_log[axis=y]"
FACING = {(0, -1): "north", (0, 1): "south", (-1, 0): "west", (1, 0): "east"}
OPP = {"north": "south", "south": "north", "west": "east", "east": "west"}
def chain(axis="y"): return "minecraft:iron_chain[axis=%s,waterlogged=false]" % axis
def lantern(kind="lantern", hanging=False, wl=False): return "minecraft:%s[hanging=%s,waterlogged=%s]" % (kind, "true" if hanging else "false", "true" if wl else "false")

class Ctx:
    """the target ground T, the water W, helpers"""
    def __init__(self, R, gr, rl, W):
        self.R, self.gr, self.rl, self.W = R, gr, rl, W; self.T = rl["T"]; self.Wt = rl["Wt"]
    def g(self, x, z): return int(self.T[self.R.ix(self.gr, x, z)])
    def wet(self, x, z): return self.Wt[self.R.ix(self.gr, x, z)] != self.R.NONE
    def inw(self, x, y, z): return self.wet(x, z) and self.g(x, z) < y <= self.W     # a water cell

# ---------------------------------------------------------------- piles, decks
def pile(b, c, x, z, top, block=LOGY):
    """a pile from the ground (bottom of the water) up to `top`"""
    for y in range(c.g(x, z) + 1, top + 1): b.set(x, y, z, block)
def deck_block(x, z, salt):
    r = hsh(x, 0, z, salt)
    return "minecraft:spruce_planks" if r < 0.55 else ("minecraft:stripped_mangrove_log[axis=x]" if r < 0.8 else "minecraft:stripped_mangrove_log[axis=z]")
def water_fence(c, x, y, z, block="spruce_fence"):
    return fence(block, c.inw(x, y, z))

# ---------------------------------------------------------------- the boardwalk (2 wide, deck W+1, gaps with tussocks, the dark gap)
def boardwalk(b, c, ft):
    W = c.W; deck = ft["deck"]; rl = c.rl; posts = []; route = []
    gaps = ft["gaps"]
    for k, (a, b2, n) in enumerate(deck):
        g = next((g for g in gaps if g["k"] - 1 <= k <= g["k"] + 1), None)
        if g is None:
            for (x, z) in (a, b2):
                b.set(x, W + 1, z, deck_block(x, z, 5201))
                for y in range(W + 2, W + 5):
                    if b.get(x, y, z) is None: b.set(x, y, z, "minecraft:air")
            if k % 3 == 0:
                for (x, z) in (a, b2): pile(b, c, x, z, W)
        else:
            if not g["dark"] and k == g["k"]:
                for (x, z) in (a, b2):
                    b.set(x, W + 1, z, "minecraft:moss_block" if hsh(x, 1, z, 5202) < 0.5 else "minecraft:mud")
                    if hsh(x, 2, z, 5203) < 0.4: b.set(x, W + 2, z, "minecraft:moss_carpet")
        # the railing: chains between fence posts on the outer side (right of the way), on every second stretch of 9
        if g is None and (k // 9) % 2 == 1:
            rx, rz = a[0] - n[0], a[1] - n[1]
            if not any(gg["k"] - 3 <= k <= gg["k"] + 3 for gg in gaps):
                if k % 3 == 0:
                    for y in range(c.g(rx, rz) + 1, W + 3): b.set(rx, y, rz, water_fence(c, rx, y, rz))
                else:
                    tx = deck[min(k + 1, len(deck) - 1)][0][0] - deck[max(k - 1, 0)][0][0]
                    b.set(rx, W + 2, rz, chain("x" if abs(tx) >= 1 else "z"))
    # the dark gap: piles beside it (the way round by jumping), no tussock
    for g in gaps:
        if not g["dark"]: continue
        k = g["k"]; a, b2, n = deck[k]
        for kk in (k - 1, k + 1):
            aa = deck[kk][0]; px, pz = aa[0] - n[0], aa[1] - n[1]
            pile(b, c, px, pz, W + 1, "minecraft:mangrove_log[axis=y]"); posts.append((px, W + 1, pz))
    return posts

# ---------------------------------------------------------------- piers
def pier(b, c, cells, boats):
    """a deck at W+1 over the cells, piles at every second cell, two posts with lanterns at the water end"""
    W = c.W
    for (x, z) in cells:
        b.set(x, W + 1, z, deck_block(x, z, 5301))
        for y in range(W + 2, W + 6):
            if b.get(x, y, z) is None: b.set(x, y, z, "minecraft:air")
        if (x + z) % 2 == 0: pile(b, c, x, z, W)
    return boats

# ---------------------------------------------------------------- the climb (graded way of half blocks, deck on piles where high)
CLIMB = Mix({"mud_bricks": 40, "cobblestone": 15, "packed_mud": 20, "mossy_cobblestone": 15, "muddy_mangrove_roots": 10}, 5401)
def climb_blocks(b, c, rl, gr, R):
    surf = rl["surf"]; trestle = rl["trestle"]; out = []
    for (x, z), s2 in surf.items():
        if gr["allow"][R.ix(gr, x, z)]: continue
        half = s2 % 2 == 1
        y = (s2 - 1) // 2 if half else s2 // 2 - 1          # the block of the way: a slab at y (top y+0.5) or a full block at y
        if (x, z) in trestle:
            b.set(x, y, z, sl("spruce_slab") if half else deck_block(x, z, 5402))
            if (x + z) % 2 == 0: pile(b, c, x, z, y - 1)
        else:
            if half:
                b.set(x, y - 1, z, "minecraft:packed_mud"); b.set(x, y, z, sl("mud_brick_slab" if hsh(x, 0, z, 5403) < 0.6 else "cobblestone_slab"))
            else: b.set(x, y, z, CLIMB)
        for yy in range(y + 1, y + 5):
            if b.get(x, yy, z) is None: b.set(x, yy, z, "minecraft:air")
        out.append((x, y, z, half))
    # the railing: on the outer cells of the trestle (the drop >= 2), fence posts every 3 with chains between
    cp = rl["cpath"]
    for k, (x, z) in enumerate(cp):
        if (x, z) not in trestle: continue
        a = cp[max(0, k - 1)]; b_ = cp[min(len(cp) - 1, k + 1)]; tx, tz = b_[0] - a[0], b_[1] - a[1]
        for sgn in (1, -1):
            nx, nz = (0, sgn) if abs(tx) >= abs(tz) else (sgn, 0)
            q = (x + nx, z + nz)
            if q not in surf or q not in trestle: continue
            s2 = surf[q]; y = (s2 - 1) // 2 if s2 % 2 else s2 // 2 - 1
            if b.get(q[0], y + 1, q[1]) not in (None, "minecraft:air"): continue
            b.set(q[0], y + 1, q[1], fence("spruce_fence") if k % 3 == 0 else chain("x" if abs(tx) >= abs(tz) else "z"))
    return out

# ---------------------------------------------------------------- lanterns on poles along the main channel
def lanterns(b, c, ft, R, gr):
    """every 20 cells of the main channel, on its left bank side (4 off the line), a pole (fence) up to W+3 and a lantern on it;
    lantern and soul lantern by turns"""
    W = c.W; main = ft["main"]; out = []; n = 0
    for k in range(10, len(main) - 5, 20):
        a = main[max(0, k - 3)]; b_ = main[min(len(main) - 1, k + 3)]; tx, tz = b_[0] - a[0], b_[1] - a[1]
        L = math.hypot(tx, tz) or 1
        for off in (4, 5, 3, 6):
            x, z = int(round(main[k][0] - tz / L * off)), int(round(main[k][1] + tx / L * off))
            if ft["mainm"][R.ix(gr, x, z)] or b.get(x, W + 1, z) is not None: continue
            break
        kind = "lantern" if n % 2 == 0 else "soul_lantern"; n += 1
        for y in range(c.g(x, z) + 1, W + 4): b.set(x, y, z, water_fence(c, x, y, z))
        b.set(x, W + 4, z, lantern(kind))
        out.append((x, W + 4, z, kind))
    return out

# ---------------------------------------------------------------- trees
MLEAF = "minecraft:mangrove_leaves[distance=1,persistent=true,waterlogged=false]"
OLEAF = "minecraft:oak_leaves[distance=1,persistent=true,waterlogged=false]"
def free(b, x, y, z): return b.get(x, y, z) in (None, "minecraft:air")
def leaf_blob(b, cx, cy, cz, rx, ry, salt, leaf, c, moss=0.1, vines=0.12):
    ri = int(math.ceil(rx)); cells = []
    for dx in range(-ri, ri + 1):
        for dz in range(-ri, ri + 1):
            for dy in range(-1, int(math.ceil(ry)) + 1):
                e = (dx * dx + dz * dz) / (rx * rx) + (dy * dy) / (ry * ry if dy > 0 else 1.4)
                if e > 1.0 or (e > 0.65 and hsh(cx + dx, cy + dy, cz + dz, salt) < 0.4): continue
                x, y, z = cx + dx, cy + dy, cz + dz
                if y <= c.g(x, z) + 1: continue
                if free(b, x, y, z): b.set(x, y, z, leaf); cells.append((x, y, z))
    # beards: pale hanging moss and vines under the leaves
    for (x, y, z) in cells:
        if not free(b, x, y - 1, z): continue
        r = hsh(x, y, z, salt + 7)
        if r < moss:
            n = 1 + int(hsh(x, y, z, salt + 8) * 4)
            for k in range(1, n + 1):
                yy = y - k
                if not free(b, x, yy, z) or yy <= max(c.g(x, z), c.W if c.wet(x, z) else -999) + 1: break
                b.set(x, yy, z, "minecraft:pale_hanging_moss[tip=%s]" % ("true" if k == n else "false"))
        elif r < moss + vines:
            # a vine hangs on the side of the leaf block below it (a vine needs a block face: north side of the leaf at z+1)
            n = 1 + int(hsh(x, y, z, salt + 9) * 5)
            for k in range(1, n + 1):
                yy = y - k
                if not free(b, x, yy, z) or yy <= max(c.g(x, z), c.W if c.wet(x, z) else -999) + 1: break
                b.set(x, yy, z, "minecraft:vine[east=false,north=false,south=false,up=true,west=false]" if k == 1 else "minecraft:vine[east=false,north=false,south=false,up=false,west=false]")
    return cells
def mangrove(b, c, x, z, salt):
    """a mangrove on prop roots: the trunk starts at W+2 (or 2 over the ground), 4..6 roots arch out and down into the mud / water"""
    W = c.W; g = c.g(x, z)
    base = max(g, W) + 2 + int(hsh(x, 0, z, salt) * 2)
    h = 5 + int(hsh(x, 1, z, salt) * 4)
    lean = (int(hsh(x, 2, z, salt) * 3) - 1, int(hsh(x, 3, z, salt) * 3) - 1)
    tx, tz = x, z
    for k in range(h):
        if k == h // 2: tx += lean[0]; tz += lean[1]
        b.set(tx, base + k, tz, "minecraft:mangrove_log[axis=y]")
    # prop roots: from the trunk base outward, down to the ground (arched)
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    nr = 4 + int(hsh(x, 4, z, salt) * 3)
    for i in range(nr):
        dx, dz = dirs[(i + int(hsh(x, 5, z, salt) * 8)) % 8]
        L = 2 + int(hsh(x, 6 + i, z, salt) * 2)
        y = base + 1
        for s in range(1, L + 2):
            px, pz = x + dx * min(s, L), z + dz * min(s, L)
            y = y if s == 1 else y - 1
            if s > L:      # down to the ground
                while y > c.g(px, pz): b.set(px, y, pz, "minecraft:mangrove_roots[waterlogged=%s]" % ("true" if c.inw(px, y, pz) else "false")); y -= 1
                break
            if y <= c.g(px, pz): break
            b.set(px, y, pz, "minecraft:mangrove_roots[waterlogged=%s]" % ("true" if c.inw(px, y, pz) else "false"))
    for y in range(c.g(x, z) + 1, base):              # the root knot under the trunk
        b.set(x, y, z, "minecraft:mangrove_roots[waterlogged=%s]" % ("true" if c.inw(x, y, z) else "false"))
    top = base + h
    leaf_blob(b, tx, top, tz, 3.2, 2.0, salt + 11, MLEAF, c, moss=0.12, vines=0.14)
    for i in range(2 + int(hsh(x, 9, z, salt) * 2)):  # side branches
        a = hsh(x, 10 + i, z, salt) * 2 * math.pi; bx, bz = tx + int(round(math.cos(a) * 3)), tz + int(round(math.sin(a) * 3)); by = top - 2 + i
        b.set(tx + int(round(math.cos(a) * 1.5)), by, tz + int(round(math.sin(a) * 1.5)), "minecraft:mangrove_log[axis=%s]" % ("x" if abs(math.cos(a)) > abs(math.sin(a)) else "z"))
        leaf_blob(b, bx, by + 1, bz, 2.4, 1.3, salt + 20 + i, MLEAF, c, moss=0.12, vines=0.14)
def swamp_oak(b, c, x, z, salt):
    """a swamp oak: a short trunk (on the ground or in shallow water), a wide flat crown with vines"""
    W = c.W; g = c.g(x, z)
    h = 4 + int(hsh(x, 0, z, salt) * 3)
    for y in range(g + 1, g + 1 + h): b.set(x, y, z, "minecraft:oak_log[axis=y]")
    top = g + h
    for i in range(4):
        a = (i + hsh(x, 1, z, salt)) * math.pi / 2; L = 2 + int(hsh(x, 2 + i, z, salt) * 2)
        px, pz = x, z
        for s in range(1, L + 1):
            px, pz = x + int(round(math.cos(a) * s)), z + int(round(math.sin(a) * s))
            b.set(px, top - 1 + (s > 1), pz, "minecraft:oak_log[axis=%s]" % ("x" if abs(math.cos(a)) > abs(math.sin(a)) else "z"))
        leaf_blob(b, px, top + 1, pz, 2.6, 1.2, salt + 30 + i, OLEAF, c, moss=0.06, vines=0.25)
    leaf_blob(b, x, top + 1, z, 3.6, 1.4, salt + 40, OLEAF, c, moss=0.06, vines=0.25)

# ---------------------------------------------------------------- the ruins of the village on piles: 2 templates
def ruin_template(kind):
    """{(dx, dy, dz): state} relative to the centre of the floor (dy 0 = floor level), unrotated (door to the south, +z).
    kind 0: a hut 5x5, floor at water level - 1 (flooded), walls 3, roof fallen in; kind 1: a house 7x6 with a porch, floor at W,
    walls 4, a broken gable roof"""
    v = {}
    P = Mix({"mangrove_planks": 50, "spruce_planks": 40, "air": 10}, 5501)
    if kind == 0:
        r = 2
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                v[(dx, 0, dz)] = "minecraft:spruce_planks" if hsh(dx, 0, dz, 5502) < 0.7 else "minecraft:mangrove_planks"
                edge = abs(dx) == r or abs(dz) == r
                for dy in range(1, 4):
                    if edge:
                        if abs(dx) == r and abs(dz) == r: v[(dx, dy, dz)] = "minecraft:stripped_mangrove_log[axis=y]"
                        elif (dx, dz) == (0, r) and dy <= 2: v[(dx, dy, dz)] = "minecraft:air"           # the door
                        else: v[(dx, dy, dz)] = P
                    else: v[(dx, dy, dz)] = "minecraft:air"
        for dx in range(-r - 1, r + 2):                                                    # the roof: slabs, half fallen in
            for dz in range(-r - 1, r + 2):
                if hsh(dx, 4, dz, 5503) < 0.45 or (dx > 0 and dz < 0): continue
                v[(dx, 4, dz)] = "minecraft:spruce_slab[type=bottom,waterlogged=false]"
        v[(1, 1, -1)] = "minecraft:cobweb"; v[(-1, 3, -1)] = "minecraft:cobweb"; v[(1, 3, 1)] = "minecraft:cobweb"
    else:
        rx, rz = 3, 2
        for dx in range(-rx, rx + 1):
            for dz in range(-rz, rz + 4):
                porch = dz > rz
                v[(dx, 0, dz)] = ("minecraft:spruce_planks" if hsh(dx, 0, dz, 5511) < 0.6 else "minecraft:stripped_mangrove_log[axis=x]") if not (porch and hsh(dx, 1, dz, 5512) < 0.3) else "minecraft:air"
                if porch: continue
                edge = abs(dx) == rx or abs(dz) == rz
                for dy in range(1, 5):
                    if edge:
                        if abs(dx) == rx and abs(dz) == rz: v[(dx, dy, dz)] = "minecraft:stripped_mangrove_log[axis=y]"
                        elif dz == rz and dx == 0 and dy <= 2: v[(dx, dy, dz)] = "minecraft:air"             # the door
                        elif dz == rz and abs(dx) == 2 and dy == 2: v[(dx, dy, dz)] = "minecraft:air"         # windows
                        elif dx == -rx and dz == 0 and dy in (2, 3): v[(dx, dy, dz)] = "minecraft:air"        # a breach
                        else: v[(dx, dy, dz)] = P
                    else: v[(dx, dy, dz)] = "minecraft:air"
        for k in range(0, rz + 2):                     # gable roof along x, broken on the east half
            y = 5 + k
            for dx in range(-rx - 1, rx + 2):
                if dx > 1 and hsh(dx, y, k, 5513) < 0.6: continue
                for zz, f in ((-rz - 1 + k, "south"), (rz + 1 - k, "north")):
                    if -rz - 1 + k <= rz + 1 - k:
                        v[(dx, y, zz)] = stairs("spruce_stairs", f) if zz != rz + 1 - k or -rz - 1 + k != zz else sl("spruce_slab")
        for (dx, dz) in ((-rx, rz + 3), (rx, rz + 3)):
            v[(dx, 1, dz)] = fence("spruce_fence")
        v[(2, 4, -1)] = "minecraft:cobweb"; v[(-2, 1, 1)] = "minecraft:cobweb"; v[(-1, 4, 1)] = "minecraft:cobweb"
    return v
def rotate(dx, dz, r):
    for _ in range(r): dx, dz = -dz, dx
    return dx, dz
ROT_FACING = ["north", "east", "south", "west"]
def rot_state(s, r):
    """rotate the facing / axis properties of a state by r quarter turns clockwise"""
    if "[" not in s: return s
    head, props = s.split("[", 1); props = props.rstrip("]")
    out = []
    for kv in props.split(","):
        k, v_ = kv.split("=")
        if k == "facing" and v_ in ROT_FACING: v_ = ROT_FACING[(ROT_FACING.index(v_) + r) % 4]
        if k == "axis" and v_ in ("x", "z") and r % 2: v_ = "z" if v_ == "x" else "x"
        out.append("%s=%s" % (k, v_))
    return head + "[" + ",".join(out) + "]"
def ruin_place(b, c, kind, cx, cz, r, role):
    """a ruin at (cx, cz) turned by r quarter turns; piles under the floor to the bottom; returns its points"""
    W = c.W; tpl = ruin_template(kind); floor = W - 1 if kind == 0 else W
    pts = {}
    cells = set()
    for (dx, dy, dz), s in tpl.items():
        rx, rz = rotate(dx, dz, r); x, y, z = cx + rx, floor + dy, cz + rz
        s = s if isinstance(s, str) else s.at(x, y, z)
        s = rot_state(s, r)
        if s == "minecraft:air" and y <= W and c.wet(x, z): continue          # the flooded inside stays water
        b.set(x, y, z, s)
        if dy == 0: cells.add((x, z))
    for (x, z) in cells:
        if (x + z) % 2 == 0: pile(b, c, x, z, floor - 1)
    # role: the note (lectern with the book), the chest of the ambush, empty
    ix_, iz_ = rotate(0, -1, r); px, pz = cx + ix_, cz + iz_
    if role == "note":
        book = ('{Book:{id:"minecraft:written_book",count:1,components:{"minecraft:written_book_content":{title:{raw:"Записка"},author:"рыбак",'
                'pages:[{raw:"Вода поднимается каждую ночь на палец. Ведьмы говорят, это не вода, это топь дышит. Сегодня ушёл Тим. Сказал, видел в заводи лицо отца. Отец утонул десять лет назад."}]}}},Page:0}')
        b.set(px, floor + 1, pz, "minecraft:lectern[facing=%s,has_book=true,powered=false]" % ROT_FACING[(2 + r) % 4] + book)
        pts["lectern"] = [px, floor + 1, pz]
    if role == "ambush":
        b.set(px, floor + 1, pz, 'minecraft:chest[facing=%s,type=single,waterlogged=false]{LootTable:"last_ember:chests/r1/common"}' % ROT_FACING[(2 + r) % 4])
        pts["chest"] = [px, floor + 1, pz]; pts["chest_facing"] = ROT_FACING[(2 + r) % 4]
    pts.update(x=cx, z=cz, floor=floor, kind=kind, rot=r, role=role)
    return pts
def ruin_template_blocks(kind):
    """the template as absolute blocks with the origin at the min corner (for the .nbt)"""
    tpl = ruin_template(kind); b = B("ruin%d" % kind)
    for (dx, dy, dz), s in tpl.items(): b.set(dx, dy, dz, s if isinstance(s, str) else s.at(dx, dy, dz))
    return b

# ---------------------------------------------------------------- the hut of the three witches
def hut(b, c, R):
    """platform 30x24 on piles (floor FL = W+4); the hall (13x12) round the dead tree with 3 cauldrons, the big table, herbs, the
    enchanting table with 7 bookshelves; three towers with crooked cone roofs: Mother (west), Maiden (north-east), Crone (south-east);
    the pier on the west with stairs, the porch on the east with the stairs from the boardwalk, the raft garden in the south"""
    W = c.W; FL = W + 4; X1, X2, Z1, Z2 = R.HX1, R.HX2, R.HZ1, R.HZ2
    pts = {}
    WALL = Mix({"mangrove_planks": 50, "spruce_planks": 38, "mud_bricks": 12}, 5601)
    FRAME = "minecraft:stripped_dark_oak_log[axis=y]"
    # the platform and its beams and piles
    for x in range(X1, X2 + 1):
        for z in range(Z1, Z2 + 1):
            b.set(x, FL, z, "minecraft:spruce_planks" if hsh(x, 0, z, 5602) < 0.7 else "minecraft:stripped_spruce_log[axis=x]")
            if x % 4 == 0 or z % 4 == 0: b.set(x, FL - 1, z, "minecraft:mangrove_log[axis=%s]" % ("x" if z % 4 == 0 else "z"))
            if x % 4 == 0 and z % 4 == 0 or (x in (X1, X2) and z % 4 == 0) or (z in (Z1, Z2) and x % 4 == 0) or (x in (X1, X2) and z in (Z1, Z2)):
                pile(b, c, x, z, FL - 1)
            for y in range(FL + 1, FL + 30):
                if b.get(x, y, z) is None: b.set(x, y, z, "minecraft:air")
    # railing on the platform edge (spruce fence), open at the stairs and the doors
    def rail(x, z):
        b.set(x, FL + 1, z, fence("spruce_fence"))
    # ---- rooms: (x1, z1, x2, z2, wall height)
    HALL = (-396, 334, -384, 345, 6)
    MOTHER = (-404, 336, -398, 342, 6)
    MAIDEN = (-383, 328, -377, 334, 6)
    CRONE = (-383, 345, -377, 351, 6)
    def room(r, salt):
        x1, z1, x2, z2, hgt = r
        for x in range(x1, x2 + 1):
            for z in range(z1, z2 + 1):
                edge = x in (x1, x2) or z in (z1, z2)
                for y in range(FL + 1, FL + hgt + 1):
                    if not edge: b.set(x, y, z, "minecraft:air"); continue
                    if x in (x1, x2) and z in (z1, z2): b.set(x, y, z, FRAME)
                    elif y <= FL + 2 and hsh(x, y, z, salt) < 0.6: b.set(x, y, z, "minecraft:mud_bricks")
                    else: b.set(x, y, z, WALL.at(x, y, z))
                b.set(x, FL + hgt + 1, z, "minecraft:dark_oak_planks" if edge else "minecraft:spruce_planks")     # ceiling
    for r, s in ((HALL, 5610), (MOTHER, 5611), (MAIDEN, 5612), (CRONE, 5613)): room(r, s)
    def opening(x, z, axis, w=1, h=3):
        for k in range(w):
            for y in range(FL + 1, FL + 1 + h):
                b.set(x + (k if axis == "x" else 0), y, z + (k if axis == "z" else 0), "minecraft:air")
    # doors: the hall east (to the porch), west (to the Mother through the passage), north-east (to the Maiden), south-east (to the Crone)
    opening(-384, 339, "z", 2); opening(-396, 339, "z", 1)
    for x in (-397,):                                  # the passage between the hall and the Mother's tower: floor, walls, roof
        for z in (338, 339, 340):
            for y in range(FL + 1, FL + 5): b.set(x, y, z, "minecraft:air" if z == 339 and y <= FL + 3 else WALL.at(x, y, z))
        b.set(x, FL + 5, 339, "minecraft:dark_oak_slab[type=bottom,waterlogged=false]")
    opening(-398, 339, "z", 1)
    opening(-380, 334, "x", 1)                         # the Maiden's door in her south wall (to the porch)
    opening(-380, 345, "x", 1)                         # the Crone's door in her north wall (to the porch) - the hall's south-east corner is x -384
    # windows (glass panes) in the towers and the hall
    for (x, y, z) in ((-404, FL + 3, 339), (-401, FL + 3, 336), (-401, FL + 3, 342), (-380, FL + 3, 328), (-377, FL + 3, 331), (-377, FL + 3, 348),
                      (-380, FL + 3, 351), (-390, FL + 4, 334), (-393, FL + 4, 345), (-387, FL + 4, 345)):
        b.set(x, y, z, "minecraft:glass_pane")
    # ---- roofs
    # the hall: a steep gable along x with a hole for the tree; dark oak and spruce stairs
    hx1, hz1, hx2, hz2, hh = HALL
    for k in range(0, 8):
        y = FL + hh + 1 + k; zn, zs = hz1 - 1 + k, hz2 + 1 - k
        if zn > zs: break
        for x in range(hx1 - 1, hx2 + 2):
            mat = "dark_oak_stairs" if hsh(x, y, 0, 5620) < 0.6 else "spruce_stairs"
            if zn < zs:
                b.set(x, y, zn, stairs(mat, "south")); b.set(x, y, zs, stairs(mat, "north"))
                for z in range(zn + 1, zs):
                    if k >= 1 and x in (hx1, hx2): b.set(x, y, z, WALL.at(x, y, z))       # gables
            else: b.set(x, y, zn, sl("dark_oak_slab"))
    # towers: crooked cones (the centre drifts with the height), a curl of dark oak fence at the top
    def cone(r, top, drift, salt):
        x1, z1, x2, z2, hgt = r; cx, cz = (x1 + x2) / 2, (z1 + z2) / 2; y0 = FL + hgt + 1; H = top - y0
        R0 = (x2 - x1) / 2 + 1.4
        for k in range(H + 1):
            y = y0 + k; t = k / H; rad = R0 * (1 - t) ** 0.9
            ox, oz = cx + drift[0] * t * t * 3, cz + drift[1] * t * t * 3
            ri = int(math.ceil(rad)) + 1
            for dx in range(-ri, ri + 1):
                for dz in range(-ri, ri + 1):
                    x, z = int(math.floor(ox + dx + 0.5)), int(math.floor(oz + dz + 0.5))
                    d = math.hypot(x - ox, z - oz)
                    if d > rad + 0.5: continue
                    if d > rad - 0.9:
                        vx, vz = x - ox, z - oz
                        f = ("east" if vx < 0 else "west") if abs(vx) >= abs(vz) else ("south" if vz < 0 else "north")
                        b.set(x, y, z, stairs("dark_oak_stairs" if hsh(x, y, z, salt) < 0.65 else "spruce_stairs", f))
                    elif k == 0: b.set(x, y, z, "minecraft:dark_oak_planks")
                    elif free(b, x, y, z): b.set(x, y, z, "minecraft:air")
        tx, tz = int(math.floor(cx + drift[0] * 3 + 0.5)), int(math.floor(cz + drift[1] * 3 + 0.5))
        b.set(tx, top, tz, "minecraft:dark_oak_planks")
        for i in range(1, 5):                           # the curl
            b.set(tx + (1 if i >= 3 else 0) * drift[0], top + i - (1 if i == 4 else 0), tz + (1 if i >= 3 else 0) * drift[1], fence("dark_oak_fence"))
        return (tx, top + 4, tz)
    tips = [cone(MOTHER, W + 24, (-1, 0), 5631), cone(MAIDEN, W + 26, (1, -1), 5632), cone(CRONE, W + 22, (1, 1), 5633)]
    # ---- the dead tree: a 2x2 trunk from the bottom of the water through the hall, bare branches over the roofs, top W+34
    tx1, tz1 = -391, 339
    for (x, z) in ((tx1, tz1), (tx1 + 1, tz1), (tx1, tz1 + 1), (tx1 + 1, tz1 + 1)):
        for y in range(c.g(x, z) + 1, W + 31):
            b.set(x, y, z, "minecraft:dark_oak_wood[axis=y]" if hsh(x, y, z, 5640) < 0.7 else "minecraft:stripped_dark_oak_wood[axis=y]")
    for (x, z) in ((tx1 - 1, tz1), (tx1 + 2, tz1 + 1), (tx1, tz1 - 1), (tx1 + 1, tz1 + 2)):         # mangrove roots at its foot (in the water)
        for y in range(c.g(x, z) + 1, FL):
            b.set(x, y, z, "minecraft:mangrove_roots[waterlogged=%s]" % ("true" if c.inw(x, y, z) else "false"))
    for i, (ang, y0, L, rise) in enumerate(((20, W + 18, 7, 0.6), (140, W + 21, 6, 0.8), (250, W + 24, 6, 0.5), (320, W + 27, 5, 0.9), (80, W + 29, 4, 1.0))):
        a = math.radians(ang); px, pz, py = tx1 + 1.0, tz1 + 1.0, float(y0)
        for k in range(L):
            px += math.cos(a); pz += math.sin(a); py += rise
            b.set(int(math.floor(px)), int(round(py)), int(math.floor(pz)), "minecraft:dark_oak_wood[axis=y]")
    for y in range(W + 31, W + 35): b.set(tx1 + (y - W - 31) // 2, y, tz1, "minecraft:dark_oak_wood[axis=y]")
    # the hole in the hall roof round the trunk
    for x in range(tx1 - 1, tx1 + 3):
        for z in range(tz1 - 1, tz1 + 3):
            for y in range(FL + hh + 1, FL + hh + 9):
                if not (tx1 <= x <= tx1 + 1 and tz1 <= z <= tz1 + 1) and b.get(x, y, z) not in (None,) and "stairs" in str(b.get(x, y, z)): b.set(x, y, z, "minecraft:air")
    # ---- the hall inside: 3 cauldrons in a triangle round the trunk, the big table north, herbs under the ceiling, lanterns
    cauldrons = [(-388, 342), (-393, 341), (-390, 336)]
    for (x, z) in cauldrons[:2]: b.set(x, FL + 1, z, "minecraft:water_cauldron[level=2]")
    b.set(cauldrons[2][0], FL + 1, cauldrons[2][1], "minecraft:cauldron")
    for x in range(-394, -386):                         # the big table: spruce slabs on top of fences? -> stripped spruce wood top
        if -391 <= x <= -390: continue
        b.set(x, FL + 1, 336, "minecraft:stripped_spruce_wood[axis=x]") if x in (-394, -387) else b.set(x, FL + 1, 336, sl("spruce_slab", "top"))
    pts["table"] = [-390, FL + 2, 336]
    b.set(-392, FL + 2, 336, "minecraft:candle[candles=3,lit=true,waterlogged=false]"); b.set(-388, FL + 2, 336, "minecraft:decorated_pot[cracked=false,facing=north,waterlogged=false]")
    for (x, z) in ((-394, 335), (-387, 335)): b.set(x, FL + 1, z, stairs("spruce_stairs", "south"))
    for x in range(hx1 + 1, hx2):                       # herbs: hanging roots and moss under the ceiling, every second cell along two rows
        for z in (336, 343):
            if (x + z) % 2 == 0 and free(b, x, FL + hh, z): b.set(x, FL + hh, z, "minecraft:hanging_roots[waterlogged=false]" if hsh(x, 1, z, 5650) < 0.6 else "minecraft:pale_hanging_moss[tip=true]")
    for (x, z) in ((-394, 338), (-386, 338), (-394, 344), (-386, 344)): b.set(x, FL + hh, z, lantern("lantern", True))
    # the enchanting table and 7 bookshelves (distance 2, air between: HQ, economy.md - the R1 table)
    ex, ez = -393, 343 - 1
    b.set(ex, FL + 1, ez, "minecraft:enchanting_table")
    shelves = [(ex - 2, ez - 2), (ex - 2, ez - 1), (ex - 2, ez), (ex - 2, ez + 1), (ex - 2, ez + 2), (ex - 1, ez + 2), (ex, ez + 2)]
    for (x, z) in shelves: b.set(x, FL + 1, z, "minecraft:bookshelf")
    pts["enchant"] = [ex, FL + 1, ez]; pts["shelves"] = [[x, FL + 1, z] for x, z in shelves]
    # ---- the Mother: cauldrons, brewing stands, pots, candles; her cauldron (the talk) by the west wall
    mx = (-402, 339)
    b.set(-403, FL + 1, 339, "minecraft:water_cauldron[level=3]"); pts["mother_item"] = [-403, FL + 1, 339]
    b.set(-403, FL + 1, 337, "minecraft:brewing_stand[has_bottle_0=true,has_bottle_1=false,has_bottle_2=true]")
    b.set(-403, FL + 1, 341, "minecraft:brewing_stand[has_bottle_0=false,has_bottle_1=true,has_bottle_2=false]")
    for (x, z) in ((-399, 337), (-399, 341), (-401, 341)): b.set(x, FL + 1, z, "minecraft:decorated_pot[cracked=%s,facing=east,waterlogged=false]" % ("true" if x == -401 else "false"))
    b.set(-401, FL + 1, 337, "minecraft:cauldron")
    b.set(-401, FL + 6, 339, lantern("lantern", True))
    pts["mother"] = [-401, FL + 1, 339, -90.0]
    # ---- the Maiden: flowers, azaleas, moss, the mirror on her north wall (glass in a frame of quartz), her door south
    for (x, z, f) in ((-382, 329, "minecraft:potted_azure_bluet"), (-378, 329, "minecraft:potted_oxeye_daisy"), (-382, 333, "minecraft:potted_lily_of_the_valley"),
                      (-378, 333, "minecraft:potted_flowering_azalea_bush")):
        b.set(x, FL + 1, z, f)
    for x in range(-382, -377):
        for z in range(329, 334):
            if free(b, x, FL + 1, z) and hsh(x, 3, z, 5660) < 0.45: b.set(x, FL + 1, z, "minecraft:moss_carpet")
    for (x, z) in ((-381, 329), (-379, 333)): b.set(x, FL + 6, z, "minecraft:hanging_roots[waterlogged=false]")
    for y in (FL + 2, FL + 3, FL + 4):                   # the mirror: 1 wide, 3 high, glass in a quartz frame, in the north wall (z 328)
        b.set(-380, y, 328, "minecraft:glass" if y < FL + 4 else "minecraft:quartz_block")
    b.set(-381, FL + 2, 328, "minecraft:quartz_pillar[axis=y]"); b.set(-379, FL + 2, 328, "minecraft:quartz_pillar[axis=y]")
    b.set(-381, FL + 3, 328, "minecraft:quartz_pillar[axis=y]"); b.set(-379, FL + 3, 328, "minecraft:quartz_pillar[axis=y]")
    pts["maiden_item"] = [-380, FL + 2, 329]
    b.set(-380, FL + 6, 331, lantern("soul_lantern", True))
    pts["maiden"] = [-380, FL + 1, 331, 0.0]
    # ---- the Crone: bones, skulls, two cages on chains from the ceiling, her cage (the talk) in the south-east
    for (x, z) in ((-382, 350), (-378, 350), (-382, 346)): b.set(x, FL + 1, z, "minecraft:bone_block[axis=y]")
    for (x, z, rr) in ((-382, 350, 3), (-378, 346, 12), (-381, 346, 6), (-378, 350, 10)):
        b.set(x, FL + 2 if (x, z) in ((-382, 350),) else FL + 1, z, "minecraft:skeleton_skull[rotation=%d,powered=false]" % rr)
    for (x, z) in ((-378, 349), (-382, 347)):            # cages: iron bars 1x1x2 under a chain
        b.set(x, FL + 6, z, chain("y")); b.set(x, FL + 5, z, chain("y")); b.set(x, FL + 4, z, "minecraft:iron_bars"); b.set(x, FL + 3, z, "minecraft:iron_bars")
    pts["crone_item"] = [-378, FL + 3, 349]
    b.set(-380, FL + 6, 348, lantern("lantern", True))
    pts["crone"] = [-380, FL + 1, 348, 180.0]
    # ---- the east porch: lanterns on posts, the stairs down to the boardwalk (east, x -374..-376 at z 339..340)
    for z in (339, 340):
        b.set(X2 + 2, W + 2, z, stairs("spruce_stairs", "west")); b.set(X2 + 1, W + 3, z, stairs("spruce_stairs", "west")); b.set(X2, FL, z, stairs("spruce_stairs", "west"))
        b.set(X2 + 2, W + 1, z, "minecraft:spruce_planks"); b.set(X2 + 1, W + 2, z, "minecraft:spruce_planks"); b.set(X2 + 1, W + 1, z, "minecraft:spruce_planks")
        for y in range(W + 3, W + 7):
            if b.get(X2 + 2, y, z) is None: b.set(X2 + 2, y, z, "minecraft:air")
        for y in range(W + 4, W + 7):
            if b.get(X2 + 1, y, z) is None: b.set(X2 + 1, y, z, "minecraft:air")
        pile(b, c, X2 + 2, z, W); pile(b, c, X2 + 1, z, W)
    # ---- the west pier for 2 boats (the end of the main channel), stairs up to the platform
    pz1, pz2 = 345, 347
    for x in range(X1 - 7, X1):
        for z in range(pz1, pz2 + 1):
            if x >= X1 - 3:
                continue
            b.set(x, W + 1, z, deck_block(x, z, 5670))
            for y in range(W + 2, W + 6):
                if b.get(x, y, z) is None: b.set(x, y, z, "minecraft:air")
            if (x + z) % 2 == 0: pile(b, c, x, z, W)
    for z in range(pz1, pz2 + 1):
        b.set(X1 - 3, W + 2, z, stairs("spruce_stairs", "east")); b.set(X1 - 2, W + 3, z, stairs("spruce_stairs", "east")); b.set(X1 - 1, FL, z, stairs("spruce_stairs", "east"))
        b.set(X1 - 3, W + 1, z, "minecraft:spruce_planks"); b.set(X1 - 2, W + 2, z, "minecraft:spruce_planks"); b.set(X1 - 2, W + 1, z, "minecraft:spruce_planks")
        b.set(X1 - 1, FL - 1, z, "minecraft:spruce_planks")
        for y in range(W + 3, W + 7):
            if b.get(X1 - 3, y, z) is None: b.set(X1 - 3, y, z, "minecraft:air")
        for y in range(W + 4, W + 8):
            if b.get(X1 - 2, y, z) is None: b.set(X1 - 2, y, z, "minecraft:air")
        for y in range(FL + 1, FL + 4):
            if b.get(X1 - 1, y, z) is None: b.set(X1 - 1, y, z, "minecraft:air")
        pile(b, c, X1 - 3, z, W); pile(b, c, X1 - 2, z, W)
    for (x, z) in ((X1 - 7, pz1), (X1 - 7, pz2)):
        for y in range(c.g(x, z) + 1, W + 3): b.set(x, y, z, water_fence(c, x, y, z))
        b.set(x, W + 3, z, lantern("lantern"))
    pts["pier_hut"] = [X1 - 5, W + 1, (pz1 + pz2) // 2]
    # boats of the hut: north and south of the pier, in the water
    pts["boats_hut"] = [[X1 - 6, W, pz1 - 2], [X1 - 6, W, pz2 + 2]]
    # ---- the raft garden (south, in the zone): a raft at W of stripped spruce, podzol beds, pumpkins and mushrooms
    for x in range(-398, -390):
        for z in range(354, 358):
            edge = x in (-398, -391) or z in (354, 357)
            b.set(x, W, z, "minecraft:stripped_spruce_log[axis=x]" if edge else "minecraft:podzol[snowy=false]")
            if not edge:
                r = hsh(x, 4, z, 5680)
                b.set(x, W + 1, z, "minecraft:pumpkin" if r < 0.3 else ("minecraft:brown_mushroom" if r < 0.55 else ("minecraft:red_mushroom" if r < 0.7 else "minecraft:air")))
            elif (x + z) % 3 == 0: b.set(x, W + 1, z, fence("spruce_fence"))
    # light on the platform: lanterns on fence posts at the corners and by the doors
    for (x, z) in ((X1, Z1), (X2, Z1), (X1, Z2), (X2, Z2), (-376, 337), (-376, 342)):
        b.set(x, FL + 1, z, fence("spruce_fence")); b.set(x, FL + 2, z, lantern("lantern"))
    for x in range(X1, X2 + 1):
        for z in (Z1, Z2):
            if free(b, x, FL + 1, z) and x % 2 == 0: rail(x, z)
    for z in range(Z1, Z2 + 1):
        for x in (X1, X2):
            if free(b, x, FL + 1, z) and z % 2 == 0 and not (pz1 - 1 <= z <= pz2 + 1) and not (338 <= z <= 341): rail(x, z)
    pts["tips"] = tips; pts["floor"] = FL; pts["cauldrons"] = [[x, FL + 1, z] for x, z in cauldrons]
    pts["rooms"] = dict(hall=HALL, mother=MOTHER, maiden=MAIDEN, crone=CRONE)
    pts["porch"] = [X2 + 2, W + 1, 339]
    return pts
