#!/usr/bin/env python3
"""T-029: placeholder textures and models of the King Who Sleeps (resource pack): the plate armour (equipment asset
last_ember:sleeping_king, dark steel with rust, a lilac cloak on the back, a crown on the helm; sleeping_king_awake: the same with the eyes
of the helm lit), the two-handed sword (item model last_ember:castle/king_sword + held poses _raised, _over, _down), the crown
(last_ember:castle/king_crown). Deterministic (a hash, no randomness): tools/check_gen.sh runs it.
  python3 tools/make_castle_textures.py"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab"))
import png

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, "resourcepack/assets/last_ember")


def h(x, y, s):
    n = (x * 374761393 + y * 668265263 + s * 2654435761) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0


STEEL = [(46, 48, 54), (56, 58, 66), (38, 40, 46), (66, 68, 76)]
RUST = [(92, 52, 30), (110, 64, 34), (74, 42, 26)]
LILAC = [(84, 52, 110), (98, 62, 128), (70, 42, 92)]
GOLD = [(214, 172, 52), (182, 140, 40), (240, 204, 90)]


def steel(x, y, s=1):
    c = STEEL[int(h(x, y, s) * 4) % 4]
    if h(x // 2, y // 2, s + 7) < 0.16: c = RUST[int(h(x, y, s + 3) * 3) % 3]
    return c + (255,)


def armour(awake, legs=False):
    W, H = 64, 32
    px = [[(0, 0, 0, 0)] * W for _ in range(H)]
    def fill(x1, y1, x2, y2, fn):
        for y in range(y1, y2):
            for x in range(x1, x2): px[y][x] = fn(x, y)
    if legs:
        fill(0, 16, 16, 32, steel)                    # legs
        fill(16, 16, 40, 32, lambda x, y: steel(x, y, 5) if y > 26 else (30, 30, 34, 255))   # the belt / tassets
        return px
    fill(0, 0, 32, 16, steel)                          # helm
    fill(16, 16, 40, 32, steel)                        # body
    fill(40, 16, 56, 32, steel)                        # arms
    fill(0, 16, 16, 32, lambda x, y: steel(x, y, 3))   # boots (legs part of layer 1)
    # the cloak on the back of the body, lilac, ragged at the hem
    fill(32, 20, 40, 32, lambda x, y: (LILAC[int(h(x, y, 9) * 3) % 3] + (255,)) if not (y == 31 and h(x, 0, 10) < 0.4) else (0, 0, 0, 0))
    # the visor: a dark slit on the front of the helm with two eyes
    for x in range(9, 15): px[12][x] = (14, 14, 18, 255)
    eye = (200, 120, 255, 255) if awake else (34, 30, 40, 255)
    px[12][10] = eye; px[12][13] = eye
    if awake: px[11][10] = (150, 90, 210, 255); px[11][13] = (150, 90, 210, 255)
    # the crown: a gold band round the top of the helm (row 8 of the sides) with points on the top face's edges
    for x in range(0, 32): px[8][x] = GOLD[int(h(x, 8, 11) * 3) % 3] + (255,)
    for x in range(8, 16):
        for y in (0, 7): px[y][x] = GOLD[(x + y) % 3] + (255,) if x % 2 == 0 else px[y][x]
    for y in range(0, 8):
        for x in (8, 15): px[y][x] = GOLD[(x + y) % 3] + (255,) if y % 2 == 0 else px[y][x]
    # a purple gem in the band's front
    px[8][11] = (140, 60, 200, 255); px[8][12] = (140, 60, 200, 255)
    return px


def sword():
    """32 x 32: a long dark blade from the lower left to the upper right, a gilded crossguard, a lilac grip"""
    px = [[(0, 0, 0, 0)] * 32 for _ in range(32)]
    for i in range(6, 31):                              # the blade along the diagonal (x = i, y = 31 - i), 2..3 wide
        for d in (-1, 0, 1):
            x, y = i + d, 31 - i
            if 0 <= x < 32 and 0 <= y < 32:
                c = (92, 96, 108) if d == 0 else (60, 62, 72)
                if h(x, y, 21) < 0.12: c = RUST[1]
                px[y][x] = c + (255,)
    for d in range(-4, 5):                              # the crossguard across the diagonal at i = 7
        x, y = 7 + d, 31 - 7 + d
        if 0 <= x < 32 and 0 <= y < 32: px[y][x] = GOLD[abs(d) % 3] + (255,)
    for i in range(1, 6):                               # the grip and the pommel
        px[31 - i][i] = LILAC[i % 3] + (255,)
    px[31][0] = GOLD[0] + (255,); px[30][0] = GOLD[1] + (255,); px[31][1] = GOLD[1] + (255,)
    return px


def crown_tex():
    px = [[GOLD[int(h(x, y, 31) * 3) % 3] + (255,) for x in range(16)] for y in range(16)]
    for (x, y) in ((3, 3), (8, 3), (12, 3)): px[y][x] = (140, 60, 200, 255)
    return px


def model(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w"), indent=1); open(path, "a").write("\n")


def main():
    eq = os.path.join(RP, "textures/entity/equipment")
    for d in ("humanoid", "humanoid_leggings"): os.makedirs(os.path.join(eq, d), exist_ok=True)
    png.write(os.path.join(eq, "humanoid/sleeping_king.png"), armour(False))
    png.write(os.path.join(eq, "humanoid/sleeping_king_awake.png"), armour(True))
    png.write(os.path.join(eq, "humanoid_leggings/sleeping_king.png"), armour(False, legs=True))
    for name, tex in (("sleeping_king", "sleeping_king"), ("sleeping_king_awake", "sleeping_king_awake")):
        model(os.path.join(RP, "equipment/%s.json" % name), {"layers": {"humanoid": [{"texture": "last_ember:%s" % tex}], "humanoid_leggings": [{"texture": "last_ember:sleeping_king"}]}})
    tx = os.path.join(RP, "textures/item/castle"); os.makedirs(tx, exist_ok=True)
    png.write(os.path.join(tx, "king_sword.png"), sword())
    png.write(os.path.join(tx, "king_crown.png"), crown_tex())
    # the held poses: the same sprite, other third-person transforms (held as usual / raised for the sweep / over the head / down into the floor)
    poses = {"king_sword": [0, -90, 55], "king_sword_raised": [0, -90, 120], "king_sword_over": [0, -90, 175], "king_sword_down": [0, -90, -125]}
    for name, rot in poses.items():
        model(os.path.join(RP, "models/item/castle/%s.json" % name), {
            "parent": "minecraft:item/handheld", "textures": {"layer0": "last_ember:item/castle/king_sword"},
            "display": {"thirdperson_righthand": {"rotation": rot, "translation": [0, 6, 1.0], "scale": [1.6, 1.6, 1.0]},
                        "thirdperson_lefthand": {"rotation": [0, 90, -55], "translation": [0, 6, 1.0], "scale": [1.6, 1.6, 1.0]},
                        "fixed": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1.2, 1.2, 1.2]}}})
        model(os.path.join(RP, "items/castle/%s.json" % name), {"model": {"type": "minecraft:model", "model": "last_ember:item/castle/%s" % name}})
    # the crown: a gold ring (12 x 3 x 12 of a 16 cube) with four points
    els = []
    for (a, b) in (((2, 0, 2), (14, 3, 3)), ((2, 0, 13), (14, 3, 14)), ((2, 0, 3), (3, 3, 13)), ((13, 0, 3), (14, 3, 13)),
                   ((7, 3, 2), (9, 6, 3)), ((7, 3, 13), (9, 6, 14)), ((2, 3, 7), (3, 6, 9)), ((13, 3, 7), (14, 6, 9))):
        els.append({"from": list(a), "to": list(b), "faces": {f: {"uv": [0, 0, 16, 16], "texture": "#c"} for f in ("north", "south", "east", "west", "up", "down")}})
    model(os.path.join(RP, "models/item/castle/king_crown.json"), {"textures": {"c": "last_ember:item/castle/king_crown", "particle": "last_ember:item/castle/king_crown"}, "elements": els})
    model(os.path.join(RP, "items/castle/king_crown.json"), {"model": {"type": "minecraft:model", "model": "last_ember:item/castle/king_crown"}})
    print("castle textures: armour (2 + leggings), sword (4 poses), crown")


if __name__ == "__main__":
    main()
