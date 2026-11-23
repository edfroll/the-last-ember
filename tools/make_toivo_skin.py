#!/usr/bin/env python3
"""T-032: placeholder skin of Toivo, the ringer's grandson (resource pack, the mannequin's profile texture last_ember:entity/toivo): a young
hunter in green (a hooded jerkin, brown breeches, boots), pale (he hung in a cocoon), shreds of web on him; and his bow with the green
string (item model last_ember:spiders/toivo_bow: a 16 x 16 sprite, lies in the clearing by the live cocoon). Classic 64 x 64 player skin
layout (wide arms). Deterministic (a hash, no randomness): tools/check_gen.sh runs it.
  python3 tools/make_toivo_skin.py"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab"))
import png

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, "resourcepack/assets/last_ember")

def h(x, y, s):
    n = (x * 374761393 + y * 668265263 + s * 2654435761) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0

GREEN = [(58, 92, 48), (52, 84, 44), (64, 100, 54), (48, 78, 40)]
GREEN_D = [(38, 62, 32), (34, 56, 30), (42, 68, 36)]
BREECH = [(92, 70, 48), (84, 64, 44), (100, 76, 52)]
HAIR = [(120, 92, 60), (110, 84, 54), (130, 100, 66)]
SKIN = [(222, 206, 196), (214, 198, 188), (228, 214, 204)]      # pale
SKIN_D = (186, 168, 160)
BOOT = [(60, 44, 30), (68, 50, 34)]
BELT = (70, 50, 32)
EYE = (60, 86, 70)
WEB = (236, 236, 232)

def pick(pal, x, y, s): return pal[int(h(x, y, s) * len(pal)) % len(pal)] + (255,)
def skin():
    img = [[(0, 0, 0, 0)] * 64 for _ in range(64)]
    def box(x1, y1, x2, y2, f):
        for y in range(y1, y2):
            for x in range(x1, x2): img[y][x] = f(x - x1, y - y1, x, y)
    def cloth(u, v, x, y):
        if h(x, y, 9) < 0.06: return WEB + (255,)                  # shreds of the cocoon
        return pick(GREEN if h(x // 2, y, 5) > 0.2 else GREEN_D, x, y, 1)
    hair = lambda u, v, x, y: pick(HAIR, x, y, 2)
    # ---- head: hair on top and back, the face pale
    box(8, 0, 16, 8, hair); box(16, 0, 24, 8, lambda u, v, x, y: pick(SKIN, x, y, 4))
    box(0, 8, 8, 16, lambda u, v, x, y: hair(u, v, x, y) if v < 4 or u < 3 else pick(SKIN, x, y, 4))
    box(16, 8, 24, 16, lambda u, v, x, y: hair(u, v, x, y) if v < 4 or u > 4 else pick(SKIN, x, y, 4))
    box(24, 8, 32, 16, hair)
    def face(u, v, x, y):
        if v <= 1: return hair(u, v, x, y)
        if v == 3 and u in (2, 5): return EYE + (255,)
        if v == 3 and u in (1, 6): return (240, 240, 236, 255)
        if v == 4 and u in (3, 4): return SKIN_D + (255,)
        if v == 6 and u in (3, 4): return (170, 120, 112, 255)
        return pick(SKIN, x, y, 4)
    box(8, 8, 16, 16, face)
    # ---- the hood (hat layer), down on the shoulders: over the back and the sides, open in front
    box(40, 0, 48, 8, lambda u, v, x, y: (0, 0, 0, 0)); box(48, 0, 56, 8, lambda u, v, x, y: (0, 0, 0, 0))
    box(32, 8, 40, 16, lambda u, v, x, y: cloth(u, v, x, y) if v >= 6 else (0, 0, 0, 0))
    box(48, 8, 56, 16, lambda u, v, x, y: cloth(u, v, x, y) if v >= 6 else (0, 0, 0, 0))
    box(56, 8, 64, 16, lambda u, v, x, y: cloth(u, v, x, y) if v >= 5 else (0, 0, 0, 0))
    box(40, 8, 48, 16, lambda u, v, x, y: (0, 0, 0, 0))
    # ---- body: the green jerkin, a belt with a quiver strap across
    def body(u, v, x, y):
        if v == 7: return BELT + (255,)
        if u == v or u == v - 1: return BELT + (255,)
        return cloth(u, v, x, y)
    box(20, 16, 28, 20, cloth); box(28, 16, 36, 20, cloth)
    box(16, 20, 20, 32, cloth); box(20, 20, 28, 32, body); box(28, 20, 32, 32, cloth); box(32, 20, 40, 32, body)
    # ---- arms: green sleeves, pale hands
    def arm(u, v, x, y): return pick(SKIN, x, y, 4) if v >= 10 else cloth(u, v, x, y)
    for (ax, ay) in ((40, 16), (32, 48)):
        box(ax + 4, ay, ax + 8, ay + 4, cloth); box(ax + 8, ay, ax + 12, ay + 4, lambda u, v, x, y: pick(SKIN, x, y, 4))
        box(ax, ay + 4, ax + 16, ay + 16, arm)
    # ---- legs: brown breeches, boots
    def leg(u, v, x, y):
        if v >= 9: return pick(BOOT, x, y, 7)
        return WEB + (255,) if h(x, y, 11) < 0.05 else pick(BREECH, x, y, 8)
    for (lx, ly) in ((0, 16), (16, 48)):
        box(lx + 4, ly, lx + 8, ly + 4, lambda u, v, x, y: pick(BREECH, x, y, 8)); box(lx + 8, ly, lx + 12, ly + 4, lambda u, v, x, y: pick(BOOT, x, y, 7))
        box(lx, ly + 4, lx + 16, ly + 16, leg)
    return img

BOW = [
    "................",
    ".........bbB....",
    "........bB..g...",
    ".......bB....g..",
    "......bB......g.",
    ".....bB.......g.",
    "....bB........g.",
    "...bB.........g.",
    "...Bb.........g.",
    "....Bb........g.",
    ".....Bb.......g.",
    "......Bb......g.",
    ".......Bb....g..",
    "........Bb..g...",
    ".........BBb....",
    "................"]
PAL = {"B": (88, 58, 32, 255), "b": (128, 90, 52, 255), "g": (70, 170, 60, 255)}

def main():
    os.makedirs(os.path.join(RP, "textures/entity"), exist_ok=True)
    png.write(os.path.join(RP, "textures/entity/toivo.png"), skin())
    for d in ("textures/item/spiders", "models/item/spiders", "items/spiders"): os.makedirs(os.path.join(RP, d), exist_ok=True)
    png.write(os.path.join(RP, "textures/item/spiders/toivo_bow.png"), [[PAL.get(c, (0, 0, 0, 0)) for c in row] for row in BOW])
    json.dump({"parent": "minecraft:item/handheld", "textures": {"layer0": "last_ember:item/spiders/toivo_bow"}}, open(os.path.join(RP, "models/item/spiders/toivo_bow.json"), "w"))
    json.dump({"model": {"type": "minecraft:model", "model": "last_ember:item/spiders/toivo_bow"}}, open(os.path.join(RP, "items/spiders/toivo_bow.json"), "w"))
    print("toivo skin and bow written")

if __name__ == "__main__":
    main()
