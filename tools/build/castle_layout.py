"""T-029: the layout of the Enchanted Castle on the castle table of T-028 (P = 166): the rooms as boxes (x1, z1, x2, z2 = the walls, the
inside is one less on each side), the levels, the stop conditions of HQ T-029, 1 and the plan picture docs/reports/T-029/castle_plan.png.
The blocks are tools/build/castle_keep.py, the datapack tools/build/castle_keep_dp.py, the run tools/build/r1_castle.py.

Levels (P = the table, the floor block of the court): the galleries P+8 (floor block; air P+9..P+12, roof P+13..P+14), the throne hall
floor P+30 (air 20 high, the gallery of the hall at P+36), the keep's roof up to P+85 (<= 255), the gaol floor P-12, the crypt floor P-24,
the secret way: the spiral from the reliquary (P+30) down to y 100, the tunnel under the rift (rock >= 4 over it) and up to the pier door
(floor W+1 = 116).
North is -z. The barbican (T-028) is on the north edge, the court behind it, the west wing (chapel, library; the gaol and the crypt
under them), the east wing (kitchens, armoury), the galleries round the court, the keep in the south: the vestibule with bonfire 11 on its
ground floor, the stair annex on its west side (up to the two west doors of the hall), the throne hall on top, the reliquary and the spiral
of the secret way east of the hall, the north tower in the north-east corner."""
import math, os
import numpy as np

P = 166
GAL = P + 8                       # the floor block of the galleries (the second tier P+8..P+14)
HALL_Y = P + 30                   # the floor block of the throne hall
HALL_H = 20                       # air above the floor
HG = 6                            # the gallery of the hall: floor block HALL_Y + 6
GAOL_Y, CRYPT_Y = P - 12, P - 24  # floor blocks
TUN_Y = 100                       # the floor block of the secret tunnel under the rift
DOOR_Y = 116                      # the floor block at the pier door (W + 1, the deck)
KEEP_TOP = P + 85

COURT = (434, 40, 469, 57)        # the court with its arcades (the open part 438..465 x 40..53)
COURT_OPEN = (438, 40, 465, 53)
GW = (433, 39, 437, 58)           # west gallery: walls x 433 / 437, corridor 434..436 (z 40..57)
GS = (422, 54, 470, 58)           # south gallery: walls z 54 / 58, corridor z 55..57 (x 423..469)
GE = (466, 39, 470, 58)           # east gallery: walls x 466 / 470, corridor 467..469
CHAPEL = (407, 39, 433, 53)
LIBRARY = (408, 54, 421, 83)
KITCHEN = (470, 44, 482, 54)
PANTRY = (476, 49, 482, 54)       # inside the kitchens (its own walls x 476, z 49)
ARMOURY = (470, 54, 482, 69)
TOWER = (471, 32, 483, 44)        # the north tower (outer 13 x 13, inside 11 x 11)
ANNEX = (422, 58, 430, 84)        # the stair annex west of the hall (lanes W 423..425, E 427..429, spine 426)
HALL = (430, 58, 463, 91)         # the throne hall walls; inside 431..462 x 59..90 (32 x 32)
VEST = (430, 58, 463, 91)         # the vestibule = the ground floor of the keep under the hall (inside, P+1 .. P+12)
RELIQ = (463, 71, 473, 81)        # the reliquary (inside 464..472 x 72..80 = 9 x 9), floor HALL_Y
SPIRAL = (473, 71, 483, 81)       # the spiral of the secret way (inside 474..482 x 72..80), from HALL_Y down to TUN_Y
NORTH_WALL_Z = 39                 # the curtain on the north edge (the barbican 444..458 stays as T-028 built it)
GATE_X = (450, 452)               # the gate passage of the barbican (T-028)
HEARTH11 = (446, P + 1, 67)       # bonfire 11 r1_throne: the hearth (the respawn 3 x 3 at z + 5, castle_dp / gen_bonfires)
# the throne hall: columns 3 x 3 (two rows of three along the W-E axis): 5 from the inner edge of the gallery, 10 between the rows
COLS_X = [(439, 441), (446, 448), (453, 455)]
COLS_Z = [(67, 69), (80, 82)]
HALL_DOORS = [(66, 68), (81, 83)]     # z of the two west doors (x 430), symmetric about the middle 74.5
NICHE_GUARD = {"n": (445, 55, 447, 57), "s": (445, 92, 447, 94), "w": (427, 73, 429, 75)}   # 3 x 3 boxes (x1 z1 x2 z2) in the wall
THRONE_Z = (74, 75)               # the seat (2 wide) in the middle of the east side
RELIQ_DOOR_Z = (73, 76)           # the door behind the throne (x 463), 4 wide, 3 high
# the secret way: the tunnel cells (x1 z1 x2 z2, from floor y1 to floor y2: a ramp of stairs when y1 != y2)
PIER_DOOR = (432, -33, 432, -31)  # in the rock face over the pier deck (x 432; F1 of T-028 is z -37..-35, F2 is above at y >= 129)
TUNNEL = [((470, 12, 473, 80), TUN_Y), ((461, 10, 469, 12), TUN_Y), ((461, -33, 463, 9), TUN_Y), ((445, -33, 460, -31), "ramp"),
          ((433, -33, 444, -31), DOOR_Y)]
# the gaol (under the chapel) and the crypt (under the library); the stair from the library door (north wall, under the balcony)
GAOL = (408, 66, 421, 83)         # under the library: corridor x 413..415, cells west and east (bars)
CRYPT = (408, 40, 433, 55)        # under the chapel


def inside(r): return (r[0] + 1, r[1] + 1, r[2] - 1, r[3] - 1)


def footprint():
    """the boxes that stand on the table (for the margin test)"""
    return dict(court=COURT, chapel=CHAPEL, library=LIBRARY, kitchen=KITCHEN, armoury=ARMOURY, tower=TOWER, annex=ANNEX, keep=HALL,
                reliquary=RELIQ, spiral=SPIRAL, gal_w=GW, gal_s=GS, gal_e=GE)


def margins(table, x1, z1):
    """for every box: the smallest distance (Chebyshev) from a box cell to a cell off the table; must be >= 3 (a margin of >= 2 blocks)"""
    dist = np.zeros(table.shape, int); cur = table.copy()
    for k in range(1, 9):            # Chebyshev distance to the nearest cell off the table, capped at 8 (erosion by 3 x 3 steps)
        dist[cur] = k; nxt = cur.copy()
        for a in (-1, 0, 1):
            for c in (-1, 0, 1): nxt &= np.roll(np.roll(cur, a, 0), c, 1)
        cur = nxt
    out = {}
    for n, (a, b, c, d) in footprint().items():
        sub = dist[b - z1:d - z1 + 1, a - x1:c - x1 + 1]
        out[n] = int(sub.min())
    return out


def column_reach():
    """the largest distance from a floor cell of the arena (inside the line of the gallery, 26 x 26) to the nearest column (Euclid,
    cell centre to the column's nearest cell), and the same over the whole 32 x 32 floor"""
    hx1, hz1, hx2, hz2 = inside(HALL); worst_in, worst_all = 0, 0
    for x in range(hx1, hx2 + 1):
        for z in range(hz1, hz2 + 1):
            if any(a <= x <= b and c <= z <= d for (a, b) in COLS_X for (c, d) in COLS_Z): continue
            dm = min(math.hypot(max(a - x, 0, x - b), max(c - z, 0, z - d)) for (a, b) in COLS_X for (c, d) in COLS_Z)
            worst_all = max(worst_all, dm)
            if hx1 + 3 <= x <= hx2 - 3 and hz1 + 3 <= z <= hz2 - 3: worst_in = max(worst_in, dm)
    return round(worst_in, 2), round(worst_all, 2)


def checks(table, x1, z1, rock_top, rift_floor):
    """the stop conditions of HQ T-029, 1"""
    out = {"margins": margins(table, x1, z1)}
    hx1, hz1, hx2, hz2 = inside(HALL)
    out["hall"] = [hx2 - hx1 + 1, hz2 - hz1 + 1, HALL_H]
    out["keep_top"] = KEEP_TOP
    out["gaol_floor"], out["crypt_floor"] = GAOL_Y, CRYPT_Y
    out["column_reach"] = column_reach()
    out["tunnel_cover_min"] = min(rift_floor) - (TUN_Y + 3) if rift_floor else None    # rock blocks over the tunnel under the rift
    out["tunnel_rock_tops"] = (min(rock_top), max(rock_top)) if rock_top else None
    stop = []
    if min(out["margins"].values()) < 3: stop.append("castle within 2 of the sheer edge: %s" % {k: v for k, v in out["margins"].items() if v < 3})
    if out["hall"][:2] != [32, 32]: stop.append("the throne hall is not 32 x 32")
    if KEEP_TOP > 255: stop.append("keep top over 255")
    if CRYPT_Y < 70: stop.append("the crypt under y 70")
    if out["tunnel_cover_min"] is not None and out["tunnel_cover_min"] < 4: stop.append("the tunnel under the rift has < 4 of rock over it")
    out["stop"] = stop
    return out


LEVELS = [("P (court, ground floors)", P + 1), ("P+8 (galleries)", GAL + 1), ("P+30 (throne hall)", HALL_Y + 1), ("P+36 (hall gallery)", HALL_Y + HG + 1)]


def plan_png(get, table, x1, z1, path, text, S=5, marks=None, tunnel=None):
    """four level plans (blocks at the feet height of each level) and the section W-E through the keep and the secret way"""
    from PIL import Image, ImageDraw
    X1, Z1, X2, Z2 = 398, -40, 492, 98
    w, h = (X2 - X1 + 1) * S, (Z2 - Z1 + 1) * S
    pad = 24
    img = Image.new("RGB", (2 * w + 3 * pad, 2 * h + 3 * pad + 420), (18, 18, 22)); d = ImageDraw.Draw(img)
    def colour(s):
        if s is None: return None
        n = s.replace("minecraft:", "").split("[")[0].split("{")[0]
        if n == "air": return (32, 32, 38)
        if "water" in n: return (40, 80, 160)
        if "chest" in n: return (255, 200, 0)
        if "lectern" in n: return (220, 120, 40)
        if "chiseled_bookshelf" in n: return (255, 80, 200)
        if "bookshelf" in n: return (150, 90, 50)
        if "iron_bars" in n or "glass" in n: return (120, 200, 230)
        if "stairs" in n or "slab" in n: return (200, 200, 120)
        if "campfire" in n or "fire" in n: return (255, 90, 0)
        if "gold" in n: return (255, 220, 60)
        if "planks" in n or "oak" in n: return (140, 100, 60)
        return (150, 150, 150)
    for k, (name, y) in enumerate(LEVELS):
        ox, oz = pad + (k % 2) * (w + pad), pad + (k // 2) * (h + pad)
        for z in range(Z1, Z2 + 1):
            for x in range(X1, X2 + 1):
                c = colour(get(x, y, z)); fl = get(x, y - 1, z)
                if c == (32, 32, 38) and fl is not None and colour(fl) not in (None, (32, 32, 38)): c = (70, 70, 80)    # walkable floor
                if c is None:
                    i, j = z - z1, x - x1
                    c = (60, 45, 35) if 0 <= i < table.shape[0] and 0 <= j < table.shape[1] and table[i, j] else (14, 14, 18)
                a = (ox + (x - X1) * S, oz + (z - Z1) * S); d.rectangle([a[0], a[1], a[0] + S - 1, a[1] + S - 1], fill=c)
        d.text((ox + 4, oz + 4), "%s  y %d" % (name, y), fill=(255, 255, 0))
        if tunnel and k == 0:                          # the secret way drawn on the ground plan: colour by height (blue low .. red high)
            for (tx, tz), ty in tunnel.items():
                t = max(0.0, min(1.0, (ty - TUN_Y) / float(DOOR_Y - TUN_Y + 4)))
                a = (ox + (tx - X1) * S, oz + (tz - Z1) * S)
                d.rectangle([a[0] + 1, a[1] + 1, a[0] + S - 2, a[1] + S - 2], fill=(int(60 + 190 * t), 80, int(250 - 190 * t)))
        for (mx, mz, label, lv) in (marks or []):
            if lv is not None and lv != k: continue
            a = (ox + (mx - X1) * S + S // 2, oz + (mz - Z1) * S + S // 2)
            d.ellipse([a[0] - 4, a[1] - 4, a[0] + 4, a[1] + 4], outline=(255, 60, 60), width=2)
            d.text((a[0] + 5, a[1] - 6), label, fill=(255, 140, 140))
        for x in range(X1 - X1 % 20 + 20, X2, 20): d.text((ox + (x - X1) * S + 2, oz + h - 12), str(x), fill=(200, 200, 0))
        for z in range(Z1 - Z1 % 20 + 20, Z2, 20): d.text((ox + 2, oz + (z - Z1) * S + 2), str(z), fill=(200, 200, 0))
    # the section: x 398..492 at z 76 (the keep, the hall, the reliquary, the spiral), y 96..256; and the tunnel line
    sy1, sy2, SS = 96, 256, 2
    ox, oy = pad, 2 * h + 3 * pad
    for y in range(sy1, sy2 + 1):
        for x in range(X1, X2 + 1):
            c = colour(get(x, y, 76)) or ((60, 45, 35) if y <= P else (14, 14, 18))
            for zz in (72, 80):
                if (get(x, y, zz) or "").endswith("air") and c == (60, 45, 35): c = (90, 70, 60)
            a = (ox + (x - X1) * SS, oy + (sy2 - y) * SS); d.rectangle([a[0], a[1], a[0] + SS - 1, a[1] + SS - 1], fill=c)
    d.text((ox + 4, oy + 2), "section W-E at z 76 (y 96..256)", fill=(255, 255, 0))
    for k, t in enumerate(text): d.text((ox + (X2 - X1 + 4) * SS + 10, oy + 4 + 15 * k), t, fill=(230, 230, 230))
    os.makedirs(os.path.dirname(path), exist_ok=True); img.save(path)
