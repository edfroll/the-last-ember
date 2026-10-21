"""Main square (card «Главная площадь»): paving with 8 rays and a trodden ring, 2-step dais under the Main Bonfire, stone benches
ring, portico of the Hall of Awakening over the stairs, light-well grate with 4 fire points, arcade around the edge with six
shortcut gates and three street openings, lamp posts, two old trees."""
import math
from lib import B, Mix, stairs, slab, lantern, candle, log, h
from geo import FLOOR, rot, unrot, face_rot
PAVE = Mix({"cobblestone": 35, "stone_bricks": 20, "andesite": 15, "mossy_cobblestone": 15, "gravel": 10, "polished_andesite": 5}, 21)
PAVE_NOGRAVEL = Mix({"cobblestone": 40, "stone_bricks": 25, "andesite": 18, "mossy_cobblestone": 17}, 22)
PILLAR = Mix({"stone_bricks": 60, "tuff_bricks": 40}, 23)
GATES = {0: "r3", 45: "r1", 90: "r6", 160: "r4", 215: "r5", 270: "r2"}
STREETS = {125: "smithy", 240: "tavern", 315: "tower"}
LANE_WELL = 22   # lane to the well yard (between the gates of R3 and R1)
def ang_of(x, z): return (math.degrees(math.atan2(x, -z)) + 360) % 360
def ang_diff(a, b): return abs((a - b + 180) % 360 - 180)
def build():
    b = B("plaza"); y = FLOOR
    R = 30
    # clear the air volume over the square
    b.cyl(0, y + 1, 0, y + 12, R + 3, "air")
    # paving
    for x in range(-R - 3, R + 4):
        for z in range(-R - 3, R + 4):
            r = math.hypot(x, z)
            if r > R + 3.3: continue
            a = ang_of(x, z)
            if r > 6 and min(ang_diff(a, k * 45) for k in range(8)) * math.pi / 180 * r < 1.0: s = "polished_andesite"
            elif 11.5 <= r <= 12.6: s = "gravel" if h(x, 0, z, 5) < 0.7 else "coarse_dirt"
            else: s = PAVE_NOGRAVEL
            b.set(x, y, z, s); b.set(x, y - 1, z, "stone")
            if 26.5 < r < 29.5 and h(x, 1, z, 6) < 0.12: b.set(x, y + 1, z, "moss_carpet")
    # dais: step 1 (y+1) square 13x13 with a stair edge, the bonfire itself (9x9 at y+2) is built by the datapack
    for x in range(-6, 7):
        for z in range(-6, 9):
            edge = abs(x) == 6 or z in (-6, 8)
            if edge:
                f = "north" if z == 8 else ("south" if z == -6 else ("west" if x == 6 else "east"))
                b.set(x, y + 1, z, stairs("stone_brick_stairs", f))   # facing = walking direction up the step
            else: b.set(x, y + 1, z, Mix({"stone_bricks": 70, "polished_tuff": 30}, 24))
    for x in range(-5, 6):  # chiseled tuff ring under the bonfire circle edge
        for z in (-5, 5): b.set(x, y + 1, z, "chiseled_tuff")
    for z in range(-5, 6):
        for x in (-5, 5): b.set(x, y + 1, z, "chiseled_tuff")
    # benches ring r 7.5..8.5 facing the fire, gaps north (urn) and south (portico path)
    for x in range(-9, 10):
        for z in range(-9, 10):
            r = math.hypot(x, z)
            if 7.6 <= r <= 8.6 and not (abs(x) <= 3 and z < 0) and not (abs(x) <= 2 and z > 0) and not (abs(x) <= 6 and abs(z) <= 8 and (abs(x) < 7 and -6 <= z <= 8)):
                a = ang_of(x, z); f = ["south", "west", "north", "east"][int(((a + 45) % 360) // 90)]
                b.set(x, y + 1, z, stairs("stone_brick_stairs" if h(x, 2, z, 7) < 0.6 else "spruce_stairs", f))
    # portico of the Hall over the stair well (stairs come up from the east, see hall.py): x -3..3, z 12..16
    b.fill(-4, y + 1, 11, 4, y + 5, 17, "air")
    for cx in (-4, 4):
        for cz in (11, 17): b.fill(cx, y + 1, cz, cx, y + 4, cz, "stone_bricks")
    b.fill(-4, y + 5, 11, 4, y + 5, 17, "polished_deepslate")
    for x in range(-5, 6): b.set(x, y + 6, 11, stairs("stone_brick_stairs", "north")); b.set(x, y + 6, 17, stairs("stone_brick_stairs", "south"))
    b.fill(-4, y + 6, 12, 4, y + 6, 16, "polished_deepslate_slab")
    b.fill(-3, y + 1, 17, 3, y + 3, 17, "stone_bricks")  # back wall (south)
    b.set(-1, y + 1, 11, "dark_oak_door[facing=south,half=lower,hinge=left,open=true]"); b.set(-1, y + 2, 11, "dark_oak_door[facing=south,half=upper,hinge=left,open=true]")
    b.set(0, y + 1, 11, "dark_oak_door[facing=south,half=lower,hinge=right,open=true]"); b.set(0, y + 2, 11, "dark_oak_door[facing=south,half=upper,hinge=right,open=true]")
    for cx in (-3, 2):
        b.fill(cx, y + 1, 11, cx, y + 3, 11, "stone_bricks")
    b.set(-3, y + 1, 10, lantern()); b.set(2, y + 1, 10, lantern())
    b.fill(-2, y + 1, 11, -2, y + 3, 11, "stone_bricks"); b.fill(1, y + 1, 11, 1, y + 3, 11, "stone_bricks")
    # light-well grate (0,+24), 3x3 iron bars flush with the paving, 4 fire points (campfires without hay, lit later by the datapack)
    b.fill(-1, y, 23, 1, y, 25, "iron_bars"); b.fill(-1, y - 1, 23, 1, y - 15, 25, "air")
    b.fill(-2, y, 22, 2, y, 26, "chiseled_stone_bricks", replace=None) if False else None
    for dx, dz in ((-2, 22), (2, 22), (-2, 26), (2, 26)): b.set(dx, y + 1, dz, "campfire[lit=false,signal_fire=false]"); b.marker("grate_fire", dx, y + 1, dz)
    b.marker("grate", 0, y, 24)
    # lamp posts r 20
    for k in range(8):
        x, z = rot(0, 0, k * 45 + 22.5, 20, 0); x, z = round(x), round(z)
        b.set(x, y + 1, z, "cobblestone_wall"); b.fill(x, y + 2, z, x, y + 3, z, "spruce_fence"); b.set(x, y + 4, z, lantern())
    arcade(b, R)
    # two old trees by the arcade (dark oak trunk, yellow poplar leaves)
    for (tx, tz) in ((-19, -19), (21, 16)):
        b.fill(tx, y + 1, tz, tx, y + 6, tz, log("dark_oak_log")); b.set(tx + 1, y + 1, tz, log("dark_oak_log")); b.set(tx, y + 7, tz, log("dark_oak_log"))
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                for dy in range(5, 10):
                    if dx * dx + dz * dz + (dy - 7.5) ** 2 * 1.6 <= 11 and h(tx + dx, dy, tz + dz, 9) < 0.85 and b.get(tx + dx, y + dy, tz + dz) in (None, "minecraft:air"):
                        b.set(tx + dx, y + dy, tz + dz, "yellow_poplar_leaves[persistent=true]")
    b.marker("plaza_trigger", 0, y + 1, 0, "circle r30")
    return b
def opening(a):
    for g in list(GATES) + list(STREETS) + [LANE_WELL]:
        if ang_diff(a, g) * math.pi / 180 * 30 <= (4.5 if g in GATES else 2.6): return g
    if 170 <= a <= 200: return "south"
    return None
def arcade(b, R):
    y = FLOOR
    for x in range(-R - 3, R + 4):
        for z in range(-R - 3, R + 4):
            r = math.hypot(x, z); a = ang_of(x, z); op = opening(a)
            if 30.5 <= r <= 31.8:   # outer wall, 6 high, with openings
                if op is None:
                    b.fill(x, y + 1, z, x, y + 5, z, PILLAR)
                    if h(x, 3, z, 31) < 0.25: b.set(x, y + 3, z, "tuff_bricks")
                elif op in GATES: pass   # gate portals are placed by gates.py
                else: b.fill(x, y + 1, z, x, y + 5, z, "air")
            if 26.6 <= r <= 27.4 and op is None and int(round(a / 7.5)) % 2 == 0 and ang_diff(a, round(a / 7.5) * 7.5) < 1.6:
                b.fill(x, y + 1, z, x, y + 4, z, PILLAR)   # inner pillars every ~7 blocks
            if 26.6 <= r <= 31.8 and op is None:
                b.set(x, y + 5, z, log("stripped_dark_oak_log", "y") if 26.6 <= r <= 27.4 else b.get(x, y + 5, z) or PILLAR)
                b.set(x, y + 6, z, slab("deepslate_tile_slab"))
                if 28.6 <= r <= 29.4 and h(x, 4, z, 33) < 0.07: b.set(x, y + 4, z, lantern(True))
                if 29.5 <= r <= 30.4 and h(x, 5, z, 34) < 0.35: b.set(x, y + 1, z, stairs("spruce_stairs", ["south", "west", "north", "east"][int(((a + 45) % 360) // 90)]))
