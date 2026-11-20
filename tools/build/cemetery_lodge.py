"""T-027: the Keeper's Lodge (card «Сторожка смотрителя · Р1»): the house 11 x 13 with the mansard and two mushroom chimneys, the shed
7 x 5 with the empty holder of the shovel, the garden, the yard with the keeper's lantern at the wicket, the bell by the door, the
kennel, the stream (spring, cascade, pool, the crack), the footbridge to the road, the road down to the pad of bonfire 2.
For tools/build/r1_cemetery.py: build(b, c, R, lr) -> points."""
from lib import Mix, h as hsh
from cemetery_build import st, stairs, slab, lantern, chain, sign_nbt, book_nbt, clear

WALL = Mix({"cobblestone": 35, "mossy_cobblestone": 25, "stone": 20, "tuff": 10, "andesite": 10}, 7201)
YARD = Mix({"coarse_dirt": 45, "podzol": 30, "gravel": 25}, 7202)
RET = Mix({"mossy_cobblestone": 70, "cobblestone": 30}, 7203)
BOOK = ["Книга учёта. Кладбище у Брода. Сорок лет, четыреста сорок рыцарей. Кто стоял до конца — лёг с оружием. Кто ушёл, сдался или предал — лёг пустым. Так велит Устав.",
        "Магистр Ордена Ясеня лёг в большой склеп. Ключ от склепа ушёл в землю с его оруженосцем. Так он сам велел. Теперь встаёт сам.",
        "Две могилы у восточных курганов я не досыпал: земля там уходит вниз. Свечи у них погасли, я не зажигаю. Обходите.",
        "Ночью в трубу видно, кто лежит с оружием: над ними горят огоньки. Остальные не горят. Им нечего стеречь."]

def build(b, c, R, lr):
    Y = R.TER_Y; tx1, tz1, tx2, tz2 = R.TERRACE; hx1, hz1, hx2, hz2 = R.HOUSE
    g = c.g; m = {}
    # ---- the terrace: yard surface, retaining walls (outside higher: the face of the outer column; outside lower: the edge column), a fence on the drops
    for x in range(tx1, tx2 + 1):
        for z in range(tz1, tz2 + 1):
            b.set(x, Y, z, YARD.at(x, Y, z) if not (hx1 <= x <= hx2 and hz1 <= z <= hz2) else "minecraft:cobblestone")
            clear(b, x, Y + 1, z, Y + 14)
    def nat(x, z): return int(c.gr["before"][R.ix(c.gr, x, z)]) if not (x, z) in lr["stream"] else Y
    edge = []
    for x in range(tx1 - 1, tx2 + 2):
        for z in range(tz1 - 1, tz2 + 2):
            if tx1 <= x <= tx2 and tz1 <= z <= tz2: continue
            if (x, z) in lr["stream"] or (x, z) in lr["roadset"] or R.P.on_pad(x, z): continue
            gy = g(x, z)
            if gy > Y:
                for yy in range(Y + 1, gy + 1): b.set(x, yy, z, RET.at(x, yy, z))
    for x in range(tx1, tx2 + 1):
        for z in range(tz1, tz2 + 1):
            if not (x in (tx1, tx2) or z in (tz1, tz2)): continue
            low = min((g(x + a, z + d) for a, d in ((1, 0), (-1, 0), (0, 1), (0, -1)) if not (tx1 <= x + a <= tx2 and tz1 <= z + d <= tz2) and (x + a, z + d) not in lr["stream"]), default=Y)
            if low < Y:
                for yy in range(low + 1, Y + 1): b.set(x, yy, z, RET.at(x, yy, z))
                if not (hx1 <= x <= hx2 and hz1 <= z <= hz2) and not (x == tx2 and R.BRIDGE_Z[0] <= z <= R.BRIDGE_Z[1]):
                    b.set(x, Y + 1, z, "minecraft:spruce_fence"); edge.append((x, z))
    # the yard's east edge over the stream: a fence with the wicket (open gate) at the bridge
    for z in range(tz1, hz1):
        if R.BRIDGE_Z[0] <= z <= R.BRIDGE_Z[1]: b.set(tx2, Y + 1, z, "minecraft:spruce_fence_gate[facing=east,in_wall=false,open=true,powered=false]")
        else: b.set(tx2, Y + 1, z, "minecraft:spruce_fence")
    # ---- the stream: the spring in the rock (z 428), pools stepping down, falls, the pool and the crack in its floor
    st_ = lr["stream"]
    for (x, z), w in st_.items():
        b.set(x, w - 1, z, "minecraft:mossy_cobblestone" if hsh(x, 0, z, 7210) < 0.5 else "minecraft:gravel")
        b.set(x, w, z, "minecraft:water[level=0]")
        for yy in range(w + 1, w + 6):
            if b.get(x, yy, z) is None: b.set(x, yy, z, "minecraft:air")
        for a in (-1, 1):                                     # the banks: stone up to the water (+1 on the road side: the curb)
            q = (x + a, z)
            if q in st_: continue
            top = w + (1 if q[0] > x else 0)
            for yy in range(w - 1, top + 1):
                if b.get(q[0], yy, z) in (None, "minecraft:air") or q[0] == 113: b.set(q[0], yy, z, RET.at(q[0], yy, z))
    zs = sorted(set(z for (_, z) in st_))
    for z in zs:                                             # the north and south ends of each step: stone to the water + falls over the lips
        nxt = z + 1
        for x in R.STREAM:
            if (x, nxt) not in st_:
                for yy in range(st_[(x, z)] - 1, st_[(x, z)] + 1): b.set(x, yy, nxt, RET.at(x, yy, nxt)) if not R.P.on_pad(x, nxt) else None
    # the falls over the lips: the scan reads flowing water as air, so the blocks here are still water; the datapack starts the flow
    # (cemetery/gen/stream: the source at each lip set again when its fall is missing) -> m["falls"] = [[source], [fall cell]]
    m["falls"] = [[[x, st_[(x, z)], z], [x, st_[(x, z)], z + 1]] for z in zs for x in R.STREAM
                  if (x, z + 1) in st_ and st_[(x, z + 1)] < st_[(x, z)]]
    for x in R.STREAM:                                       # the spring: a niche in the rock face at z 427
        b.set(x, 196, 427, "minecraft:water[level=0]"); b.set(x, 195, 427, "minecraft:mossy_cobblestone")
        for yy in (197, 198): b.set(x, yy, 427, "minecraft:air")
        b.set(x, 199, 427, "minecraft:mossy_cobblestone"); b.set(x + (1 if x == R.STREAM[1] else -1), 196, 427, "minecraft:mossy_cobblestone")
    for (x, z) in ((R.STREAM[0], 426), (R.STREAM[1], 426)):
        for yy in range(195, 200): b.set(x, yy, z, "minecraft:mossy_cobblestone" if yy != 199 else "minecraft:moss_block")
    cx, cz = R.STREAM[1], 441                                # the crack: the water goes down a slot in the pool's floor
    w = st_[(cx, cz)]
    for yy in range(w - 4, w): b.set(cx, yy, cz, "minecraft:water[level=8]")
    b.set(cx, w - 5, cz, "minecraft:stone")
    for (a, d) in ((1, 0), (0, 1), (-1, 0)):
        for yy in range(w - 5, w - 1):
            if b.get(cx + a, yy, cz + d) is None and not R.P.on_pad(cx + a, cz + d): b.set(cx + a, yy, cz + d, "minecraft:stone")
    for (x, z) in ((R.STREAM[0], 440), (R.STREAM[0], 438), (113, 436)):     # fireflies by the water
        if b.get(x, w + 1, z) in (None, "minecraft:air") and (x, z) not in st_: b.set(x, g(x, z) + 1, z, "minecraft:firefly_bush")
    # ---- the road (graded: slabs for the half blocks, stairs for a whole block)
    prev = None
    for (x, z), s2 in lr["road_list"]:
        half = s2 % 2 == 1
        y = (s2 - 1) // 2 if half else s2 // 2 - 1
        if half: b.set(x, y, z, slab("cobblestone_slab") if hsh(x, 1, z, 7211) < 0.5 else slab("mossy_cobblestone_slab")); b.set(x, y - 1, z, "minecraft:dirt")
        else:
            up = lr["road_up"].get((x, z))
            b.set(x, y, z, stairs("cobblestone_stairs", up) if up else YARD.at(x, y, z))
        clear(b, x, y + 1, z, y + 4)
    # ---- the footbridge from the wicket to the road (z 434..435), spruce, with rails
    for x in range(R.STREAM[0], 114):
        for z in range(R.BRIDGE_Z[0], R.BRIDGE_Z[1] + 1): b.set(x, Y, z, "minecraft:spruce_planks")
        for z in (R.BRIDGE_Z[0] - 1, R.BRIDGE_Z[1] + 1):
            if x != 113: b.set(x, Y + 1, z, "minecraft:spruce_fence")
    for z in (R.BRIDGE_Z[0], R.BRIDGE_Z[1]):
        b.set(R.STREAM[0], Y - 1, z, "minecraft:spruce_log[axis=y]") if False else None
    # ---- the house
    H = Y + 1                                                # walls from here; ground floor 4 high (H..H+3), mansard floor at H+4
    for x in range(hx1, hx2 + 1):
        for z in range(hz1, hz2 + 1):
            wall = x in (hx1, hx2) or z in (hz1, hz2)
            b.set(x, Y, z, "minecraft:cobblestone" if wall else "minecraft:spruce_planks")
            for yy in range(H, H + 4):
                if wall:
                    corner = x in (hx1, hx2) and z in (hz1, hz2)
                    b.set(x, yy, z, "minecraft:stripped_spruce_log[axis=y]" if corner else WALL.at(x, yy, z))
                else: b.set(x, yy, z, "minecraft:air")
            b.set(x, H + 4, z, "minecraft:spruce_planks" if not wall else WALL.at(x, H + 4, z))
    # the roof: gable along z, eaves at x hx1-1 / hx2+1 at H+4, ridge over the middle x (hx1+hx2)/2
    mid = (hx1 + hx2) // 2
    for z in range(hz1 - 1, hz2 + 2):
        for x in range(hx1 - 1, hx2 + 2):
            d = abs(x - mid); y = H + 4 + (mid - hx1 + 1 - d)
            if x == mid: b.set(x, y, z, slab("spruce_slab"))
            else:
                f = "east" if x < mid else "west"
                endz = z in (hz1 - 1, hz2 + 1)
                b.set(x, y, z, stairs("mossy_cobblestone_stairs" if endz else "spruce_stairs", f))
                if not endz and d >= 1: b.set(x, y - 1, z, stairs("spruce_stairs", "west" if x < mid else "east", "top")) if False else None
        # the gable walls (north and south) under the roof
    for z in (hz1, hz2):
        for x in range(hx1 + 1, hx2):
            d = abs(x - mid); top = H + 4 + (mid - hx1 + 1 - d) - 1
            for yy in range(H + 5, top + 1): b.set(x, yy, z, WALL.at(x, yy, z))
        b.set(mid, H + 6, z, "minecraft:glass_pane")
    # mansard air
    for x in range(hx1 + 1, hx2):
        for z in range(hz1 + 1, hz2):
            d = abs(x - mid); top = H + 4 + (mid - hx1 + 1 - d) - 1
            for yy in range(H + 5, top + 1): b.set(x, yy, z, "minecraft:air")
    # door north (to the yard), back door south (to the garden), windows (glass panes), the east window on the cemetery
    dx_ = mid
    for (z, f) in ((hz1, "north"), (hz2, "south")):
        x = dx_ if z == hz1 else hx2 - 2
        b.set(x, H, z, "minecraft:spruce_door[facing=%s,half=lower,hinge=left,open=false,powered=false]" % ("south" if f == "north" else "north"))
        b.set(x, H + 1, z, "minecraft:spruce_door[facing=%s,half=upper,hinge=left,open=false,powered=false]" % ("south" if f == "north" else "north"))
    m["door"] = [dx_, H, hz1]; m["door_back"] = [hx2 - 2, H, hz2]
    wins = [(hx2, 441), (hx2, 444), (hx2, 447), (hx1, 441), (hx1, 446), (102, hz1), (108, hz1), (103, hz2)]
    for (x, z) in wins:
        for yy in (H + 1, H + 2): b.set(x, yy, z, "minecraft:glass_pane")
        b.set(x + (1 if x == hx2 else (-1 if x == hx1 else 0)), H, z + (1 if z == hz2 else (-1 if z == hz1 else 0)), "minecraft:spruce_trapdoor[facing=%s,half=top,open=false,powered=false,waterlogged=false]" % ("east" if x == hx2 else "west" if x == hx1 else "south" if z == hz2 else "north")) if False else None
    # inside: the hearth at the south wall (campfire in a stone hearth, chimney 1 over it), table, bed, the armchair by the east window
    hx, hz = 104, hz2 - 1
    for x in (hx - 1, hx, hx + 1):
        b.set(x, H + 2, hz, "minecraft:cobblestone"); b.set(x, H + 3, hz, "minecraft:cobblestone")
    b.set(hx - 1, H, hz, "minecraft:cobblestone"); b.set(hx + 1, H, hz, "minecraft:cobblestone"); b.set(hx - 1, H + 1, hz, "minecraft:cobblestone"); b.set(hx + 1, H + 1, hz, "minecraft:cobblestone")
    b.set(hx, H, hz, "minecraft:campfire[facing=north,lit=true,signal_fire=false,waterlogged=false]"); b.set(hx, H + 1, hz, "minecraft:air")
    m["hearth"] = [hx, H, hz - 2]
    chim = [(hx, hz2), (102, hz1)]
    for (x, z) in chim:
        top = H + 13
        for yy in range(H, top): b.set(x, yy, z, "minecraft:mushroom_stem[down=true,east=true,north=true,south=true,up=true,west=true]")
        cap = "red_mushroom_block" if (x, z) == chim[0] else "brown_mushroom_block"
        for a in (-1, 0, 1):
            for d in (-1, 0, 1):
                b.set(x + a, top, z + d, "minecraft:%s[down=%s,east=true,north=true,south=true,up=true,west=true]" % (cap, "true" if (a or d) else "false"))
        b.set(x, top + 1, z, "minecraft:%s[down=false,east=true,north=true,south=true,up=true,west=true]" % cap)
    b.set(hx, H + 2, hz2, "minecraft:mushroom_stem[down=true,east=true,north=true,south=true,up=true,west=true]")
    # table and chairs, bed, barrels, the ladder to the mansard
    for (x, z) in ((104, 443), (105, 443)):
        b.set(x, H, z, "minecraft:spruce_fence"); b.set(x, H + 1, z, "minecraft:spruce_pressure_plate[powered=false]") if False else None
        b.set(x, H, z, "minecraft:spruce_fence")
    for (x, z) in ((104, 443), (105, 443)): b.set(x, H + 1, z, slab("spruce_slab")) if False else None
    b.set(104, H, 443, "minecraft:spruce_fence"); b.set(104, H + 1, 443, "minecraft:spruce_pressure_plate[powered=false]")
    b.set(105, H, 443, "minecraft:spruce_fence"); b.set(105, H + 1, 443, "minecraft:spruce_pressure_plate[powered=false]")
    b.set(103, H, 443, stairs("spruce_stairs", "west")); b.set(106, H, 443, stairs("spruce_stairs", "east"))
    b.set(hx1 + 1, H, 446, "minecraft:brown_bed[facing=north,occupied=false,part=foot]"); b.set(hx1 + 1, H, 445, "minecraft:brown_bed[facing=north,occupied=false,part=head]")
    for (x, z) in ((hx1 + 1, 448), (hx1 + 1, 449)): b.set(x, H, z, st("barrel", facing="up", open="false"))
    for yy in range(H, H + 5): b.set(hx1 + 1, yy, hz1 + 1, "minecraft:ladder[facing=south,waterlogged=false]")
    b.set(hx1 + 1, H + 4, hz1 + 1, "minecraft:ladder[facing=south,waterlogged=false]")
    # the armchair by the east window (the keeper sits here by day)
    b.set(hx2 - 1, H, 444, stairs("spruce_stairs", "east"))
    b.set(hx2 - 1, H, 443, "minecraft:spruce_trapdoor[facing=south,half=bottom,open=true,powered=false,waterlogged=false]")
    b.set(hx2 - 1, H, 445, "minecraft:spruce_trapdoor[facing=north,half=bottom,open=true,powered=false,waterlogged=false]")
    m["chair"] = [hx2 - 1, H, 444]; m["window"] = [hx2, H + 1, 441]       # the spyglass stands at the gate of the descent (review T-027)
    # lanterns (the warm windows; gone after the fading)
    lan = [(105, H + 3, 441), (103, H + 3, 447), (105, H + 8, 444), (107, H + 3, 446)]
    for (x, y, z) in lan: b.set(x, y, z, lantern("lantern", True))
    m["lamps"] = [list(p) for p in lan]
    # the mansard: the lectern with the Book of Records, shelves, a chest of old papers
    lx, lz = mid, 446
    b.set(lx, H + 5, lz, st("lectern", facing="north", has_book="true", powered="false") + book_nbt("Книга учёта", "смотритель", BOOK))
    m["lectern"] = [lx, H + 5, lz]
    for z in (440, 441, 449, 448):
        b.set(mid - 1, H + 5, z, "minecraft:bookshelf"); b.set(mid + 1, H + 5, z, "minecraft:bookshelf")
    # ---- the yard: the keeper's lantern on its post at the wicket, the bell on its post by the door, the kennel
    px, pz = R.TERRACE[2] - 1, R.BRIDGE_Z[0] - 1
    for yy in range(H, H + 5): b.set(px, yy, pz, "minecraft:spruce_log[axis=y]")
    b.set(px + 1, H + 4, pz, "minecraft:spruce_fence"); b.set(px + 1, H + 3, pz, chain())
    b.set(px + 1, H + 2, pz, lantern("lantern", True))
    m["post_lantern"] = [px + 1, H + 2, pz]
    bx, bz = dx_ + 2, hz1 - 1
    b.set(bx, H, bz, "minecraft:stone_brick_wall"); b.set(bx, H + 1, bz, "minecraft:bell[attachment=floor,facing=north,powered=false]")
    m["bell"] = [bx, H + 1, bz]
    kx, kz = tx1, tz1 + 1                                    # the kennel 3 x 3 (spruce, an opening to the east)
    for x in range(kx, kx + 3):
        for z in range(kz, kz + 3):
            for yy in (H, H + 1):
                if x == kx + 2 and z == kz + 1: b.set(x, yy, z, "minecraft:air"); continue
                b.set(x, yy, z, "minecraft:spruce_planks" if (x in (kx, kx + 2) or z in (kz, kz + 2)) else "minecraft:air")
            b.set(x, H + 2, z, slab("spruce_slab"))
    b.set(kx + 1, H, kz + 1, "minecraft:brown_carpet")
    m["dog"] = [dx_, H, hz1 - 1]; m["kennel"] = [kx + 1, H, kz + 1]
    # ---- the shed (7 x 5 spruce, roof of slabs, door west): the holder of the shovel empty (2 tripwire hooks), a lantern, barrels of lime, boards
    sx1, sz1, sx2, sz2 = R.SHED
    for x in range(sx1, sx2 + 1):
        for z in range(sz1, sz2 + 1):
            wall = x in (sx1, sx2) or z in (sz1, sz2)
            b.set(x, Y, z, "minecraft:spruce_planks")
            for yy in range(H, H + 3):
                corner = x in (sx1, sx2) and z in (sz1, sz2)
                b.set(x, yy, z, ("minecraft:stripped_spruce_log[axis=y]" if corner else "minecraft:spruce_planks") if wall else "minecraft:air")
            b.set(x, H + 3, z, slab("spruce_slab"))
    for yy in (H, H + 1): b.set(sx1, yy, 453, "minecraft:spruce_door[facing=west,half=%s,hinge=left,open=false,powered=false]" % ("lower" if yy == H else "upper"))
    b.set(sx2, H + 1, 452, "minecraft:tripwire_hook[attached=false,facing=west,powered=false]")
    b.set(sx2, H + 1, 454, "minecraft:tripwire_hook[attached=false,facing=west,powered=false]")
    m["holder"] = [sx2 - 1, H + 1, 453]
    b.set(sx1 + 1, H, sz1 + 1, st("barrel", facing="up", open="false")); b.set(sx1 + 2, H, sz1 + 1, st("barrel", facing="up", open="false"))
    b.set(sx1 + 1, H, sz2 - 1, slab("spruce_slab")); b.set(sx1 + 2, H, sz2 - 1, slab("spruce_slab", "double") if False else slab("spruce_slab"))
    b.set(sx2 - 2, H, sz2 - 1, "minecraft:composter[level=0]")
    b.set(sx1 + 3, H + 2, 453, lantern("lantern", True)); m["lamps"].append([sx1 + 3, H + 2, 453])
    # ---- the garden: pumpkins, carved pumpkins (faces inward only: to the west/north), ferns as cabbage, the scarecrow (a stand, the datapack)
    gx1, gz1, gx2, gz2 = R.GARDEN
    for x in range(gx1, gx2 + 1):
        for z in range(gz1, gz2 + 1):
            b.set(x, Y, z, "minecraft:farmland[moisture=7]" if (x + z) % 2 == 0 else "minecraft:rooted_dirt")
            r = hsh(x, 3, z, 7220)
            if (x + z) % 2 == 0 and x != gx2 - 1: b.set(x, Y + 1, z, "minecraft:wheat[age=%d]" % (3 + int(r * 5)) if r < 0.4 else "minecraft:air")
            elif r < 0.35: b.set(x, Y + 1, z, "minecraft:pumpkin")
            elif r < 0.5: b.set(x, Y + 1, z, "minecraft:carved_pumpkin[facing=%s]" % ("west" if r < 0.43 else "north"))
            elif r < 0.7: b.set(x, Y + 1, z, "minecraft:fern")
    m["scarecrow"] = [gx2 - 1, Y + 1, (gz1 + gz2) // 2]
    b.set(gx2 - 1, Y + 1, (gz1 + gz2) // 2, "minecraft:air")
    m["centre"] = [(hx1 + hx2) // 2, Y + 1, (hz1 + hz2) // 2]
    m["edge_fence"] = len(edge)
    return m
