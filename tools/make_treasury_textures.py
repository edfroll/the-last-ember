#!/usr/bin/env python3
"""T-034: placeholder textures and models of the owners of the treasuries of R1 (resource pack):
  - the Ogre: the equipment asset last_ember:ogre (dirty skin, scraps of hides, a belt; layer humanoid + leggings), the club
    (item model last_ember:treasury/ogre_club and the held pose _raised: the same sprite over the head);
  - the Jelly: last_ember:treasury/jelly (a translucent green mass, bones and a rusty helmet inside: a cube 16 with inner boxes);
  - the White Lady: last_ember:treasury/white_lady (a tall pale woman in a long dress, no feet, the face hidden by hair; translucent);
  - the raven: last_ember:treasury/raven (a black bird sitting: body, head with a beak, tail).
Deterministic (a hash, no randomness): tools/check_gen.sh runs it.
  python3 tools/make_treasury_textures.py"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab"))
import png

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, "resourcepack/assets/last_ember")


def h(x, y, s):
    n = (x * 374761393 + y * 668265263 + s * 2654435761) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0


def pick(pal, x, y, s): return pal[int(h(x, y, s) * len(pal)) % len(pal)]
SKIN = [(132, 112, 86), (118, 98, 74), (146, 124, 96), (104, 88, 66)]
DIRT = [(86, 70, 50), (72, 58, 42)]
HIDE = [(94, 62, 38), (110, 74, 44), (78, 52, 32), (124, 88, 56)]
WOOD = [(92, 66, 40), (74, 52, 32), (108, 80, 50)]
GREEN = [(96, 170, 84), (84, 152, 72), (110, 186, 96), (74, 140, 66)]
PALE = [(226, 230, 236), (210, 216, 224), (236, 238, 242), (196, 204, 214)]
HAIR = [(48, 48, 54), (64, 62, 70), (36, 36, 40)]
BLACK = [(22, 22, 26), (32, 30, 36), (16, 16, 20), (42, 40, 48)]


def model(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w"), indent=1); open(path, "a").write("\n")


def item(name):
    model(os.path.join(RP, "items/treasury/%s.json" % name), {"model": {"type": "minecraft:model", "model": "last_ember:item/treasury/%s" % name}})


def ogre_armour(legs=False):
    W, H = 64, 32
    px = [[(0, 0, 0, 0)] * W for _ in range(H)]
    def fill(x1, y1, x2, y2, fn):
        for y in range(y1, y2):
            for x in range(x1, x2): px[y][x] = fn(x, y)
    def skin(x, y, s=1):
        c = pick(SKIN, x, y, s)
        if h(x // 2, y // 2, s + 5) < 0.2: c = pick(DIRT, x, y, s + 2)
        return c + (255,)
    def hide(x, y, s=3): return pick(HIDE, x, y, s) + (255,)
    if legs:
        fill(0, 16, 16, 32, lambda x, y: hide(x, y, 4) if y < 26 or h(x, 0, 6) < 0.5 else (0, 0, 0, 0))     # ragged hide breeches
        fill(16, 16, 40, 32, lambda x, y: (52, 38, 26, 255) if y > 27 else hide(x, y, 7))                    # the belt
        return px
    fill(0, 0, 32, 16, skin)                                                      # the head: a bald, dirty skin
    for x in (9, 14): px[12][x] = (30, 18, 14, 255)                                # small eyes
    for x in range(10, 14): px[14][x] = (60, 30, 24, 255)                          # a wide mouth
    fill(16, 16, 40, 32, lambda x, y: hide(x, y) if (y < 24 or h(x, y, 8) < 0.5) else skin(x, y, 2))   # scraps of hides on the body
    fill(40, 16, 56, 32, skin)                                                    # the arms bare
    fill(0, 16, 16, 32, lambda x, y: skin(x, y, 3))
    return px


def club():
    px = [[(0, 0, 0, 0)] * 32 for _ in range(32)]
    for i in range(3, 30):                                                        # a crooked log, thicker at the top right
        r = 1 if i < 14 else 2 if i < 22 else 3
        for d in range(-r, r + 1):
            x, y = i + d // 2, 31 - i + (d + 1) // 2
            if 0 <= x < 32 and 0 <= y < 32: px[y][x] = pick(WOOD, x, y, 21) + (255,)
    for (x, y) in ((24, 5), (27, 7), (22, 9), (26, 3)): px[y][x] = (180, 176, 160, 255)   # bone nails in the head
    return px


def tex(name, w, hgt, fn):
    p = os.path.join(RP, "textures/item/treasury"); os.makedirs(p, exist_ok=True)
    png.write(os.path.join(p, name + ".png"), [[fn(x, y) for x in range(w)] for y in range(hgt)])


def box(a, b, t, tint=None):
    return {"from": list(a), "to": list(b), "faces": {f: {"uv": [0, 0, 16, 16], "texture": "#" + t} for f in ("north", "south", "east", "west", "up", "down")}}


def main():
    eq = os.path.join(RP, "textures/entity/equipment")
    for d in ("humanoid", "humanoid_leggings"): os.makedirs(os.path.join(eq, d), exist_ok=True)
    png.write(os.path.join(eq, "humanoid/ogre.png"), ogre_armour())
    png.write(os.path.join(eq, "humanoid_leggings/ogre.png"), ogre_armour(legs=True))
    model(os.path.join(RP, "equipment/ogre.json"), {"layers": {"humanoid": [{"texture": "last_ember:ogre"}], "humanoid_leggings": [{"texture": "last_ember:ogre"}]}})
    tex("ogre_club", 32, 32, lambda x, y: club()[y][x])
    for name, rot in (("ogre_club", [0, -90, 55]), ("ogre_club_raised", [0, -90, 160])):
        model(os.path.join(RP, "models/item/treasury/%s.json" % name), {
            "parent": "minecraft:item/handheld", "textures": {"layer0": "last_ember:item/treasury/ogre_club"},
            "display": {"thirdperson_righthand": {"rotation": rot, "translation": [0, 5, 1.0], "scale": [1.4, 1.4, 1.0]},
                        "thirdperson_lefthand": {"rotation": [0, 90, -55], "translation": [0, 5, 1.0], "scale": [1.4, 1.4, 1.0]}}})
        item(name)
    # the jelly: translucent green (alpha 150) with darker swirls; the bones (bone white) and the helmet (rust) inside
    tex("jelly", 16, 16, lambda x, y: pick(GREEN, x, y, 31) + (150 if h(x, y, 32) > 0.15 else 190,))
    tex("jelly_bone", 16, 16, lambda x, y: (222, 214, 190, 255) if h(x, y, 33) > 0.2 else (196, 186, 160, 255))
    tex("jelly_helm", 16, 16, lambda x, y: (122, 72, 40, 255) if h(x, y, 34) > 0.35 else (88, 52, 30, 255))
    els = [box((0, 0, 0), (16, 12, 16), "g"), box((2, 12, 2), (14, 15, 14), "g"),
           box((4, 3, 6), (12, 4, 7), "b"), box((6, 5, 9), (7, 9, 10), "b"), box((9, 2, 4), (10, 3, 11), "b"),   # bones inside
           box((5, 6, 3), (10, 9, 7), "h")]                                                                      # the rusty helmet
    model(os.path.join(RP, "models/item/treasury/jelly.json"), {"textures": {"g": "last_ember:item/treasury/jelly", "b": "last_ember:item/treasury/jelly_bone",
          "h": "last_ember:item/treasury/jelly_helm", "particle": "last_ember:item/treasury/jelly"}, "elements": els[2:] + els[:2]})
    item("jelly")
    # the White Lady: 32 high (2 blocks at scale 1): the dress widening to the floor (no feet), the arms, the head under long hair
    tex("lady_dress", 16, 16, lambda x, y: pick(PALE, x, y, 41) + (170,))
    tex("lady_hair", 16, 16, lambda x, y: pick(HAIR, x, y, 42) + (230,))
    tex("lady_skin", 16, 16, lambda x, y: (236, 232, 228, 200))
    els = [box((3, 0, 4), (13, 8, 12), "d"), box((4, 8, 5), (12, 16, 11), "d"), box((5, 16, 6), (11, 24, 10), "d"),
           box((3, 14, 7), (5, 23, 9), "s"), box((11, 14, 7), (13, 23, 9), "s"),
           box((5, 24, 5), (11, 31, 11), "s"), box((4, 21, 4), (12, 32, 6), "h"), box((4, 24, 6), (5, 32, 12), "h"), box((11, 24, 6), (12, 32, 12), "h"),
           box((5, 30, 6), (11, 32, 12), "h"), box((5, 22, 11), (11, 31, 12), "h")]
    model(os.path.join(RP, "models/item/treasury/white_lady.json"), {"textures": {"d": "last_ember:item/treasury/lady_dress", "h": "last_ember:item/treasury/lady_hair",
          "s": "last_ember:item/treasury/lady_skin", "particle": "last_ember:item/treasury/lady_dress"}, "elements": els})
    item("white_lady")
    # the raven: 16 units, sitting
    tex("raven", 16, 16, lambda x, y: pick(BLACK, x, y, 51) + (255,))
    tex("raven_beak", 16, 16, lambda x, y: (60, 58, 56, 255))
    els = [box((5, 2, 4), (11, 8, 12), "r"), box((6, 7, 2), (10, 11, 6), "r"), box((7, 8, 0), (9, 9, 2), "k"),
           box((6, 3, 12), (10, 4, 16), "r"), box((6, 0, 7), (7, 2, 8), "k"), box((9, 0, 7), (10, 2, 8), "k")]
    model(os.path.join(RP, "models/item/treasury/raven.json"), {"textures": {"r": "last_ember:item/treasury/raven", "k": "last_ember:item/treasury/raven_beak",
          "particle": "last_ember:item/treasury/raven"}, "elements": els})
    item("raven")
    print("treasury textures: the ogre (armour + leggings, club 2 poses), the jelly, the white lady, the raven")


if __name__ == "__main__":
    main()
