"""Hall of Awakening (card «Зал Пробуждения», v2): Cell of Awakening, Hall of Peoples (5 statues + sealed 6th niche with the
kneeling giant behind it), light well to the plaza grate, Font of Callings (turquoise grotto, 4 class altars, 5 name stones),
stairs up to the portico. Route (see report): Cell (north) -> Hall -> Font (south) -> corridor east -> shaft 7x7 at (+28,+40)
y55->96 -> corridor under the plaza -> short stair under the portico (0,+14)."""
import math
from lib import B, Mix, stairs, slab, lantern, candle, log, h
from geo import FLOOR, unrot, face_rot
HX, HZ = 0, 24; HR = 20.5; HF = 56            # hall centre, inner radius, floor block (players stand at 57)
TOP = 86                                     # highest air of the dome
ROCK = Mix({"stone": 80, "andesite": 10, "tuff": 10}, 80)
HALLW = Mix({"stone_bricks": 30, "tuff_bricks": 25, "polished_tuff": 15, "mossy_stone_bricks": 15, "cracked_stone_bricks": 15}, 81)
OLDW = Mix({"tuff_bricks": 55, "cracked_stone_bricks": 30, "mossy_stone_bricks": 15}, 82)
CELLW = Mix({"deepslate_tiles": 40, "polished_deepslate": 30, "cracked_deepslate_tiles": 20, "chiseled_deepslate": 10}, 83)
FONTW = Mix({"calcite": 30, "dripstone_block": 25, "tuff": 25, "smooth_basalt": 10, "moss_block": 10}, 84)
# niches: angle (deg from north, clockwise) -> people
PEOPLES = {45: "humans", 90: "elves", 135: "halflings", 270: "dwarves", 315: "ashborn"}
SIXTH = 225
NAMES = {"humans": "Люди Долин", "elves": "Эльфы", "dwarves": "Гномы", "halflings": "Полурослики", "ashborn": "Пеплорождённые"}
BASE = {"humans": "stone", "elves": "calcite", "dwarves": "deepslate", "halflings": "packed_mud", "ashborn": "blackstone"}
def stamp(b, m, ang, cx=HX, cz=HZ, y0=HF, r0=0.0, rng=40):
    """model m{(u,v,dy): state} in the local frame of a niche (u outward from the hall centre, from radius r0; v to the right
    looking outward) -> world. Facings in states: OUT/IN/RIGHT/LEFT."""
    us = [k[0] for k in m]; vs = [k[1] for k in m]
    a = math.radians(ang); pts = []
    for u in (min(us) - 1, max(us) + 1):
        for v in (min(vs) - 1, max(vs) + 1):
            pts.append((cx + (r0 + u) * math.sin(a) + v * math.cos(a), cz - (r0 + u) * math.cos(a) + v * math.sin(a)))
    xs = [p[0] for p in pts]; zs = [p[1] for p in pts]
    dys = sorted({k[2] for k in m})
    for x in range(int(min(xs)) - 1, int(max(xs)) + 2):
        for z in range(int(min(zs)) - 1, int(max(zs)) + 2):
            u, v = unrot(cx, cz, ang, x, z); ui, vi = int(round(u - r0)), int(round(v))
            for dy in dys:
                s = m.get((ui, vi, dy))
                if s is None: continue
                if isinstance(s, Mix): b.set(x, y0 + dy, z, s); continue
                for k, lf in (("OUT", "out"), ("IN", "in"), ("RIGHT", "right"), ("LEFT", "left")): s = s.replace(k, face_rot(lf, ang))
                b.set(x, y0 + dy, z, s)
def wpos(ang, u, v, cx=HX, cz=HZ):
    a = math.radians(ang); return round(cx + u * math.sin(a) + v * math.cos(a)), round(cz - u * math.cos(a) + v * math.sin(a))
# ------------------------------------------------------------------ statues (local frame: u depth, -u = toward the hall; v lateral; dy up)
def figure(kind):
    m = {}; base = BASE[kind]
    def put(u, v, dy, s): m[(u, v, dy)] = s
    def box(u1, u2, v1, v2, d1, d2, s):
        for u in range(u1, u2 + 1):
            for v in range(v1, v2 + 1):
                for dy in range(d1, d2 + 1): put(u, v, dy, s)
    if kind == "humans":
        M = Mix({"stone": 50, "andesite": 30, "polished_andesite": 20}, 91)
        box(-1, 1, -2, -1, 0, 5, M); box(-1, 1, 1, 2, 0, 5, M)           # legs
        box(-1, 1, -3, 3, 6, 11, M); box(-1, 1, -4, 4, 10, 11, M)       # torso, shoulders
        box(-1, 1, -1, 1, 12, 14, M)                                     # head
        box(2, 2, -4, 4, 2, 11, "polished_andesite"); box(1, 2, -4, -4, 3, 10, "polished_andesite"); box(1, 2, 4, 4, 3, 10, "polished_andesite")  # cloak
        box(-2, -2, 0, 0, 0, 6, "iron_bars"); put(-2, 0, 7, "gold_block"); put(-2, -1, 7, "stone"); put(-2, 1, 7, "stone")    # sword point down, hilt
        box(-2, -2, -3, -2, 7, 9, M); box(-2, -2, 2, 3, 7, 9, M)          # forearms to the guard
        put(-2, 0, 8, "gold_block")
    elif kind == "elves":
        M = Mix({"calcite": 60, "polished_diorite": 40}, 92)
        box(0, 0, -1, -1, 0, 7, M); box(0, 0, 1, 1, 0, 7, M); box(0, 1, -1, 1, 0, 7, M)
        box(-1, 1, -2, 2, 8, 13, M); box(-1, 0, -3, 3, 12, 13, M)
        box(-1, 1, -1, 1, 14, 16, M); put(-2, 0, 15, M); put(0, -2, 15, M) if False else None
        for v in (-1, 0, 1): put(-1, v, 16, "amethyst_block")      # circlet (front of the head)
        put(0, -2, 16, "amethyst_block"); put(0, 2, 16, "amethyst_block")
        box(0, 0, 4, 4, 6, 12, M); box(0, 0, -4, -4, 7, 12, M)            # arms
        for dy, dv in ((2, 6), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 6)): put(-1, dv, dy, "stripped_dark_oak_log[axis=y]")   # bow
        box(-1, -1, 5, 5, 2, 9, "iron_chain[axis=y]")
    elif kind == "dwarves":
        M = Mix({"deepslate": 55, "polished_basalt[axis=y]": 45}, 93)
        box(-1, 1, -3, -1, 0, 3, M); box(-1, 1, 1, 3, 0, 3, M)           # short thick legs
        box(-2, 1, -4, 4, 4, 8, M); box(-1, 1, -5, 5, 7, 8, M)           # wide torso (shoulders 11)
        box(-1, 1, -1, 1, 9, 11, M); box(-2, -2, -1, 1, 9, 9, M)         # lowered head, brow
        box(-2, -2, -2, 2, 4, 8, "waxed_oxidized_copper"); box(-3, -3, -1, 1, 5, 7, "waxed_oxidized_copper")   # beard
        box(0, 0, 5, 5, 4, 6, M); box(-1, -1, -5, -5, 4, 6, M)           # arms
        for i in range(5): put(0, 5, 9 + i, "stripped_spruce_log[axis=y]")   # hammer shaft on the right shoulder
        box(-1, 1, 4, 6, 13, 14, "iron_block")
    elif kind == "halflings":
        M = Mix({"packed_mud": 55, "mud_bricks": 45}, 94)
        box(0, 2, -3, 3, 0, 3, Mix({"cobblestone": 60, "mossy_cobblestone": 40}, 95))   # sitting stone
        box(-3, -1, -2, -1, 3, 3, M); box(-3, -3, -2, -1, 0, 2, M); box(-2, 0, 1, 2, 4, 4, M); box(-3, -3, 1, 2, 0, 3, M)   # thighs, shins, crossed leg
        box(-1, 1, -2, 2, 4, 7, M); box(-1, 1, -3, 3, 6, 7, M)
        box(-1, 1, -1, 1, 8, 10, M)
        box(1, 2, -3, 3, 4, 8, "moss_block")                             # cloak
        box(-1, -1, 2, 2, 5, 7, M)                                       # arm to the pipe
        put(-2, 1, 8, "dark_oak_log[axis=x]"); put(-3, 1, 8, "dark_oak_log[axis=x]"); put(-4, 1, 8, "campfire[lit=true,signal_fire=false,facing=OUT]")
    elif kind == "ashborn":
        M = Mix({"blackstone": 50, "smooth_basalt": 30, "polished_blackstone": 20}, 96)
        box(-1, 1, -2, 2, 0, 6, M)                                       # robe
        box(-1, 1, -2, 2, 7, 11, M); box(-1, 1, -3, 3, 10, 11, M)
        box(-1, 1, -1, 1, 12, 14, M); box(-2, -2, -1, 1, 14, 14, M); put(-2, 0, 13, "air") if False else None   # hood
        box(0, 0, 3, 3, 9, 15, M)                                        # raised right arm
        put(0, 3, 16, "iron_bars"); put(0, 3, 17, "coal_block"); put(0, 3, 18, "iron_bars")
        put(-1, 3, 17, "iron_bars"); put(1, 3, 17, "iron_bars"); put(0, 2, 17, "iron_bars"); put(0, 4, 17, "iron_bars")
        box(0, 0, -3, -3, 6, 10, M)
        for (u, v, dy) in ((-1, -1, 6), (-1, 2, 9), (0, 3, 12), (-1, 0, 10), (1, -3, 8)): put(u, v, dy, "magma_block")   # cracks (>= 4 above the floor)
    return m
PED = {"humans": 3, "elves": 2, "dwarves": 5, "halflings": 7, "ashborn": 3}     # pedestal heights: heads at 18 / 19 / 17 / 18 / 18(+lamp)
def niche(b, ang, kind):
    wide = kind == "dwarves"; hw = 5 if wide else 4; depth = 8 if wide else 7
    m = {}
    for u in range(0, depth + 2):
        for v in range(-hw - 1, hw + 2):
            for dy in range(0, 21):
                inside = 0 <= u <= depth - 1 and abs(v) <= hw and 1 <= dy <= 19
                m[(u, v, dy)] = "air" if inside else ("polished_tuff" if dy == 0 else HALLW)
    # deepslate tile arch at the opening
    for v in range(-hw, hw + 1): m[(0, v, 20)] = "deepslate_tiles"; m[(0, v, 19)] = "deepslate_tile_stairs[facing=IN,half=top,shape=straight]" if abs(v) == hw else "air"
    p = PED[kind]
    for u in range(1, depth - 1):
        for v in range(-hw + 1, hw):
            for dy in range(1, p + 1): m[(u, v, dy)] = "polished_tuff" if dy < p else "chiseled_tuff"
    stamp(b, m, ang, r0=HR - 0.5)
    fig = {(u + 4, v, dy + p + 1): s for (u, v, dy), s in figure(kind).items()}
    stamp(b, fig, ang, r0=HR - 0.5)
    # plate on the pedestal front + two candles
    sx, sz = wpos(ang, HR + 0.5, 0)
    b.set(sx, HF + max(1, p - 1), sz, f'dark_oak_wall_sign[facing={face_rot("in", ang)}]{{front_text:{{messages:["",{{"text":"{NAMES[kind]}"}},"",""]}}}}')
    for vv in (-hw + 1, hw - 1):
        cx_, cz_ = wpos(ang, HR + 0.5 + 1, vv); b.set(cx_, HF + p + 1, cz_, candle(2, True))
    # light from below: ochre froglight under iron bars just in front of the niche; selection pad 3x3
    for vv in (-1, 0, 1):
        fx, fz = wpos(ang, HR - 1, vv); b.set(fx, HF, fz, "iron_bars"); b.set(fx, HF - 1, fz, "ochre_froglight")
    for uu in (HR - 5, HR - 4, HR - 3):
        for vv in (-1, 0, 1):
            px, pz = wpos(ang, uu, vv); b.set(px, HF, pz, "polished_tuff" if (uu, vv) != (HR - 4, 0) else "chiseled_tuff")
    px, pz = wpos(ang, HR - 4, 0); b.marker(f"people_pad_{kind}", px, HF + 1, pz, "trigger 3x3, sign/button point")
def sixth(b, fallen=False):
    """sealed niche (flush with the wall) + the cavity with the kneeling giant; fallen=True: wall down, rubble on the floor"""
    m = {}; hw = 4
    for u in range(0, 15):
        for v in range(-7, 8):
            for dy in range(0, 31):
                cav = 2 <= u <= 13 and abs(v) <= 6 and 1 <= dy <= 30
                m[(u, v, dy)] = "air" if cav else ("polished_tuff" if dy == 0 else HALLW)
    for v in range(-hw, hw + 1):              # the bricked opening 9x7 (19 high), two blocks thick
        for dy in range(1, 20):
            for u in (0, 1): m[(u, v, dy)] = "air" if fallen else OLDW
    for u in (0, 1):
        for v in range(-hw - 1, hw + 2): m[(u, v, 20)] = "deepslate_tiles"
    G = Mix({"tuff": 45, "polished_tuff": 25, "stone": 15, "cracked_stone_bricks": 15}, 97)
    def box(u1, u2, v1, v2, d1, d2, s):
        for u in range(u1, u2 + 1):
            for v in range(v1, v2 + 1):
                for dy in range(d1, d2 + 1): m[(u, v, dy)] = s
    box(8, 12, -4, -2, 1, 2, G); box(8, 12, 2, 4, 1, 2, G)        # shins on the ground (kneeling)
    box(6, 8, -4, -2, 1, 8, G); box(6, 8, 2, 4, 1, 8, G)          # thighs up to the hips
    box(5, 9, -4, 4, 9, 18, G); box(5, 9, -6, 6, 16, 18, G)       # torso, shoulders 13 wide
    box(4, 7, -2, 2, 18, 21, G)                                    # bowed head (forward)
    box(6, 8, -6, -6, 9, 23, G); box(6, 8, 6, 6, 9, 23, G)         # arms raised to hold the sphere
    SUN = Mix({"gilded_blackstone": 55, "polished_blackstone": 45}, 98)
    for u in range(2, 14):
        for v in range(-6, 7):
            for dy in range(19, 31):
                if (u - 7.5) ** 2 + v * v + (dy - 25) ** 2 <= 5.6 ** 2: m[(u, v, dy)] = SUN
    if fallen:
        for (u, v) in [(-1, -3), (-1, 0), (-2, 1), (-1, 2), (-3, -1), (0, -4), (0, 3), (-2, -2)]:
            m[(u, v, 1)] = OLDW
        for (u, v) in [(-1, -1), (-2, 0), (0, 1)]: m[(u, v, 2)] = "cracked_stone_bricks"
        for u in range(-3, 0):
            for v in range(-4, 5): m.setdefault((u, v, 0), "polished_andesite")
    stamp(b, m, SIXTH, r0=HR - 0.5)
    x, z = wpos(SIXTH, HR + 0.5, 0); b.marker("sixth_niche_swap", x, HF + 1, z, "templates refuge/sixth_intact|sixth_fallen")
# ------------------------------------------------------------------ assemble
def build(envelope=True):
    b = B("hall")
    # solid rock envelope (no caves) from y 20 up to the bottom of the stairs corridor: the card asks for solid stone to y 20
    if envelope: b.fill(-34, 20, -14, 36, 95, 72, ROCK)
    # Cell of Awakening: inner 11x9, height 5, floor HF; door to the hall in the south wall
    b.fill(-6, HF, -11, 6, HF + 6, -1, CELLW); b.fill(-5, HF + 1, -10, 5, HF + 5, -2, "air")
    for i, x in enumerate((-3, 0, 3)):
        b.set(x, HF + 1, -9, "polished_deepslate"); b.set(x, HF + 1, -8, "polished_deepslate")
        b.set(x, HF + 2, -9, slab("smooth_stone_slab")); b.set(x, HF + 2, -8, slab("smooth_stone_slab"))
        b.set(x, HF + 3, -10, candle(1, True)) if False else None
        b.set(x, HF + 1, -10, "polished_deepslate"); b.set(x, HF + 2, -10, candle(1, True))
        b.marker(f"world_spawn_bed_{i}", x, HF + 3, -8, "player spawn")
    b.fill(-1, HF + 1, -1, 1, HF + 3, 4, "air")
    b.set(0, HF + 1, -1, "dark_oak_door[facing=south,half=lower,hinge=left,open=false]"); b.set(0, HF + 2, -1, "dark_oak_door[facing=south,half=upper,hinge=left,open=false]")
    b.set(-1, HF + 1, -1, CELLW); b.set(1, HF + 1, -1, CELLW); b.set(-1, HF + 2, -1, CELLW); b.set(1, HF + 2, -1, CELLW)
    b.marker("door_cell", 0, HF + 1, -1, "held closed until the choice")
    b.fill(-2, HF, -1, 2, HF + 4, 4, CELLW, replace=[ROCK.at(0, 0, 0)] and None) if False else None
    for x in (-2, 2):
        b.fill(x, HF + 1, 0, x, HF + 3, 3, CELLW)
    b.fill(-1, HF, 0, 1, HF, 4, "polished_deepslate"); b.fill(-2, HF + 4, 0, 2, HF + 4, 3, CELLW)
    # Hall of Peoples: wall shell 3 thick, dome, mosaic floor
    for x in range(-25, 26):
        for z in range(HZ - 25, HZ + 26):
            r = math.hypot(x - HX, z - HZ)
            if r > HR + 3.3: continue
            if r <= HR + 0.3:
                a = (math.degrees(math.atan2(x, -(z - HZ))) + 360) % 360
                if r < 2.3: fl = "chiseled_tuff"
                elif r < 6.3: fl = "polished_deepslate" if int(a // 22.5) % 2 == 0 else "polished_diorite"
                elif r < 7.3: fl = "polished_deepslate"
                elif r < 12.3: fl = "polished_andesite" if int((a + 11.25) // 22.5) % 2 == 0 else "polished_diorite"
                elif r < 13.3: fl = "polished_deepslate"
                else: fl = "polished_andesite"
                b.set(x, HF, z, fl); b.set(x, HF - 1, z, "stone")
                for y in range(HF + 1, TOP + 1):
                    k = (y - 75) / 12.6 if y > 75 else 0
                    ri = HR * math.sqrt(max(0.0, 1 - k * k)) if y > 75 else HR
                    if r <= ri + 0.3: b.set(x, y, z, "air")
                    elif r <= ri + 3.3: b.set(x, y, z, HALLW if y <= 75 else Mix({"deepslate_tiles": 70, "cracked_deepslate_tiles": 30}, 85))
                b.set(x, TOP + 1, z, Mix({"deepslate_tiles": 70, "cracked_deepslate_tiles": 30}, 85))
            else:
                for y in range(HF, 76): b.set(x, y, z, HALLW)
    for x in range(-22, 23):                      # cornice of upside-down stairs at the springing line
        for z in range(HZ - 22, HZ + 23):
            r = math.hypot(x - HX, z - HZ)
            if HR - 0.4 <= r <= HR + 0.6:
                a = (math.degrees(math.atan2(x, -(z - HZ))) + 360) % 360
                b.set(x, 76, z, f"deepslate_tile_stairs[facing={face_rot('in', a)},half=top,shape=straight]")
    # light well 3x3 from the dome to the plaza grate (the plaza cuts the top part)
    b.fill(-1, TOP + 1, 23, 1, FLOOR - 1, 25, "air"); b.walls(-2, TOP + 1, 22, 2, FLOOR - 1, 26, "stone_bricks")
    # north entrance (from the Cell) and south exit (to the Font): 3 wide, 4 high openings through the shell
    b.fill(-1, HF + 1, 0, 1, HF + 4, 4, "air"); b.fill(-1, HF + 1, 44, 1, HF + 4, 49, "air"); b.fill(-1, HF, 44, 1, HF, 49, "polished_deepslate")
    for x in (-2, 2): b.fill(x, HF + 1, 44, x, HF + 4, 49, "stone_bricks")
    b.fill(-2, HF + 5, 44, 2, HF + 5, 49, "deepslate_tiles")
    b.set(0, HF + 1, 48, "dark_oak_door[facing=north,half=lower,hinge=left,open=false]"); b.set(0, HF + 2, 48, "dark_oak_door[facing=north,half=upper,hinge=left,open=false]")
    b.fill(-1, HF + 1, 48, -1, HF + 4, 48, "stone_bricks"); b.fill(1, HF + 1, 48, 1, HF + 4, 48, "stone_bricks"); b.fill(0, HF + 3, 48, 0, HF + 4, 48, "stone_bricks")
    b.marker("door_hall", 0, HF + 1, 48, "Hall -> Font, held closed until the choice")
    for ang, kind in PEOPLES.items(): niche(b, ang, kind)
    sixth(b)
    font(b)
    b.fill(-1, HF + 1, 44, 1, HF + 3, 47, "air"); b.fill(-1, HF, 44, 1, HF, 47, "polished_deepslate")     # the Font shell must not close the exit
    stairs_up(b)
    return b
# ------------------------------------------------------------------ Font of Callings
FX, FZ = 0, 57; FY = 54         # grotto centre, walking surface block (players stand at 55); water surface y 54 (1 below the rim top)
ALTARS = {"shield": (-5, 52), "horn": (5, 52), "staff": (-5, 62), "phial": (5, 62)}
def font(b):
    for x in range(-16, 17):
        for z in range(44, 70):
            ex = ((x - FX) / 13.5) ** 2 + ((z - FZ) / 11.5) ** 2
            if ex > 1.35: continue
            for y in range(FY - 3, 72):
                dome = ((x - FX) / 13.5) ** 2 + ((z - FZ) / 11.5) ** 2 + ((y - FY) / 15.0) ** 2
                wob = (h(x, y, z, 99) - 0.5) * 0.12
                if dome + wob <= 1.0 and y > FY: b.set(x, y, z, "air")
                elif dome + wob <= 1.25 and y > FY - 3: b.set(x, y, z, FONTW)
            if ex + (h(x, 0, z, 98) - 0.5) * 0.1 <= 1.0:
                pool = ex <= 0.62
                if pool:
                    deep = ex <= 0.40
                    b.set(x, FY - 2, z, Mix({"prismarine": 55, "sand": 45}, 86) if deep else "sand"); b.set(x, FY - 1, z, "water" if deep else Mix({"prismarine": 55, "sand": 45}, 86))
                    b.set(x, FY, z, "water"); b.set(x, FY - 3, z, "stone")
                else:
                    b.set(x, FY, z, Mix({"tuff": 40, "calcite": 30, "moss_block": 30}, 87)); b.set(x, FY - 1, z, "stone")
                    if h(x, 1, z, 88) < 0.08: b.set(x, FY + 1, z, "moss_carpet")
    # dripstone from the ceiling, glow lichen accents
    for x in range(-12, 13):
        for z in range(47, 68):
            if h(x, 2, z, 89) < 0.05:
                for y in range(71, FY + 5, -1):
                    if b.get(x, y, z) == "minecraft:air":
                        n = 1 + int(h(x, 3, z, 90) * 3)
                        for i in range(n): b.set(x, y - i, z, f"pointed_dripstone[thickness={'tip' if i == n - 1 else ('frustum' if i == n - 2 else 'base')},vertical_direction=down]" if n > 1 else "pointed_dripstone[thickness=tip,vertical_direction=down]")
                        break
    # causeway (smooth stone top slabs, waterlogged), central flat stone, 4 altar pillars
    path = set()
    for z in range(46, 69): path.add((0, z)); path.add((-1, z)) if z < 52 else None
    for x in range(-5, 6): path.add((x, 57))
    for (ax, az) in ALTARS.values():
        for z in range(min(az, 57), max(az, 57) + 1): path.add((ax - (2 if ax < 0 else -2), z))
    for x in range(1, 15): path.add((x, 57))
    for (x, z) in path:
        if b.get(x, FY, z) == "minecraft:water": b.set(x, FY, z, "smooth_stone_slab[type=top,waterlogged=true]")
    b.fill(-1, FY, 56, 1, FY, 58, "smooth_stone"); b.marker("font_centre", 0, FY + 1, 57)
    for cls, (ax, az) in ALTARS.items():
        b.fill(ax - 1, FY - 2, az - 1, ax + 1, FY + 2, az + 1, "polished_tuff"); b.fill(ax - 1, FY + 3, az - 1, ax + 1, FY + 3, az + 1, "chiseled_tuff")
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                b.set(ax + dx, FY + 4, az + dz, "sea_lantern" if (dx, dz) == (0, 0) else ("waxed_oxidized_copper_grate" if dx and dz else "waxed_oxidized_cut_copper"))
        for dx, dz in ((-1, -1), (1, -1), (-1, 1), (1, 1)): b.set(ax + dx, FY + 5, az + dz, "waxed_oxidized_cut_copper_slab[type=bottom]")
        b.marker(f"altar_{cls}", ax, FY + 1, az, "trigger 3x3 at the pillar"); b.marker(f"altar_symbol_{cls}", ax, FY + 5, az, "item_display point over the bowl")
    # five name stones on the bottom (statue base material), away from the causeway
    for (kind, (x, z)) in zip(("humans", "elves", "dwarves", "halflings", "ashborn"), ((-3, 54), (3, 54), (-3, 60), (3, 60), (2, 57) if False else (0, 61))):
        if b.get(x, FY, z) != "minecraft:water": z += 1
        b.set(x, FY - 2, z, BASE[kind]); b.marker(f"name_stone_{kind}", x, FY - 2, z, "becomes sea_lantern")
    # exit east: corridor along z 56..58 (between the altar pairs) to x 29, door, then north to the shaft (x 25..31, z 37..43)
    b.fill(12, FY + 1, 55, 30, FY + 5, 59, "stone_bricks"); b.fill(26, FY + 1, 44, 30, FY + 5, 59, "stone_bricks")
    b.fill(12, FY, 56, 29, FY, 58, "polished_deepslate"); b.fill(12, FY + 1, 56, 29, FY + 4, 58, "air")
    b.fill(27, FY, 44, 29, FY, 58, "polished_deepslate"); b.fill(27, FY + 1, 44, 29, FY + 4, 58, "air")
    b.fill(14, FY + 1, 56, 14, FY + 4, 58, "stone_bricks"); b.fill(14, FY + 1, 57, 14, FY + 2, 57, "air")
    b.set(14, FY + 1, 57, "dark_oak_door[facing=west,half=lower,hinge=left,open=false]"); b.set(14, FY + 2, 57, "dark_oak_door[facing=west,half=upper,hinge=left,open=false]")
    b.marker("door_font", 14, FY + 1, 57, "Font -> stairs, held closed until the choice")
    b.set(20, FY + 4, 57, lantern(True)); b.set(28, FY + 4, 50, lantern(True))
    b.marker("font_biome_box", -16, 53, 44, "to 16 73 68")
# ------------------------------------------------------------------ stairs up
SX1, SZ1 = 25, 37   # shaft 7x7: x 25..31, z 37..43
def stairs_up(b):
    y0, y1 = FY, 96        # floor blocks: bottom (Font level) and top (corridor under the plaza)
    b.fill(SX1, y0, SZ1, SX1 + 6, y1 + 5, SZ1 + 6, "stone_bricks"); b.fill(SX1 + 1, y0 + 1, SZ1 + 1, SX1 + 5, y1 + 4, SZ1 + 5, "air")
    b.fill(SX1 + 2, y0, SZ1 + 2, SX1 + 4, y1, SZ1 + 4, Mix({"stone_bricks": 60, "polished_deepslate": 40}, 76))   # 3x3 core
    b.fill(27, y0 + 1, 43, 29, y0 + 4, 43, "air")                 # entry from the south corridor
    # ring of 16 cells around the core, walked clockwise from the south-east entry; one rise per cell, flat landing every 8
    ring = [(SX1 + 3 + i, SZ1 + 5) for i in range(-2, 3)][::-1]
    ring = [(28, 42), (27, 42), (26, 42), (26, 41), (26, 40), (26, 39), (26, 38), (27, 38), (28, 38), (29, 38), (30, 38), (30, 39), (30, 40), (30, 41), (30, 42), (29, 42)]
    nxt = {i: ring[(i + 1) % 16] for i in range(16)}
    def sim():
        yy_, n_ = y0, 0
        while yy_ < y1:
            if n_ % 9 != 8: yy_ += 1
            n_ += 1
        return n_
    n = sim(); k = (8 - (n - 1)) % 16          # flat cells at the bottom so that the last step lands on the north row (exit north)
    y = y0; land = 0; tops = {}
    for j in range(k + n):
        i = j; x, z = ring[i % 16]; nx, nz = nxt[i % 16]
        flat = j < k or ((j - k) % 9 == 8)
        if not flat: y += 1
        px, pz = ring[(i - 1) % 16]                      # a stair faces the way it is climbed (from the previous cell)
        fac = {(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}[(x - px, z - pz)]
        if y > y0 + 1 and (b.get(x, y - 1, z) or "minecraft:air") == "minecraft:air": b.set(x, y - 1, z, "stone_brick_slab[type=top]")
        b.set(x, y, z, "stone_bricks" if flat else stairs("stone_brick_stairs", fac))
        if flat and j >= k:                               # landing light in a niche of the core (no lantern at head height)
            for cx_, cz_ in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
                if SX1 + 2 <= cx_ <= SX1 + 4 and SZ1 + 2 <= cz_ <= SZ1 + 4:
                    b.set(cx_, y + 2, cz_, "air"); b.set(cx_, y + 1, cz_, "stone_bricks"); b.set(cx_, y + 2, cz_, lantern()); break
            land += 1
        for dy in range(1, 4): b.set(x, y + dy, z, "air")
        tops[(x, z)] = max(tops.get((x, z), -99), y)
    last = ring[(k + n - 1) % 16]; steps = n
    global SHAFT_PATH
    SHAFT_PATH = []; yy_ = y0
    for j in range(k + n):
        if not (j < k or ((j - k) % 9 == 8)): yy_ += 1
        SHAFT_PATH.append((ring[j % 16][0] + 0.5, ring[j % 16][1] + 0.5, yy_ + 1))
    b.marker("stairs_top", last[0], y + 1, last[1], f"{steps} cells, {land} landings, top y {y}")
    for (cx_, cz_), ty in tops.items():                 # close the top: floor over every ring cell whose last step is well below
        if ty <= y1 - 5: b.set(cx_, y1, cz_, "polished_deepslate")
    # walk off at y1 (top floor): open the north wall of the shaft, corridor north along x 27..29 to z 18, then west along z 18..20
    yy = y1
    legs = [(27, 18, 29, 36), (-6, 18, 29, 20), (-6, 12, -4, 20)]
    for (x1, z1, x2, z2) in legs: b.fill(x1 - 1, yy, z1 - 1, x2 + 1, yy + 5, z2 + 1, "stone_bricks")      # shells first, then the hollows
    for (x1, z1, x2, z2) in legs: b.fill(x1, yy, z1, x2, yy, z2, "polished_deepslate"); b.fill(x1, yy + 1, z1, x2, yy + 4, z2, "air")
    b.fill(27, yy + 1, 37, 29, yy + 4, 37, "air"); b.set(28, yy, 37, "polished_deepslate")
    for (lx, lz) in ((28, 30), (20, 19), (8, 19), (-4, 19), (-5, 15)): b.set(lx, yy + 4, lz, lantern(True))
    # final flight: east along z 13..15 from x -3 (y 97) to x 2 (y 102 = plaza floor) through a hole under the portico
    for k, x in enumerate(range(-3, 3)):
        for z in (13, 14, 15):
            ty = yy + 1 + k
            b.fill(x, yy, z, x, ty - 1, z, "stone_bricks")
            b.set(x, ty, z, stairs("stone_brick_stairs", "east"))
            for dy in range(1, 5): b.set(x, ty + dy, z, "air")
    b.fill(-3, yy + 1, 12, 3, FLOOR, 12, "stone_bricks"); b.fill(-3, yy + 1, 16, 3, FLOOR, 16, "stone_bricks"); b.fill(3, yy + 1, 13, 3, FLOOR - 1, 15, "stone_bricks")
    b.marker("portico_stairs_top", 2, FLOOR + 1, 14)
def plaza_holes():
    """cells the plaza must leave open (stair hole under the portico)"""
    return {(x, FLOOR + dy, z) for x in range(-3, 3) for z in (13, 14, 15) for dy in range(-5, 1)} | {(x, FLOOR + dy, z) for x in range(-3, 2) for z in (13, 14, 15) for dy in range(1, 4)}
def sixth_templates():
    a = B("sixth_intact"); sixth(a); f = B("sixth_fallen"); sixth(f, fallen=True); return a, f
def statue_pieces():
    out = []
    for ang, kind in PEOPLES.items():
        s = B(f"statue_{kind}"); niche(s, ang, kind); out.append(s)
    return out
