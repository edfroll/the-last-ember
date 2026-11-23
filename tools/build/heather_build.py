"""T-031: the models of the Village of Heather: the peasant houses with their oddities (HQ T-031, 2), the miller's house, the church with
the bell tower, the mill, the well, the gardens with swords, the pasture. Blocks go into a lib.B (absolute coordinates); the points the
datapack needs go into `meta`. Read by tools/build/r1_heather.py.

A house is built in its own frame: u along the front (0 = left seen from the street), w into the depth (0 = the front wall), y absolute;
`face` is the side the door looks to (the street)."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Mix, h as hsh, stairs, slab, lantern

LO = Mix({"cobblestone": 40, "mossy_cobblestone": 20, "stone": 20, "tuff": 10, "andesite": 10}, 3101)        # card: houses, low
FILL = Mix({"spruce_planks": 60, "packed_mud": 40}, 3102)                                                   # card: houses, high
LOG = "minecraft:dark_oak_log[axis=y]"
CHURCH = Mix({"bricks": 50, "mud_bricks": 30, "stone_bricks": 20}, 3103)
STREET = Mix({"gravel": 40, "coarse_dirt": 40, "cobblestone": 20}, 3104)
WALLB = Mix({"cobblestone": 50, "mossy_cobblestone": 30, "stone": 20}, 3105)     # retaining walls (the palette of the houses, low)
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}
LEFT = {"south": "west", "north": "east", "west": "north", "east": "south"}      # seen from the street, looking at the front
RIGHT = {v: OPP[v] for v, _ in []} or {k: OPP[v] for k, v in LEFT.items()}
DXZ = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}

class Frame:
    """house frame: footprint r = (x1, z1, x2, z2), face = where the door looks; W along the front, D deep"""
    def __init__(self, r, face):
        self.r, self.face = r, face
        x1, z1, x2, z2 = r
        if face in ("south", "north"): self.W, self.D = x2 - x1 + 1, z2 - z1 + 1
        else: self.W, self.D = z2 - z1 + 1, x2 - x1 + 1
    def xz(self, u, w):
        x1, z1, x2, z2 = self.r
        return {"south": (x1 + u, z2 - w), "north": (x2 - u, z1 + w), "west": (x1 + w, z1 + u), "east": (x2 - w, z2 - u)}[self.face]
    def d(self, local):
        """local direction (out, in, left, right) -> world"""
        return {"out": self.face, "in": OPP[self.face], "left": LEFT[self.face], "right": OPP[LEFT[self.face]]}[local]

def put(b, f, u, w, y, s): x, z = f.xz(u, w); b.set(x, y, z, s)
def p3(f, u, w, y): x, z = f.xz(u, w); return [x, y, z]
def st(block, f, local, half="bottom"): return stairs(block, f.d(local), half)

def door(f, local="out", half="lower", hinge="left", block="spruce_door", open_=False):
    return "minecraft:%s[facing=%s,half=%s,hinge=%s,open=%s,powered=false]" % (block, f.d(local), half, hinge, "true" if open_ else "false")

def lectern_book(title, author, pages, facing):
    pg = ",".join('{raw:"%s"}' % p.replace('"', '\\"') for p in pages)
    return ('minecraft:lectern[facing=%s,has_book=true,powered=false]{Book:{id:"minecraft:written_book",count:1,components:{"minecraft:written_book_content":'
            '{title:{raw:"%s"},author:"%s",pages:[%s]}}}}' % (facing, title, author, pg))

def sign_nbt(lines):
    msgs = ",".join('"%s"' % l for l in (lines + ["", "", "", ""])[:4])
    return '{front_text:{messages:[%s],has_glowing_text:0b},back_text:{messages:["","","",""]},is_waxed:1b}' % msgs

# ---------------------------------------------------------------- the shell of a house
def shell(b, f, L, storeys, ground_lo, seed, roof="spruce", door_u=None, windows=True, meta=None):
    """foundation (LO from the lowest ground to L), floor at L, walls: LO up to L+1, above FILL with dark oak posts at the corners and
    by the door; storey 4 high; a gable roof of spruce stairs (or hay steps) along u; returns (top, door_u)"""
    W, D = f.W, f.D; top = L + 4 * storeys
    du = W // 2 if door_u is None else door_u
    for u in range(W):
        for w in range(D):
            edge = u in (0, W - 1) or w in (0, D - 1)
            for y in range(min(ground_lo, L) - 1, L): put(b, f, u, w, y, LO)
            put(b, f, u, w, L, LO if edge else "minecraft:spruce_planks")
            for y in range(L + 1, top + 1):
                if not edge: put(b, f, u, w, y, "minecraft:air"); continue
                corner = u in (0, W - 1) and w in (0, D - 1)
                if corner: put(b, f, u, w, y, LOG)
                elif y <= L + 1: put(b, f, u, w, y, LO)
                elif (y - L) % 4 == 0: put(b, f, u, w, y, "minecraft:dark_oak_log[axis=%s]" % ("x" if (w in (0, D - 1)) == (f.face in ("north", "south")) else "z"))
                else: put(b, f, u, w, y, FILL)
            if storeys > 1 and not edge:
                put(b, f, u, w, L + 4, "minecraft:spruce_planks")
    # the posts by the door
    for y in range(L + 2, top + 1):
        if (y - L) % 4: put(b, f, du - 1, 0, y, LOG); put(b, f, du + 1, 0, y, LOG)
    roof_(b, f, top, roof, seed)
    return top, du

def roof_(b, f, top, kind, seed):
    """gable along u: eaves at w = -1 and w = D on top + 1, rising 1 per row inwards; gable ends (u = 0, W - 1) filled; overhang 1 at
    the gable ends. Hay roofs: hay steps (full blocks) instead of stairs (the card: thatch only far from lanterns and hearths)"""
    W, D = f.W, f.D
    n = (D + 1) // 2 + 1
    for k in range(n + 1):
        y = top + 1 + k
        wf, wb = -1 + k, D - k
        if wf > wb: break
        for u in range(-1, W + 1):
            if wf == wb:
                put(b, f, u, wf, y, "minecraft:spruce_slab[type=bottom]" if kind == "spruce" else "minecraft:hay_block[axis=x]")
                continue
            if wf == wb - 1:
                for w in (wf, wb): put(b, f, u, w, y, "minecraft:spruce_planks" if kind == "spruce" else "minecraft:hay_block[axis=y]")
                continue
            if kind == "spruce":
                put(b, f, u, wf, y, st("spruce_stairs", f, "in")); put(b, f, u, wb, y, st("spruce_stairs", f, "out"))
            else:
                put(b, f, u, wf, y, "minecraft:hay_block[axis=y]"); put(b, f, u, wb, y, "minecraft:hay_block[axis=y]")
            if u in (0, W - 1):
                for w in range(wf + 1, wb): put(b, f, u, w, y, FILL if (u + w + y) % 5 else LOG)
        # under the eaves at the gable overhang nothing
    return top + n

def window(b, f, u, w, y, lit=False, side_out="out"):
    """a window in the wall at (u, w): glass pane; a lit window is a lantern box: the lantern one cell inside behind the pane, closed
    to the room by tinted glass (HQ T-031, 2: the windows glow, the depth of the room stays dark - block light 0, spawning possible)"""
    put(b, f, u, w, y, "minecraft:glass_pane")
    if lit:
        di = {"out": (0, 1), "left": (1, 0), "right": (-1, 0), "in": (0, -1)}[side_out]
        u2, w2 = u + di[0], w + di[1]
        put(b, f, u2, w2, y, lantern())
        put(b, f, u2 + di[0], w2 + di[1], y, "minecraft:tinted_glass")
        for (a, c) in ((di[1], di[0]), (-di[1], -di[0])): put(b, f, u2 + a, w2 + c, y, LO)
        put(b, f, u2, w2, y - 1, LO); put(b, f, u2, w2, y + 1, FILL)
        return f.xz(u2, w2)

def furnish_room(b, f, L, u1, w1, u2, w2, seed, reverse=False):
    """a table with two chairs and a bed (the reversed house: the bed's head to the door, the chairs facing away from the table)"""
    tu, tw = (u1 + u2) // 2, (w1 + w2) // 2
    put(b, f, tu, tw, L + 1, "minecraft:spruce_fence"); put(b, f, tu, tw, L + 2, "minecraft:spruce_pressure_plate[powered=false]")
    put(b, f, tu - 1, tw, L + 1, st("spruce_stairs", f, "right" if reverse else "left"))
    put(b, f, tu + 1, tw, L + 1, st("spruce_stairs", f, "left" if reverse else "right"))

# ---------------------------------------------------------------- the houses
def house(b, spec, ground_lo, meta):
    """one house of the street with its oddity (spec from heather_plan.house_sites); returns its points"""
    kind = spec["kind"]; f = Frame(spec["r"], spec["face"]); L = spec["L"]; sd = 3200 + spec["k"] * 17
    out = dict(k=spec["k"], kind=kind, r=list(spec["r"]), face=spec["face"], L=L, door=list(spec["door"]))
    W, D = f.W, f.D
    hay = kind in ("walled", "ladder") and spec["k"] >= 5            # two thatched roofs, far from lanterns and hearths
    if kind == "deep":
        top, du = shell(b, f, L, 1, ground_lo, sd, "spruce")
        deep(b, f, L, du, out)
    elif kind == "walled":
        top, du = shell(b, f, L, spec["storeys"], ground_lo, sd, "hay" if hay else "spruce")
        walled(b, f, L, du, out)
    elif kind == "ladder":
        top, du = shell(b, f, L, 2, ground_lo, sd, "hay" if hay else "spruce")
        ladder_house(b, f, L, du, out)
    elif kind == "roof":
        top, du = flat_roof_house(b, f, L, ground_lo, sd, out)
    elif kind == "reversed":
        top, du = shell(b, f, L, 1, ground_lo, sd, "spruce")
        reversed_(b, f, L, du, out)
    # the threshold: a step from the street (the street by the door may be half a block higher: a slab)
    out["inside"] = p3(f, du, 2, L + 1)
    out["front"] = list(f.xz(du, -1))
    out["top"] = top
    return out

def front_windows(b, f, L, du, lit_u=None, skip=()):
    lit = None
    for u in range(2, f.W - 2, 3):
        if abs(u - du) <= 1 or u in skip: continue
        p = window(b, f, u, 0, L + 2, lit=(lit is None and (lit_u is None or u == lit_u)))
        if p and lit is None: lit = p
    for w in range(2, f.D - 2, 3):
        window(b, f, 0, w, L + 2); window(b, f, f.W - 1, w, L + 2)
    return lit

def walled(b, f, L, du, out):
    """1: the door walled up from outside (the door frame stays, the opening is cobble with moss), the way in is a window at the ground
    (an opening 1 x 2 beside the door, the bot walks through it); inside the note «Марта» on a lectern"""
    put(b, f, du, 0, L + 1, "minecraft:mossy_cobblestone"); put(b, f, du, 0, L + 2, "minecraft:cobblestone")
    put(b, f, du, -1, L + 1, "minecraft:cobblestone_wall"); put(b, f, du, -1, L + 2, "minecraft:mossy_cobblestone_wall")   # the walling outside
    wu = du + 2
    put(b, f, wu, 0, L + 1, "minecraft:air"); put(b, f, wu, 0, L + 2, "minecraft:air")
    put(b, f, wu, 0, L + 3, "minecraft:spruce_trapdoor[facing=%s,half=top,open=false]" % f.d("in"))      # the lintel of the window
    lit = front_windows(b, f, L, du, skip=(wu, wu - 1, wu + 1))
    out["window_in"] = list(f.xz(wu, 0)); out["lantern"] = lit
    lu, lw = 1, f.D - 2
    out["lectern"] = p3(f, lu, lw, L + 1)
    out["note"] = 1
    furnish_room(b, f, L, 2, 2, f.W - 3, f.D - 3, 0)
    put(b, f, f.W - 2, f.D - 2, L + 1, "minecraft:red_bed[facing=%s,occupied=false,part=head]" % f.d("in"))
    put(b, f, f.W - 2, f.D - 3, L + 1, "minecraft:red_bed[facing=%s,occupied=false,part=foot]" % f.d("in"))

def ladder_house(b, f, L, du, out):
    """2: the stair to the upper storey runs into the ceiling; the upper storey is entered by an outer stair (on the right side wall, up
    to a door at the back corner); upstairs the beds are made on the wall (wool pillow and blanket in the wall, frames of trapdoors)"""
    W, D = f.W, f.D
    put(b, f, du, 0, L + 1, door(f, "out", "lower")); put(b, f, du, 0, L + 2, door(f, "out", "upper"))
    # the inner stair along the left wall: 3 steps up into the ceiling (a full planks block over the last step)
    for k in range(3):
        put(b, f, 1, 1 + k, L + 1 + k, st("spruce_stairs", f, "in"))
        for y in range(L + 1, L + 1 + k): put(b, f, 1, 1 + k, y, "minecraft:spruce_planks")
    put(b, f, 1, 4, L + 4, "minecraft:spruce_planks")
    lit = front_windows(b, f, L, du)
    out["lantern"] = lit
    out["lectern"] = p3(f, W - 2, 2, L + 1); out["note"] = 2
    furnish_room(b, f, L, 3, 3, W - 3, D - 2, 0)
    # the outer stair: along the right side wall outside (u = W), from the front corner to a landing at the back, door at the back of
    # the right wall on the upper storey (floor L + 4, feet L + 5): 4 steps, a landing, 0 steps more (one march: 4 up from the street +1)
    ou = W
    rise = 4
    for k in range(rise):
        put(b, f, ou, 1 + k, L + 1 + k, st("spruce_stairs", f, "in"))
        for y in range(L, L + 1 + k): put(b, f, ou, 1 + k, y, LO)
        for y in range(L + 2 + k, L + 5 + k): put(b, f, ou, 1 + k, y, "minecraft:air")
    for w in range(1 + rise, 1 + rise + 2):
        for y in range(L, L + 5): put(b, f, ou, w, y, LO)
        for y in range(L + 5, L + 8): put(b, f, ou, w, y, "minecraft:air")
        put(b, f, ou + 1, w, L + 5, "minecraft:spruce_fence")
    for k in range(rise): put(b, f, ou + 1, 1 + k, L + 2 + k, "minecraft:spruce_fence")
    dw = 1 + rise
    put(b, f, W - 1, dw, L + 5, door(f, "right", "lower")); put(b, f, W - 1, dw, L + 6, door(f, "right", "upper"))
    out["upper_door"] = p3(f, W, dw, L + 5)
    out["upper_in"] = p3(f, W - 2, dw, L + 5)
    # the beds made on the wall: on the left wall upstairs, two beds: pillow (white wool) up, blanket (red wool) 2 below, trapdoor frames
    for (bw, col) in ((2, "red"), (D - 3, "blue")):
        put(b, f, 0, bw, L + 7, "minecraft:white_wool"); put(b, f, 0, bw, L + 6, "minecraft:%s_wool" % col); put(b, f, 0, bw, L + 5, "minecraft:%s_wool" % col)
        put(b, f, 1, bw, L + 5, "minecraft:spruce_trapdoor[facing=%s,half=bottom,open=true]" % f.d("right"))
    put(b, f, W - 2, 2, L + 5, "minecraft:spruce_trapdoor[facing=%s,half=bottom,open=false]" % f.d("out"))    # a chest-like stool
    window(b, f, du, 0, L + 6); window(b, f, 0, D // 2, L + 6)

def flat_roof_house(b, f, L, ground_lo, sd, out):
    """3: a flat roof with a parapet (spruce fence), a table laid on it with chairs round, a ladder up the left side wall; inside the
    note «Хозяйка» and the table downstairs (where somebody always sits)"""
    W, D = f.W, f.D; top = L + 4
    for u in range(W):
        for w in range(D):
            edge = u in (0, W - 1) or w in (0, D - 1)
            for y in range(min(ground_lo, L) - 1, L): put(b, f, u, w, y, LO)
            put(b, f, u, w, L, LO if edge else "minecraft:spruce_planks")
            for y in range(L + 1, top):
                if not edge: put(b, f, u, w, y, "minecraft:air"); continue
                corner = u in (0, W - 1) and w in (0, D - 1)
                put(b, f, u, w, y, LOG if corner else (LO if y <= L + 1 else FILL))
            put(b, f, u, w, top, "minecraft:spruce_planks" if not edge else "minecraft:dark_oak_planks")
            if edge: put(b, f, u, w, top + 1, "minecraft:spruce_fence")
    du = W // 2
    put(b, f, du, 0, L + 1, door(f, "out", "lower")); put(b, f, du, 0, L + 2, door(f, "out", "upper"))
    lit = front_windows(b, f, L, du)
    out["lantern"] = lit
    # the ladder up the left side wall (outside, u = -1), from the ground at the front to the roof; a gap in the parapet over it
    lw = 2
    for y in range(L + 1, top + 2): put(b, f, -1, lw, y, "minecraft:ladder[facing=%s,waterlogged=false]" % f.d("left"))
    put(b, f, 0, lw, top + 1, "minecraft:air")
    out["ladder"] = p3(f, -1, lw, L + 1); out["roof"] = p3(f, 1, lw, top + 1)
    # the table on the roof: 2 x 1 of spruce slabs (top) on fences? -> trapdoors as a table top, chairs (stairs) round it
    tu, tw = W // 2, D // 2
    for a in (0, 1):
        put(b, f, tu + a - 1, tw, top + 1, "minecraft:spruce_trapdoor[facing=%s,half=top,open=false]" % f.d("out"))
    put(b, f, tu - 2, tw, top + 1, st("spruce_stairs", f, "left")); put(b, f, tu + 1, tw, top + 1, st("spruce_stairs", f, "right"))
    put(b, f, tu - 1, tw - 1, top + 1, st("spruce_stairs", f, "out")); put(b, f, tu, tw + 1, top + 1, st("spruce_stairs", f, "in"))
    out["roof_table"] = p3(f, tu - 1, tw, top + 1)
    out["roof_chair"] = p3(f, tu, tw + 1, top + 1)
    # downstairs: the same table, laid
    furnish_room(b, f, L, 2, 2, W - 3, D - 3, 0)
    out["lectern"] = p3(f, W - 2, D - 2, L + 1); out["note"] = 3
    return top + 1, du

def deep(b, f, L, du, out):
    """4: the house without a floor: the cellar is open, a smaller house stands in it (lit inside, chest 1); the way down: a ledge along
    the front wall, then a stair along the left wall (marches with a landing, 3 of head room), the way out the same way (no jumps)"""
    W, D = f.W, f.D; depth = 7; bot = L - depth
    put(b, f, du, 0, L + 1, door(f, "out", "lower")); put(b, f, du, 0, L + 2, door(f, "out", "upper"))
    lit = front_windows(b, f, L, du)
    out["lantern"] = lit
    # the pit: u 1..W-2, w 2..D-2 down to bot (the walls of the pit: LO), the ledge w = 1 at L (the door side), the lectern on it
    for u in range(1, W - 1):
        for w in range(2, D - 1):
            for y in range(bot + 1, L + 1): put(b, f, u, w, y, "minecraft:air")
            put(b, f, u, w, bot, "minecraft:coarse_dirt" if (u + w) % 3 else "minecraft:dirt")
    for u in range(0, W):
        for w in range(1, D):
            if 1 <= u <= W - 2 and 2 <= w <= D - 2: continue
            for y in range(bot - 1, L): put(b, f, u, w, y, LO)
    for u in range(0, W):
        for y in range(bot - 1, L): put(b, f, u, D - 1, y, LO)
    # a fence along the ledge edge (not over the stair head)
    for u in range(3, W - 1): put(b, f, u, 2, L + 1, "minecraft:spruce_fence") if False else None
    # the stair: from the ledge (w 1) at u 1 down along the left wall (u 1) southwards... w 2..D-2: 7 steps down to bot + 1 surface
    for k in range(depth):
        w = 2 + k
        y = L - 1 - k                          # the stair block top = L - k (standing L - k + ... ) : step down 1 per cell (stairs)
        put(b, f, 1, w, y, st("spruce_stairs", f, "out"))
        for yy in range(bot, y): put(b, f, 1, w, yy, LO)
    out["stair_top"] = p3(f, 1, 1, L + 1); out["stair_bot"] = p3(f, 1, 2 + depth, bot + 1)
    # the ledge railing: fences along w = 2 from u 2 (beside the stair) to W - 2, a gap at the stair (u 1)
    for u in range(2, W - 1): put(b, f, u, 1, L + 1, "minecraft:air")
    for u in range(3, W - 1): put(b, f, u, 2, L + 1, "minecraft:spruce_fence")
    put(b, f, 2, 2, L + 1, "minecraft:spruce_fence")
    # the small house below: u 3..W-2 (5 wide), w 3..D-3, floor bot, walls 3, a little gable; door to the stair side (left, u 3)
    su1, su2, sw1, sw2 = 3, W - 2, 3, D - 3
    for u in range(su1, su2 + 1):
        for w in range(sw1, sw2 + 1):
            edge = u in (su1, su2) or w in (sw1, sw2)
            put(b, f, u, w, bot, "minecraft:spruce_planks")
            for y in range(bot + 1, bot + 4):
                put(b, f, u, w, y, (LOG if (u in (su1, su2) and w in (sw1, sw2)) else (LO if y == bot + 1 else FILL)) if edge else "minecraft:air")
            put(b, f, u, w, bot + 4, "minecraft:spruce_slab[type=bottom]" if edge else "minecraft:spruce_planks")
    dw = (sw1 + sw2) // 2
    put(b, f, su1, dw, bot + 1, door(f, "left", "lower", block="spruce_door")); put(b, f, su1, dw, bot + 2, door(f, "left", "upper", block="spruce_door"))
    put(b, f, su1 + 1, sw2 - 1, bot + 1, "minecraft:chest[facing=%s,type=single,waterlogged=false]{LootTable:\"last_ember:chests/r1/common\"}" % f.d("left"))
    put(b, f, su2 - 1, sw1 + 1, bot + 1, lantern())               # «в нём тоже горит свет»
    put(b, f, su2 - 1, sw2 - 1, bot + 1, "minecraft:spruce_fence"); put(b, f, su2 - 1, sw2 - 1, bot + 2, "minecraft:spruce_pressure_plate[powered=false]")
    window(b, f, su1, dw + 1, bot + 2); window(b, f, su2, dw, bot + 2)
    out["chest"] = p3(f, su1 + 1, sw2 - 1, bot + 1)
    out["small_door"] = p3(f, su1 - 1, dw, bot + 1)
    out["small_in"] = p3(f, su1 + 1, dw, bot + 1)
    out["lectern"] = p3(f, W - 2, 1, L + 1); out["note"] = 4
    out["bot"] = bot

def reversed_(b, f, L, du, out):
    """5: all turned by 180°: the hearth by the door (inside, at the front wall), the door in the hearth: the back wall has a fireplace
    portal of bricks with an unlit campfire on its floor (no burning in passing) and a door behind it to the yard; the bed's head and
    the chairs turned away from the table; the lectern «Бран, ученик»"""
    W, D = f.W, f.D
    put(b, f, du, 0, L + 1, door(f, "out", "lower")); put(b, f, du, 0, L + 2, door(f, "out", "upper"))
    lit = front_windows(b, f, L, du)
    out["lantern"] = lit
    # the hearth by the door: bricks round a campfire (lit, the smoke goes up a chimney in the front wall corner)
    hu = du + 2 if du + 2 < W - 1 else du - 2
    put(b, f, hu, 1, L + 1, "minecraft:campfire[facing=%s,lit=true,signal_fire=false,waterlogged=false]" % f.d("in"))
    for (a, c) in ((-1, 0), (1, 0)): put(b, f, hu + a, 1, L + 1, "minecraft:bricks"); put(b, f, hu + a, 1, L + 2, "minecraft:bricks")
    put(b, f, hu, 1, L + 2, "minecraft:air"); put(b, f, hu, 1, L + 3, "minecraft:bricks")
    for (a, c) in ((-1, 0), (0, 0), (1, 0)): put(b, f, hu + a, 1, L + 4, "minecraft:bricks")
    for y in range(L + 4, L + 9): put(b, f, hu, 0, y, "minecraft:bricks")
    out["hearth"] = p3(f, hu, 1, L + 1)
    # the door in the hearth: the back wall at du: a portal 3 wide of bricks, inside it the unlit campfire on the floor, the door behind
    bw = D - 1
    for y in range(L + 1, L + 4):
        put(b, f, du - 1, bw - 1, y, "minecraft:bricks"); put(b, f, du + 1, bw - 1, y, "minecraft:bricks")
    put(b, f, du - 1, bw - 1, L + 4, "minecraft:bricks"); put(b, f, du, bw - 1, L + 4, "minecraft:bricks"); put(b, f, du + 1, bw - 1, L + 4, "minecraft:bricks")
    put(b, f, du, bw - 1, L + 1, "minecraft:campfire[facing=%s,lit=false,signal_fire=false,waterlogged=false]" % f.d("out"))
    put(b, f, du, bw - 1, L + 2, "minecraft:air"); put(b, f, du, bw - 1, L + 3, "minecraft:air")
    put(b, f, du, bw, L + 1, door(f, "in", "lower", hinge="right")); put(b, f, du, bw, L + 2, door(f, "in", "upper", hinge="right"))
    for y in range(L + 1, L + 4): put(b, f, du, bw + 1, y, "minecraft:air")
    put(b, f, du, bw + 1, L, LO)
    out["back_door"] = p3(f, du, bw + 1, L + 1)
    # the room turned round: the bed's head to the door, the chairs away from the table
    put(b, f, 1, 2, L + 1, "minecraft:red_bed[facing=%s,occupied=false,part=head]" % f.d("out"))
    put(b, f, 1, 3, L + 1, "minecraft:red_bed[facing=%s,occupied=false,part=foot]" % f.d("out"))
    furnish_room(b, f, L, 2, 3, W - 3, D - 3, 0, reverse=True)
    out["lectern"] = p3(f, W - 2, D - 3, L + 1); out["note"] = 5

def miller_house(b, r, face, L, ground_lo, meta):
    """the miller's house by the mill: a plain house, the door locked (an oak door barred from inside by a full block: the contract
    «Вересковый волк» takes it away later)"""
    f = Frame(r, face)
    top, du = shell(b, f, L, 1, ground_lo, 3299, "spruce")
    put(b, f, du, 0, L + 1, door(f, "out", "lower", block="dark_oak_door")); put(b, f, du, 0, L + 2, door(f, "out", "upper", block="dark_oak_door"))
    put(b, f, du, 1, L + 1, "minecraft:spruce_planks"); put(b, f, du, 1, L + 2, "minecraft:spruce_planks")     # the bar
    front_windows(b, f, L, du, lit_u=-1)
    furnish_room(b, f, L, 2, 2, f.W - 3, f.D - 3, 0)
    meta["miller"] = dict(r=list(r), face=face, L=L, door=list(f.xz(du, 0)), bar=p3(f, du, 1, L + 1))

# ---------------------------------------------------------------- the well, the gardens, the scarecrows, the pasture
def well(b, cx, cz, L, meta):
    """the well in the middle of the square: a curb of mossy stone bricks 5 x 5 (walls 2 high), inside to the brim poppies on grass,
    a roof on 4 dark oak posts"""
    for a in range(-2, 3):
        for c in range(-2, 3):
            edge = abs(a) == 2 or abs(c) == 2
            for y in range(L - 3, L + 1): b.set(cx + a, y, cz + c, "minecraft:mossy_stone_bricks" if edge else "minecraft:dirt")
            if edge:
                b.set(cx + a, L + 1, cz + c, "minecraft:mossy_stone_bricks")
                b.set(cx + a, L + 2, cz + c, "minecraft:mossy_stone_brick_slab[type=bottom,waterlogged=false]")
            else:
                b.set(cx + a, L + 1, cz + c, "minecraft:grass_block[snowy=false]"); b.set(cx + a, L + 2, cz + c, "minecraft:poppy")
    for (a, c) in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
        for y in range(L + 3, L + 6): b.set(cx + a, y, cz + c, "minecraft:dark_oak_fence")
    for a in range(-3, 4):
        b.set(cx + a, L + 6, cz - 1, "minecraft:spruce_stairs[facing=south,half=bottom,shape=straight]")
        b.set(cx + a, L + 6, cz + 1, "minecraft:spruce_stairs[facing=north,half=bottom,shape=straight]")
        b.set(cx + a, L + 6, cz, "minecraft:spruce_slab[type=top]")
        b.set(cx + a, L + 7, cz, "minecraft:spruce_slab[type=bottom]")
    meta["well"] = [cx, L + 1, cz]

def small_sword(b, x, y, z, k):
    """a small sword in a bed (card: blade tuff wall 2..3, guard a stone brick slab): the grip of a dark oak fence over the guard"""
    n = 2 + (k % 2)
    for d in range(n): b.set(x, y + d, z, "minecraft:tuff_wall")
    b.set(x, y + n, z, "minecraft:stone_brick_slab[type=bottom,waterlogged=false]")

def garden(b, r, L, seed, meta, key):
    """a garden: level beds of rooted dirt / coarse dirt in rows along x (no farmland: it is trampled), on every bed a row of small swords
    (one per 2 cells), between the rows pumpkins; a low fence round with a gate gap"""
    x1, z1, x2, z2 = r
    swords = []
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            edge = x in (x1, x2) or z in (z1, z2)
            b.set(x, L, z, "minecraft:coarse_dirt" if not edge else "minecraft:dirt_path")
            if edge: continue
            row = (z - z1) % 3
            if row == 1:
                b.set(x, L, z, "minecraft:rooted_dirt")
                if (x - x1) % 2 == 1: small_sword(b, x, L + 1, z, x + z); swords.append([x, L + 1, z])
            elif row == 2 and (x - x1) % 3 == 1:
                b.set(x, L + 1, z, "minecraft:pumpkin" if hsh(x, 1, z, seed) < 0.7 else "minecraft:carved_pumpkin[facing=south]")
    meta.setdefault("gardens", {})[key] = dict(r=list(r), L=L, swords=len(swords), first=swords[0] if swords else None)
    return swords

def scarecrow_points(r, n, seed):
    x1, z1, x2, z2 = r
    pts = []
    for k in range(n):
        x = x1 + 3 + int(hsh(k, 2, 7, seed) * (x2 - x1 - 6)); z = z1 + 3 + int(hsh(k, 3, 9, seed) * (z2 - z1 - 6))
        if all(abs(x - p[0]) + abs(z - p[1]) >= 5 for p in pts): pts.append((x, z))
    return pts

def pasture(b, r, ground, seed, meta):
    """the pasture: a fence of spruce along its edge over the natural ground (follows it, posts every cell), a gate opening on the
    street side; inside an empty pen (a smaller fenced square with an open gate and a trough of a composter on its side? no: a cauldron)"""
    x1, z1, x2, z2 = r
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            if not (x in (x1, x2) or z in (z1, z2)): continue
            if z == z2 and abs(x - (x1 + 3)) <= 1: continue           # the gate gap (south side)
            g = ground(x, z); b.set(x, g + 1, z, "minecraft:spruce_fence")
    px1, pz1, px2, pz2 = x2 - 6, z1 + 2, x2 - 2, z1 + 6
    for x in range(px1, px2 + 1):
        for z in range(pz1, pz2 + 1):
            if not (x in (px1, px2) or z in (pz1, pz2)): continue
            if z == pz2 and x == px1 + 2: continue
            g = ground(x, z); b.set(x, g + 1, z, "minecraft:dark_oak_fence")
    meta["pasture"] = dict(r=list(r), pen=[px1, pz1, px2, pz2], gate=[x1 + 3, z2])

# ---------------------------------------------------------------- the mill
def mill(b, r, L, ground_lo, meta):
    """the mill: a round tower (stone below, wood above), the axle on the south wall (to the bridge and the bonfire), a conical roof;
    the sails are 4 block displays (the datapack); the door on the west to the street side"""
    x1, z1, x2, z2 = r; cx, cz = (x1 + x2) // 2, (z1 + z2) // 2
    R = 3.6; H1, H2 = 7, 13
    for a in range(-4, 5):
        for c in range(-4, 5):
            d = math.hypot(a, c)
            if d > R + 0.4: continue
            wall = d > R - 0.8
            x, z = cx + a, cz + c
            for y in range(min(ground_lo, L) - 1, L + 1): b.set(x, y, z, LO)
            for y in range(L + 1, L + H2 + 1):
                if not wall: b.set(x, y, z, "minecraft:air"); continue
                b.set(x, y, z, LO if y <= L + H1 else ("minecraft:spruce_planks" if (a + c + y) % 4 else LOG))
            if not wall and (a, c) != (0, 0): b.set(x, L + 7, z, "minecraft:spruce_planks")    # the upper floor (no stair: the mill is closed)
    for k in range(6):
        rr = R + 0.6 - k * 0.75
        for a in range(-5, 6):
            for c in range(-5, 6):
                d = math.hypot(a, c)
                if rr - 0.8 < d <= rr: b.set(cx + a, L + H2 + 1 + k, cz + c, "minecraft:dark_oak_planks" if k % 2 else "minecraft:spruce_planks")
                elif d <= rr - 0.8 and k < 5: b.set(cx + a, L + H2 + 1 + k, cz + c, "minecraft:air")
    b.set(cx, L + H2 + 7, cz, "minecraft:dark_oak_fence")
    # the door on the west, 2 high
    b.set(cx - 4, L + 1, cz, "minecraft:spruce_door[facing=west,half=lower,hinge=left,open=false,powered=false]")
    b.set(cx - 4, L + 2, cz, "minecraft:spruce_door[facing=west,half=upper,hinge=left,open=false,powered=false]")
    b.set(cx - 3, L + 1, cz, "minecraft:air"); b.set(cx - 3, L + 2, cz, "minecraft:air")
    # the axle: a dark oak log through the south wall, out 2
    ay = L + H1 + 4
    for c in range(3, 6): b.set(cx, ay, cz + c, "minecraft:dark_oak_log[axis=z]")
    b.set(cx, ay, cz + 6, "minecraft:dark_oak_wood[axis=z]")
    meta["mill"] = dict(r=list(r), L=L, centre=[cx, cz], axle=[cx + 0.5, ay + 0.5, cz + 7.05], door=[cx - 5, L + 1, cz], hub=[cx, ay, cz + 6])

# ---------------------------------------------------------------- the church with the bell tower
def church(b, r, L, ground_lo_at, meta):
    """the red church on its terrace (r = 28 x 14, x along the contour): the bell tower 7 x 7 on the west end, the nave 21 x 11 east of
    it, the sacristy 5 x 4 on the north-east of the nave; the door in the south wall of the nave by the tower (the street comes to the
    south edge of the terrace); the benches turned to the north wall; the altar on the east; the tower stair: a square spiral round a
    3 x 3 well (marches of 3 with corner landings, 3 of head room everywhere), the bell platform at L + 21 with the bell, the ringer's
    place and two lanterns; the spire of brick walls up to L + 32"""
    x1, z1, x2, z2 = r
    tx1, tz1 = x1 + 1, z1 + 3; tx2, tz2 = tx1 + 6, tz1 + 6                  # the tower 7 x 7
    nx1, nz1, nx2, nz2 = tx2 + 1, z1 + 1, x2 - 1, z1 + 11                    # the nave (x2 - 1 - tx2 - 1 + 1 = 19 long, 11 wide)
    NH = 9                                                                  # walls of the nave up to L + 9
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1): b.set(x, L, z, "minecraft:stone_bricks" if (x + z) % 2 else "minecraft:cobblestone")
    # the nave
    for x in range(nx1, nx2 + 1):
        for z in range(nz1, nz2 + 1):
            edge = x in (nx1, nx2) or z in (nz1, nz2)
            for y in range(min(ground_lo_at(x, z), L) - 1, L): b.set(x, y, z, "minecraft:stone_bricks")
            b.set(x, L, z, "minecraft:stone_bricks" if edge else ("minecraft:spruce_planks" if (x + z) % 3 else "minecraft:dark_oak_planks"))
            for y in range(L + 1, L + NH + 1): b.set(x, y, z, CHURCH if edge else "minecraft:air")
    # tall windows (2 wide pairs, glass panes in red) on the long walls, the rose on the east
    for x in range(nx1 + 3, nx2 - 1, 4):
        for z in (nz1, nz2):
            for y in range(L + 3, L + 7): b.set(x, y, z, "minecraft:red_stained_glass_pane")
    for y in range(L + 4, L + 8):
        for z in range((nz1 + nz2) // 2 - 1, (nz1 + nz2) // 2 + 2):
            if y in (L + 4, L + 7) and z != (nz1 + nz2) // 2: continue
            b.set(nx2, y, z, "minecraft:red_stained_glass_pane")
    # the roof: deepslate tile stairs, gable along x, eaves over the long walls
    zc = (nz1 + nz2) / 2.0
    for k in range(8):
        y = L + NH + 1 + k
        zf, zb = nz1 - 1 + k, nz2 + 1 - k
        if zf > zb: break
        for x in range(nx1 - 1, nx2 + 2):
            if zf == zb: b.set(x, y, zf, "minecraft:deepslate_tile_slab[type=bottom,waterlogged=false]"); continue
            b.set(x, y, zf, "minecraft:deepslate_tile_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]")
            b.set(x, y, zb, "minecraft:deepslate_tile_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]")
            if x in (nx1, nx2):
                for z in range(zf + 1, zb): b.set(x, y, z, CHURCH)
            elif nx1 < x < nx2:
                for z in range(zf + 1, zb): b.set(x, y, z, "minecraft:air")
    # inside: the altar (east), the benches turned to the north wall (rows of stairs facing south: the sitter looks north at the wall)
    ac = (nz1 + nz2) // 2
    b.set(nx2 - 2, L + 1, ac, "minecraft:polished_deepslate"); b.set(nx2 - 2, L + 1, ac - 1, "minecraft:polished_deepslate"); b.set(nx2 - 2, L + 1, ac + 1, "minecraft:polished_deepslate")
    b.set(nx2 - 2, L + 2, ac, "minecraft:candle[candles=3,lit=false,waterlogged=false]")
    benches = []
    for x in range(nx1 + 3, nx2 - 4, 2):
        for z in (nz1 + 2, nz1 + 3, nz2 - 3, nz2 - 2):
            b.set(x, L + 1, z, "minecraft:spruce_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]")
            benches.append([x, L + 1, z])
    # the sacristy: north-east of the nave, 5 x 4 outside the nave's north wall? inside: the east end, north corner, a wall of planks
    sx1, sz1, sx2, sz2 = nx2 - 5, nz1, nx2, nz1 + 4
    for x in range(sx1, sx2 + 1):
        for y in range(L + 1, L + 5):
            b.set(x, y, sz2, "minecraft:spruce_planks" if x != sx1 + 2 or y > L + 2 else "minecraft:air")
    for z in range(sz1, sz2 + 1):
        for y in range(L + 1, L + 5): b.set(sx1, y, z, "minecraft:spruce_planks")
    for x in range(sx1 + 1, sx2):
        for z in range(sz1 + 1, sz2): b.set(x, L + 5, z, "minecraft:spruce_planks")
    b.set(sx1 + 2, L + 1, sz2, "minecraft:spruce_door[facing=south,half=lower,hinge=left,open=false,powered=false]")
    b.set(sx1 + 2, L + 2, sz2, "minecraft:spruce_door[facing=south,half=upper,hinge=left,open=false,powered=false]")
    b.set(sx2 - 1, L + 1, sz1 + 1, "minecraft:chest[facing=south,type=single,waterlogged=false]{LootTable:\"last_ember:chests/r1/common\"}")
    meta_s = dict(chest=[sx2 - 1, L + 1, sz1 + 1], lectern=[sx1 + 1, L + 1, sz1 + 1], door=[sx1 + 2, L + 1, sz2 + 1])
    # the door of the church: the south wall of the nave by the tower, 2 wide
    dx = nx1 + 2
    for x in (dx, dx + 1):
        b.set(x, L + 1, nz2, "minecraft:dark_oak_door[facing=south,half=lower,hinge=%s,open=false,powered=false]" % ("left" if x == dx else "right"))
        b.set(x, L + 2, nz2, "minecraft:dark_oak_door[facing=south,half=upper,hinge=%s,open=false,powered=false]" % ("left" if x == dx else "right"))
        b.set(x, L + 3, nz2, CHURCH)
    # the tower: 7 x 7 walls (bricks), inside 5 x 5: the spiral stair round the 3 x 3 well, from the nave through an arch in its east wall
    TOP = L + 21                                                            # the bell platform floor
    for x in range(tx1, tx2 + 1):
        for z in range(tz1, tz2 + 1):
            edge = x in (tx1, tx2) or z in (tz1, tz2)
            for y in range(min(ground_lo_at(x, z), L) - 1, L): b.set(x, y, z, "minecraft:stone_bricks")
            b.set(x, L, z, "minecraft:stone_bricks")
            for y in range(L + 1, TOP + 6): b.set(x, y, z, CHURCH if edge else "minecraft:air")
    # the arch nave -> tower (in the tower's east wall = the nave's west end; the nave starts at tx2 + 1: the tower wall is its west wall)
    for z in (tz1 + 3,):
        for y in (L + 1, L + 2, L + 3): b.set(tx2, y, z, "minecraft:air")
    # the spiral: the ring cells of the 5 x 5 inside (tx1+1..tx2-1), order counter-clockwise from the arch; every cell up 1 (a stair)
    # except the corners (landings); 3 of head room above each (the next turn is 16 above: the ring has 16 cells)
    ring = []
    ix1, iz1, ix2, iz2 = tx1 + 1, tz1 + 1, tx2 - 1, tz2 - 1
    for z in range(iz2 - 1, iz1 - 1, -1): ring.append((ix2, z, "north"))      # east side going north
    for x in range(ix2 - 1, ix1 - 1, -1): ring.append((x, iz1, "west"))       # north side going west
    for z in range(iz1 + 1, iz2 + 1): ring.append((ix1, z, "south"))          # west side going south
    for x in range(ix1 + 1, ix2 + 1): ring.append((x, iz2, "east"))           # south side going east
    # start: the cell by the arch (ix2, tz1 + 3) at L (floor); climb
    start = ring.index((ix2, tz1 + 3, "north"))
    ring = ring[start:] + ring[:start]
    y = L; k = 0; steps = []
    corners = {(ix1, iz1), (ix2, iz1), (ix1, iz2), (ix2, iz2)}
    while y < TOP:
        x, z, fdir = ring[k % len(ring)]
        if (x, z) in corners:
            b.set(x, y, z, "minecraft:stone_bricks")                      # a landing at the level of the last step top
            for yy in range(y + 1, y + 4): b.set(x, yy, z, "minecraft:air")
            steps.append((x, z, y + 1))
        else:
            y += 1
            b.set(x, y, z, "minecraft:stone_brick_stairs[facing=%s,half=bottom,shape=straight,waterlogged=false]" % fdir)
            b.set(x, y - 1, z, "minecraft:stone_bricks")
            for yy in range(y + 1, y + 4): b.set(x, yy, z, "minecraft:air")
            steps.append((x, z, y))
        # the underside: solid under each step down to the previous turn
        k += 1
        if k > 200: break
    # the last cells reach TOP: the platform floor is TOP over the whole inside except the stair's opening (the last 2 ring cells)
    last = steps[-1]
    for x in range(ix1, ix2 + 1):
        for z in range(iz1, iz2 + 1):
            if (x, z) in [(s[0], s[1]) for s in steps[-2:]]: continue
            if (x, z) == (last[0], last[1]): continue
            b.set(x, TOP, z, "minecraft:spruce_planks")
    # the well (3 x 3) is open (the bell rope hangs: chains), a rail of fences round the opening at the platform
    for x in range(ix1 + 1, ix2):
        for z in range(iz1 + 1, iz2):
            for yy in range(L + 1, TOP): b.set(x, yy, z, "minecraft:air") if b.get(x, yy, z) is None or "stairs" not in b.get(x, yy, z) else None
    # the belfry: TOP + 1 .. TOP + 5 open arches (2 wide) on each side with fence parapets (1.5 high), the bell hanging from the ceiling
    bx, bz = (tx1 + tx2) // 2, (tz1 + tz2) // 2
    for x in range(tx1, tx2 + 1):
        for z in range(tz1, tz2 + 1):
            edge = x in (tx1, tx2) or z in (tz1, tz2)
            corner = x in (tx1, tx2) and z in (tz1, tz2)
            if edge and not corner:
                mid = abs(x - bx) <= 1 if z in (tz1, tz2) else abs(z - bz) <= 1
                if mid:
                    b.set(x, TOP + 1, z, "minecraft:brick_wall"); b.set(x, TOP + 2, z, "minecraft:air"); b.set(x, TOP + 3, z, "minecraft:air")
            if not edge:
                for yy in range(TOP + 1, TOP + 5): b.set(x, yy, z, "minecraft:air")
            b.set(x, TOP + 5, z, CHURCH if edge else "minecraft:spruce_planks")
    # the bell: hangs from the ceiling over the well's centre (attachment ceiling), the ringer stands west of it
    b.set(bx, TOP + 3, bz, "minecraft:bell[attachment=ceiling,facing=north,powered=false]")
    b.set(bx, TOP + 4, bz, "minecraft:chain[axis=y,waterlogged=false]") if False else None
    for x in range(ix1, ix2 + 1):
        for z in range(iz1, iz2 + 1):
            if abs(x - bx) <= 1 and abs(z - bz) <= 1 and (x, z) != (bx, bz): b.set(x, TOP, z, "minecraft:spruce_planks")
    b.set(bx, TOP, bz, "minecraft:spruce_planks")
    b.set(ix1, TOP + 4, iz1, lantern(True)); b.set(ix2, TOP + 4, iz2, lantern(True))
    # the spire: a pyramid of brick walls 7 -> 1 up to L + 32 (the card: brick_wall)
    sy = TOP + 6; n = 0
    while sy <= L + 32:
        rr = max(0, 3 - n // 3)
        for x in range(bx - rr, bx + rr + 1):
            for z in range(bz - rr, bz + rr + 1):
                if rr == 0 or x in (bx - rr, bx + rr) or z in (bz - rr, bz + rr): b.set(x, sy, z, "minecraft:brick_wall")
        sy += 1; n += 1
    meta["church"] = dict(r=list(r), L=L, nave=[nx1, nz1, nx2, nz2], tower=[tx1, tz1, tx2, tz2], door=[dx, L + 1, nz2 + 1], top=TOP,
                          bell=[bx, TOP + 3, bz], ringer=[ix1 + 0.5, TOP + 1, bz + 0.5], benches=benches, altar=[nx2 - 2, L + 1, ac],
                          sacristy=meta_s, spire=L + 32, stair_top=list(last), arch=[tx2, L + 1, tz1 + 3])
    return meta["church"]
