"""T-023: the Weeper statue (card «Круг Плакальщиц», plakal'shchitsy): a hooded woman, palms at the face, tear streaks of tuff and
andesite from the eyes down, a 1x1 niche at the eyes (particles of the event). Two poses: hands at the face (up) and hands lowered (down).
Two templates per pose: orthogonal (canonical facing north) and diagonal (canonical facing north-east); `place template` rotations give
all 8 directions.

dy is counted up from the floor the plinth stands on (dy 0 = first block above the ground). Template box 7x7 (centre at local 3,3),
height H. Cells outside the model inside the box are air (a swap clears the other pose). Candles on the corners of the plinth (dy 1,
lit, 1..3 per group) are part of both poses: placing a template relights them."""
import math
from lib import Mix

K = 3                     # template is (2K+1) x H x (2K+1), the statue centre at (K, K)
H = 12
ROBE = Mix({"calcite": 42, "polished_diorite": 24, "smooth_stone": 14, "tuff": 6, "andesite": 6, "moss_block": 8}, 2301)
HOOD = Mix({"calcite": 55, "polished_diorite": 30, "smooth_stone": 15}, 2302)
TEAR = Mix({"tuff": 55, "andesite": 45}, 2303)
PLINTH = Mix({"smooth_stone": 40, "polished_diorite": 35, "calcite": 15, "mossy_stone_bricks": 10}, 2304)
STAIR = Mix({"polished_diorite_stairs": 50, "tuff_stairs": 25, "andesite_stairs": 25}, 2305)
SLAB = Mix({"polished_diorite_slab": 45, "smooth_stone_slab": 35, "tuff_slab": 20}, 2306)
FACE = "minecraft:polished_deepslate"          # the face deep in the hood reads as shadow
PALM = "minecraft:calcite"
AIR = "minecraft:air"
EYE_DY = 9                # the niche at the eyes: the air cell in front of the recessed face, under the brim of the hood

# Both models are written straight in template coordinates (dx east, dz south from the centre cell; dy up from the floor):
#   ortho: canonical facing north (forward f = -dz, right s = +dx); diag: canonical facing north-east, sculpted on its own (not a
#   rotation of the ortho one): forward u = dx - dz, right v = dx + dz (one step of u or v = half a diagonal cell).
# The figure: a plinth, a hem widening to 5x5 with folds of stairs and slabs, a body 3 wide, shoulders 5 wide, a hood with a brim over
# a face recessed one block (in shadow), the eye niche under the brim; tears of tuff/andesite from the niche down the face and breast.
#   up    elbows spread to the sides, forearms rising, the palms at the lower face
#   down  arms hanging along the body, the hands folded at the waist, the face open

def _ortho(pose):
    m = {}
    def put(f, s, dy, st): m[(s, -f, dy)] = st
    def stair(f, s, dy, toward, half="bottom"):
        """a stair whose tall side looks `toward` (local: 'f+', 'f-', 's+', 's-')"""
        put(f, s, dy, ("stair", {"f+": "north", "f-": "south", "s+": "east", "s-": "west"}[toward], half))
    rng = range(-2, 3)
    for f in rng:
        for s in rng: put(f, s, 0, PLINTH)                                             # plinth 5x5
    for f in rng:
        for s in rng:
            if abs(f) == 2 and abs(s) == 2: continue                                   # corners: candles
            put(f, s, 1, ROBE)                                                         # the hem, 5x5 without corners
    for f in range(-1, 2):
        for s in range(-1, 2):
            for dy in range(2, 7): put(f, s, dy, ROBE)                                 # the body 3x3
    for k in range(-1, 2):                                                             # folds: stairs stepping down outwards
        stair(2, k, 2, "f-"); stair(-2, k, 2, "f+"); stair(k, 2, 2, "s-"); stair(k, -2, 2, "s+")
    for f, s in ((2, 0), (0, 2), (0, -2), (-2, 0)): put(f, s, 3, ("slab",))
    for f in range(-1, 2):
        for s in range(-1, 2): put(f, s, 7, ROBE)
    for f in (0, -1):
        put(f, -2, 7, ROBE); put(f, 2, 7, ROBE)                                        # shoulders 5 wide
    for dy in range(3, 8): put(-2, 0, dy, ROBE)                                        # the hood falls down the back
    put(-2, -1, 5, ("slab",)); put(-2, 1, 5, ("slab",))
    # the head: chin, face (recessed one block), hood sides reaching forward, the brim, the peak tilted forward
    put(0, 0, 8, TEAR); put(0, -1, 8, HOOD); put(0, 1, 8, HOOD)
    for s in range(-1, 2): put(-1, s, 8, HOOD); put(-1, s, 9, HOOD); put(-1, s, 10, HOOD); put(0, s, 10, HOOD)
    put(0, 0, 9, FACE); put(0, -1, 9, HOOD); put(0, 1, 9, HOOD); put(1, -1, 9, HOOD); put(1, 1, 9, HOOD)
    put(1, 0, 9, AIR); put(1, 0, 8, AIR)
    for s in range(-1, 2): stair(1, s, 10, "f-", "top")                                # the brim over the face
    put(0, 0, 11, HOOD); put(-1, 0, 11, HOOD); put(1, 0, 11, ("slab",)); put(0, -1, 11, ("slab",)); put(0, 1, 11, ("slab",))
    for dy in range(3, 8): put(1, 0, dy, TEAR)                                         # tears down the breast
    put(1, -1, 6, TEAR); put(1, 1, 5, TEAR); put(1, -1, 4, TEAR)
    if pose == "up":
        put(0, -3, 6, ROBE); put(0, 3, 6, ROBE)                                        # elbows spread
        put(1, -2, 7, ROBE); put(1, 2, 7, ROBE)                                        # forearms rising
        put(1, -1, 8, PALM); put(1, 1, 8, PALM)                                        # the palms at the lower face
    else:
        for dy in (4, 5, 6): put(0, -2, dy, ROBE); put(0, 2, dy, ROBE)                 # arms along the body
        put(1, -2, 5, ROBE); put(1, 2, 5, ROBE)
        for s in (-1, 0, 1): put(2, s, 5, PALM)                                        # hands folded at the waist
    return m, [(2, 2, 2), (-2, 2, 1), (-2, -2, 3), (2, -2, 1)]                         # candles: (dx, dz, n) on the plinth corners

def _diag(pose):
    m = {}
    def put(dx, dz, dy, st): m[(dx, dz, dy)] = st
    def uv(u, v): return ((u + v) // 2, (v - u) // 2)
    cheb = [(dx, dz) for dx in range(-1, 2) for dz in range(-1, 2)]
    diamond = [(dx, dz) for dx in range(-3, 4) for dz in range(-3, 4) if abs(dx) + abs(dz) <= 3]
    tips = [(3, 0), (0, 3), (-3, 0), (0, -3)]
    for c in diamond: put(*c, 0, PLINTH)                                               # plinth: a diamond (5x5 turned by 45 degrees)
    for c in diamond:
        if c not in tips: put(*c, 1, ROBE)                                             # the hem; tips: candles
    for c in cheb:
        for dy in range(2, 8): put(*c, dy, ROBE)                                       # the body
    for c in ((2, 0), (0, 2), (-2, 0), (0, -2)): put(*c, 2, ("slab",))                 # folds
    for c in ((2, -1), (1, -2)): put(*c, 2, ("slab",))
    for c in ((2, 0), (0, -2)): put(*c, 3, ("slab",))
    for u in (-1, 0, 1):                                                               # shoulders: 9 half-diagonals wide
        for v in range(-4, 5):
            if (u + v) % 2 == 0: put(*uv(u, v), 7, ROBE)
    for dy in range(3, 8): put(-2, 1, dy, ROBE); put(-1, 2, dy, ROBE)                  # the hood falls down the back
    # the head: face (0,0) recessed, open to the front through a V-niche (1,0) (0,-1) (1,-1) under the brim, hood sides (1,1) (-1,-1) frame it
    put(0, 0, 8, TEAR)
    for c in ((-1, 0), (0, 1), (-1, 1), (1, 1), (-1, -1)):
        for dy in (8, 9, 10): put(*c, dy, HOOD)
    put(0, 0, 9, FACE); put(1, 0, 9, AIR); put(0, -1, 9, AIR); put(1, -1, 9, AIR)
    for c in ((1, -1), (1, 0), (0, -1), (0, 0)): put(*c, 10, HOOD)                     # the brim and the crown of the hood
    put(1, -1, 8, AIR)
    put(0, 0, 11, HOOD); put(-1, 1, 11, HOOD); put(1, -1, 11, ("slab",)); put(1, 0, 11, ("slab",)); put(0, -1, 11, ("slab",))
    for dy in range(3, 8): put(1, -1, dy, TEAR)                                        # tears down the breast (the front corner)
    put(1, 0, 6, TEAR); put(0, -1, 5, TEAR); put(1, 0, 4, TEAR)
    if pose == "up":
        put(*uv(1, 3), 6, ROBE); put(*uv(1, -3), 6, ROBE)                              # elbows spread
        put(*uv(2, 2), 7, ROBE); put(*uv(2, -2), 7, ROBE)                              # forearms rising
        put(1, 0, 8, PALM); put(0, -1, 8, PALM)                                        # the palms at the lower face
    else:
        put(1, 0, 8, AIR); put(0, -1, 8, AIR)
        for dy in (4, 5, 6): put(*uv(1, 3), dy, ROBE); put(*uv(1, -3), dy, ROBE)      # arms along the body
        put(*uv(2, 2), 5, ROBE); put(*uv(2, -2), 5, ROBE)
        put(*uv(3, 1), 5, PALM); put(*uv(3, -1), 5, PALM)                              # hands folded at the waist
    return m, [(3, 0, 2), (0, 3, 1), (-3, 0, 3), (0, -3, 2)]

def plinth(diag):
    """the footprint of the plinth: (dx, dz) cells"""
    return [(dx, dz) for dx in range(-3, 4) for dz in range(-3, 4) if (abs(dx) + abs(dz) <= 3 if diag else max(abs(dx), abs(dz)) <= 2)]

def _state(st, x, y, z):
    if isinstance(st, Mix): return st.at(x, y, z)
    if isinstance(st, tuple):
        if st[0] == "slab": return SLAB.at(x, y, z) + "[type=bottom,waterlogged=false]"
        return STAIR.at(x, y, z) + "[facing=%s,half=%s,shape=straight,waterlogged=false]" % (st[1], st[2])
    return st

def template(pose, diag):
    """{(x, y, z): state} in template coordinates (0..2K, 0..H-1, 0..2K), every cell listed (air included); candles lit"""
    m, candles = (_diag if diag else _ortho)(pose); out = {}
    for x in range(2 * K + 1):
        for z in range(2 * K + 1):
            for y in range(H): out[(x, y, z)] = AIR
    for (dx, dz, dy), st in m.items():
        x, z = K + dx, K + dz; out[(x, dy, z)] = _state(st, x, dy, z)
    for dx, dz, n in candles: out[(K + dx, 1, K + dz)] = "minecraft:candle[candles=%d,lit=true,waterlogged=false]" % n
    return out

def eye(diag):
    """template-local cell of the eyes' niche (x, y, z)"""
    return (K + 1, EYE_DY, K - 1) if diag else (K, EYE_DY, K - 1)

def probe(diag):
    """a template cell that is solid in the 'up' pose and air in the 'down' pose (the sync checks it)"""
    up, dn = template("up", diag), template("down", diag)
    for c in sorted(up):
        if up[c] != AIR and dn[c] == AIR and "candle" not in up[c]: return c
    raise SystemExit("no probe cell")

# ---------------------------------------------------------------- place template rotation (pivot at the template origin)
ROT = {"none": (1, 0, 0, 1), "clockwise_90": (0, -1, 1, 0), "180": (-1, 0, 0, -1), "counterclockwise_90": (0, 1, -1, 0)}
def rot(r, x, z):
    """template-local (x, z) -> offset from the placement position after rotation r: none (x,z), cw90 (-z,x), 180 (-x,-z), ccw90 (z,-x)"""
    a, b, c, d = ROT[r]; return a * x + b * z, c * x + d * z
def facing_rot(direction):
    """compass direction (0 N, 45 NE, ... 315 NW) -> (diag, rotation)"""
    d = direction % 360; diag = d % 90 == 45; base = 45 if diag else 0
    return diag, {0: "none", 90: "clockwise_90", 180: "180", 270: "counterclockwise_90"}[(d - base) % 360]
def place_pos(cx, cz, direction):
    """placement position so that the statue centre lands on (cx, cz)"""
    diag, r = facing_rot(direction); ox, oz = rot(r, K, K); return cx - ox, cz - oz, diag, r
def world(cx, cy, cz, direction, pose):
    """the statue as world blocks {(x,y,z): state} (the plan picture, the checks); cy = first block above the ground"""
    px, pz, diag, r = place_pos(cx, cz, direction); out = {}
    for (x, y, z), st in template(pose, diag).items():
        ox, oz = rot(r, x, z); out[(px + ox, cy + y, pz + oz)] = st
    return out
def world_cell(cx, cy, cz, direction, cell):
    px, pz, diag, r = place_pos(cx, cz, direction); ox, oz = rot(r, cell[0], cell[2]); return (px + ox, cy + cell[1], pz + oz)

if __name__ == "__main__":
    for diag in (False, True):
        for pose in ("up", "down"):
            t = template(pose, diag); print(f"== diag={diag} pose={pose} eye={eye(diag)} probe={probe(diag)}")
            for y in range(H - 1, -1, -1):
                row = []
                for z in range(2 * K + 1):
                    row.append("".join(("." if t[(x, y, z)] == "minecraft:air" else ("c" if "candle" in t[(x, y, z)] else ("T" if t[(x, y, z)] in ("minecraft:tuff", "minecraft:andesite") else "#"))) for x in range(2 * K + 1)))
                print(f"{y:2d} " + " ".join(row))
