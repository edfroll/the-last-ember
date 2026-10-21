"""Bonfire standard (card «Стандарт костра»): circle 7x7 (main 9x9), hearth on hay in a stair bowl, stela on the north edge with the
nest, 3x3 respawn pad to the south with a lantern post, roofed nook for a straw bed beside the pad. Variants by region.
Anchor = hearth block (campfire), y = hearth y (circle floor at y-1)."""
from lib import B, Mix, stairs, slab, lantern, candle, log
VARIANTS = {
    "std":    dict(field=Mix({"stone_bricks": 60, "mossy_stone_bricks": 25, "cracked_stone_bricks": 15}, 3), ring="polished_andesite", corner="chiseled_stone_bricks",
                   bowl="stone_brick_stairs", stela=("polished_tuff", "tuff_brick_wall"), pad="cobblestone", roof=("spruce_planks", "spruce_slab"), hay=True, deco=None),
    "dol":    dict(field=Mix({"mossy_stone_bricks": 45, "stone_bricks": 30, "moss_block": 15, "pale_moss_block": 10}, 4), ring="polished_andesite", corner="chiseled_stone_bricks",
                   bowl="stone_brick_stairs", stela=("polished_tuff", "tuff_brick_wall"), pad="mossy_cobblestone", roof=("pale_oak_planks", "pale_oak_slab"), hay=True, deco="pale_moss_carpet"),
    "snow":   dict(field=Mix({"snow_block": 55, "packed_ice": 30, "stone_bricks": 15}, 5), ring="polished_diorite", corner="chiseled_stone_bricks",
                   bowl="stone_brick_stairs", stela=("calcite", "tuff_brick_wall"), pad="stone_bricks", roof=("spruce_planks", "spruce_slab"), hay=True, deco=None),
    "desert": dict(field=Mix({"smooth_sandstone": 60, "cut_red_sandstone": 40}, 6), ring="cut_sandstone", corner="chiseled_red_sandstone",
                   bowl="sandstone_stairs", stela=("cut_red_sandstone", "red_sandstone_wall"), pad="smooth_sandstone", roof=("stripped_acacia_log", "acacia_slab"), hay=True, deco=None),
    "ash":    dict(field=Mix({"polished_blackstone": 50, "basalt": 30, "polished_blackstone_bricks": 20}, 7), ring="polished_basalt", corner="chiseled_polished_blackstone",
                   bowl="polished_blackstone_stairs", stela=("polished_blackstone", "polished_blackstone_wall"), pad="polished_blackstone_bricks", roof=("crimson_planks", "crimson_slab"), hay=False, deco=None),
    "under":  dict(field=Mix({"deepslate_bricks": 60, "cracked_deepslate_bricks": 20, "deepslate_tiles": 20}, 8), ring="polished_deepslate", corner="chiseled_deepslate",
                   bowl="deepslate_brick_stairs", stela=("polished_tuff", "tuff_brick_wall"), pad="cobbled_deepslate", roof=("spruce_planks", "spruce_slab"), hay=False, deco=None),
}
def build(variant="std", r=3):
    V = VARIANTS[variant]; b = B(f"bonfire_{variant}_{r}"); y = 0
    # site: clear air above, foundation below
    b.fill(-r - 2, y, -r - 1, r + 3, y + 4, r + 4, "air")
    b.fill(-r - 1, y - 2, -r - 1, r + 1, y - 2, r + 4, "stone")
    for x in range(-r, r + 1):
        for z in range(-r, r + 1):
            edge = abs(x) == r or abs(z) == r
            b.set(x, y - 1, z, V["corner"] if abs(x) == r and abs(z) == r else (V["ring"] if edge else V["field"]))
    # hearth bowl: stairs around the hearth (half a block lower look), hay / stone under the fire
    for dx, dz, f in ((0, -1, "south"), (0, 1, "north"), (-1, 0, "east"), (1, 0, "west")): b.set(dx, y - 1, dz, stairs(V["bowl"], f))
    for dx, dz in ((-1, -1), (1, -1), (-1, 1), (1, 1)): b.set(dx, y - 1, dz, slab(V["bowl"].replace("_stairs", "_slab").replace("stone_brick_slab", "stone_brick_slab")))
    b.set(0, y - 1, 0, "hay_block" if V["hay"] else "stone")
    b.set(0, y, 0, "campfire[lit=false,signal_fire=false]")
    # stela on the north edge: base, nest (unlit chiseled_tuff / lit shroomlight), top
    b.set(0, y, -r, V["stela"][0]); b.set(0, y + 1, -r, "chiseled_tuff"); b.set(0, y + 2, -r, V["stela"][1])
    # candles on the corners
    for dx, dz in ((-r, -r), (r, -r), (-r, r), (r, r)): b.set(dx, y, dz, candle(3, False))
    # respawn pad 3x3 to the south, lantern post, roofed nook for the straw bed east of the pad
    pz = r + 2
    b.fill(-1, y - 1, pz - 1, 1, y - 1, pz + 1, V["pad"])
    b.set(-2, y - 1, pz, V["pad"]); b.set(-2, y, pz, "spruce_fence"); b.set(-2, y + 1, pz, lantern())
    b.fill(2, y - 1, pz - 1, 3, y - 1, pz + 1, V["pad"])
    for cx, cz in ((3, pz - 1), (3, pz + 1)): b.fill(cx, y, cz, cx, y + 1, cz, "spruce_fence")
    b.fill(2, y + 2, pz - 1, 3, y + 2, pz + 1, slab(V["roof"][1]) if "log" not in V["roof"][1] else V["roof"][1])
    if V["deco"]:
        for dx, dz in ((-r + 1, -r + 1), (r - 1, r - 2), (-r + 1, r - 1)): b.set(dx, y, dz, V["deco"])
    b.marker("hearth", 0, y, 0); b.marker("stela_nest", 0, y + 1, -r); b.marker("respawn", 0, y, pz); b.marker("straw_bed", 2, y, pz)
    return b
