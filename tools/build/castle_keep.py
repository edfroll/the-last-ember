"""T-029: the block model of the Enchanted Castle on the table of T-028 (layout: tools/build/castle_layout.py): the court with its arcades
and galleries, the west wing (chapel, library with the riddle wall), the east wing (kitchens with the pantry, armoury), the north tower
(shell), the keep (the vestibule with bonfire 11, the stair annex, the throne hall with its columns, gallery, guard niches, throne and
windows, the reliquary), the gaol and the crypt under the west wing, the secret way (the spiral from the reliquary, the tunnel under the
rift, the door in the rock over the pier). Everything here is offline blocks (tools/blockwriter.sh apply); entities (armour stands, the
king, the displays of the mechanics) are the datapack's. Returns the points for the datapack, the bot and the tests (meta["keep"]).

Changeable states are templates (structure/castle/k_*.nbt, written by r1_castle.nbt): the gate of the barbican (closed / open), the gaol
door, the two doors of the hall, the three guard niches, the reliquary door, the pier door (rock / open with the portcullis raised), the
throne before / after (the sword and the crown left on it)."""
import math
from lib import Mix, h as hsh
import castle_layout as L
import castle_build as CB
import castle_plan as PL
from castle_build import st, stairs, slab, lantern, sign_nbt, AIR

P = L.P
WALL_LO = Mix({"stone_bricks": 24, "tuff_bricks": 16, "mossy_stone_bricks": 30, "andesite": 13, "cracked_stone_bricks": 5, "polished_tuff": 12}, 2900)
WALL_MID = CB.CASTLE
WALL_HI = Mix({"stone_bricks": 30, "tuff_bricks": 20, "mossy_stone_bricks": 4, "andesite": 16, "cracked_stone_bricks": 20, "polished_tuff": 10}, 2901)
FLOOR = Mix({"stone_bricks": 5, "cobblestone": 2, "mossy_stone_bricks": 2, "cracked_stone_bricks": 1}, 2902)
COURT = Mix({"cobblestone": 4, "mossy_cobblestone": 3, "stone_bricks": 2, "gravel": 1, "coarse_dirt": 1}, 2903)
DUNG = Mix({"cobbled_deepslate": 5, "deepslate_bricks": 3, "cracked_deepslate_bricks": 2, "tuff": 1}, 2904)
ROOF_ST, ROOF_SL, ROOF_FULL = "deepslate_tile_stairs", "deepslate_tile_slab", "minecraft:deepslate_tiles"
PLANK = "minecraft:dark_oak_planks"
BEAM_X, BEAM_Z, BEAM_Y = st("stripped_dark_oak_log", axis="x"), st("stripped_dark_oak_log", axis="z"), st("stripped_dark_oak_log", axis="y")


def wall_at(x, y, z):
    """the castle walls: lighter than the rock, more moss low, more cracks high (the card)"""
    return (WALL_LO if y <= P + 4 else WALL_HI if y >= P + 24 else WALL_MID).at(x, y, z)


def is_air(s): return s is None or s == AIR


class K:
    """the builder: b = lib.B of the place; walls/rooms keep a set of the cells that must stay air"""
    def __init__(self, b):
        self.b = b; self.meta = {}; self.tpl = {}; self.walk = []

    def set(self, x, y, z, s): self.b.set(x, y, z, s)
    def get(self, x, y, z): return self.b.get(x, y, z)
    def wall(self, x, y, z): self.b.set(x, y, z, wall_at(x, y, z))
    def fill(self, x1, y1, z1, x2, y2, z2, s):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.b.set(x, y, z, wall_at(x, y, z) if s == "W" else s.at(x, y, z) if isinstance(s, Mix) else s)
    def air(self, x1, y1, z1, x2, y2, z2): self.fill(x1, y1, z1, x2, y2, z2, AIR)

    def shell(self, r, y1, y2, floor=FLOOR, ceil=True):
        """walls of the box r from y1 to y2, the floor at y1 - 1 inside, air inside, the ceiling at y2 + 1 (stone)"""
        x1, z1, x2, z2 = r
        for y in range(y1 - 1, y2 + 2):
            for x in range(x1, x2 + 1):
                for z in range(z1, z2 + 1):
                    edge = x in (x1, x2) or z in (z1, z2)
                    if edge or y == y2 + 1 and ceil: self.wall(x, y, z)
                    elif y == y1 - 1: self.set(x, y, z, floor.at(x, y, z) if isinstance(floor, Mix) else floor)
                    elif y <= y2: self.set(x, y, z, AIR)

    def hip_roof(self, r, y, overhang=1, spire=False):
        """a stepped hip roof (the card: cones of deepslate tile stairs and slabs) over the box r from level y; spire: copper + rod"""
        x1, z1, x2, z2 = r[0] - overhang, r[1] - overhang, r[2] + overhang, r[3] + overhang
        k = 0
        while x1 + k <= x2 - k and z1 + k <= z2 - k:
            a, b_, c, d = x1 + k, z1 + k, x2 - k, z2 - k; yy = y + k
            for x in range(a, c + 1):
                for z in range(b_, d + 1):
                    if a < x < c and b_ < z < d: continue
                    corner = (x in (a, c)) and (z in (b_, d))
                    if a == c or b_ == d: self.set(x, yy, z, slab(ROOF_SL)); continue
                    if corner: self.set(x, yy, z, ROOF_FULL); continue
                    f = "south" if z == b_ else "north" if z == d else "east" if x == a else "west"
                    self.set(x, yy, z, stairs(ROOF_ST, f))
            # under the ring: full tiles (the roof is solid, no holes when seen from below the eaves)
            if k > 0:
                for x in range(a, c + 1):
                    for z in range(b_, d + 1):
                        if x in (a, c) or z in (b_, d): self.set(x, yy - 1, z, ROOF_FULL) if is_air(self.get(x, yy - 1, z)) else None
            k += 1
        top = y + k
        if spire:
            cx, cz = (r[0] + r[2]) // 2, (r[1] + r[3]) // 2
            for yy in range(top - 1, top + 3): self.set(cx, yy, cz, "minecraft:oxidized_cut_copper")
            self.set(cx, top + 3, cz, "minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]")
            top += 4
        return top

    def crenel(self, cells, y):
        for (x, z) in cells:
            if (x + z) % 2 == 0: self.wall(x, y, z)

    def window(self, x, y1, y2, z, kind="bars"):
        for y in range(y1, y2 + 1): self.set(x, y, z, "minecraft:iron_bars" if kind == "bars" else "minecraft:tinted_glass" if kind == "tinted" else kind)


def edge_cells(r):
    x1, z1, x2, z2 = r
    return [(x, z) for x in range(x1, x2 + 1) for z in range(z1, z2 + 1) if x in (x1, x2) or z in (z1, z2)]


def book(title, author, pages, extra=""):
    pg = ",".join('{raw:"%s"}' % p.replace('"', '\\"') for p in pages)
    return '{id:"minecraft:written_book",count:1,components:{"minecraft:written_book_content":{title:{raw:"%s"},author:"%s",pages:[%s]}%s}}' % (title, author, pg, extra)


def lectern_with(facing, bk): return st("lectern", facing=facing, has_book="true", powered="false") + "{Book:%s}" % bk
def sign(x, y, z, k, lines, facing, wall=True):
    s = (st("dark_oak_wall_sign", facing=facing, waterlogged="false") if wall else st("dark_oak_sign", rotation=str({"south": 0, "west": 4, "north": 8, "east": 12}[facing]), waterlogged="false")) + sign_nbt(lines)
    k.set(x, y, z, s)


# ================================================================ texts (HQ T-029, 5)
RIDDLE = ["Год Дома шёл за солнцем.\\nВесна вставала там, где встаёт оно.\\nЛето стояло там, где оно в полдень.\\nОсень ложилась туда, где оно ложится.\\nЗима не пришла. Не ищи ей места."]
TOWER_NOTE = ["В северную башню больше никто не ходит."]
PRISONER = ["Меня заперли за то, что я не лёг. Все спят, а я считаю дни по капле. Если найдёте короля — не будите. Он проснётся не добрым."]
VOLUMES = {   # key: (title, pages) -- the tomes of the chronicle, author «летописец Дома» (quest items: castle_keep_dp gives them the custom_data)
    "spring": ("Весна", ["Каменные короли донесли огонь до воды и встали. Дальше им было не дойти. Огонь взял наш король. Ему надели корону, и Дол зазеленел.",
                         "Говорят, короли у воды помнят каждую руку, что держала огонь. Чужую руку они не пустят."]),
    "summer": ("Лето", ["Сорок лет огонь горел в донжоне. Мы пекли хлеб на его углях и не знали голода.",
                        "Рыцари Ясеня стерегли дорогу. Магистр клялся королю: я буду стоять, пока стоит огонь."]),
    "autumn": ("Осень", ["Огонь стал меньше. Король носил его к каждой свече, но свечи гасли.",
                         "Король сказал: я не понесу его дальше. Я усну, пока огонь не вернётся, и Дом уснёт со мной. Кто придёт с огнём — разбудит.",
                         "Мы легли. Последнее, что я помню, — лиловый свет в витражах."]),
    "winter": ("Зима", ["…", "", ""]),
}
CHRON = "летописец Дома"


def volume_book(key, gen=1):
    t, pages = VOLUMES[key]
    return book(t, CHRON, pages, ',"minecraft:custom_data":{le_citem:"vol_%s",le_keep:1b,gen:%d}' % (key, gen))


# ================================================================ the court, the curtain, the galleries
def court(k, gr, rl):
    x1, z1, x2, z2 = L.COURT
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            k.set(x, P, z, CB.COURT.at(x, P, z) if hasattr(CB, "COURT") else COURT.at(x, P, z))
            for y in range(P + 1, P + 8): k.set(x, y, z, AIR)
    # the curtain on the north edge (z 39) west and east of the barbican, 2 thick, crenellated, P+12
    for x in list(range(437, 444)) + list(range(459, 467)):
        for z in (38, 39):
            for y in range(P, P + 13): k.wall(x, y, z)
        k.crenel([(x, 38)], P + 13)
    # the dry well
    wx, wz = 444, 47
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            r = max(abs(dx), abs(dz))
            if r == 2: k.set(wx + dx, P + 1, wz + dz, "minecraft:stone_bricks" if (dx + dz) % 2 else "minecraft:mossy_stone_bricks")
            elif r <= 1:
                for y in range(P - 6, P + 1): k.set(wx + dx, y, wz + dz, AIR)
                k.set(wx + dx, P - 7, wz + dz, "minecraft:coarse_dirt")
                for y in range(P - 6, P + 1):
                    for (a, c) in ((2, 0), (-2, 0), (0, 2), (0, -2)):
                        pass
    for y in range(P - 7, P + 1):
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                if max(abs(dx), abs(dz)) == 2 and y < P + 1: k.set(wx + dx, y, wz + dz, "minecraft:stone_bricks")
    k.set(wx, P - 6, wz, "minecraft:cobweb"); k.set(wx - 1, P - 6, wz + 1, "minecraft:bone_block[axis=x]")
    for (dx, dz) in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
        for y in (P + 2, P + 3): k.set(wx + dx, y, wz + dz, "minecraft:dark_oak_fence")
    for dx in range(-2, 3):
        for dz in (-2, 2): k.set(wx + dx, P + 4, wz + dz, slab("dark_oak_slab"))
    for dz in range(-1, 2):
        for dx in (-2, 2): k.set(wx + dx, P + 4, wz + dz, slab("dark_oak_slab"))
    k.set(wx, P + 3, wz, "minecraft:iron_chain[axis=y,waterlogged=false]")
    # two broken carts
    for (cx, cz, ax) in ((456, 44, "x"), (460, 50, "z")):
        for d in range(3):
            x, z = (cx + d, cz) if ax == "x" else (cx, cz + d)
            k.set(x, P + 1, z, slab("dark_oak_slab", "top") if d < 2 else slab("dark_oak_slab"))
        wx_, wz_ = (cx, cz + 1) if ax == "x" else (cx + 1, cz)
        k.set(wx_, P + 1, wz_, st("dark_oak_trapdoor", facing="north" if ax == "x" else "west", half="bottom", open="true", powered="false", waterlogged="false"))
        k.set(cx + (3 if ax == "x" else 0), P + 1, cz + (0 if ax == "x" else 3), "minecraft:barrel[facing=up,open=false]")
    # the dry tree (a dead dark oak: trunk and bare branches)
    tx, tz = 440, 51
    for y in range(P + 1, P + 7): k.set(tx, y, tz, "minecraft:dark_oak_log[axis=y]")
    for (dx, dy, dz, a) in ((1, 5, 0, "x"), (2, 6, 0, "x"), (-1, 4, 0, "x"), (0, 6, 1, "z"), (0, 7, 2, "z"), (0, 5, -1, "z")):
        k.set(tx + dx, P + dy, tz + dz, "minecraft:dark_oak_log[axis=%s]" % a)
    k.set(tx + 1, P + 1, tz, "minecraft:dead_bush"); k.set(tx - 1, P + 1, tz + 1, "minecraft:dead_bush")
    k.meta["well"] = [wx, P + 1, wz]


def galleries(k):
    """the arcades on the ground and the covered galleries over them (floor GAL, air GAL+1..GAL+4, roof GAL+5..+6) on the west, south and
    east sides of the court, the south one running on to the stair annex; windows to the court (iron bars, tinted glass), banners inside"""
    cor = set()
    for x in range(434, 437):
        for z in range(40, 58): cor.add((x, z))
    for x in range(423, 470):
        for z in range(55, 58): cor.add((x, z))
    for x in range(467, 470):
        for z in range(40, 58): cor.add((x, z))
    walls = set()
    for (x, z) in cor:
        for a in (-1, 0, 1):
            for c in (-1, 0, 1):
                q = (x + a, z + c)
                if q not in cor: walls.add(q)
    G = L.GAL
    court_side = lambda q: L.COURT_OPEN[0] - 1 <= q[0] <= L.COURT_OPEN[2] + 1 and L.COURT_OPEN[1] <= q[1] <= L.COURT_OPEN[3] + 1
    for (x, z) in cor:
        k.set(x, G, z, PLANK if (x + z) % 5 else BEAM_X)
        for y in range(G + 1, G + 5): k.set(x, y, z, AIR)
        k.set(x, G + 5, z, PLANK); k.set(x, G - 1, z, BEAM_Z if 434 <= x <= 436 or x >= 467 else BEAM_X)
    for (x, z) in walls:
        for y in range(G, G + 6):
            if is_air(k.get(x, y, z)) or k.get(x, y, z) is None: k.wall(x, y, z)
        k.crenel([(x, z)], G + 7); k.wall(x, G + 6, z)
    # roofs: a lean-to of slabs over each gallery (G + 6 .. G + 7)
    for (x, z) in cor:
        k.set(x, G + 6, z, ROOF_FULL); k.set(x, G + 7, z, slab(ROOF_SL))
    # windows to the court: every 3rd cell of the court-side wall, 2 high
    win = []
    for (x, z) in sorted(walls):
        if court_side((x, z)) and (x + z) % 3 == 0:
            for y in (G + 2, G + 3): k.set(x, y, z, "minecraft:iron_bars" if (x + z) % 2 else "minecraft:tinted_glass")
            win.append((x, z))
    # the arcade under the galleries: piers every 4 on the court side, open arches between (ground walkable under the gallery)
    for (x, z) in walls:
        if not court_side((x, z)): continue
        pier = (x % 4 == 0) if z in (54, 58) else (z % 4 == 0)
        for y in range(P + 1, G):
            if pier: k.wall(x, y, z)
            elif y >= G - 1: k.set(x, y, z, stairs("stone_brick_stairs", "north" if z in (54,) else "south" if z == 58 else "west" if x == 437 else "east", "top"))
            else: k.set(x, y, z, AIR)
    for (x, z) in cor:
        k.set(x, P, z, FLOOR.at(x, P, z))
        for y in range(P + 1, G - 1): k.set(x, y, z, AIR)
    # tapestries (banners) on the inner walls of the galleries
    ban = []
    for (x, z, f, c) in ((433, 44, "east", "purple"), (433, 50, "east", "gray"), (470, 44, "west", "purple"), (470, 50, "west", "gray"),
                         (440, 58, "north", "purple"), (452, 58, "north", "black"), (462, 58, "north", "purple")):
        k.set(x, G + 3, z, st("%s_wall_banner" % c, facing=f)); ban.append((x, G + 3, z))
    k.meta["gallery_banners"] = ban
    k.meta["gallery_cells"] = len(cor)
    return cor


# ================================================================ west wing: chapel, library
def chapel(k):
    r = L.CHAPEL; x1, z1, x2, z2 = r; top = P + 12
    k.shell(r, P + 1, top)
    k.hip_roof(r, top + 2)
    for (x, z) in edge_cells(r): k.wall(x, top + 1, z)
    # door from the arcade (east wall x 433, z 45..47) on the ground; the door to the library (south wall, x 414..416)
    k.air(x2, P + 1, 45, x2, P + 3, 47)
    k.air(414, P + 1, z2, 416, P + 3, z2)
    # benches (dark oak stairs facing the altar in the west), the aisle z 45..47
    for x in range(412, 428, 2):
        for z in list(range(43, 45)) + list(range(48, 51)):
            if z < 45 and x > 418: continue
            k.set(x, P + 1, z, stairs("dark_oak_stairs", "east"))
    # the altar at the west end, the stained window over it, candles
    ax = x1 + 2
    for z in range(44, 49): k.set(ax, P + 1, z, "minecraft:polished_deepslate")
    k.set(ax, P + 2, 44, "minecraft:candle[candles=3,lit=false,waterlogged=false]"); k.set(ax, P + 2, 48, "minecraft:candle[candles=2,lit=false,waterlogged=false]")
    k.set(ax + 1, P + 1, 46, lectern_with("east", volume_book("spring")))
    k.meta["lectern_spring"] = [ax + 1, P + 1, 46]
    for y in range(P + 4, P + 11):
        for z in range(44, 49):
            k.set(x1, y, z, "minecraft:purple_stained_glass" if (y + z) % 3 else "minecraft:cyan_stained_glass")
    for z in (42, 50):
        for x in (420, 426): k.set(x, P + 1, z, "minecraft:candle[candles=4,lit=false,waterlogged=false]") if is_air(k.get(x, P + 1, z)) else None
    # the choir loft at the east end (P+8, x 429..432) with its stair, the door into the west gallery
    G = L.GAL
    for x in range(429, 433):
        for z in range(z1 + 1, z2):
            k.set(x, G, z, PLANK)
    for z in range(z1 + 1, z2): k.set(428, G + 1, z, "minecraft:dark_oak_fence")
    for i in range(8):      # the stair on the north side, rising east x 421 -> 428, z 40..42 (P+1..P+8)
        x = 421 + i
        for z in range(40, 43):
            k.set(x, P + 1 + i, z, stairs("dark_oak_stairs", "east")); k.set(x, P + i, z, PLANK) if i else None
            for y in range(P + 2 + i, P + 6 + i): k.set(x, y, z, AIR)
    for z in range(40, 43):
        for x in range(421, 429): pass
    k.set(428, G + 1, 41, AIR); k.set(428, G + 1, 40, AIR); k.set(428, G + 1, 42, AIR)
    for z in range(40, 43):
        k.set(429, G, z, PLANK)
    k.air(x2, G + 1, 45, x2, G + 3, 47)
    k.meta["chapel_door"] = [x2, P + 1, 46]


def riddle_shelf(facing, empty_slot):
    occ = {i: i != empty_slot for i in range(6)}
    props = dict(facing=facing, **{"slot_%d_occupied" % i: "true" if occ[i] else "false" for i in range(6)})
    items = ",".join('{Slot:%db,id:"minecraft:book",count:1}' % i for i in range(6) if occ[i])
    return st("chiseled_bookshelf", **props) + "{Items:[%s]}" % items


def library(k):
    r = L.LIBRARY; x1, z1, x2, z2 = r; top = P + 12; G = L.GAL
    k.shell(r, P + 1, top)
    k.hip_roof(r, top + 2)
    for (x, z) in edge_cells(r): k.wall(x, top + 1, z)
    ix1, iz1, ix2, iz2 = L.inside(r)
    # the balcony on all four sides (3 wide, floor G) on beams, a parapet of dark oak fence, 2 lanterns? no: dark (spawn)
    for x in range(ix1, ix2 + 1):
        for z in range(iz1, iz2 + 1):
            if x <= ix1 + 2 or x >= ix2 - 2 or z <= iz1 + 2 or z >= iz2 - 2:
                k.set(x, G, z, PLANK if (x + z) % 4 else BEAM_X)
            inner = ix1 + 3 <= x <= ix2 - 3 and iz1 + 3 <= z <= iz2 - 3
            on_rim = (x in (ix1 + 3, ix2 - 3) and iz1 + 3 <= z <= iz2 - 3) or (z in (iz1 + 3, iz2 - 3) and ix1 + 3 <= x <= ix2 - 3)
            if not inner:
                pass
    for x in range(ix1 + 3, ix2 - 2):
        for z in (iz1 + 2, iz2 - 2): k.set(x, G + 1, z, "minecraft:dark_oak_fence")
    for z in range(iz1 + 3, iz2 - 2):
        for x in (ix1 + 2, ix2 - 2): k.set(x, G + 1, z, "minecraft:dark_oak_fence")
    # posts under the balcony edge
    for (x, z) in ((ix1 + 2, iz1 + 2), (ix2 - 2, iz1 + 2), (ix1 + 2, iz2 - 2), (ix2 - 2, iz2 - 2), (ix1 + 2, 69), (ix2 - 2, 69)):
        for y in range(P + 1, G): k.set(x, y, z, BEAM_Y)
    # the stair to the balcony: along the east wall, rising north z 80 -> 73 (P+1..P+8), x ix2-2..ix2
    for i in range(8):
        z = 80 - i
        for x in range(ix2 - 2, ix2 + 1):
            k.set(x, P + 1 + i, z, stairs("dark_oak_stairs", "north"))
            if i: k.set(x, P + i, z, PLANK)
            for y in range(P + 2 + i, P + 6 + i):
                if y < G or z > iz2 - 3 or True: k.set(x, y, z, AIR) if y != G or z < 73 else None
    for x in range(ix2 - 2, ix2 + 1):
        for z in range(73, 81):
            if L.GAL + 1 > P + 1 + (80 - z): pass
        for z in range(74, 81): k.set(x, G, z, AIR) if P + 1 + (80 - z) < G else None
    for x in range(ix2 - 2, ix2 + 1):
        k.set(x, G + 1, 81, AIR)
    for z in range(74, 81): k.set(ix2 - 3, G + 1, z, "minecraft:dark_oak_fence")
    # bookshelves on the walls (ground: P+1..P+5, balcony: G+1..G+3), leaving the doors and the riddle shelves
    for (x, z) in edge_cells(r):
        for y in list(range(P + 1, P + 6)) + list(range(G + 1, G + 4)):
            if y == G or not (ix1 - 1 <= x <= ix2 + 1 and iz1 - 1 <= z <= iz2 + 1): continue
            inx = x + (1 if x == x1 else -1 if x == x2 else 0); inz = z + (1 if z == z1 else -1 if z == z2 else 0)
            if (x in (x1, x2)) and (z in (z1, z2)): continue
            k.set(inx, y, inz, "minecraft:bookshelf") if is_air(k.get(inx, y, inz)) and (hsh(x, y, z, 2910) < 0.8) else None
    # clear what the shelves must not block: the stair, the balcony walk
    for x in range(ix2 - 2, ix2 + 1):
        for z in range(72, 82):
            for y in range(P + 1, G + 4):
                if "bookshelf" in (k.get(x, y, z) or "") and not (x == ix2 and True): k.set(x, y, z, AIR)
    for x in range(ix1, ix2 + 1):
        for z in range(iz1, iz2 + 1):
            for y in range(G + 1, G + 4):
                if "bookshelf" in (k.get(x, y, z) or "") and (ix1 < x < ix2 and iz1 < z < iz2): k.set(x, y, z, AIR)
    # doors: from the chapel (north wall x 414..416, ground); into the annex at G (east wall x 421, z 66..68)
    k.air(414, P + 1, z1, 416, P + 3, z1)
    for x in range(414, 417):
        for z in (iz1,): k.set(x, P + 1, z, AIR); k.set(x, P + 2, z, AIR); k.set(x, P + 3, z, AIR)
    k.air(x2, G + 1, 66, x2, G + 3, 68)
    # the riddle wall: one chiseled shelf in the middle of each wall at P+2 (ground floor), a banner over it
    mid_x, mid_z = (ix1 + ix2) // 2, (iz1 + iz2) // 2
    shelves = {"north": (mid_x + 3, P + 2, iz1, "south", "white"), "south": (mid_x, P + 2, iz2, "north", "yellow"),       # clear of the balcony posts
               "west": (ix1, P + 2, mid_z - 1, "east", "orange"), "east": (ix2, P + 2, mid_z - 4, "west", "lime")}
    k.meta["shelves"] = {}
    for side, (x, y, z, f, col) in shelves.items():
        for dy in (-1, 0, 1, 2, 3):
            if "bookshelf" in (k.get(x, y + dy, z) or ""): k.set(x, y + dy, z, AIR)
        slot = 4
        k.set(x, y, z, riddle_shelf(f, slot))
        k.set(x, y - 1, z, "minecraft:chiseled_stone_bricks"); k.set(x, y + 1, z, AIR)
        k.set(x, y + 2, z, st("%s_wall_banner" % col, facing=f))
        bx, bz = x + (1 if f == "east" else -1 if f == "west" else 0), z + (1 if f == "south" else -1 if f == "north" else 0)
        k.meta["shelves"][side] = dict(pos=[x, y, z], slot=slot, facing=f, banner=[x, y + 2, z])
        # wall behind it solid (the shelf stands in front of the wall)
    # the lecterns: the riddle in the middle, Winter beside it, the note on the tower; chest 1
    cx, cz = mid_x, mid_z
    k.set(cx, P + 1, cz, lectern_with("north", book("Год Дома", CHRON, RIDDLE)))
    k.set(cx - 2, P + 1, cz + 1, lectern_with("north", volume_book("winter")))
    k.set(ix1 + 4, P + 1, iz2 - 4, lectern_with("west", book("Записка", "", TOWER_NOTE)))
    k.set(ix1 + 1, P + 1, iz2 - 1, st("chest", facing="east", type="single", waterlogged="false") + '{LootTable:"last_ember:chests/r1/common"}')
    k.meta.update(lectern_riddle=[cx, P + 1, cz], lectern_winter=[cx - 2, P + 1, cz + 1], lectern_tower=[ix1 + 4, P + 1, iz2 - 4],
                  chest1=[ix1 + 1, P + 1, iz2 - 1], library_box=[x1, P, z1, x2, G + 5, z2])
    # the gaol door niche under the north balcony (west part): the alcove x 409..411 z 55..57 walled at x 412 with the door (bars) x 412
    gx1, gx2 = 409, 411
    for z in range(iz1, iz1 + 4):             # the alcove z 55..58 (the floor over the stair opens till the stair is 4 under it)
        for y in range(P + 1, G):
            k.wall(412, y, z) if not (iz1 <= z <= iz1 + 2 and y <= P + 3) else k.set(412, y, z, "minecraft:iron_bars")
            for x in range(gx1, gx2 + 1):
                if y <= P + 4: k.set(x, y, z, AIR)
    for y in range(P + 4, G):
        for z in range(iz1, iz1 + 3): k.wall(412, y, z)
    for y in range(P + 1, G):                       # the alcove's south side (the stair runs on under the library floor)
        for x in range(gx1, gx2 + 2): k.wall(x, y, iz1 + 4)
    for x in range(gx1, gx2 + 1):
        for y in range(P + 1, G):
            if "bookshelf" in (k.get(x, y, iz1 - 0) or ""): k.set(x, y, iz1, AIR)
    k.tpl["gaol_door_closed"] = {(412, y, z): "minecraft:iron_bars" for y in range(P + 1, P + 4) for z in range(iz1, iz1 + 3)}
    k.tpl["gaol_door_open"] = {(412, y, z): AIR for y in range(P + 1, P + 4) for z in range(iz1, iz1 + 3)}
    k.meta["gaol_door"] = [412, P + 1, iz1 + 1]


# ================================================================ east wing: kitchens, armoury; the north tower
def kitchens(k):
    r = L.KITCHEN; x1, z1, x2, z2 = r; top = P + 11
    k.shell(r, P + 1, top)
    k.hip_roof(r, top + 2)
    for (x, z) in edge_cells(r): k.wall(x, top + 1, z)
    k.air(x1, P + 1, 48, x1, P + 3, 50)                 # from the arcade (GE ground)
    # the pantry (store room) x 477..481 z 50..53: walls x 476, z 49, door at z 49 x 478..480
    for y in range(P + 1, top + 1):
        for z in range(49, z2): k.wall(476, y, z)
        for x in range(476, x2): k.wall(x, y, 49)
    k.air(478, P + 1, 49, 480, P + 3, 49)
    k.set(481, P + 1, 52, lectern_with("west", volume_book("summer")))
    k.meta["lectern_summer"] = [481, P + 1, 52]
    for (x, z) in ((477, 50), (477, 51), (477, 53), (478, 53), (479, 53)):
        k.set(x, P + 1, z, "minecraft:barrel[facing=up,open=false]")
    k.set(477, P + 2, 53, "minecraft:barrel[facing=up,open=false]")
    # hearths on the east wall (unlit campfires in brick chimneys), cauldrons, the long table
    for z in (45, 47):
        k.set(x2 - 1, P + 1, z, "minecraft:campfire[facing=west,lit=false,signal_fire=false,waterlogged=false]")
        for y in range(P + 2, top + 1): k.set(x2 - 1, y, z, "minecraft:bricks")
        k.set(x2 - 2, P + 1, z, "minecraft:cauldron")
    for x in range(471, 475):
        k.set(x, P + 1, 51, "minecraft:spruce_planks" if x % 2 else slab("dark_oak_slab", "top"))
    for x in range(471, 475):
        for z in (50, 52): k.set(x, P + 1, z, stairs("dark_oak_stairs", "south" if z == 50 else "north")) if is_air(k.get(x, P + 1, z)) else None
    for (x, z) in ((475, 53), (474, 53)): k.set(x, P + 1, z, "minecraft:barrel[facing=up,open=false]")
    # the stair up to the east gallery (G): along the north wall z 45..47, rising west x 475 -> 472? no: the gallery door is at x 470
    G = L.GAL
    for i in range(8):
        x = 478 - i; y = P + 1 + i   # stairs P+1 (x 478) .. G (x 471), the door x 470 flush at G
        for z in range(45, 48):
            k.set(x, y, z, stairs("stone_brick_stairs", "west"))
            for yy in range(y + 1, y + 5): k.set(x, yy, z, AIR)
            for yy in range(P + 1, y): k.wall(x, yy, z)
        k.set(x1, G, 45 + (i % 3), FLOOR.at(x1, G, 45))
    for (x, z) in ((471, 45), (472, 45), (471, 46), (474, 45)):
        if "barrel" in (k.get(x, P + 1, z) or ""): k.set(x, P + 1, z, k.get(x, P + 1, z))
    k.air(x1, G + 1, 45, x1, G + 3, 47)                  # into the east gallery
    k.meta["kitchen_door"] = [x1, P + 1, 49]


def armoury(k):
    r = L.ARMOURY; x1, z1, x2, z2 = r; top = P + 9
    k.shell(r, P + 1, top)
    k.hip_roof(r, top + 2)
    for (x, z) in edge_cells(r): k.wall(x, top + 1, z)
    k.air(x1, P + 1, 56, x1, P + 3, 58)                 # from the south arcade corner
    # weapon racks (fence + item frames are entities: here banners and grindstones), the 6 armour stands are the datapack's
    for z in range(58, 68, 3):
        k.set(x2 - 1, P + 1, z, "minecraft:grindstone[face=floor,facing=west]")
    for x in range(473, 481, 2):
        k.set(x, P + 1, z2 - 1, "minecraft:smithing_table" if x == 477 else "minecraft:barrel[facing=up,open=false]")
    k.set(x2 - 1, P + 1, z2 - 1, lectern_with("north", volume_book("autumn")))
    k.meta["lectern_autumn"] = [x2 - 1, P + 1, z2 - 1]
    k.set(x2, P + 4, 60, st("black_wall_banner", facing="west")); k.set(x2, P + 4, 64, st("purple_wall_banner", facing="west"))
    k.meta["armour_stands"] = [[473.5, P + 1, z + 0.5, 0] for z in (58, 61, 64)] + [[479.5, P + 1, z + 0.5, 180] for z in (58, 61, 64)]


def tower(k):
    """the north tower (the shell only): walls up to the third tier and beyond, an outer window on the third tier, the door from the
    castle (from the east gallery's north end) bricked up from inside, the inside empty"""
    r = L.TOWER; x1, z1, x2, z2 = r; top = P + 40
    for y in range(P, top + 1):
        for (x, z) in edge_cells(r): k.wall(x, y, z)
    for x in range(x1 + 1, x2):
        for z in range(z1 + 1, z2):
            k.set(x, P, z, FLOOR.at(x, P, z))
            for y in range(P + 1, top + 1): k.set(x, y, z, AIR)
    for (x, z) in edge_cells(r): k.crenel([(x, z)], top + 1)
    rt = k.hip_roof((x1 + 1, z1 + 1, x2 - 1, z2 - 1), top + 2, overhang=0, spire=True)
    # the window of the third tier (P+24 .. P+27) on the north face, outside
    for y in range(P + 24, P + 28):
        for x in (476, 477, 478): k.set(x, y, z1, "minecraft:iron_bars" if x != 477 else AIR)
    # the bricked-up door: from the east gallery's north end a passage x 470..471, z 41..43 at G, the doorway in the tower wall x 471
    G = L.GAL
    for x in (470,):
        for z in range(41, 44):
            for y in range(G + 1, G + 4): k.set(x, y, z, AIR)
            k.set(x, G, z, PLANK)
    for z in range(41, 44):
        for y in range(G + 1, G + 4): k.set(x1, y, z, "minecraft:mossy_cobblestone" if (y + z) % 2 else "minecraft:cobblestone")
    k.meta["tower"] = dict(box=list(r), top=rt, window=[477, P + 24, z1])


# ================================================================ the keep: the vestibule, the annex, the hall, the reliquary, the roofs
def keep(k):
    H = L.HALL; x1, z1, x2, z2 = H; G = L.GAL; HY = L.HALL_Y
    ix1, iz1, ix2, iz2 = L.inside(H)
    # the walls of the keep from P to the top of the hall
    hall_top = HY + L.HALL_H
    for y in range(P, hall_top + 2):
        for (x, z) in edge_cells(H): k.wall(x, y, z)
    # the vestibule: P+1..P+12 under a vault; above it the floors of the keep up to the hall (solid, not reachable)
    for x in range(ix1, ix2 + 1):
        for z in range(iz1, iz2 + 1):
            k.set(x, P, z, FLOOR.at(x, P, z))
            for y in range(P + 1, P + 13): k.set(x, y, z, AIR)
            for y in range(P + 13, HY): k.set(x, y, z, "minecraft:stone_bricks" if y in (P + 13, HY - 1) else "minecraft:tuff")
    # pillars and arches of the vestibule
    for px in (438, 455):                          # clear of the way from the court door to the annex door (x 430, z 81..83)
        for pz in (64, 74, 86):
            for y in range(P + 1, P + 13): k.set(px, y, pz, "minecraft:polished_tuff" if y % 4 else "minecraft:chiseled_tuff")
            for (a, c, f) in ((1, 0, "east"), (-1, 0, "west")):
                k.set(px + a, P + 6, pz + c, st("lantern", hanging="false", waterlogged="false")) if False else None
            k.set(px, P + 13, pz, "minecraft:polished_tuff")
    # the vestibule is lit (the bonfire's hall): lanterns hanging from the vault
    for (lx, lz) in ((440, 70), (452, 70), (440, 80), (452, 80), (446, 86), (434, 75), (459, 75)):
        k.set(lx, P + 12, lz, "minecraft:iron_chain[axis=y,waterlogged=false]"); k.set(lx, P + 11, lz, lantern(True))
    # the door from the court (north wall, x 450..452)
    k.air(450, P + 1, z1, 452, P + 4, z1)
    # the bonfire 11: a clear pad 7 x 7 + the respawn 3 x 3 south of it (built by the datapack: bonfire/gen/register)
    hx, hy, hz = L.HEARTH11
    for x in range(hx - 3, hx + 4):
        for z in range(hz - 3, hz + 9):
            k.set(x, P, z, "minecraft:polished_deepslate" if (x + z) % 2 else "minecraft:deepslate_tiles")
            for y in range(P + 1, P + 6): k.set(x, y, z, AIR)
    # windows of the vestibule (bars, high) and the stairs of the annex
    annex(k)
    hall(k)
    reliquary(k)
    # the roof of the keep: a stepped cone from the hall's top
    rt = k.hip_roof(H, hall_top + 2, overhang=1, spire=True)
    for (x, z) in edge_cells(H): k.wall(x, hall_top + 2, z) if is_air(k.get(x, hall_top + 2, z)) else None
    # corner turrets
    for (cx, cz) in ((x1 - 1, z1 - 1), (x2 + 1, z1 - 1), (x1 - 1, z2 + 1), (x2 + 1, z2 + 1)):      # bartizans outside the corners
        for y in range(hall_top - 4, hall_top + 6):
            for a in (-1, 0, 1):
                for c in (-1, 0, 1): k.wall(cx + a, y, cz + c)
        k.hip_roof((cx - 1, cz - 1, cx + 1, cz + 1), hall_top + 6, overhang=0, spire=True)
    k.meta["keep_top"] = rt
    return rt


def annex(k):
    """the stair annex west of the hall (x 423..429 inside, z 59..83): from the vestibule (door x 430, z 81..83) up lane E (x 427..429)
    northward with a landing at G (z 71..73, the west walkway of the galleries), on to P+19 (landing z 59..61), back up lane W (x 423..425)
    southward to HALL_Y (z 72), the landing at HALL_Y in lane W (z 73..83) and the walk at HALL_Y over lane E to the two doors of the hall.
    The walkway at G in lane W (z 59..73) joins the south gallery (door in the north wall, x 423..425) and the library (door x 422, z 66..68)."""
    A = L.ANNEX; x1, z1, x2, z2 = A; G = L.GAL; HY = L.HALL_Y
    ix1, iz1, ix2, iz2 = L.inside(A)
    top = HY + 5
    for y in range(P, top + 2):
        for (x, z) in edge_cells(A):
            if x != x2: k.wall(x, y, z)
    for x in range(ix1, ix2 + 1):
        for z in range(iz1, iz2 + 1):
            k.set(x, P, z, FLOOR.at(x, P, z))
            for y in range(P + 1, top + 1): k.set(x, y, z, AIR)
            k.set(x, top + 1, z, "minecraft:stone_bricks")
    k.hip_roof(A, top + 3, overhang=1)
    for (x, z) in edge_cells(A): k.wall(x, top + 2, z)
    LW, LE = (ix1, ix1 + 2), (ix2 - 2, ix2)          # 423..425, 427..429
    path = []
    def lane_cells(lane, z, y, s):
        for x in range(lane[0], lane[1] + 1): k.set(x, y, z, s if isinstance(s, str) else s.at(x, y, z))
    # the ground door from the vestibule (x 430 z 81..83) -> landing lane E z 81..83 at P
    k.air(x2, P + 1, 81, x2, P + 3, 83)
    # run 1 (lane E, north): z 80 -> 74 levels 1..7, landing z 71..73 at G (= P + 8), z 70 -> 60 levels 9..19, landing z 59..61 (+ lane W) at P+19
    # (a landing is flush with the last stair of its flight: the stair block's top = the landing's top)
    lvl = {}
    for i, z in enumerate(range(80, 72, -1)): lvl[z] = i + 1          # z 80..73 -> 1..8
    for z in (72, 71, 70): lvl[z] = 8                                 # the landing at G
    for i, z in enumerate(range(69, 61, -1)): lvl[z] = 9 + i          # z 69..62 -> 9..16
    for z in (61, 60, 59): lvl[z] = 16
    for z, l in lvl.items():
        flat = z in (70, 71, 72, 59, 60, 61)
        lane_cells(LE, z, P + l, FLOOR if flat else stairs("stone_brick_stairs", "north"))
        for zz in [z]:
            for x in range(LE[0], LE[1] + 1):
                for y in range(P + 1, P + l): k.set(x, y, zz, "minecraft:stone_bricks") if is_air(k.get(x, y, zz)) else None
    # the spine (x 426) carries the landings across
    for z in (59, 60, 61):
        for x in range(LW[0], LE[1] + 1): k.set(x, P + 16, z, FLOOR.at(x, P + 16, z))
    # run 2 (lane W, south): z 62 -> 75 levels 17..30 (HALL_Y - P = 30)
    for i, z in enumerate(range(62, 76)):
        l = 17 + i
        lane_cells(LW, z, P + l, stairs("stone_brick_stairs", "south"))
        for x in range(LW[0], LW[1] + 1): k.set(x, P + l - 1, z, "minecraft:stone_bricks") if is_air(k.get(x, P + l - 1, z)) else None
    # the landing at HY in lane W z 73..83 and the walk at HY over the spine and lane E z 59..83 (the two doors at z 65..67, 82..84)
    for z in range(76, iz2 + 1):
        for x in range(LW[0], LW[1] + 1): k.set(x, HY, z, PLANK)
    for z in range(iz1, iz2 + 1):
        for x in range(LE[0] - 1, LE[1] + 1): k.set(x, HY, z, PLANK)
    for z in range(iz1, 74):
        k.set(LE[0] - 1, HY + 1, z, "minecraft:dark_oak_fence")
    # the walkway at G in lane W (z 59..73) + the spine at the landing (z 71..73)
    for z in range(iz1, 73):
        for x in range(LW[0], LW[1] + 1): k.set(x, G, z, PLANK)
    for z in (70, 71, 72): k.set(LE[0] - 1, G, z, PLANK)
    for z in range(iz1, 70): k.set(LE[0] - 1, G + 1, z, "minecraft:dark_oak_fence")
    # doors: north wall x 423..425 at G (from the south gallery), west wall x 422 z 66..68 at G (the library)
    k.air(LW[0], G + 1, z1, LW[1], G + 3, z1)
    k.air(x1, G + 1, 66, x1, G + 3, 68)
    # lanterns? the annex is the keep's: dark like the wings (spawn) -- except one lantern at each landing (the stair is long)
    for (lx, ly, lz) in ((424, G + 4, 60), (428, P + 20, 60), (424, HY + 4, 80), (428, HY + 4, 75), (428, P + 4, 82)):
        k.set(lx, ly, lz, lantern(True)); k.set(lx, ly + 1, lz, "minecraft:iron_chain[axis=y,waterlogged=false]")
    k.meta["annex"] = dict(lvl={str(z): l for z, l in lvl.items()})


def hall(k):
    H = L.HALL; x1, z1, x2, z2 = H; HY = L.HALL_Y; HG = HY + L.HG
    ix1, iz1, ix2, iz2 = L.inside(H)
    top = HY + L.HALL_H
    # the floor (chequer of polished deepslate and deepslate tiles), the air, the ceiling on dark oak beams
    for x in range(ix1, ix2 + 1):
        for z in range(iz1, iz2 + 1):
            k.set(x, HY, z, "minecraft:polished_deepslate" if (x + z) % 2 else "minecraft:deepslate_tiles")
            for y in range(HY + 1, top + 1): k.set(x, y, z, AIR)
            k.set(x, top + 1, z, BEAM_X if z % 4 == 0 else "minecraft:dark_oak_planks")
    # the columns (3 x 3, full height): polished tuff with chiseled bands
    for (a, b_) in L.COLS_X:
        for (c, d) in L.COLS_Z:
            for x in range(a, b_ + 1):
                for z in range(c, d + 1):
                    for y in range(HY + 1, top + 1):
                        k.set(x, y, z, "minecraft:chiseled_tuff" if (y - HY) % 6 == 0 else "minecraft:polished_tuff")
    # the gallery round the hall: floor HG, 3 wide, dark oak planks on stripped dark oak beams, a parapet of tuff brick wall with gaps
    gal = set()
    for x in range(ix1, ix2 + 1):
        for z in range(iz1, iz2 + 1):
            if x <= ix1 + 2 or x >= ix2 - 2 or z <= iz1 + 2 or z >= iz2 - 2: gal.add((x, z))
    for (x, z) in gal:
        k.set(x, HG, z, "minecraft:dark_oak_planks")
        k.set(x, HG - 1, z, BEAM_X if (x <= ix1 + 2 or x >= ix2 - 2) and z % 3 == 0 else BEAM_Z if (z <= iz1 + 2 or z >= iz2 - 2) and x % 3 == 0 else AIR)
    rim = [(x, z) for (x, z) in gal if (x == ix1 + 2 and iz1 + 2 <= z <= iz2 - 2) or (x == ix2 - 2 and iz1 + 2 <= z <= iz2 - 2) or
           (z == iz1 + 2 and ix1 + 2 <= x <= ix2 - 2) or (z == iz2 - 2 and ix1 + 2 <= x <= ix2 - 2)]
    for (x, z) in rim:
        gap = (x + z) % 7 in (0, 1)
        if not gap: k.set(x, HG + 1, z, "minecraft:tuff_brick_wall")
    # posts under the gallery rim (stripped logs) every 6
    for (x, z) in rim:
        if (x in (ix1 + 2, ix2 - 2) and z % 6 == 0) or (z in (iz1 + 2, iz2 - 2) and x % 6 == 0):
            for y in range(HY + 1, HG): k.set(x, y, z, BEAM_Y)
    # the stairs from the floor to the gallery in the west corners: NW along z iz1+3..iz1+5 rising west from x ix1+9 -> ix1+4? (6 steps)
    st_cells = {}
    for (zz, f) in (((iz1 + 3, iz1 + 5), "north"), ((iz2 - 5, iz2 - 3), "south")):
        for i in range(6):
            x = ix1 + 8 - i       # x 439 (HY+1) .. 434 (HY+6 = HG: the gallery beyond is flush)
            for z in range(zz[0], zz[1] + 1):
                y = HY + 1 + i
                k.set(x, y, z, stairs("dark_oak_stairs", "west"))
                for yy in range(HY + 1, y): k.set(x, yy, z, "minecraft:dark_oak_planks")
                st_cells[(x, z)] = y
        # the rim gap where the stair lands (x ix1+3 .. ix1+5 on the inner side of the gallery)
        for z in range(zz[0], zz[1] + 1):
            k.set(ix1 + 2, HG + 1, z, AIR)
    # the two west doors (x 430) with their portcullises (templates), the guard niches (3 x 3 x 4, bars), the reliquary door
    for (za, zb) in L.HALL_DOORS:
        for z in range(za, zb + 1):
            for y in range(HY + 1, HY + 4): k.set(x1, y, z, AIR)
    k.tpl["hall_doors_closed"] = {(x1, y, z): "minecraft:iron_bars" for (za, zb) in L.HALL_DOORS for z in range(za, zb + 1) for y in range(HY + 1, HY + 4)}
    k.tpl["hall_doors_open"] = {p: AIR for p in k.tpl["hall_doors_closed"]}
    niches = {}
    for key, (nx1, nz1, nx2, nz2) in L.NICHE_GUARD.items():
        # a bay box round the niche (walls), the floor at HG, air HG+1..HG+4, the bars on the hall side
        for x in range(nx1 - 1, nx2 + 2):
            for z in range(nz1 - 1, nz2 + 2):
                for y in range(HG - 1, HG + 6):
                    inside = nx1 <= x <= nx2 and nz1 <= z <= nz2 and HG + 1 <= y <= HG + 4
                    hall_side = ix1 <= x <= ix2 and iz1 <= z <= iz2
                    if hall_side: continue
                    k.set(x, y, z, AIR if inside else wall_at(x, y, z))
        if key == "n": bars = [(x, z1) for x in range(nx1, nx2 + 1)]
        elif key == "s": bars = [(x, z2) for x in range(nx1, nx2 + 1)]
        else: bars = [(x1, z) for z in range(nz1, nz2 + 1)]
        for (x, z) in bars:
            k.set(x, HG, z, "minecraft:dark_oak_planks")
            for y in range(HG + 1, HG + 5): k.set(x, y, z, AIR)
        k.tpl["niche_%s_closed" % key] = {(x, y, z): "minecraft:iron_bars" for (x, z) in bars for y in range(HG + 1, HG + 5)}
        k.tpl["niche_%s_open" % key] = {p: AIR for p in k.tpl["niche_%s_closed" % key]}
        cx, cz = (nx1 + nx2) / 2 + 0.5, (nz1 + nz2) / 2 + 0.5
        niches[key] = [cx, HG + 1, cz]
    # corbels under the north and south bays (they hang out of the wall over the court / the cliff)
    for key in ("n", "s"):
        nx1, nz1, nx2, nz2 = L.NICHE_GUARD[key]
        f = "south" if key == "n" else "north"
        for x in range(nx1 - 1, nx2 + 2):
            zz = nz1 - 1 if key == "n" else nz2 + 1
            k.set(x, HG - 2, zz, stairs("stone_brick_stairs", f, "top"))
    # the windows: stained glass between HY+10 and HY+18 in the north, south and east walls (the only light), and west high up
    for (x, z) in edge_cells(H):
        side = "n" if z == z1 else "s" if z == z2 else "w" if x == x1 else "e"
        t = (x - x1) if side in ("n", "s") else (z - z1)
        if side in ("n", "s") and t % 5 in (2, 3) and 2 < t < 32 or side in ("e", "w") and t % 5 in (2, 3) and 2 < t < 32:
            if side == "e" and 70 <= z <= 79: continue
            for y in range(HY + 10, HY + 19):
                k.set(x, y, z, "minecraft:purple_stained_glass" if (y + t) % 4 else "minecraft:cyan_stained_glass")
    # the throne: a dais of three steps (slab, slab+1, full) at the east wall, the seat of polished blackstone with gold
    tz1, tz2 = L.THRONE_Z
    dz1, dz2 = tz1 - 4, tz2 + 4
    for z in range(dz1, dz2 + 1):
        for x in range(ix2 - 8, ix2 - 2):
            lvl = 0 if x == ix2 - 8 else 1 if x == ix2 - 7 else 2
            if lvl == 0: k.set(x, HY + 1, z, slab("polished_blackstone_slab"))
            elif lvl == 1: k.set(x, HY + 1, z, "minecraft:polished_blackstone"); k.set(x, HY + 2, z, slab("polished_blackstone_slab"))
            else:
                k.set(x, HY + 1, z, "minecraft:polished_blackstone"); k.set(x, HY + 2, z, "minecraft:polished_blackstone")
    # step edges as stairs: three steps of half a block (0.5, 1.5 .. -> walkable without jumps)
    for z in range(dz1, dz2 + 1):
        k.set(ix2 - 8, HY + 1, z, slab("polished_blackstone_slab"))
        k.set(ix2 - 7, HY + 1, z, "minecraft:polished_blackstone"); k.set(ix2 - 7, HY + 2, z, AIR)
        for x in range(ix2 - 6, ix2 - 2): k.set(x, HY + 1, z, "minecraft:polished_blackstone"); k.set(x, HY + 2, z, slab("polished_blackstone_slab"))
    sx = ix2 - 4                                # the seat column x 458; the back at 459; the walk behind x 460..462 (floor level)
    th = {}
    for z in range(tz1, tz2 + 1):
        th[(sx, HY + 3, z)] = stairs("polished_blackstone_stairs", "east")
        for y in range(HY + 3, HY + 7): th[(sx + 1, y, z)] = "minecraft:gold_block" if y in (HY + 5, HY + 6) and z == tz1 or y == HY + 6 else "minecraft:polished_blackstone"
    for z in (tz1 - 1, tz2 + 1):
        th[(sx, HY + 3, z)] = "minecraft:polished_blackstone"; th[(sx, HY + 4, z)] = "minecraft:gold_block"
        th[(sx + 1, HY + 3, z)] = "minecraft:polished_blackstone"; th[(sx + 1, HY + 4, z)] = "minecraft:polished_blackstone"
    for p, s in th.items(): k.set(*p, s)
    # the sign at the foot of the dais
    sign(ix2 - 9, HY + 1, tz1 - 2, k, ["Разбудит огонь."], "west", wall=False)
    k.tpl["throne_before"] = {(sx, HY + 4, z): AIR for z in range(tz1, tz2 + 1)}
    after = {(sx, HY + 4, tz1): "minecraft:air", (sx, HY + 4, tz2): "minecraft:air"}
    k.tpl["throne_after"] = after
    # the door behind the throne (x 463, z 73..76) to the reliquary: closed (wall) / open
    rz1, rz2 = L.RELIQ_DOOR_Z
    closed = {(x2, y, z): "minecraft:polished_blackstone_bricks" if y < HY + 3 else "minecraft:chiseled_polished_blackstone" for z in range(rz1, rz2 + 1) for y in range(HY + 1, HY + 4)}
    k.tpl["reliq_door_closed"] = closed; k.tpl["reliq_door_open"] = {p: AIR for p in closed}
    for p, s in closed.items(): k.set(*p, s)
    k.meta["hall"] = dict(box=[ix1, HY + 1, iz1, ix2, top, iz2], floor=HY, gallery=HG, niches=niches, throne=[sx + 0.5, HY + 3, (tz1 + tz2) / 2 + 0.5],
                          doors=[[x1, HY + 1, za, x1, HY + 3, zb] for (za, zb) in L.HALL_DOORS], stairs={"%d,%d" % q: y for q, y in st_cells.items()},
                          reliq_door=[x2, HY + 1, rz1, x2, HY + 3, rz2], center=[(ix1 + ix2) / 2 + 0.5, HY + 1, (iz1 + iz2) / 2 + 0.5])


def reliquary(k):
    R = L.RELIQ; x1, z1, x2, z2 = R; HY = L.HALL_Y
    ix1, iz1, ix2, iz2 = L.inside(R)
    top = HY + 6
    for y in range(P, top + 2):
        for (x, z) in edge_cells(R): k.wall(x, y, z)
    for x in range(ix1, ix2 + 1):
        for z in range(iz1, iz2 + 1):
            for y in range(P + 1, HY): k.set(x, y, z, "minecraft:tuff")
            k.set(x, HY, z, "minecraft:polished_blackstone_bricks" if (x + z) % 2 else "minecraft:polished_deepslate")
            for y in range(HY + 1, top + 1): k.set(x, y, z, AIR)
            k.set(x, top + 1, z, "minecraft:polished_blackstone_bricks")
    k.hip_roof(R, top + 2)
    cx, cz = (ix1 + ix2) // 2, (iz1 + iz2) // 2
    k.set(cx, HY + 1, cz, "minecraft:chiseled_polished_blackstone")         # the pedestal of the Signet
    for (a, c) in ((-3, -3), (3, -3), (-3, 3), (3, 3)): k.set(cx + a, HY + 1, cz + c, "minecraft:candle[candles=3,lit=false,waterlogged=false]")
    k.set(ix2, HY + 1, iz1, st("chest", facing="west", type="single", waterlogged="false") + '{LootTable:"last_ember:chests/r1/castle_reliquary"}')
    # the windows: two slits of purple glass
    for y in (HY + 3, HY + 4): k.set(x2, y, cz, "minecraft:purple_stained_glass")
    # the secret door to the spiral: the east wall x 474 at z 78..80 (a passage, always open: the reliquary itself is locked)
    for z in range(iz2 - 2, iz2 + 1):
        for y in range(HY + 1, HY + 4): k.set(x2, y, z, AIR)
    k.meta.update(pedestal=[cx + 0.5, HY + 2, cz + 0.5], chest3=[ix2, HY + 1, iz1], reliquary_box=[ix1, HY + 1, iz1, ix2, top, iz2])


# ================================================================ the secret way
def spiral(k):
    """the spiral of the secret way inside the column x 474..484 (inside 475..483 x 72..80): a 3 x 3 core, lanes 3 wide round it, each
    side three steps down, the corners flat; from HALL_Y (the door from the reliquary, west side z 78..80) down to TUN_Y; the tunnel leaves
    at the bottom northward (x 475..477). Returns the bot points (centre line)."""
    S = L.SPIRAL; x1, z1, x2, z2 = S; HY = L.HALL_Y
    ix1, iz1, ix2, iz2 = L.inside(S)
    top = HY + 6
    for y in range(L.TUN_Y - 1, top + 2):
        for (x, z) in edge_cells(S):
            if y >= P + 1 or True: k.set(x, y, z, wall_at(x, y, z) if y > P else CB.rock_at(x, y, z, P) or "minecraft:stone")
    for x in range(ix1, ix2 + 1):
        for z in range(iz1, iz2 + 1):
            for y in range(L.TUN_Y, top + 1): k.set(x, y, z, "minecraft:tuff" if ix1 + 3 <= x <= ix1 + 5 and iz1 + 3 <= z <= iz1 + 5 else AIR)
            k.set(x, top + 1, z, "minecraft:stone_bricks")
    k.hip_roof(S, top + 2)
    for z in range(iz2 - 2, iz2 + 1):                 # the doorway from the reliquary (its east wall is the spiral's west wall)
        for y in range(HY + 1, HY + 4): k.set(x1, y, z, AIR)
        k.set(x1, HY, z, FLOOR.at(x1, HY, z))
    # the walk: clockwise seen from above, starting in the SW corner (x 475..477, z 78..80) at HY, going down
    corners = [(ix1, iz2 - 2), (ix1, iz1), (ix2 - 2, iz1), (ix2 - 2, iz2 - 2)]       # SW, NW, NE, SE (the 3 x 3 corner squares' min cells)
    sides = [("north", [(ix1, iz2 - 3), (ix1, iz2 - 4), (ix1, iz2 - 5)]), ("east", [(ix1 + 3, iz1), (ix1 + 4, iz1), (ix1 + 5, iz1)]),
             ("south", [(ix2 - 2, iz1 + 3), (ix2 - 2, iz1 + 4), (ix2 - 2, iz1 + 5)]), ("west", [(ix2 - 3, iz2 - 2), (ix2 - 4, iz2 - 2), (ix2 - 5, iz2 - 2)])]
    y = HY; pts = []; seq = []
    k_ = 0
    while True:
        c = corners[k_ % 4]
        for a in range(3):
            for b_ in range(3): k.set(c[0] + a, y, c[1] + b_, FLOOR.at(c[0] + a, y, c[1] + b_))
        pts.append((c[0] + 1, c[1] + 1, y))
        if y <= L.TUN_Y: break
        f, cells = sides[k_ % 4]
        for (sx, sz) in cells:          # stairs at H, H-1, H-2 below a corner at H (flush with it), the next corner at H-3
            for d in range(3):
                x, z = (sx, sz + d) if f in ("east", "west") else (sx + d, sz)
                # going down in direction f means the stair rises toward the opposite side
                back = {"north": "south", "south": "north", "east": "west", "west": "east"}[f]
                k.set(x, y, z, stairs("stone_brick_stairs", back))
                k.set(x, y - 1, z, "minecraft:stone_bricks")
            y -= 1
        k_ += 1
        if y <= L.TUN_Y:
            c = corners[k_ % 4]
            for a in range(3):
                for b_ in range(3): k.set(c[0] + a, y, c[1] + b_, FLOOR.at(c[0] + a, y, c[1] + b_))
            pts.append((c[0] + 1, c[1] + 1, y)); break
    # every flat corner gets the floor; the air over each walk cell: 4 (the turn above is 3 higher: so the corner squares keep 3 of air
    # under the next turn's floor? each revolution drops 12, so there are 11 blocks between the floors of the same corner)
    k.meta["spiral"] = dict(points=pts, bottom=y, corners=corners)
    # lights: rare (soul lanterns every second revolution)
    for (px, pz, py) in pts[::8]: k.set(px, py + 3, pz, "minecraft:soul_lantern[hanging=true,waterlogged=false]")
    return pts


def tunnel(k):
    """the tunnel from the bottom of the spiral (its NW corner) north under the east wing, west under the rift, north under the
    bridgehead, west and up to the pier door; lined with the rock of the castle (no cave of the natural ground opens into it)"""
    cells = {}       # (x, z) -> floor y
    def seg(r, y):
        for x in range(r[0], r[2] + 1):
            for z in range(r[1], r[3] + 1): cells[(x, z)] = y
    T = L.TUN_Y
    seg((470, 78, 473, 80), T)            # out of the spiral's SW corner (its bottom) west through its wall
    seg((470, 12, 472, 80), T)            # north under the east wing (x 470..472)
    seg((461, 10, 469, 12), T)            # west under the rift
    seg((461, -33, 463, 9), T)            # north under the rift's floor and the bridgehead
    # west and up: x 460 -> 445 rising from T to DOOR_Y (16 steps), then flat to x 433
    ramp = {}
    for i, x in enumerate(range(460, 444, -1)):
        for z in range(-33, -30): cells[(x, z)] = T + 1 + i; ramp[(x, z)] = T + 1 + i
    seg((433, -33, 444, -31), L.DOOR_Y)
    for (x, z), y in cells.items():
        for yy in range(y - 1, y + 5):
            for (a, c) in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + a, z + c)
                if q in cells and (a or c): continue
                cur = k.get(q[0], yy, q[1])
                if (a, c) == (0, 0): continue
                if cur is None: k.set(q[0], yy, q[1], DUNG.at(q[0], yy, q[1]))
        k.set(x, y - 1, z, DUNG.at(x, y - 1, z))
        k.set(x, y, z, stairs("cobbled_deepslate_stairs", "west") if (x, z) in ramp else DUNG.at(x, y, z) if False else "minecraft:deepslate_tiles" if (x + z) % 3 == 0 else "minecraft:cobbled_deepslate")
        for yy in range(y + 1, y + 4): k.set(x, yy, z, AIR)
        k.set(x, y + 4, z, DUNG.at(x, y + 4, z))
    # the ramp: the stair blocks are the walking surface (each one block higher), the cell under each one solid
    for (x, z), y in ramp.items(): k.set(x, y, z, stairs("cobbled_deepslate_stairs", "west")); k.set(x, y - 1, z, "minecraft:cobbled_deepslate")
    # rare lights
    lamps = []
    for (x, z) in ((471, 60), (471, 30), (466, 11), (462, -10), (452, -32), (438, -32)):
        y = cells[(x, z)]; k.set(x, y + 3, z, "minecraft:soul_lantern[hanging=true,waterlogged=false]"); lamps.append((x, y + 3, z))
    # the pier door in the face (x 432, z -33..-31, y 117..119): closed = the rock face; open = passage + raised portcullis (bars at the top)
    dx = L.PIER_DOOR[0]
    closed = {}; opened = {}
    for z in range(-33, -30):
        for y in range(L.DOOR_Y + 1, L.DOOR_Y + 4):
            closed[(dx, y, z)] = CB.rock_at(dx, y, z, 162) or "minecraft:stone"
            opened[(dx, y, z)] = AIR
        opened[(dx, L.DOOR_Y + 4, z)] = "minecraft:iron_bars"; closed[(dx, L.DOOR_Y + 4, z)] = CB.rock_at(dx, L.DOOR_Y + 4, z, 162) or "minecraft:stone"
        k.set(dx, L.DOOR_Y, z, "minecraft:cobbled_deepslate")
    for p, s in closed.items(): k.set(*p, s)
    k.tpl["pier_door_closed"] = closed; k.tpl["pier_door_open"] = opened
    k.tunnel_cells = dict(cells)
    k.meta["tunnel"] = dict(cells=len(cells), lamps=lamps, door=[dx, L.DOOR_Y + 1, -32], inside=[dx + 2.5, L.DOOR_Y + 1, -31.5])
    return cells


# ================================================================ under the west wing: the gaol and the crypt
def gaol(k):
    """the stair from the alcove of the library (x 409..411, z 55 -> 66, P-1 .. P-12), the landing z 67..69, the corridor x 413..415 z 67..82
    with cells on both sides (bars), the arrow trap with its hint, the prisoner's note, chest 2 in the last cell; the stair down to the
    crypt from the corridor's north end (x 413..415, z 66 -> 55, P-13 .. P-24)"""
    GY, CY = L.GAOL_Y, L.CRYPT_Y
    # the room of the gaol: x 408..421, z 66..83 (walls), floor GY, air GY+1..GY+4
    gx1, gz1, gx2, gz2 = 408, 66, 421, 83
    for x in range(gx1, gx2 + 1):
        for z in range(gz1, gz2 + 1):
            for y in range(GY - 1, GY + 6):
                edge = x in (gx1, gx2) or z in (gz1, gz2) or y in (GY - 1, GY + 5)
                k.set(x, y, z, DUNG.at(x, y, z) if edge else AIR)
            k.set(x, GY, z, DUNG.at(x, GY, z)) if gx1 < x < gx2 and gz1 < z < gz2 else None
    # the entrance stair (the alcove floor at P is opened over its first steps)
    for i in range(12):
        z = 55 + i; y = P - i            # the first stair flush with the library floor, the last one over the landing GY
        for x in range(409, 412):
            k.set(x, y, z, stairs("stone_brick_stairs", "north"))
            for yy in range(y + 1, y + 4):
                if yy < P or z <= 58: k.set(x, yy, z, AIR)       # the library floor stays (only the alcove z 55..58 is open)
            k.set(x, y - 1, z, DUNG.at(x, y - 1, z)); k.set(x, y + 5, z, DUNG.at(x, y + 5, z)) if y + 5 < P else None
        for x in (408, 412):
            for yy in range(y - 1, y + 6):
                if yy < P: k.set(x, yy, z, DUNG.at(x, yy, z))
    # cells: west x 409..411 (z 70..73, 75..78, 80..82), east x 417..420 (z 67..70, 72..75, 77..80); bars toward the corridor x 412 / 416
    cells_w = [(70, 73), (75, 78), (80, 82)]; cells_e = [(68, 71), (73, 76), (78, 82)]
    for (za, zb) in cells_w:
        for z in range(za - 1, zb + 2):
            for y in range(GY + 1, GY + 5): k.set(412, y, z, "minecraft:iron_bars" if za <= z <= zb else DUNG.at(412, y, z))
            for y in range(GY + 1, GY + 5):
                if z in (za - 1, zb + 1): k.fill(409, y, z, 411, y, z, DUNG)
    for (za, zb) in cells_e:
        for z in range(za - 1, zb + 2):
            for y in range(GY + 1, GY + 5): k.set(416, y, z, "minecraft:iron_bars" if za <= z <= zb else DUNG.at(416, y, z))
            for y in range(GY + 1, GY + 5):
                if z in (za - 1, zb + 1) and z <= 82: k.fill(417, y, z, 420, y, z, DUNG)
    for y in range(GY + 1, GY + 5): k.set(412, y, 67, AIR); k.set(412, y, 68, AIR); k.set(412, y, 69, AIR)
    # remains, chains, skulls
    for (x, z) in ((410, 72), (419, 70), (418, 74), (410, 77)):
        k.set(x, GY + 1, z, "minecraft:bone_block[axis=x]" if (x + z) % 2 else "minecraft:skeleton_skull[powered=false,rotation=%d]" % ((x * 3 + z) % 16))
    for (x, z) in ((409, 71), (420, 69), (420, 75), (409, 76), (420, 80)):
        for y in (GY + 3, GY + 4): k.set(x, y, z, "minecraft:iron_chain[axis=y,waterlogged=false]")
    k.set(419, GY + 1, 74, lectern_with("west", book("Записка узника", "", PRISONER)))
    k.set(409, GY + 1, 82, st("chest", facing="north", type="single", waterlogged="false") + '{LootTable:"last_ember:chests/r1/common"}')
    k.set(412, GY + 1, 81, AIR); k.set(412, GY + 2, 81, AIR); k.set(412, GY + 1, 82, AIR); k.set(412, GY + 2, 82, AIR)   # the last cell: bars broken open
    # the arrow trap: the corridor z 74..76 (x 413..415); slits in the east wall? (cells) -> in the floor-level slits of the west cell wall
    # (x 412, z 74 is a wall cell between two cells): the hint: dark slits and a bone on a pressure plate
    k.set(414, GY + 1, 75, "minecraft:polished_blackstone_pressure_plate[powered=false]")
    for z in (74, 79):
        k.set(412, GY + 2, z, "minecraft:iron_bars")   # the slits (between the west cells)
    k.meta["trap"] = dict(box=[413, GY + 1, 73, 415, GY + 3, 77], plate=[414, GY + 1, 75], pts=[[412, GY + 2, 74], [412, GY + 2, 79]], bone=[414.5, GY + 1.07, 75.5])
    # the crypt stair: from the corridor's north end (z 66) north down x 413..415 to z 55 (CY)
    for i in range(12):
        z = 66 - i; y = GY - i
        for x in range(413, 416):
            k.set(x, y, z, stairs("stone_brick_stairs", "south"))
            for yy in range(y + 1, y + 5): k.set(x, yy, z, AIR)
            k.set(x, y - 1, z, DUNG.at(x, y - 1, z))
            if y + 5 <= GY: k.set(x, y + 5, z, DUNG.at(x, y + 5, z))
        for x in (412, 416):
            for yy in range(y - 1, y + 6):
                if yy <= GY + 5 and not (x == 412 and z >= 55 and yy >= P - 13 - (z - 55)): k.set(x, yy, z, DUNG.at(x, yy, z))
    for x in range(413, 416):
        for y in range(GY + 1, GY + 5): k.set(x, y, 66, AIR)       # the top stair (z 66, flush with the gaol floor) stays
    k.meta["gaol_box"] = [gx1, GY, gz1, gx2, GY + 5, gz2]


def crypt(k):
    """the royal crypt under the chapel: x 408..433, z 40..55 (walls), floor CRYPT_Y, air 6; tombs of polished deepslate with candles, a
    crown on one, the empty sarcophagus with its sign"""
    CY = L.CRYPT_Y
    cx1, cz1, cx2, cz2 = 408, 40, 433, 55
    for x in range(cx1, cx2 + 1):
        for z in range(cz1, cz2 + 1):
            for y in range(CY - 1, CY + 8):
                edge = x in (cx1, cx2) or z in (cz1, cz2) or y in (CY - 1, CY + 7)
                k.set(x, y, z, DUNG.at(x, y, z) if edge else AIR)
            if cx1 < x < cx2 and cz1 < z < cz2: k.set(x, CY, z, "minecraft:polished_deepslate" if (x + z) % 2 else "minecraft:deepslate_bricks")
    for x in range(413, 416):
        for y in range(CY + 1, CY + 5): k.set(x, y, cz2, AIR)
    # pillars
    for px in (414, 420, 426):
        for pz in (44, 51):
            for y in range(CY + 1, CY + 7): k.set(px, y, pz, "minecraft:polished_deepslate")
    tombs = []
    for i, (tx, tz) in enumerate(((417, 42), (423, 42), (429, 42), (417, 48), (423, 48), (429, 48))):
        empty = i == 5
        for x in range(tx, tx + 2):
            for z in range(tz, tz + 3):
                k.set(x, CY + 1, z, "minecraft:polished_deepslate")
                k.set(x, CY + 2, z, AIR if empty else slab("polished_deepslate_slab"))
        k.set(tx - 1, CY + 1, tz, "minecraft:candle[candles=2,lit=false,waterlogged=false]")
        k.set(tx + 2, CY + 1, tz + 2, "minecraft:candle[candles=3,lit=false,waterlogged=false]")
        tombs.append([tx, CY + 1, tz])
    sign(429, CY + 1, 47, k, ["Место короля.", "Он лёг в другом", "месте."], "north")
    k.meta["crypt"] = dict(box=[cx1, CY, cz1, cx2, CY + 7, cz2], tombs=tombs, crown=[417.5 + 0.5, CY + 2.55, 43.5], candles=True)


# ================================================================ the gate of the barbican (templates)
def gate_templates(k, barbican):
    gx1, gy1, gz, gx2, gy2, _ = barbican["portcullis"]
    closed = {(x, y, gz): "minecraft:iron_bars" for x in range(gx1, gx2 + 1) for y in range(gy1, gy2 + 1)}
    opened = {(x, y, gz): AIR for x in range(gx1, gx2 + 1) for y in range(gy1, gy2)}
    for x in range(gx1, gx2 + 1): opened[(x, gy2, gz)] = "minecraft:iron_bars"
    k.tpl["gate_closed"] = closed; k.tpl["gate_open"] = opened


def build(b, gr, rl, barbican):
    k = K(b)
    court(k, gr, rl)
    galleries(k)
    for (bx, bz, f, c) in ((440, 40, "south", "purple"), (463, 40, "south", "purple"), (452, 53, "north", "black")):   # banners of the court
        k.set(bx, P + 5, bz, st("%s_wall_banner" % c, facing=f))
    chapel(k)
    library(k)
    kitchens(k)
    armoury(k)
    tower(k)
    keep(k)
    spiral(k)
    tunnel(k)
    crypt(k)                      # before the gaol: the crypt stair (gaol) cuts its north wall
    gaol(k)
    gate_templates(k, barbican)
    k.meta["hearth11"] = list(L.HEARTH11)
    m = k.meta
    k.marks = [(L.HEARTH11[0], L.HEARTH11[2], "bonfire 11", 0), (450, 36, "gate", 0), (m["well"][0], m["well"][2], "well", 0),
               (m["lectern_spring"][0], m["lectern_spring"][2], "Spring", 0), (m["lectern_summer"][0], m["lectern_summer"][2], "Summer", 0),
               (m["lectern_autumn"][0], m["lectern_autumn"][2], "Autumn", 0), (m["lectern_winter"][0], m["lectern_winter"][2], "Winter", 0),
               (m["lectern_riddle"][0], m["lectern_riddle"][2], "riddle", 0), (m["chest1"][0], m["chest1"][2], "chest 1", 0),
               (m["gaol_door"][0], m["gaol_door"][2], "gaol door", 0), (412, 70, "gaol (P-12)", 0), (420, 47, "crypt (P-24)", 0), (409, 82, "chest 2", 0),
               (414, 75, "trap", 0), (477, 38, "north tower", 0), (476, 61, "6 stands", 0), (434, -32, "pier door", 0)]
    k.marks += [(s_["pos"][0], s_["pos"][2], "shelf " + n[0].upper(), 0) for n, s_ in m["shelves"].items()]
    h = m["hall"]
    k.marks += [(int(h["throne"][0]), int(h["throne"][2]), "throne", 2), (L.HALL[0], 67, "door 1", 2), (L.HALL[0], 82, "door 2", 2),
                (L.HALL[2], 74, "reliquary door", 2), (int(m["pedestal"][0]), int(m["pedestal"][2]), "Signet", 2), (m["chest3"][0], m["chest3"][2], "chest 3", 2),
                (476, 79, "spiral down", 2)]
    k.marks += [(int(v[0]), int(v[2]), "guard " + n, 3) for n, v in h["niches"].items()]
    return k
