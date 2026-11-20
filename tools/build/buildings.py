"""Smithy, tavern «Последний Уголёк» with the order board and the cellar cache, well yard (state "before")."""
import math
from lib import B, Mix, stairs, slab, lantern, candle, log, h
from geo import SMITHY, TAVERN, WELL
def gable_roof(b, x1, x2, z1, z2, y0, block="deepslate_tile_stairs", ridge="deepslate_tile_slab", axis="x"):
    """roof along axis: stairs climbing from both long sides until they meet"""
    if axis == "x":
        n = (z2 - z1 + 2) // 2
        for i in range(n):
            for x in range(x1 - 1, x2 + 2):
                b.set(x, y0 + i, z1 - 1 + i, stairs(block.replace("stairs", "stairs"), "south")); b.set(x, y0 + i, z2 + 1 - i, stairs(block, "north"))
                if i > 0:
                    for zz in (z1 - 1 + i - 1, z2 + 1 - i + 1): pass
            for x in (x1, x2):
                for z in range(z1 + i, z2 - i + 1): b.set(x, y0 + i, z, "spruce_planks")
        if (z2 - z1) % 2 == 0:
            for x in range(x1 - 1, x2 + 2): b.set(x, y0 + n, (z1 + z2) // 2, slab(ridge))
    else:
        n = (x2 - x1 + 2) // 2
        for i in range(n):
            for z in range(z1 - 1, z2 + 2):
                b.set(x1 - 1 + i, y0 + i, z, stairs(block, "east")); b.set(x2 + 1 - i, y0 + i, z, stairs(block, "west"))
            for z in (z1, z2):
                for x in range(x1 + i, x2 - i + 1): b.set(x, y0 + i, z, "spruce_planks")
        if (x2 - x1) % 2 == 0:
            for z in range(z1 - 1, z2 + 2): b.set((x1 + x2) // 2, y0 + n, z, slab(ridge))
def timber_wall(b, x1, x2, z1, z2, y1, y2):
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            for z in (z1, z2): b.set(x, y, z, log("dark_oak_log") if x in (x1, x2) or (x - x1) % 4 == 0 or y == y1 else Mix({"spruce_planks": 60, "packed_mud": 40}, 41))
        for z in range(z1, z2 + 1):
            for x in (x1, x2): b.set(x, y, z, log("dark_oak_log") if z in (z1, z2) or (z - z1) % 4 == 0 or y == y1 else Mix({"spruce_planks": 60, "packed_mud": 40}, 42))
# ------------------------------------------------------------------ smithy
def smithy():
    cx, cz, fy = SMITHY; b = B("smithy"); x1, x2, z1, z2 = cx - 8, cx + 7, cz - 10, cz + 3   # workshop 16x14, facade north (to the street)
    W = Mix({"cobblestone": 35, "deepslate_bricks": 25, "stone_bricks": 20, "cracked_deepslate_bricks": 10, "mossy_cobblestone": 10}, 43)
    b.fill(x1 - 1, fy + 1, z1 - 1, x2 + 1, fy + 22, z2 + 8, "air")
    b.fill(x1, fy, z1, x2, fy, z2, "polished_deepslate"); b.fill(cx - 3, fy, z2 - 3, cx + 3, fy, z2, "cobbled_deepslate")
    b.walls(x1, fy + 1, z1, x2, fy + 5, z2, W)
    b.fill(cx - 3, fy + 1, z1, cx + 3, fy + 4, z1, "air"); b.fill(cx - 4, fy + 5, z1, cx + 4, fy + 5, z1, log("dark_oak_log", "x"))   # 7-wide opening under a beam
    b.set(x2, fy + 1, z2 - 4, "air"); b.set(x2, fy + 2, z2 - 4, "air")   # back door to the yard (east side)
    # forge 5x3 at the back wall: magma behind iron bars, blast furnace, hood and chimney
    b.fill(cx - 2, fy + 1, z2 - 2, cx + 2, fy + 3, z2 - 1, Mix({"deepslate_bricks": 50, "bricks": 30, "mud_bricks": 20}, 44))
    b.fill(cx - 1, fy + 1, z2 - 2, cx + 1, fy + 1, z2 - 2, "iron_bars"); b.fill(cx - 1, fy + 1, z2 - 1, cx + 1, fy + 1, z2 - 1, "magma_block")
    b.set(cx + 3, fy + 1, z2 - 1, "blast_furnace[facing=north,lit=false]")
    for x in range(cx - 2, cx + 3): b.set(x, fy + 4, z2 - 3, stairs("deepslate_tile_stairs", "south", "top"))
    b.fill(cx - 1, fy + 4, z2 - 2, cx + 1, fy + 21, z2 - 1, "bricks"); b.fill(cx, fy + 5, z2 - 2, cx, fy + 21, z2 - 2, "air") if False else None
    # work places
    b.set(cx - 5, fy + 1, z2 - 5, "anvil[facing=north]"); b.set(cx - 5, fy + 1, z2 - 2, "grindstone[face=floor,facing=north]")
    b.set(cx + 5, fy + 1, z2 - 2, "smithing_table"); b.set(cx + 5, fy + 1, z2 - 5, "water_cauldron[level=3]")
    for z in range(z1 + 2, z1 + 6): b.set(cx + 5, fy + 1, z, slab("spruce_slab", "top"))          # counter right of the opening
    b.marker("smith_trader", cx + 6, fy + 1, z1 + 3); b.marker("weapon_wall", x1 + 1, fy + 2, z1 + 6, "3-4 armor stands / frames")
    for (lx, lz) in ((cx - 4, z1 + 4), (cx + 4, z2 - 4)): b.set(lx, fy + 4, lz, lantern(True))
    b.fill(x1 + 1, fy + 5, z1 + 1, x2 - 1, fy + 5, z2 - 1, "spruce_planks"); b.fill(cx - 2, fy + 5, z2 - 3, cx + 2, fy + 5, z2 - 1, "deepslate_bricks")   # 2nd floor, not near the furnace
    for i in range(4): b.set(x1 + 1, fy + 1 + i, z1 + 8 - i, stairs("spruce_stairs", "south")); b.set(x1 + 1, fy + 5, z1 + 5, "air") if False else None
    b.fill(x1 + 1, fy + 5, z1 + 4, x1 + 1, fy + 5, z1 + 7, "air")
    timber_wall(b, x1, x2, z1, z2, fy + 6, fy + 8)
    gable_roof(b, x1, x2, z1, z2, fy + 9, axis="x")
    b.set(x2 - 2, fy + 6, z1 + 2, "straw_bed[facing=south,part=head]"); b.set(x2 - 2, fy + 6, z1 + 3, "straw_bed[facing=south,part=foot]")
    b.set(x2 - 4, fy + 6, z1 + 2, "chest[facing=south]"); b.set(x2 - 5, fy + 6, z1 + 5, "spruce_fence"); b.set(x2 - 5, fy + 7, z1 + 5, "spruce_pressure_plate")
    for z in (z1 + 4, z2 - 4): b.set(x1, fy + 7, z, "glass_pane"); b.set(x2, fy + 7, z, "glass_pane")
    # yard 8x6 east of the back door: woodpile and barrels under a lean-to, smithy campfire under open sky
    yx1, yz1 = x2 + 1, z2 - 6
    b.fill(yx1, fy, yz1, yx1 + 7, fy, yz1 + 6, Mix({"cobblestone": 60, "gravel": 20, "coarse_dirt": 20}, 45))
    b.walls(yx1, fy + 1, yz1, yx1 + 7, fy + 1, yz1 + 6, "cobblestone_wall"); b.set(yx1, fy + 1, yz1 + 2, "air")
    b.fill(yx1 + 1, fy + 1, yz1 + 5, yx1 + 4, fy + 2, yz1 + 5, log("spruce_log", "x")); b.fill(yx1 + 1, fy + 3, yz1 + 4, yx1 + 4, fy + 3, yz1 + 5, slab("spruce_slab"))
    for i in range(3): b.set(yx1 + 5 + (i % 2), fy + 1, yz1 + 5 - (i // 2), "barrel[facing=up,open=false]")
    b.set(yx1 + 4, fy, yz1 + 2, "stone"); b.set(yx1 + 4, fy + 1, yz1 + 2, "campfire[lit=true,signal_fire=false]"); b.marker("smithy_campfire", yx1 + 4, fy + 1, yz1 + 2, "3 air above, open sky")
    b.set(yx1 + 6, fy + 2, yz1 + 1, lantern()); b.set(yx1 + 6, fy + 1, yz1 + 1, "cobblestone_wall")
    return b
# ------------------------------------------------------------------ tavern
def tavern():
    cx, cz, fy = TAVERN; b = B("tavern"); x1, x2, z1, z2 = cx - 8, cx + 7, cz - 9, cz + 4   # hall 16x14, facade north (board side)
    W = Mix({"cobblestone": 40, "mossy_cobblestone": 20, "stone_bricks": 20, "tuff": 10, "andesite": 10}, 51)
    b.fill(x1 - 2, fy + 1, z1 - 5, x2 + 2, fy + 22, z2 + 3, "air")
    b.fill(x1, fy, z1, x2, fy, z2, Mix({"spruce_planks": 70, "dark_oak_planks": 30}, 52))
    b.walls(x1, fy + 1, z1, x2, fy + 5, z2, W)
    DX = cx + 1                                          # front door (double), right of the order board
    b.fill(DX, fy + 1, z1, DX + 1, fy + 2, z1, "air")
    b.set(DX, fy + 1, z1, "spruce_door[facing=south,half=lower,hinge=left,open=false]"); b.set(DX, fy + 2, z1, "spruce_door[facing=south,half=upper,hinge=left,open=false]")
    b.set(DX + 1, fy + 1, z1, "spruce_door[facing=south,half=lower,hinge=right,open=false]"); b.set(DX + 1, fy + 2, z1, "spruce_door[facing=south,half=upper,hinge=right,open=false]")
    b.set(x2, fy + 1, z2 - 2, "spruce_door[facing=west,half=lower,hinge=left,open=false]"); b.set(x2, fy + 2, z2 - 2, "spruce_door[facing=west,half=upper,hinge=left,open=false]")   # kitchen back door
    for x in range(x1 + 2, x2 - 1, 3):     # warm windows
        for z in (z1, z2): b.set(x, fy + 3, z, "glass_pane")
    # order board 7x4 on the front wall left of the door, trophy shelf above, awning 9x4 over board and door
    bx1 = cx - 8 + 1
    for x in range(bx1 - 1, bx1 + 8):
        for y in range(fy + 1, fy + 6): b.set(x, y, z1, log("dark_oak_log", "x") if y in (fy + 1, fy + 5) or x in (bx1 - 1, bx1 + 7) else "spruce_planks")
    k = 0
    for row in (fy + 3, fy + 2):
        for x in range(bx1 + 1, bx1 + 6, 2):
            b.set(x, row, z1 - 1, 'dark_oak_wall_sign[facing=north]{is_waxed:1b,front_text:{messages:["",{"text":"","color":"dark_gray"},"",""]}}'); b.marker(f"order_sign_{k}", x, row, z1 - 1); k += 1
    for i, x in enumerate(range(bx1, bx1 + 7)): b.set(x, fy + 5, z1 - 1, slab("dark_oak_slab", "top"))
    for i in range(6): b.marker(f"trophy_head_{i}", bx1 + 1 + i, fy + 6, z1 - 1)
    for x in range(bx1 - 1, bx1 + 12):
        for z in range(z1 - 4, z1): b.set(x, fy + 6, z, slab("spruce_slab"))
    for x in (bx1 - 1, bx1 + 11): b.fill(x, fy + 1, z1 - 4, x, fy + 5, z1 - 4, "spruce_fence")
    b.set(bx1 + 3, fy + 5, z1 - 3, lantern(True))
    for x in range(bx1 + 1, bx1 + 5): b.set(x, fy + 1, z1 - 3, stairs("spruce_stairs", "north"))
    b.set(bx1 - 1, fy + 1, z1 - 2, "barrel[facing=up,open=false]"); b.set(bx1 - 1, fy + 1, z1 - 1, "barrel[facing=up,open=false]"); b.set(bx1, fy + 1, z1 - 1, "carved_pumpkin[facing=north]")
    # hall: hearth on the west wall, long tables, bar counter, kitchen
    b.fill(x1 + 1, fy + 1, cz - 2, x1 + 1, fy + 4, cz + 1, "stone_bricks"); b.set(x1 + 1, fy + 1, cz, "campfire[lit=true,signal_fire=false]"); b.set(x1 + 1, fy + 1, cz - 1, "campfire[lit=true,signal_fire=false]")
    b.fill(x1 + 1, fy + 2, cz - 1, x1 + 1, fy + 3, cz, "air"); b.fill(x1 + 2, fy + 4, cz - 2, x1 + 2, fy + 4, cz + 1, stairs("stone_brick_stairs", "east", "top"))
    for tz in (cz - 5, cz - 1, cz + 3):
        for x in range(x1 + 4, x1 + 8):
            b.set(x, fy + 1, tz, "spruce_fence"); b.set(x, fy + 2, tz, slab("spruce_slab", "bottom")) if False else b.set(x, fy + 2, tz, slab("spruce_slab"))
            b.set(x, fy + 1, tz - 1, stairs("spruce_stairs", "south")); b.set(x, fy + 1, tz + 1, stairs("spruce_stairs", "north"))
            if x % 2 == 0: b.set(x, fy + 3, tz, candle(2, True))
    for z in range(z1 + 2, z2 - 3): b.set(x2 - 4, fy + 1, z, "barrel[facing=up,open=false]" if z == z1 + 2 else slab("spruce_slab", "top")) if False else b.set(x2 - 4, fy + 1, z, "spruce_planks"); 
    for z in range(z1 + 2, z2 - 3): b.set(x2 - 4, fy + 2, z, slab("spruce_slab"))
    b.marker("innkeeper", x2 - 3, fy + 1, cz - 2)
    b.set(x2 - 1, fy + 1, z2 - 4, "furnace[facing=west,lit=false]"); b.set(x2 - 1, fy + 1, z2 - 5, "smoker[facing=west,lit=false]"); b.set(x2 - 2, fy + 1, z2 - 1, "cauldron")
    b.set(x2 - 1, fy + 1, z2 - 1, "barrel[facing=up,open=false]"); b.set(x2 - 1, fy + 2, z2 - 1, "barrel[facing=up,open=false]")
    for (lx, lz) in ((cx - 3, cz - 3), (cx + 2, cz + 1), (x2 - 2, z1 + 3)): b.set(lx, fy + 5, lz, lantern(True))
    b.set(cx - 5, fy + 1, z2 - 1, "lectern[facing=north,has_book=false]"); b.marker("cache_hint_note", cx - 5, fy + 1, z2 - 1, "note: 'old Hugo hid it behind the third barrel'")
    # cellar 8x8 under the hall, trapdoor behind the counter, the cache behind the 'door' barrel
    cx1, cz1, cy = cx + 1, cz - 4, fy - 5
    b.fill(cx1 - 1, cy - 1, cz1 - 1, cx1 + 8, cy + 4, cz1 + 8, "cobblestone"); b.fill(cx1, cy, cz1, cx1 + 7, cy + 3, cz1 + 7, "air")
    b.fill(cx1, cy - 1, cz1, cx1 + 7, cy - 1, cz1 + 7, Mix({"cobblestone": 60, "gravel": 25, "mossy_cobblestone": 15}, 53))
    tx, tz = x2 - 4, z1 + 2            # trapdoor hole behind the counter, ladder down
    b.fill(tx, fy, tz - 1, tx, cy + 4, tz - 1, "air")
    b.set(tx, fy, tz - 1, "spruce_trapdoor[facing=south,half=top,open=false]")
    for y in range(cy, fy): b.set(tx, y, tz - 1, "ladder[facing=south]") if b.get(tx, y, tz - 2) is not None or True else None
    b.fill(tx - 1, cy, tz - 2, tx + 1, fy - 1, tz - 2, "cobblestone")
    for i, x in enumerate(range(cx1 + 1, cx1 + 7)):     # barrel row along the far wall; the third one stands one block forward
        b.set(x, cy, cz1 + 7 - (1 if i == 2 else 0), "barrel[facing=up,open=false]")
        b.set(x, cy + 1, cz1 + 7, "barrel[facing=up,open=false]") if i % 2 == 0 else None
    dx_ = cx1 + 3; b.set(dx_, cy - 1, cz1 + 5, "mud")       # wet mud spot next to the door barrel
    b.fill(dx_, cy, cz1 + 8, dx_, cy + 1, cz1 + 8, "air"); b.set(dx_, cy, cz1 + 8, "chest[facing=north]")   # niche 1x2 with the cache chest
    b.set(dx_, cy, cz1 + 7, "air"); b.marker("cache_door_barrel", dx_, cy, cz1 + 6); b.marker("cache_chest", dx_, cy, cz1 + 8)
    b.set(cx1 + 1, cy + 2, cz1 + 1, lantern(True))
    # second floor (overhanging by 1), three rooms with straw beds, roof with dormers, chimney
    ux1, ux2, uz1, uz2 = x1 - 1, x2 + 1, z1 - 1, z2 + 1
    b.fill(ux1, fy + 6, uz1, ux2, fy + 6, uz2, "spruce_planks")
    timber_wall(b, ux1, ux2, uz1, uz2, fy + 7, fy + 10)
    for x in range(ux1 + 2, ux2 - 1, 3):
        for z in (uz1, uz2): b.set(x, fy + 8, z, "glass_pane")
    for i, rx in enumerate((ux1 + 3, cx, ux2 - 4)):
        b.set(rx, fy + 7, uz2 - 2, "straw_bed[facing=south,part=head]"); b.set(rx, fy + 7, uz2 - 3, "straw_bed[facing=south,part=foot]"); b.marker(f"tavern_bed_{i}", rx, fy + 7, uz2 - 2)
        if i < 2: b.fill(rx + 3, fy + 7, uz1 + 5, rx + 3, fy + 10, uz2 - 1, "spruce_planks")
        b.set(rx, fy + 10, uz2 - 4, lantern(True))
    for i in range(5): b.set(x1 + 2 + i, fy + 1 + i, z2 - 1, stairs("spruce_stairs", "east")); b.fill(x1 + 2 + i, fy + 6, z2 - 1, x1 + 2 + i, fy + 6, z2 - 2, "air") if i >= 2 else None
    gable_roof(b, ux1, ux2, uz1, uz2, fy + 11, axis="x")
    b.fill(x1 + 1, fy + 5, cz - 1, x1 + 1, fy + 19, cz, "cobblestone")      # chimney over the hearth
    return b
# ------------------------------------------------------------------ well yard
def well():
    cx, cz, fy = WELL; b = B("well"); y = fy
    b.fill(cx - 10, y + 1, cz - 10, cx + 10, y + 9, cz + 10, "air")
    b.fill(cx - 10, y, cz - 10, cx + 10, y, cz + 10, Mix({"cobblestone": 60, "mossy_cobblestone": 25, "gravel": 15}, 61))
    for x in range(cx - 10, cx + 11):           # neighbouring house walls on three sides, lane opening to the south-west
        for z in (cz - 10, cz + 10): b.fill(x, y + 1, z, x, y + 4, z, Mix({"cobblestone": 50, "stone_bricks": 30, "mossy_cobblestone": 20}, 62))
    for z in range(cz - 10, cz + 11):
        b.fill(cx + 10, y + 1, z, cx + 10, y + 4, z, Mix({"cobblestone": 50, "stone_bricks": 30, "mossy_cobblestone": 20}, 62))
    b.fill(cx - 10, y + 1, cz + 10, cx - 6, y + 4, cz + 10, "air"); b.fill(cx - 10, y + 1, cz - 2, cx - 10, y + 4, cz + 2, "air")
    b.fill(cx - 2, y + 1, cz - 2, cx + 2, y + 1, cz + 2, Mix({"mossy_stone_bricks": 60, "cobblestone": 40}, 63))
    b.fill(cx - 2, y + 2, cz - 2, cx + 2, y + 2, cz + 2, slab("stone_brick_slab"))
    b.fill(cx - 1, y + 2, cz - 1, cx + 1, y + 2, cz + 1, "air"); b.fill(cx - 1, y + 1, cz - 1, cx + 1, y - 18, cz + 1, "air")
    b.fill(cx - 1, y + 1, cz - 1, cx + 1, y + 1, cz + 1, "iron_bars")      # grate one block below the curb top
    b.fill(cx - 1, y - 19, cz - 1, cx + 1, y - 19, cz + 1, Mix({"stone": 60, "cobblestone": 25, "gravel": 15}, 64)); b.marker("well_bottom", cx, y - 18, cz, "shaft 3x3 to y 83")
    for dx, dz in ((-2, -2), (2, -2), (-2, 2), (2, 2)): b.fill(cx + dx, y + 2, cz + dz, cx + dx, y + 5, cz + dz, log("stripped_spruce_log"))
    for i in range(3):
        for x in range(cx - 3, cx + 4): b.set(x, y + 6 + i, cz - 3 + i, stairs("spruce_stairs", "south")); b.set(x, y + 6 + i, cz + 3 - i, stairs("spruce_stairs", "north"))
    for x in range(cx - 3, cx + 4): b.set(x, y + 9, cz, slab("spruce_slab"))
    b.fill(cx - 2, y + 5, cz, cx + 2, y + 5, cz, log("spruce_log", "x")); b.fill(cx, y + 3, cz, cx, y + 4, cz, "iron_chain")
    b.set(cx - 6, y + 1, cz - 8, stairs("spruce_stairs", "south")); b.set(cx - 5, y + 1, cz - 8, stairs("spruce_stairs", "south"))
    b.set(cx + 8, y + 1, cz + 8, "barrel[facing=up,open=false]"); b.set(cx + 8, y + 1, cz + 7, "barrel[facing=up,open=false]")
    b.set(cx - 8, y + 1, cz - 8, "cobblestone_wall"); b.set(cx - 8, y + 2, cz - 8, lantern())
    b.marker("well_swap", cx, y, cz, "21x21 yard + shaft, states before/after"); b.marker("well_trigger", cx, y + 1, cz, "sounds and cold wind")
    return b
