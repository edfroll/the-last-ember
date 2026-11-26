"""T-033: the blocks of the Iron Ore Mines (mines_plan.py lays them out): the yard (its surface, the retaining walls, the headframe over
the shaft, the office with the lunch, the journal, Bran's note and the chest, the store shed, the spoil heap, the rails, the lanterns, the
sign by the trail), the approach, the adit with its portal, the shaft (deck, platforms, ladders), the three horizons (shell rock by
horizon, timbering every 4, lanterns on H1, rails on H1), the inclines, the ore strips, the cave-ins (sensors, hints), the water of H3 and
its drips, the big collapse with Bran's crawl, Bran's pocket, the barrels; the rock that fills the vanilla caves, lava and gravel of the
box of the place (H3 - 10 .. ground - 6) and round the workings."""
import math, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Mix, h as hsh, stairs, slab, log
import mines_plan as P
from mines_plan import ix, in_rect

YARD = Mix({"coarse_dirt": 45, "gravel": 20, "dirt": 20, "packed_mud": 15}, 3301)
TRAIL = Mix({"coarse_dirt": 55, "gravel": 30, "dirt": 15}, 3302)
TRAIL_SLAB = Mix({"spruce_slab[type=bottom,waterlogged=false]": 70, "cobblestone_slab[type=bottom,waterlogged=false]": 30}, 3303)   # timber steps
WALL = Mix({"cobblestone": 70, "mossy_cobblestone": 30}, 3304)
SPOIL = Mix({"gravel": 40, "cobblestone": 30, "andesite": 20, "tuff": 10}, 3305)
ROCK = {1: Mix({"stone": 70, "andesite": 30}, 3306), 2: Mix({"stone": 60, "andesite": 40}, 3307), 3: Mix({"tuff": 60, "stone": 40}, 3308)}
CEIL3 = Mix({"tuff": 45, "stone": 30, "dripstone_block": 25}, 3309)
STAIR = Mix({"stone_brick_stairs": 60, "cobblestone_stairs": 40}, 3310)
COLLAPSE = Mix({"cobblestone": 45, "gravel": 30, "andesite": 15, "tuff": 10}, 3311)
PLANKS = "minecraft:spruce_planks"
FENCE = "minecraft:spruce_fence"
LANTERN_UP = "minecraft:lantern[hanging=false,waterlogged=false]"
LANTERN_DOWN = "minecraft:lantern[hanging=true,waterlogged=false]"
CHAIN = "minecraft:iron_chain[axis=y,waterlogged=false]"
CHEST = 'minecraft:chest[facing=%s,type=single,waterlogged=false]{LootTable:"last_ember:chests/r1/miner"}'
BARREL = 'minecraft:barrel[facing=%s,open=false]%s'
SENSOR = "minecraft:sculk_sensor[power=0,sculk_sensor_phase=inactive,waterlogged=false]"

def lectern_book(title, author, pages, facing):
    pg = ",".join('{raw:"%s"}' % p.replace('"', '\\"') for p in pages)
    return ('minecraft:lectern[facing=%s,has_book=true,powered=false]{Book:{id:"minecraft:written_book",count:1,components:{"minecraft:written_book_content":'
            '{title:{raw:"%s"},author:"%s",pages:[%s]}}}}' % (facing, title, author, pg))

def sign_nbt(lines):
    msgs = ",".join('"%s"' % l for l in (lines + ["", "", "", ""])[:4])
    return '{front_text:{messages:[%s],has_glowing_text:0b},back_text:{messages:["","","",""]},is_waxed:1b}' % msgs

class Ctx:
    def __init__(self, gr, rl, pl, W):
        self.gr, self.rl, self.pl, self.W = gr, rl, pl, W; self.T = rl["T"]; self.lv = W["lv"]
        self.walk = {}           # (x, z) -> surface in half blocks: the approach (feet = v / 2 + 1)
        self.crib = set()        # cells of the timbering (no ore there)
        self.noore = set()       # cells kept free of ore (cave-ins and round them, junctions, barrels)
        self.meta = {}
    def g(self, x, z): return int(self.T[ix(self.gr, x, z)])
    def horizon_of_y(self, y):
        lv = self.lv
        return 1 if y >= lv[1] - 3 else 2 if y >= lv[3] + 6 else 3

# ---------------------------------------------------------------- the yard
def yard(b, c):
    """the surface of the terrace and the approach (the top block at T, a slab over it on an odd half level), the retaining walls"""
    gr = c.gr; Y = c.pl["yard"]["Y"]; x1, z1, x2, z2 = c.pl["yard"]["r"]
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1): b.set(x, Y, z, YARD)
    for (x, z), v in c.pl["ta"].items():
        y = v // 2; b.set(x, y, z, TRAIL)
        if v % 2: b.set(x, y + 1, z, TRAIL_SLAB)
        c.walk[(x, z)] = v
    rw = c.rl["walls"]
    for (x, z) in rw["cut"]:                   # the cut face: the first ring outside the yard, Y + 1 .. its natural ground
        for y in range(Y + 1, c.g(x, z) + 1): b.set(x, y, z, WALL)
    for (x, z) in rw["fill"]:                  # the fill face: the yard's edge column down to the lower natural ground beside it
        lo = min(P.B4(gr, x + a, z + d) for a, d in ((1, 0), (-1, 0), (0, 1), (0, -1)) if not in_rect(c.pl["yard"]["r"], x + a, z + d)) if any(
            not in_rect(c.pl["yard"]["r"], x + a, z + d) for a, d in ((1, 0), (-1, 0), (0, 1), (0, -1))) else Y - 1
        for y in range(lo - 1, Y + 1): b.set(x, y, z, WALL)
        if (x, z) not in c.walk and not any((x + a, z + d) in c.walk for a in (-1, 0, 1) for d in (-1, 0, 1)):
            b.set(x, Y + 1, z, FENCE)         # a rail along the drop
    c.meta["walls"] = dict(cut=len(rw["cut"]), fill=len(rw["fill"]))

def headframe(b, c):
    """HQ T-033, 2 (card): the headframe 7 x 7, 20 high over the shaft: four posts, frames of stripped logs every 6, crossed braces of
    fence, a platform under the top, the sheave (trapdoors round a log axle) and chains down to the deck"""
    Y = c.pl["yard"]["Y"]; x1, z1, x2, z2 = P.HEADFRAME; H = 20
    for (x, z) in ((x1, z1), (x1, z2), (x2, z1), (x2, z2)):
        for y in range(Y + 1, Y + H + 1): b.set(x, y, z, log("spruce_log"))
    for y in (Y + 6, Y + 12, Y + 18):
        for x in range(x1 + 1, x2): b.set(x, y, z1, log("stripped_spruce_log", "x")); b.set(x, y, z2, log("stripped_spruce_log", "x"))
        for z in range(z1 + 1, z2): b.set(x1, y, z, log("stripped_spruce_log", "z")); b.set(x2, y, z, log("stripped_spruce_log", "z"))
    for y0 in (Y + 1, Y + 7, Y + 13):          # braces: a diagonal of fence on each face
        for k in range(5):
            b.set(x1 + 1 + k, y0 + k, z1, FENCE); b.set(x2 - 1 - k, y0 + k, z2, FENCE)
            b.set(x1, y0 + k, z2 - 1 - k, FENCE); b.set(x2, y0 + k, z1 + 1 + k, FENCE)
    for x in range(x1 + 1, x2):
        for z in range(z1 + 1, z2): b.set(x, Y + 18, z, PLANKS)
    cx, cz = (x1 + x2) // 2, (z1 + z2) // 2
    b.set(cx, Y + 18, cz, "minecraft:spruce_trapdoor[facing=north,half=bottom,open=true,powered=false,waterlogged=false]")
    ay = Y + 21                                # the sheave: an axle along z, trapdoors on the rim (radius 2) in the x-y plane
    for z in range(z1 + 1, z2): b.set(cx, ay, z, log("spruce_log", "z"))
    b.set(cx, Y + 19, cz - 2, FENCE); b.set(cx, Y + 20, cz - 2, FENCE); b.set(cx, Y + 19, cz + 2, FENCE); b.set(cx, Y + 20, cz + 2, FENCE)
    for (dx, dy, f) in ((-2, 0, "east"), (2, 0, "west"), (0, 2, None), (-1, 2, None), (1, 2, None), (-2, 1, "east"), (2, 1, "west"), (-2, -1, "east"), (2, -1, "west")):
        if f: b.set(cx + dx, ay + dy, cz, "minecraft:spruce_trapdoor[facing=%s,half=bottom,open=true,powered=false,waterlogged=false]" % f)
        else: b.set(cx + dx, ay + dy, cz, "minecraft:spruce_trapdoor[facing=north,half=top,open=false,powered=false,waterlogged=false]")
    for y in range(Y + 2, ay - 1):
        if y != Y + 18: b.set(cx, y, cz, CHAIN)
    b.set(cx, Y + 18, cz, CHAIN)
    b.set(cx, Y + 1, cz, "minecraft:spruce_trapdoor[facing=north,half=bottom,open=false,powered=false,waterlogged=false]")   # the hook's plate

def shaft(b, c):
    """the shaft 5 x 5 from H3 to the deck: platforms (spruce planks) at the levels of mines_plan.shaft_platforms, each with its opening
    over the ladder of the flight above it (the columns alternate: a fall through an opening lands on the next platform, <= 6); the deck
    at Y closes the shaft but its opening; timber rings round the shaft at every platform"""
    lv = c.lv; plats = c.W["plats"]; x1, z1, x2, z2 = P.SHAFT
    for k, py in enumerate(plats):
        for x in range(x1, x2 + 1):
            for z in range(z1, z2 + 1):
                if k == len(plats) - 1: b.set(x, py, z, ROCK[3].at(x, py, z))
                else: b.set(x, py, z, PLANKS)
        for x in range(x1 - 1, x2 + 2):          # the ring of logs round the shaft at the platform (only into rock)
            for z in (z1 - 1, z2 + 1):
                if (x, py, z) not in c.W["air"] and k: b.set(x, py, z, log("spruce_log", "x")); c.crib.add((x, py, z))
        for z in range(z1, z2 + 1):
            for x in (x1 - 1, x2 + 1):
                if (x, py, z) not in c.W["air"] and k: b.set(x, py, z, log("spruce_log", "z")); c.crib.add((x, py, z))
    ladders = []
    for k in range(len(plats) - 1):
        top, bot = plats[k], plats[k + 1]; lx = P.ladder_x(k)
        for y in range(bot + 1, top + 1): b.set(lx, y, P.LADDER_Z, "minecraft:ladder[facing=south,waterlogged=false]")
        b.set(lx, top, P.LADDER_Z - 1, ROCK[1].at(lx, top, P.LADDER_Z - 1))
        ladders.append(dict(x=lx, bottom=bot, top=top))
    c.meta["shaft"] = dict(platforms=plats, ladders=ladders)
    # the deck's railing round the headframe's inner side is the headframe itself; nothing over the opening (it is the way in)

def office(b, c):
    """the office 9 x 7 (card: cobblestone, spruce, a roof of deepslate tile stairs), the door on the south; inside the table with the
    lunch (item_display, the datapack), the lectern with the journal, the lectern with Bran's note by the table, the chest"""
    Y = c.pl["yard"]["Y"]; x1, z1, x2, z2 = 255, -81, 263, -75
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            b.set(x, Y, z, PLANKS)
            edge = x in (x1, x2) or z in (z1, z2)
            for y in range(Y + 1, Y + 5):
                if not edge: b.set(x, y, z, "minecraft:air"); continue
                corner = x in (x1, x2) and z in (z1, z2)
                b.set(x, y, z, log("spruce_log") if corner else WALL if y <= Y + 2 else PLANKS)
            if not edge: b.set(x, Y + 5, z, PLANKS)
    dx = 259
    b.set(dx, Y + 1, z2, "minecraft:spruce_door[facing=north,half=lower,hinge=left,open=false,powered=false]")
    b.set(dx, Y + 2, z2, "minecraft:spruce_door[facing=north,half=upper,hinge=left,open=false,powered=false]")
    for (x, z) in ((257, z2), (261, z2), (x1, -78), (x2, -78)):
        b.set(x, Y + 3, z, "minecraft:glass_pane[east=false,north=false,south=false,waterlogged=false,west=false]")
    # the roof: a gable along x, eaves over z1 - 1 and z2 + 1
    for k in range(5):
        y = Y + 5 + k; za, zb = z1 - 1 + k, z2 + 1 - k
        for x in range(x1 - 1, x2 + 2):
            if za < zb:
                b.set(x, y, za, stairs("deepslate_tile_stairs", "south")); b.set(x, y, zb, stairs("deepslate_tile_stairs", "north"))
            elif za == zb: b.set(x, y, za, "minecraft:deepslate_tiles")
        if za < zb:
            for z in range(za + 1, zb):
                for x in (x1, x2): b.set(x, y, z, PLANKS)
    # inside
    tx, tz = 258, -78
    for x in (tx, tx + 1): b.set(x, Y + 1, tz, slab("spruce_slab", "top").replace("]", ",waterlogged=false]"))
    b.set(tx - 1, Y + 1, tz, stairs("spruce_stairs", "west").replace("]", ",waterlogged=false]"))
    b.set(tx + 2, Y + 1, tz, stairs("spruce_stairs", "east").replace("]", ",waterlogged=false]"))
    b.set(261, Y + 1, -80, lectern_book("Журнал выработки", "Штейгер", JOURNAL, "south"))
    b.set(tx, Y + 1, tz + 1, lectern_book("Записка", "Бран", [NOTE], "north"))
    b.set(256, Y + 1, -80, CHEST % "south")
    b.set(260, Y + 4, -78, LANTERN_DOWN)
    c.meta["office"] = dict(table=[tx, Y + 1, tz], journal=[261, Y + 1, -80], note=[tx, Y + 1, tz + 1], chest=[256, Y + 1, -80], door=[dx, Y + 1, z2])

JOURNAL = ["Первый горизонт: уголь, три штрека. Выбрано до половины. Крепь целая.",
           "Второй горизонт: железо дальше от ствола, уголь ближе. Крепь сохнет. Велел ходить тише: кровля слушает.",
           "Третий горизонт: лучшая жила. Вода по колено. В конце главного штрека села кровля, жила осталась за ней. Разбирать не стали. Люди не идут.",
           "Сегодня ушли все. Обед оставили. Кто вернётся — не шумите внизу."]
NOTE = ("Наверху пусто, всё выбрано. В журнале сказано: на третьем, за обвалом, жила. Мастер велел без железа не возвращаться. "
        "Спускаюсь. Если кто найдёт это — я внизу, стучу.")

def store(b, c):
    """the store shed (a lean-to 7 x 4 open to the south): posts, a back wall of planks, a roof of slabs; a barrel (the miner's loot),
    stacked logs and planks"""
    Y = c.pl["yard"]["Y"]; x1, z1, x2, z2 = 255, -72, 261, -69
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1): b.set(x, Y + 4, z, "minecraft:spruce_slab[type=bottom,waterlogged=false]")
        b.set(x, Y + 1, z1, PLANKS); b.set(x, Y + 2, z1, PLANKS); b.set(x, Y + 3, z1, PLANKS)
    for (x, z) in ((x1, z1), (x2, z1), (x1, z2), (x2, z2)):
        for y in range(Y + 1, Y + 4): b.set(x, y, z, log("spruce_log"))
    b.set(x1 + 1, Y + 1, z1 + 1, BARREL % ("up", '{LootTable:"last_ember:chests/r1/miner"}'))
    for x in range(x1 + 3, x2):
        b.set(x, Y + 1, z1 + 1, log("spruce_log", "x"))
    b.set(x1 + 4, Y + 2, z1 + 1, log("spruce_log", "x"))
    b.set(x2 - 1, Y + 1, z1 + 2, "minecraft:spruce_slab[type=bottom,waterlogged=false]")
    c.meta["barrels"] = [dict(pos=[x1 + 1, Y + 1, z1 + 1], loot="last_ember:chests/r1/miner", where="store")]

def spoil(b, c):
    """the spoil heap in the south-west corner (card: gravel 40, cobblestone 30, andesite 20, tuff 10): a mound up to 4 high"""
    Y = c.pl["yard"]["Y"]; cx, cz = 256.0, -64.5
    for x in range(253, 260):
        for z in range(-68, -61):
            d = math.hypot((x - cx) / 1.1, z - cz)
            hgt = int(round(4.2 - d * 1.05 + (hsh(x, 0, z, 3320) - 0.5) * 0.8))
            for y in range(Y + 1, Y + 1 + max(0, hgt)): b.set(x, y, z, SPOIL)

def rails(b, c):
    """the rails from the adit's mouth to the spoil heap (yard), down the adit's rail lane, into H1 and north along A1; the shapes by the
    neighbours; the carts' places"""
    Y = c.pl["yard"]["Y"]; f1 = c.lv[1]
    for x in range(260, 283): b.set(x, Y + 1, -66, "minecraft:rail[shape=east_west,waterlogged=false]")
    b.set(259, Y + 1, -66, log("spruce_log", "x"))                       # the stop block at the end
    for (x, z), (kind, y) in c.W["inc"]["adit"]["cells"].items():
        if kind == "rail_up": b.set(x, y, z, "minecraft:rail[shape=ascending_west,waterlogged=false]"); b.set(x, y - 1, z, ROCK[1].at(x, y - 1, z))
        elif kind == "rail": b.set(x, y, z, "minecraft:rail[shape=east_west,waterlogged=false]"); b.set(x, y - 1, z, ROCK[1].at(x, y - 1, z))
    b.set(298, f1 + 1, -66, "minecraft:rail[shape=east_west,waterlogged=false]")
    b.set(299, f1 + 1, -66, "minecraft:rail[shape=north_west,waterlogged=false]")
    for z in range(-79, -66): b.set(299, f1 + 1, z, "minecraft:rail[shape=north_south,waterlogged=false]")
    c.meta["carts"] = [[261.5, Y + 1, -65.5], [263.5, Y + 1, -65.5], [281.5, Y + 1, -65.5], [299.5, f1 + 1, -73.5]]

def lights(b, c):
    """the yard is lit (card): lanterns on posts, by the office door, at the portal"""
    Y = c.pl["yard"]["Y"]
    for (x, z) in ((265, -62), (279, -62), (266, -79), (281, -77), (254, -73), (270, -66), (262, -74)):
        if b.get(x, Y + 1, z) not in (None, "minecraft:air"): continue
        b.set(x, Y + 1, z, FENCE); b.set(x, Y + 2, z, FENCE); b.set(x, Y + 3, z, LANTERN_UP)

def sign(b, c):
    """a post with the sign «Шахта» by the trail (one word): beside the approach's start, outside the banks of the trail"""
    sx, sz, sv = c.pl["pa"][-1]
    for (x, z) in ((sx - 2, sz), (sx - 2, sz - 1), (sx + 3, sz), (sx + 3, sz - 1)):
        if not P.in_place(x, z) or c.gr["ftrail"][ix(c.gr, x, z)] or (x, z) in c.walk: continue
        y = c.g(x, z)
        b.set(x, y + 1, z, FENCE); b.set(x, y + 2, z, "minecraft:spruce_sign[rotation=0,waterlogged=false]" + sign_nbt(["", "Шахта", "", ""]))
        c.meta["sign"] = [x, y + 2, z]; return
    raise SystemExit("no cell for the sign by the trail")

def portal(b, c):
    """the adit's portal in the cut face: posts and a lintel of spruce logs, a lantern beside it"""
    Y = c.pl["yard"]["Y"]; x = P.INCLINES[0][2][0]; za, zb = P.INCLINES[0][2][1] - 1, P.INCLINES[0][2][3] + 1
    for y in range(Y + 1, Y + 4):
        b.set(x, y, za, log("spruce_log")); b.set(x, y, zb, log("spruce_log"))
    for z in range(za, zb + 1): b.set(x, Y + 4, z, log("spruce_log", "z"))

# ---------------------------------------------------------------- underground
def shell_mix(c, x, y, z):
    h = c.horizon_of_y(y)
    return ROCK[h]

def underground(b, c):
    """the workings: air, floors, stairs, the shell (the rock round the air by horizon), the timbering every 4, the lanterns of H1"""
    W = c.W; lv = c.lv
    for q in W["air"]: b.set(*q, "minecraft:air")
    for nm, d in W["inc"].items():
        for (x, z), (kind, y) in d["cells"].items():
            if kind == "stair": b.set(x, y, z, stairs(STAIR.at(x, y, z).replace("minecraft:", ""), d["face"]).replace("]", ",waterlogged=false]"))
            elif kind == "land": b.set(x, y, z, ROCK[c.horizon_of_y(y)].at(x, y, z))
    # the shell
    T = c.T
    for (x, y, z) in sorted(W["air"]):
        for (a, e, f) in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            q = (x + a, y + e, z + f)
            if q in W["air"] or b.get(*q) is not None: continue
            if q[1] > T[ix(c.gr, q[0], q[2])]: continue
            h = c.horizon_of_y(q[1])
            s = CEIL3 if (h == 3 and e == 1) else ROCK[h]
            b.set(*q, s)
    timbering(b, c)

def timbering(b, c):
    """HQ T-033, 2 (card): timbering every 4 along each drift and incline: two posts of spruce log in the walls (rows floor + 1 .. + 3)
    and a cap log across in the ceiling (floor + 4); H2 is old (posts missing, stripped caps, a fence brace); H1 lanterns hang under every
    third cap"""
    W = c.W; lv = c.lv
    n = 0
    for h, segs in P.DRIFTS.items():
        if h == 4: continue
        for name, r in segs:
            ax = "x" if (r[2] - r[0]) >= (r[3] - r[1]) else "z"
            length = (r[2] - r[0] + 1) if ax == "x" else (r[3] - r[1] + 1)
            if length < 5: continue
            f = lv[h]
            for k in range(2, length - 1, 4):
                if ax == "x": x = r[0] + k; cells = [(x, z) for z in range(r[1], r[3] + 1)]; side = [(x, r[1] - 1), (x, r[3] + 1)]
                else: z = r[1] + k; cells = [(x, z) for x in range(r[0], r[2] + 1)]; side = [(r[0] - 1, z), (r[2] + 1, z)]
                if any(in_rect(P.SHAFT, *q) for q in cells + side): continue
                if any(cave_rect_near(q, 1) for q in cells): continue
                if any((q[0], f + 1, q[1]) in W["air"] for q in side): continue          # a junction: no posts in the opening
                old = h == 2
                for si, (sx, sz) in enumerate(side):
                    if old and hsh(sx, f, sz, 3330) < 0.25: continue
                    for y in range(f + 1, f + 4): b.set(sx, y, sz, log("spruce_log")); c.crib.add((sx, y, sz))
                cap = "stripped_spruce_log" if old and hsh(cells[0][0], f, cells[0][1], 3331) < 0.5 else "spruce_log"
                for (x, z) in side + cells:
                    if old and (x, z) in cells and hsh(x, f + 4, z, 3332) < 0.15: continue
                    b.set(x, f + 4, z, log(cap, "z" if ax == "x" else "x")); c.crib.add((x, f + 4, z))
                if old and hsh(cells[0][0], 1, cells[0][1], 3333) < 0.3:
                    b.set(cells[0][0], f + 3, cells[0][1], FENCE)
                if h == 1 and (k // 4) % 3 == 1:
                    m = cells[len(cells) // 2]; b.set(m[0], f + 3, m[1], LANTERN_DOWN); n += 1
    c.meta["lanterns_h1"] = n

def cave_rect_near(q, m):
    for (n, h, r, ax) in P.CAVES:
        if r[0] - m <= q[0] <= r[2] + m and r[1] - m <= q[1] <= r[3] + m: return True
    return False

def caves(b, c):
    """HQ T-033, 2: 3 cave-ins: the sensor 2 into the rock over the zone's middle (floor + 5), the hints (a post without its pair, a patch
    of cobblestone and tuff in the ceiling - not gravel: over the air of the drift it falls at the first block update (a template placed,
    a block broken beside it) and blocks the drift -, gravel on the floor); the templates are made by r1_mines.py"""
    lv = c.lv; out = []
    for (n, h, r, ax) in P.CAVES:
        f = lv[h]; x1, z1, x2, z2 = r
        mx, mz = (x1 + x2) // 2, (z1 + z2) // 2
        b.set(mx, f + 5, mz, SENSOR)
        for x in range(x1, x2 + 1):
            for z in range(z1, z2 + 1):
                if hsh(x, f, z, 3340 + n) < 0.55: b.set(x, f, z, "minecraft:gravel")
                far = abs(x - mx) >= 2 if ax == "x" else abs(z - mz) >= 2
                if far and hsh(x, f + 4, z, 3341 + n) < 0.6: b.set(x, f + 4, z, "minecraft:tuff" if hsh(x, 0, z, 3342) < 0.4 else "minecraft:cobblestone")
                elif hsh(x, f + 4, z, 3343 + n) < 0.3: b.set(x, f + 4, z, "minecraft:cobblestone")
        # the post without its pair: in the wall on one side at the zone's middle
        sx, sz = ((mx, z1 - 1) if ax == "x" else (x1 - 1, mz))
        for y in range(f + 1, f + 4): b.set(sx, y, sz, log("spruce_log")); c.crib.add((sx, y, sz))
        b.set(sx, f + 4, sz, log("spruce_log", "z" if ax == "x" else "x"))
        for x in range(x1 - 2, x2 + 3):
            for z in range(z1 - 2, z2 + 3):
                for y in range(f, f + 6): c.noore.add((x, y, z))
        out.append(dict(n=n, h=h, rect=list(r), axis=ax, floor=f, sensor=[mx, f + 5, mz], origin=[x1, f + 1, z1], post=[sx, f + 1, sz]))
    c.meta["caves"] = out

def cave_after(b, cv):
    """the cells of `cave_<n>_after`: the zone's air rows full of fallen rock (cobblestone, gravel on what is under it, andesite, tuff,
    a broken cap), the ceiling row half fallen too (holes where it came down)"""
    x1, z1, x2, z2 = cv["rect"]; f = cv["floor"]; ax = cv["axis"]; out = {}
    for x in range(x1, x2 + 1):
        for y in range(f + 1, f + 5):
            for z in range(z1, z2 + 1):
                s = b.get(x, y, z) or "minecraft:air"
                if y <= f + 3: s = ("minecraft:stripped_spruce_log[axis=%s]" % ("z" if ax == "x" else "x")) if hsh(x, y, z, 3344) < 0.08 else COLLAPSE.at(x, y, z)
                elif hsh(x, y, z, 3345) < 0.4 and "log" not in s: s = "minecraft:air"
                out[(x, y, z)] = s
    return out

def water(b, c):
    """HQ T-033, 2: knee-deep water on H3's main drift: the floor 1 lower over x WATER, waterlogged bottom slabs at both ends (half steps),
    source blocks only (the rock round them is solid: no flowing water); 4 pointed dripstones under the ceiling with a sealed water source
    over their ceiling block (the vanilla drip)"""
    f = c.lv[3]; xa, xb = P.WATER
    for x in range(xa, xb + 1):
        for z in range(-46, -43):
            b.set(x, f - 1, z, ROCK[3].at(x, f - 1, z))
            if x in (xa, xb): b.set(x, f, z, "minecraft:tuff_slab[type=bottom,waterlogged=true]")
            else: b.set(x, f, z, "minecraft:water[level=0]")
            c.noore.add((x, f + 1, z))
    for (x, z) in P.DRIPS:
        b.set(x, f + 3, z, "minecraft:pointed_dripstone[thickness=tip,vertical_direction=down,waterlogged=false]")
        b.set(x, f + 4, z, "minecraft:dripstone_block")
        b.set(x, f + 5, z, "minecraft:water[level=0]")
        for (a, e, g) in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, 1, 0)):
            q = (x + a, f + 5 + e, z + g)
            if b.get(*q) in (None, "minecraft:air") or b.get(*q) and "water" not in b.get(*q): b.set(*q, ROCK[3].at(*q))
    c.meta["water"] = dict(x=[xa, xb], drips=[list(d) for d in P.DRIPS])

def big_collapse(b, c):
    """HQ T-033, 2: the old big collapse at the end of D1b: cobblestone and gravel on a solid floor, broken timber, its front a slope
    (1 then 2 rows), the pickaxe (item_display, the datapack) on it; Bran's crawl on its east side: fresh gravel 2 x 2 through it, a dead
    torch (item_display) at its mouth"""
    f = c.lv[3]; x1, z1, x2, z2 = P.BIG["rect"]; fr = P.BIG["front"]; la = P.BIG["lane"]
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            rows = 1 if z == fr else 2 if z == fr - 1 else 3
            if x in la and z >= fr - 1: rows = 0          # the mouth of the crawl is dug out: its gravel face shows
            for y in range(f + 1, f + 1 + rows):
                crawl = x in la and y <= f + 2 and z <= fr - 2
                if crawl: b.set(x, y, z, "minecraft:gravel")
                else: b.set(x, y, z, "minecraft:stripped_spruce_log[axis=x]" if hsh(x, y, z, 3350) < 0.1 else COLLAPSE.at(x, y, z) if hsh(x, y, z, 3351) < 0.6 else "minecraft:cobblestone")
            for y in range(f, f + 5): c.noore.add((x, y, z))
    # gravel never over air: the front rows sit on the floor; the crawl's upper gravel sits on its lower one
    c.meta["big"] = dict(rect=[x1, z1, x2, z2], pick=[x1 + 0.5, f + 2.45, fr + 0.75], torch=[la[0] + 1.0, f + 1.04, fr - 0.3],
                         crawl=[la[0], f + 1, fr - 2, la[1], f + 2, z1])

def pocket(b, c):
    """Bran's pocket behind the big collapse (8 x 6 x 3): its barrel (chests/r1/common), Bran faces the vein (the west wall)"""
    f = c.lv[4]; x1, z1, x2, z2 = P.DRIFTS[4][0][1]
    b.set(x2, f + 1, z1, BARREL % ("up", '{LootTable:"last_ember:chests/r1/common"}'))
    c.noore.add((x2 + 1, f + 1, z1)); c.noore.add((x2, f + 1, z1 - 1))
    c.meta["barrels"].append(dict(pos=[x2, f + 1, z1], loot="last_ember:chests/r1/common", where="pocket"))
    c.meta["bran"] = [x1 + 1.5, f + 1, (z1 + z2) / 2 + 0.5, 90]     # yaw 90: facing west (the vein)
    c.meta["pocket"] = [x1, f + 1, z1, x2, f + 3, z2]
    c.meta["peace_items"] = [[x1 + 1.5, f + 1.1, (z1 + z2) / 2 + 0.5]]

def barrels(b, c):
    """the barrels of the workings (HQ T-033, 2: 4..6; two with chests/r1/miner): H1 (miner) at the north end of A1, H2 (empty) at the
    corner of B1, H3 (empty) in the wall of D2; each in the wall at the feet row"""
    f1, f2, f3 = c.lv[1], c.lv[2], c.lv[3]
    for (pos, loot, where, face) in (((301, f1 + 1, -80), "last_ember:chests/r1/miner", "H1", "west"), ((262, f2 + 1, -72), None, "H2", "east"),
                                    ((276, f3 + 1, -60), None, "H3", "west")):
        b.set(*pos, BARREL % (face, '{LootTable:"%s"}' % loot if loot else ""))
        c.noore.add(pos)
        c.meta["barrels"].append(dict(pos=list(pos), loot=loot, where=where))

def ore(b, c):
    """HQ T-033, 2: the ore by horizon in strips along the drifts' walls, exact numbers (mines_plan.ORE); only shell cells of rock (not the
    timbering, not the cave-ins and their surroundings, not the barrels), each with a face to the drift's air"""
    W = c.W
    def skip(x, y, z):
        s = b.get(x, y, z)
        return (x, y, z) in c.crib or (x, y, z) in c.noore or s is None or not re.search(r"minecraft:(stone|andesite|tuff|dripstone_block)$", s)
    wl = P.walls(W, skip)
    got = {}; used = set()
    def place(cands, n, blk, salt, order, where):
        cs = [q for q in cands if (q[0], q[1], q[2]) not in used]
        pk = P.strips(cs, n, salt, order)
        if len(pk) != n: raise SystemExit("STOP (HQ T-033, 2): %d of %d %s fit in strips on %s" % (len(pk), n, blk, where))
        for q in pk: b.set(q[0], q[1], q[2], "minecraft:" + blk); used.add((q[0], q[1], q[2]))
        got[(where, blk)] = got.get((where, blk), 0) + n
    sx, sz = (P.SHAFT[0] + P.SHAFT[2]) / 2, (P.SHAFT[1] + P.SHAFT[3]) / 2
    dist = lambda q: abs(q[0] - sx) + abs(q[2] - sz)
    h1 = wl[1]
    for k, seg in enumerate(("A1", "A2", "A3")):
        place([q for q in h1 if q[4] == seg], 40, "coal_ore", 3360 + k, lambda q: q[5], "H1")
    place([q for q in h1 if q[4] == "A2" and q[0] < 280], 15, "copper_ore", 3364, lambda q: q[0], "H1")
    h2 = wl[2]
    near = [q for q in h2 if q[4] in ("B1", "B1b", "B2a", "B2b")]
    place(near, 40, "coal_ore", 3365, dist, "H2")
    far = [q for q in h2 if q[4] in ("B2d", "K2a", "K2b", "K2c") or q[4] == "B2c" and q[0] >= 296]
    place(far, 40, "iron_ore", 3366, lambda q: -dist(q), "H2")
    mid = [q for q in h2 if q[4] in ("K1a", "K1b", "K1c") or q[4] == "B2c" and q[0] < 296]
    place(mid, 25, "copper_ore", 3367, dist, "H2")
    place(wl[3], 35, "iron_ore", 3368, lambda q: q[5], "H3")
    place(wl[4], 25, "iron_ore", 3369, lambda q: q[5], "pocket")
    place(wl[4], 12, "lapis_ore", 3370, lambda q: -q[5], "pocket")
    c.meta["ore"] = {"%s %s" % k: v for k, v in sorted(got.items())}

def fill(b, c):
    """HQ T-033, 2: in the box of the place from H3 - 10 up to the ground - 6 only our workings and solid rock: the vanilla caves, lava,
    water, gravel, infested stone there (and any of them within 2 of the workings) become the rock of the horizon"""
    gr = c.gr; lo = c.lv[3] - 10; n = 0
    near = set()
    for (x, y, z) in c.W["air"]:
        for a in (-2, -1, 0, 1, 2):
            for e in (-2, -1, 0, 1, 2):
                for f in (-2, -1, 0, 1, 2): near.add((x + a, y + e, z + f))
    for (x, y, z), nm in sorted(gr["under"].items()):
        if b.get(x, y, z) is not None or (x, y, z) in c.W["air"]: continue
        if not (P.PLACE[0] <= x <= P.PLACE[2] and P.PLACE[1] <= z <= P.PLACE[3]): continue
        t = c.g(x, z)
        if not ((lo <= y <= t - P.FILL_BELOW) or ((x, y, z) in near and y <= t - 1)): continue
        if re.search(r"ore$", nm): pass
        b.set(x, y, z, ROCK[c.horizon_of_y(y)]); n += 1
    c.meta["filled"] = n

def build(gr, rl, pl, W):
    from lib import B
    b = B("mines"); c = Ctx(gr, rl, pl, W)
    yard(b, c)
    underground(b, c)
    shaft(b, c)
    headframe(b, c)
    office(b, c)
    store(b, c)
    spoil(b, c)
    portal(b, c)
    rails(b, c)
    lights(b, c)
    sign(b, c)
    caves(b, c)
    water(b, c)
    big_collapse(b, c)
    pocket(b, c)
    barrels(b, c)
    ore(b, c)
    fill(b, c)
    return b, c
