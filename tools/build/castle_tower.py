"""T-034: the Locked Tower (Запертая башня, Р1, card 5.3) inside the step of the castle (called from castle_keep.tower()).

HQ T-034, 4: the tower of T-029 (TOWER = (471, 32, 483, 44), the window of the third tier on the north face x 477, y P+24, the door from
the castle bricked up, the inside empty) keeps all that. Added:
  - the room 11 x 11 on the tier of the window: the floor P+23, the ceiling P+30 (air 6), cobwebs, broken dark oak furniture, torn
    tapestries (wall banners; one torn down on the floor before the niche), the niche in a thickened south wall with the chest and its
    lock (a broken piece of the masonry: cracked stone bricks over it); no light of its own (the window only; the datapack hangs a soul
    lantern in the window at night);
  - the ledges: from the barbican (the table's strip before its east side, z 29) east along the north edge of the table on the ruins of
    an old gallery wall (z 29, 1 wide), round the corner past the tower (x 487) and west along the tower's north face (z 31, on corbels)
    to the window: 23 stairs, 3 jumps over a gap of 1 (a flat cell to run and to land), iron chains on posts along the edge over the rift
    (not a solid wall; none at the gaps).
Points go to server/build/r1/tower.json (the datapack, the tests, the bot); the vault line r1_tower."""
import json, os
from lib import Mix, h as hsh
import castle_layout as L
from castle_build import st, AIR

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = L.P
FLOOR_Y = P + 23; CEIL_Y = P + 30
ROOM = (472, 33, 482, 43)                       # inside the tower walls
WINDOW = (477, P + 24, 32)
RUIN = Mix({"mossy_stone_bricks": 34, "stone_bricks": 22, "cracked_stone_bricks": 22, "tuff_bricks": 12, "mossy_cobblestone": 10}, 3401)
WALK = Mix({"stone_bricks": 40, "mossy_stone_bricks": 30, "cracked_stone_bricks": 20, "tuff_bricks": 10}, 3402)
STEP = Mix({"stone_brick_stairs": 55, "mossy_stone_brick_stairs": 25, "tuff_brick_stairs": 20}, 3403)
TFLOOR = Mix({"dark_oak_planks": 50, "stone_bricks": 25, "cracked_stone_bricks": 15, "mossy_stone_bricks": 10}, 3404)
CHAIN_X = "minecraft:iron_chain[axis=x,waterlogged=false]"
CHAIN_Z = "minecraft:iron_chain[axis=z,waterlogged=false]"
POST = "minecraft:stone_brick_wall"

# the way along the ledges: (x, z, kind, feet after the cell, facing of a stair); kinds: stair, flat, gap
def ledge_cells():
    out = []; f = P + 1                          # the feet on the table (166 + 1)
    def add(x, z, kind, face=None):
        nonlocal f
        if kind == "stair": f += 1
        out.append(dict(x=x, z=z, kind=kind, f=f, face=face))
    for x in range(460, 470): add(x, 29, "stair", "east")             # 10 stairs: 168 .. 177
    add(470, 29, "flat"); add(471, 29, "gap"); add(472, 29, "flat")
    for x in range(473, 482): add(x, 29, "stair", "east")             # 9: .. 186
    add(482, 29, "flat"); add(483, 29, "gap"); add(484, 29, "flat")   # 483: the natural notch of the cliff
    for x in (485, 486): add(x, 29, "stair", "east")                  # .. 188
    add(487, 29, "flat")
    add(487, 30, "stair", "south"); add(487, 31, "flat")              # 189
    add(486, 31, "stair", "west")                                     # 190
    add(485, 31, "flat"); add(484, 31, "gap")
    for x in range(483, 476, -1): add(x, 31, "flat")                  # 483 .. 477 at 190: the window at x 477 (z 32)
    assert out[-1]["f"] == WINDOW[1] and out[-1]["x"] == WINDOW[0], out[-1]
    return out


def ledges(k):
    cells = ledge_cells()
    occ = {(c["x"], c["z"]) for c in cells}
    for c in cells:
        x, z, f = c["x"], c["z"], c["f"]
        if c["kind"] == "gap":
            prev = cells[cells.index(c) - 1]["f"]
            for y in range(prev - 6, prev + 3): k.set(x, y, z, AIR)          # broken: open far down (the table / the rift under it)
            k.set(x, prev - 7, z, RUIN.at(x, prev - 7, z)) if z == 29 and x != 483 else None
            continue
        if c["kind"] == "stair":
            k.set(x, f - 1, z, st(STEP.at(x, f, z).replace("minecraft:", ""), facing=c["face"], half="bottom", shape="straight", waterlogged="false"))
        else: k.set(x, f - 1, z, WALK.at(x, f - 1, z))
        for y in range(f, f + 3): k.set(x, y, z, AIR)
        # the support: the old wall from the table up (holes in it), or corbels on the tower's face
        if z == 31 and x <= L.TOWER[2]:
            k.set(x, f - 2, z, st("stone_brick_stairs", facing="south", half="top", shape="straight", waterlogged="false"))
        else:
            for y in range(P + 1, f - 1):
                k.set(x, y, z, AIR if (hsh(x, y, z, 3405) < 0.16 and f - 1 - y > 2 and y > P + 2) else RUIN.at(x, y, z))
    # the rail: posts (stone brick wall) every third cell on the outer side, chains between them at the feet; none beside the gaps
    gaps = [(c["x"], c["z"]) for c in cells if c["kind"] == "gap"]
    def near_gap(x, z): return any(abs(x - gx) + abs(z - gz) <= 1 for (gx, gz) in gaps)
    for i, c in enumerate(cells):
        if c["kind"] == "gap" or near_gap(c["x"], c["z"]): continue
        x, z, f = c["x"], c["z"], c["f"]
        if z == 29 and x <= 486: ox, oz, ch = x, 28, CHAIN_X
        elif z == 31 and x <= 485: ox, oz, ch = x, 30, CHAIN_X
        elif x == 487: ox, oz, ch = 488, z, CHAIN_Z
        else: continue
        if (ox, oz) in occ: continue
        if i % 3 == 0:
            k.set(ox, f, oz, POST); k.set(ox, f + 1, oz, POST)
            k.set(ox, f - 1, oz, st("stone_brick_stairs", facing={28: "south", 30: "south"}.get(oz, "west"), half="top", shape="straight", waterlogged="false"))
        else: k.set(ox, f, oz, ch)
    return cells


def room(k):
    """the floor, the ceiling, the thickened south wall with the niche and the chest, the decor"""
    x1, z1, x2, z2 = ROOM
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            k.set(x, FLOOR_Y, z, TFLOOR.at(x, FLOOR_Y, z))
            k.set(x, CEIL_Y, z, "minecraft:dark_oak_planks" if (x + z) % 4 else st("stripped_dark_oak_log", axis="x"))
            for y in range(FLOOR_Y + 1, CEIL_Y): k.set(x, y, z, AIR)
    # the niche: the south wall thickened by one (z 43, x 474..480), the chest at x 477 behind the torn tapestry, its lock over it
    for x in range(474, 481):
        for y in range(FLOOR_Y + 1, CEIL_Y): k.wall(x, y, 43)
    cx, cy, cz = 477, FLOOR_Y + 1, 43
    k.set(cx, cy, cz, 'minecraft:chest[facing=north,type=single,waterlogged=false]{LootTable:"last_ember:vault/r1_tower"}')
    k.set(cx, cy + 1, cz, "minecraft:cracked_stone_bricks")
    for (x, z) in ((476, 42), (477, 41), (478, 42), (476, 41)):
        k.set(x, FLOOR_Y + 1, z, "minecraft:purple_carpet")                      # the tapestry torn down, on the floor before the niche
    k.set(478, FLOOR_Y + 3, 42, st("purple_wall_banner", facing="north"))       # a rag of it still hanging beside the niche
    # tapestries on the other walls (wall banners), some torn (a lone one high, one low)
    for (x, y, z, f, c) in ((472, FLOOR_Y + 3, 37, "east", "black"), (472, FLOOR_Y + 2, 40, "east", "gray"), (482, FLOOR_Y + 3, 36, "west", "purple"),
                            (482, FLOOR_Y + 4, 40, "west", "black"), (474, FLOOR_Y + 3, 33, "south", "gray")):
        k.set(x, y, z, st("%s_wall_banner" % c, facing=f))
    # broken furniture: a table fallen on its side (slabs, a fence leg), a chair tipped over, boards, a cupboard's door
    for (x, y, z, s) in ((474, 1, 39, st("dark_oak_slab", type="bottom", waterlogged="false")), (475, 1, 39, st("dark_oak_slab", type="top", waterlogged="false")),
                         (474, 2, 39, "minecraft:dark_oak_fence"), (480, 1, 37, st("dark_oak_stairs", facing="east", half="top", shape="straight", waterlogged="false")),
                         (481, 1, 41, st("dark_oak_trapdoor", facing="west", half="bottom", open="true", powered="false", waterlogged="false")),
                         (473, 1, 42, st("dark_oak_stairs", facing="south", half="bottom", shape="straight", waterlogged="false")),
                         (481, 1, 34, "minecraft:dark_oak_fence"), (480, 1, 34, st("dark_oak_slab", type="bottom", waterlogged="false"))):
        k.set(x, FLOOR_Y + y, z, s)
    # cobwebs: the corners and high up (not on the way from the window to the niche)
    way = {(477, z) for z in range(33, 43)} | {(476, z) for z in range(33, 43)} | {(478, z) for z in range(33, 43)}
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            for y in range(FLOOR_Y + 1, CEIL_Y):
                if k.get(x, y, z) not in (None, AIR) or (x, z) in way and y <= FLOOR_Y + 3: continue
                edge = (x in (x1, x2)) + (z in (z1, z2))
                hi = y >= CEIL_Y - 2
                r = hsh(x, y, z, 3406)
                if (edge == 2 and r < 0.55) or (hi and edge and r < 0.3) or (hi and r < 0.07) or (edge and y == FLOOR_Y + 1 and r < 0.08):
                    k.set(x, y, z, "minecraft:cobweb")
    return dict(chest=[cx, cy, cz], lock=[cx, cy + 1, cz], lock_block="minecraft:cracked_stone_bricks", room=[x1, FLOOR_Y + 1, z1, x2, CEIL_Y - 1, z2],
                rest=[477.5, FLOOR_Y + 2.0, 40.5], lantern=[WINDOW[0], WINDOW[1] + 3, WINDOW[2]], window=list(WINDOW), floor=FLOOR_Y)


def build(k):
    m = room(k)
    cells = ledges(k)
    m["ledges"] = cells
    m["start"] = [458.5, P + 1, 29.5]
    json.dump(m, open(os.path.join(ROOT, "server/build/r1/tower.json"), "w"))
    from r1 import replace_lines
    replace_lines(os.path.join(ROOT, "treasury/vaults.txt"), ["vault r1_tower "],
                  ["vault r1_tower r1 overworld %d %d %d block=chest[facing=north] build=0   # T-034: the Locked Tower, the niche behind the torn tapestry" % tuple(m["chest"])])
    k.meta["tower_t034"] = m
    import treasury_dp
    treasury_dp.run_tower(m)
    return m
