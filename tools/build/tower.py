"""Watchtower (card «Сторожевая башня»): on the cone hill north-west of the plaza. Plinth d13, round shaft d11 narrowing to d9,
external spiral stair (2 turns, half steps, no jumps) with three landings/galleries, top room d15 with the map wall (16 frames), balcony, belfry with
the bell, conical roof and spire. Street from the plaza climbs the cone as a switchback path."""
import math
from lib import B, Mix, stairs, slab, lantern, log, h
from geo import TOWER, FLOOR
TX, TZ = TOWER; BASE = 125
WALL = Mix({"stone_bricks": 40, "cracked_stone_bricks": 15, "mossy_stone_bricks": 15, "tuff_bricks": 20, "andesite": 10}, 71)
def rad_at(y):
    if y < BASE + 4: return 6.5
    if y < 189: return 5.5 - 1.0 * (y - BASE - 4) / (189 - BASE - 4)
    return 7.5
def build():
    """Card «Смотровая башня» v3: plinth d13 x6 with a south arch (store room), shaft d11->d9 to y 188 with arrow slits, outside
    stair 2 wide around the shaft (stone brick stairs, spruce-plank landings every 8 blocks with a lantern, spruce fence rail on the
    outer edge, no jumps) in 2 turns, three wooden galleries on braces at landings, top room d15 on corbels (spruce planks, dark oak
    posts, windows to four sides, map wall), narrow balcony round it, belfry with the bell, cone roof, spire."""
    b = B("tower"); y0 = BASE
    b.cyl(TX, y0, TZ, y0 + 95, 13, "air")
    b.disc(TX, y0 - 1, TZ, 7.3, Mix({"cobblestone": 60, "gravel": 20, "coarse_dirt": 20}, 72))
    PL = Mix({"cobblestone": 35, "mossy_cobblestone": 25, "stone_bricks": 20, "tuff": 10, "mossy_stone_bricks": 10}, 73)
    SH = Mix({"stone_bricks": 35, "tuff_bricks": 20, "cobblestone": 15, "andesite": 15, "cracked_stone_bricks": 10, "mossy_stone_bricks": 5}, 71)
    def shaft_r(y): return 6.5 if y <= y0 + 5 else (5.5 - 1.0 * (y - y0 - 6) / (188 - y0 - 6) if y <= 188 else 0)
    # plinth d13, 6 high, store room inside, arch to the south
    for y in range(y0, y0 + 6): b.disc(TX, y, TZ, 6.5, PL, hollow_r=4.6)
    b.disc(TX, y0 - 1, TZ, 5, "polished_andesite"); b.disc(TX, y0 + 6, TZ, 5.5, "spruce_planks")
    b.fill(TX - 1, y0, TZ + 4, TX + 1, y0 + 2, TZ + 7, "air")
    for x in (TX - 1, TX + 1): b.set(x, y0 + 2, TZ + 7, stairs("stone_brick_stairs", "west" if x < TX else "east", "top"))
    b.set(TX, y0 + 3, TZ + 4, lantern(True)) if False else b.set(TX, y0 + 5, TZ, lantern(True))
    b.marker("tower_keeper", TX, y0, TZ - 2, "store room, NPC point")
    # shaft
    for y in range(y0 + 6, 189):
        r = shaft_r(y); b.disc(TX, y, TZ, r, SH if y > y0 + 20 else Mix({"stone_bricks": 40, "mossy_stone_bricks": 25, "mossy_cobblestone": 15, "cobblestone": 20}, 74), hollow_r=r - 1.2)
        if (y - y0) % 8 == 4:                             # arrow slits on the diagonals (away from the stair flights)
            for sx_, sz_ in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                k = round(r / 1.4142); b.set(TX + sx_ * k, y, TZ + sz_ * k, "air"); b.set(TX + sx_ * k, y + 1, TZ + sz_ * k, "air")
    # ---- outside stair: square spiral, sides with lanes at distance d, d+1 from the axis
    FR = {0: lambda t, w: (w, -t), 1: lambda t, w: (-t, -w), 2: lambda t, w: (-w, t), 3: lambda t, w: (t, w)}
    FACE = {0: "north", 1: "west", 2: "south", 3: "east"}
    D = [7, 6, 6, 6, 6, 6, 6, 8]; RISE = [8] * 7 + [9]
    steps = {}; order = []; landings = []; sv = y0          # sv = walking surface
    prev_end = None
    for k, d in enumerate(D):
        side = k % 4; n = 2 * d - 1; f = FR[side]
        cells_t = list(range(-(d - 1), d))
        first = [f(cells_t[0], w) for w in (d, d + 1)]
        if prev_end is not None:                            # corner landing: box spanning the previous side's end and this side's start
            xs = [c[0] for c in prev_end + first]; zs = [c[1] for c in prev_end + first]
            box = [(x, z) for x in range(min(xs), max(xs) + 1) for z in range(min(zs), max(zs) + 1) if (x, z) not in [c for c in prev_end]]
            for c in box: steps[c + (sv - 1,)] = ("minecraft:spruce_planks", "flat", sv); order.append((c, sv))
            landings.append((box, sv))
        plan = ["flat"] + ["stair"] * RISE[k]
        if k < 7: plan += ["flat"] * (n - len(plan))
        else: plan += ["flat"]                               # the last side stops on the balcony
        for i, kind in enumerate(plan):
            t = cells_t[i]
            if kind == "stair": sv += 1
            for w in (d, d + 1):
                c = f(t, w)
                st = stairs("stone_brick_stairs", FACE[side]) if kind == "stair" else ("minecraft:stone_bricks" if k < 7 else "minecraft:spruce_planks")
                steps[c + (sv - 1,)] = (st, kind, sv)
            order.append((f(t, d), sv))
            # close the gap to the shaft wall with the same block (the stair is built against the shaft)
            for w in range(d - 1, 3, -1):
                c = f(t, w)
                if math.hypot(*c) <= shaft_r(sv - 1) + 0.3: break
                if k == 7 and math.hypot(*c) < 7.6: break
                steps.setdefault(c + (sv - 1,), (steps[f(t, d) + (sv - 1,)][0], "fill", sv))
        prev_end = [f(cells_t[len(plan) - 1], w) for w in (d, d + 1)]
    global LINE, STEPS
    STEPS = {(TX + x, y, TZ + z): v for (x, z, y), v in steps.items()}; LINE = [((TX + c[0], TZ + c[1]), s_) for c, s_ in order]
    # galleries: wooden platforms on braces at three landings (y 149, 157, 173 walking level)
    gal = [landings[2], landings[3], landings[5]]
    for gi, (box, s_) in enumerate(gal):
        xs = [c[0] for c in box]; zs = [c[1] for c in box]; cx_ = 1 if max(xs) > 0 else -1; cz_ = 1 if max(zs) > 0 else -1
        x1, x2 = (min(xs), max(xs) + 3) if cx_ > 0 else (min(xs) - 3, max(xs)); z1, z2 = (min(zs), max(zs) + 3) if cz_ > 0 else (min(zs) - 3, max(zs))
        for x in range(x1, x2 + 1):
            for z in range(z1, z2 + 1):
                if math.hypot(x, z) <= shaft_r(s_ - 1) + 0.3: continue
                steps.setdefault((x, z, s_ - 1), ("minecraft:spruce_planks", "gallery", s_))
        ox = x2 if cx_ > 0 else x1; oz = z2 if cz_ > 0 else z1
        for dy in (1, 2): b.set(TX + ox, s_ - 1 - dy, TZ + oz, log("stripped_dark_oak_log")); b.set(TX + ox - cx_ * dy, s_ - 1 - dy, TZ + oz, log("stripped_dark_oak_log", "x"))
        b.set(TX + ox - cx_, s_, TZ + oz - cz_, "potted_red_tulip"); b.set(TX + ox - cx_ * 2, s_, TZ + oz - cz_, stairs("spruce_stairs", "south" if cz_ < 0 else "north"))
        b.marker(f"gallery_{gi}", TX + ox - cx_, s_, TZ + oz - cz_)
    # place: headroom, blocks, supports under the first flight, fence rail on outer edges, lanterns on landing corners
    occ = {(x, z): (y, v) for (x, z, y), v in steps.items()}
    for (x, z, y), (st, kind, s_) in steps.items():
        for yy in range(y + 1, y + 4):
            if (x, z, yy) not in steps: b.set(TX + x, yy, TZ + z, "air")
    for (x, z, y), (st, kind, s_) in steps.items():
        b.set(TX + x, y, TZ + z, st)
        if y <= y0 + 9:
            for yy in range(y0 - 3, y):
                if b.get(TX + x, yy, TZ + z) in (None, "minecraft:air"): b.set(TX + x, yy, TZ + z, PL)
        elif kind != "fill" and b.get(TX + x, y - 1, TZ + z) in (None, "minecraft:air"): b.set(TX + x, y - 1, TZ + z, slab("stone_brick_slab", "top"))
    for (x, z, y), (st, kind, s_) in steps.items():
        r = math.hypot(x, z)
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, z + dz)
            if math.hypot(*q) <= r or any((q[0], q[1], yy) in steps for yy in range(y - 2, y + 3)): continue
            if y >= 186 and math.hypot(*q) < 9.6: continue      # the balcony takes over at the top
            if b.get(TX + q[0], s_, TZ + q[1]) in (None, "minecraft:air"): b.set(TX + q[0], s_, TZ + q[1], "spruce_fence")
    for box, s_ in landings:
        far = max(box, key=lambda c: math.hypot(*c))
        rr = math.hypot(*far); ux, uz = far[0] / rr, far[1] / rr; q = (round(far[0] + ux), round(far[1] + uz))
        b.set(TX + q[0], s_, TZ + q[1], "spruce_fence"); b.set(TX + q[0], s_ + 1, TZ + q[1], lantern())
    # ---- top room d15 on corbels, y 189..197
    b.disc(TX, 188, TZ, 7.5, log("stripped_dark_oak_log", "x"), hollow_r=5.0)
    b.disc(TX, 189, TZ, 7.5, "spruce_planks")
    for y in range(190, 197):
        for x in range(-8, 9):
            for z in range(-8, 9):
                r = math.hypot(x, z)
                if 6.3 < r <= 7.8:
                    post = abs(x) == abs(z) or x == 0 or z == 0
                    b.set(TX + x, y, TZ + z, log("dark_oak_log") if post and y < 196 else ("dark_oak_planks" if y == 196 else "spruce_planks"))
                elif r <= 6.3: b.set(TX + x, y, TZ + z, "air")
    for (wx, wz, ax) in ((7, 0, "z"), (-7, 0, "z"), (0, 7, "x")):          # windows 2x2 to east, west, south; north holds the map
        for o in (-1, 1):
            for y in (192, 193):
                x, z = (wx, wz + o) if ax == "z" else (wx + o, wz)
                b.set(TX + x, y, TZ + z, "glass_pane")
    for o in (-4, 4):
        for y in (192, 193): b.set(TX + o, y, TZ - 7 + (1 if abs(o) > 3 else 0), "glass_pane")
    b.fill(TX - 2, 190, TZ - 6, TX + 1, 195, TZ - 6, "spruce_planks")
    for i in range(4):
        for j in range(4): b.marker(f"map_frame_{i}{j}", TX - 2 + i, 194 - j, TZ - 5, "item_frame facing south")
    b.set(TX + 3, 190, TZ + 3, "cartography_table"); b.set(TX + 2, 190, TZ + 4, "barrel[facing=up,open=false]")
    b.set(TX - 3, 190, TZ + 3, "straw_bed[facing=east,part=head]"); b.set(TX - 4, 190, TZ + 3, "straw_bed[facing=east,part=foot]")
    b.disc(TX, 197, TZ, 7.5, "spruce_planks")
    for (lx, lz) in ((TX, TZ), (TX - 3, TZ - 2), (TX + 2, TZ + 2)): b.set(lx, 196, lz, lantern(True))
    # doorway from the balcony where the stair arrives (south side, east of the axis)
    b.fill(TX + 2, 190, TZ + 6, TX + 3, 192, TZ + 7, "air")
    # balcony round the room: planks, spruce fence, 4 spyglass points
    for x in range(-11, 12):
        for z in range(-11, 12):
            r = math.hypot(x, z)
            under = [yy for yy in range(183, 190) if (x, z, yy) in steps]
            if 7.6 < r <= 9.5 and (not under or max(under) == 189) and (x, z, 189) not in steps: b.set(TX + x, 189, TZ + z, "spruce_planks")
            if 9.5 < r <= 10.4 and not any((x, z, yy) in steps for yy in range(184, 190)): b.set(TX + x, 190, TZ + z, "spruce_fence")
    for nm, (x, z) in (("north", (0, -9)), ("east", (9, 0)), ("south", (0, 9)), ("west", (-9, 0))): b.marker(f"spyglass_{nm}", TX + x, 190, TZ + z, "sign with the region")
    # ladder to the belfry (east inner side), post behind it
    b.fill(TX + 6, 190, TZ - 2, TX + 6, 197, TZ - 2, log("dark_oak_log"))
    b.fill(TX + 5, 190, TZ - 2, TX + 5, 198, TZ - 2, "ladder[facing=west]")
    # belfry y 198..205, roof cone, spire
    b.disc(TX, 198, TZ, 7.5, "polished_deepslate"); b.set(TX + 5, 198, TZ - 2, "ladder[facing=west]")
    b.set(TX + 6, 198, TZ - 2, log("dark_oak_log"))
    for dx, dz in ((-5, -5), (5, -5), (-5, 5), (5, 5)): b.fill(TX + dx, 199, TZ + dz, TX + dx, 205, TZ + dz, log("stripped_dark_oak_log"))
    b.disc(TX, 206, TZ, 7.5, "dark_oak_planks"); b.fill(TX - 4, 205, TZ, TX + 4, 205, TZ, log("dark_oak_log", "x"))
    b.set(TX, 204, TZ, "bell[attachment=ceiling,facing=north]"); b.marker("bell", TX, 204, TZ)
    for y in range(207, 214):
        r = 7.5 * (214 - y) / 7.5
        b.disc(TX, y, TZ, r, "deepslate_tiles", hollow_r=max(r - 1.4, -1))
    b.fill(TX, 214, TZ, TX, 215, TZ, "oxidized_cut_copper"); b.set(TX, 216, TZ, "iron_chain"); b.set(TX, 217, TZ, "lightning_rod")
    # safety rail: wherever a walkable spot of the climb borders a drop of 2+ blocks, a spruce fence (computed from the built blocks)
    import walkcheck as wk
    def g(x, y, z):
        v = b.get(x, y, z)
        return "minecraft:dirt" if v is None and y <= y0 - 1 else v
    for _ in range(2):
        S = wk.reach(g, (TX + 7, TZ + 6, float(y0)), (TX - 13, TZ - 13, TX + 13, TZ + 13), y0 - 5, 200)
        cols = {(x, z) for x, z, _s in S}
        for x, z, s_ in S:
            if s_ < y0 + 2: continue
            fy = math.floor(s_)
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, nz = x + dx, z + dz
                if (nx, nz) in cols and any(abs(t - s_) <= 1 for a, c, t in S if (a, c) == (nx, nz)): continue
                if wk.kind(g(nx, fy, nz)) != "air": continue
                d = 0; yy = fy - 1
                while yy > y0 - 5 and wk.kind(g(nx, yy, nz)) == "air": d += 1; yy -= 1
                if d >= 2: b.set(nx, fy, nz, "spruce_fence")
    b.marker("tower_view", TX, 190, TZ + 9, "view to the plaza")
    b.marker("tower_stair", TX + 7, y0, TZ + 6, f"{len(order)} walking cells, 2 turns, 2 wide, no jumps")
    return b
def path(b, natural_h):
    """paved switchback on the cone; natural_h(x,z) gives the sculpted ground"""
    pts = []
    sx, sz = round(TX + 28 * math.sin(math.radians(135))), round(TZ - 28 * math.cos(math.radians(135)))
    for i in range(140):
        t = i / 139; r = 28 - 22 * t; a = math.radians(135 + 225 * t)
        x, z = TX + r * math.sin(a), TZ - r * math.cos(a); pts.append((x, z))
    for (x, z) in pts:
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                xi, zi = round(x) + dx, round(z) + dz; yy = natural_h(xi, zi)
                if yy is None: continue
                b.set(xi, yy, zi, Mix({"cobblestone": 45, "gravel": 25, "coarse_dirt": 20, "mossy_cobblestone": 10}, 75))
    return b
