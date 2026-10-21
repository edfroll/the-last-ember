"""Urn of the Lost (card «Урна Утраченного»): podium 7x7 with three steps on the front (+z, towards the bonfire), urn: base 3x3,
belly 5x5 with cut corners (3 high), neck 3x3 with ash, two bands, bowl (cauldron) at the front, name plate at the back.
Anchor = podium centre at square level (players stand at y; podium occupies y)."""
from lib import B, Mix, stairs, candle
VARIANTS = {
    "r0": dict(body=Mix({"deepslate_tiles": 40, "polished_deepslate": 30, "cracked_deepslate_tiles": 20, "chiseled_deepslate": 10}, 11), band="waxed_oxidized_cut_copper", podium="polished_deepslate", step="deepslate_tile_stairs"),
    "r2": dict(body=Mix({"prismarine_bricks": 60, "dark_prismarine": 25, "prismarine": 15}, 12), band="polished_blackstone", podium="dark_prismarine", step="prismarine_brick_stairs"),
    "r3": dict(body=Mix({"calcite": 70, "packed_ice": 30}, 13), band="polished_blackstone", podium="polished_diorite", step="polished_diorite_stairs"),
    "r4": dict(body=Mix({"cut_red_sandstone": 70, "smooth_red_sandstone": 30}, 14), band="polished_blackstone", podium="cut_red_sandstone", step="red_sandstone_stairs"),
    "r5": dict(body=Mix({"deepslate": 50, "deepslate_tiles": 35, "sculk": 15}, 15), band="polished_blackstone", podium="polished_deepslate", step="deepslate_tile_stairs"),
    "r6": dict(body=Mix({"blackstone": 50, "basalt": 30, "polished_blackstone_bricks": 20}, 16), band="polished_blackstone", podium="polished_blackstone", step="polished_blackstone_stairs"),
}
def build(v="r0"):
    V = VARIANTS[v]; b = B(f"urn_{v}"); y = 0
    b.fill(-3, y, -3, 3, y + 7, 4, "air")
    b.fill(-3, y - 1, -3, 3, y - 1, 3, V["podium"])
    b.fill(-3, y, -3, 3, y, 3, V["podium"])
    for x in (-1, 0, 1): b.set(x, y, 4, stairs(V["step"], "north"))
    b.fill(-1, y + 1, -1, 1, y + 1, 1, V["body"])
    for yy in (y + 2, y + 3, y + 4):
        for x in range(-2, 3):
            for z in range(-2, 3):
                if abs(x) == 2 and abs(z) == 2: continue
                b.set(x, yy, z, V["band"] if yy in (y + 2, y + 4) and (abs(x) == 2 or abs(z) == 2) else V["body"])
    b.fill(-1, y + 5, -1, 1, y + 5, 1, V["body"])
    b.set(0, y + 5, 0, "light_gray_concrete_powder"); b.set(0, y + 6, 0, "gray_carpet")
    for dx, dz in ((-1, -1), (1, -1), (-1, 1), (1, 1)): b.set(dx, y + 6, dz, candle(1, False))
    b.set(0, y + 1, 3, "cauldron")
    b.fill(-1, y + 1, -3, 1, y + 2, -3, "polished_deepslate"); b.set(0, y + 3, -3, "polished_deepslate_slab")
    b.marker("urn_neck", 0, y + 5, 0); b.marker("bowl", 0, y + 1, 3); b.marker("plate", 0, y + 2, -3)
    return b
