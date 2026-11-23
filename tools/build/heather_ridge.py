"""T-031: the Dragon Ridge (card 5.3, HQ T-031, 1): the spine on the natural massif (a crest of cobbled deepslate and tuff with uneven
«vertebrae» 2..6 high along the crest line), the rock palette on the slopes with patches of slid earth, the head-cliff 30 x 30 on the
east end (the skull to y 120, the mouth open to the north with a viewing platform 5 x 5, teeth of dripstone round its edge, the eye: a
niche of tinted glass on the west side of the skull), the sword of 36 blocks stuck into the skull over the eye, leaning west, the sign.
Blocks into a lib.B; the head and the sword are also saved as templates structure/heather/head.nbt, sword_lo.nbt, sword_hi.nbt.

Head frame: X = x - HEAD.x1 (0..29), Z = z - HEAD.z1 (0 = the north edge, the snout; 29 = the back of the skull), y absolute."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Mix, h as hsh
import heather_plan as P

ROCK = Mix({"stone": 40, "andesite": 30, "tuff": 30}, 3301)                      # card: the ridge
CREST = Mix({"cobbled_deepslate": 60, "tuff": 40}, 3302)
SKULL = Mix({"stone": 35, "andesite": 30, "tuff": 25, "cobbled_deepslate": 10}, 3303)
SLID = Mix({"grass_block[snowy=false]": 55, "coarse_dirt": 30, "rooted_dirt": 15}, 3304)

def sign_nbt(lines):
    msgs = ",".join('"%s"' % l for l in (lines + ["", "", "", ""])[:4])
    return '{front_text:{messages:[%s],has_glowing_text:0b},back_text:{messages:["","","",""]},is_waxed:1b}' % msgs

# ---------------------------------------------------------------- the spine and the slopes
def spine(b, gr, T, keep, meta):
    """along the crest line (heather_plan.ridge_axis) from the west end of the place to the neck: a crest 3 wide of cobbled deepslate /
    tuff one block over the ground, every 4..7 blocks a vertebra (2..6 high, 1..3 wide, leaning a little); on the neck the crest goes
    on to the back of the skull. `keep`: cells never written (the trail, its banks)"""
    axis = P.ridge_axis(gr)
    n = 0; verts = []
    x = P.RIDGE[0] + 2; nxt = x + 3
    pts = [(xx, axis[xx][0]) for xx in range(P.RIDGE[0] + 2, 98)]
    # the neck: from the massif's shoulder (x 98) to the back-west corner of the skull, along z -552
    pts += [(xx, -552) for xx in range(98, P.HEAD[0] + 4)]
    for (x, z) in pts:
        if (x, z) in keep: continue
        g = int(T[P.ix(gr, x, z)])
        for c in (-1, 0, 1):
            q = (x, z + c)
            if q in keep: continue
            gg = int(T[P.ix(gr, *q)])
            b.set(x, gg + 1, z + c, CREST.at(x, gg + 1, z + c)) if c == 0 or hsh(x, 1, z + c, 3310) < 0.6 else None
        if x >= nxt:
            hgt = 2 + int(hsh(x, 2, z, 3311) * 5)                    # 2..6
            wd = 1 + int(hsh(x, 3, z, 3312) * 3)
            lean = 1 if hsh(x, 4, z, 3313) < 0.5 else -1
            for k in range(hgt):
                w = max(1, wd - k // 2)
                for a in range(w):
                    q = (x + a, z + (lean if k >= hgt - 2 and hgt > 3 else 0))
                    if q in keep: continue
                    gg = int(T[P.ix(gr, *q)])
                    b.set(q[0], gg + 2 + k, q[1], CREST.at(q[0], gg + 2 + k, q[1]))
            verts.append([x, z, g + 1 + hgt]); n += 1
            nxt = x + 4 + int(hsh(x, 5, z, 3314) * 4)
    meta["vertebrae"] = len(verts); meta["spine_top"] = max(v[2] for v in verts)
    return verts

def slopes(b, gr, T, keep):
    """the slopes of the ridge place: the top block of every column to the rock palette, patches of slid earth with grass where the
    slope is gentle (noise); trees stay (card: «местами сползающая земля с травой»)"""
    n = 0
    for x in range(P.RIDGE[0], P.RIDGE[2] + 1):
        for z in range(P.RIDGE[1], P.RIDGE[3] + 1):
            if (x, z) in keep or P.in_rect(P.HEAD, x, z): continue
            i, j = P.ix(gr, x, z)
            if gr["wet"][i, j]: continue
            g = int(T[i, j])
            nb = max(abs(int(T[i + a, j + c]) - g) for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            earth = nb <= 1 and hsh(x // 4, 7, z // 4, 3320) < 0.45
            if b.get(x, g, z) is None:
                b.set(x, g, z, SLID.at(x, g, z) if earth else ROCK.at(x, g, z)); n += 1
    return n

# ---------------------------------------------------------------- the head
def skull_cells():
    """the voxels of the head over its mound (y >= MOUTH_Y - 1): {(x, y, z): state}; the mouth cavity and the passage carved"""
    hx1, hz1, hx2, hz2 = P.HEAD; Y0 = P.MOUTH_Y
    out = {}
    def S(x, y, z, s=None): out[(x, y, z)] = s or SKULL.at(x, y, z)
    def A(x, y, z): out[(x, y, z)] = "minecraft:air"
    # the cranium: an ellipsoid centred over the back half, flattened under; the brow ridges; the cheeks down to the jaw
    cx, cz, cy = hx1 + 14.5, hz1 + 17.0, 101.0
    rx, rz, ry = 13.5, 12.5, P.HEAD_TOP - 101.0 + 0.4
    for x in range(hx1, hx2 + 1):
        for z in range(hz1, hz2 + 1):
            for y in range(Y0 - 1, P.HEAD_TOP + 1):
                e = ((x + 0.5 - cx) / rx) ** 2 + ((z + 0.5 - cz) / rz) ** 2 + ((y + 0.5 - cy) / ry) ** 2
                if e <= 1.0 or (y < cy and ((x + 0.5 - cx) / rx) ** 2 + ((z + 0.5 - cz) / rz) ** 2 <= 1.0): S(x, y, z)
    # the snout (upper jaw): from the cranium forward (north) to Z 0, X 8..21, y 90..97, narrowing and rising a little to the front
    for z in range(hz1, hz1 + 12):
        Z = z - hz1
        half = 5.5 + Z * 0.15
        for x in range(hx1, hx2 + 1):
            if abs(x + 0.5 - cx) > half: continue
            for y in range(Y0 + 6, Y0 + 13 - (1 if Z < 2 else 0)): S(x, y, z)
    # the lower jaw: Z 0..13, the floor at Y0 - 1 (the mound is under it), the gums 1 high along its sides
    for z in range(hz1, hz1 + 14):
        Z = z - hz1; half = 6.5 + Z * 0.2
        for x in range(hx1, hx2 + 1):
            if abs(x + 0.5 - cx) > half: continue
            S(x, Y0 - 1, z); S(x, Y0 - 2, z)
    # the mouth cavity: X cx-5.5..cx+5.5, Z 0..12, y Y0..Y0+5 (open to the north), carved
    for z in range(hz1, hz1 + 13):
        for x in range(hx1, hx2 + 1):
            if abs(x + 0.5 - cx) > 5.2: continue
            for y in range(Y0, Y0 + 6): A(x, y, z)
    # the cheeks closing the cavity on the sides (X = cx -6 / +6 columns) from Y0 to Y0 + 5
    for z in range(hz1, hz1 + 13):
        for x in (int(cx - 6.0), int(cx + 6.0)):
            for y in range(Y0, Y0 + 6): S(x, y, z)
    # the passage from the west (the trail's end NECK_END) to the platform: Z 2..4, from X 0 to the cavity, 3 high, a rough arch
    tz = P.NECK_END[1]
    for x in range(hx1, int(cx - 5)):
        for z in (tz - 1, tz, tz + 1):
            S(x, Y0 - 1, z, "minecraft:tuff")
            for y in range(Y0, Y0 + 3): A(x, y, z)
            S(x, Y0 + 3, z, "minecraft:cobbled_deepslate")
        S(x, Y0, tz - 2); S(x, Y0 + 1, tz - 2); S(x, Y0 + 2, tz - 2)
        S(x, Y0, tz + 2); S(x, Y0 + 1, tz + 2); S(x, Y0 + 2, tz + 2)
    x0 = int(cx - 6.0)
    for z in (tz - 1, tz, tz + 1):
        for y in range(Y0, Y0 + 3): A(x0, y, z)
    # the platform: polished tuff 5 x 5 at Y0 - 1 (the floor), the rest of the cavity floor tuff
    mx1, mz1, mx2, mz2 = P.MOUTH
    for x in range(mx1, mx2 + 1):
        for z in range(mz1, mz2 + 1): S(x, Y0 - 1, z, "minecraft:polished_tuff")
    # the teeth round the open (north) edge of the jaw, Z 0: dripstone blocks 1 high with fangs (base + tip, up) and between them a
    # frustum + tip standing on the floor: every cell of the edge holds 1.5+ of collision, nobody can stand on it (HQ T-031, 1)
    for x in range(hx1, hx2 + 1):
        if abs(x + 0.5 - cx) > 5.2: continue
        z = hz1
        if (x - hx1) % 2 == 0:
            S(x, Y0, z, "minecraft:dripstone_block")
            S(x, Y0 + 1, z, "minecraft:pointed_dripstone[thickness=base,vertical_direction=up,waterlogged=false]")
            S(x, Y0 + 2, z, "minecraft:pointed_dripstone[thickness=tip,vertical_direction=up,waterlogged=false]")
        else:
            S(x, Y0, z, "minecraft:pointed_dripstone[thickness=frustum,vertical_direction=up,waterlogged=false]")
            S(x, Y0 + 1, z, "minecraft:pointed_dripstone[thickness=tip,vertical_direction=up,waterlogged=false]")
        # the upper fangs hanging from the snout's front (y Y0 + 5 .. down), every other cell
        if (x - hx1) % 2 == 1:
            S(x, Y0 + 5, z, "minecraft:pointed_dripstone[thickness=base,vertical_direction=down,waterlogged=false]")
            S(x, Y0 + 4, z, "minecraft:pointed_dripstone[thickness=tip,vertical_direction=down,waterlogged=false]")
        else:
            S(x, Y0 + 5, z, "minecraft:dripstone_block")
    # the eye: on the west side of the cranium at Z 13..14, y 103..104: a niche 1 deep, tinted glass at its back, a dripstone brow over it
    ex = None
    for x in range(hx1, hx2 + 1):
        if (x, 103, hz1 + 13) in out and out[(x, 103, hz1 + 13)] != "minecraft:air": ex = x; break
    eye = []
    for z in (hz1 + 13, hz1 + 14):
        for y in (103, 104):
            A(ex, y, z); S(ex + 1, y, z, "minecraft:tinted_glass"); eye.append([ex + 1, y, z])
        S(ex - 1, 105, z, "minecraft:dripstone_block")
    # the horns: two curved prongs from the back of the cranium, backwards (south) and up
    for side in (-1, 1):
        x0, z0, y0 = cx + side * 8, hz1 + 25, 110
        for k in range(9):
            x = int(round(x0 + side * k * 0.3)); z = int(round(z0 + k * 0.6)); y = int(round(y0 + k * 0.9))
            if z > hz2: break
            S(x, y, z, "minecraft:cobbled_deepslate"); S(x, y - 1, z, "minecraft:tuff")
    meta = dict(eye=eye, eye_x=ex, centre=[cx, cz], cavity=[int(cx - 5), hz1, int(cx + 5), hz1 + 12])
    return out, meta

def sword_cells(eye):
    """the sword (card: 36 blocks, leaning west): the point sunk into the cranium over the eye, the blade going up and west (lean 16°),
    3 wide (the flat faces north-south), polished andesite edges, andesite flat with rust streaks of brown terracotta, the guard of
    polished tuff 9 wide, the grip of dark oak logs bound with chains, the pommel; {(x, y, z): state}, the base point"""
    ex, ey, ez = eye[0][0], max(e[1] for e in eye), sum(e[2] for e in eye) / len(eye)
    bx, by, bz = ex + 4.5, ey + 7.0, ez + 0.5                          # where the blade goes into the skull (above the eye, inside)
    lean = math.radians(16)
    ax, ay = -math.sin(lean), math.cos(lean)                         # along the blade: up and west
    px, py = math.cos(lean), math.sin(lean)                          # across it in the plane x-y
    L = 36.0; BL = 25.0
    cells = {}
    for x in range(int(bx) - 16, int(bx) + 6):
        for y in range(int(by) - 6, int(by) + 38):
            dx, dy = x + 0.5 - bx, y + 0.5 - by
            t = dx * ax + dy * ay; s_ = dx * px + dy * py
            zc = int(ez)
            if -4 <= t <= BL and abs(s_) <= 1.35 - (0.6 if t < 2 else 0):
                edge = abs(s_) > 0.55
                for z in (zc, zc + 1) if not edge else (zc,):
                    st = "minecraft:polished_andesite" if edge else ("minecraft:brown_terracotta" if hsh(x, y, z, 3330) < 0.1 else "minecraft:andesite")
                    cells[(x, y, z)] = st
            elif BL < t <= BL + 1.2 and abs(s_) <= 4.4:                  # the guard
                for z in (zc - 1, zc, zc + 1, zc + 2) if abs(s_) <= 2.4 else (zc, zc + 1):
                    cells[(x, y, z)] = "minecraft:polished_tuff"
            elif BL + 1.2 < t <= BL + 8.5 and abs(s_) <= 0.6:            # the grip
                for z in (zc, zc + 1):
                    cells[(x, y, z)] = "minecraft:iron_chain[axis=y,waterlogged=false]" if int(t) % 3 == 0 and z == zc + 1 else "minecraft:dark_oak_log[axis=y]"
            elif BL + 8.5 < t <= L and abs(s_) <= 1.4:                   # the pommel
                for z in (zc, zc + 1): cells[(x, y, z)] = "minecraft:polished_tuff" if abs(s_) > 0.6 else "minecraft:chiseled_tuff"
    return cells, [int(bx), int(by), int(ez)]

def head(b, meta):
    """the head and the sword into b (the head's cells overwrite the mound's surface); the templates of both; the sign"""
    sk, hm = skull_cells()
    for k, s_ in sk.items(): b.set(*k, s_)
    sw, base = sword_cells(hm["eye"])
    for k, s_ in sw.items():
        if k in sk and sk[k] != "minecraft:air": continue           # inside the skull: the skull stays (the blade is sunk)
        b.set(*k, s_)
    # the sign at the foot of the blade: the skull top is out of reach - on the west cheek by the mouth passage, under the sword (a
    # plaque of polished tuff, the wall sign on its west face, at the eye level of the trail)
    tz = P.NECK_END[1]
    sx, sy, sz = P.HEAD[0], P.MOUTH_Y + 1, tz + 3
    b.set(sx, sy, sz, "minecraft:polished_tuff")
    b.set(sx - 1, sy, sz, 'minecraft:dark_oak_wall_sign[facing=west,waterlogged=false]' + sign_nbt(["Он дошёл", "до самой головы.", "Дальше идти", "было некуда."]))
    hm.update(sword_base=base, sword_top=max(k[1] for k in sw), sword=len(sw), sign=[sx - 1, sy, sz], head_cells=len(sk))
    meta["head"] = hm
    return sk, sw
