"""T-023: the Weeper statue (card «Круг Плакальщиц», plakal'shchitsy): a hooded woman, palms at the face, tear streaks of tuff and
andesite from the eyes down, a 1x1 niche at the eyes (particles of the event). Two poses: hands at the face (up) and hands lowered (down).
Two templates per pose: orthogonal (canonical facing north) and diagonal (canonical facing north-east); `place template` rotations give
all 8 directions.

Local frame of the model: f forward (the way she looks), s to her right, dy up from the floor the plinth stands on (dy 0 = first block
above the ground). Template box 7x7 (centre at local 3,3), height H. Cells outside the model inside the box are air (a swap clears the
other pose). Candles at her feet (lit, 1..3 per group) are part of both poses: placing a template relights them."""
import math
from lib import Mix, h as hsh

K = 3                     # template is (2K+1) x H x (2K+1), the statue centre at (K, K)
H = 12
ROBE = Mix({"calcite": 42, "polished_diorite": 24, "smooth_stone": 14, "tuff": 6, "andesite": 6, "moss_block": 8}, 2301)
HOOD = Mix({"calcite": 55, "polished_diorite": 30, "smooth_stone": 15}, 2302)
TEAR = Mix({"tuff": 55, "andesite": 45}, 2303)
PLINTH = Mix({"smooth_stone": 40, "polished_diorite": 35, "calcite": 15, "mossy_stone_bricks": 10}, 2304)
FACE = "minecraft:smooth_stone"
EYE_DY = 9                # the niche at the eyes: local (f=1, s=0, dy=9)

def model(pose, seed=0):
    """{(f, s, dy): state}. Full blocks only (rotations by 45 degrees keep it simple); air cells are not listed."""
    m = {}
    def put(f, s, dy, st): m[(f, s, dy)] = st
    def box(f1, f2, s1, s2, d1, d2, st):
        for f in range(f1, f2 + 1):
            for s in range(s1, s2 + 1):
                for dy in range(d1, d2 + 1): put(f, s, dy, st)
    box(-1, 1, -1, 1, 0, 0, PLINTH); box(-1, 1, -1, 1, 1, 1, PLINTH)                 # plinth 3x3x2 (the inscription is on its inner face)
    box(-1, 1, -1, 1, 2, 3, ROBE)                                                       # hem of the robe, full 3x3
    box(-1, 0, -1, 1, 4, 7, ROBE); put(1, 0, 4, ROBE)                                   # skirt and body, a fold in front at the knees
    box(-1, 0, -1, 1, 8, 8, ROBE)                                                       # shoulders
    box(-1, 0, -1, 1, 9, 10, HOOD); put(0, 0, 9, FACE)                                  # head in the hood, the face
    put(-1, 0, 11, HOOD); put(0, 0, 11, HOOD)                                           # hood peak
    put(1, 0, 10, HOOD)                                                                 # the brim over the face (the eyes' niche under it)
    put(-2, 0, 9, HOOD); put(-2, 0, 8, ROBE); put(-2, 0, 7, ROBE); put(-2, 0, 6, ROBE)  # the hood falls down the back as a cloak
    put(-2, -1, 6, ROBE); put(-2, 1, 6, ROBE); put(-2, 0, 5, ROBE); put(-2, 0, 4, ROBE)
    for dy in range(2, 9): put(0, 0, dy, TEAR)                                          # tears from the eyes down the front
    put(0, -1, 7, TEAR); put(0, -1, 6, TEAR); put(0, 1, 5, TEAR); put(1, 0, 4, TEAR); put(1, 0, 3, TEAR)
    if pose == "up":                                                                    # palms at the face, elbows out
        put(0, -2, 7, ROBE); put(0, 2, 7, ROBE)
        put(1, -1, 8, ROBE); put(1, 1, 8, ROBE)
        put(1, -1, 9, HOOD); put(1, 1, 9, HOOD)
    else:                                                                               # hands lowered along the robe
        for dy in (5, 6, 7): put(0, -2, dy, ROBE); put(0, 2, dy, ROBE)
        put(0, -2, 4, HOOD); put(0, 2, 4, HOOD)
    return m

CANDLES = [(2, -2, 3), (2, 2, 2), (-2, 2, 1), (-3, -1, 2), (3, 0, 1)]                  # (f, s, n) at dy 0 around the plinth

def rot_fs(f, s, diag):
    """local (f, s) -> template-local offset (dx, dz) from the centre, canonical facing north (f -> -z, s -> +x) or north-east"""
    if not diag: return s, -f
    a = math.radians(45); fx, fz = math.sin(a), -math.cos(a); sx, sz = math.cos(a), math.sin(a)
    return f * fx + s * sx, f * fz + s * sz

def template(pose, diag):
    """{(x, y, z): state} in template coordinates (0..2K, 0..H-1, 0..2K), every cell listed (air included)"""
    m = model(pose); out = {}
    for x in range(2 * K + 1):
        for z in range(2 * K + 1):
            for y in range(H): out[(x, y, z)] = "minecraft:air"
    if not diag:
        for (f, s, dy), st in m.items():
            dx, dz = rot_fs(f, s, False); out[(K + dx, dy, K + dz)] = st.at(K + dx, dy, K + dz) if isinstance(st, Mix) else st
    else:
        # inverse sampling: each cell takes the model cell nearest to its centre rotated back by 45 degrees (dense, no holes)
        for x in range(2 * K + 1):
            for z in range(2 * K + 1):
                dx, dz = x - K, z - K
                a = math.radians(45); f = dx * math.sin(a) - dz * math.cos(a); s = dx * math.cos(a) + dz * math.sin(a)
                fi, si = int(round(f)), int(round(s))
                for y in range(H):
                    st = m.get((fi, si, y))
                    if st is None: continue
                    out[(x, y, z)] = st.at(x, y, z) if isinstance(st, Mix) else st
        # the face, the niche and the palms must survive the rasterisation: placed on the diagonal explicitly
        for (f, s, dy, st) in face_cells(pose):
            dx, dz = rot_fs(f, s, True); out[(K + int(round(dx)), dy, K + int(round(dz)))] = st
    for f, s, n in CANDLES:
        dx, dz = rot_fs(f, s, diag); c = (K + int(round(dx)), 0, K + int(round(dz)))
        if out.get(c) == "minecraft:air": out[c] = "minecraft:candle[candles=%d,lit=true,waterlogged=false]" % n
    return out

def face_cells(pose):
    """diagonal: (f, s, dy, state) placed after sampling, f/s on the diagonal grid (1 step = one diagonal cell = (1,1) offset)"""
    c = [(0, 0, 9, FACE), (1.42, 0, EYE_DY, "minecraft:air"), (1.42, 0, 10, "minecraft:calcite"), (0, 0, 10, "minecraft:polished_diorite")]
    if pose == "up": c += [(0.71, -0.71, 9, "minecraft:calcite"), (0.71, 0.71, 9, "minecraft:calcite"), (0.71, -0.71, 8, "minecraft:polished_diorite"), (0.71, 0.71, 8, "minecraft:polished_diorite")]
    else: c += [(0.71, -0.71, 9, "minecraft:air"), (0.71, 0.71, 9, "minecraft:air"), (0.71, -0.71, 8, "minecraft:air"), (0.71, 0.71, 8, "minecraft:air")]
    return c

def eye(diag):
    """template-local cell of the eyes' niche (x, y, z)"""
    dx, dz = rot_fs(1.42 if diag else 1, 0, diag); return (K + int(round(dx)), EYE_DY, K + int(round(dz)))

def probe(diag):
    """a template cell that is solid in the 'up' pose and air in the 'down' pose (the sync checks it)"""
    up, dn = template("up", diag), template("down", diag)
    for c in sorted(up):
        if up[c] != "minecraft:air" and dn[c] == "minecraft:air" and "candle" not in up[c]: return c
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
