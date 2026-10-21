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
    b = B("tower"); y0 = BASE
    b.cyl(TX, y0, TZ, y0 + 95, 12, "air"); b.disc(TX, y0 - 1, TZ, 7.3, Mix({"cobblestone": 60, "gravel": 20, "coarse_dirt": 20}, 72))
    # plinth d13, 4 high, battered
    for y in range(y0, y0 + 4): b.disc(TX, y, TZ, 6.5 - (y - y0) * 0.25, Mix({"cobblestone": 50, "mossy_cobblestone": 25, "stone_bricks": 25}, 73), hollow_r=4.6 - (y - y0) * 0.25)
    b.disc(TX, y0 - 1, TZ, 5, "polished_andesite")
    # shaft
    for y in range(y0 + 4, 189):
        r = rad_at(y); b.disc(TX, y, TZ, r, WALL, hollow_r=r - 1.2)
        if (y - y0) % 12 == 6:   # slit windows on 4 sides
            for dx, dz in ((round(r), 0), (-round(r), 0), (0, round(r)), (0, -round(r))): b.set(TX + dx, y, TZ + dz, "air"); b.set(TX + dx, y + 1, TZ + dz, "air")
    # door to the stairwell (south side, facing the plaza path) and an inner ladder shaft for the descent
    b.fill(TX, y0, TZ + 4, TX, y0 + 1, TZ + 7, "air")      # doorway exactly 2 high (no gap over the door)
    b.set(TX, y0, TZ + 5, "spruce_door[facing=north,half=lower,hinge=left,open=false]"); b.set(TX, y0 + 1, TZ + 5, "spruce_door[facing=north,half=upper,hinge=left,open=false]")
    b.set(TX, y0 + 3, TZ + 3, lantern(True))                 # hangs from the store-room ceiling (y0+4)
    # external spiral stair (T-008 review: no jumps, 2 turns). A 4-connected walking line at radius 8.5 (no diagonal moves) rises
    # exactly half a block per cell (bottom slab / full block alternate), widened to 3 lanes; it arrives on the balcony (y 190).
    b.disc(TX, y0 + 4, TZ, 4.2, "spruce_planks")        # store-room ceiling inside the shaft (not visible outside)
    A0 = 200.0; TURNS = 2; S0, S1 = 2 * y0, 2 * 190; RW = 9.0
    line = []
    for k in range(int(360 * TURNS * 8) + 1):
        a = math.radians(A0 + k / 8); c = (TX + round(math.sin(a) * RW), TZ - round(math.cos(a) * RW))
        if line and c == line[-1][0]: continue
        if line and abs(c[0] - line[-1][0][0]) + abs(c[1] - line[-1][0][1]) == 2:   # diagonal: insert the corner nearer the circle
            p1, p2 = (c[0], line[-1][0][1]), (line[-1][0][0], c[1])
            line.append((min((p1, p2), key=lambda q: abs(math.hypot(q[0] - TX, q[1] - TZ) - RW)), a))
        line.append((c, a))
    moves = len(line) - 1; rise = S1 - S0
    assert moves >= rise, (moves, rise)
    steps = {}; rails = set(); sv = S0; lane = []
    for i, ((cx_, cz_), a) in enumerate(line):
        if i: sv = S0 + (i * rise) // moves
        yb = (sv - 1) // 2 if sv % 2 else sv // 2 - 1
        st = slab("stone_brick_slab") if sv % 2 else "minecraft:stone_bricks"
        lane.append((cx_, yb, cz_, st, (sv + 1) // 2))
    main = {(x, z) for x, _, z, _, _ in lane}
    for x, yb, z, st, top in lane:
        steps[(x, yb, z)] = (st, top)
    for x, yb, z, st, top in lane:                       # side lanes: radial neighbours take the height of the main line
        rr = math.hypot(x - TX, z - TZ); ux, uz = (x - TX) / rr, (z - TZ) / rr
        for dr in (-1, 1):
            q = (round(x + ux * dr), round(z + uz * dr))
            if q in main or any((q[0], y, q[1]) in steps for y in range(yb - 2, yb + 3)): continue
            steps[(q[0], yb, q[1])] = (st, top)
        for k in range(2, 6):                            # fill inward up to the shaft wall: no gaps to look (or fall) through
            q = (round(x - ux * k), round(z - uz * k))
            if math.hypot(q[0] - TX, q[1] - TZ) <= rad_at(min(yb, 188)) + 0.3: break
            if yb >= 183 and math.hypot(q[0] - TX, q[1] - TZ) < 7.6: break      # keep the top-room floor whole
            if q in main or any((q[0], y, q[1]) in steps for y in range(yb - 2, yb + 3)): continue
            steps[(q[0], yb, q[1])] = (st, top)
        q = (round(x + ux * 2), round(z + uz * 2))
        if q not in main: rails.add((q[0], top, q[1]))
    brackets = []                                        # every 6th cell a stone bracket ties the stair to the shaft
    for i, (x, yb, z, st, top) in enumerate(lane):
        if True: continue
        rr = math.hypot(x - TX, z - TZ); ux, uz = (x - TX) / rr, (z - TZ) / rr
        for k in range(1, 5):
            q = (round(x - ux * k), round(z - uz * k))
            if math.hypot(q[0] - TX, q[1] - TZ) <= rad_at(min(yb, 188)) + 0.3: break
            if yb >= 183 and math.hypot(q[0] - TX, q[1] - TZ) < 7.6: break      # keep the top-room floor whole
            brackets.append((q[0], yb - 1, q[1]))
    global STEPS, LINE; STEPS = steps; LINE = lane
    # galleries / landings at 145, 152, 172: ring platform with a wall rail and a lantern
    for gy in (145, 152, 172):
        r = rad_at(gy); b.disc(TX, gy, TZ, r + 2.4, slab("stone_brick_slab", "top"), hollow_r=r)
        b.disc(TX, gy + 1, TZ, r + 3.4, "stone_brick_wall", hollow_r=r + 2.6); b.disc(TX, gy, TZ, r + 3.4, slab("stone_brick_slab", "top"), hollow_r=r)
        b.set(TX + round(r) + 1, gy + 1, TZ, lantern()); b.marker(f"gallery_{gy}", TX, gy + 1, TZ + round(r) + 1)
    # top room d15, y 189..197, floor 189, windows all round, the map wall (16 frames, 4x4) on the north inner wall
    b.disc(TX, 189, TZ, 7.5, "spruce_planks"); b.disc(TX, 188, TZ, 7.5, WALL, hollow_r=5.5)
    for y in range(190, 198):
        b.disc(TX, y, TZ, 7.5, WALL, hollow_r=6.3)
    b.cyl(TX, 190, TZ, 197, 6.3, "air")
    for k in range(12):
        a = math.radians(k * 30 + 15); x, z = TX + round(math.sin(a) * 7.2), TZ - round(math.cos(a) * 7.2)
        if not (k in (11, 0)): b.fill(x, 192, z, x, 194, z, "glass_pane")
    for i in range(4):
        for j in range(4): b.marker(f"map_frame_{i}{j}", TX - 2 + i, 194 - j, TZ - 6, "item_frame facing south")
    b.fill(TX - 3, 190, TZ - 6, TX + 2, 195, TZ - 6, "spruce_planks")
    b.fill(TX - 2, 190, TZ - 5, TX + 1, 190, TZ - 5, "spruce_stairs[facing=north,half=bottom,shape=straight]") if False else None
    b.set(TX + 3, 190, TZ + 2, "cartography_table"); b.set(TX + 2, 190, TZ + 2, "barrel[facing=up,open=false]")
    b.set(TX - 3, 190, TZ + 3, "straw_bed[facing=east,part=head]"); b.set(TX - 4, 190, TZ + 3, "straw_bed[facing=east,part=foot]")
    for (lx, lz) in ((TX, TZ), (TX - 3, TZ - 3), (TX + 3, TZ + 3)): b.set(lx, 197, lz, lantern(True))
    # entry from the stair top into the room (south-west side)
    # balcony ring at 190 (outside the room), rail
    b.disc(TX, 189, TZ, 11.4, slab("stone_brick_slab", "top"), hollow_r=7.6); b.disc(TX, 190, TZ, 11.4, "stone_brick_wall", hollow_r=10.6)
    b.marker("tower_view", TX, 190, TZ + 9, "view to the plaza, south-east")
    # belfry y198..205: floor, 4 pillars, open arches, the bell hanging under a beam
    b.disc(TX, 198, TZ, 7.5, "polished_deepslate")
    for dx, dz in ((-5, -5), (5, -5), (-5, 5), (5, 5)): b.fill(TX + dx, 199, TZ + dz, TX + dx, 205, TZ + dz, log("stripped_dark_oak_log"))
    b.disc(TX, 206, TZ, 7.5, "dark_oak_planks"); b.fill(TX - 4, 205, TZ, TX + 4, 205, TZ, log("dark_oak_log", "x"))
    b.set(TX, 204, TZ, "bell[attachment=ceiling,facing=north]"); b.marker("bell", TX, 204, TZ)
    b.set(TX + 4, 199, TZ + 4, "ladder[facing=north]") if False else None
    b.fill(TX + 5, 190, TZ - 1, TX + 5, 198, TZ - 1, "ladder[facing=west]") if False else None
    # ladder from the room to the belfry (east inner wall)
    b.fill(TX + 6, 190, TZ, TX + 6, 198, TZ, "ladder[facing=west]"); b.set(TX + 6, 198, TZ, "ladder[facing=west]")
    # roof cone 207..213, spire to 217
    for y in range(207, 214):
        r = 7.5 * (214 - y) / 7.5
        b.disc(TX, y, TZ, r, "deepslate_tiles", hollow_r=max(r - 1.4, -1))
    b.fill(TX, 214, TZ, TX, 216, TZ, "iron_chain"); b.set(TX, 217, TZ, "lightning_rod")
    # headroom over every step (cuts the hatch through the room floor at the top of the climb), then the steps, a top-slab underside, the rail
    for (x, yb, z), (st, top) in steps.items():
        for y in range(yb + 1, top + 3):
            if (x, y, z) not in steps: b.set(x, y, z, "air")
    for (x, y, z) in rails:
        if not any((x, y + k, z) in steps for k in (-2, -1, 0, 1, 2)) and math.hypot(x - TX, z - TZ) > rad_at(min(y, 188)) + 0.4:
            b.set(x, y, z, "stone_brick_wall")
    for (x, yb, z), (st, top) in steps.items():
        b.set(x, yb, z, st)
        if (x, yb - 1, z) not in steps and b.get(x, yb - 1, z) in (None, "minecraft:air"): b.set(x, yb - 1, z, slab("stone_brick_slab", "top"))
    for (x, y, z) in brackets:
        if b.get(x, y, z) in (None, "minecraft:air"): b.set(x, y, z, slab("stone_brick_slab", "top"))
    # entry (after the room walls are built): a 3x3 doorway from the balcony into the top room where the stair arrives
    a = math.radians(A0); ox_, oz_ = math.sin(a), -math.cos(a); px_, pz_ = math.cos(a), math.sin(a)
    for rr_ in (5.8, 6.4, 7.0, 7.6):
        for w in (-1, 0, 1):
            q = (TX + round(ox_ * rr_ + px_ * w), TZ + round(oz_ * rr_ + pz_ * w))
            b.fill(q[0], 190, q[1], q[0], 192, q[1], "air"); b.set(q[0], 189, q[1], "minecraft:spruce_planks")
    q = (TX + round(ox_ * 6.4), TZ + round(oz_ * 6.4)); b.set(q[0], 193, q[1], "minecraft:stone_bricks")
    q = (TX + round(ox_ * 5.2), TZ + round(oz_ * 5.2)); b.set(q[0], 196, q[1], lantern(True))
    b.marker("tower_stair", TX, y0, TZ + 8, f"{len(lane)} cells, 2 turns, no jumps")
    # path up the cone: switchback from the plaza street end (south-east) to the door
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
