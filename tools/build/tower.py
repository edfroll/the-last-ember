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
    # external spiral stair (T-008 review: no jumps): 2 turns, 2 wide, from the ground (y 125) to the room floor (standing at 190).
    # Surfaces go up in half blocks: bottom slab (+0.5), full block (+0.5 from a slab) or a stair block (+1, walkable) -- never a jump.
    b.disc(TX, y0 + 4, TZ, 5, "spruce_planks")          # store-room ceiling inside the plinth
    def r0_at(yy): return rad_at(min(yy, 188))
    A0 = 200.0; TURNS = 2.0; S0, S1 = 2 * y0, 2 * 190     # surfaces in half blocks
    outer = []; k = 0
    while True:                                          # distinct cells of the outer lane, in walking order
        a = A0 + k * 0.5; k += 1
        if a > A0 + 360 * TURNS: break
        frac = (a - A0) / (360 * TURNS); yy = int((S0 + frac * (S1 - S0)) // 2)
        rr = r0_at(yy) + 1.9; c = (TX + round(math.sin(math.radians(a)) * rr), TZ - round(math.cos(math.radians(a)) * rr))
        if not outer or outer[-1][0] != c: outer.append((c, a))
    N = len(outer); m = N - (S1 - S0) // 2; kst = (S1 - S0) // 2 - m      # m slab pairs (+1,+1), kst stairs (+2)
    assert m >= 0 and kst >= 0, (N, m, kst)
    units = []; acc = 0.0
    for i in range(m + kst):                             # spread the slab pairs evenly among the stairs
        acc += m / (m + kst)
        if acc >= 1: units += [1, 1]; acc -= 1
        else: units.append(2)
    units += [1] * (N - len(units))
    steps = {}; rails = {}; sv = S0
    for i, ((cx_, cz_), a) in enumerate(outer):
        d = units[i] if i < len(units) else 0; sv = min(S1, sv + d)
        ar = math.radians(a); tx, tz = math.cos(ar), math.sin(ar)
        fac = ("east" if tx > 0 else "west") if abs(tx) >= abs(tz) else ("south" if tz > 0 else "north")
        if sv % 2: st = slab("stone_brick_slab"); yb = (sv - 1) // 2
        elif d == 2: st = stairs("stone_brick_stairs", fac); yb = sv // 2 - 1
        else: st = Mix({"stone_bricks": 60, "cobblestone": 40}, 74); yb = sv // 2 - 1
        yb_ = (sv + 1) // 2
        rr0 = r0_at(yb)
        for rr in (rr0 + 0.9, rr0 + 1.9):
            c = (TX + round(math.sin(ar) * rr), TZ - round(math.cos(ar) * rr))
            if (c[0], c[1]) not in [(k_[0], k_[2]) for k_ in steps if k_[1] == yb]: steps.setdefault((c[0], yb, c[1]), (st, yb_))
        rx, rz = TX + round(math.sin(ar) * (rr0 + 2.9)), TZ - round(math.cos(ar) * (rr0 + 2.9))
        rails[(rx, yb_, rz)] = True
    cells = list(steps)
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
    # headroom over every step (cuts the hatch through the room floor at the top of the climb), then the steps and the rail
    for (x, yb, z), (st, top) in steps.items():
        for y in range(yb + 1, top + 3):
            b.set(x, y, z, "air")
    for (x, y, z) in rails:
        if (x, y, z) not in steps and (x, y - 1, z) not in steps: b.set(x, y, z, "stone_brick_wall")
    for (x, yb, z), (st, top) in steps.items(): b.set(x, yb, z, st)
    b.marker("tower_stair", outer[0][0][0], y0, outer[0][0][1], f"{len(outer)} cells, 2 turns, no jumps")
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
