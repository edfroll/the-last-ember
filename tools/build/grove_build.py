"""T-030: the models of the Mushroom Grove (Р1): the mushroom house of the Advisor, the giant mushrooms (4 shapes in rotations), the
poplars with shelf mushrooms, the 6 thick poplars with faces (closed / open), the small glowing mushrooms, the path, the garden.
All coordinates are absolute; the models write into a lib.B. Read by tools/build/r1_grove.py."""
import math
from lib import B, Mix, h as hsh, stairs, slab, lantern

LEAVES = Mix({"yellow_poplar_leaves[persistent=true]": 45, "orange_poplar_leaves[persistent=true]": 35, "red_poplar_leaves[persistent=true]": 20}, 3001)
GROUND = Mix({"podzol": 40, "moss_block": 25, "coarse_dirt": 15, "mycelium": 20}, 3002)
STEEP = Mix({"coarse_dirt": 30, "stone": 25, "mossy_cobblestone": 20, "tuff": 10, "podzol": 15}, 3003)
PATH = Mix({"mossy_cobblestone": 60, "cobblestone": 40}, 3004)
WALL = Mix({"mossy_cobblestone": 65, "cobblestone": 35}, 3005)
STEM = "minecraft:mushroom_stem"
def RED(down=True): return "minecraft:red_mushroom_block" + ("" if down else "[down=false]")
def BROWN(down=True): return "minecraft:brown_mushroom_block" + ("" if down else "[down=false]")
LOG = "minecraft:poplar_log[axis=y]"
ROT = ["north", "east", "south", "west"]
DXZ = {"north": (0, -1), "east": (1, 0), "south": (0, 1), "west": (-1, 0)}
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}

# ---------------------------------------------------------------- the house (HQ T-030: stem 9 x 9, height 26, cap 21 across)
def octagon(dx, dz, r=4): return abs(dx) <= r and abs(dz) <= r and not (abs(dx) == r and abs(dz) == r)

def house(b, cx, cz, L, meta):
    """ground L (floor of oak planks at L); 1st floor feet L+1..L+7, ceiling L+8 (spruce), the cap's underside L+8 round the stem,
    2nd floor (oak planks) L+9 over the whole inside of the cap (r <= 8.6), feet L+10; the cap: skirt r 8.6..10.5 L+8..L+12, dome to L+26.
    The door east (cx+4, cz); round windows N, S, W; the stair along the south and the west walls; the chimney out of the cap's west side"""
    F1 = L + 1; C1 = L + 8; F2 = L + 9; TOP = L + 26
    # the stem: one block of mushroom stem round the 7 x 7 room (HQ: inside spruce planks would make it 5 x 5 again: the planks are the
    # ribs on the inner corners, the ceiling, the frames and the floor 2 joists)
    for dx in range(-4, 5):
        for dz in range(-4, 5):
            if not octagon(dx, dz): continue
            x, z = cx + dx, cz + dz
            b.set(x, L, z, "minecraft:oak_planks" if abs(dx) <= 3 and abs(dz) <= 3 else STEM)
            for y in range(L - 3, L): b.set(x, y, z, STEM if not (abs(dx) <= 3 and abs(dz) <= 3) else "minecraft:dirt")
            shell = abs(dx) == 4 or abs(dz) == 4 or (abs(dx) == 3 and abs(dz) == 4) or (abs(dz) == 3 and abs(dx) == 4)
            for y in range(F1, C1 + 1):
                if shell: b.set(x, y, z, STEM)
                elif y == C1: b.set(x, y, z, "minecraft:spruce_planks")
                else: b.set(x, y, z, "minecraft:air")
    for (dx, dz) in ((-3, 3), (3, -3), (-3, -3)):               # plank ribs in the inner corners (the SE one is the way onto the stair)
        for y in range(F1, C1): b.set(cx + dx, y, cz + dz, "minecraft:spruce_planks")
    # the cap: underside layer C1 (pores + shroomlight) round the stem, the floor of the 2nd storey F2, skirt and dome
    for dx in range(-11, 12):
        for dz in range(-11, 12):
            r = math.hypot(dx, dz); x, z = cx + dx, cz + dz
            if r > 10.6: continue
            if r > 4.6 or not octagon(dx, dz):
                b.set(x, C1, z, "minecraft:shroomlight" if hsh(x, C1, z, 3010) < 0.22 else RED(False))
            if r <= 8.6: b.set(x, F2, z, "minecraft:oak_planks")
            else:
                for y in range(F2, L + 13): b.set(x, y, z, RED())
    for y in range(L + 12, TOP + 1):
        t = (y - (L + 12)) / (TOP - (L + 12))
        ro = 10.5 * math.sqrt(max(0.0, 1 - t ** 1.6)); ri = ro - 1.6
        for dx in range(-11, 12):
            for dz in range(-11, 12):
                r = math.hypot(dx, dz)
                if r <= ro + 0.1 and (r > ri or y >= TOP - 1): b.set(cx + dx, y, cz + dz, RED())
                elif r <= ro + 0.1 and y > F2: b.set(cx + dx, y, cz + dz, "minecraft:air")
    for dx in range(-9, 10):                              # the room under the cap: air above the floor
        for dz in range(-9, 10):
            r = math.hypot(dx, dz)
            if r <= 8.6:
                for y in range(F2 + 1, L + 13): b.set(cx + dx, y, cz + dz, "minecraft:air")
    # the door (east): spruce door in a round frame of spruce stairs
    dxx = cx + 4
    b.set(dxx, F1, cz, "minecraft:spruce_door[facing=west,half=lower,hinge=left,open=false]")
    b.set(dxx, F1 + 1, cz, "minecraft:spruce_door[facing=west,half=upper,hinge=left,open=false]")
    for s in (-1, 1):
        b.set(dxx, F1, cz + s, "minecraft:spruce_planks"); b.set(dxx, F1 + 1, cz + s, "minecraft:spruce_planks")
        b.set(dxx, F1 + 2, cz + s, stairs("spruce_stairs", "north" if s > 0 else "south", "top"))
    b.set(dxx, F1 + 2, cz, slab("spruce_slab", "top"))
    b.set(dxx + 1, F1 - 1, cz, "minecraft:mossy_cobblestone")
    # round windows: 3 x 3 in the wall plane, stairs at the corners, panes in the cross
    def window(wx, wz, along, y0, face):
        for a in (-1, 0, 1):
            for c in (-1, 0, 1):
                x = wx + (a if along == "x" else 0); z = wz + (a if along == "z" else 0); y = y0 + c
                if a and c: b.set(x, y, z, stairs("spruce_stairs", face, "top" if c > 0 else "bottom"))
                else: b.set(x, y, z, "minecraft:glass_pane")
    window(cx, cz - 4, "x", F1 + 3, "south"); window(cx, cz + 4, "x", F1 + 3, "north"); window(cx - 4, cz, "z", F1 + 3, "east")
    # the stair: south row west (5 steps), landing in the SW corner, west row north (4 steps) to the 2nd storey
    st = []
    for k, dx in enumerate((2, 1, 0, -1, -2)): st.append((cx + dx, F1 + k, cz + 3, "west"))
    for k, dz in enumerate((2, 1, 0, -1)): st.append((cx - 3, F1 + 5 + k, cz + dz, "north"))
    for (x, y, z, f) in st: b.set(x, y, z, stairs("spruce_stairs", f))
    b.set(cx - 3, F1 + 4, cz + 3, "minecraft:spruce_planks")                     # the landing (flush with the 5th step)
    for (x, y, z, f) in st:
        for yy in range(y + 1, y + 4):
            if yy in (C1, F2) or yy < C1: b.set(x, yy, z, "minecraft:air")
    b.set(cx - 3, F1 + 5, cz + 3, "minecraft:air"); b.set(cx - 3, F1 + 6, cz + 3, "minecraft:air"); b.set(cx - 3, C1, cz + 3, "minecraft:air")   # head room over the landing
    # the balustrade on the room side of the flights (posts stepping with the stairs: the fall to the study floor is up to 5)
    for dx, y in ((1, F1 + 2), (0, F1 + 3), (-1, F1 + 4), (-2, F1 + 5), (-2, F1 + 6)): b.set(cx + dx, y, cz + 2, "minecraft:spruce_fence")
    for (x, z) in ((cx - 2, cz + 1), (cx - 2, cz), (cx - 2, cz + 2), (cx - 2, cz - 1)):
        b.set(x, F2 + 1, z, "minecraft:spruce_fence")                              # the rail round the stair hole
    for dz in (3, 2):
        b.set(cx - 2, F2 + 1, cz + dz, "minecraft:spruce_fence")
    # under the west flight: bookshelves where the steps leave room
    for dz, top in ((2, F1 + 4), (1, F1 + 5), (0, F1 + 6)):
        for y in range(F1, min(top, F1 + 3)): b.set(cx - 3, y, cz + dz, "minecraft:bookshelf")
    meta["stair"] = [list(s[:3]) for s in st]
    # ---- the study (1st floor)
    # the hearth: campfire in a stone fireplace on the north wall, the hood up to the ceiling
    fx, fz = cx, cz - 3
    b.set(fx, F1, fz, "minecraft:campfire[facing=south,lit=true,signal_fire=false,waterlogged=false]")
    for s in (-1, 1):
        b.set(fx + s, F1, fz, "minecraft:stone_bricks"); b.set(fx + s, F1 + 1, fz, "minecraft:stone_bricks")
        b.set(fx + s, F1 + 2, fz, stairs("stone_brick_stairs", "south", "top"))
    b.set(fx, F1 + 2, fz, "minecraft:mossy_stone_bricks")
    for y in range(F1 + 3, C1): b.set(fx, y, fz, "minecraft:bricks")
    b.set(fx, F1 + 1, fz, "minecraft:air")
    # the armchair facing the fire (seat = stairs with the back south), armrests (top slabs)
    ax, az = cx, cz - 1
    b.set(ax, F1, az, stairs("spruce_stairs", "south")); b.set(ax - 1, F1, az, slab("spruce_slab", "top")); b.set(ax + 1, F1, az, slab("spruce_slab", "top"))
    meta["chair"] = [ax, F1, az]; meta["armrest"] = [ax + 1, F1, az]; meta["hearth"] = [fx, F1, fz]
    # shelves on the north wall: bookshelves and the two chiseled ones (books in some slots)
    for dx in (-3, -2, 2, 3):
        for y in range(F1, F1 + 3): b.set(cx + dx, y, cz - 3, "minecraft:bookshelf")
    b.set(cx - 2, F1 + 1, cz - 3, "minecraft:chiseled_bookshelf[facing=south,slot_0_occupied=true,slot_1_occupied=true,slot_2_occupied=false,slot_3_occupied=true,slot_4_occupied=false,slot_5_occupied=true]{Items:[{Slot:0b,id:\"minecraft:book\",count:1},{Slot:1b,id:\"minecraft:book\",count:1},{Slot:3b,id:\"minecraft:writable_book\",count:1},{Slot:5b,id:\"minecraft:enchanted_book\",count:1}]}")
    b.set(cx + 2, F1 + 1, cz - 3, "minecraft:chiseled_bookshelf[facing=south,slot_0_occupied=false,slot_1_occupied=true,slot_2_occupied=true,slot_3_occupied=true,slot_4_occupied=true,slot_5_occupied=false]{Items:[{Slot:1b,id:\"minecraft:book\",count:1},{Slot:2b,id:\"minecraft:book\",count:1},{Slot:3b,id:\"minecraft:book\",count:1},{Slot:4b,id:\"minecraft:writable_book\",count:1}]}")
    # the jars: pots on the shelves and the floor (8..10 with the 2nd storey's)
    pots = []
    def pot(x, y, z, kind):
        if kind == "deco": b.set(x, y, z, "minecraft:decorated_pot[facing=south,cracked=false,waterlogged=false]{sherds:[\"minecraft:brick\",\"minecraft:brick\",\"minecraft:brick\",\"minecraft:brick\"]}")
        else: b.set(x, y, z, "minecraft:" + kind)
        pots.append([x, y, z])
    pot(cx - 3, F1 + 3, cz - 3, "potted_red_mushroom"); pot(cx - 2, F1 + 3, cz - 3, "potted_brown_mushroom")
    pot(cx + 3, F1 + 3, cz - 3, "potted_fern"); pot(cx + 2, F1 + 3, cz - 3, "potted_red_mushroom")
    pot(cx - 3, F1, cz - 2, "deco"); pot(cx - 3, F1, cz - 1, "deco")
    # the table with the maps and the open books (frames and displays: datapack), the crystal ball, the lectern
    for dz in (-2, -1): b.set(cx + 2, F1, cz + dz, slab("spruce_slab", "top"))
    meta["table"] = [[cx + 2, F1, cz - 2], [cx + 2, F1, cz - 1]]
    b.set(cx - 2, F1, cz - 2, "minecraft:amethyst_block"); b.set(cx - 2, F1 + 1, cz - 2, "minecraft:tinted_glass")
    import grove_dp
    b.set(cx - 2, F1, cz, "minecraft:lectern[facing=east,has_book=true,powered=false]" + grove_dp.book_nbt())
    meta["lectern"] = [cx - 2, F1, cz]; meta["ball"] = [cx - 2, F1 + 1, cz - 2]
    b.set(cx + 3, F1 + 5, cz + 3, lantern(True)); b.set(cx - 1, C1 - 1, cz - 2, lantern(True))
    # ---- the 2nd storey: bedroom and observatory under the cap
    b.set(cx - 6, F2 + 1, cz - 1, "minecraft:red_bed[facing=west,part=head,occupied=false]")
    b.set(cx - 5, F2 + 1, cz - 1, "minecraft:red_bed[facing=west,part=foot,occupied=false]")
    b.set(cx - 6, F2 + 1, cz - 2, "minecraft:spruce_planks"); pot(cx - 6, F2 + 2, cz - 2, "potted_brown_mushroom")
    pot(cx + 1, F2 + 1, cz - 7, "deco"); pot(cx - 1, F2 + 1, cz + 7, "potted_red_mushroom")
    b.set(cx - 6, F2 + 1, cz + 2, "minecraft:spruce_planks"); b.set(cx - 6, F2 + 2, cz + 2, lantern())
    # star maps: wall banners on the skirt's inner face (dark blue / black, white stars)
    stars = [("north", cx - 3, cz + 8, "blue", ["minecraft:flower", "minecraft:small_stripes"]), ("south", cx + 2, cz - 8, "black", ["minecraft:globe"]),
             ("north", cx + 3, cz + 8, "black", ["minecraft:flower", "minecraft:curly_border"]), ("east", cx - 8, cz + 3, "blue", ["minecraft:globe", "minecraft:border"])]
    for (f, x, z, col, pats) in stars:
        p = ",".join('{pattern:"%s",color:"white"}' % q for q in pats)
        b.set(x, F2 + 3, z, "minecraft:%s_wall_banner[facing=%s]{patterns:[%s]}" % (col, f, p))
        bx, bz = DXZ[OPP[f]]; b.set(x + bx, F2 + 3, z + bz, RED())
    # the spyglass window east in the skirt: round, the spyglass itself is an item display (datapack)
    wx = cx + 9
    for x in (wx, wx + 1):
        for a in (-1, 0, 1):
            for c in (-1, 0, 1):
                y = F2 + 3 + c; z = cz + a
                if a and c: b.set(x, y, z, stairs("spruce_stairs", "west", "top" if c > 0 else "bottom") if x == wx else RED())
                else: b.set(x, y, z, "minecraft:glass_pane" if x == wx + 1 else "minecraft:air")
    b.set(wx - 1, F2 + 1, cz, "minecraft:spruce_fence"); b.set(wx - 1, F2 + 2, cz, "minecraft:spruce_trapdoor[facing=east,half=bottom,open=false]")
    meta["spyglass"] = [wx - 1, F2 + 2, cz]; meta["night"] = [wx - 3, F2 + 1, cz]; meta["day"] = [ax, F1, az]
    for (x, y, z) in ((cx + 5, F2 + 4, cz + 5), (cx - 5, F2 + 4, cz - 5), (cx + 5, F2 + 4, cz - 5)): b.set(x, y + 2, z, "minecraft:iron_chain[axis=y]"); b.set(x, y + 1, z, lantern(True))
    # the chimney: out of the cap's west side, up past the dome; the signal campfire on hay at its mouth, walled in
    chx, chz = cx - 9, cz + 3
    for y in range(L + 13, L + 29):
        for (a, c) in ((0, 0), (1, 0), (0, 1), (1, 1)):
            x, z = chx + a, chz + c
            if y >= L + 27 and (a, c) != (0, 0): b.set(x, y, z, "minecraft:bricks"); continue
            if (a, c) == (0, 0) and y == L + 27: b.set(x, y, z, "minecraft:hay_block"); continue
            if (a, c) == (0, 0) and y == L + 28: b.set(x, y, z, "minecraft:campfire[facing=north,lit=true,signal_fire=true,waterlogged=false]"); continue
            b.set(x, y, z, "minecraft:bricks" if hsh(x, y, z, 3011) < 0.75 else "minecraft:mud_bricks")
    for (a, c) in ((-1, 0), (0, -1), (-1, -1), (2, 0), (0, 2), (2, 1), (1, 2), (-1, 1), (1, -1), (2, 2), (-1, 2), (2, -1)):
        b.set(chx + a, L + 28, chz + c, "minecraft:mud_brick_wall")
    meta["chimney"] = [chx, L + 28, chz]
    meta["pots"] = pots
    meta["floors"] = {"f1": F1, "f2": F2 + 1}
    meta["door"] = [dxx, F1, cz]
    return meta

# ---------------------------------------------------------------- the giant mushrooms (4 shapes) and the small glowing ones
def giant(b, x, z, kind, rot, ground_lo, ground_at, hh, cr):
    """stem from the lowest ground under it (no hanging mushrooms on the slope) to the cap; the cap leans one block toward `rot`"""
    g0 = ground_at(x, z); lo = ground_lo
    gmax = max(ground_at(x + a, z + c) for a in range(-cr - 2, cr + 3) for c in range(-cr - 2, cr + 3) if a * a + c * c <= (cr + 1.5) ** 2)
    hh = max(hh, gmax + 4 - g0)                 # the cap clears the slope under it (never into the hillside)
    thick = 2 if cr >= 5 else 1                 # the wide caps on a stem of 5 (a plus), the small one on 1
    cells = [(a, c) for a in range(-thick + 1, thick) for c in range(-thick + 1, thick)] if thick == 2 else [(0, 0)]
    if thick == 2: cells = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)]
    top = g0 + hh
    ox, oz = DXZ[ROT[rot]]
    for (a, c) in cells:
        for y in range(lo - 2, top):
            lean = 1 if y > g0 + hh * 0.6 else 0
            b.set(x + a + ox * lean, y, z + c + oz * lean, STEM)
    cx, cz = x + ox, z + oz
    red = kind.startswith("red")
    capb = RED if red else BROWN
    under = []
    if kind == "red_dome" or kind == "red_bell":
        H = cr - 1 if kind == "red_dome" else cr
        for k in range(H + 1):
            y = top + k
            ro = cr * math.sqrt(max(0.0, 1 - (k / (H + 0.6)) ** 2)); ri = ro - 1.5
            for a in range(-cr - 1, cr + 2):
                for c in range(-cr - 1, cr + 2):
                    r = math.hypot(a, c)
                    if r <= ro + 0.2 and (r > ri or k == H): b.set(cx + a, y, cz + c, capb())
        for a in range(-cr - 1, cr + 2):           # the skirt (bell: 2 down) and the gills underneath
            for c in range(-cr - 1, cr + 2):
                r = math.hypot(a, c)
                if cr - 0.8 < r <= cr + 0.2:
                    for y in range(top - (2 if kind == "red_bell" else 1), top): b.set(cx + a, y, cz + c, capb())
                if r <= cr - 0.8: under.append((cx + a, top - 1, cz + c))
    else:
        for a in range(-cr - 1, cr + 2):
            for c in range(-cr - 1, cr + 2):
                r = math.hypot(a, c)
                if r <= cr + 0.2: b.set(cx + a, top, cz + c, capb())
                if r <= cr - 2.2: b.set(cx + a, top + 1, cz + c, capb())
                if cr - 0.8 < r <= cr + 0.2 and kind == "brown_flat": b.set(cx + a, top - 1, cz + c, capb())
                if r <= cr - 0.8: under.append((cx + a, top - 1, cz + c))
    for (ux, uy, uz) in under:
        if b.get(ux, uy, uz) == STEM: continue
        if hsh(ux, uy, uz, 3012) < 0.28: b.set(ux, uy, uz, "minecraft:shroomlight")
        elif hsh(ux, uy, uz, 3013) < 0.5: b.set(ux, uy, uz, capb(False))
    for (a, c) in ((2, 1), (-1, 2), (-2, -1), (1, -2)):        # small mushrooms at the roots
        if hsh(x + a, 7, z + c, 3014) < 0.7:
            gy = ground_at(x + a, z + c)
            b.set(x + a, gy + 1, z + c, "minecraft:red_mushroom" if hsh(x + a, 8, z + c, 3015) < 0.5 else "minecraft:brown_mushroom")
    return dict(x=x, z=z, kind=kind, top=top + (cr if red else 1), lo=lo, cap=[cx, top, cz, cr])

def glow_mushroom(b, x, gy, z, ground=None):
    """a small glowing mushroom (card Р5): stem 1, shroomlight (open on its four sides), brown cap over it (a plus of 5; a cap cell over
    higher ground is left out: never into the ground)"""
    b.set(x, gy + 1, z, STEM); b.set(x, gy + 2, z, "minecraft:shroomlight")
    for (a, c) in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        if ground is None or ground(x + a, z + c) < gy + 3: b.set(x + a, gy + 3, z + c, BROWN())
    return (x, gy + 2, z)

# ---------------------------------------------------------------- the poplars and the faces
def poplar(b, x, gy, z, hh, salt, lo=None):
    """a columnar poplar: trunk 1 x 1 from the lowest ground under it, crown from 1/3 of the height to hh + 2, widest at 0.55;
    2..4 shelf mushrooms up the trunk in a ladder (facing away from the trunk)"""
    lo = gy if lo is None else lo
    for y in range(lo - 1, gy + hh): b.set(x, y, z, LOG)
    y0 = gy + int(hh * 0.33); y1 = gy + hh + 2; mid = gy + hh * 0.58
    for y in range(y0, y1 + 1):
        t = (y - mid) / ((y1 - y0) / 2 + 0.5)
        rr = 2.3 * math.sqrt(max(0.0, 1 - t * t)) + 0.3
        for a in range(-3, 4):
            for c in range(-3, 4):
                if (a or c) and math.hypot(a, c) <= rr and hsh(x + a, y, z + c, salt) < 0.92: b.set(x + a, y, z + c, LEAVES)
        if y >= gy + hh: b.set(x, y, z, LEAVES)
    n = 2 + int(hsh(x, 1, z, salt + 1) * 3); f0 = int(hsh(x, 2, z, salt + 2) * 4)
    for k in range(n):
        f = ROT[(f0 + k) % 4]; dx, dz = DXZ[f]; y = gy + 2 + k
        if b.get(x + dx, y, z + dz) is None: b.set(x + dx, y, z + dz, "minecraft:shelf_mushroom[age=1,facing=%s]" % f)
    return dict(x=x, z=z, h=hh)

def thick_poplar(b, x, gy, z, hh, lo, salt):
    """a thick poplar: trunk 3 x 3 (logs standing, axis y) from the lowest ground, crown 3 wider"""
    for a in (-1, 0, 1):
        for c in (-1, 0, 1):
            for y in range(lo - 1, gy + hh): b.set(x + a, y, z + c, LOG)
    y0 = gy + int(hh * 0.3); y1 = gy + hh + 3; mid = gy + hh * 0.6
    for y in range(y0, y1 + 1):
        t = (y - mid) / ((y1 - y0) / 2 + 0.5)
        rr = 3.6 * math.sqrt(max(0.0, 1 - t * t)) + 0.6
        for a in range(-5, 6):
            for c in range(-5, 6):
                if max(abs(a), abs(c)) <= 1 and y < gy + hh: continue
                if math.hypot(a, c) <= rr + 1.2 and hsh(x + a, y, z + c, salt) < 0.9: b.set(x + a, y, z + c, LEAVES)
    n = 3; f0 = int(hsh(x, 2, z, salt + 2) * 4)
    for k in range(n):
        f = ROT[(f0 + k) % 4]; dx, dz = DXZ[f]; y = gy + 3 + k * 2
        sx, sz = x + dx * 2 + (dz != 0) * (k - 1), z + dz * 2 + (dx != 0) * (k - 1)
        if b.get(sx, y, sz) is None: b.set(sx, y, sz, "minecraft:shelf_mushroom[age=1,facing=%s]" % f)

def face_cells(x, gy, z, side, state):
    """the face on one side of a thick poplar (HQ T-030: quieter than T-025): eyes = the two outer cells of the face side at gy+5,
    closed: a lid of stripped poplar (the bark taken off) with a dark oak trapdoor fold over its lower half, open: verdant froglight; the mouth fold at gy+3 (a dark oak
    trapdoor in front of the middle cell). Returns {(x, y, z): state} for the trunk plane and the cells in front of it (the template)"""
    dx, dz = DXZ[side]; px, pz = (-dz, dx)            # along the face
    out = {}
    fx, fz = x + dx, z + dz                           # the middle cell of the face side (trunk)
    for k in (-1, 0, 1):
        for y in range(gy + 2, gy + 7):
            out[(fx + px * k, y, fz + pz * k)] = LOG
            out[(fx + px * k + dx, y, fz + pz * k + dz)] = "minecraft:air"
    for k in (-1, 1):
        ex, ez = fx + px * k, fz + pz * k; ey = gy + 5
        if state == "closed":           # the bark itself, a thin dark fold of the lid in front (seen only when looked for)
            out[(ex, ey, ez)] = "minecraft:stripped_poplar_log[axis=y]"
            out[(ex + dx, ey, ez + dz)] = "minecraft:dark_oak_trapdoor[facing=%s,half=bottom,open=false]" % side
        else:
            out[(ex, ey, ez)] = "minecraft:verdant_froglight[axis=y]"
            out[(ex + dx, ey + 1, ez + dz)] = "minecraft:dark_oak_trapdoor[facing=%s,half=bottom,open=false]" % side
    out[(fx + dx, gy + 3, fz + dz)] = "minecraft:dark_oak_trapdoor[facing=%s,half=top,open=false]" % side
    out[(fx, gy + 4, fz)] = LOG
    return out
