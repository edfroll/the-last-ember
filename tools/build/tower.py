"""Watchtower (card «Сторожевая башня»): on the cone hill north-west of the plaza. Plinth d13, round shaft d11 narrowing to d9,
external spiral stair (1.5 turns) with three landings/galleries, top room d15 with the map wall (16 frames), balcony, belfry with
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
    b.cyl(TX, y0 - 1, TZ, y0 + 95, 12, "air"); b.disc(TX, y0 - 1, TZ, 7.3, Mix({"cobblestone": 60, "gravel": 20, "coarse_dirt": 20}, 72))
    # plinth d13, 4 high, battered
    for y in range(y0, y0 + 4): b.disc(TX, y, TZ, 6.5 - (y - y0) * 0.25, Mix({"cobblestone": 50, "mossy_cobblestone": 25, "stone_bricks": 25}, 73), hollow_r=4.6 - (y - y0) * 0.25)
    b.disc(TX, y0 - 1, TZ, 5, "polished_andesite")
    # shaft
    for y in range(y0 + 4, 189):
        r = rad_at(y); b.disc(TX, y, TZ, r, WALL, hollow_r=r - 1.2)
        if (y - y0) % 12 == 6:   # slit windows on 4 sides
            for dx, dz in ((round(r), 0), (-round(r), 0), (0, round(r)), (0, -round(r))): b.set(TX + dx, y, TZ + dz, "air"); b.set(TX + dx, y + 1, TZ + dz, "air")
    # door to the stairwell (south side, facing the plaza path) and an inner ladder shaft for the descent
    b.fill(TX, y0, TZ + 4, TX, y0 + 2, TZ + 7, "air")
    b.set(TX, y0, TZ + 5, "spruce_door[facing=north,half=lower,hinge=left,open=false]"); b.set(TX, y0 + 1, TZ + 5, "spruce_door[facing=north,half=upper,hinge=left,open=false]")
    b.set(TX, y0 + 2, TZ + 4, lantern(True))
    # external spiral stair: 64 steps, 1.5 turns, 2 wide, from the plinth top (y0+4) to y 189, with a stone rail
    steps = 64; turns = 1.5; ytop = 189; cells = []
    b.disc(TX, y0 + 4, TZ, 5, "spruce_planks")          # store-room ceiling inside the plinth
    for i in range(steps):
        a = math.radians(180 + i * 360 * turns / steps); yy = y0 + round(i * (ytop - y0 - 1) / (steps - 1))
        r0 = max(rad_at(yy), rad_at(yy + 3))
        for rr in (r0 + 0.9, r0 + 1.9):
            x, z = TX + round(math.sin(a) * rr), TZ - round(math.cos(a) * rr)
            b.set(x, yy, z, Mix({"stone_bricks": 60, "cobblestone": 40}, 74)); cells.append((x, yy, z))
        rx, rz = TX + round(math.sin(a) * (r0 + 2.9)), TZ - round(math.cos(a) * (r0 + 2.9))
        b.set(rx, yy + 1, rz, "stone_brick_wall")
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
    a = math.radians(180 + 360 * turns); ex, ez = TX + round(math.sin(a) * 7), TZ - round(math.cos(a) * 7)
    b.fill(ex, 190, ez, ex, 191, ez, "air")
    # balcony ring at 190 (outside the room), rail
    b.disc(TX, 189, TZ, 9.4, slab("stone_brick_slab", "top"), hollow_r=7.6); b.disc(TX, 190, TZ, 9.4, "stone_brick_wall", hollow_r=8.6)
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
    # headroom over every step (cuts the hatch through the balcony and the room floor at the top of the climb)
    cs = set(cells)
    for (x, yy, z) in cells:
        for dy in (1, 2, 3):
            if (x, yy + dy, z) not in cs: b.set(x, yy + dy, z, "air")
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
